# =============================================================================
# HYDRA-UMC-SDK - Tool descriptor and tool state (URTC tool heads)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `ToolDescriptor` and `ToolState` contracts: what a URTC tool head is, and one reading of a connected head.

`ToolDescriptor` is a catalogue entry (the profile number, name, kind, the metric the tool is judged by, its limits, its watchdog and its features). It is static data
that comes from the tool table of URTC, not a reading. `ToolState` is the reading: which tool is active, the firmware of the head, the state of its CAN controller, its
temperatures and its faults, composed by an adapter from the frames of the head. `tool_id` of a state points to the descriptor with the same `tool_id`.

Both are closed. `validate()` applies exactly the rules of the JSON Schemas (the differential tests compare them); the rules that join fields, which a JSON Schema cannot
state, are the functions `descriptor_problems` and `state_problems`, which return the problems as texts instead of raising, so that a consumer can show them.
"""

from __future__ import annotations

import re
from typing import Any

from .contract_rules import IDENTIFIER, check_fields, one_of, real, require_object, whole
from .validation import ContractValidationError, _require_date_time

TOOL_KINDS: tuple[str, ...] = ("motion", "actuator", "telemetry", "external")
TOOL_STATES: tuple[str, ...] = ("active", "idle", "fault", "unknown")
CAN_STATES: tuple[str, ...] = ("ok", "error_passive", "bus_off", "unknown")
THERMAL_FAULTS: tuple[str, ...] = ("NONE", "MAXTEMP", "HEATING_NO_RISE", "DROPPED_AT_TARGET")

_NAME = re.compile(r"[A-Z][A-Z0-9_]{0,63}")
_VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?")

_DESCRIPTOR_REQUIRED = ("schema_version", "tool_id", "name", "title", "kind")
_DESCRIPTOR_OPTIONAL = ("category", "hero_metric", "limits", "watchdog_ms", "features", "expansion_board", "min_firmware_version")
_STATE_REQUIRED = ("schema_version", "tool_id", "state", "source", "timestamp_utc")
_STATE_OPTIONAL = ("firmware_version", "can", "temperature_c", "setpoint_c", "mcu_temp_c", "vdda_mv", "critical_error", "thermal_fault")


def _short_text(payload: dict[str, Any], name: str, maximum: int, *, minimum: int = 1) -> None:
    value = payload[name]
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise ContractValidationError(f"{name} must be a text of {minimum} to {maximum} characters")


def _version(payload: dict[str, Any], name: str) -> None:
    value = payload[name]
    if not (isinstance(value, str) and _VERSION.fullmatch(value)):
        raise ContractValidationError(f"{name} must be a version of three or four numbers separated by dots")


def validate_tool_descriptor(payload: dict[str, Any]) -> None:
    """The checks of the ToolDescriptor contract."""
    require_object(payload)
    check_fields(payload, _DESCRIPTOR_REQUIRED, _DESCRIPTOR_OPTIONAL)
    whole(payload, "tool_id", 0, 255)
    if not (isinstance(payload["name"], str) and _NAME.fullmatch(payload["name"])):
        raise ContractValidationError("name must be capitals, digits and underscores, starting with a capital (up to 64)")
    _short_text(payload, "title", 120)
    one_of(payload, "kind", TOOL_KINDS)
    if "category" in payload:
        _short_text(payload, "category", 80)
    if "hero_metric" in payload:
        metric = require_object(payload["hero_metric"], "hero_metric")
        check_fields(metric, ("label", "unit"), (), "hero_metric")
        _short_text(metric, "label", 40)
        _short_text(metric, "unit", 16, minimum=0)
    if "limits" in payload:
        limits = require_object(payload["limits"], "limits")
        check_fields(limits, ("default", "min", "max"), (), "limits")
        for name in ("default", "min", "max"):
            real(limits, name)
    if "watchdog_ms" in payload:
        whole(payload, "watchdog_ms", 1, 600000)
    if "features" in payload:
        features = payload["features"]
        if not isinstance(features, list) or len(features) > 32:
            raise ContractValidationError("features must be an array of at most 32 texts")
        for feature in features:
            if not isinstance(feature, str) or not 1 <= len(feature) <= 80:
                raise ContractValidationError("every feature must be a text of 1 to 80 characters")
    if "expansion_board" in payload:
        _short_text(payload, "expansion_board", 80)
    if "min_firmware_version" in payload:
        _version(payload, "min_firmware_version")


def validate_tool_state(payload: dict[str, Any]) -> None:
    """The checks of the ToolState contract."""
    require_object(payload)
    check_fields(payload, _STATE_REQUIRED, _STATE_OPTIONAL)
    whole(payload, "tool_id", 0, 255)
    one_of(payload, "state", TOOL_STATES)
    if not (isinstance(payload["source"], str) and IDENTIFIER.fullmatch(payload["source"])):
        raise ContractValidationError("source must be 1 to 64 letters, digits, dots, colons, dashes or underscores")
    _require_date_time(payload, "timestamp_utc")
    if "firmware_version" in payload:
        _version(payload, "firmware_version")
    if "can" in payload:
        can = require_object(payload["can"], "can")
        check_fields(can, ("state",), ("tec", "rec", "bus_off_count"), "can")
        one_of(can, "state", CAN_STATES)
        for name in ("tec", "rec", "bus_off_count"):
            if name in can:
                whole(can, name, 0, 255)
    if "temperature_c" in payload:
        real(payload, "temperature_c", -55, 1000)
    if "setpoint_c" in payload:
        real(payload, "setpoint_c", 0, 1000)
    if "mcu_temp_c" in payload:
        real(payload, "mcu_temp_c", -55, 150)
    if "vdda_mv" in payload:
        whole(payload, "vdda_mv", 0, 5000)
    if "critical_error" in payload and type(payload["critical_error"]) is not bool:
        raise ContractValidationError("critical_error must be true or false")
    if "thermal_fault" in payload:
        one_of(payload, "thermal_fault", THERMAL_FAULTS)


def descriptor_problems(payload: dict[str, Any]) -> list[str]:
    """The rules a JSON Schema cannot state, for a descriptor that is already valid: the limits are ordered (min <= default <= max)."""
    validate_tool_descriptor(payload)
    problems: list[str] = []
    limits = payload.get("limits")
    if limits is not None and not limits["min"] <= limits["default"] <= limits["max"]:
        problems.append("limits must satisfy min <= default <= max")
    return problems


def state_problems(payload: dict[str, Any], descriptor: dict[str, Any] | None = None) -> list[str]:
    """The rules that join the fields of a state that is already valid.

    * a thermal fault or a critical error means the state is `fault`, and a state `fault` has one of them or a bus-off controller;
    * a CAN controller in `bus_off` reports a transmit error counter of 255 when it reports one (a bus-off count above zero on an `ok` controller is history and is allowed);
    * given the descriptor of the tool: the ids match, the setpoint lies within its limits and the firmware is not older than the one the tool needs.
    """
    validate_tool_state(payload)
    problems: list[str] = []
    faulted = payload.get("critical_error") is True or payload.get("thermal_fault", "NONE") != "NONE"
    if faulted and payload["state"] != "fault":
        problems.append("a critical error or a thermal fault needs the state fault")
    if payload["state"] == "fault" and not (faulted or payload.get("can", {}).get("state") == "bus_off"):
        problems.append("the state fault needs a critical error, a thermal fault or a CAN controller in bus-off")
    can = payload.get("can")
    if can is not None and can["state"] == "bus_off" and can.get("tec", 255) != 255:
        problems.append("a CAN controller in bus-off reports a transmit error counter of 255")
    if descriptor is not None:
        validate_tool_descriptor(descriptor)
        if descriptor["tool_id"] != payload["tool_id"]:
            problems.append("the descriptor is the one of another tool")
        limits = descriptor.get("limits")
        if limits is not None and "setpoint_c" in payload and not limits["min"] <= payload["setpoint_c"] <= limits["max"]:
            problems.append("the setpoint is outside the limits of the tool")
        needed = descriptor.get("min_firmware_version")
        if needed is not None and "firmware_version" in payload and _version_key(payload["firmware_version"]) < _version_key(needed):
            problems.append("the firmware of the head is older than the tool needs")
    return problems


def _version_key(version: str) -> tuple[int, int, int, int]:
    parts = [int(part) for part in version.split(".")]
    if len(parts) == 3:
        parts.append(0)
    return (parts[0], parts[1], parts[2], parts[3])
