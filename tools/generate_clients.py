#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Typed server client generated from the OpenAPI contract
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Generate the typed client of the server routes (TypeScript, Kotlin and Dart) from the full OpenAPI document.

The source is `contracts/openapi/v1/server.full.openapi.json`, the same document the route tables come from. For every
operation the generator writes one method whose name is made from the verb and the path, whose arguments are the path
parameters, the query parameters and the body, and whose result is the type of the first 2xx JSON answer. Every named
schema of the document becomes an interface. The client never touches the network: it builds the request and hands it
to an injectable transport, so an app keeps its own fetch, its own token and its own error handling. Nothing in the
output is edited by hand. A route may also take a binary body (`application/octet-stream`), answer in text or in bytes, and
declare response headers (the `ETag` of the settings): the request then carries `contentType` and `responseType`, and a method
named `<route>WithHeaders` asks the transport for a `{ body, headers }` reply. The Kotlin and Dart clients have the same shape and no dependency: the transport is a
`suspend` function interface in Kotlin and a `Future` function in Dart, and every object of the contract is a class
with fields (a `data class` in Kotlin, a `const` class in Dart) with `fromJson` and `toJson` over the plain JSON model
(maps, lists and scalars), so any JSON library can feed them and none is needed. The rules of the classes are written
above the `Native` model below: required and optional fields, `additionalProperties` open or closed, schemas that refer
to themselves, enums and the schemas that stay aliases. TypeScript keeps one `interface` with fields per named schema.

Besides the three clients the generator writes two round trip files into conformance/generated-clients (an example of
every class is read with `fromJson` and written with `toJson`, and must come back equal); a smoke program compiled in
generated-clients.yml runs them. `--spec FILE --out DIR` makes the same five files from another OpenAPI document (the
synthetic one of conformance/generated-clients/synthetic, which covers what the server contract does not use).

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
KT_NAME = "HydraServerClient.kt"
DART_NAME = "hydra_server_client.dart"
KOTLIN_PACKAGE = "hydra.umc.client"
KOTLIN_WORDS = frozenset("as break class continue do else false for fun if in interface is null object package return super this throw true try typealias typeof val var when while".split())
DART_WORDS = frozenset("abstract as assert async await break case catch class const continue covariant default deferred do dynamic else enum export extends extension external factory false final finally for get hide if implements import in interface is late library mixin new null of on operator part required rethrow return set show static super switch sync this throw true try typedef var void while with yield".split())


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
        return ("Uint8Array" if schema.get("format") == "binary" else "string") + nullable
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


def success_response(operation: dict[str, Any]) -> tuple[str, dict[str, Any] | None, list[str]]:
    """The kind of the first 2xx answer (json, text, binary or none), its schema and the response headers it declares."""
    for status in sorted(operation.get("responses", {})):
        if status.startswith("2"):
            answer = operation["responses"][status]
            content = answer.get("content") or {}
            headers = list((answer.get("headers") or {}).keys())
            if "application/json" in content:
                return "json", content["application/json"].get("schema") or {}, headers
            for media in content:
                if "octet" in media:
                    return "binary", {"type": "string", "format": "binary"}, headers
                if media.startswith("text/") or media.endswith(("json", "ndjson", "jsonl")):
                    return "text", {"type": "string"}, headers
            return "none", None, headers
    return "none", None, []


def success_type(operation: dict[str, Any]) -> str:
    schema = success_response(operation)[1]
    return type_of(schema) if schema is not None else "void"


