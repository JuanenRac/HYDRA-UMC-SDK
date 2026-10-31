#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Contract source generator and drift check
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The SDK as the source of a group of server routes.

`contracts/sources/<group>.routes.json` declares the routes of a group (method,
path, access, query parameters, status codes) and names the closed JSON Schemas
the answers are made of. This tool turns that source into an OpenAPI 3.1
document and checks that nothing that should follow the source has drifted.

    python tools/contract_source.py            write the generated document(s)
    python tools/contract_source.py --check    fail when anything drifted

`--check` verifies, for every source:

* the generated OpenAPI document is exactly what the source produces;
* every vendored copy of the schemas (`clients/*/schemas`) is byte-identical to
  `contracts/json-schema/v1` and listed with the right hash in its
  `manifest.json`;
* the server (a `HYDRA-UMC-SERVER` checkout, found next to this SDK or given by
  `--server` / `HYDRA_UMC_SERVER_DIR`): its generated `docs/openapi.json`
  offers every route with the same method, the same access, the declared status
  codes and the declared query parameters, carries the closed schemas with the
  same fields, required list and enums, and its `src/connections.ts` enums are
  the schema enums;
* the consumers (other checkouts given by `--consumer`, or the Studio and the
  Suite next to this SDK): every route under a source path they mention exists
  in the source, and every query parameter they send is declared.

A checkout that is not there is reported as skipped, unless
`HYDRA_UMC_REQUIRE_WORKSPACE=1` (then it fails). Read-only except when
generating.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "contracts" / "sources"
SCHEMAS = ROOT / "contracts" / "json-schema" / "v1"
OPENAPI_ROOT = ROOT / "contracts"
HTTP_METHODS = ("get", "put", "post", "delete", "patch")
MIDDLEWARE_CODES = {"401", "403", "429"}
CONSUMER_REPOSITORIES = ("HYDRA-UMC-STUDIO", "HYDRA-UMC-SUITE")
CONSUMER_SUFFIXES = {".ts", ".tsx", ".js", ".mjs", ".py", ".qml", ".kt", ".swift", ".dart", ".go", ".rs"}
SKIPPED_PARTS = {".git", "node_modules", "dist", "build", "target", "__pycache__", ".venv", "tests", "test"}


class SourceError(Exception):
    """The source itself is not usable."""


