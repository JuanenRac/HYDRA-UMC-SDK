# =============================================================================
# HYDRA-UMC-SDK - One finished production cycle
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `ProductionEvent` contract: one finished cycle of one machine or robot.

It carries what the production reports need to compute OEE: when the cycle ended, how long it took and whether the part was good. A producer (the orchestrator, a
bridge or the robot itself) publishes it and the reports read it. The schema is closed, so nothing else can slip in. `production_event_fields` gives the two numbers
in the form the data lake stores them (one sample per cycle, `good` as 1.0 or 0.0 and `cycleTimeS`, both written at the same instant).
"""

from __future__ import annotations

import math
import re
from typing import Any

from .validation import ContractValidationError, _require_date_time

MAX_CYCLE_TIME_S = 604800  # one week
IDENTIFIER = re.compile(r"[A-Za-z0-9._:-]{1,64}")

_KEYS = frozenset({"schema_version", "source_id", "at_utc", "good", "cycle_time_s", "job_id", "reject_reason"})
_REQUIRED = ("schema_version", "source_id", "at_utc", "good", "cycle_time_s")


def validate_production_event(payload: dict[str, Any]) -> None:
    """The checks of the ProductionEvent contract."""
    if not isinstance(payload, dict):
        raise ContractValidationError("payload must be an object")
    for field in _REQUIRED:
        if field not in payload:
            raise ContractValidationError(f"missing required field: {field}")
    unknown = sorted(set(payload) - _KEYS)
    if unknown:
        raise ContractValidationError(f"unsupported field(s): {', '.join(unknown)}")
    if payload["schema_version"] != "1.0":
        raise ContractValidationError("schema_version must be '1.0'")
    for name in ("source_id", "job_id"):
        if name in payload and not (isinstance(payload[name], str) and IDENTIFIER.fullmatch(payload[name])):
            raise ContractValidationError(f"{name} must be 1 to 64 letters, digits, dots, colons, dashes or underscores")
    _require_date_time(payload, "at_utc")
    if type(payload["good"]) is not bool:
        raise ContractValidationError("good must be true or false")
    cycle = payload["cycle_time_s"]
    if type(cycle) not in (int, float) or not math.isfinite(cycle) or not 0 < cycle <= MAX_CYCLE_TIME_S:
        raise ContractValidationError(f"cycle_time_s must be a number greater than 0 and at most {MAX_CYCLE_TIME_S}")
    if "reject_reason" in payload and not (isinstance(payload["reject_reason"], str) and 1 <= len(payload["reject_reason"]) <= 120):
        raise ContractValidationError("reject_reason must be a text of 1 to 120 characters")


def production_event_fields(payload: dict[str, Any]) -> dict[str, float]:
    """The fields of the data lake sample of a valid event: `good` as 1.0 or 0.0 and `cycleTimeS`."""
    validate_production_event(payload)
    return {"good": 1.0 if payload["good"] else 0.0, "cycleTimeS": float(payload["cycle_time_s"])}
