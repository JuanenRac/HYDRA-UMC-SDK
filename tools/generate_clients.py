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
`suspend` function interface in Kotlin and a `Future` function in Dart, and the named schemas are aliases of the plain
JSON model (maps, lists and scalars) so any JSON library can feed them.

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


def request_extras(op: dict[str, Any], with_headers: bool) -> list[tuple[str, str]]:
    """The request fields that are not the default (a JSON body, a JSON or empty answer, no reply headers) as (field, value)."""
    extras: list[tuple[str, str]] = []
    if op["body"] is not None and op["body_media"] != "application/json":
        extras.append(("contentType", op["body_media"]))
    if op["answer"] in ("text", "binary"):
        extras.append(("responseType", op["answer"]))
    if with_headers:
        extras.append(("withHeaders", "true"))
    return extras


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
        "  /** True for the WithHeaders methods: the transport answers with a HydraReply that holds the response headers the contract declares. */",
        "  readonly withHeaders?: boolean;",
        "}",
        "",
        "/** The answer of a route that declares response headers: the decoded body and the headers under their declared names (ETag, X-Next-Cursor). */",
        "export interface HydraReply<T> {",
        "  readonly body: T;",
        "  readonly headers: Readonly<Record<string, string>>;",
        "}",
        "",
        "/** Carries one request to the server and returns the decoded answer (undefined when there is none); a request with withHeaders gets a HydraReply. */",
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
        plain = "".join(f", {f}: {quote(v)}" for f, v in request_extras(op, False))
        lines += [
            f"  /** {note.replace('*/', '* /')} (access: {op['access']}) */",
            f"  {op['name']}({signature}): Promise<{op['result']}> {{",
            f"    return {send}{plain} }}) as Promise<{op['result']}>;",
            "  }",
            "",
        ]
        if op["reply_headers"]:
            extras = "".join(f", {f}: {v if f == 'withHeaders' else quote(v)}" for f, v in request_extras(op, True))
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


Param = tuple[str, str, str, str, bool]


def native_arguments(op: dict[str, Any], flavor: Flavor, cyclic: frozenset[str]) -> tuple[list[Param], str]:
    """The parameters of a method as (identifier, type, where, wire name, required), and the type of its result."""
    taken: set[str] = {"transport"}
    found: list[Param] = []
    default = {"type": "string"}
    for p in op["path_parameters"]:
        found.append((identifier(p["name"], flavor, taken), native_type(p.get("schema", default), flavor, cyclic), "path", p["name"], True))
    for p in op["query"]:
        found.append((identifier(p["name"], flavor, taken), native_type(p.get("schema", default), flavor, cyclic), "query", p["name"], bool(p.get("required"))))
    for p in op["headers"]:
        found.append((identifier("header " + p["name"], flavor, taken), native_type(p.get("schema", default), flavor, cyclic), "header", p["name"], bool(p.get("required"))))
    if op["body"] is not None:
        found.append((identifier("body", flavor, taken), native_type(op["body_schema"], flavor, cyclic), "body", "body", op["body_required"]))
    found.sort(key=lambda item: not item[4])
    if op["result_schema"] is None:
        return found, "Unit" if flavor.kotlin else "void"
    return found, native_type(op["result_schema"], flavor, cyclic)


def doc_note(op: dict[str, Any]) -> str:
    note = op["summary"] or f"{op['method']} {op['path']}"
    return f"{note.replace('*/', '* /')} (access: {op['access']})"


def schema_aliases(document: dict[str, Any], flavor: Flavor) -> list[str]:
    schemas = document.get("components", {}).get("schemas", {})
    cyclic = cyclic_schemas(schemas)
    lines: list[str] = []
    for name in sorted(schemas):
        schema = schemas[name]
        target = native_type({k: v for k, v in schema.items() if k != "description"}, flavor, cyclic)
        required = schema.get("required") or []
        fields = ", ".join(f"{p}{'' if p in required else '?'}" for p in (schema.get("properties") or {}))
        if fields:
            lines.append(f"/** Fields: {fields.replace('*/', '* /')} */" if flavor.kotlin else f"/// Fields: {fields}")
        lines.append(f"typealias Hydra{name} = {target}" if flavor.kotlin else f"typedef Hydra{name} = {target};")
        lines.append("")
    return lines


