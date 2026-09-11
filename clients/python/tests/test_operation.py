# =============================================================================
# HYDRA-UMC-SDK - P03 Operation lifecycle tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import unittest

from hydra_umc_sdk.operation import (
    OPERATION_STATUSES,
    OperationRecord,
    TERMINAL_STATUSES,
    is_terminal,
    validate_status_transition,
)
from hydra_umc_sdk.validation import ContractValidationError


def _operation(**over):
    payload = {
        "schema_version": "1.0",
        "operation_id": "op-1",
        "correlation_id": "mission-1",
        "kind": "move_to_pose",
        "target": {"kind": "robot", "id": "controller-1:robot-1"},
        "status": "received",
        "requested_at_utc": "2026-01-02T08:00:00Z",
        "updated_at_utc": "2026-01-02T08:00:00Z",
        "params": {},
    }
    payload.update(over)
    return payload


class OperationLifecycleTests(unittest.TestCase):
    def test_the_full_forward_path_is_legal_step_by_step(self):
        path = ["received", "authorized", "queued", "sent", "confirmed", "terminated"]
        for previous, next_status in zip(path, path[1:]):
            self.assertTrue(validate_status_transition(previous, next_status), f"{previous} -> {next_status}")

    def test_rejected_is_reachable_from_every_non_terminal_status(self):
        for status in OPERATION_STATUSES:
            if status in TERMINAL_STATUSES:
                continue
            self.assertTrue(validate_status_transition(status, "rejected"), status)

    def test_nothing_is_reachable_from_a_terminal_status(self):
        for terminal in TERMINAL_STATUSES:
            for candidate in OPERATION_STATUSES:
                self.assertFalse(validate_status_transition(terminal, candidate), f"{terminal} -> {candidate}")

    def test_skipping_a_stage_is_illegal(self):
        # received -> sent skips authorized and queued entirely - exactly
        # the kind of silent collapse P03 exists to prevent.
        self.assertFalse(validate_status_transition("received", "sent"))
        self.assertFalse(validate_status_transition("queued", "confirmed"))

    def test_going_backwards_is_illegal(self):
        self.assertFalse(validate_status_transition("queued", "authorized"))
        self.assertFalse(validate_status_transition("confirmed", "sent"))

    def test_an_unrecognised_status_on_either_side_returns_false_not_raises(self):
        self.assertFalse(validate_status_transition("received", "executed"))
        self.assertFalse(validate_status_transition("executed", "received"))

    def test_is_terminal(self):
        self.assertTrue(is_terminal("terminated"))
        self.assertTrue(is_terminal("rejected"))
        self.assertFalse(is_terminal("queued"))
        self.assertFalse(is_terminal("unknown-status"))


class OperationRecordTests(unittest.TestCase):
    def test_from_payload_reads_the_real_fields(self):
        record = OperationRecord.from_payload(_operation(status="sent"))
        self.assertEqual(record.operation_id, "op-1")
        self.assertEqual(record.correlation_id, "mission-1")
        self.assertEqual(record.kind, "move_to_pose")
        self.assertEqual(record.status, "sent")
        self.assertEqual(record.target_kind, "robot")
        self.assertEqual(record.target_id, "controller-1:robot-1")
        self.assertFalse(record.is_terminal)

    def test_is_terminal_property_reflects_status(self):
        record = OperationRecord.from_payload(_operation(status="terminated"))
        self.assertTrue(record.is_terminal)

    def test_from_payload_rejects_a_malformed_payload(self):
        with self.assertRaises(ContractValidationError):
            OperationRecord.from_payload(_operation(status="executed"))

    def test_from_payload_rejects_a_target_missing_id(self):
        with self.assertRaises(ContractValidationError):
            OperationRecord.from_payload(_operation(target={"kind": "robot"}))


if __name__ == "__main__":
    unittest.main()
