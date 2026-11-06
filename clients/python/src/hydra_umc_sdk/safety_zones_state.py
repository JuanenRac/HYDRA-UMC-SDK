# =============================================================================
# HYDRA-UMC-SDK - Safety zones state
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `SafetyZonesState` contract: the latest verdict of the safety zones service, as `GET /state` answers it.

The signed state is the one `SafetyState` describes; the rest is what a panel shows next to it. The schema is closed. A consumer acts on the signed state only,
never on the counts or the breaches.
"""

from __future__ import annotations

import re
from typing import Any

from .contract_rules import SHA256_HEX, check_fields, one_of, require_object, whole
from .validation import ContractValidationError, validate

STATES: tuple[str, ...] = ("READY", "INHIBITED", "FAULT", "SAFE_STOP")
ALGORITHMS: tuple[str, ...] = ("HMAC-SHA256", "Ed25519")
MAX_BREACHES = 20
_SIGNATURE = re.compile(r"[0-9a-f]{64}|[0-9a-f]{128}")
_REQUIRED = ("sdkSafetyState", "reason")
_OPTIONAL = ("sdkSafetyStateSignature", "armorInhibitOnly", "configSha256", "separation", "breaches", "breachCount", "estopRequestCount")


def validate_safety_zones_state(payload: dict[str, Any]) -> None:
    """The checks of the SafetyZonesState contract."""
    require_object(payload)
    check_fields(payload, _REQUIRED, _OPTIONAL)
    if not isinstance(payload["sdkSafetyState"], dict):
        _fail("sdkSafetyState must be an object")
    validate("SafetyState", payload["sdkSafetyState"])
    if payload["reason"] is not None and not isinstance(payload["reason"], str):
        _fail("reason must be a text or null")
    if "sdkSafetyStateSignature" in payload:
        signature = require_object(payload["sdkSafetyStateSignature"], "sdkSafetyStateSignature")
        check_fields(signature, ("alg", "key_id", "counter", "sig"), (), "sdkSafetyStateSignature")
        one_of(signature, "alg", ALGORITHMS)
        if not isinstance(signature["key_id"], str) or not 1 <= len(signature["key_id"]) <= 64:
            _fail("key_id must be a text of 1 to 64 characters")
        whole(signature, "counter", 0)
        if not isinstance(signature["sig"], str) or not _SIGNATURE.fullmatch(signature["sig"]):
            _fail("sig must be 64 or 128 lowercase hexadecimal characters")
    if "armorInhibitOnly" in payload and payload["armorInhibitOnly"] is not True:
        _fail("armorInhibitOnly must be true when present")
    if "configSha256" in payload and not (isinstance(payload["configSha256"], str) and SHA256_HEX.fullmatch(payload["configSha256"])):
        _fail("configSha256 must be 64 lowercase hexadecimal characters")
    if "separation" in payload:
        require_object(payload["separation"], "separation")
    if "breaches" in payload:
        breaches = payload["breaches"]
        if not isinstance(breaches, list) or len(breaches) > MAX_BREACHES:
            _fail(f"breaches must be a list of at most {MAX_BREACHES}")
        for item in breaches:
            entry = require_object(item, "breach")
            check_fields(entry, ("zone_id", "level", "object_id"), (), "breach")
            for name, limit in (("zone_id", 128), ("level", 32), ("object_id", 128)):
                if not isinstance(entry[name], str) or len(entry[name]) > limit:
                    _fail(f"{name} must be a text of at most {limit} characters")
    for name in ("breachCount", "estopRequestCount"):
        if name in payload:
            whole(payload, name, 0)


def _fail(message: str) -> None:
    raise ContractValidationError(message)
