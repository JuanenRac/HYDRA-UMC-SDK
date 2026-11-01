#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Types of the closed contracts for TypeScript, Kotlin and Dart
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Generate the TypeScript, Kotlin and Dart types of every closed JSON Schema.

`contracts/json-schema/v1/*.schema.json` is the single source. The files in
`generated/` are produced from it and are never edited by hand; a client copies
the one it needs into its own `generated/` folder, and its CI runs this tool
with `--check` (against a checkout of this SDK) to keep the copy honest.

    python tools/generate_types.py           write generated/
    python tools/generate_types.py --check   fail when a generated file is out of date

The mapping is deliberately small. An object with `properties` becomes a type
named after the schema file and, for objects inside it, after the parent and
the field. `enum` and `const` become a union of literals in TypeScript and a
string elsewhere. Keywords the types cannot say (`anyOf`, `allOf`, `if`) are left
to the validators of the SDK; a field with no usable `type` is untyped.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "contracts" / "json-schema" / "v1"
OUT = ROOT / "generated"
HEADER = "Generated from the HYDRA-UMC JSON Schemas by tools/generate_types.py. Do not edit."
KOTLIN_PACKAGE = "hydra.umc.contracts"

KOTLIN_RESERVED = {"as", "break", "class", "continue", "do", "else", "false", "for", "fun", "if", "in", "interface", "is", "null", "object", "package",
                   "return", "super", "this", "throw", "true", "try", "typealias", "typeof", "val", "var", "when", "while"}
DART_RESERVED = {"abstract", "as", "assert", "async", "await", "break", "case", "catch", "class", "const", "continue", "covariant", "default", "deferred", "do",
                 "dynamic", "else", "enum", "export", "extends", "extension", "external", "factory", "false", "final", "finally", "for", "get", "if", "implements",
                 "import", "in", "interface", "is", "late", "library", "mixin", "new", "null", "on", "operator", "part", "required", "rethrow", "return", "set",
                 "static", "super", "switch", "this", "throw", "true", "try", "typedef", "var", "void", "while", "with", "yield"}


def pascal(name: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in re.split(r"[^0-9A-Za-z]+", name) if part)


class Ty:
    """A type: kind is string, integer, number, boolean, literal, enum, array, map, object or any."""

    def __init__(self, kind: str, *, nullable: bool = False, values: list[Any] | None = None, inner: "Ty | None" = None, name: str = "") -> None:
        self.kind, self.nullable, self.values, self.inner, self.name = kind, nullable, values or [], inner, name


class Obj:
    def __init__(self, name: str) -> None:
        self.name = name
        self.fields: list[tuple[str, Ty, bool]] = []


def resolve(schema: Any, owner: str, objects: list[Obj]) -> Ty:
    if not isinstance(schema, dict):
        return Ty("any")
    if "const" in schema:
        return Ty("literal", values=[schema["const"]])
    if "enum" in schema:
        return Ty("enum", values=list(schema["enum"]))
    kind = schema.get("type")
    nullable = False
    if isinstance(kind, list):
        nullable = "null" in kind
        rest = [item for item in kind if item != "null"]
        kind = rest[0] if len(rest) == 1 else None
    if kind == "array":
        return Ty("array", nullable=nullable, inner=resolve(schema.get("items"), owner, objects))
    if kind == "object" or (kind is None and "properties" in schema):
        if schema.get("properties"):
            return Ty("object", nullable=nullable, name=build(schema, owner, objects).name)
        extra = schema.get("additionalProperties")
        if isinstance(extra, dict) and extra.get("type"):
            return Ty("map", nullable=nullable, inner=resolve(extra, owner, objects))
        return Ty("map", nullable=nullable, inner=Ty("any"))
    if kind in ("string", "integer", "number", "boolean"):
        return Ty(kind, nullable=nullable)
    return Ty("any", nullable=nullable)


def build(schema: dict[str, Any], name: str, objects: list[Obj]) -> Obj:
    result = Obj(name)
    required = set(schema.get("required", []))
    objects.append(result)
    for prop, child in schema.get("properties", {}).items():
        result.fields.append((prop, resolve(child, name + pascal(prop), objects), prop in required))
    return result


