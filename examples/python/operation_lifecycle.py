#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Example: the P03 Operation lifecycle, end to end
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Walks one Operation through its real lifecycle and shows the 2 real
guardrails `validate_status_transition()` enforces: the forward path is
legal step by step, and a status jump that would silently collapse a
distinct stage (e.g. "queued" straight to "confirmed", skipping "sent")
is rejected instead.

    PYTHONPATH=clients/python/src python examples/python/operation_lifecycle.py
"""
from __future__ import annotations

import json

from hydra_umc_sdk import OperationRecord, validate_status_transition

operation = {
    "schema_version": "1.0",
    "operation_id": "op-9c21",
    "correlation_id": "mission-pick-and-place-14",
    "kind": "move_to_pose",
    "target": {"kind": "robot", "id": "controller-1:robot-2"},
    "status": "received",
    "requested_at_utc": "2026-01-05T10:00:00Z",
    "updated_at_utc": "2026-01-05T10:00:00Z",
    "params": {"pose": {"x": 80.0, "y": 12.5, "z": 30.0}},
}

record = OperationRecord.from_payload(operation)
print(f"loaded {record.operation_id} for {record.target_kind}:{record.target_id}, status={record.status}")

# The real forward path - each step is a distinct, observable stage.
forward_path = ["authorized", "queued", "sent", "confirmed", "terminated"]
status = record.status
for next_status in forward_path:
    ok = validate_status_transition(status, next_status)
    print(f"  {status} -> {next_status}: {'legal' if ok else 'REJECTED'}")
    if ok:
        status = next_status

# The point of this contract: an update that tries to skip straight from
# "queued" to "confirmed" - silently treating "sent" as if it never
# mattered - must be rejected, not accepted as a shortcut.
skip_attempt = validate_status_transition("queued", "confirmed")
print(f"\nqueued -> confirmed (skipping sent): {'legal' if skip_attempt else 'REJECTED - exactly what P03 exists to catch'}")

print("\nfinal operation payload:")
print(json.dumps({**operation, "status": status, "updated_at_utc": "2026-01-05T10:00:07Z"}, indent=2))
