# =============================================================================
# HYDRA-UMC-SDK - Contracts of the maintenance agent: snapshot, proposal, canary result
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The three files the maintenance agent writes besides its incidents: `NodeSnapshot` (what the edge side saw in one pass), `ChangeProposal` (a change that
a person reviews) and `CanaryDeployResult` (how far an approved change got on one node).

Consumers (the development server, the local technician, the dashboard) used to copy these shapes by hand. The wire form is the one the agent writes, with
camelCase names, and every object is closed: nothing else can slip in. Text fields reach these contracts already redacted by the agent. `schema_version`
is optional so that a file written before the contracts existed still validates.
"""

from __future__ import annotations

import re
from typing import Any

from .contract_rules import check_fields, identifier, one_of, require_object, text
from .maintenance import validate_maintenance_incident
from .validation import ContractValidationError, _require_date_time

PROPOSAL_STATUSES: tuple[str, ...] = ("pending", "approved", "rejected")
STAGES: tuple[str, ...] = ("staged", "diff_applied", "build_verified", "diff_committed", "promoted", "rolled_back")
SHA256_HEX = re.compile(r"[0-9a-f]{64}")


# --- small helpers: every one raises ContractValidationError with the field name and converts nothing ------------------------------------------------

def _object(value: Any, label: str, required: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractValidationError(f"{label} must be an object")
    check_fields(value, required, (), label)
    return value


def _array(value: Any, label: str, maximum: int) -> list[Any]:
    if not isinstance(value, list) or len(value) > maximum:
        raise ContractValidationError(f"{label} must be an array of at most {maximum} entries")
    return value


def _text(holder: dict[str, Any], name: str, maximum: int, *, minimum: int = 1, nullable: bool = False, label: str = "") -> None:
    value = holder[name]
    if value is None and nullable:
        return
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise ContractValidationError(f"{label}{name} must be {'null or ' if nullable else ''}a text of {minimum} to {maximum} characters")


def _flag(holder: dict[str, Any], name: str, *, nullable: bool = False, label: str = "") -> None:
    value = holder[name]
    if not (isinstance(value, bool) or (nullable and value is None)):
        raise ContractValidationError(f"{label}{name} must be true or false{' (or null)' if nullable else ''}")


def _whole(holder: dict[str, Any], name: str, minimum: int | None, maximum: int | None = None, *, nullable: bool = False, label: str = "") -> None:
    value = holder[name]
    if value is None and nullable:
        return
    if type(value) is not int or (minimum is not None and value < minimum) or (maximum is not None and value > maximum):
        raise ContractValidationError(f"{label}{name} must be {'null or ' if nullable else ''}an integer")


def _number(holder: dict[str, Any], name: str, minimum: float | None, maximum: float | None = None, *, nullable: bool = False, label: str = "") -> None:
    value = holder[name]
    if value is None and nullable:
        return
    if type(value) not in (int, float) or value != value or value in (float("inf"), float("-inf")):
        raise ContractValidationError(f"{label}{name} must be {'null or ' if nullable else ''}a finite number")
    if (minimum is not None and value < minimum) or (maximum is not None and value > maximum):
        raise ContractValidationError(f"{label}{name} is out of range")


def _stamp(holder: dict[str, Any], name: str, *, nullable: bool = False) -> None:
    if nullable and holder[name] is None:
        return
    _require_date_time(holder, name)


# --- NodeSnapshot ---------------------------------------------------------------------------------------------------------------------------------

_SNAPSHOT_REQUIRED = ("sourceNode", "collectedAt", "correlationId", "projects", "manifestIssues", "systemdAvailable", "systemdUnavailableReason",
                      "serviceHealth", "httpHealth", "incidents")


def validate_node_snapshot(payload: dict[str, Any]) -> None:
    """The checks of the NodeSnapshot contract (every incident inside it is checked as a MaintenanceIncident)."""
    require_object(payload)
    check_fields(payload, _SNAPSHOT_REQUIRED, ("schema_version", "hostHealth"))
    identifier(payload, "sourceNode")
    identifier(payload, "correlationId")
    _require_date_time(payload, "collectedAt")
    for entry in _array(payload["projects"], "projects", 1000):
        item = _object(entry, "projects entry", ("name", "version", "maturity", "manifestPath"))
        _text(item, "name", 200, label="projects entry ")
        _text(item, "version", 64, label="projects entry ")
        _text(item, "maturity", 64, label="projects entry ")
        _text(item, "manifestPath", 4096, label="projects entry ")
    for entry in _array(payload["manifestIssues"], "manifestIssues", 1000):
        item = _object(entry, "manifestIssues entry", ("path", "reason"))
        _text(item, "path", 4096, label="manifestIssues entry ")
        _text(item, "reason", 2000, label="manifestIssues entry ")
    _flag(payload, "systemdAvailable", nullable=True)
    reason = payload["systemdUnavailableReason"]
    if reason is not None and not (isinstance(reason, str) and len(reason) <= 2000):
        raise ContractValidationError("systemdUnavailableReason must be null or a text of at most 2000 characters")
    for entry in _array(payload["serviceHealth"], "serviceHealth", 1000):
        item = _object(entry, "serviceHealth entry", ("unitName", "active", "detail"))
        _text(item, "unitName", 256, label="serviceHealth entry ")
        _flag(item, "active", label="serviceHealth entry ")
        _text(item, "detail", 2000, minimum=0, label="serviceHealth entry ")
    for entry in _array(payload["httpHealth"], "httpHealth", 1000):
        item = _object(entry, "httpHealth entry", ("url", "reachable", "statusCode", "detail"))
        _text(item, "url", 2048, label="httpHealth entry ")
        _flag(item, "reachable", label="httpHealth entry ")
        _whole(item, "statusCode", 100, 599, nullable=True, label="httpHealth entry ")
        _text(item, "detail", 2000, minimum=0, label="httpHealth entry ")
    for entry in _array(payload["incidents"], "incidents", 10000):
        validate_maintenance_incident(entry)
    if "hostHealth" in payload:
        _validate_host_health(payload["hostHealth"])


def _validate_host_health(value: Any) -> None:
    health = _object(value, "hostHealth", ("disks", "thermal", "backups"))
    for entry in _array(health["disks"], "hostHealth.disks", 100):
        disk = _object(entry, "hostHealth.disks entry", ("path", "freeBytes", "totalBytes", "freePercent", "error"))
        _text(disk, "path", 4096, label="disk ")
        _whole(disk, "freeBytes", 0, nullable=True, label="disk ")
        _whole(disk, "totalBytes", 0, nullable=True, label="disk ")
        _number(disk, "freePercent", 0, 100, nullable=True, label="disk ")
        _text(disk, "error", 200, minimum=0, nullable=True, label="disk ")
    thermal = _object(health["thermal"], "hostHealth.thermal", ("celsius", "throttledRaw", "throttledNow", "throttledPast", "vcgencmdAvailable"))
    _number(thermal, "celsius", None, nullable=True, label="thermal ")
    _whole(thermal, "throttledRaw", 0, nullable=True, label="thermal ")
    for name in ("throttledNow", "throttledPast"):
        for flag in _array(thermal[name], f"thermal {name}", 8):
            if not isinstance(flag, str) or not 1 <= len(flag) <= 100:
                raise ContractValidationError(f"every thermal {name} entry must be a text of 1 to 100 characters")
    _flag(thermal, "vcgencmdAvailable", label="thermal ")
    backups = health["backups"]
    if backups is not None:
        item = _object(backups, "hostHealth.backups", ("directory", "count", "newestAgeDays", "error"))
        _text(item, "directory", 4096, label="backups ")
        _whole(item, "count", 0, nullable=True, label="backups ")
        _number(item, "newestAgeDays", 0, nullable=True, label="backups ")
        _text(item, "error", 200, minimum=0, nullable=True, label="backups ")


# --- ChangeProposal -------------------------------------------------------------------------------------------------------------------------------

_PROPOSAL_REQUIRED = ("proposalId", "incidentId", "correlationId", "createdAt", "projectName", "description", "diff", "rationale", "status")
_PROPOSAL_OPTIONAL = ("schema_version", "decidedBy", "decidedAt", "decisionReason", "approvedContentDigest", "allowProtectedPaths", "approvalExpiresAt",
                      "approvedBaseCommit", "approvalSignature", "generatedBy")


def validate_change_proposal(payload: dict[str, Any]) -> None:
    """The checks of the ChangeProposal contract."""
    require_object(payload)
    check_fields(payload, _PROPOSAL_REQUIRED, _PROPOSAL_OPTIONAL)
    for name in ("proposalId", "incidentId", "correlationId"):
        identifier(payload, name)
    _require_date_time(payload, "createdAt")
    text(payload, "projectName", 200)
    text(payload, "description", 100000)
    text(payload, "diff", 262144)
    text(payload, "rationale", 100000)
    one_of(payload, "status", PROPOSAL_STATUSES)
    optional_texts = (("decidedBy", 1, 200), ("decisionReason", 0, 100000), ("approvedBaseCommit", 0, 64), ("approvalSignature", 0, 1024), ("generatedBy", 1, 200))
    for name, minimum, maximum in optional_texts:
        if name in payload:
            _text(payload, name, maximum, minimum=minimum, nullable=True)
    for name in ("decidedAt", "approvalExpiresAt"):
        if name in payload:
            _stamp(payload, name, nullable=True)
    if "approvedContentDigest" in payload:
        digest = payload["approvedContentDigest"]
        if digest is not None and not (isinstance(digest, str) and SHA256_HEX.fullmatch(digest)):
            raise ContractValidationError("approvedContentDigest must be null or 64 lowercase hexadecimal characters")
    if "allowProtectedPaths" in payload:
        _flag(payload, "allowProtectedPaths")


# --- CanaryDeployResult ---------------------------------------------------------------------------------------------------------------------------

_CANARY_REQUIRED = ("deployId", "proposalId", "projectName", "startedAt", "finishedAt", "promoted", "stageReached", "buildOutput", "detail")


def validate_canary_deploy_result(payload: dict[str, Any]) -> None:
    """The checks of the CanaryDeployResult contract."""
    require_object(payload)
    check_fields(payload, _CANARY_REQUIRED, ("schema_version", "backupPath", "patchPath"))
    identifier(payload, "deployId")
    identifier(payload, "proposalId")
    text(payload, "projectName", 200)
    _require_date_time(payload, "startedAt")
    _require_date_time(payload, "finishedAt")
    _flag(payload, "promoted")
    one_of(payload, "stageReached", STAGES)
    _text(payload, "buildOutput", 1_000_000, minimum=0)
    _text(payload, "detail", 100000, minimum=0)
    for name in ("backupPath", "patchPath"):
        if name in payload:
            _text(payload, name, 4096, minimum=0, nullable=True)
