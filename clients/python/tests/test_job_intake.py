# =============================================================================
# HYDRA-UMC-SDK - Job intake tests (idempotency store, retained-message guard, observed machine state)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import os
import tempfile
import threading
import unittest

from hydra_umc_sdk.bridge_contract import (
    BridgeError,
    BridgeJob,
    CellState,
    JobPhase,
    MachineState,
    evaluate_job,
    job_to_dict,
)
from hydra_umc_sdk.job_intake import IdempotencyStore, JobIntake


def payload(key="key-1", **overrides):
    value = job_to_dict(BridgeJob("job-1", key, "bridge", JobPhase.LOAD, MachineState.IDLE, {"station": "1"}))
    value.update(overrides)
    return value


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


class ObservedStateTests(unittest.TestCase):
    def job(self, claimed):
        return BridgeJob("job-1", "key-1", "bridge", JobPhase.LOAD, claimed, {})

    def test_the_observed_state_beats_the_claimed_one(self):
        # the requester claims IDLE, the bridge sees the machine running: refused
        decision = evaluate_job(self.job(MachineState.IDLE), CellState.READY, MachineState.RUNNING)
        self.assertFalse(decision.allowed)
        self.assertIn("RUNNING", decision.reason)

    def test_an_observed_idle_machine_is_allowed_whatever_is_claimed(self):
        self.assertTrue(evaluate_job(self.job(MachineState.FAULT), CellState.READY, MachineState.IDLE).allowed)

    def test_without_an_observation_the_claim_is_still_used(self):
        self.assertFalse(evaluate_job(self.job(MachineState.RUNNING), CellState.READY).allowed)
        self.assertTrue(evaluate_job(self.job(MachineState.IDLE), CellState.READY, allow_unobserved=True).allowed)

    def test_an_observation_that_is_not_a_state_is_an_error(self):
        with self.assertRaises(BridgeError):
            evaluate_job(self.job(MachineState.IDLE), CellState.READY, "IDLE")  # type: ignore[arg-type]

    def test_abort_ignores_both(self):
        job = BridgeJob("job-1", "key-1", "bridge", JobPhase.ABORT, MachineState.FAULT, {})
        self.assertTrue(evaluate_job(job, CellState.FAULT, MachineState.FAULT).allowed)


class JobSizeTests(unittest.TestCase):
    def test_a_job_with_too_many_or_too_long_parameters_is_refused(self):
        with self.assertRaises(BridgeError):
            BridgeJob("j", "k", "s", JobPhase.LOAD, MachineState.IDLE, {str(i): "x" for i in range(33)})
        with self.assertRaises(BridgeError):
            BridgeJob("j", "k", "s", JobPhase.LOAD, MachineState.IDLE, {"a": "x" * 1025})
        with self.assertRaises(BridgeError):
            BridgeJob("j", "k", "s", JobPhase.LOAD, MachineState.IDLE, {"a" * 65: "x"})
        with self.assertRaises(BridgeError):
            BridgeJob("j" * 129, "k", "s", JobPhase.LOAD, MachineState.IDLE, {})

    def test_the_limits_themselves_are_allowed(self):
        BridgeJob("j" * 128, "k", "s", JobPhase.LOAD, MachineState.IDLE, {("a" * 64) + str(i)[:0]: "x" * 1024 for i in range(1)})
        BridgeJob("j", "k", "s", JobPhase.LOAD, MachineState.IDLE, {str(i): "x" for i in range(32)})


class IdempotencyStoreTests(unittest.TestCase):
    def test_the_first_claim_wins_and_a_repeat_loses(self):
        store = IdempotencyStore()
        self.assertTrue(store.claim("a"))
        self.assertFalse(store.claim("a"))
        self.assertTrue(store.claim("b"))
        self.assertEqual(len(store), 2)

    def test_a_blank_key_is_an_error(self):
        with self.assertRaises(BridgeError):
            IdempotencyStore().claim("  ")

    def test_a_key_is_forgotten_after_the_ttl(self):
        clock = Clock()
        store = IdempotencyStore(ttl_seconds=60, clock=clock)
        self.assertTrue(store.claim("a"))
        clock.now += 59
        self.assertFalse(store.claim("a"))
        clock.now += 2
        self.assertTrue(store.claim("a"))

    def test_the_oldest_keys_make_room_when_the_store_is_full(self):
        clock = Clock()
        store = IdempotencyStore(max_entries=3, clock=clock)
        for index in range(5):
            clock.now += 1
            self.assertTrue(store.claim(f"k{index}"))
        self.assertLessEqual(len(store), 3)
        self.assertFalse(store.claim("k4"))   # the newest is still remembered

    def test_the_answer_given_to_a_key_can_be_recalled(self):
        store = IdempotencyStore()
        store.claim("a")
        self.assertIsNone(store.recall("a"))
        store.remember("a", "refused: cell is FAULT")
        self.assertEqual(store.recall("a"), "refused: cell is FAULT")
        self.assertIsNone(store.recall("never-seen"))

    def test_a_file_store_survives_a_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "keys.sqlite")
            first = IdempotencyStore(path)
            self.assertTrue(first.claim("a"))
            first.remember("a", "done")
            first.close()
            second = IdempotencyStore(path)
            self.assertFalse(second.claim("a"))
            self.assertEqual(second.recall("a"), "done")
            second.close()

    def test_two_threads_cannot_both_claim_a_key(self):
        store = IdempotencyStore()
        wins = []

        def worker():
            wins.append(store.claim("same"))

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(wins.count(True), 1)


class JobIntakeTests(unittest.TestCase):
    def test_a_good_job_is_accepted_once(self):
        intake = JobIntake(IdempotencyStore())
        first = intake.accept(payload())
        self.assertTrue(first.accepted)
        self.assertEqual(first.job.job_id, "job-1")
        second = intake.accept(payload())
        self.assertFalse(second.accepted)
        self.assertTrue(second.duplicate)
        self.assertEqual(second.job.idempotency_key, "key-1")

    def test_a_duplicate_without_a_stored_answer_is_marked_in_doubt(self):
        store = IdempotencyStore()
        intake = JobIntake(store)
        self.assertTrue(intake.accept(payload()).accepted)
        again = intake.accept(payload())
        self.assertTrue(again.duplicate)
        self.assertTrue(again.in_doubt)
        store.remember("key-1", "done")
        answered = intake.accept(payload())
        self.assertTrue(answered.duplicate)
        self.assertFalse(answered.in_doubt)

    def test_a_retained_message_is_ignored_and_does_not_use_up_its_key(self):
        store = IdempotencyStore()
        intake = JobIntake(store)
        replay = intake.accept(payload(), retained=True)
        self.assertFalse(replay.accepted)
        self.assertTrue(replay.retained)
        self.assertEqual(len(store), 0)
        self.assertTrue(intake.accept(payload()).accepted)

    def test_a_malformed_job_is_refused_with_the_reason(self):
        intake = JobIntake(IdempotencyStore())
        for bad in ({}, {"job_id": "x"}, payload(phase="NOPE"), payload(parameters=[]), "not a mapping"):
            result = intake.accept(bad)  # type: ignore[arg-type]
            self.assertFalse(result.accepted)
            self.assertIn("malformed", result.reason)

    def test_without_a_store_only_retained_and_malformed_are_stopped(self):
        intake = JobIntake()
        self.assertTrue(intake.accept(payload()).accepted)
        self.assertTrue(intake.accept(payload()).accepted)
        self.assertFalse(intake.accept(payload(), retained=True).accepted)


if __name__ == "__main__":
    unittest.main()
