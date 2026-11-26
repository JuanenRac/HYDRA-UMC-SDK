# =============================================================================
# HYDRA-UMC-SDK - clients/python/tests/test_signed_global_stop.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The signed announcement of the global stop, the identifiers and key of a confirmation proof, and the vectors other languages check against."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from hydra_umc_sdk.confirmation_proof import load_confirmation_key, proof_identifier, verify_confirmation_proof
from hydra_umc_sdk.global_stop import STATE_READY, STATE_SAFE_STOP, STATE_UNVERIFIED, GlobalStopGuard, GlobalStopSettings, settings_from_environment, sign_announcement
from hydra_umc_sdk.signed_commands import CommandSigningError
from hydra_umc_sdk.validation import ContractValidationError

FIXTURES = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1"
KEY = b"k" * 32
SETTINGS = GlobalStopSettings(True)


def message(state, at=None, key=KEY, topic=SETTINGS.topic):
    body = {"schema_version": "1.0", "state": state, "source": "test"}
    if at is not None:
        body = sign_announcement(topic, body, key, now_ms=at)
    return json.dumps(body).encode()


class SignedAnnouncement(unittest.TestCase):
    def guard(self):
        return GlobalStopGuard(SETTINGS, key=KEY)

    def test_a_stop_is_obeyed_signed_or_not(self):
        for payload in (message("SAFE_STOP"), message("SAFE_STOP", 5), message("SAFE_STOP", 5, key=b"x" * 32)):
            guard = self.guard()
            self.assertEqual(guard.observe(payload), STATE_SAFE_STOP)
            self.assertTrue(guard.blocks())

    def test_only_a_signed_and_newer_ready_ends_a_stop(self):
        guard = self.guard()
        guard.observe(message("SAFE_STOP", 100))
        for payload in (message("READY"), message("READY", 200, key=b"x" * 32), message("READY", 200, topic="other/safety/estop"), message("READY", 99), message("READY", 100)):
            guard.observe(payload)
            self.assertEqual(guard.state, STATE_SAFE_STOP)
        self.assertEqual(guard.observe(message("READY", 101)), STATE_READY)
        self.assertEqual(guard.observe(message("READY", 101)), STATE_READY)  # the retained message again after a reconnect

    def test_a_release_published_again_does_not_end_a_later_stop(self):
        guard = self.guard()
        old = message("READY", 100)
        guard.observe(old)
        guard.observe(message("SAFE_STOP"))
        guard.observe(old)
        self.assertEqual(guard.state, STATE_SAFE_STOP)

    def test_an_unsigned_ready_heard_first_keeps_the_bridge_still(self):
        guard = self.guard()
        self.assertEqual(guard.observe(message("READY")), STATE_UNVERIFIED)
        self.assertTrue(guard.blocks())
        self.assertIn("signed", guard.reason())

    def test_the_key_is_there_when_the_switch_is_turned_on_later(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "stop.key"
            path.write_bytes(KEY)
            os.chmod(path, 0o600)
            guard = GlobalStopGuard(GlobalStopSettings(False, ready_key_file=str(path)))
        guard.settings = GlobalStopSettings(True, ready_key_file=str(path))
        guard.observe(message("SAFE_STOP"))
        guard.observe(message("READY"))
        self.assertTrue(guard.blocks())

    def test_without_a_key_nothing_changes(self):
        guard = GlobalStopGuard(SETTINGS)
        guard.observe(message("SAFE_STOP"))
        self.assertEqual(guard.observe(message("READY")), STATE_READY)

    def test_the_key_file_of_the_environment_is_read_and_a_bad_one_stops_the_start(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "stop.key"
            path.write_bytes(KEY)
            os.chmod(path, 0o600)
            os.environ["HYDRA_UMC_T_GLOBAL_STOP_KEY_FILE"] = str(path)
            try:
                self.assertEqual(settings_from_environment("T").ready_key_file, str(path))
            finally:
                del os.environ["HYDRA_UMC_T_GLOBAL_STOP_KEY_FILE"]
            guard = GlobalStopGuard(GlobalStopSettings(True, ready_key_file=str(path)))
            self.assertEqual(guard.observe(message("READY")), STATE_UNVERIFIED)
            self.assertEqual(load_confirmation_key(str(path)), KEY)
            with self.assertRaises(CommandSigningError):
                GlobalStopGuard(GlobalStopSettings(True, ready_key_file=str(path) + ".missing"))
            with self.assertRaises(ContractValidationError):
                load_confirmation_key(str(path) + ".missing")

    def test_the_shared_vectors(self):
        data = json.loads((FIXTURES / "global-stop-signing-vectors.json").read_text(encoding="utf-8"))
        for vector in data["vectors"]:
            self.assertEqual(sign_announcement(data["topic"], vector["payload"], data["key"].encode(), now_ms=vector["issued_at_ms"]), vector["signed"])
        data = json.loads((FIXTURES / "confirmation-proof-vectors.json").read_text(encoding="utf-8"))
        for text, expected in data["identifiers"].items():
            self.assertEqual(proof_identifier(text), expected)
        for proof in data["proofs"]:
            result = verify_confirmation_proof(data["key"].encode(), proof, expected_action_id=proof["action_id"], expected_subject_id=proof["subject_id"], now_ms=1700000000500)
            self.assertEqual(result, (True, ""))


if __name__ == "__main__":
    unittest.main()