def dart_string(text: str) -> str:
    return "'" + text.replace("\\", "\\\\").replace("'", "\\'").replace("$", "\\$") + "'"


def as_kotlin(document: dict[str, Any]) -> str:
    flavor = Flavor("kotlin")
    ops = operations(document)
    cyclic = cyclic_schemas(document.get("components", {}).get("schemas", {}))
    lines = [f"// {HEADER}", "", '@file:Suppress("UNCHECKED_CAST", "unused")', "", f"package {KOTLIN_PACKAGE}", "",
             "// The transport hands back the decoded JSON model: Map, List, String, Long, Double, Boolean or null.", ""]
    lines += schema_aliases(document, flavor)
    lines += [
        "/** contentType is the media type of a body that is not JSON; responseType is text or binary when the answer is not JSON; withHeaders asks for a HydraReply. */",
        "class HydraRequest(val method: String, val path: String, val query: Map<String, String>, val body: Any?, val access: String, val headers: Map<String, String> = emptyMap(),",
        "                   val contentType: String? = null, val responseType: String? = null, val withHeaders: Boolean = false)",
        "",
        "/** The answer of a route that declares response headers: the decoded body and the headers under their declared names (ETag, X-Next-Cursor). */",
        "class HydraReply<T>(val body: T, val headers: Map<String, String>)",
        "",
        "/** Carries one request to the server and returns the decoded answer (null when there is none); a request with withHeaders gets a HydraReply. */",
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
    for op in ops:
        params, result = native_arguments(op, flavor, cyclic)
        signature = ", ".join(f"{n}: {t}" if req else f"{n}: {flavor.optional(t)} = null" for n, t, _, _, req in params)
        path_values = ", ".join(f"{quote(w)} to {n}" for n, _, where, w, _ in params if where == "path")
        query_values = ", ".join(f"{quote(w)} to {n}" for n, _, where, w, _ in params if where == "query")
        header_values = ", ".join(f"{quote(w)} to {n}" for n, _, where, w, _ in params if where == "header")
        body_name = next((n for n, _, where, _, _ in params if where == "body"), "null")
        path_expr = f"fillPath({quote(op['path'])}, mapOf({path_values}))" if path_values else quote(op["path"])
        query_expr = f"queryOf(mapOf({query_values}))" if query_values else "emptyMap()"
        head = f"transport.send(HydraRequest({quote(op['method'])}, {path_expr}, {query_expr}, {body_name}, {quote(op['access'])}{', headers = queryOf(mapOf(' + header_values + '))' if header_values else ''}"
        call = head + "".join(f", {f} = {quote(v)}" for f, v in request_extras(op, False)) + "))"
        lines += [f"    /** {doc_note(op)} */", f"    suspend fun {op['name']}({signature}): {result} {{"]
        if result == "Unit":
            lines += [f"        {call}", "        return Unit"]
        else:
            lines.append(f"        return {call} as {result}")
        lines += ["    }", ""]
        if op["reply_headers"]:
            wrapped = head + "".join(f", {f} = {v if f == 'withHeaders' else quote(v)}" for f, v in request_extras(op, True)) + "))"
            lines += [f"    /** {doc_note(op)}; the reply also holds the response headers {', '.join(op['reply_headers'])}. */",
                      f"    suspend fun {op['name']}WithHeaders({signature}): HydraReply<{result}> {{",
                      f"        val reply = {wrapped} as HydraReply<Any?>",
                      f"        return HydraReply(reply.body as {result}, reply.headers)",
                      "    }", ""]
    lines += ["}", "", "val HYDRA_CLIENT_OPERATIONS: List<String> = listOf("]
    lines += [f"    {quote(op['name'])}," for op in ops]
    lines += [")", ""]
    return "\n".join(lines)


def as_dart(document: dict[str, Any]) -> str:
    flavor = Flavor("dart")
    ops = operations(document)
    cyclic = cyclic_schemas(document.get("components", {}).get("schemas", {}))
    lines = [f"// {HEADER}", "// ignore_for_file: unused_element", "",
             "// The transport hands back the decoded JSON model: Map, List, String, int, double, bool or null.", ""]
    lines += schema_aliases(document, flavor)
    lines += [
        "class HydraRequest {",
        "  const HydraRequest(this.method, this.path, this.query, this.body, this.access, {this.headers = const <String, String>{}, this.contentType, this.responseType, this.withHeaders = false});",
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
        "  /// True for the WithHeaders methods: the transport answers with a HydraReply.",
        "  final bool withHeaders;",
        "}",
        "",
        "/// The answer of a route that declares response headers: the decoded body and the headers under their declared names (ETag, X-Next-Cursor).",
        "class HydraReply<T> {",
        "  const HydraReply(this.body, this.headers);",
        "  final T body;",
        "  final Map<String, String> headers;",
        "}",
        "",
        "/// Carries one request to the server and returns the decoded answer (null when there is none); a request with withHeaders gets a HydraReply.",
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
    for op in ops:
        params, result = native_arguments(op, flavor, cyclic)
        required = [p for p in params if p[4]]
        optional = [p for p in params if not p[4]]
        pieces = [f"required {t} {n}" for n, t, _, _, _ in required] + [f"{flavor.optional(t)} {n}" for n, t, _, _, _ in optional]
        signature = "{" + ", ".join(pieces) + "}" if pieces else ""
        path_values = ", ".join(f"{dart_string(w)}: {n}" for n, _, where, w, _ in params if where == "path")
        query_values = ", ".join(f"{dart_string(w)}: {n}" for n, _, where, w, _ in params if where == "query")
        header_values = ", ".join(f"{dart_string(w)}: {n}" for n, _, where, w, _ in params if where == "header")
        body_name = next((n for n, _, where, _, _ in params if where == "body"), "null")
        path_expr = f"fillPath({dart_string(op['path'])}, {{{path_values}}})" if path_values else dart_string(op["path"])
        query_expr = f"queryOf({{{query_values}}})" if query_values else "const <String, String>{}"
        head = f"_transport(HydraRequest({dart_string(op['method'])}, {path_expr}, {query_expr}, {body_name}, {dart_string(op['access'])}{', headers: queryOf({' + header_values + '})' if header_values else ''}"
        call = head + "".join(f", {f}: {dart_string(v)}" for f, v in request_extras(op, False)) + "))"
        lines += [f"  /// {doc_note(op)}", f"  Future<{result}> {op['name']}({signature}) async {{"]
        if result == "void":
            lines.append(f"    await {call};")
        else:
            lines.append(f"    return (await {call}) as {result};")
        lines += ["  }", ""]
        if op["reply_headers"]:
            wrapped = head + "".join(f", {f}: {v if f == 'withHeaders' else dart_string(v)}" for f, v in request_extras(op, True)) + "))"
            lines += [f"  /// {doc_note(op)}; the reply also holds the response headers {', '.join(op['reply_headers'])}.",
                      f"  Future<HydraReply<{result}>> {op['name']}WithHeaders({signature}) async {{",
                      f"    final reply = (await {wrapped}) as HydraReply<dynamic>;",
                      f"    return HydraReply<{result}>(reply.body as {result}, reply.headers);",
                      "  }", ""]
    lines += ["}", "", "const List<String> hydraClientOperations = ["]
    lines += [f"  {dart_string(op['name'])}," for op in ops]
    lines += ["];", ""]
    return "\n".join(lines)


def outputs() -> dict[str, str]:
    document = json.loads(FULL.read_text(encoding="utf-8"))
    return {TS_NAME: as_typescript(document), KT_NAME: as_kotlin(document), DART_NAME: as_dart(document)}


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
