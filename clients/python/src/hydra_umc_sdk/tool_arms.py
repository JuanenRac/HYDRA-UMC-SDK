# =============================================================================
# HYDRA-UMC-SDK - Tool arms
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `ToolArms` contract: the arm state of the URTC tools, as `GET /tool-arms` of the safety zones service answers it.

A tool is armed when its power stage may act. The service only records what the driving service reports; a report older than `ttlSeconds` is stale and is
not counted in `armedCount`. The schema is closed. A consumer shows a stale armed tool as a warning and never as safe.
"""

from __future__ import annotations

import re
from typing import Any

from .contract_rules import check_fields, real, require_object, whole
from .validation import ContractValidationError

MAX_ARMS = 256
MAX_TOOL_ID = 24
_ROBOT = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:\-]{0,63}")
_REQUIRED = ("schema_version", "ttlSeconds", "arms", "armedCount", "staleCount")
_ARM_FIELDS = ("robot", "toolId", "armed", "by", "seq", "ageSeconds", "stale")


def validate_tool_arms(payload: dict[str, Any]) -> None:
    """The checks of the ToolArms contract."""
    require_object(payload)
    check_fields(payload, _REQUIRED)
    real(payload, "ttlSeconds", 0, exclusive_minimum=True)
    arms = payload["arms"]
    if not isinstance(arms, list) or len(arms) > MAX_ARMS:
        raise ContractValidationError(f"arms must be a list of at most {MAX_ARMS}")
    for item in arms:
        arm = require_object(item, "arm")
        check_fields(arm, _ARM_FIELDS, (), "arm")
        if not isinstance(arm["robot"], str) or not _ROBOT.fullmatch(arm["robot"]):
            raise ContractValidationError("robot must be a robot id of letters, digits and . _ : - (1 to 64 characters)")
        whole(arm, "toolId", 0, MAX_TOOL_ID)
        for name in ("armed", "stale"):
            if type(arm[name]) is not bool:
                raise ContractValidationError(f"{name} must be true or false")
        if not isinstance(arm["by"], str) or len(arm["by"]) > 64:
            raise ContractValidationError("by must be a text of at most 64 characters")
        whole(arm, "seq", 1)
        real(arm, "ageSeconds", 0)
    whole(payload, "armedCount", 0)
    whole(payload, "staleCount", 0)