def load() -> list[Obj]:
    objects: list[Obj] = []
    for path in sorted(SCHEMAS.glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        if schema.get("properties"):
            build(schema, pascal(path.name.split(".")[0]), objects)
    return objects


# ---------------------------------------------------------------- TypeScript
def ts_type(ty: Ty) -> str:
    base: str
    if ty.kind == "literal":
        return " | ".join(json.dumps(v) for v in ty.values)
    if ty.kind == "enum":
        return " | ".join(json.dumps(v) for v in ty.values)
    if ty.kind in ("integer", "number"):
        base = "number"
    elif ty.kind in ("string", "boolean"):
        base = ty.kind
    elif ty.kind == "array":
        inner = ts_type(ty.inner or Ty("any"))
        base = f"({inner})[]" if "|" in inner else f"{inner}[]"
    elif ty.kind == "map":
        base = f"Record<string, {ts_type(ty.inner or Ty('any'))}>"
    elif ty.kind == "object":
        base = ty.name
    else:
        base = "unknown"
    return base + (" | null" if ty.nullable else "")


def render_ts(objects: list[Obj]) -> str:
    lines = [f"// {HEADER}", ""]
    for obj in objects:
        lines.append(f"export interface {obj.name} {{")
        for name, ty, required in obj.fields:
            key = name if re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", name) else json.dumps(name)
            lines.append(f"  {key}{'' if required else '?'}: {ts_type(ty)};")
        lines += ["  [extra: string]: unknown;", "}", ""]
    return "\n".join(lines)


# -------------------------------------------------------------------- Kotlin
def kt_type(ty: Ty) -> str:
    if ty.kind in ("string", "literal", "enum"):
        base = "String" if ty.kind != "literal" or isinstance(ty.values[0], str) else ("Boolean" if isinstance(ty.values[0], bool) else "Double")
        if ty.kind == "enum" and not all(isinstance(v, str) for v in ty.values):
            base = "Any"
    elif ty.kind == "integer":
        base = "Long"
    elif ty.kind == "number":
        base = "Double"
    elif ty.kind == "boolean":
        base = "Boolean"
    elif ty.kind == "array":
        base = f"List<{kt_type(ty.inner or Ty('any'))}>"
    elif ty.kind == "map":
        base = f"Map<String, {kt_type(ty.inner or Ty('any'))}>"
    elif ty.kind == "object":
        base = ty.name
    else:
        base = "Any"
    if base == "Any" or ty.nullable:
        return base + "?" if not base.endswith("?") else base
    return base


def kt_name(name: str) -> str:
    safe = name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) else re.sub(r"[^0-9A-Za-z_]", "_", name)
    return f"`{safe}`" if safe in KOTLIN_RESERVED else safe


