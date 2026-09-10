# =============================================================================
# HYDRA-UMC-SDK - External machine bridge contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import unittest

from hydra_umc_sdk.bridge_contract import (
    BridgeError,
    BridgeJob,
    CellState,
    GateDecision,
    JobPhase,
    MachineState,
    decision_to_dict,
    evaluate_job,
    job_from_dict,
    job_to_dict,
)


def job(phase=JobPhase.LOAD, machine_state=MachineState.IDLE):
    return BridgeJob("job-1", "unique-1", "HYDRA-UMC-BRIDGE-OPENPNP", phase, machine_state, {"station": "pnp-1"})


class BridgeContractTests(unittest.TestCase):
    def test_ready_cell_and_idle_machine_permit_productive_phase(self):
        self.assertTrue(evaluate_job(job(), CellState.READY).allowed)

    def test_busy_machine_is_not_reused(self):
        decision = evaluate_job(job(machine_state=MachineState.RUNNING), CellState.READY)
        self.assertFalse(decision.allowed)
        self.assertIn("RUNNING", decision.reason)

    def test_safe_stop_cell_blocks_productive_phase(self):
        self.assertFalse(evaluate_job(job(), CellState.SAFE_STOP).allowed)

    def test_abort_remains_available_from_a_faulted_cell(self):
        self.assertTrue(evaluate_job(job(phase=JobPhase.ABORT, machine_state=MachineState.FAULT), CellState.FAULT).allowed)

    def test_invalid_identifiers_are_rejected(self):
        with self.assertRaises(BridgeError):
            BridgeJob("", "key", "bridge", JobPhase.LOAD, MachineState.IDLE, {})

    # SDK-01 (P1): the finding's own exact reproduction - constructing BridgeJob
    # DIRECTLY (not through job_from_dict, which already validated this)
    # with an unrecognised phase used to succeed, and
    # evaluate_job(job, CellState.READY) could then return allowed=True
    # for a phase it never actually recognised - `job.phase is
    # JobPhase.ABORT` is simply False for a garbage value, falling
    # through to the same "ready" path a real, known phase would take.
    def test_constructor_rejects_an_unrecognised_phase_string(self):
        with self.assertRaises(BridgeError):
            BridgeJob("job-1", "key-1", "bridge", "TELEPORT", MachineState.IDLE, {})  # type: ignore[arg-type]

    def test_constructor_rejects_an_unrecognised_machine_state_string(self):
        with self.assertRaises(BridgeError):
            BridgeJob("job-1", "key-1", "bridge", JobPhase.LOAD, "QUANTUM", {})  # type: ignore[arg-type]

    # REV-009 (P2): same
    # class of gap as SDK-01 above, on `parameters` instead of
    # `phase`/`machine_state`. `job_from_dict()` already guarded this
    # before ever constructing a BridgeJob, but the direct public
    # constructor didn't - passing a list here used to raise a bare
    # AttributeError ('list' object has no attribute 'items') out of
    # __post_init__ instead of the intended BridgeError every other
    # invalid-shape input on this same constructor raises.
    def test_constructor_rejects_non_mapping_parameters_instead_of_crashing(self):
        with self.assertRaises(BridgeError):
            BridgeJob("job-1", "key-1", "bridge", JobPhase.LOAD, MachineState.IDLE, [])  # type: ignore[arg-type]

    def test_constructor_still_rejects_non_string_parameter_values_in_a_real_mapping(self):
        with self.assertRaises(BridgeError):
            BridgeJob("job-1", "key-1", "bridge", JobPhase.LOAD, MachineState.IDLE, {"count": 3})  # type: ignore[arg-type]


class JobSerializationTests(unittest.TestCase):
    """job_to_dict()/job_from_dict() - the real wire shape a bridge now
    publishes/consumes over HYDRA-UMC-MQTT-BROKER, so this round-trip must
    be exact, and malformed input must fail closed (BridgeError), never a
    bare KeyError/ValueError/AttributeError escaping into a bridge's own
    MQTT message handler."""

    def test_round_trips_a_real_job(self):
        original = job()
        restored = job_from_dict(job_to_dict(original))
        self.assertEqual(original, restored)

    def test_to_dict_uses_plain_json_compatible_values(self):
        payload = job_to_dict(job())
        self.assertEqual(payload["phase"], "LOAD")
        self.assertEqual(payload["machine_state"], "IDLE")
        self.assertIsInstance(payload["parameters"], dict)

    def test_from_dict_rejects_a_non_mapping(self):
        with self.assertRaises(BridgeError):
            job_from_dict("not-a-mapping")  # type: ignore[arg-type]

    def test_from_dict_rejects_a_missing_field(self):
        payload = job_to_dict(job())
        del payload["idempotency_key"]
        with self.assertRaises(BridgeError):
            job_from_dict(payload)

    def test_from_dict_rejects_an_unrecognised_phase(self):
        payload = job_to_dict(job())
        payload["phase"] = "TELEPORT"
        with self.assertRaises(BridgeError):
            job_from_dict(payload)

    def test_from_dict_rejects_an_unrecognised_machine_state(self):
        payload = job_to_dict(job())
        payload["machine_state"] = "QUANTUM"
        with self.assertRaises(BridgeError):
            job_from_dict(payload)

    def test_from_dict_rejects_non_string_parameters(self):
        payload = job_to_dict(job())
        payload["parameters"] = {"count": 3}
        with self.assertRaises(BridgeError):
            job_from_dict(payload)

    def test_decision_to_dict_shape(self):
        self.assertEqual(decision_to_dict(GateDecision(True, "ok")), {"allowed": True, "reason": "ok"})
