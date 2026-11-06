# =============================================================================
# HYDRA-UMC-SDK - VLA approval
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `VlaApproval` contract: the approval a person gives to a proposed trajectory of the VLA engine (the answer of `POST /confirmations/<id>/confirm`).

It names the fingerprint of exactly that trajectory, the robot and the operator, the moment of the approval and the moment it stops being valid, and carries an
HMAC-SHA256 signature of those fields. The layer that executes the motion checks all of it; an approval is used once and is short-lived. The schema is closed.
"""

from __future__ import annotations

from typing import Any

from .contract_rules import SHA256_HEX, check_fields, require_object, text, whole
from .validation import ContractValidationError

_REQUIRED = ("approved", "fingerprint", "robot_id", "operator", "approved_at_ms", "expires_at_ms", "signature")


def validate_vla_approval(payload: dict[str, Any]) -> None:
    """The checks of the VlaApproval contract."""
    require_object(payload)
    check_fields(payload, _REQUIRED)
    if payload["approved"] is not True:
        raise ContractValidationError("approved must be true")
    for name in ("fingerprint", "signature"):
        if not (isinstance(payload[name], str) and SHA256_HEX.fullmatch(payload[name])):
            raise ContractValidationError(f"{name} must be 64 lowercase hexadecimal characters")
    text(payload, "robot_id", 64)
    text(payload, "operator", 64)
    whole(payload, "approved_at_ms", 1)
    whole(payload, "expires_at_ms", 1)
