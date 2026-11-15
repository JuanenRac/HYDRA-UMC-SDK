#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Typed server client generated from the OpenAPI contract
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Generate the typed client of the server routes (TypeScript first) from the full OpenAPI document.

The source is `contracts/openapi/v1/server.full.openapi.json`, the same document the route tables come from. For every
operation the generator writes one method whose name is made from the verb and the path, whose arguments are the path
parameters, the query parameters and the body, and whose result is the type of the first 2xx JSON answer. Every named
schema of the document becomes an interface. The client never touches the network: it builds the request and hands it
to an injectable transport, so an app keeps its own fetch, its own token and its own error handling. Nothing in the
output is edited by hand.

    python tools/generate_clients.py           write generated/
    python tools/generate_clients.py --check   fail when a generated file is out of date
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
FULL = ROOT / "contracts" / "openapi" / "v1" / "server.full.openapi.json"
OUT = ROOT / "generated"
HEADER = "Generated from the server contract by tools/generate_clients.py. Do not edit."
METHODS = ("get", "put", "post", "delete", "patch")
IDENTIFIER = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")
TS_NAME = "hydra-server-client.ts"


def quote(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def key(name: str) -> str:
    return name if IDENTIFIER.match(name) else quote(name)


def type_of(schema: dict[str, Any] | None) -> str:
    """The TypeScript type of one schema of the subset the contract uses."""
    if not schema:
        return "unknown"
    if "$ref" in schema:
        return schema["$ref"].rsplit("/", 1)[-1]
    nullable = " | null" if schema.get("nullable") else ""
    if "enum" in schema:
        return " | ".join(quote(v) if isinstance(v, str) else json.dumps(v) for v in schema["enum"]) + nullable
    kind = schema.get("type")
    if kind == "string":
        return "string" + nullable
    if kind in ("integer", "number"):
        return "number" + nullable
    if kind == "boolean":
        return "boolean" + nullable
    if kind == "array":
        item = type_of(schema.get("items"))
        return (f"({item})" if " | " in item else item) + "[]" + nullable
    if kind == "object" or "properties" in schema or "additionalProperties" in schema:
        properties = schema.get("properties") or {}
        extra = schema.get("additionalProperties")
        if not properties:
            value = type_of(extra) if isinstance(extra, dict) and extra else "unknown"
            return f"Record<string, {value}>" + nullable
        required = set(schema.get("required") or [])
        fields = [f"{key(name)}{'' if name in required else '?'}: {type_of(sub)}" for name, sub in properties.items()]
        if extra:
            fields.append(f"[other: string]: {type_of(extra) if isinstance(extra, dict) else 'unknown'}")
        return "{ " + "; ".join(fields) + " }" + nullable
    return "unknown" + nullable


def interface(name: str, schema: dict[str, Any]) -> list[str]:
    properties = schema.get("properties") or {}
    if schema.get("type") != "object" and "properties" not in schema:
        return [f"export type {name} = {type_of(schema)};", ""]
    required = set(schema.get("required") or [])
    lines = [f"export interface {name} {{"]
    for prop, sub in properties.items():
        note = sub.get("description") if isinstance(sub, dict) else None
        if note:
            lines.append(f"  /** {note.replace('*/', '* /')} */")
        lines.append(f"  {key(prop)}{'' if prop in required else '?'}: {type_of(sub)};")
    extra = schema.get("additionalProperties")
    if extra:
        lines.append(f"  [other: string]: {type_of(extra) if isinstance(extra, dict) else 'unknown'};")
    lines += ["}", ""]
    return lines


def operation_name(method: str, path: str) -> str:
    """get + /api/robot/{id}/command -> getRobotByIdCommand (the shared /api prefix is dropped)."""
    parts: list[str] = []
    for segment in path.strip("/").split("/"):
        if segment == "api" and not parts:
            continue
        if segment.startswith("{") and segment.endswith("}"):
            parts.append("By" + camel(segment[1:-1]))
        else:
            parts.append(camel(segment))
    return method + "".join(parts)


def camel(text: str) -> str:
    words = [w for w in re.split(r"[^A-Za-z0-9]+", text) if w]
    return "".join(w[:1].upper() + w[1:] for w in words)


def parameters(path: str, operation: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """The path parameters (in the order of the path) and the query parameters of an operation."""
    declared = {p["name"]: p for p in operation.get("parameters", []) if p.get("in") == "path"}
    in_path = re.findall(r"\{([^}]+)\}", path)
    path_parameters = [declared.get(n, {"name": n, "in": "path", "required": True, "schema": {"type": "string"}}) for n in in_path]
    query = [p for p in operation.get("parameters", []) if p.get("in") == "query"]
    return path_parameters, query


def success_type(operation: dict[str, Any]) -> str:
    for status in sorted(operation.get("responses", {})):
        if status.startswith("2"):
            content = operation["responses"][status].get("content") or {}
            if "application/json" in content:
                return type_of(content["application/json"].get("schema"))
            return "void"
    return "void"


def operations(document: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    for path in sorted(document["paths"]):
        for method in METHODS:
            operation = document["paths"][path].get(method)
            if operation is None:
                continue
            name = operation_name(method, path)
            if name in seen:
                raise SystemExit(f"GENERATED_CLIENTS=FAIL two routes make the method name {name}: {seen[name]} and {method.upper()} {path}")
            seen[name] = f"{method.upper()} {path}"
            path_parameters, query = parameters(path, operation)
            body = (operation.get("requestBody") or {}).get("content", {}).get("application/json")
            found.append({
                "name": name,
                "method": method.upper(),
                "path": path,
                "path_parameters": path_parameters,
                "query": query,
                "body": type_of(body.get("schema")) if body else None,
                "body_required": bool((operation.get("requestBody") or {}).get("required")),
                "result": success_type(operation),
                "access": operation.get("x-access", "user"),
                "summary": operation.get("summary", ""),
            })
    return found


def arguments(op: dict[str, Any]) -> tuple[str, bool]:
    """The TypeScript parameter list of one method and whether the call may omit it entirely."""
    fields: list[str] = []
    required = False
    if op["path_parameters"]:
        inner = "; ".join(f"{key(p['name'])}: {type_of(p.get('schema', {'type': 'string'}))}" for p in op["path_parameters"])
        fields.append(f"path: {{ {inner} }}")
        required = True
    if op["query"]:
        needed = any(p.get("required") for p in op["query"])
        inner = "; ".join(f"{key(p['name'])}{'' if p.get('required') else '?'}: {type_of(p.get('schema', {'type': 'string'}))}" for p in op["query"])
        fields.append(f"query{'' if needed else '?'}: {{ {inner} }}")
        required = required or needed
    if op["body"] is not None:
        fields.append(f"body{'' if op['body_required'] else '?'}: {op['body']}")
        required = required or op["body_required"]
    if not fields:
        return "", False
    return "args" + ("" if required else "?") + ": { " + "; ".join(fields) + " }", required


def as_typescript(document: dict[str, Any]) -> str:
    ops = operations(document)
    lines = [f"// {HEADER}", "", "/* eslint-disable */", ""]
    for name in sorted(document.get("components", {}).get("schemas", {})):
        lines += interface(name, document["components"]["schemas"][name])
    lines += [
        "export interface HydraRequest {",
        "  readonly method: string;",
        "  readonly path: string;",
        "  readonly query: Readonly<Record<string, string>>;",
        "  readonly body: unknown;",
        "  readonly access: string;",
        "}",
        "",
        "/** Carries one request to the server and returns the decoded JSON of the answer (undefined when there is none). */",
        "export type HydraTransport = (request: HydraRequest) => Promise<unknown>;",
        "",
        "export function fillPath(template: string, values: Readonly<Record<string, string | number>> | undefined): string {",
        "  return template.replace(/\\{([^}]+)\\}/g, (_whole, name: string) => {",
        "    const value = values?.[name];",
        "    if (value === undefined || value === \"\") throw new Error(`missing path parameter ${name}`);",
        "    return encodeURIComponent(String(value));",
        "  });",
        "}",
        "",
        "export function queryOf(values: Readonly<Record<string, unknown>> | undefined): Record<string, string> {",
        "  const found: Record<string, string> = {};",
        "  for (const [name, value] of Object.entries(values ?? {})) {",
        "    if (value !== undefined && value !== null) found[name] = String(value);",
        "  }",
        "  return found;",
        "}",
        "",
        "export class HydraServerClient {",
        "  constructor(private readonly transport: HydraTransport) {}",
        "",
    ]
    for op in ops:
        signature, _ = arguments(op)
        note = op["summary"] or f"{op['method']} {op['path']}"
        path_expr = "fillPath(" + quote(op["path"]) + ", args?.path)" if op["path_parameters"] else quote(op["path"])
        query_expr = "queryOf(args?.query)" if op["query"] else "{}"
        body_expr = "args?.body" if op["body"] is not None else "undefined"
        lines += [
            f"  /** {note.replace('*/', '* /')} (access: {op['access']}) */",
            f"  {op['name']}({signature}): Promise<{op['result']}> {{",
            f"    return this.transport({{ method: {quote(op['method'])}, path: {path_expr}, query: {query_expr}, "
            f"body: {body_expr}, access: {quote(op['access'])} }}) as Promise<{op['result']}>;",
            "  }",
            "",
        ]
    lines += ["}", "", "export const HYDRA_CLIENT_OPERATIONS: readonly string[] = ["]
    lines += [f"  {quote(op['name'])}," for op in ops]
    lines += ["];", ""]
    return "\n".join(lines)


def outputs() -> dict[str, str]:
    return {TS_NAME: as_typescript(json.loads(FULL.read_text(encoding="utf-8")))}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail when a generated file is out of date")
    args = parser.parse_args(argv)
    produced = outputs()
    if args.check:
        stale = [name for name, text in produced.items()
                 if not (OUT / name).is_file() or (OUT / name).read_bytes().replace(b"\r\n", b"\n") != text.encode("utf-8")]
        if stale:
            print("GENERATED_CLIENTS=FAIL out of date: " + ", ".join(stale) + " (run python tools/generate_clients.py)", file=sys.stderr)
            return 1
        print(f"GENERATED_CLIENTS=PASS {len(produced)} files match the contract")
        return 0
    OUT.mkdir(exist_ok=True)
    for name, text in produced.items():
        (OUT / name).write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(produced)} files to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
