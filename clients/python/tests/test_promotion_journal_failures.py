# =============================================================================
# HYDRA-UMC-SDK - promotion journal failure-path tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from hydra_umc_sdk import promotion_journal
from hydra_umc_sdk.promotion_journal import PromotionJournal, PromotionPhase, check_service_health


class AtomicWriteFailureTests(unittest.TestCase):
    def test_a_failed_write_keeps_the_old_journal_and_leaves_no_temporary_file(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            journal = PromotionJournal(path)
            record = journal.begin("demo", Path("/a/t"), Path("/a/s"), Path("/a/b"))
            before = path.read_bytes()
            with mock.patch.object(promotion_journal.os, "replace", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    journal.advance(record.promotion_id, PromotionPhase.BACKED_UP)
            self.assertEqual(path.read_bytes(), before, "the previous complete journal is untouched")
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["journal.json"])
            self.assertEqual(PromotionJournal(path).pending()[0].phase, PromotionPhase.STARTED)

    def test_the_journal_is_written_to_disk_before_the_rename_makes_it_current(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            calls = []
            real_fsync = os.fsync
            real_replace = os.replace

            def fsync(fd):
                calls.append("fsync")
                return real_fsync(fd)

            def replace(src, dst):
                calls.append("replace")
                return real_replace(src, dst)

            with mock.patch.object(promotion_journal.os, "fsync", fsync), mock.patch.object(promotion_journal.os, "replace", replace):
                PromotionJournal(path).begin("demo", Path("/a/t"), Path("/a/s"), Path("/a/b"))
            self.assertLess(calls.index("fsync"), calls.index("replace"))

    def test_the_journal_directory_is_created_when_it_does_not_exist(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "a" / "b" / "journal.json"
            PromotionJournal(path).begin("demo", Path("/a/t"), Path("/a/s"), Path("/a/b"))
            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema_version"], "1.0")


class PreserveFailureTests(unittest.TestCase):
    def test_a_corrupt_journal_that_cannot_be_moved_still_loads_as_empty(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            path.write_text("{not json", encoding="utf-8")
            journal = PromotionJournal(path)
            with mock.patch.object(promotion_journal.os, "replace", side_effect=OSError("read-only")):
                self.assertEqual(journal.pending(), [])
            self.assertEqual(journal.preserved_files, [])

    def test_a_journal_with_a_binary_body_is_set_aside(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            path.write_bytes(b"\xff\xfe\x00garbage")
            journal = PromotionJournal(path)
            self.assertEqual(journal.pending(), [])
            self.assertEqual(len(journal.preserved_files), 1)
            self.assertTrue(journal.preserved_files[0].exists())

    def test_a_promotions_section_that_is_not_an_object_is_set_aside(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            path.write_text(json.dumps({"schema_version": "1.0", "promotions": ["x"]}), encoding="utf-8")
            journal = PromotionJournal(path)
            self.assertEqual(journal.pending(), [])
            self.assertEqual(len(journal.preserved_files), 1)


class HealthCheckFailureTests(unittest.TestCase):
    def test_an_unexpected_error_is_reported_never_raised(self):
        with mock.patch.object(promotion_journal.urllib.request, "urlopen", side_effect=RuntimeError("boom")):
            self.assertEqual(check_service_health("http://127.0.0.1:1/health"), (False, "boom"))

    def test_an_error_without_a_message_is_named_by_its_type(self):
        with mock.patch.object(promotion_journal.urllib.request, "urlopen", side_effect=ValueError()):
            self.assertEqual(check_service_health("http://127.0.0.1:1/health"), (False, "ValueError"))

    def test_other_schemes_are_refused_before_any_connection(self):
        for url in ("file:///etc/passwd", "ftp://example.com/x", "javascript:alert(1)", ""):
            with mock.patch.object(promotion_journal.urllib.request, "urlopen") as urlopen:
                healthy, reason = check_service_health(url)
                urlopen.assert_not_called()
            self.assertFalse(healthy)
            self.assertIn("http", reason)


if __name__ == "__main__":
    unittest.main()
