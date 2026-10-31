# =============================================================================
# HYDRA-UMC-SDK - The health of the ecosystem and the signal of life of the robots
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `EcosystemHealth` and `RobotLiveness` contracts.

`EcosystemHealth` is what a server answers at `GET /api/ecosystem/health`: for each service that declares a port or a unit, whether it answers and
which version it reports against the one its manifest expects, plus the state of the TLS certificate of the server itself. The port, the health
path, the unit and the active state of a service are for administrators only.

`RobotLiveness` is what a server answers at `GET /api/robots/liveness`: for each robot of the roster, whether the server had news of it recently.
It is news the server received, not a measurement of the hardware. Both contracts are closed, so nothing else can slip in.
"""

from __future__ import annotations

import re
from typing import Any

from .validation import ContractValidationError, _require_date_time

SERVICE_STATES = ("ok", "degraded", "down", "unknown")
SERVICE_REASONS = (
    "health_ok", "health_degraded", "health_failed", "http_error", "unreachable", "unreachable_unit_active",
    "reachable_unit_not_active", "unit_active", "unit_starting", "unit_failed", "unit_inactive", "no_signal", "probe_error",
)
CERTIFICATE_STATES = ("ok", "expiring", "expired", "unreadable")
WARNING_CODES = ("certificate_expiring", "certificate_expired", "certificate_unreadable", "version_drift", "service_down", "service_degraded")
LIVENESS_STATES = ("live", "stale", "unknown")
LIVENESS_SOURCES = ("state", "heartbeat")
VERSION = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._+-]{0,23}$")

_SUMMARY_KEYS = ("total", "ok", "degraded", "down", "unknown", "drift")
_SERVICE_REQUIRED = ("name", "family", "role", "state", "reason", "version_expected", "version_reported", "drift", "last_seen_utc", "latency_ms")
_SERVICE_OPTIONAL = ("port", "health_path", "systemd_unit", "active_state")
_CERTIFICATE_KEYS = ("state", "not_after_utc", "days_left", "warn_days")


def _object(value: Any, what: str, required: tuple[str, ...], optional: tuple[str, ...] = ()) -> None:
    if not isinstance(value, dict):
        raise ContractValidationError(f"{what} must be an object")
    for field in required:
        if field not in value:
            raise ContractValidationError(f"{what} is missing required field: {field}")
    unknown = sorted(set(value) - set(required) - set(optional))
    if unknown:
        raise ContractValidationError(f"{what} has unsupported field(s): {', '.join(unknown)}")


def _integer(value: Any, what: str, minimum: int, maximum: int | None = None, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if type(value) is not int or value < minimum or (maximum is not None and value > maximum):
        bound = f" from {minimum} to {maximum}" if maximum is not None else f" >= {minimum}"
        raise ContractValidationError(f"{what} must be an integer{bound}{' or null' if nullable else ''}")


def _text(value: Any, what: str, *, maximum: int | None = None, minimum: int = 0, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or len(value) < minimum or (maximum is not None and len(value) > maximum):
        raise ContractValidationError(f"{what} must be a text{' or null' if nullable else ''}")


def _one_of(value: Any, what: str, allowed: tuple[str, ...]) -> None:
    if not isinstance(value, str) or value not in allowed:
        raise ContractValidationError(f"{what} must be one of {', '.join(allowed)}")


def _date_time_or_null(payload: dict[str, Any], name: str) -> None:
    if payload[name] is not None:
        _require_date_time(payload, name)


def _version(value: Any, what: str) -> None:
    if value is not None and not (isinstance(value, str) and VERSION.fullmatch(value)):
        raise ContractValidationError(f"{what} must be a plain version of 1 to 24 characters or null")


def validate_ecosystem_health(payload: dict[str, Any]) -> None:
    """The checks of the EcosystemHealth contract."""
    _object(payload, "payload", ("schema_version", "generated_at_utc", "available", "summary", "services", "certificate", "warnings"))
    if payload["schema_version"] != "1.0":
        raise ContractValidationError("schema_version must be '1.0'")
    _require_date_time(payload, "generated_at_utc")
    if type(payload["available"]) is not bool:
        raise ContractValidationError("available must be true or false")
    summary = payload["summary"]
    _object(summary, "summary", _SUMMARY_KEYS)
    for key in _SUMMARY_KEYS:
        _integer(summary[key], f"summary.{key}", 0)
    if not isinstance(payload["services"], list):
        raise ContractValidationError("services must be a list")
    for index, service in enumerate(payload["services"]):
        where = f"services[{index}]"
        _object(service, where, _SERVICE_REQUIRED, _SERVICE_OPTIONAL)
        _text(service["name"], f"{where}.name", minimum=1, maximum=100)
        _text(service["family"], f"{where}.family", nullable=True)
        _text(service["role"], f"{where}.role", nullable=True)
        _one_of(service["state"], f"{where}.state", SERVICE_STATES)
        _one_of(service["reason"], f"{where}.reason", SERVICE_REASONS)
        _version(service["version_expected"], f"{where}.version_expected")
        _version(service["version_reported"], f"{where}.version_reported")
        if type(service["drift"]) is not bool:
            raise ContractValidationError(f"{where}.drift must be true or false")
        _date_time_or_null(service, "last_seen_utc")
        _integer(service["latency_ms"], f"{where}.latency_ms", 0, nullable=True)
        if "port" in service:
            _integer(service["port"], f"{where}.port", 1, 65535, nullable=True)
        for name in ("health_path", "systemd_unit", "active_state"):
            if name in service:
                _text(service[name], f"{where}.{name}", nullable=True)
    certificate = payload["certificate"]
    if certificate is not None:
        _object(certificate, "certificate", _CERTIFICATE_KEYS)
        _one_of(certificate["state"], "certificate.state", CERTIFICATE_STATES)
        _date_time_or_null(certificate, "not_after_utc")
        if certificate["days_left"] is not None and type(certificate["days_left"]) is not int:
            raise ContractValidationError("certificate.days_left must be an integer or null")
        _integer(certificate["warn_days"], "certificate.warn_days", 1, 365)
    if not isinstance(payload["warnings"], list):
        raise ContractValidationError("warnings must be a list")
    for index, warning in enumerate(payload["warnings"]):
        _object(warning, f"warnings[{index}]", ("code",), ("service",))
        _one_of(warning["code"], f"warnings[{index}].code", WARNING_CODES)
        if "service" in warning:
            _text(warning["service"], f"warnings[{index}].service", minimum=1, maximum=100)


def validate_robot_liveness(payload: dict[str, Any]) -> None:
    """The checks of the RobotLiveness contract."""
    _object(payload, "payload", ("schema_version", "stale_after_s", "robots"))
    if payload["schema_version"] != "1.0":
        raise ContractValidationError("schema_version must be '1.0'")
    _integer(payload["stale_after_s"], "stale_after_s", 1, 3600)
    if not isinstance(payload["robots"], list):
        raise ContractValidationError("robots must be a list")
    for index, robot in enumerate(payload["robots"]):
        where = f"robots[{index}]"
        _object(robot, where, ("controller_id", "robot_id", "state"), ("last_update_utc", "age_s", "source"))
        _text(robot["controller_id"], f"{where}.controller_id", maximum=100)
        _integer(robot["robot_id"], f"{where}.robot_id", 0)
        _one_of(robot["state"], f"{where}.state", LIVENESS_STATES)
        if "last_update_utc" in robot:
            _require_date_time(robot, "last_update_utc")
        if "age_s" in robot:
            _integer(robot["age_s"], f"{where}.age_s", 0)
        if "source" in robot:
            _one_of(robot["source"], f"{where}.source", LIVENESS_SOURCES)