def _read(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise SourceError(f"{path}: {error}") from error


def load_sources(directory: Path = SOURCES) -> dict[str, dict[str, Any]]:
    found = {path.name[: -len(".routes.json")]: _read(path) for path in sorted(directory.glob("*.routes.json"))}
    if not found:
        raise SourceError(f"no *.routes.json source under {directory}")
    return found


def duplicate_routes(sources: dict[str, dict[str, Any]]) -> list[str]:
    """One method on one path belongs to one source, once."""
    seen: dict[tuple[str, str], str] = {}
    problems: list[str] = []
    for name, source in sources.items():
        for route in source["routes"]:
            key = (route["method"], route["path"])
            if key in seen:
                problems.append(f"{route['method'].upper()} {route['path']} is declared by both {seen[key]} and {name}")
            seen[key] = name
    return problems


def schema_of(name: str, source: dict[str, Any], schemas: Path = SCHEMAS) -> dict[str, Any]:
    if name not in source["schemas"]:
        raise SourceError(f"the source names no schema {name!r}")
    return _read(schemas / source["schemas"][name])


def enum_of(reference: str, source: dict[str, Any], schemas: Path = SCHEMAS) -> list[str]:
    """`Schema.property` -> the enum (or the const) of that property in the closed schema."""
    schema_name, _, prop = reference.partition(".")
    properties = schema_of(schema_name, source, schemas).get("properties", {})
    if prop not in properties:
        raise SourceError(f"{reference}: the schema has no such property")
    definition = properties[prop]
    if "enum" in definition:
        return list(definition["enum"])
    if "const" in definition:
        return [definition["const"]]
    raise SourceError(f"{reference}: the property has no enum")


def _query_parameter(spec: dict[str, Any], source: dict[str, Any], schemas: Path) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": "string"}
    if "enum_from" in spec:
        schema["enum"] = enum_of(spec["enum_from"], source, schemas)
    elif "enum" in spec:
        schema["enum"] = list(spec["enum"])
    if "pattern" in spec:
        schema["pattern"] = spec["pattern"]
    return {"name": spec["name"], "in": "query", "required": False, "description": spec["description"], "schema": schema}


def _ref(name: str) -> dict[str, str]:
    return {"$ref": f"#/components/schemas/{name}"}


def _json(schema: dict[str, Any]) -> dict[str, Any]:
    return {"application/json": {"schema": schema}}


def build_document(source: dict[str, Any], schemas: Path = SCHEMAS) -> dict[str, Any]:
    components: dict[str, Any] = {}
    for name in source["schemas"]:
        body = dict(schema_of(name, source, schemas))
        body.pop("$schema", None)
        body.pop("$id", None)
        components[name] = body
    for name, spec in source.get("lists", {}).items():
        components[name] = {
            "type": "object",
            "additionalProperties": False,
            "required": [spec["field"]],
            "properties": {spec["field"]: {"type": "array", "items": _ref(spec["item"])}},
        }
    components["Error"] = {
        "type": "object",
        "required": ["error"],
        "properties": {"error": {"type": "string"}},
    }
    paths: dict[str, Any] = {}
    for route in source["routes"]:
        responses: dict[str, Any] = {}
        for code, spec in route["responses"].items():
            if "list" in spec:
                responses[code] = {"description": spec["description"], "content": _json(_ref(spec["list"]))}
            elif spec.get("error"):
                responses[code] = {"description": spec["description"], "content": _json(_ref("Error"))}
            else:
                responses[code] = {"description": spec["description"]}
        operation: dict[str, Any] = {
            "tags": [source["group"]],
            "operationId": route["operationId"],
            "summary": route["summary"],
            "x-access": route["access"],
            "parameters": [_query_parameter(q, source, schemas) for q in route.get("query", [])],
            "responses": responses,
        }
        if route["access"] != "public":
            operation["security"] = [{"bearerAuth": []}]
        paths.setdefault(route["path"], {})[route["method"]] = operation
    document = source["document"]
    return {
        "openapi": "3.1.0",
        "info": {"title": document["title"], "version": document["version"], "description": document["description"]},
        "paths": paths,
        "components": {
            "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}},
            "schemas": components,
        },
    }


def render(document: dict[str, Any]) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def output_path(source: dict[str, Any]) -> Path:
    return OPENAPI_ROOT / source["output"]


# ---------------------------------------------------------------- checks

def check_generated(name: str, source: dict[str, Any]) -> list[str]:
    path = output_path(source)
    expected = render(build_document(source))
    try:
        current = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    except OSError:
        return [f"{name}: {path.name} is missing - run: python tools/contract_source.py"]
    if current != expected:
        return [f"{name}: {path.name} is out of date with its source - run: python tools/contract_source.py"]
    return []


def check_schema_copies(source: dict[str, Any], clients: Path = ROOT / "clients", schemas: Path = SCHEMAS) -> list[str]:
    problems: list[str] = []
    for file in sorted(set(source["schemas"].values())):
        canonical = (schemas / file).read_bytes()
        digest = hashlib.sha256(canonical).hexdigest()
        directories = [schemas] + sorted(path for path in clients.glob("*/schemas") if path.is_dir())
        for directory in directories:
            label = directory.relative_to(ROOT).as_posix() if directory.is_relative_to(ROOT) else str(directory)
            copy = directory / file
            if not copy.is_file():
                problems.append(f"{label}/{file} is missing")
                continue
            if copy.read_bytes() != canonical:
                problems.append(f"{label}/{file} differs from contracts/json-schema/v1/{file}")
            manifest_file = directory / "manifest.json"
            try:
                listed = {entry["file"]: entry["sha256"] for entry in json.loads(manifest_file.read_text(encoding="utf-8"))["contracts"]}
            except (OSError, ValueError, KeyError):
                problems.append(f"{label}/manifest.json cannot be read")
                continue
            if listed.get(file) != digest:
                problems.append(f"{label}/manifest.json lists {file} with another hash")
    return problems


def _is_public(operation: dict[str, Any]) -> bool:
    return not operation.get("security") or all(not entry for entry in operation["security"])


def _closed_shape(schema: dict[str, Any]) -> dict[str, Any]:
    """What must not drift between the closed schema of the SDK and the copy in an OpenAPI document."""
    properties: dict[str, Any] = {}
    for prop, definition in sorted(schema.get("properties", {}).items()):
        shape: dict[str, Any] = {}
        if "enum" in definition:
            shape["enum"] = list(definition["enum"])
        elif "const" in definition:
            shape["enum"] = [definition["const"]]
        for key in ("pattern", "format"):
            if key in definition:
                shape[key] = definition[key]
        properties[prop] = shape
    return {
        "additionalProperties": schema.get("additionalProperties"),
        "required": sorted(schema.get("required", [])),
        "properties": properties,
    }


def compare_with_server_document(source: dict[str, Any], server: dict[str, Any], schemas: Path = SCHEMAS) -> list[str]:
    problems: list[str] = []
    for route in source["routes"]:
        label = f"{route['method'].upper()} {route['path']}"
        offered = server.get("paths", {}).get(route["path"], {}).get(route["method"])
        if offered is None:
            problems.append(f"{label}: the source declares this route and the server does not register it")
            continue
        if (route["access"] == "public") != _is_public(offered):
            problems.append(f"{label}: access differs (source {route['access']}, server {'public' if _is_public(offered) else 'signed in'})")
        have = set(offered.get("responses", {}))
        for code in route["responses"]:
            if code not in MIDDLEWARE_CODES and code not in have:
                problems.append(f"{label}: the source lists status {code} and the handler never produces it")
        for code in sorted(have - set(route["responses"]) - MIDDLEWARE_CODES):
            problems.append(f"{label}: the handler produces status {code} and the source does not list it")
        declared = {q["name"] for q in route.get("query", [])}
        read = {p["name"] for p in offered.get("parameters", []) if p.get("in") == "query"}
        for name in sorted(declared - read):
            problems.append(f"{label}: the source declares the query parameter {name!r} and the handler never reads it")
        for name in sorted(read - declared):
            problems.append(f"{label}: the handler reads the query parameter {name!r} and the source does not declare it")
    server_schemas = server.get("components", {}).get("schemas", {})
    for name in source["schemas"]:
        if name not in server_schemas:
            problems.append(f"schema {name}: the server document does not carry it")
        elif _closed_shape(server_schemas[name]) != _closed_shape(schema_of(name, source, schemas)):
            problems.append(f"schema {name}: the server copy differs from the closed schema of the SDK")
    return problems


def _typescript_constant(text: str, constant: str) -> list[str] | None:
    match = re.search(rf"\b{re.escape(constant)}\s*=\s*\[([^\]]*)\]", text)
    return None if match is None else re.findall(r'"([^"]*)"', match.group(1))


def compare_server_enums(source: dict[str, Any], server_root: Path, schemas: Path = SCHEMAS) -> list[str]:
    spec = source.get("consumers", {}).get("server_enums")
    if not spec:
        return []
    path = server_root / spec["file"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return [f"{spec['file']}: cannot be read in the server checkout"]
    problems: list[str] = []
    for constant, reference in spec["constants"].items():
        declared = _typescript_constant(text, constant)
        if declared is None:
            problems.append(f"{spec['file']}: constant {constant} not found")
        elif declared != enum_of(reference, source, schemas):
            problems.append(f"{spec['file']}: {constant} differs from the enum of {reference} in the SDK")
    return problems


def scan_consumer(source: dict[str, Any], root: Path) -> list[str]:
    """Routes under a source path that a client mentions must exist; the query parameters it sends must be declared."""
    prefixes = sorted({"/".join(route["path"].split("/")[:3]) + "/" for route in source["routes"]})
    declared = {route["path"]: {q["name"] for q in route.get("query", [])} for route in source["routes"]}
    pattern = re.compile(r"(" + "|".join(re.escape(p) for p in prefixes) + r")([A-Za-z0-9_/-]*)(\?([^\"'`\s)]*))?")
    problems: list[str] = []
    for path in sorted(root.rglob("*")):
        if path.suffix not in CONSUMER_SUFFIXES or not path.is_file():
            continue
        relative = path.relative_to(root)
        if SKIPPED_PARTS & set(relative.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in pattern.finditer(text):
            route = (match.group(1) + match.group(2)).rstrip("/")
            where = f"{root.name}/{relative.as_posix()}"
            if route not in declared:
                problems.append(f"{where}: mentions {route}, which the source does not declare")
                continue
            for pair in (match.group(4) or "").split("&"):
                key = pair.split("=")[0]
                if key and re.fullmatch(r"[A-Za-z_]+", key) and key not in declared[route]:
                    problems.append(f"{where}: sends the query parameter {key!r} to {route}, which the source does not declare")
    return problems


# ---------------------------------------------------------------- command line

def _find(workspace: Path, name: str, explicit: str | None, variable: str) -> Path | None:
    for candidate in (explicit, os.environ.get(variable)):
        if candidate:
            return Path(candidate).resolve()
    sibling = workspace / name
    return sibling if sibling.is_dir() else None


def run_check(workspace: Path, server: str | None, consumers: list[str]) -> int:
    require = os.environ.get("HYDRA_UMC_REQUIRE_WORKSPACE") == "1"
    problems: list[str] = []
    notices: list[str] = []
    sources = load_sources()
    problems += duplicate_routes(sources)
    server_root = _find(workspace, "HYDRA-UMC-SERVER", server, "HYDRA_UMC_SERVER_DIR")
    consumer_roots = [Path(c).resolve() for c in consumers] or [workspace / n for n in CONSUMER_REPOSITORIES if (workspace / n).is_dir()]
    for name, source in sources.items():
        problems += check_generated(name, source)
        problems += [f"{name}: {p}" for p in check_schema_copies(source)]
        if server_root is not None and (server_root / "docs" / "openapi.json").is_file():
            document = _read(server_root / "docs" / "openapi.json")
            problems += [f"{name}: server: {p}" for p in compare_with_server_document(source, document)]
            problems += [f"{name}: server: {p}" for p in compare_server_enums(source, server_root)]
        else:
            (problems if require else notices).append(f"{name}: no HYDRA-UMC-SERVER checkout with docs/openapi.json to compare with")
        if not consumer_roots:
            (problems if require else notices).append(f"{name}: no consumer checkout to scan")
        for root in consumer_roots:
            problems += [f"{name}: {p}" for p in scan_consumer(source, root)]
    for notice in notices:
        print(f"CONTRACT_SOURCE=SKIP {notice}")
    if problems:
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        print(f"CONTRACT_SOURCE=FAIL {len(problems)} difference(s)", file=sys.stderr)
        return 1
    routes = sum(len(s["routes"]) for s in sources.values())
    print(f"CONTRACT_SOURCE=PASS sources={len(sources)} routes={routes} server={'checked' if server_root else 'skipped'} consumers={len(consumer_roots)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the OpenAPI documents of the contract sources, or check them for drift.")
    parser.add_argument("--check", action="store_true", help="fail when the generated file, a schema copy, the server or a consumer drifted")
    parser.add_argument("--workspace", default=str(ROOT.parent), help="folder that holds the sibling checkouts (default: next to this SDK)")
    parser.add_argument("--server", help="HYDRA-UMC-SERVER checkout (default: HYDRA_UMC_SERVER_DIR, then the sibling)")
    parser.add_argument("--consumer", action="append", default=[], help="a client checkout to scan (repeatable)")
    args = parser.parse_args(argv)
    try:
        if args.check:
            return run_check(Path(args.workspace), args.server, args.consumer)
        sources = load_sources()
        duplicates = duplicate_routes(sources)
        if duplicates:
            raise SourceError("; ".join(duplicates))
        for name, source in sources.items():
            path = output_path(source)
            path.write_text(render(build_document(source)), encoding="utf-8", newline="\n")
            print(f"wrote {path.relative_to(ROOT).as_posix()} ({name})")
        return 0
    except SourceError as error:
        print(f"CONTRACT_SOURCE=FAIL {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
