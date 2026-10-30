# =============================================================================
# HYDRA-UMC-SDK - The history of the clients that connect to a server
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `ConnectionEvent` and `ConnectionClient` contracts.

A server keeps a history of the applications that talk to it (Studio, Suite, the phone and watch apps, the voice service) and a list of the clients it has seen.
Both say what happened and who, never how: neither carries a password, a token, a cookie or a code, and the schemas are closed so a field like that cannot slip in.
The address (`ip`) and the user agent (`agent`) are for administrators only; the server removes them from the answer to anybody else.
"""

from __future__ import annotations

import re
from typing import Any

from .validation import ContractValidationError, _require_date_time

CLIENT_KINDS = ("studio", "suite", "android", "ios", "dsi", "watch", "voice", "other")
ACTIONS = ("first_seen", "login", "login_failed", "second_factor_failed", "logout", "session_ended", "session_expired")
ORIGINS = ("local", "remote")
CLIENT_ID = re.compile(r"^[0-9a-f]{16}$")
APP_VERSION = re.compile(r"^[0-9A-Za-z._-]{1,24}$")

_EVENT_KEYS = frozenset({"schema_version", "id", "at_utc", "action", "client_kind", "client_id", "user", "origin", "two_factor", "app_version", "ip", "agent"})
_CLIENT_KEYS = frozenset({
    "schema_version", "id", "kind", "user", "app_version", "origin", "two_factor", "first_seen_utc", "last_seen_utc", "last_failure_utc",
    "active_sessions", "logins_ok", "logins_failed", "ip", "agent",
})


def _integer(payload: dict[str, Any], name: str, minimum: int) -> None:
    value = payload[name]
    if type(value) is not int or value < minimum:
        raise ContractValidationError(f"{name} must be an integer >= {minimum}")


def _text(payload: dict[str, Any], name: str, maximum: int) -> None:
    if name in payload and (not isinstance(payload[name], str) or not 1 <= len(payload[name]) <= maximum):
        raise ContractValidationError(f"{name} must be a text of 1 to {maximum} characters")


def _shared(payload: dict[str, Any], keys: frozenset[str], required: tuple[str, ...]) -> None:
    if not isinstance(payload, dict):
        raise ContractValidationError("payload must be an object")
    for field in required:
        if field not in payload:
            raise ContractValidationError(f"missing required field: {field}")
    unknown = sorted(set(payload) - keys)
    if unknown:
        raise ContractValidationError(f"unsupported field(s): {', '.join(unknown)}")
    if payload["schema_version"] != "1.0":
        raise ContractValidationError("schema_version must be '1.0'")
    _text(payload, "user", 60)
    _text(payload, "ip", 64)
    _text(payload, "agent", 120)
    if "origin" in payload and payload["origin"] not in ORIGINS:
        raise ContractValidationError(f"origin must be one of {', '.join(ORIGINS)}")
    if "two_factor" in payload and type(payload["two_factor"]) is not bool:
        raise ContractValidationError("two_factor must be true or false")
    if "app_version" in payload and not (isinstance(payload["app_version"], str) and APP_VERSION.fullmatch(payload["app_version"])):
        raise ContractValidationError("app_version must be 1 to 24 letters, digits, dots, dashes or underscores")


def validate_connection_event(payload: dict[str, Any]) -> None:
    """The checks of the ConnectionEvent contract."""
    _shared(payload, _EVENT_KEYS, ("schema_version", "id", "at_utc", "action", "client_kind", "client_id"))
    _integer(payload, "id", 1)
    _require_date_time(payload, "at_utc")
    if payload["action"] not in ACTIONS:
        raise ContractValidationError(f"action must be one of {', '.join(ACTIONS)}")
    if payload["client_kind"] not in CLIENT_KINDS:
        raise ContractValidationError(f"client_kind must be one of {', '.join(CLIENT_KINDS)}")
    if not (isinstance(payload["client_id"], str) and CLIENT_ID.fullmatch(payload["client_id"])):
        raise ContractValidationError("client_id must be 16 lowercase hexadecimal digits")


def validate_connection_client(payload: dict[str, Any]) -> None:
    """The checks of the ConnectionClient contract."""
    _shared(payload, _CLIENT_KEYS, ("schema_version", "id", "kind", "first_seen_utc", "last_seen_utc", "active_sessions", "logins_ok", "logins_failed"))
    if not (isinstance(payload["id"], str) and CLIENT_ID.fullmatch(payload["id"])):
        raise ContractValidationError("id must be 16 lowercase hexadecimal digits")
    if payload["kind"] not in CLIENT_KINDS:
        raise ContractValidationError(f"kind must be one of {', '.join(CLIENT_KINDS)}")
    for name in ("first_seen_utc", "last_seen_utc"):
        _require_date_time(payload, name)
    if "last_failure_utc" in payload:
        _require_date_time(payload, "last_failure_utc")
    for name in ("active_sessions", "logins_ok", "logins_failed"):
        _integer(payload, name, 0)
