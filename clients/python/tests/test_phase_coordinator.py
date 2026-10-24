# =============================================================================
# HYDRA-UMC-SDK - Shared phase coordinator tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import math
import unittest

from hydra_umc_sdk.bridge_contract import BridgeJob, CellState, JobPhase, MachineState
from hydra_umc_sdk.phase_coordinator import PhaseCoordinator, PhaseDecision


def job(phase, parameters=None, machine_state=MachineState.IDLE):
    return BridgeJob("j1", "k1", "test", phase, machine_state, parameters or {})


def finite_xy(parameters):
    values = {name: float(parameters[name]) for name in ("x", "y")}
    if not all(math.isfinite(v) for v in values.values()):
        raise ValueError("WALK needs finite numeric x and y coordinates")
    return values


TABLE = {
    JobPhase.PREPARE: "WALK",
    JobPhase.LOAD: "PICK",
    JobPhase.COMPLETE: "HOME",
    JobPhase.ABORT: "HOLD",
}


def coordinator(**extra):
    return PhaseCoordinator(
        TABLE,
        safe_actions=frozenset({"HOME", "HOLD"}),
        required_parameters={"WALK": ("x", "y"), "PICK": ("object_id",)},
        validators={"WALK": finite_xy},
        extra_actions=("SIT",),
        **extra,
    )


class DecideTests(unittest.TestCase):
    def test_a_productive_phase_needs_a_ready_cell_and_an_observed_idle_machine(self):
        c = coordinator()
        ok = c.decide(job(JobPhase.PREPARE, {"x": "1", "y": "2"}), CellState.READY, MachineState.IDLE)
        self.assertTrue(ok.accepted)
        self.assertEqual(ok.action, "WALK")
        self.assertEqual(ok.parameters, {"x": 1.0, "y": 2.0})
        self.assertFalse(c.decide(job(JobPhase.PREPARE, {"x": "1", "y": "2"}), CellState.INHIBITED, MachineState.IDLE).accepted)
        self.assertFalse(c.decide(job(JobPhase.PREPARE, {"x": "1", "y": "2"}), CellState.READY, MachineState.RUNNING).accepted)

    def test_without_an_observation_the_gate_refuses_the_claim_of_the_job(self):
        decision = coordinator().decide(job(JobPhase.PREPARE, {"x": "1", "y": "2"}), CellState.READY)
        self.assertFalse(decision.accepted)
        self.assertIn("did not read", decision.reason)

    def test_a_phase_with_no_action_is_refused(self):
        decision = coordinator().decide(job(JobPhase.PROCESS), CellState.READY, MachineState.IDLE)
        self.assertFalse(decision.accepted)
        self.assertEqual(decision.action, "none")

    def test_missing_parameters_are_named(self):
        decision = coordinator().decide(job(JobPhase.PREPARE, {"x": "1"}), CellState.READY, MachineState.IDLE)
        self.assertFalse(decision.accepted)
        self.assertIn("y", decision.reason)
        self.assertIn("WALK", decision.reason)

    def test_the_validator_refuses_with_its_reason(self):
        decision = coordinator().decide(job(JobPhase.PREPARE, {"x": "nan", "y": "2"}), CellState.READY, MachineState.IDLE)
        self.assertFalse(decision.accepted)
        self.assertIn("finite", decision.reason)

    def test_a_safe_action_is_forwarded_whatever_the_gate_said(self):
        c = coordinator()
        home = c.decide(job(JobPhase.COMPLETE), CellState.INHIBITED, MachineState.RUNNING)
        self.assertTrue(home.accepted)
        self.assertIn("always forwarded", home.reason)
        # and with no observation at all
        self.assertTrue(c.decide(job(JobPhase.COMPLETE), CellState.FAULT).accepted)

    def test_an_action_that_is_not_safe_stays_refused(self):
        self.assertFalse(coordinator().decide(job(JobPhase.LOAD, {"object_id": "a"}), CellState.INHIBITED, MachineState.IDLE).accepted)

    def test_abort_is_always_forwarded_by_the_shared_gate(self):
        self.assertTrue(coordinator().decide(job(JobPhase.ABORT), CellState.SAFE_STOP, MachineState.FAULT).accepted)

    def test_safe_actions_do_not_skip_their_parameter_checks(self):
        c = PhaseCoordinator({JobPhase.COMPLETE: "HOME"}, safe_actions=frozenset({"HOME"}), required_parameters={"HOME": ("map",)})
        self.assertFalse(c.decide(job(JobPhase.COMPLETE), CellState.READY, MachineState.IDLE).accepted)

    def test_extra_parameters_are_merged_into_the_decision(self):
        decision = coordinator().decide(
            job(JobPhase.PREPARE, {"x": "1", "y": "2"}), CellState.READY, MachineState.IDLE, extra_parameters={"map_id": "m1"}
        )
        self.assertEqual(decision.parameters["map_id"], "m1")


class VocabularyTests(unittest.TestCase):
    def test_the_plan_lists_each_action_once_and_the_standalone_ones(self):
        plan = coordinator().plan()
        self.assertEqual(plan.actions, ("WALK", "PICK", "HOME", "HOLD", "SIT"))
        self.assertEqual(plan.mode, "plan-only")
        self.assertEqual(plan.to_dict()["actions"], ["WALK", "PICK", "HOME", "HOLD", "SIT"])

    def test_two_phases_with_one_action_are_listed_once(self):
        c = PhaseCoordinator({JobPhase.PREPARE: "WALK", JobPhase.PROCESS: "WALK"})
        self.assertEqual(c.vocabulary(), ("WALK",))

    def test_the_table_keys_must_be_phases(self):
        with self.assertRaises(ValueError):
            PhaseCoordinator({"PREPARE": "WALK"})  # type: ignore[dict-item]


class StandaloneTests(unittest.TestCase):
    def test_a_de_escalation_is_always_forwarded(self):
        decision = coordinator().always_forwarded("SIT", "sit requested")
        self.assertEqual(decision, PhaseDecision(True, "SIT", "sit requested - always forwarded regardless of cell/machine state"))

    def test_a_productive_standalone_request_is_gated_like_a_job(self):
        c = coordinator()
        self.assertTrue(c.gated_request("STAND", CellState.READY, MachineState.IDLE).accepted)
        refused = c.gated_request("STAND", CellState.INHIBITED, MachineState.IDLE)
        self.assertFalse(refused.accepted)
        self.assertEqual(refused.action, "STAND")
        self.assertFalse(c.gated_request("STAND", CellState.READY, MachineState.RUNNING).accepted)


if __name__ == "__main__":
    unittest.main()
