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
import json
import sys
from typing import Any


class ContractValidationError(ValueError):
    """Raised when a payload violates a required initial contract invariant."""


REQUIRED: dict[str, tuple[str, ...]] = {
    "DeviceDescriptor": ("schema_version", "node_id", "profile", "hostname", "machine", "operating_system", "kernel", "interfaces"),
    "HealthReport": ("schema_version", "state", "timestamp_utc", "checks"),
    "SafetyState": ("schema_version", "state", "source", "timestamp_utc"),
    "UpdateManifest": ("schema_version", "project", "version", "artifact_url", "sha256"),
    "EventEnvelope": ("schema_version", "event_id", "type", "source", "timestamp_utc", "sequence"),
    "ServerDiscovery": ("schema_version", "product", "remoteApiVersion", "appVersion", "hostname", "controllerCount", "robotCount", "uptimeSeconds"),
}
ENUMS = {
    "HealthReport": {"READY", "DEGRADED", "INHIBITED", "FAULT", "SAFE_STOP"},
    "SafetyState": {"READY", "INHIBITED", "FAULT", "SAFE_STOP"},
}


def _require_string(payload: dict[str, Any], name: str) -> None:
    if not isinstance(payload.get(name), str) or not payload[name]:
        raise ContractValidationError(f"{name} must be a non-empty string")


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
        if field not in {"interfaces", "checks", "sequence", "remoteApiVersion", "controllerCount", "robotCount", "uptimeSeconds"}:
            _require_string(payload, field)
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
    if contract == "UpdateManifest" and not payload["artifact_url"].startswith("https://"):
        raise ContractValidationError("artifact_url must use https")
    if contract == "EventEnvelope" and (not isinstance(payload["sequence"], int) or payload["sequence"] < 0):
        raise ContractValidationError("sequence must be a non-negative integer")
    if contract == "ServerDiscovery":
        for field in ("remoteApiVersion", "controllerCount", "robotCount", "uptimeSeconds"):
            minimum = 1 if field == "remoteApiVersion" else 0
            if not isinstance(payload[field], int) or payload[field] < minimum:
                raise ContractValidationError(f"{field} must be an integer >= {minimum}")


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
