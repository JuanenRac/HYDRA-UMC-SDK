#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Example: the T07/I60 before/after check on two real pairs
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Runs `compare_runs()` on two recorded ScenarioOutcome pairs:

  1. a fix whose regression suite went green but whose base fingerprint
     never changed - `apparent-success`, not promotable;
  2. a fix that reproduced before, did not after, on a base that
     genuinely moved - `regression-fixed`, promotable.

    PYTHONPATH=clients/python/src python examples/python/compare_scenario_runs.py
"""
from __future__ import annotations

import json

from hydra_umc_sdk.scenario import compare_runs

# 1. Apparent success: same base_fingerprint before and after.
APPARENT_BEFORE = {
    "schema_version": "1.0", "scenario_id": "ops-agent/repair/nozzle-drift",
    "run_id": "r-101", "base_fingerprint": "src@9f2a1c", "phase": "before",
    "repro_case": "nozzle-drift-after-1000-cycles",
    "observed": {"outcome": "reproduced", "exit_code": 1, "evidence": "drift 0.42mm > 0.20mm tolerance"},
    "timestamp_utc": "2026-01-05T10:00:00Z",
}
APPARENT_AFTER = {
    "schema_version": "1.0", "scenario_id": "ops-agent/repair/nozzle-drift",
    "run_id": "r-102", "base_fingerprint": "src@9f2a1c", "phase": "after",
    "repro_case": "nozzle-drift-after-1000-cycles",
    "observed": {"outcome": "not-reproduced", "exit_code": 0, "evidence": "regression suite green"},
    "timestamp_utc": "2026-01-05T10:40:00Z",
}

# 2. Genuine fix: the base moved between the runs.
FIXED_BEFORE = {
    "schema_version": "1.0", "scenario_id": "ops-agent/repair/nozzle-drift",
    "run_id": "r-201", "base_fingerprint": "src@9f2a1c", "phase": "before",
    "repro_case": "nozzle-drift-after-1000-cycles",
    "observed": {"outcome": "reproduced", "exit_code": 1, "evidence": "drift 0.42mm > 0.20mm tolerance"},
    "timestamp_utc": "2026-01-05T11:00:00Z",
}
FIXED_AFTER = {
    "schema_version": "1.0", "scenario_id": "ops-agent/repair/nozzle-drift",
    "run_id": "r-202", "base_fingerprint": "src@3d81ee", "phase": "after",
    "repro_case": "nozzle-drift-after-1000-cycles",
    "observed": {"outcome": "not-reproduced", "exit_code": 0, "evidence": "drift 0.06mm, 1500 cycles"},
    "timestamp_utc": "2026-01-05T11:55:00Z",
}


def main() -> int:
    for label, before, after in (
        ("apparent success", APPARENT_BEFORE, APPARENT_AFTER),
        ("genuine fix", FIXED_BEFORE, FIXED_AFTER),
    ):
        result = compare_runs(before, after)
        print(f"{label}: {json.dumps(result.to_dict(), indent=2)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
