# =============================================================================
# HYDRA-UMC-SDK - Capability: declared support vs. recently verified
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Whether a target supports a given operation kind at all (`declared` - a
static claim from a manifest or descriptor) is genuinely different data
from whether that support was actually, recently verified
(`last_checked_at`/`checked_configuration`/`max_age_seconds`). Collapsing
both into one boolean ("supported": true) is exactly the gap exists
to close: a target can declare a capability it has never once
successfully exercised, or one whose last real check is long stale
because the target's own configuration moved on since.

`is_capability_usable()` is the one real gate a caller should use before
relying on `kind` against `target` - it never trusts `declared` alone,
and mirrors this SDK's own `operation.py`'s `concludes_success()` and the
ecosystem's established calibration/observation freshness pattern
(HYDRA-UMC-SAFETY-ZONES' own `calibration.py`/`observation.py`): never
checked, checked too long ago, or a failed/unknown outcome all count as
"not usable right now", never silently as "probably fine".
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

CAPABILITY_CHECK_OUTCOMES: tuple[str, ...] = ("verified", "failed", "unknown")


class CapabilityError(ValueError):
    """Raised when a Capability payload violates a required invariant."""


@dataclass(frozen=True)
class CapabilityStatus:
    target_kind: str
    target_id: str
    kind: str
    declared: bool
    last_checked_at: datetime | None = None
    checked_configuration: str | None = None
    max_age_seconds: float | None = None
    last_check_outcome: str | None = None
    last_check_reason: str | None = None

    def __post_init__(self) -> None:
        if self.max_age_seconds is not None and (
            isinstance(self.max_age_seconds, bool) or self.max_age_seconds <= 0
        ):
            raise CapabilityError("max_age_seconds must be a positive number")
        if self.last_check_outcome is not None and self.last_check_outcome not in CAPABILITY_CHECK_OUTCOMES:
            raise CapabilityError(
                f"last_check_outcome must be one of {CAPABILITY_CHECK_OUTCOMES}, got {self.last_check_outcome!r}"
            )


def capability_check_age_seconds(status: CapabilityStatus, now: datetime) -> float | None:
    """None when `status` has never been checked at all - a real, honest
    "no evidence exists" distinct from "evidence exists but is old"."""
    if status.last_checked_at is None:
        return None
    return (now - status.last_checked_at).total_seconds()


def is_capability_check_stale(status: CapabilityStatus, now: datetime) -> bool:
    """Mirrors HYDRA-UMC-SAFETY-ZONES' own is_observation_stale()/
    is_calibration_expired(): never checked, timestamped in the future
    (clock skew), or older than its own declared max_age_seconds all
    count as stale. A check with no max_age_seconds declared at all is
    also treated as stale - a single past check is never, by itself,
    permanently valid; a real expiry must be stated for a check to ever
    be trusted as current."""
    age = capability_check_age_seconds(status, now)
    if age is None or age < 0:
        return True
    if status.max_age_seconds is None:
        return True
    return age > status.max_age_seconds


def is_capability_usable(status: CapabilityStatus, now: datetime) -> tuple[bool, str]:
    """The real gate: `declared` alone is never enough, and neither is a
    check that once passed but has since gone stale or come back
    failed/unknown. Returns (True, reason) only when `kind` is both
    declared AND backed by a real, recent, successful check."""
    if not status.declared:
        return False, f"{status.kind} is not declared as a supported capability of {status.target_kind}:{status.target_id}"
    if status.last_check_outcome == "failed":
        reason = status.last_check_reason or "the most recent check failed"
        return False, f"{status.kind} is declared but its last check failed: {reason}"
    if is_capability_check_stale(status, now):
        return False, f"{status.kind} is declared but has no sufficiently recent verified check"
    if status.last_check_outcome == "unknown":
        reason = status.last_check_reason or "outcome unknown"
        return False, f"{status.kind} is declared but its last check outcome is unknown: {reason}"
    age = capability_check_age_seconds(status, now)
    return True, f"{status.kind} is declared and was verified {age:.1f}s ago"


def parse_capability_status(payload: dict[str, Any]) -> CapabilityStatus:
    """Validates `payload` against the real Capability contract first
    (raises ContractValidationError on anything non-conformant) and only
    then builds the status - never silently accepts a payload this
    contract itself would reject."""
    from .validation import validate

    validate("Capability", payload)
    target = payload["target"]
    last_checked_raw = payload.get("last_checked_at_utc")
    last_checked_at = datetime.fromisoformat(last_checked_raw.replace("Z", "+00:00")) if last_checked_raw else None
    return CapabilityStatus(
        target_kind=target["kind"],
        target_id=target["id"],
        kind=payload["kind"],
        declared=payload["declared"],
        last_checked_at=last_checked_at,
        checked_configuration=payload.get("checked_configuration"),
        max_age_seconds=payload.get("max_age_seconds"),
        last_check_outcome=payload.get("last_check_outcome"),
        last_check_reason=payload.get("last_check_reason"),
    )
