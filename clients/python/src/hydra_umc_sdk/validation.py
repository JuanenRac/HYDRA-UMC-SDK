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
    "deployment_target": {"cm5", "user-pc", "mobile", "wearable"},
    "maturity": {"scaffolding", "functional", "established", "production"},
}
PROJECT_NAME_PATTERN = re.compile(r"^(HYDRA-UMC|URTC)(-[A-Z0-9-]+)?$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
RFC3339_DATE_TIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


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
        datetime.fromisoformat(value.replace("Z", "+00:00"))
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
    if payload.get("ecosystem") != "HYDRA-UMC":
        raise ContractValidationError("ecosystem must be 'HYDRA-UMC'")
    if not PROJECT_NAME_PATTERN.fullmatch(payload.get("name", "")):
        raise ContractValidationError("name must match ^(HYDRA-UMC|URTC)(-[A-Z0-9-]+)?$")
    if not SEMVER_PATTERN.fullmatch(payload.get("version", "")):
        raise ContractValidationError("version must be MAJOR.MINOR.PATCH")
    if payload.get("role") not in PROJECT_MANIFEST_ENUMS["role"]:
        raise ContractValidationError(f"unsupported role: {payload.get('role')!r}")
    if payload.get("deployment_target") not in PROJECT_MANIFEST_ENUMS["deployment_target"]:
        raise ContractValidationError(f"unsupported deployment_target: {payload.get('deployment_target')!r}")
    if payload.get("maturity") not in PROJECT_MANIFEST_ENUMS["maturity"]:
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
        if set(pattern) != {"major", "minor", "patch"} or any(
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
            "technologies", "native_version", "parent", "build", "notes",
        }:
            _require_string(payload, field)
    if contract in {"HealthReport", "SafetyState", "EventEnvelope"}:
        _require_date_time(payload, "timestamp_utc")
    if contract == "DeviceDescriptor" and not isinstance(payload["interfaces"], list):
        raise ContractValidationError("interfaces must be an array")
    if contract == "DeviceDescriptor" and not all(isinstance(item, str) and item for item in payload["interfaces"]):
        raise ContractValidationError("interfaces must contain non-empty strings")
    if contract == "HealthReport" and not isinstance(payload["checks"], dict):
        raise ContractValidationError("checks must be an object")
    if contract in ENUMS and payload["state"] not in ENUMS[contract]:
        raise ContractValidationError(f"unsupported {contract} state: {payload['state']}")
    if contract == "UpdateManifest" and (len(payload["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in payload["sha256"].lower())):
        raise ContractValidationError("sha256 must be a 64-character hexadecimal digest")
    if contract == "UpdateManifest":
        parsed_artifact_url = urlparse(payload["artifact_url"])
        if parsed_artifact_url.scheme != "https" or not parsed_artifact_url.hostname:
            raise ContractValidationError("artifact_url must be an https URL with a hostname")
    if contract == "EventEnvelope":
        _require_integer(payload, "sequence", 0)
    if contract == "ProjectManifest":
        _validate_project_manifest(payload)
    if contract == "ServerDiscovery":
        for field in ("remoteApiVersion", "controllerCount", "robotCount", "uptimeSeconds"):
            minimum = 1 if field == "remoteApiVersion" else 0
            _require_integer(payload, field, minimum)


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
