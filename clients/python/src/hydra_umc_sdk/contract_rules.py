# =============================================================================
# HYDRA-UMC-SDK - Small checks shared by the closed contracts
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The few rules every closed contract repeats: no unknown field, a required field is there, an identifier, a bounded text, a finite number, a bounded integer.

Each helper raises `ContractValidationError` with the name of the field, and none of them converts a value: a boolean is never a number, a number is never a text.
"""

from __future__ import annotations

import math
import re
from typing import Any

from .validation import ContractValidationError

IDENTIFIER = re.compile(r"[A-Za-z0-9._:-]{1,64}")
SHA256_HEX = re.compile(r"[0-9a-f]{64}")


def require_object(payload: Any, label: str = "payload") -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ContractValidationError(f"{label} must be an object")
    return payload


def check_fields(payload: dict[str, Any], required: tuple[str, ...], optional: tuple[str, ...] = (), label: str = "payload") -> None:
    """Every required field is there, no field is outside the two lists, and `schema_version` (when listed) is '1.0'."""
    for name in required:
        if name not in payload:
            raise ContractValidationError(f"missing required field: {name}" if label == "payload" else f"{label}: missing required field: {name}")
    unknown = sorted(set(payload) - set(required) - set(optional))
    if unknown:
        raise ContractValidationError(f"unsupported field(s): {', '.join(unknown)}" if label == "payload" else f"{label}: unsupported field(s): {', '.join(unknown)}")
    if "schema_version" in payload and payload["schema_version"] != "1.0":
        raise ContractValidationError("schema_version must be '1.0'")


def identifier(payload: dict[str, Any], name: str) -> None:
    value = payload[name]
    if not (isinstance(value, str) and IDENTIFIER.fullmatch(value)):
        raise ContractValidationError(f"{name} must be 1 to 64 letters, digits, dots, colons, dashes or underscores")


def text(payload: dict[str, Any], name: str, maximum: int) -> None:
    value = payload[name]
    if not isinstance(value, str) or not 1 <= len(value) <= maximum:
        raise ContractValidationError(f"{name} must be a text of 1 to {maximum} characters")


def one_of(payload: dict[str, Any], name: str, allowed: tuple[str, ...]) -> None:
    value = payload[name]
    if not isinstance(value, str) or value not in allowed:
        raise ContractValidationError(f"{name} must be one of {', '.join(allowed)}")


def real(payload: dict[str, Any], name: str, minimum: float | None = None, maximum: float | None = None, *, exclusive_minimum: bool = False) -> None:
    """A finite number (never a boolean) within the bounds."""
    value = payload[name]
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ContractValidationError(f"{name} must be a finite number")
    if minimum is not None and (value <= minimum if exclusive_minimum else value < minimum):
        raise ContractValidationError(f"{name} must be {'greater than' if exclusive_minimum else 'at least'} {minimum}")
    if maximum is not None and value > maximum:
        raise ContractValidationError(f"{name} must be at most {maximum}")


def whole(payload: dict[str, Any], name: str, minimum: int, maximum: int | None = None) -> None:
    value = payload[name]
    if type(value) is not int or value < minimum or (maximum is not None and value > maximum):
        raise ContractValidationError(f"{name} must be an integer from {minimum}" + (f" to {maximum}" if maximum is not None else ""))
