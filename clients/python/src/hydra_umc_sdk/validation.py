# =============================================================================
# HYDRA-UMC-SDK - Initial contract validation reference client
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

"""Small dependency-free validation for the initial HYDRA-UMC SDK contracts.

The JSON Schema files are normative. This module gives early adopters a
portable validation path before generated clients are introduced.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import re
import sys
from typing import Any
from urllib.parse import urlparse


class ContractValidationError(ValueError):
    """Raised when a payload violates a required initial contract invariant."""


REQUIRED: dict[str, tuple[str, ...]] = {
    "DeviceDescriptor": ("schema_version", "node_id", "profile", "hostname", "machine", "operating_system", "kernel", "interfaces"),
    "HealthReport": ("schema_version", "state", "timestamp_utc", "checks"),
    "SafetyState": ("schema_version", "state", "source", "timestamp_utc"),
    "UpdateManifest": ("schema_version", "project", "version", "artifact_url", "sha256"),
    "EventEnvelope": ("schema_version", "event_id", "type", "source", "timestamp_utc", "sequence"),
    "ScenarioOutcome": ("schema_version", "scenario_id", "run_id", "base_fingerprint", "phase", "repro_case", "observed", "timestamp_utc"),
    "Operation": ("schema_version", "operation_id", "correlation_id", "kind", "target", "status", "requested_at_utc", "updated_at_utc", "params"),
    "Capability": ("schema_version", "target", "kind", "declared"),
    "ServerDiscovery": ("schema_version", "product", "remoteApiVersion", "appVersion", "hostname", "controllerCount", "robotCount", "uptimeSeconds"),
    "ProjectManifest": (
        "schema_version", "ecosystem", "name", "version", "role", "stack", "technologies",
        "deployment_target", "maturity", "family", "parent", "native_version", "build", "notes",
    ),
}
ENUMS = {
    "HealthReport": {"READY", "DEGRADED", "INHIBITED", "FAULT", "SAFE_STOP"},
    "SafetyState": {"READY", "INHIBITED", "FAULT", "SAFE_STOP"},
}
PROJECT_MANIFEST_ENUMS = {
    "role": {"api", "ui", "cli", "firmware", "library", "service", "tool"},
    # "dev-server" added for HYDRA-UMC-DEV-SERVER - a Raspberry Pi 5/CM5
    # host dedicated to development and task execution, distinct from
    # "cm5" (the operational node that talks to real machines/robots).
    # A compatible manifest extension: no existing value changed meaning,
    # no consumer needs to change.
    "deployment_target": {"cm5", "user-pc", "mobile", "wearable", "dev-server"},
    "maturity": {"scaffolding", "functional", "established", "production"},
}
PROJECT_NAME_PATTERN = re.compile(r"^(HYDRA-UMC|URTC)(-[A-Z0-9-]+)?$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:\.\d+)?$")
# RFC 3339 allows a lowercase "t" and "z"; the schema validators of the other
# clients accept them, so this one does too.
RFC3339_DATE_TIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$"
)
PROJECT_MANIFEST_KEYS = frozenset({
    "schema_version", "ecosystem", "name", "version", "role", "stack", "technologies", "deployment_target",
    "deployment_target_note", "maturity", "family", "parent", "native_version", "build", "notes", "service",
})
PROJECT_MANIFEST_SERVICE_KEYS = frozenset({"port", "health_path", "systemd_unit"})


def _is_one_of(value: Any, allowed: Any) -> bool:
    """Enum membership that refuses (rather than crashes on) a value that is not
    a string: a list or an object in a set lookup raises TypeError (unhashable),
    which a caller catching ContractValidationError would never see."""
    return isinstance(value, str) and value in allowed


def _require_string(payload: dict[str, Any], name: str) -> None:
    if not isinstance(payload.get(name), str) or not payload[name]:
        raise ContractValidationError(f"{name} must be a non-empty string")


def _require_date_time(payload: dict[str, Any], name: str) -> None:
    """Require the RFC 3339 date-time form used by JSON Schema v1."""
    _require_string(payload, name)
    value = payload[name]
    if not RFC3339_DATE_TIME.fullmatch(value):
        raise ContractValidationError(f"{name} must be an RFC 3339 date-time")
    try:
        datetime.fromisoformat(value.upper().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractValidationError(f"{name} must be a valid RFC 3339 date-time") from exc


def _require_integer(payload: dict[str, Any], name: str, minimum: int) -> None:
    """Require a JSON integer, deliberately excluding Python booleans."""
    value = payload[name]
    if type(value) is not int or value < minimum:
        raise ContractValidationError(f"{name} must be an integer >= {minimum}")


def _validate_project_manifest(payload: dict[str, Any]) -> None:
    """Real v1 ProjectManifest checks - the `hydra-umc.project.json`
    contract every one of this ecosystem's real repositories publishes.
    Mirrors project-manifest.schema.json's own real constraints rather
    than re-deriving them independently, so the two can't silently drift
    without a conformance fixture (see tools/verify_contract_matrix.py)
    catching it."""
    # The schema does not allow other top-level fields (its optional `service`
    # block has its own fixed set), so neither does this check.
    unknown = sorted(set(payload) - PROJECT_MANIFEST_KEYS)
    if unknown:
        raise ContractValidationError(f"unsupported manifest field(s): {', '.join(unknown)}")
    if not _is_one_of(payload.get("ecosystem"), {"HYDRA-UMC", "URTC"}):
        raise ContractValidationError("ecosystem must be 'HYDRA-UMC' or 'URTC'")
    if "deployment_target_note" in payload and not isinstance(payload["deployment_target_note"], str):
        raise ContractValidationError("deployment_target_note must be a string")
    if "service" in payload:
        service = payload["service"]
        if not isinstance(service, dict) or set(service) - PROJECT_MANIFEST_SERVICE_KEYS:
            raise ContractValidationError("service must be an object with only port, health_path and systemd_unit")
        if "port" in service and (type(service["port"]) is not int or not 1 <= service["port"] <= 65535):
            raise ContractValidationError("service.port must be an integer from 1 to 65535")
        for key in ("health_path", "systemd_unit"):
            if key in service and (not isinstance(service[key], str) or not service[key]):
                raise ContractValidationError(f"service.{key} must be a non-empty string")
    if not PROJECT_NAME_PATTERN.fullmatch(payload.get("name", "")):
        raise ContractValidationError("name must match ^(HYDRA-UMC|URTC)(-[A-Z0-9-]+)?$")
    if not SEMVER_PATTERN.fullmatch(payload.get("version", "")):
        raise ContractValidationError("version must be MAJOR.MINOR.PATCH")
    if not _is_one_of(payload.get("role"), PROJECT_MANIFEST_ENUMS["role"]):
        raise ContractValidationError(f"unsupported role: {payload.get('role')!r}")
    if not _is_one_of(payload.get("deployment_target"), PROJECT_MANIFEST_ENUMS["deployment_target"]):
        raise ContractValidationError(f"unsupported deployment_target: {payload.get('deployment_target')!r}")
    if not _is_one_of(payload.get("maturity"), PROJECT_MANIFEST_ENUMS["maturity"]):
        raise ContractValidationError(f"unsupported maturity: {payload.get('maturity')!r}")

    technologies = payload.get("technologies")
    if (
        not isinstance(technologies, list)
        or not technologies
        or any(not isinstance(item, str) or not item for item in technologies)
        or len(set(technologies)) != len(technologies)
    ):
        raise ContractValidationError("technologies must be a non-empty array of unique non-empty strings")

    parent = payload.get("parent")
    if parent is not None and (not isinstance(parent, str) or not parent):
        raise ContractValidationError("parent must be a non-empty string or null")

    for field in ("build", "notes"):
        if not isinstance(payload.get(field), str):
            raise ContractValidationError(f"{field} must be a string")

    native_version = payload.get("native_version")
    if not isinstance(native_version, dict) or set(native_version) != {"file", "pattern"}:
        raise ContractValidationError("native_version must contain exactly file and pattern")
    if not isinstance(native_version.get("file"), str) or not native_version["file"]:
        raise ContractValidationError("native_version.file must be a non-empty string")
    pattern = native_version.get("pattern")
    if isinstance(pattern, str):
        if not pattern:
            raise ContractValidationError("native_version.pattern must not be empty")
    elif isinstance(pattern, dict):
        if not {"major", "minor", "patch"} <= set(pattern) <= {"major", "minor", "patch", "build"} or any(
            not isinstance(value, str) or not value for value in pattern.values()
        ):
            raise ContractValidationError("native_version.pattern mapping must contain non-empty major, minor and patch")
    else:
        raise ContractValidationError("native_version.pattern must be a string or a component mapping")


def validate(contract: str, payload: dict[str, Any]) -> None:
    """Validate the required v1 subset; unknown additive fields are allowed."""
    if contract not in REQUIRED:
        raise ContractValidationError(f"unknown contract: {contract}")
    if not isinstance(payload, dict):
        raise ContractValidationError("payload must be an object")
    for field in REQUIRED[contract]:
        if field not in payload:
            raise ContractValidationError(f"missing required field: {field}")
    if payload.get("schema_version") != "1.0":
        raise ContractValidationError("schema_version must be '1.0'")
    for field in REQUIRED[contract]:
        if field not in {
            "interfaces", "checks", "sequence", "remoteApiVersion", "controllerCount", "robotCount", "uptimeSeconds",
            "technologies", "native_version", "parent", "build", "notes", "observed", "target", "params", "declared",
        }:
            _require_string(payload, field)
    if contract in {"HealthReport", "SafetyState", "EventEnvelope", "ScenarioOutcome"}:
        _require_date_time(payload, "timestamp_utc")
    if contract == "Operation":
        _require_date_time(payload, "requested_at_utc")
        _require_date_time(payload, "updated_at_utc")
        if not _is_one_of(payload["status"], {"received", "authorized", "queued", "sent", "confirmed", "terminated", "rejected"}):
            # P03's own core point: "no presentar todos como ejecutado" -
            # this contract has no "executed" status at all, on purpose.
            raise ContractValidationError("status must be one of: received, authorized, queued, sent, confirmed, terminated, rejected")
        target = payload["target"]
        if not isinstance(target, dict) or not isinstance(target.get("kind"), str) or not target.get("kind") \
                or not isinstance(target.get("id"), str) or not target.get("id"):
            raise ContractValidationError("target must be an object with non-empty kind and id")
        if not isinstance(payload["params"], dict):
            raise ContractValidationError("params must be an object")
        if "status_reason" in payload and not isinstance(payload["status_reason"], str):
            raise ContractValidationError("status_reason must be a string")
        if "error" in payload:
            error = payload["error"]
            if not isinstance(error, dict) or not isinstance(error.get("code"), str) or not error.get("code") \
                    or not isinstance(error.get("message"), str) or not error.get("message"):
                raise ContractValidationError("error, when present, must be an object with non-empty code and message")
        if "result" in payload:
            # an optional, real result distinct from the Operation's
            # own status transitions - see operation.py's concludes_success()
            # for why observers_enabled/run_id/outcome exist at all.
            result = payload["result"]
            if not isinstance(result, dict):
                raise ContractValidationError("result must be an object")
            for field in ("run_id", "origin"):
                if not isinstance(result.get(field), str) or not result[field]:
                    raise ContractValidationError(f"result.{field} must be a non-empty string")
            if not _is_one_of(result["origin"], {"real", "simulated"}):
                raise ContractValidationError("result.origin must be 'real' or 'simulated'")
            if not isinstance(result.get("observers_enabled"), bool):
                raise ContractValidationError("result.observers_enabled must be a boolean")
            if not _is_one_of(result.get("outcome"), {"success", "failure", "unknown"}):
                raise ContractValidationError("result.outcome must be 'success', 'failure' or 'unknown'")
            if "outcome_reason" in result and not isinstance(result["outcome_reason"], str):
                raise ContractValidationError("result.outcome_reason must be a string")
            if "revision" in result and not isinstance(result["revision"], str):
                raise ContractValidationError("result.revision must be a string")
            if result["outcome"] != "success" and not result.get("outcome_reason"):
                raise ContractValidationError("result.outcome_reason is required when outcome is not 'success'")
            for ts_field in ("accepted_at_utc", "executed_at_utc", "observed_at_utc"):
                if ts_field in result:
                    _require_date_time(result, ts_field)
    if contract == "ScenarioOutcome":
        if not _is_one_of(payload["phase"], {"before", "after"}):
            raise ContractValidationError("phase must be 'before' or 'after'")
        observed = payload["observed"]
        if not isinstance(observed, dict):
            raise ContractValidationError("observed must be an object")
        if not _is_one_of(observed.get("outcome"), {"reproduced", "not-reproduced", "error"}):
            raise ContractValidationError("observed.outcome must be 'reproduced', 'not-reproduced' or 'error'")
        if "exit_code" in observed and type(observed["exit_code"]) is not int:
            raise ContractValidationError("observed.exit_code must be an integer")
        if "evidence" in observed and not isinstance(observed["evidence"], str):
            raise ContractValidationError("observed.evidence must be a string")
    if contract == "DeviceDescriptor" and not isinstance(payload["interfaces"], list):
        raise ContractValidationError("interfaces must be an array")
    if contract == "DeviceDescriptor" and not all(isinstance(item, str) and item for item in payload["interfaces"]):
        raise ContractValidationError("interfaces must contain non-empty strings")
    if contract == "HealthReport" and not isinstance(payload["checks"], dict):
        raise ContractValidationError("checks must be an object")
    if contract in ENUMS and not _is_one_of(payload["state"], ENUMS[contract]):
        raise ContractValidationError(f"unsupported {contract} state: {payload['state']}")
    if contract == "UpdateManifest":
        if not SEMVER_PATTERN.fullmatch(payload["version"]):
            raise ContractValidationError("version must be MAJOR.MINOR.PATCH")
        if len(payload["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in payload["sha256"].lower()):
            raise ContractValidationError("sha256 must be a 64-character hexadecimal digest")
        parsed_artifact_url = urlparse(payload["artifact_url"])
        if parsed_artifact_url.scheme != "https" or not parsed_artifact_url.hostname:
            raise ContractValidationError("artifact_url must be an https URL with a hostname")
    if contract == "EventEnvelope":
        _require_integer(payload, "sequence", 0)
        if "correlation_id" in payload and not isinstance(payload["correlation_id"], str):
            raise ContractValidationError("correlation_id must be a string")
    if contract == "ProjectManifest":
        _validate_project_manifest(payload)
    if contract == "ServerDiscovery":
        for field in ("remoteApiVersion", "controllerCount", "robotCount", "uptimeSeconds"):
            minimum = 1 if field == "remoteApiVersion" else 0
            _require_integer(payload, field, minimum)
    if contract == "Capability":
        target = payload["target"]
        if not isinstance(target, dict) or not isinstance(target.get("kind"), str) or not target.get("kind") \
                or not isinstance(target.get("id"), str) or not target.get("id"):
            raise ContractValidationError("target must be an object with non-empty kind and id")
        if not isinstance(payload["declared"], bool):
            raise ContractValidationError("declared must be a boolean")
        if "last_checked_at_utc" in payload:
            _require_date_time(payload, "last_checked_at_utc")
        if "checked_configuration" in payload and not isinstance(payload["checked_configuration"], str):
            raise ContractValidationError("checked_configuration must be a string")
        if "max_age_seconds" in payload:
            value = payload["max_age_seconds"]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
                raise ContractValidationError("max_age_seconds must be a positive number")
        if "last_check_outcome" in payload and not _is_one_of(payload["last_check_outcome"], {"verified", "failed", "unknown"}):
            raise ContractValidationError("last_check_outcome must be 'verified', 'failed' or 'unknown'")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a HYDRA-UMC SDK v1 JSON payload.")
    parser.add_argument("contract", choices=sorted(REQUIRED))
    parser.add_argument("payload", help="JSON file to validate")
    args = parser.parse_args(argv)
    try:
        with open(args.payload, encoding="utf-8") as source:
            validate(args.contract, json.load(source))
    except (ContractValidationError, OSError, json.JSONDecodeError) as exc:
        print(f"hydra-umc-contract-validate: {exc}", file=sys.stderr)
        return 2
    print(f"valid {args.contract} v1 payload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
