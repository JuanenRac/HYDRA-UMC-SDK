#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Dependency-free OpenAPI structural verification
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Structural checks for contracts/openapi/v1/*.openapi.json.

Deliberately stdlib-only (json + pathlib), matching every other script under
tools/ (generate_manifest.py, verify_contract_matrix.py) and ci_validate.py's
own dependency-free baseline - a real OpenAPI 3.x validator (e.g.
openapi-spec-validator) caught real issues while this document was first
written and is worth running by hand occasionally, but is not vendored here
just to keep this repository's own CI dependency-free. This script instead
catches the two mistakes most likely to survive hand-editing a document this
size: a $ref pointing at a components/schemas entry that does not exist, and
a path item with no real HTTP method under it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPENAPI_DIR = ROOT / "contracts" / "openapi" / "v1"
HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
REQUIRED_TOP_LEVEL_KEYS = ("openapi", "info", "paths", "components")


def fail(message: str) -> None:
    print(f"OPENAPI_VERIFY=FAIL {message}", file=sys.stderr)
    raise SystemExit(1)


def collect_refs(node: object, refs: list[str]) -> None:
    """Recursively collects every local ("#/...") $ref/mapping target."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("$ref",) and isinstance(value, str) and value.startswith("#/"):
                refs.append(value)
            elif key == "mapping" and isinstance(value, dict):
                for target in value.values():
                    if isinstance(target, str) and target.startswith("#/"):
                        refs.append(target)
            else:
                collect_refs(value, refs)
    elif isinstance(node, list):
        for item in node:
            collect_refs(item, refs)


def resolve_pointer(document: dict, pointer: str) -> bool:
    """Reports whether a '#/a/b/c' JSON Pointer resolves inside document."""
    node: object = document
    for segment in pointer.lstrip("#/").split("/"):
        if not isinstance(node, dict) or segment not in node:
            return False
        node = node[segment]
    return True


def verify_document(path: Path) -> tuple[int, int]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)}: not valid JSON ({exc})")

    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in document]
    if missing:
        fail(f"{path.relative_to(ROOT)}: missing required top-level key(s): {', '.join(missing)}")
    if not str(document["openapi"]).startswith("3."):
        fail(f"{path.relative_to(ROOT)}: openapi version {document['openapi']!r} is not an OpenAPI 3.x document")

    paths = document["paths"]
    if not paths:
        fail(f"{path.relative_to(ROOT)}: paths must not be empty")
    for route, item in paths.items():
        if not (HTTP_METHODS & item.keys()):
            fail(f"{path.relative_to(ROOT)}: path {route!r} declares no real HTTP method")

    refs: list[str] = []
    collect_refs(document, refs)
    broken = sorted({ref for ref in refs if not resolve_pointer(document, ref)})
    if broken:
        fail(f"{path.relative_to(ROOT)}: broken $ref/mapping target(s): {', '.join(broken)}")

    schema_count = len(document.get("components", {}).get("schemas", {}))
    return len(paths), schema_count


def main() -> int:
    documents = sorted(OPENAPI_DIR.glob("*.openapi.json"))
    if not documents:
        fail(f"no *.openapi.json documents found under {OPENAPI_DIR.relative_to(ROOT)}")

    total_paths = total_schemas = 0
    for document_path in documents:
        path_count, schema_count = verify_document(document_path)
        total_paths += path_count
        total_schemas += schema_count

    print(f"OPENAPI_VERIFY=PASS documents={len(documents)} paths={total_paths} schemas={total_schemas}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
