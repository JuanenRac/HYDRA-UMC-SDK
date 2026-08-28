# =============================================================================
# HYDRA-UMC-SDK - External machine bridge contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import unittest

from hydra_umc_sdk.bridge_contract import BridgeError, BridgeJob, CellState, JobPhase, MachineState, evaluate_job


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
