#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Example: P07's own acceptance criterion, end to end
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""3 real services (STUDIO, HYDRA-UMC-SERVER, a URTC relay) each log their
own view of one real incident. An operator gets paged for STUDIO's own
"command rejected" error - the LAST symptom, not the cause. This example
shows `trace_first_failure()` walking the real `caused_by` chain back to
the actual first failure, and `StructuredLogEntry.redacted()` sanitizing
a real leaked token along the way.

    PYTHONPATH=clients/python/src python examples/python/trace_first_failure.py
"""
from __future__ import annotations

from hydra_umc_sdk import StructuredLogEntry, trace_first_failure

root = StructuredLogEntry(
    component="urtc-relay", correlation_id="c-urtc-9021", version="0.3.0",
    timestamp_utc="2026-01-05T10:00:00Z", level="error",
    message="CAN bus timeout on 0x1A8 readback, auth_token=sk-live-abc123 in the retry log",
    error_cause="bus timeout after 3 retries", caused_by=None,
)
middle = StructuredLogEntry(
    component="hydra-umc-server", correlation_id="c-server-4471", version="0.6.2",
    timestamp_utc="2026-01-05T10:00:01Z", level="error",
    message="robot command failed: relay did not confirm",
    error_cause="upstream relay error", caused_by=("urtc-relay", "c-urtc-9021"),
)
leaf = StructuredLogEntry(
    component="studio", correlation_id="c-studio-2004", version="0.5.5",
    timestamp_utc="2026-01-05T10:00:02Z", level="error",
    message="command rejected by server",
    error_cause="server returned 500", caused_by=("hydra-umc-server", "c-server-4471"),
)

incident = [leaf, middle, root]

print("An operator is paged for this alert:")
print(f"  [{leaf.component}] {leaf.message}")

first_failure = trace_first_failure(incident, start_correlation_id="c-studio-2004")
print(f"\ntrace_first_failure() walks the caused_by chain back to the real origin:")
print(f"  [{first_failure.component}] {first_failure.message}")

sanitized = first_failure.redacted(lambda text: text.replace("sk-live-abc123", "[REDACTED]"))
print(f"\nredacted() before this ever leaves the process:")
print(f"  [{sanitized.component}] {sanitized.message}")
