# =============================================================================
# HYDRA-UMC-SDK - P07 lifecycle/structured-log tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import unittest

from hydra_umc_sdk.lifecycle import (
    BoundedLog,
    ProcessLifecycleState,
    StructuredLogEntry,
    trace_first_failure,
)


def _entry(component, correlation_id, **over):
    fields = dict(
        component=component, correlation_id=correlation_id, version="1.0.0",
        timestamp_utc="2026-01-02T09:00:00Z", level="error", message="something failed",
        error_cause=None, caused_by=None,
    )
    fields.update(over)
    return StructuredLogEntry(**fields)


class ProcessLifecycleStateTests(unittest.TestCase):
    def test_has_exactly_the_5_states_p07_names(self):
        self.assertEqual(
            {s.value for s in ProcessLifecycleState},
            {"alive", "ready", "degraded", "disconnected", "unknown"},
        )


class StructuredLogEntryRedactionTests(unittest.TestCase):
    def test_redacted_passes_message_and_error_cause_through_the_redactor(self):
        entry = _entry("server", "c-1", message="token=abc123", error_cause="leaked password=hunter2")
        redacted = entry.redacted(lambda text: text.replace("abc123", "[REDACTED]").replace("hunter2", "[REDACTED]"))
        self.assertEqual(redacted.message, "token=[REDACTED]")
        self.assertEqual(redacted.error_cause, "leaked password=[REDACTED]")

    def test_redacted_leaves_structural_fields_untouched(self):
        entry = _entry("server", "c-1")
        redacted = entry.redacted(lambda text: "REPLACED")
        self.assertEqual(redacted.component, "server")
        self.assertEqual(redacted.correlation_id, "c-1")
        self.assertEqual(redacted.version, "1.0.0")

    def test_redacted_handles_a_none_error_cause(self):
        entry = _entry("server", "c-1", error_cause=None)
        redacted = entry.redacted(lambda text: "REPLACED")
        self.assertIsNone(redacted.error_cause)

    def test_original_entry_is_not_mutated(self):
        entry = _entry("server", "c-1", message="token=abc123")
        entry.redacted(lambda text: "REPLACED")
        self.assertEqual(entry.message, "token=abc123")  # frozen dataclass + replace() - the original is untouched


class BoundedLogTests(unittest.TestCase):
    def test_rejects_a_non_positive_max_entries(self):
        with self.assertRaises(ValueError):
            BoundedLog(0)
        with self.assertRaises(ValueError):
            BoundedLog(-1)

    def test_keeps_entries_under_the_cap(self):
        log = BoundedLog(max_entries=3)
        for i in range(3):
            log.append(_entry("server", f"c-{i}"))
        self.assertEqual(len(log), 3)
        self.assertEqual(log.dropped_count, 0)

    def test_drops_the_oldest_entry_once_over_the_cap(self):
        log = BoundedLog(max_entries=2)
        log.append(_entry("server", "c-1"))
        log.append(_entry("server", "c-2"))
        log.append(_entry("server", "c-3"))
        self.assertEqual([e.correlation_id for e in log.entries()], ["c-2", "c-3"])
        self.assertEqual(log.dropped_count, 1)

    def test_dropped_count_accumulates_across_many_overflows(self):
        log = BoundedLog(max_entries=1)
        for i in range(5):
            log.append(_entry("server", f"c-{i}"))
        self.assertEqual(log.dropped_count, 4)
        self.assertEqual(len(log), 1)


class TraceFirstFailureTests(unittest.TestCase):
    def test_returns_none_when_no_entry_matches(self):
        self.assertIsNone(trace_first_failure([_entry("server", "c-1")], "c-nonexistent"))

    def test_an_entry_with_no_caused_by_is_its_own_root(self):
        entry = _entry("orchestrator", "c-1", caused_by=None)
        self.assertIs(trace_first_failure([entry], "c-1"), entry)

    def test_walks_a_real_multi_service_chain_back_to_the_first_failure(self):
        # The real P07 acceptance criterion: SERVER reported the failure
        # last (an operator would be paged for THIS one), but the actual
        # first failure was in the URTC firmware relay, two hops upstream.
        root = _entry("urtc-relay", "c-urtc-9", caused_by=None, message="CAN bus timeout")
        middle = _entry("hydra-umc-server", "c-server-4", caused_by=("urtc-relay", "c-urtc-9"), message="robot command failed")
        leaf = _entry("studio", "c-studio-2", caused_by=("hydra-umc-server", "c-server-4"), message="command rejected")
        result = trace_first_failure([leaf, middle, root], "c-studio-2")
        self.assertIs(result, root)
        self.assertEqual(result.component, "urtc-relay")

    def test_stops_at_the_earliest_entry_actually_collected_when_the_chain_extends_further_back(self):
        # A real, incomplete trace (the true origin's own log was never
        # collected) - reported honestly as the earliest entry actually
        # available, not silently treated as the root.
        leaf = _entry("studio", "c-studio-2", caused_by=("hydra-umc-server", "c-server-missing"))
        result = trace_first_failure([leaf], "c-studio-2")
        self.assertIs(result, leaf)

    def test_a_cycle_in_the_data_does_not_loop_forever(self):
        a = _entry("service-a", "c-a", caused_by=("service-b", "c-b"))
        b = _entry("service-b", "c-b", caused_by=("service-a", "c-a"))
        result = trace_first_failure([a, b], "c-a")
        self.assertIn(result, (a, b))  # malformed input - just must terminate and return something real


if __name__ == "__main__":
    unittest.main()