def success_schema(operation: dict[str, Any]) -> dict[str, Any] | None:
    """The schema of the first 2xx answer, an empty dict when a JSON answer declares none, None when there is no body."""
    return success_response(operation)[1]


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
            if name.endswith("WithHeaders"):
                raise SystemExit(f"GENERATED_CLIENTS=FAIL the method name {name} ends in WithHeaders, which the generator keeps for the reply variant")
            path_parameters, query = parameters(path, operation)
            headers = [p for p in operation.get("parameters", []) if p.get("in") == "header"]
            content = (operation.get("requestBody") or {}).get("content", {})
            media = "application/json" if "application/json" in content else next(iter(content), None)
            body = content[media] if media else None
            if body is not None and media != "application/json":
                body = {**body, "schema": {"type": "string", "format": "binary"}}
            answer, _, reply_headers = success_response(operation)
            found.append({
                "name": name,
                "method": method.upper(),
                "path": path,
                "path_parameters": path_parameters,
                "query": query,
                "headers": headers,
                "body": type_of(body.get("schema")) if body else None,
                "body_schema": body.get("schema") if body else None,
                "body_media": media if body else None,
                "answer": answer,
                "reply_headers": reply_headers,
                "body_required": bool((operation.get("requestBody") or {}).get("required")),
                "result": success_type(operation),
                "result_schema": success_schema(operation),
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
    if op["headers"]:
        needed = any(p.get("required") for p in op["headers"])
        inner = "; ".join(f"{quote(p['name'])}{'' if p.get('required') else '?'}: {type_of(p.get('schema', {'type': 'string'}))}" for p in op["headers"])
        fields.append(f"headers{'' if needed else '?'}: {{ {inner} }}")
        required = required or needed
    if op["body"] is not None:
        fields.append(f"body{'' if op['body_required'] else '?'}: {op['body']}")
        required = required or op["body_required"]
    if not fields:
        return "", False
    return "args" + ("" if required else "?") + ": { " + "; ".join(fields) + " }", required


def request_extras(op: dict[str, Any], with_headers: bool) -> list[tuple[str, str | list[str]]]:
    """The request fields that are not the default (a JSON body, a JSON or empty answer, no reply headers) as (field, value)."""
    extras: list[tuple[str, str | list[str]]] = []
    if op["body"] is not None and op["body_media"] != "application/json":
        extras.append(("contentType", op["body_media"]))
    if op["answer"] in ("text", "binary"):
        extras.append(("responseType", op["answer"]))
    if with_headers:
        extras.append(("replyHeaders", list(op["reply_headers"])))
    return extras


def extras_text(op: dict[str, Any], with_headers: bool, assign: str, spelling: Any, listing: Any) -> str:
    """The extra request fields as `, field<assign>value` pieces: a text through `spelling`, a list of header names through `listing`."""
    pieces = []
    for field, value in request_extras(op, with_headers):
        text = listing([spelling(v) for v in value]) if isinstance(value, list) else spelling(value)
        pieces.append(f", {field}{assign}{text}")
    return "".join(pieces)


def ts_list(items: list[str]) -> str:
    return "[" + ", ".join(items) + "]"


def kt_list(items: list[str]) -> str:
    return "listOf(" + ", ".join(items) + ")"


def dart_list(items: list[str]) -> str:
    return "const <String>[" + ", ".join(items) + "]"


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
        "  readonly headers: Readonly<Record<string, string>>;",
        "  readonly body: unknown;",
        "  readonly access: string;",
        "  /** The media type of the body when it is not JSON (a binary image goes as application/octet-stream). */",
        "  readonly contentType?: string;",
        "  /** How the answer is read when it is not JSON: text (a string) or binary (a Uint8Array). */",
        "  readonly responseType?: \"text\" | \"binary\";",
        "  /** The response headers the contract declares for the route, set for the WithHeaders methods: the transport answers with a HydraReply that holds them under these names. */",
        "  readonly replyHeaders?: readonly string[];",
        "}",
        "",
        "/** The answer of a route that declares response headers: the decoded body and the headers under their declared names (ETag, X-Next-Cursor). */",
        "export interface HydraReply<T> {",
        "  readonly body: T;",
        "  readonly headers: Readonly<Record<string, string>>;",
        "}",
        "",
        "/** Carries one request to the server and returns the decoded answer (undefined when there is none); a request with replyHeaders gets a HydraReply. */",
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
        "  private readonly transport: HydraTransport;",
        "  constructor(transport: HydraTransport) {",
        "    this.transport = transport;",
        "  }",
        "",
    ]
    for op in ops:
        signature, _ = arguments(op)
        note = op["summary"] or f"{op['method']} {op['path']}"
        path_expr = "fillPath(" + quote(op["path"]) + ", args?.path)" if op["path_parameters"] else quote(op["path"])
        query_expr = "queryOf(args?.query)" if op["query"] else "{}"
        headers_expr = "queryOf(args?.headers)" if op["headers"] else "{}"
        body_expr = "args?.body" if op["body"] is not None else "undefined"
        send = (f"this.transport({{ method: {quote(op['method'])}, path: {path_expr}, query: {query_expr}, "
                f"headers: {headers_expr}, body: {body_expr}, access: {quote(op['access'])}")
        plain = extras_text(op, False, ": ", quote, ts_list)
        lines += [
            f"  /** {note.replace('*/', '* /')} (access: {op['access']}) */",
            f"  {op['name']}({signature}): Promise<{op['result']}> {{",
            f"    return {send}{plain} }}) as Promise<{op['result']}>;",
            "  }",
            "",
        ]
        if op["reply_headers"]:
            extras = extras_text(op, True, ": ", quote, ts_list)
            lines += [
                f"  /** {note.replace('*/', '* /')} (access: {op['access']}); the reply also holds the response headers {', '.join(op['reply_headers'])}. */",
                f"  {op['name']}WithHeaders({signature}): Promise<HydraReply<{op['result']}>> {{",
                f"    return {send}{extras} }}) as Promise<HydraReply<{op['result']}>>;",
                "  }",
                "",
            ]
    lines += ["}", "", "export const HYDRA_CLIENT_OPERATIONS: readonly string[] = ["]
    lines += [f"  {quote(op['name'])}," for op in ops]
    lines += ["];", ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------------------------------------------------
# Kotlin and Dart. Both clients share the plan below; only the spelling of types and calls differs.
# --------------------------------------------------------------------------------------------------------------------

class Flavor:
    """The spelling of one language: its types, its reserved words and its way to mark an optional value."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.kotlin = name == "kotlin"
        self.words = KOTLIN_WORDS if self.kotlin else DART_WORDS
        self.scalars = ({"string": "String", "integer": "Long", "number": "Double", "boolean": "Boolean"} if self.kotlin
                        else {"string": "String", "integer": "int", "number": "num", "boolean": "bool"})
        self.bytes = "ByteArray" if self.kotlin else "List<int>"
        self.any = "Any?" if self.kotlin else "dynamic"
        self.object = "Map<String, Any?>" if self.kotlin else "Map<String, dynamic>"
        self.list = "List<Any?>" if self.kotlin else "List<dynamic>"

    def optional(self, text: str) -> str:
        return text if text.endswith("?") or text == "dynamic" else text + "?"


def kind_of(schema: dict[str, Any]) -> tuple[str | None, bool]:
    """The single JSON type of a schema and whether it also accepts null (a type list such as ["string", "null"])."""
    kind = schema.get("type")
    nullable = bool(schema.get("nullable"))
    if isinstance(kind, list):
        nullable = nullable or "null" in kind
        kind = next((k for k in kind if k != "null"), None)
    if not isinstance(kind, str):
        return None, nullable
    return kind, nullable


def native_type(schema: dict[str, Any] | None, flavor: Flavor, cyclic: frozenset[str]) -> str:
    """The Kotlin or Dart type of a schema; objects and arrays are the plain JSON model so no library is needed."""
    if not schema:
        return flavor.any
    if "$ref" in schema:
        short = schema["$ref"].rsplit("/", 1)[-1]
        return flavor.any if short in cyclic else "Hydra" + short
    kind, nullable = kind_of(schema)
    if "enum" in schema and kind is None:
        values = [v for v in schema["enum"] if v is not None]
        kind = "string" if values and all(isinstance(v, str) for v in values) else None
        nullable = nullable or len(values) != len(schema["enum"])
    if kind == "string" and schema.get("format") == "binary":
        result = flavor.bytes
    elif kind in flavor.scalars:
        result = flavor.scalars[kind]
    elif kind == "array":
        item = native_type(schema.get("items"), flavor, cyclic)
        result = f"List<{item}>" if flavor.kotlin else flavor.list
    elif kind == "object" or "properties" in schema or "additionalProperties" in schema:
        extra = schema.get("additionalProperties")
        if flavor.kotlin and not schema.get("properties") and isinstance(extra, dict) and extra:
            result = f"Map<String, {native_type(extra, flavor, cyclic)}>"
        else:
            result = flavor.object
    else:
        return flavor.any
    return flavor.optional(result) if nullable else result


def refs_of(schema: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(schema, dict):
        if "$ref" in schema:
            found.add(schema["$ref"].rsplit("/", 1)[-1])
        for value in schema.values():
            found |= refs_of(value)
    elif isinstance(schema, list):
        for value in schema:
            found |= refs_of(value)
    return found


def cyclic_schemas(schemas: dict[str, Any]) -> frozenset[str]:
    """Names of the schemas that reach themselves through references: an alias cannot be recursive."""
    graph = {name: refs_of(body) for name, body in schemas.items()}
    cyclic: set[str] = set()
    for start in graph:
        stack, seen = list(graph[start]), set()
        while stack:
            current = stack.pop()
            if current == start:
                cyclic.add(start)
                break
            if current in seen or current not in graph:
                continue
            seen.add(current)
            stack.extend(graph[current])
    return frozenset(cyclic)


def identifier(text: str, flavor: Flavor, taken: set[str]) -> str:
    """A lowerCamel identifier made from a parameter name, never a reserved word, never one already used."""
    words = [w for w in re.split(r"[^A-Za-z0-9]+", text) if w]
    name = (words[0][:1].lower() + words[0][1:] if words else "value") + "".join(w[:1].upper() + w[1:] for w in words[1:])
    if name[:1].isdigit():
        name = "p" + name
    if name in flavor.words:
        name += "Value"
    while name in taken:
        name += "2"
    taken.add(name)
    return name


def kt_string(text: str) -> str:
    """A Kotlin string literal: JSON escapes plus the dollar sign, which Kotlin reads as a template."""
    return quote(text).replace("$", "\\$")


def one_line(text: str) -> str:
    return " ".join(str(text).split()).replace("*/", "* /")


# --------------------------------------------------------------------------------------------------------------------
# The model: a class with fields for every object of the contract, in Kotlin and in Dart.
#
#   - A named schema with properties, and every inline object with properties (a request body, an answer, a nested
#     object), is a class: a `data class` in Kotlin, a `const` class in Dart. `fromJson` reads the plain JSON model
#     (what the transport hands back) and `toJson` writes it again, so no JSON library is needed.
#   - Field names are the wire names in lowerCamelCase (`schema_version` is `schemaVersion`); `toJson` writes the wire
#     names again.
#   - A required field must be present and of its type, or `fromJson` throws; an optional field is nullable and left
#     out of `toJson` while it is null (an explicit JSON null of an optional field reads as absent).
#   - `additionalProperties`: `false` or absent means a closed object (a key the contract does not list is dropped when
#     the object is read); `true` or a schema means an open one, and the unlisted keys are kept in the field
#     `additionalProperties` (typed by that schema) and written back by `toJson`, so nothing is lost on the way.
#   - A schema that refers to itself, directly or through other schemas, is an ordinary recursive class (the field that
#     closes the loop is optional or a list in a well-formed contract; the generator needs no special case).
#   - An enum is its base type (String): the server owns the set of values and a client must not fail on a new one.
#   - A named schema that is not an object with properties (a map, a list, a scalar) stays an alias of its plain type.
# --------------------------------------------------------------------------------------------------------------------

KOTLIN_MEMBERS = frozenset("toJson fromJson hashCode toString equals copy json jsonOut Companion knownKeys".split())
DART_MEMBERS = frozenset("toJson fromJson hashCode toString runtimeType noSuchMethod json hydraOut".split())


class Native:
    """One type of the model: its spelling, how a JSON value becomes it and how it becomes a JSON value again.

    `decode(expr, depth)` and `encode(expr, depth)` return an expression; `depth` names the variables of nested lambdas.
    `plain` is true when encoding changes nothing, `call` is the member call that encodes a class (`.toJson()`),
    `anything` marks the untyped value and `inner` the non-null type of a nullable one."""

    def __init__(self, spelling: str, decode: Any, encode: Any, *, plain: bool = False, anything: bool = False,
                 call: str | None = None, inner: "Native | None" = None) -> None:
        self.type = spelling
        self.decode = decode
        self.encode = encode
        self.plain = plain
        self.anything = anything
        self.call = call
        self.inner = inner

    @property
    def nullable(self) -> bool:
        return self.anything or self.inner is not None


def is_class(schema: dict[str, Any]) -> bool:
    """An object with at least one property is a class; any other schema stays an alias of a plain type."""
    kind, _ = kind_of(schema)
    return bool(schema.get("properties")) and kind in (None, "object")


class Builder:
    """Turns the schemas of one document into Natives for one language and collects the classes they need."""

    def __init__(self, document: dict[str, Any], flavor: Flavor, package: str = KOTLIN_PACKAGE) -> None:
        self.flavor = flavor
        self.kotlin = flavor.kotlin
        self.package = package
        self.schemas: dict[str, Any] = document.get("components", {}).get("schemas", {})
        self.reserved = {"Hydra" + name for name, body in self.schemas.items() if is_class(body)}
        self.named: dict[str, Native] = {}
        self.natives: dict[str, Native] = {}
        self.signatures: dict[str, str] = {}
        self.defs: dict[str, dict[str, Any]] = {}
        self.stack: list[str] = []
        self.map_fn = "hydraMap" if self.kotlin else "_hydraMap"
        self.any_type = flavor.any

    # -- the building blocks ------------------------------------------------------------------------------------------

    def anything(self) -> Native:
        return Native(self.any_type, lambda e, d: e, lambda e, d: e, plain=True, anything=True)

    def scalar(self, kind: str) -> Native:
        spelling = self.flavor.scalars[kind]
        if self.kotlin:
            casts = {"string": "{e} as String", "boolean": "{e} as Boolean", "integer": "({e} as Number).toLong()",
                     "number": "({e} as Number).toDouble()"}
        else:
            casts = {"string": "{e} as String", "boolean": "{e} as bool", "integer": "({e} as num).toInt()", "number": "{e} as num"}
        cast = casts[kind]
        return Native(spelling, lambda e, d: cast.replace("{e}", e), lambda e, d: e, plain=True)

    def binary(self) -> Native:
        if self.kotlin:
            return Native("ByteArray", lambda e, d: f"{e} as ByteArray", lambda e, d: e, plain=True)
        return Native("List<int>", lambda e, d: f"List<int>.from({e} as List)", lambda e, d: e, plain=True)

    def nullable(self, inner: Native) -> Native:
        if inner.nullable:
            return inner
        if self.kotlin:
            def decode(e: str, d: int) -> str:
                return f"{e}?.let {{ v{d} -> {inner.decode(f'v{d}', d + 1)} }}"

            def encode(e: str, d: int) -> str:
                if inner.call:
                    return f"{e}?{inner.call}"
                if inner.plain:
                    return e
                return f"{e}?.let {{ v{d} -> {inner.encode(f'v{d}', d + 1)} }}"
        else:
            def decode(e: str, d: int) -> str:
                return f"{e} == null ? null : {inner.decode(e, d)}"

            def encode(e: str, d: int) -> str:
                if inner.call:
                    return f"{e}?{inner.call}"
                if inner.plain:
                    return e
                return f"_hydraNullable({e}, (v{d}) => {inner.encode(f'v{d}', d + 1)})"
        return Native(inner.type + "?", decode, encode, plain=inner.plain, inner=inner)

    def array(self, item: Native) -> Native:
        spelling = f"List<{item.type}>"
        if self.kotlin:
            def decode(e: str, d: int) -> str:
                if item.anything:
                    return f"hydraList({e})"
                return f"hydraList({e}).map {{ v{d} -> {item.decode(f'v{d}', d + 1)} }}"

            def encode(e: str, d: int) -> str:
                return e if item.plain else f"{e}.map {{ v{d} -> {item.encode(f'v{d}', d + 1)} }}"
        else:
            def decode(e: str, d: int) -> str:
                if item.anything:
                    return f"List<dynamic>.from({e} as List)"
                return f"({e} as List).map((v{d}) => {item.decode(f'v{d}', d + 1)}).toList()"

            def encode(e: str, d: int) -> str:
                return e if item.plain else f"{e}.map((v{d}) => {item.encode(f'v{d}', d + 1)}).toList()"
        return Native(spelling, decode, encode, plain=item.plain)

    def keyed(self, item: Native) -> Native:
        """A map from text to `item`: a schema with additionalProperties and no properties, or the open part of a class."""
        spelling = f"Map<String, {item.type}>"
        if self.kotlin:
            def decode(e: str, d: int) -> str:
                if item.anything:
                    return f"hydraMap({e})"
                return f"hydraMap({e}).mapValues {{ (_, v{d}) -> {item.decode(f'v{d}', d + 1)} }}"

            def encode(e: str, d: int) -> str:
                return e if item.plain else f"{e}.mapValues {{ (_, v{d}) -> {item.encode(f'v{d}', d + 1)} }}"
        else:
            def decode(e: str, d: int) -> str:
                if item.anything:
                    return f"_hydraMap({e})"
                return (f"<String, {item.type}>{{for (final entry{d} in _hydraMap({e}).entries) "
                        f"entry{d}.key: {item.decode(f'entry{d}.value', d + 1)}}}")

            def encode(e: str, d: int) -> str:
                if item.plain:
                    return e
                return f"<String, dynamic>{{for (final entry{d} in {e}.entries) entry{d}.key: {item.encode(f'entry{d}.value', d + 1)}}}"
        return Native(spelling, decode, encode, plain=item.plain)

    # -- schemas ------------------------------------------------------------------------------------------------------

    def native(self, schema: dict[str, Any] | None, ctx: str) -> Native:
        if not schema:
            return self.anything()
        if "$ref" in schema:
            return self.reference(schema["$ref"].rsplit("/", 1)[-1])
        for word in ("anyOf", "oneOf"):
            if word in schema:
                members = [m for m in schema[word] if m != {"type": "null"}]
                if len(members) != 1:
                    return self.anything()
                inner = self.native(members[0], ctx)
                return self.nullable(inner) if len(members) != len(schema[word]) else inner
        if "allOf" in schema and len(schema["allOf"]) == 1:
            return self.native(schema["allOf"][0], ctx)
        kind, nullable = kind_of(schema)
        if kind is None and "const" in schema:
            kind = {str: "string", bool: "boolean", int: "integer", float: "number"}.get(type(schema["const"]))
        if "enum" in schema and kind is None:
            values = [v for v in schema["enum"] if v is not None]
            kind = "string" if values and all(isinstance(v, str) for v in values) else None
            nullable = nullable or len(values) != len(schema["enum"])
        if kind == "string" and schema.get("format") == "binary":
            result = self.binary()
        elif kind in self.flavor.scalars:
            result = self.scalar(kind)
        elif kind == "array":
            result = self.array(self.native(schema.get("items"), ctx + "Item"))
        elif kind == "object" or "properties" in schema or "additionalProperties" in schema:
            extra = schema.get("additionalProperties")
            if schema.get("properties"):
                result = self.klass(ctx, schema)
            elif isinstance(extra, dict) and extra:
                result = self.keyed(self.native(extra, ctx + "Value"))
            else:
                result = self.keyed(self.anything())
        else:
            return self.anything()
        return self.nullable(result) if nullable else result

    def reference(self, short: str) -> Native:
        if short in self.named:
            return self.named[short]
        body = self.schemas.get(short)
        if body is None:
            return self.anything()
        if is_class(body):
            result = self.klass(short, body, named=True)
        else:
            if short in self.stack:
                return self.anything()
            self.stack.append(short)
            result = self.native({k: v for k, v in body.items() if k != "description"}, short)
            self.stack.pop()
        self.named[short] = result
        return result

    def klass(self, ctx: str, schema: dict[str, Any], named: bool = False) -> Native:
        signature = json.dumps(schema, sort_keys=True)
        name = "Hydra" + ctx
        if not named:
            base, count = name, 1
            while name in self.reserved or (name in self.natives and self.signatures[name] != signature):
                count += 1
                name = f"{base}{count}"
        if name in self.natives:
            return self.natives[name]
        helper = self.map_fn
        native = Native(name, lambda e, d: f"{name}.fromJson({helper}({e}))", lambda e, d: f"{e}.toJson()", call=".toJson()")
        self.natives[name] = native
        self.signatures[name] = signature
        required = set(schema.get("required") or [])
        taken: set[str] = set(KOTLIN_MEMBERS if self.kotlin else DART_MEMBERS)
        fields: list[dict[str, Any]] = []
        for prop, sub in (schema.get("properties") or {}).items():
            sub = sub if isinstance(sub, dict) else {}
            kind = self.native(sub, ctx + camel(prop))
            needed = prop in required
            fields.append({"wire": prop, "name": identifier(prop, self.flavor, taken), "native": kind if needed else self.nullable(kind),
                           "required": needed, "note": one_line(sub.get("description", ""))})
        extra = schema.get("additionalProperties")
        open_part = None
        if extra is True or isinstance(extra, dict):
            item = self.native(extra, ctx + "Extra") if isinstance(extra, dict) and extra else self.anything()
            open_part = {"name": identifier("additional properties", self.flavor, taken), "native": self.keyed(item)}
        self.defs[name] = {"schema": schema, "fields": fields, "open": open_part, "note": one_line(schema.get("description", ""))}
        return native


def kotlin_class(name: str, definition: dict[str, Any]) -> list[str]:
    fields, open_part = definition["fields"], definition["open"]
    note = definition["note"] or "An object of the server contract."
    lines = [f"/** {note} */", f"data class {name}("]
    for field in fields:
        if field["note"]:
            lines.append(f"    /** {field['note']} */")
        default = "" if field["required"] else " = null"
        lines.append(f"    val {field['name']}: {field['native'].type}{default},")
    if open_part:
        lines.append("    /** The keys the contract does not list, kept as they came. */")
        lines.append(f"    val {open_part['name']}: {open_part['native'].type} = emptyMap(),")
    lines += [") {", "    fun toJson(): Map<String, Any?> {", "        val jsonOut = LinkedHashMap<String, Any?>()"]
    if open_part:
        lines.append(f"        jsonOut.putAll({open_part['native'].encode(open_part['name'], 0)})")
    for field in fields:
        wire, ident, kind = kt_string(field["wire"]), field["name"], field["native"]
        if field["required"]:
            lines.append(f"        jsonOut[{wire}] = {kind.encode(ident, 0)}")
        else:
            lines.append(f"        if ({ident} != null) jsonOut[{wire}] = {(kind.inner or kind).encode(ident, 0)}")
    lines += ["        return jsonOut", "    }", "", "    companion object {"]
    if open_part:
        keys = ", ".join(kt_string(f["wire"]) for f in fields)
        lines.append(f"        private val knownKeys: Set<String> = setOf({keys})")
        lines.append("")
    lines += [f"        fun fromJson(json: Map<String, Any?>): {name} = {name}("]
    for field in fields:
        lines.append(f"            {field['name']} = {field['native'].decode('json[' + kt_string(field['wire']) + ']', 0)},")
    if open_part:
        lines.append(f"            {open_part['name']} = {open_part['native'].decode('json.filterKeys { it !in knownKeys }', 0)},")
    lines += ["        )", "    }", "}", ""]
    return lines


def dart_class(name: str, definition: dict[str, Any]) -> list[str]:
    fields, open_part = definition["fields"], definition["open"]
    note = definition["note"] or "An object of the server contract."
    lines = [f"/// {note}", f"class {name} {{", f"  const {name}({{"]
    for field in fields:
        lines.append(f"    {'required ' if field['required'] else ''}this.{field['name']},")
    if open_part:
        lines.append(f"    this.{open_part['name']} = const {open_part['native'].type[3:]}{{}},")
    lines += ["  });", "", f"  factory {name}.fromJson(Map<String, dynamic> json) => {name}("]
    for field in fields:
        lines.append(f"        {field['name']}: {field['native'].decode('json[' + dart_string(field['wire']) + ']', 0)},")
    if open_part:
        keys = ", ".join(dart_string(f["wire"]) for f in fields)
        listing = "{" + f"{keys}" + "}"
        entries = ("<String, dynamic>{for (final entry in json.entries) if (!_knownKeys.contains(entry.key)) entry.key: entry.value}")
        lines.append(f"        {open_part['name']}: {open_part['native'].decode(entries, 0)},")
        lines += ["      );", "", f"  static const Set<String> _knownKeys = <String>{listing};"]
    else:
        lines.append("      );")
    lines.append("")
    for field in fields:
        if field["note"]:
            lines.append(f"  /// {field['note']}")
        lines.append(f"  final {field['native'].type} {field['name']};")
    if open_part:
        lines += ["  /// The keys the contract does not list, kept as they came.", f"  final {open_part['native'].type} {open_part['name']};"]
    lines += ["", "  Map<String, dynamic> toJson() {"]
    if open_part:
        lines.append(f"    final hydraOut = <String, dynamic>{{...{open_part['native'].encode(open_part['name'], 0)}}};")
    else:
        lines.append("    final hydraOut = <String, dynamic>{};")
    for index, field in enumerate(fields):
        wire, ident, kind = dart_string(field["wire"]), field["name"], field["native"]
        if field["required"]:
            lines.append(f"    hydraOut[{wire}] = {kind.encode(ident, 0)};")
        else:
            local = f"hydraField{index}"
            lines += [f"    final {local} = {ident};", f"    if ({local} != null) hydraOut[{wire}] = {(kind.inner or kind).encode(local, 0)};"]
    lines += ["    return hydraOut;", "  }", "}", ""]
    return lines


Param = tuple[str, str, str, str, bool, Native]


def native_arguments(op: dict[str, Any], builder: Builder) -> tuple[list[Param], Native | None]:
    """The parameters of a method as (identifier, type, where, wire name, required, model), and the model of its result."""
    flavor = builder.flavor
    taken: set[str] = {"transport", "raw", "reply"}
    found: list[Param] = []
    default = {"type": "string"}
    context = camel(op["name"])
    for p in op["path_parameters"]:
        kind = builder.native(p.get("schema", default), context + camel(p["name"]))
        found.append((identifier(p["name"], flavor, taken), kind.type, "path", p["name"], True, kind))
    for p in op["query"]:
        kind = builder.native(p.get("schema", default), context + camel(p["name"]))
        found.append((identifier(p["name"], flavor, taken), kind.type, "query", p["name"], bool(p.get("required")), kind))
    for p in op["headers"]:
        kind = builder.native(p.get("schema", default), context + camel(p["name"]))
        found.append((identifier("header " + p["name"], flavor, taken), kind.type, "header", p["name"], bool(p.get("required")), kind))
    if op["body"] is not None:
        kind = builder.native(op["body_schema"], context + "Body")
        needed = op["body_required"]
        kind = kind if needed else builder.nullable(kind)
        found.append((identifier("body", flavor, taken), kind.type, "body", "body", needed, kind))
    found.sort(key=lambda item: not item[4])
    if op["result_schema"] is None:
        return found, None
    return found, builder.native(op["result_schema"], context + "Result")


def doc_note(op: dict[str, Any]) -> str:
    note = op["summary"] or f"{op['method']} {op['path']}"
    return f"{note.replace('*/', '* /')} (access: {op['access']})"


def dart_string(text: str) -> str:
    return "'" + text.replace("\\", "\\\\").replace("'", "\\'").replace("$", "\\$") + "'"


def type_section(document: dict[str, Any], builder: Builder) -> list[str]:
    """The aliases of the named schemas that are not classes, then every class, in name order."""
    lines: list[str] = []
    for name in sorted(builder.schemas):
        if not is_class(builder.schemas[name]):
            target = builder.named[name].type
            lines.append(f"typealias Hydra{name} = {target}" if builder.kotlin else f"typedef Hydra{name} = {target};")
            lines.append("")
    for name in sorted(builder.defs):
        lines += kotlin_class(name, builder.defs[name]) if builder.kotlin else dart_class(name, builder.defs[name])
    return lines


def as_kotlin(document: dict[str, Any], package: str = KOTLIN_PACKAGE) -> str:
    flavor = Flavor("kotlin")
    ops = operations(document)
    builder = Builder(document, flavor, package)
    for name in sorted(builder.schemas):
        builder.reference(name)
    methods: list[str] = []
    for op in ops:
        params, result = native_arguments(op, builder)
        text = "Unit" if result is None else result.type
        signature = ", ".join(f"{n}: {t}" if req else f"{n}: {flavor.optional(t)} = null" for n, t, _, _, req, _ in params)
        path_values = ", ".join(f"{quote(w)} to {n}" for n, _, where, w, _, _ in params if where == "path")
        query_values = ", ".join(f"{quote(w)} to {n}" for n, _, where, w, _, _ in params if where == "query")
        header_values = ", ".join(f"{quote(w)} to {n}" for n, _, where, w, _, _ in params if where == "header")
        body = next((p for p in params if p[2] == "body"), None)
        body_expr = body[5].encode(body[0], 0) if body else "null"
        path_expr = f"fillPath({quote(op['path'])}, mapOf({path_values}))" if path_values else quote(op["path"])
        query_expr = f"queryOf(mapOf({query_values}))" if query_values else "emptyMap()"
        head = f"transport.send(HydraRequest({quote(op['method'])}, {path_expr}, {query_expr}, {body_expr}, {quote(op['access'])}{', headers = queryOf(mapOf(' + header_values + '))' if header_values else ''}"
        call = head + extras_text(op, False, " = ", quote, kt_list) + "))"
        methods += [f"    /** {doc_note(op)} */", f"    suspend fun {op['name']}({signature}): {text} {{"]
        if result is None:
            methods += [f"        {call}", "        return Unit"]
        else:
            methods += [f"        val raw = {call}", f"        return {result.decode('raw', 0)}"]
        methods += ["    }", ""]
        if op["reply_headers"]:
            wrapped = head + extras_text(op, True, " = ", quote, kt_list) + "))"
            decoded = "Unit" if result is None else result.decode("reply.body", 0)
            methods += [f"    /** {doc_note(op)}; the reply also holds the response headers {', '.join(op['reply_headers'])}. */",
                        f"    suspend fun {op['name']}WithHeaders({signature}): HydraReply<{text}> {{",
                        f"        val reply = {wrapped} as HydraReply<Any?>",
                        f"        return HydraReply<{text}>({decoded}, reply.headers)",
                        "    }", ""]
    lines = [f"// {HEADER}", "", '@file:Suppress("UNCHECKED_CAST", "unused")', "", f"package {package}", "",
             "// The transport hands back the decoded JSON model: Map, List, String, Long, Double, Boolean or null. Every object of the",
             "// contract is a data class with fromJson (reads that model) and toJson (writes it again); no JSON library is needed.", ""]
    lines += type_section(document, builder)
    lines += [
        "private fun hydraMap(value: Any?): Map<String, Any?> =",
        "    (value as Map<*, *>).entries.associate { (key, item) -> (key as String) to item }",
        "",
        "private fun hydraList(value: Any?): List<Any?> = value as List<*>",
        "",
        "/** contentType is the media type of a body that is not JSON; responseType is text or binary when the answer is not JSON; replyHeaders names the response headers to hand back in a HydraReply. */",
        "class HydraRequest(val method: String, val path: String, val query: Map<String, String>, val body: Any?, val access: String, val headers: Map<String, String> = emptyMap(),",
        "                   val contentType: String? = null, val responseType: String? = null, val replyHeaders: List<String> = emptyList())",
        "",
        "/** The answer of a route that declares response headers: the decoded body and the headers under their declared names (ETag, X-Next-Cursor). */",
        "class HydraReply<T>(val body: T, val headers: Map<String, String>)",
        "",
        "/** Carries one request to the server and returns the decoded answer (null when there is none); a request with replyHeaders gets a HydraReply. */",
        "fun interface HydraTransport {",
        "    suspend fun send(request: HydraRequest): Any?",
        "}",
        "",
        "fun fillPath(template: String, values: Map<String, Any>): String =",
        '    Regex("\\\\{([^}]+)\\\\}").replace(template) { match ->',
        "        val value = values[match.groupValues[1]]?.toString()",
        '        require(!value.isNullOrEmpty()) { "missing path parameter ${match.groupValues[1]}" }',
        '        java.net.URLEncoder.encode(value, "UTF-8").replace("+", "%20")',
        "    }",
        "",
        "fun queryOf(values: Map<String, Any?>): Map<String, String> =",
        "    values.filterValues { it != null }.mapValues { it.value.toString() }",
        "",
        "class HydraServerClient(private val transport: HydraTransport) {",
    ]
    lines += methods
    lines += ["}", "", "val HYDRA_CLIENT_OPERATIONS: List<String> = listOf("]
    lines += [f"    {quote(op['name'])}," for op in ops]
    lines += [")", ""]
    return "\n".join(lines)


def as_dart(document: dict[str, Any]) -> str:
    flavor = Flavor("dart")
    ops = operations(document)
    builder = Builder(document, flavor)
    for name in sorted(builder.schemas):
        builder.reference(name)
    methods: list[str] = []
    for op in ops:
        params, result = native_arguments(op, builder)
        text = "void" if result is None else result.type
        required = [p for p in params if p[4]]
        optional = [p for p in params if not p[4]]
        pieces = [f"required {t} {n}" for n, t, _, _, _, _ in required] + [f"{flavor.optional(t)} {n}" for n, t, _, _, _, _ in optional]
        signature = "{" + ", ".join(pieces) + "}" if pieces else ""
        path_values = ", ".join(f"{dart_string(w)}: {n}" for n, _, where, w, _, _ in params if where == "path")
        query_values = ", ".join(f"{dart_string(w)}: {n}" for n, _, where, w, _, _ in params if where == "query")
        header_values = ", ".join(f"{dart_string(w)}: {n}" for n, _, where, w, _, _ in params if where == "header")
        body = next((p for p in params if p[2] == "body"), None)
        body_expr = body[5].encode(body[0], 0) if body else "null"
        path_expr = f"fillPath({dart_string(op['path'])}, {{{path_values}}})" if path_values else dart_string(op["path"])
        query_expr = f"queryOf({{{query_values}}})" if query_values else "const <String, String>{}"
        head = f"_transport(HydraRequest({dart_string(op['method'])}, {path_expr}, {query_expr}, {body_expr}, {dart_string(op['access'])}{', headers: queryOf({' + header_values + '})' if header_values else ''}"
        call = head + extras_text(op, False, ": ", dart_string, dart_list) + "))"
        methods += [f"  /// {doc_note(op)}", f"  Future<{text}> {op['name']}({signature}) async {{"]
        if result is None:
            methods.append(f"    await {call};")
        else:
            methods += [f"    final raw = await {call};", f"    return {result.decode('raw', 0)};"]
        methods += ["  }", ""]
        if op["reply_headers"]:
            wrapped = head + extras_text(op, True, ": ", dart_string, dart_list) + "))"
            decoded = "null" if result is None else result.decode("reply.body", 0)
            methods += [f"  /// {doc_note(op)}; the reply also holds the response headers {', '.join(op['reply_headers'])}.",
                        f"  Future<HydraReply<{text}>> {op['name']}WithHeaders({signature}) async {{",
                        f"    final reply = (await {wrapped}) as HydraReply<dynamic>;",
                        f"    return HydraReply<{text}>({decoded}, reply.headers);",
                        "  }", ""]
    lines = [f"// {HEADER}", "// ignore_for_file: unused_element", "",
             "// The transport hands back the decoded JSON model: Map, List, String, int, double, bool or null. Every object of the",
             "// contract is a class with fromJson (reads that model) and toJson (writes it again); no JSON library is needed.", ""]
    lines += type_section(document, builder)
    lines += [
        "Map<String, dynamic> _hydraMap(Object? value) => Map<String, dynamic>.from(value as Map);",
        "",
        "R? _hydraNullable<S, R>(S? value, R Function(S) encode) => value == null ? null : encode(value);",
        "",
        "class HydraRequest {",
        "  const HydraRequest(this.method, this.path, this.query, this.body, this.access, {this.headers = const <String, String>{}, this.contentType, this.responseType, this.replyHeaders = const <String>[]});",
        "  final String method;",
        "  final String path;",
        "  final Map<String, String> query;",
        "  final Object? body;",
        "  final String access;",
        "  final Map<String, String> headers;",
        "  /// The media type of a body that is not JSON.",
        "  final String? contentType;",
        "  /// 'text' or 'binary' when the answer is not JSON.",
        "  final String? responseType;",
        "  /// The response headers to hand back in a HydraReply (set for the WithHeaders methods).",
        "  final List<String> replyHeaders;",
        "}",
        "",
        "/// The answer of a route that declares response headers: the decoded body and the headers under their declared names (ETag, X-Next-Cursor).",
        "class HydraReply<T> {",
        "  const HydraReply(this.body, this.headers);",
        "  final T body;",
        "  final Map<String, String> headers;",
        "}",
        "",
        "/// Carries one request to the server and returns the decoded answer (null when there is none); a request with replyHeaders gets a HydraReply.",
        "typedef HydraTransport = Future<dynamic> Function(HydraRequest request);",
        "",
        "String fillPath(String template, Map<String, Object> values) {",
        "  return template.replaceAllMapped(RegExp(r'\\{([^}]+)\\}'), (match) {",
        "    final value = values[match.group(1)]?.toString();",
        "    if (value == null || value.isEmpty) {",
        "      throw ArgumentError('missing path parameter ${match.group(1)}');",
        "    }",
        "    return Uri.encodeComponent(value);",
        "  });",
        "}",
        "",
        "Map<String, String> queryOf(Map<String, Object?> values) {",
        "  return {",
        "    for (final entry in values.entries)",
        "      if (entry.value != null) entry.key: entry.value.toString(),",
        "  };",
        "}",
        "",
        "class HydraServerClient {",
        "  HydraServerClient(this._transport);",
        "",
        "  final HydraTransport _transport;",
        "",
    ]
    lines += methods
    lines += ["}", "", "const List<String> hydraClientOperations = ["]
    lines += [f"  {dart_string(op['name'])}," for op in ops]
    lines += ["];", ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------------------------------------------------
# The round trip files: for every class of a named schema, an example built from the schema (all fields, then only the
# required ones) is read with fromJson and written with toJson, and the result must equal the example.
# --------------------------------------------------------------------------------------------------------------------

def example_of(schema: dict[str, Any] | None, schemas: dict[str, Any], full: bool, stack: tuple[str, ...] = ()) -> Any:
    """A JSON value that fits the schema; None only when it would need an object that is already being built."""
    if not schema:
        return "sample"
    if "$ref" in schema:
        name = schema["$ref"].rsplit("/", 1)[-1]
        if name in stack or name not in schemas:
            return None
        return example_of(schemas[name], schemas, full, stack + (name,))
    for word in ("anyOf", "oneOf"):
        if word in schema:
            members = [m for m in schema[word] if m != {"type": "null"}]
            return example_of(members[0], schemas, full, stack) if len(members) == 1 else "sample"
    if "allOf" in schema and len(schema["allOf"]) == 1:
        return example_of(schema["allOf"][0], schemas, full, stack)
    kind, _ = kind_of(schema)
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        values = [v for v in schema["enum"] if v is not None]
        value = values[0] if values else None
        return float(value) if kind == "number" and isinstance(value, int) and not isinstance(value, bool) else value
    if kind == "string":
        return "text"
    if kind == "integer":
        return 7
    if kind == "number":
        return 1.5
    if kind == "boolean":
        return True
    if kind == "array":
        item = example_of(schema.get("items"), schemas, full, stack)
        return [] if item is None else [item]
    if kind == "object" or "properties" in schema or "additionalProperties" in schema:
        required = set(schema.get("required") or [])
        found: dict[str, Any] = {}
        for prop, sub in (schema.get("properties") or {}).items():
            if not full and prop not in required:
                continue
            value = example_of(sub if isinstance(sub, dict) else {}, schemas, full, stack)
            if value is not None or prop in required:
                found[prop] = value
        extra = schema.get("additionalProperties")
        if full and (extra is True or isinstance(extra, dict)):
            found["extraKey"] = example_of(extra, schemas, full, stack) if isinstance(extra, dict) and extra else "extra"
        elif not schema.get("properties") and not extra:
            found["key"] = "value"
        return found
    return "sample"


def kt_literal(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return f"{value}L"
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        return kt_string(value)
    if isinstance(value, list):
        return "listOf<Any?>(" + ", ".join(kt_literal(v) for v in value) + ")"
    if isinstance(value, dict):
        return "mapOf<String, Any?>(" + ", ".join(f"{kt_string(k)} to {kt_literal(v)}" for k, v in value.items()) + ")"
    return "null"


def dart_literal(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return dart_string(value)
    if isinstance(value, list):
        return "<dynamic>[" + ", ".join(dart_literal(v) for v in value) + "]"
    if isinstance(value, dict):
        return "<String, dynamic>{" + ", ".join(f"{dart_string(k)}: {dart_literal(v)}" for k, v in value.items()) + "}"
    return "null"


def round_trip_cases(document: dict[str, Any]) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    schemas = document.get("components", {}).get("schemas", {})
    cases = []
    for name in sorted(schemas):
        if is_class(schemas[name]):
            cases.append((name, example_of(schemas[name], schemas, True, (name,)), example_of(schemas[name], schemas, False, (name,))))
    return cases


def round_trip_kotlin(document: dict[str, Any], package: str = KOTLIN_PACKAGE) -> str:
    lines = [f"// {HEADER}", "", f"package {package}", "",
             "// Reads an example of every class with fromJson and writes it with toJson: the result must equal the example.",
             "private val failures = mutableListOf<String>()", "",
             "private fun <T> roundTrip(label: String, example: Map<String, Any?>, read: (Map<String, Any?>) -> T, write: (T) -> Map<String, Any?>) {",
             "    val again = try { write(read(example)) } catch (error: Exception) { failures.add(\"$label threw $error\"); return }",
             "    if (again != example) failures.add(\"$label changed: $again instead of $example\")",
             "}", ""]
    cases = round_trip_cases(document)
    for name, full, minimal in cases:
        lines += [f"private fun roundTripHydra{name}() {{",
                  f"    roundTrip(\"Hydra{name} full\", {kt_literal(full)}, {{ Hydra{name}.fromJson(it) }}, {{ it.toJson() }})",
                  f"    roundTrip(\"Hydra{name} required only\", {kt_literal(minimal)}, {{ Hydra{name}.fromJson(it) }}, {{ it.toJson() }})",
                  "}", ""]
    lines += ["/** Runs every round trip and returns the failures (empty when all pass). */", "fun roundTripAll(): List<String> {", "    failures.clear()"]
    lines += [f"    roundTripHydra{name}()" for name, _, _ in cases]
    lines += ["    return failures.toList()", "}", f"const val ROUND_TRIP_CLASSES: Int = {len(cases)}", ""]
    return "\n".join(lines)


def round_trip_dart(document: dict[str, Any]) -> str:
    lines = [f"// {HEADER}", "", "import 'hydra_server_client.dart';", "",
             "// Reads an example of every class with fromJson and writes it with toJson: the result must equal the example.",
             "bool _same(Object? a, Object? b) {",
             "  if (a is Map && b is Map) {",
             "    return a.length == b.length && a.keys.every((key) => b.containsKey(key) && _same(a[key], b[key]));",
             "  }",
             "  if (a is List && b is List) {",
             "    return a.length == b.length && List<bool>.generate(a.length, (i) => _same(a[i], b[i])).every((same) => same);",
             "  }",
             "  return a == b;",
             "}", "",
             "void _roundTrip<T>(List<String> failures, String label, Map<String, dynamic> example, T Function(Map<String, dynamic>) read, Map<String, dynamic> Function(T) write) {",
             "  try {",
             "    final again = write(read(example));",
             "    if (!_same(again, example)) failures.add('$label changed: $again instead of $example');",
             "  } catch (error) {",
             "    failures.add('$label threw $error');",
             "  }",
             "}", ""]
    cases = round_trip_cases(document)
    lines += [f"const int roundTripClasses = {len(cases)};", "", "/// Runs every round trip and returns the failures (empty when all pass).", "List<String> roundTripAll() {", "  final failures = <String>[];"]
    for name, full, minimal in cases:
        lines += [f"  _roundTrip<Hydra{name}>(failures, 'Hydra{name} full', {dart_literal(full)}, Hydra{name}.fromJson, (value) => value.toJson());",
                  f"  _roundTrip<Hydra{name}>(failures, 'Hydra{name} required only', {dart_literal(minimal)}, Hydra{name}.fromJson, (value) => value.toJson());"]
    lines += ["  return failures;", "}", ""]
    return "\n".join(lines)


KT_ROUND_TRIP_NAME = "HydraServerClientRoundTrip.kt"
DART_ROUND_TRIP_NAME = "hydra_server_client_round_trip.dart"


def outputs(document: dict[str, Any] | None = None, package: str = KOTLIN_PACKAGE) -> dict[str, str]:
    """The three clients and the two round trip files, by file name."""
    document = document if document is not None else json.loads(FULL.read_text(encoding="utf-8"))
    return {TS_NAME: as_typescript(document), KT_NAME: as_kotlin(document, package), DART_NAME: as_dart(document),
            KT_ROUND_TRIP_NAME: round_trip_kotlin(document, package), DART_ROUND_TRIP_NAME: round_trip_dart(document)}


# The round trip files of the contract sit next to the hand-written smoke programs; the three clients sit in generated/.
CONFORMANCE = ROOT / "conformance" / "generated-clients"
ROUND_TRIP_NAMES = (KT_ROUND_TRIP_NAME, DART_ROUND_TRIP_NAME)


def target(name: str) -> Path:
    return (CONFORMANCE if name in ROUND_TRIP_NAMES else OUT) / name


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail when a generated file is out of date")
    parser.add_argument("--spec", type=Path, help="generate from this OpenAPI document into --out instead of the server contract")
    parser.add_argument("--out", type=Path, help="the folder for --spec (all five files are written there)")
    parser.add_argument("--kotlin-package", default=KOTLIN_PACKAGE, help="the Kotlin package of the files made from --spec")
    args = parser.parse_args(argv)
    if args.spec:
        if args.check or not args.out:
            raise SystemExit("GENERATED_CLIENTS=FAIL --spec needs --out and cannot be combined with --check")
        args.out.mkdir(parents=True, exist_ok=True)
        produced = outputs(json.loads(args.spec.read_text(encoding="utf-8")), args.kotlin_package)
        for name, text in produced.items():
            (args.out / name).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {len(produced)} files to {args.out}")
        return 0
    produced = outputs()
    if args.check:
        stale = [name for name, text in produced.items()
                 if not target(name).is_file() or target(name).read_bytes().replace(b"\r\n", b"\n") != text.encode("utf-8")]
        if stale:
            print("GENERATED_CLIENTS=FAIL out of date: " + ", ".join(stale) + " (run python tools/generate_clients.py)", file=sys.stderr)
            return 1
        print(f"GENERATED_CLIENTS=PASS {len(produced)} files match the contract")
        return 0
    OUT.mkdir(exist_ok=True)
    CONFORMANCE.mkdir(parents=True, exist_ok=True)
    for name, text in produced.items():
        target(name).write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(produced)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
