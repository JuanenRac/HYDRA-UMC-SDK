#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Route tables of the server contract for the clients
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Generate the table of the routes of the server for JSON, TypeScript, Kotlin and Dart.

The table is made from `contracts/openapi/v1/server.full.openapi.json`, which is itself generated from
`contracts/sources`. Each row says the method, the path, who may call it, the query parameters it reads and the status
codes it answers. A client copies the file it needs into its own `generated/` folder and tests that every route it
calls is in the table, instead of keeping a hand-written list of the routes it knows. Nothing here is edited by hand.

    python tools/generate_routes.py           write generated/
    python tools/generate_routes.py --check   fail when a generated file is out of date
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
FULL = ROOT / "contracts" / "openapi" / "v1" / "server.full.openapi.json"
OUT = ROOT / "generated"
HEADER = "Generated from the server contract by tools/generate_routes.py. Do not edit."
METHODS = ("get", "put", "post", "delete", "patch")


def rows(document: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for path in sorted(document["paths"]):
        for method in METHODS:
            operation = document["paths"][path].get(method)
            if operation is None:
                continue
            found.append({
                "method": method.upper(),
                "path": path,
                "access": operation.get("x-access", "user"),
                "group": operation["tags"][0] if operation.get("tags") else "",
                "query": sorted(p["name"] for p in operation.get("parameters", []) if p.get("in") == "query"),
                "statuses": sorted(operation.get("responses", {})),
            })
    return found


def quote(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def as_json(table: list[dict[str, Any]]) -> str:
    return json.dumps({"_comment": HEADER, "routes": table}, indent=2, ensure_ascii=False) + "\n"


def as_typescript(table: list[dict[str, Any]]) -> str:
    lines = [f"// {HEADER}", "",
             'export type HydraRouteAccess = "public" | "user" | "admin";', "",
             "export interface HydraRoute {",
             "  readonly method: string;", "  readonly path: string;", "  readonly access: string;", "  readonly group: string;",
             "  readonly query: readonly string[];", "  readonly statuses: readonly string[];", "}", "",
             "export const HYDRA_ROUTES: readonly HydraRoute[] = ["]
    for r in table:
        lines.append(f"  {{ method: {quote(r['method'])}, path: {quote(r['path'])}, access: {quote(r['access'])}, group: {quote(r['group'])}, "
                     f"query: [{', '.join(quote(q) for q in r['query'])}], statuses: [{', '.join(quote(s) for s in r['statuses'])}] }},")
    lines += ["];", ""]
    return "\n".join(lines)


def as_kotlin(table: list[dict[str, Any]]) -> str:
    lines = [f"// {HEADER}", "package hydra.umc.contracts", "",
             "data class HydraRoute(val method: String, val path: String, val access: String, val group: String, val query: List<String>, val statuses: List<String>)", "",
             "val HYDRA_ROUTES: List<HydraRoute> = listOf("]
    for r in table:
        path = r["path"].replace("$", "\\$")
        lines.append(f'    HydraRoute("{r["method"]}", "{path}", "{r["access"]}", "{r["group"]}", '
                     f'listOf({", ".join(quote(q) for q in r["query"])}), listOf({", ".join(quote(s) for s in r["statuses"])})),')
    lines += [")", ""]
    return "\n".join(lines)


def as_dart(table: list[dict[str, Any]]) -> str:
    lines = [f"// {HEADER}", "",
             "class HydraRoute {",
             "  const HydraRoute(this.method, this.path, this.access, this.group, this.query, this.statuses);",
             "  final String method;", "  final String path;", "  final String access;", "  final String group;",
             "  final List<String> query;", "  final List<String> statuses;", "}", "",
             "const List<HydraRoute> hydraRoutes = <HydraRoute>["]
    for r in table:
        path = r["path"].replace("$", "\\$")
        lines.append(f"  HydraRoute('{r['method']}', '{path}', '{r['access']}', '{r['group']}', "
                     f"<String>[{', '.join(repr(q) for q in r['query'])}], <String>[{', '.join(repr(s) for s in r['statuses'])}]),")
    lines += ["];", ""]
    return "\n".join(lines)


def outputs() -> dict[str, str]:
    table = rows(json.loads(FULL.read_text(encoding="utf-8")))
    return {
        "hydra-routes.json": as_json(table),
        "hydra-routes.ts": as_typescript(table),
        "HydraRoutes.kt": as_kotlin(table),
        "hydra_routes.dart": as_dart(table),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail when a generated file is out of date")
    args = parser.parse_args(argv)
    produced = outputs()
    if args.check:
        stale = [name for name, text in produced.items()
                 if not (OUT / name).is_file() or (OUT / name).read_bytes().replace(b"\r\n", b"\n") != text.encode("utf-8")]
        if stale:
            print("GENERATED_ROUTES=FAIL out of date: " + ", ".join(stale) + " (run python tools/generate_routes.py)", file=sys.stderr)
            return 1
        print(f"GENERATED_ROUTES=PASS {len(produced)} files match the contract")
        return 0
    OUT.mkdir(exist_ok=True)
    for name, text in produced.items():
        (OUT / name).write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(produced)} files to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
