# =============================================================================
# HYDRA-UMC-SDK - Job intake: key per source, release of a key, and the consult policy for a job in doubt
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import json
import os
import tempfile
import unittest

from hydra_umc_sdk.bridge_contract import BridgeError, BridgeJob, JobPhase, MachineState, job_to_dict
from hydra_umc_sdk.job_intake import IdempotencyStore, JobIntake, read_job_message

TOPIC = "hydra-umc/bridge/test/cmd/job"


def raw(key="key-1"):
    return json.dumps(job_to_dict(BridgeJob("job-1", key, "bridge", JobPhase.LOAD, MachineState.IDLE, {"station": "1"}))).encode()


class SourceTests(unittest.TestCase):
    def test_the_same_key_text_of_two_sources_is_two_keys(self):
        store = IdempotencyStore()
        self.assertTrue(store.claim("k", "sender-a"))
        self.assertTrue(store.claim("k", "sender-b"))
        self.assertFalse(store.claim("k", "sender-a"))
        store.remember("k", "answer-a", "sender-a")
        self.assertEqual(store.recall("k", "sender-a"), "answer-a")
        self.assertIsNone(store.recall("k", "sender-b"))

    def test_a_key_without_source_keeps_its_old_meaning(self):
        store = IdempotencyStore()
        self.assertTrue(store.claim("k"))
        self.assertFalse(store.claim("k"))
        self.assertTrue(store.claim("k", "sender-a"), "a source is a different key from the bare text")

    def test_the_stored_file_of_an_older_bridge_is_still_read(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "keys.sqlite")
            first = IdempotencyStore(path)
            first.claim("old-key")
            first.close()
            second = IdempotencyStore(path)
            self.assertFalse(second.claim("old-key"))
            second.close()

    def test_a_bad_source_is_refused(self):
        store = IdempotencyStore()
        for source in ("", "  ", "a\x1fb"):
            with self.assertRaises(BridgeError):
                store.claim("k", source)

    def test_the_intake_applies_its_source_to_every_step(self):
        store = IdempotencyStore()
        a, b = JobIntake(store, source="a"), JobIntake(store, source="b")
        self.assertTrue(a.accept(json.loads(raw())).accepted)
        self.assertTrue(b.accept(json.loads(raw())).accepted)
        self.assertTrue(a.accept(json.loads(raw())).duplicate)
        a.remember("key-1", "done")
        self.assertEqual(a.recall("key-1"), "done")
        self.assertIsNone(b.recall("key-1"))


class ReleaseTests(unittest.TestCase):
    def test_a_released_key_can_be_claimed_again(self):
        store = IdempotencyStore()
        store.claim("k")
        self.assertTrue(store.release("k"))
        self.assertTrue(store.claim("k"))

    def test_a_key_with_an_answer_cannot_be_released(self):
        store = IdempotencyStore()
        store.claim("k")
        store.remember("k", "done")
        self.assertFalse(store.release("k"))
        self.assertFalse(store.claim("k"))
        self.assertEqual(store.recall("k"), "done")

    def test_releasing_an_unknown_key_changes_nothing(self):
        store = IdempotencyStore()
        self.assertFalse(store.release("never-seen"))
        self.assertFalse(JobIntake().release("k"))

    def test_the_retry_after_a_failure_that_did_nothing_is_a_new_job(self):
        intake = JobIntake(IdempotencyStore())
        first = intake.accept(json.loads(raw()))
        self.assertTrue(first.accepted)
        self.assertTrue(intake.release("key-1"))
        self.assertTrue(intake.accept(json.loads(raw())).accepted)


class InDoubtTests(unittest.TestCase):
    def doubtful(self, **options):
        intake = JobIntake(IdempotencyStore(), **options)
        self.assertIsNotNone(read_job_message(intake, TOPIC, raw()).job)
        return intake

    def test_consult_returns_the_state_of_the_machine_and_never_runs_the_job_again(self):
        asked = []
        intake = self.doubtful(status_query=lambda job: asked.append(job.job_id) or "running on the machine")
        message = read_job_message(intake, TOPIC, raw())
        self.assertEqual(message.repeat_answer, "running on the machine")
        self.assertIsNone(message.job)
        self.assertEqual(asked, ["job-1"])
        self.assertEqual(read_job_message(intake, TOPIC, raw()).repeat_answer, "running on the machine")
        self.assertEqual(asked, ["job-1"], "the answer is stored: the machine is not asked twice")

    def test_without_a_query_or_with_the_refuse_policy_the_job_is_refused(self):
        for options in ({}, {"in_doubt_policy": "refuse", "status_query": lambda job: "x"}):
            intake = self.doubtful(**options)
            message = read_job_message(intake, TOPIC, raw())
            self.assertIsNone(message.job)
            self.assertIsNone(message.repeat_answer)
            self.assertFalse(message.refusal["allowed"])
            self.assertIn("not run again", message.refusal["reason"])

    def test_a_failing_or_empty_query_leaves_the_job_refused(self):
        def boom(job):
            raise OSError("machine unreachable")

        for query in (boom, lambda job: None, lambda job: "  ", lambda job: 7):
            message = read_job_message(self.doubtful(status_query=query), TOPIC, raw())
            self.assertIsNone(message.repeat_answer)
            self.assertFalse(message.refusal["allowed"])

    def test_there_is_no_policy_that_retries(self):
        with self.assertRaises(ValueError):
            JobIntake(in_doubt_policy="retry")
        self.assertEqual(JobIntake().in_doubt_policy, "consult")


if __name__ == "__main__":
    unittest.main()