def render_kt(objects: list[Obj]) -> str:
    lines = [f"// {HEADER}", f"package {KOTLIN_PACKAGE}", ""]
    for obj in objects:
        lines.append(f"data class {obj.name}(")
        parts = []
        for name, ty, required in obj.fields:
            kind = kt_type(ty)
            if required and not kind.endswith("?"):
                parts.append(f"    val {kt_name(name)}: {kind}")
            else:
                parts.append(f"    val {kt_name(name)}: {kind.rstrip('?')}? = null")
        lines.append(",\n".join(parts) if parts else "")
        lines += [")", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------------- Dart
def dart_type(ty: Ty) -> str:
    if ty.kind in ("string", "literal", "enum"):
        base = "String"
        if ty.kind in ("literal", "enum") and not all(isinstance(v, str) for v in ty.values):
            base = "Object"
    elif ty.kind == "integer":
        base = "int"
    elif ty.kind == "number":
        base = "double"
    elif ty.kind == "boolean":
        base = "bool"
    elif ty.kind == "array":
        base = f"List<{dart_type(ty.inner or Ty('any'))}>"
    elif ty.kind == "map":
        base = f"Map<String, {dart_type(ty.inner or Ty('any'))}>"
    elif ty.kind == "object":
        base = ty.name
    else:
        return "Object?"
    return base + ("?" if ty.nullable else "")


def dart_decode(expr: str, ty: Ty, depth: int = 0) -> str:
    if ty.kind in ("string",):
        return f"{expr} as String"
    if ty.kind in ("literal", "enum"):
        return f"{expr} as {dart_type(Ty(ty.kind, values=ty.values))}"
    if ty.kind == "integer":
        return f"({expr} as num).toInt()"
    if ty.kind == "number":
        return f"({expr} as num).toDouble()"
    if ty.kind == "boolean":
        return f"{expr} as bool"
    if ty.kind == "object":
        return f"{ty.name}.fromJson(Map<String, dynamic>.from({expr} as Map))"
    var = f"e{depth}"
    if ty.kind == "array":
        inner = ty.inner or Ty("any")
        return f"({expr} as List).map(({var}) => {dart_decode(var, inner, depth + 1)}).toList()"
    if ty.kind == "map":
        inner = ty.inner or Ty("any")
        if inner.kind == "any":
            return f"Map<String, dynamic>.from({expr} as Map)"
        return f"({expr} as Map).map((k{depth}, {var}) => MapEntry(k{depth} as String, {dart_decode(var, inner, depth + 1)}))"
    return expr


def dart_encode(expr: str, ty: Ty, depth: int = 0) -> str:
    var = f"e{depth}"
    if ty.kind == "object":
        return f"{expr}.toJson()"
    if ty.kind == "array":
        inner = ty.inner or Ty("any")
        if inner.kind in ("object", "array", "map"):
            return f"{expr}.map(({var}) => {dart_encode(var, inner, depth + 1)}).toList()"
        return expr
    if ty.kind == "map":
        inner = ty.inner or Ty("any")
        if inner.kind in ("object", "array", "map"):
            return f"{expr}.map((k{depth}, {var}) => MapEntry(k{depth}, {dart_encode(var, inner, depth + 1)}))"
        return expr
    return expr


def dart_name(name: str) -> str:
    safe = re.sub(r"[^0-9A-Za-z_]", "_", name)
    if safe[:1].isdigit():
        safe = "_" + safe
    return safe + "_" if safe in DART_RESERVED else safe


def render_dart(objects: list[Obj]) -> str:
    lines = [f"// {HEADER}", "// ignore_for_file: non_constant_identifier_names, constant_identifier_names", ""]
    for obj in objects:
        lines.append(f"class {obj.name} {{")
        for name, ty, required in obj.fields:
            kind = dart_type(ty)
            nullable = (not required) or kind.endswith("?")
            lines.append(f"  final {kind.rstrip('?') + ('?' if nullable else '')} {dart_name(name)};")
        ctor = ", ".join(f"{'required ' if (required and not dart_type(ty).endswith('?')) else ''}this.{dart_name(name)}" for name, ty, required in obj.fields)
        lines.append(f"  const {obj.name}({{{ctor}}});" if obj.fields else f"  const {obj.name}();")
        lines.append(f"  factory {obj.name}.fromJson(Map<String, dynamic> json) => {obj.name}(")
        for name, ty, required in obj.fields:
            key = json.dumps(name)
            if ty.kind == "any":
                lines.append(f"        {dart_name(name)}: json[{key}],")
            else:
                lines.append(f"        {dart_name(name)}: json[{key}] == null ? null : {dart_decode(f'json[{key}]', ty)},"
                             if not (required and not ty.nullable) else f"        {dart_name(name)}: {dart_decode(f'json[{key}]', ty)},")
        lines.append("      );")
        lines.append("  Map<String, dynamic> toJson() => {")
        for name, ty, required in obj.fields:
            key = json.dumps(name)
            value = dart_encode(dart_name(name), ty)
            if required and not ty.nullable:
                lines.append(f"        {key}: {value},")
            elif value == dart_name(name):
                lines.append(f"        if ({dart_name(name)} != null) {key}: {value},")
            else:
                lines.append(f"        if ({dart_name(name)} != null) {key}: {dart_encode(dart_name(name) + '!', ty)},")
        lines += ["      };", "}", ""]
    return "\n".join(lines)


def outputs() -> dict[str, str]:
    objects = load()
    return {
        "hydra-contracts.ts": render_ts(objects),
        "HydraContracts.kt": render_kt(objects),
        "hydra_contracts.dart": render_dart(objects),
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
            print("GENERATED_TYPES=FAIL out of date: " + ", ".join(stale) + " (run python tools/generate_types.py)", file=sys.stderr)
            return 1
        print(f"GENERATED_TYPES=PASS {len(produced)} files match the schemas")
        return 0
    OUT.mkdir(exist_ok=True)
    for name, text in produced.items():
        (OUT / name).write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(produced)} files to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
