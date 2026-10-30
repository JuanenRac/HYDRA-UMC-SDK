# =============================================================================
# HYDRA-UMC-SDK - Routes of the mock server derived from an OpenAPI document
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

"""Turns an OpenAPI 3.x document of the server into the routes of the mock
server, so a client can be exercised against the real paths, methods and
status codes of the published contract before any real server exists.

Every answer is built from the document itself: the first 2xx response of the
operation, with a body synthesised from its schema (the `example`, `default`
or first `enum` value where the schema gives one, a minimal value of the
declared type otherwise). An operation that needs a bearer token answers 401
without an `Authorization` header, exactly as the contract declares. Nothing
is stored: a write is answered with the static example and changes nothing.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

HTTP_METHODS = ("get", "put", "post", "delete", "patch", "head", "options")
_MAX_DEPTH = 8


def _resolve(ref: str, doc: dict[str, Any]) -> dict[str, Any]:
    node: Any = doc
    for part in ref.lstrip("#/").split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def synthesize(schema: Any, doc: dict[str, Any], depth: int = 0) -> Any:
    """A small value that satisfies `schema` (None when the schema is empty)."""
    if not isinstance(schema, dict) or depth > _MAX_DEPTH:
        return None
    if "$ref" in schema:
        return synthesize(_resolve(schema["$ref"], doc), doc, depth + 1)
    for key in ("example", "default", "const"):
        if key in schema:
            return schema[key]
    if schema.get("enum"):
        return schema["enum"][0]
    if schema.get("allOf"):
        merged: dict[str, Any] = {}
        for part in schema["allOf"]:
            value = synthesize(part, doc, depth + 1)
            if isinstance(value, dict):
                merged.update(value)
        return merged
    for key in ("oneOf", "anyOf"):
        if schema.get(key):
            return synthesize(schema[key][0], doc, depth + 1)
    kind = schema.get("type")
    if isinstance(kind, list):
        kind = next((k for k in kind if k != "null"), "null")
    if kind == "object" or (kind is None and "properties" in schema):
        out: dict[str, Any] = {}
        properties = schema.get("properties", {})
        for name in schema.get("required", []):
            out[name] = synthesize(properties.get(name, {}), doc, depth + 1)
        return out
    if kind == "array":
        item = synthesize(schema.get("items", {}), doc, depth + 1)
        count = max(int(schema.get("minItems", 0)), 0)
        return [item for _ in range(count)]
    if kind == "string":
        fmt = schema.get("format")
        text = {"date-time": "2026-01-01T00:00:00Z", "date": "2026-01-01", "uri": "http://localhost/",
                "uuid": "00000000-0000-4000-8000-000000000000"}.get(fmt, "mock")
        return text[: schema["maxLength"]] if "maxLength" in schema else text
    if kind == "integer":
        return int(schema.get("minimum", 0))
    if kind == "number":
        return float(schema.get("minimum", 0))
    if kind == "boolean":
        return False
    return None


def conforms(value: Any, schema: Any, doc: dict[str, Any], depth: int = 0) -> str | None:
    """None when `value` satisfies the part of `schema` this module checks
    (type, required, enum, array items, nested properties); otherwise the
    reason. Deliberately small: it proves the mock does not drift from the
    document, it is not a full JSON Schema validator."""
    if not isinstance(schema, dict) or depth > _MAX_DEPTH:
        return None
    if "$ref" in schema:
        return conforms(value, _resolve(schema["$ref"], doc), doc, depth + 1)
    if schema.get("allOf"):
        for part in schema["allOf"]:
            reason = conforms(value, part, doc, depth + 1)
            if reason:
                return reason
        return None
    for key in ("oneOf", "anyOf"):
        if schema.get(key):
            reasons = [conforms(value, part, doc, depth + 1) for part in schema[key]]
            return None if any(r is None for r in reasons) else reasons[0]
    if schema.get("enum") and value not in schema["enum"]:
        return f"{value!r} is not in the enum"
    kind = schema.get("type")
    kinds = kind if isinstance(kind, list) else [kind] if kind else []
    if value is None:
        return None if (not kinds or "null" in kinds or schema.get("nullable")) else "null where a value is required"
    checks = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
    }
    if kinds and not any(k == "null" or checks[k](value) for k in kinds):
        return f"{type(value).__name__} where {kinds} is declared"
    if isinstance(value, dict):
        for name in schema.get("required", []):
            if name not in value:
                return f"missing required property {name!r}"
        for name, sub in schema.get("properties", {}).items():
            if name in value:
                reason = conforms(value[name], sub, doc, depth + 1)
                if reason:
                    return f"{name}: {reason}"
    if isinstance(value, list) and "items" in schema:
        for item in value:
            reason = conforms(item, schema["items"], doc, depth + 1)
            if reason:
                return reason
    return None


class OpenApiRouter:
    """Matches a method and a path against the operations of the document."""

    def __init__(self, doc: dict[str, Any]) -> None:
        self.doc = doc
        self._routes: list[tuple[re.Pattern[str], str, dict[str, dict[str, Any]]]] = []
        for template, item in doc.get("paths", {}).items():
            pattern = "^" + re.sub(r"\\\{[^}]+\\\}", "([^/]+)", re.escape(template)) + "/?$"
            operations = {m: item[m] for m in HTTP_METHODS if isinstance(item.get(m), dict)}
            self._routes.append((re.compile(pattern), template, operations))

    @classmethod
    def from_file(cls, path: str | Path) -> OpenApiRouter:
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def operations(self) -> list[tuple[str, str, dict[str, Any]]]:
        return [(m.upper(), t, op) for _, t, ops in self._routes for m, op in ops.items()]

    def match(self, method: str, path: str) -> tuple[str, dict[str, Any] | None, list[str]]:
        """(template, operation or None, allowed methods). An empty template
        means no path of the document matches."""
        route = path.split("?", 1)[0]
        for pattern, template, operations in self._routes:
            if pattern.match(route):
                return template, operations.get(method.lower()), sorted(m.upper() for m in operations)
        return "", None, []

    def answer(self, operation: dict[str, Any], authorization: str | None) -> tuple[int, dict[str, str], Any]:
        """(status, extra headers, body) for one operation."""
        responses = operation.get("responses", {})
        needs_token = bool(operation.get("security", self.doc.get("security")))
        if needs_token and not (authorization or "").lower().startswith("bearer ") and "401" in responses:
            return 401, {}, self._body(responses["401"])
        status = next((s for s in sorted(responses) if s.startswith("2")), None)
        if status is None:
            return 200, {}, {}
        headers = {}
        for name in responses[status].get("headers", {}):
            if name.lower() == "etag":
                headers["ETag"] = '"1"'
        return int(status), headers, self._body(responses[status])

    def _body(self, response: dict[str, Any]) -> Any:
        content = response.get("content", {}).get("application/json")
        return synthesize(content.get("schema", {}), self.doc) if content else None
