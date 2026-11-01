# =============================================================================
# HYDRA-UMC-SDK - Maintenance incident
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `MaintenanceIncident` contract: one observation that the maintenance agent of a node reports.

The agent reads a node, finds something off (a service that should run and does not, a manifest that does not parse, a health check that fails) and writes
one incident for it. Consumers (the development server, the local technician, the dashboard) used to copy the shape by hand and had already drifted apart
(`incident_id` here, `incidentId` there). The wire form is the one the agent writes, with camelCase names, and it is closed: nothing else can slip in.

The text fields reach this contract already redacted by the agent; `redactionLevel` says so (`sanitized`), and a consumer that stores or forwards incidents
refuses `raw` unless its configuration allows it. `schema_version` is optional so that an incident written before the contract existed still validates.
"""

from __future__ import annotations

from typing import Any

from .contract_rules import check_fields, identifier, one_of, require_object, text
from .validation import ContractValidationError, _require_date_time

SEVERITIES: tuple[str, ...] = ("info", "warning", "critical")
REDACTION_LEVELS: tuple[str, ...] = ("sanitized", "raw")
MAX_EVIDENCE_REFS = 50

_REQUIRED = ("incidentId", "sourceNode", "detectedAt", "severity", "component", "symptom", "evidenceRefs", "redactionLevel", "requestedBy", "correlationId")
_OPTIONAL = ("schema_version",)


def validate_maintenance_incident(payload: dict[str, Any]) -> None:
    """The checks of the MaintenanceIncident contract."""
    require_object(payload)
    check_fields(payload, _REQUIRED, _OPTIONAL)
    for name in ("incidentId", "sourceNode", "correlationId"):
        identifier(payload, name)
    _require_date_time(payload, "detectedAt")
    one_of(payload, "severity", SEVERITIES)
    text(payload, "component", 500)
    text(payload, "symptom", 2000)
    refs = payload["evidenceRefs"]
    if not isinstance(refs, list) or len(refs) > MAX_EVIDENCE_REFS:
        raise ContractValidationError(f"evidenceRefs must be an array of at most {MAX_EVIDENCE_REFS} texts")
    for ref in refs:
        if not isinstance(ref, str) or not 1 <= len(ref) <= 1000:
            raise ContractValidationError("every evidenceRefs entry must be a text of 1 to 1000 characters")
    one_of(payload, "redactionLevel", REDACTION_LEVELS)
    requested_by = payload["requestedBy"]
    if requested_by is not None and not (isinstance(requested_by, str) and 1 <= len(requested_by) <= 120):
        raise ContractValidationError("requestedBy must be null or a text of 1 to 120 characters")


def incident_may_be_stored(payload: dict[str, Any], *, allow_raw: bool = False) -> bool:
    """Whether a consumer that keeps or forwards incidents may take this one: a valid incident whose redaction level is `sanitized`, or `raw` when the consumer allows it."""
    validate_maintenance_incident(payload)
    return payload["redactionLevel"] == "sanitized" or allow_raw
