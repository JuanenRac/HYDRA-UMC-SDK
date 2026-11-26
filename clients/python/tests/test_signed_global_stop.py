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
from unittest import mock

from hydra_umc_sdk.confirmation_proof import load_confirmation_key, proof_identifier, verify_confirmation_proof
from hydra_umc_sdk.global_stop import (STATE_READY, STATE_SAFE_STOP, STATE_UNVERIFIED, GlobalStopGuard, GlobalStopSettings, default_state_file,
                                       settings_from_environment, sign_announcement)
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


class ReadyMark(unittest.TestCase):
    """The mark on disk: an old signed READY stays old after a restart, and anything doubtful leaves the machine still."""

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.path = self.folder / "state" / "mark.json"

    def guard(self, path=None, key=KEY, topic=SETTINGS.topic):
        return GlobalStopGuard(GlobalStopSettings(True, topic, ready_state_file=str(path or self.path)), key=key)

    def test_an_old_release_is_refused_after_a_restart_and_the_current_one_is_accepted(self):
        first = self.guard()
        first.observe(message("READY", 100))
        first.observe(message("SAFE_STOP", 150))
        first.observe(message("READY", 200))
        second = self.guard()
        second.observe(message("READY", 100))
        self.assertTrue(second.blocks())
        self.assertEqual(second.observe(message("READY", 200)), STATE_READY)  # the retained message that was in force
        self.assertFalse(second.blocks())

    def test_a_bridge_that_was_stopped_starts_stopped(self):
        first = self.guard()
        first.observe(message("READY", 100))
        first.observe(message("SAFE_STOP"))  # unsigned: still remembered
        second = self.guard()
        self.assertTrue(second.blocks())
        second.observe(message("READY", 100))
        self.assertTrue(second.blocks())
        self.assertEqual(second.observe(message("READY", 101)), STATE_READY)

    def test_a_stop_heard_after_a_restart_cancels_the_restored_release(self):
        self.guard().observe(message("READY", 100))
        second = self.guard()
        second.observe(message("SAFE_STOP"))
        second.observe(message("READY", 100))
        self.assertEqual(second.state, STATE_SAFE_STOP)

    def test_a_damaged_altered_or_foreign_mark_keeps_everything_still(self):
        self.guard().observe(message("READY", 100))
        good = self.path.read_bytes()
        for content in (b"", b"not json", good[:-10], good.replace(b"100", b"1"), b"[1]"):
            self.path.write_bytes(content)
            guard = self.guard()
            self.assertTrue(guard.blocks(), content)
            guard.observe(message("READY", 500))
            self.assertTrue(guard.blocks(), content)
            self.assertIn("removes the file", guard.reason())
            self.assertEqual(self.path.read_bytes(), content)  # left for the operator to look at
        self.path.write_bytes(good)
        self.assertTrue(self.guard(topic="other/safety/estop").blocks())
        self.assertTrue(self.guard(key=b"x" * 32).blocks())
        self.path.unlink()
        self.assertFalse(self.guard().blocks())  # no file: a first start

    def test_a_release_that_cannot_be_written_is_not_believed(self):
        guard = self.guard()
        # the write itself fails (a full or read-only disk), the same way on every system
        with mock.patch("tempfile.mkstemp", side_effect=PermissionError("read only")):
            guard.observe(message("READY", 100))
            self.assertTrue(guard.blocks())
            self.assertIn("could not be remembered", guard.reason())
            guard.observe(message("SAFE_STOP", 101))
            self.assertEqual(guard.state, STATE_SAFE_STOP)

    def test_a_mark_that_cannot_be_read_keeps_everything_still(self):
        self.path.mkdir(parents=True)  # a folder where the file should be
        guard = self.guard()
        guard.observe(message("READY", 100))
        self.assertTrue(guard.blocks())
        self.assertIn("cannot be read", guard.reason())

    def test_writing_leaves_no_temporary_file(self):
        guard = self.guard()
        for at in (1, 2, 3):
            guard.observe(message("READY", at))
        self.assertEqual([p.name for p in self.path.parent.iterdir()], ["mark.json"])

    def test_a_key_file_gives_a_default_mark_in_the_state_folder_and_the_environment_names_one(self):
        key_file = self.folder / "stop.key"
        key_file.write_bytes(KEY)
        os.chmod(key_file, 0o600)
        settings = GlobalStopSettings(True, ready_key_file=str(key_file))
        with mock.patch.dict(os.environ, {"STATE_DIRECTORY": str(self.folder / "service")}):
            default = default_state_file(settings.topic, str(key_file))
            GlobalStopGuard(settings).observe(message("READY", 100))
        self.assertEqual(Path(default).parent, self.folder / "service")
        self.assertTrue(Path(default).is_file())
        with mock.patch.dict(os.environ, {"HYDRA_UMC_T_GLOBAL_STOP_STATE_FILE": str(self.path)}):
            self.assertEqual(settings_from_environment("T").ready_state_file, str(self.path))

    def test_without_a_key_nothing_is_written(self):
        guard = GlobalStopGuard(GlobalStopSettings(True, ready_state_file=str(self.path)))
        guard.observe(message("READY"))
        self.assertFalse(self.path.exists())


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
