# =============================================================================
# HYDRA-UMC-SDK - P07: useful observability across services
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Shared structured-log entry, process-lifecycle states, and the one real
capability P07 is actually about: given a chain of structured log entries
across several services that all trace back to the same real failure,
identify the FIRST component that failed - not just the last one that
happened to notice and report it.

Builds on the existing `EventEnvelope` contract (`correlation_id` is
already one of its optional fields) rather than introducing a competing
wire shape - a `StructuredLogEntry` here is the payload a service puts
inside an `EventEnvelope`, not a replacement for it.

Distinct from `RiskLevel`/`HealthReport`/`SafetyState` (already published
contracts): those describe a ROBOT's or a MACHINE's own safety state.
`ProcessLifecycleState` describes whether a SERVICE PROCESS itself
(SERVER, ORCHESTRATOR, a bridge, ...) is observably alive and reachable -
a different, complementary concern, not a duplicate of either.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any


class ProcessLifecycleState(str, Enum):
    """The 5 real, distinct states P07 calls for - never collapsed into
    a single boolean "up"/"down". A caller that only ever reports ALIVE
    or DISCONNECTED, skipping READY/DEGRADED/UNKNOWN, is under-using this
    enum, not using a simpler one correctly."""

    ALIVE = "alive"
    READY = "ready"
    DEGRADED = "degraded"
    DISCONNECTED = "disconnected"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class StructuredLogEntry:
    """One real, structured log/diagnostic entry - the 4 fields P07 names
    explicitly (`component`, `correlation_id`, `version`, and
    `error_cause` when this entry reports a real error) plus the one
    field that makes cross-service failure tracing possible at all:
    `caused_by`.

    `caused_by`, when set, names the (component, correlation_id) of the
    EARLIER entry that this one's own failure is a downstream symptom
    of - not a duplicate correlation_id for the same request, a real
    pointer to a DIFFERENT, earlier failure this one was caused by. A
    service that only logs its own failure with no `caused_by` is
    reporting a ROOT cause (or doesn't know its own upstream cause,
    which is also honest - see UNKNOWN above).
    """

    component: str
    correlation_id: str
    version: str
    timestamp_utc: str
    level: str  # "info" | "warn" | "error"
    message: str
    error_cause: str | None = None
    caused_by: tuple[str, str] | None = None  # (component, correlation_id) of the earlier entry

    def redacted(self, redactor: Any) -> "StructuredLogEntry":
        """Returns a copy with `message` and `error_cause` passed through
        `redactor` (a callable str -> str, e.g. a project's own
        `redact_secrets()`) - the real "exportar diagnóstico saneado"
        requirement. Every other field is left untouched: `component`/
        `correlation_id`/`version`/`caused_by` are structural identifiers,
        never where a real secret would land."""
        return replace(
            self,
            message=redactor(self.message),
            error_cause=redactor(self.error_cause) if self.error_cause is not None else None,
        )


class BoundedLog:
    """A real, size-capped log - "acotar tamaño de logs, colas y
    reintentos" as actual enforced behavior, not just a design note.
    Drops the OLDEST entry once `max_entries` is exceeded (same
    drop-oldest policy this ecosystem's own bounded queues already use
    elsewhere, e.g. HYDRA-UMC's RelayRxQueue) - a caller diagnosing a
    live incident needs the most RECENT context, not the earliest.
    """

    def __init__(self, max_entries: int):
        if max_entries <= 0:
            raise ValueError("max_entries must be a positive integer")
        self.max_entries = max_entries
        self._entries: list[StructuredLogEntry] = []
        self.dropped_count = 0

    def append(self, entry: StructuredLogEntry) -> None:
        self._entries.append(entry)
        if len(self._entries) > self.max_entries:
            self._entries.pop(0)
            self.dropped_count += 1

    def entries(self) -> tuple[StructuredLogEntry, ...]:
        return tuple(self._entries)

    def __len__(self) -> int:
        return len(self._entries)


def trace_first_failure(
    entries: list[StructuredLogEntry],
    start_correlation_id: str,
) -> StructuredLogEntry | None:
    """P07's own literal acceptance criterion, as real, tested code: given
    every structured log entry collected for one real incident (from
    however many services), walk the `caused_by` chain starting from the
    entry matching `start_correlation_id` back to the ROOT entry - the
    actual first component that failed, not whichever entry a caller
    happened to look at first (in practice, usually the LAST service to
    notice and report the failure, since that is typically the one an
    operator is paged for).

    Returns None if no entry matches `start_correlation_id` at all.
    Returns the starting entry itself if it has no `caused_by` (it IS
    the root cause). Stops and returns the last entry successfully
    resolved if a `caused_by` reference points to a (component,
    correlation_id) pair not present in `entries` - a real, incomplete
    trace (e.g. the origin service's own log was never collected) is
    reported as itself, never silently treated as if the chain ended
    there by design.
    """
    by_key = {(entry.component, entry.correlation_id): entry for entry in entries}
    current = next((entry for entry in entries if entry.correlation_id == start_correlation_id), None)
    if current is None:
        return None
    seen: set[tuple[str, str]] = set()
    while current.caused_by is not None:
        key = (current.component, current.correlation_id)
        if key in seen:
            break  # a real cycle in the data - stop rather than loop forever; this is malformed input, not a valid chain
        seen.add(key)
        upstream = by_key.get(current.caused_by)
        if upstream is None:
            break  # the chain points further back than what was collected - return the earliest entry actually available
        current = upstream
    return current
