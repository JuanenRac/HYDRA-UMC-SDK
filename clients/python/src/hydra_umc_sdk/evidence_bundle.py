# =============================================================================
# HYDRA-UMC-SDK - Evidence bundle
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `EvidenceBundle` contract: what a node hands to a development node when an incident needs a change of code.

The shape was defined by the local technician and copied by the development node; here it is a closed contract of the SDK. `bundle_checksum` is the
checksum a writer puts in the bundle and a reader recomputes: the SHA-256 (hex) of the canonical JSON of the bundle without its `checksum` field (keys
sorted, no ASCII escaping), so a bundle edited after it was assembled no longer matches. `seal_bundle` fills it in. The validator checks the shape only; that
no secret is inside is the job of the redaction that runs before a bundle is built and of the reader.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .contract_rules import check_fields, require_object
from .validation import ContractValidationError, _require_date_time

_REQUIRED = (
    "componentVersions", "relevantManifests", "redactedLogExcerpts", "reproductionSteps", "failedTests",
    "impact", "actionsAttempted", "checksum", "date", "localValidationResult",
)
_TEXT_LISTS = ("relevantManifests", "redactedLogExcerpts", "reproductionSteps", "failedTests", "actionsAttempted")
_NON_EMPTY_TEXTS = ("impact", "checksum", "localValidationResult")


def bundle_checksum(content: dict[str, Any]) -> str:
    """The checksum of a bundle: SHA-256 (hex) of its canonical JSON without the `checksum` field."""
    canonical = json.dumps({key: value for key, value in content.items() if key != "checksum"}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def seal_bundle(content: dict[str, Any]) -> dict[str, Any]:
    """The bundle with its checksum filled in (the other fields untouched), validated before it is returned."""
    sealed = {**content, "checksum": "pending"}
    sealed["checksum"] = bundle_checksum(sealed)
    validate_evidence_bundle(sealed)
    return sealed


def validate_evidence_bundle(payload: dict[str, Any]) -> None:
    """The checks of the EvidenceBundle contract (the shape; the checksum is checked by `bundle_matches_checksum`)."""
    require_object(payload)
    check_fields(payload, _REQUIRED)
    if not isinstance(payload["componentVersions"], dict):
        raise ContractValidationError("componentVersions must be an object")
    for name in _TEXT_LISTS:
        value = payload[name]
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ContractValidationError(f"{name} must be an array of texts")
    if not payload["reproductionSteps"]:
        raise ContractValidationError("reproductionSteps must have at least one step")
    for name in _NON_EMPTY_TEXTS:
        value = payload[name]
        if not isinstance(value, str) or not value:
            raise ContractValidationError(f"{name} must be a non-empty text")
    _require_date_time(payload, "date")


def bundle_matches_checksum(payload: dict[str, Any]) -> bool:
    """A valid bundle whose checksum is that of its content."""
    validate_evidence_bundle(payload)
    return bundle_checksum(payload) == payload["checksum"]
