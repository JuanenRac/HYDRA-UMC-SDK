#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Example: I02's two real evidence gates
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Shows the two questions I02 keeps separate, each with its own real gate:

1. `concludes_success()` - given ONE Operation's `result`, was it really
   confirmed, or just reported by a queue? A stale run_id or disabled
   observers must never let outcome="success" pass through.
2. `is_capability_usable()` - does `target` even support `kind` at all
   (declared), AND was that support actually, recently verified?
   A capability can be declared forever without ever being usable.

    PYTHONPATH=clients/python/src python examples/python/i02_result_and_capability.py
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from hydra_umc_sdk import (
    CapabilityStatus,
    concludes_success,
    is_capability_usable,
    parse_operation_result,
)

NOW = datetime(2026, 1, 5, 10, 0, 10, tzinfo=timezone.utc)

print("=== concludes_success() ===\n")

real_run_result = parse_operation_result({
    "run_id": "run-2026-01-05-0007",
    "origin": "real",
    "observers_enabled": True,
    "outcome": "success",
    "accepted_at_utc": "2026-01-05T10:00:01Z",
    "executed_at_utc": "2026-01-05T10:00:06Z",
    "observed_at_utc": "2026-01-05T10:00:09Z",
})
ok, reason = concludes_success(real_run_result, expected_run_id="run-2026-01-05-0007")
print(f"real, active, matching run   -> {ok}: {reason}")

stale_result = parse_operation_result({
    "run_id": "run-2026-01-04-0003",  # a PREVIOUS run's message, arriving late
    "origin": "real",
    "observers_enabled": True,
    "outcome": "success",
    "observed_at_utc": "2026-01-04T22:00:00Z",
})
ok, reason = concludes_success(stale_result, expected_run_id="run-2026-01-05-0007")
print(f"result from a different run  -> {ok}: {reason}")

no_observers_result = parse_operation_result({
    "run_id": "run-2026-01-05-0007",
    "origin": "simulated",
    "observers_enabled": False,  # a dry-run/simulation with observation off
    "outcome": "success",
})
ok, reason = concludes_success(no_observers_result, expected_run_id="run-2026-01-05-0007")
print(f"observers disabled            -> {ok}: {reason}")

print("\n=== is_capability_usable() ===\n")

never_checked = CapabilityStatus(target_kind="robot", target_id="controller-1:robot-2", kind="move_to_pose", declared=True)
usable, reason = is_capability_usable(never_checked, NOW)
print(f"declared, never checked       -> {usable}: {reason}")

stale_check = CapabilityStatus(
    target_kind="robot", target_id="controller-1:robot-2", kind="move_to_pose", declared=True,
    last_checked_at=NOW - timedelta(hours=6), max_age_seconds=3600, last_check_outcome="verified",
)
usable, reason = is_capability_usable(stale_check, NOW)
print(f"declared, check gone stale     -> {usable}: {reason}")

fresh_check = CapabilityStatus(
    target_kind="robot", target_id="controller-1:robot-2", kind="move_to_pose", declared=True,
    last_checked_at=NOW - timedelta(seconds=30), max_age_seconds=3600, last_check_outcome="verified",
    checked_configuration="config-rev-7",
)
usable, reason = is_capability_usable(fresh_check, NOW)
print(f"declared, recently verified    -> {usable}: {reason}")
