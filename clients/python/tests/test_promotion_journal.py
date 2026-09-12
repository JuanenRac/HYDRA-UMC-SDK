# =============================================================================
# HYDRA-UMC-SDK - P01 promotion journal tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from hydra_umc_sdk.promotion_journal import PromotionJournal, PromotionPhase, check_service_health, recover


class PromotionJournalBasicsTests(unittest.TestCase):
    def test_begin_creates_a_started_record(self):
        with TemporaryDirectory() as tmp:
            journal = PromotionJournal(Path(tmp) / "journal.json")
            record = journal.begin("demo", Path("/a/target"), Path("/a/staging"), Path("/a/backup"))
            self.assertEqual(record.phase, PromotionPhase.STARTED)
            self.assertEqual(record.project, "demo")

    def test_journal_survives_a_fresh_read_from_disk(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            journal = PromotionJournal(path)
            record = journal.begin("demo", Path("/a/target"), Path("/a/staging"), Path("/a/backup"))
            reloaded = PromotionJournal(path)
            pending = reloaded.pending()
            self.assertEqual(len(pending), 1)
            self.assertEqual(pending[0].promotion_id, record.promotion_id)

    def test_advance_updates_phase_and_persists(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            journal = PromotionJournal(path)
            record = journal.begin("demo", Path("/a/target"), Path("/a/staging"), Path("/a/backup"))
            journal.advance(record.promotion_id, PromotionPhase.BACKED_UP)
            self.assertEqual(PromotionJournal(path).pending()[0].phase, PromotionPhase.BACKED_UP)

    def test_advance_on_an_unknown_id_raises(self):
        with TemporaryDirectory() as tmp:
            journal = PromotionJournal(Path(tmp) / "journal.json")
            with self.assertRaises(KeyError):
                journal.advance("does-not-exist", PromotionPhase.PROMOTED)

    def test_complete_removes_the_record_from_pending(self):
        with TemporaryDirectory() as tmp:
            journal = PromotionJournal(Path(tmp) / "journal.json")
            record = journal.begin("demo", Path("/a/target"), Path("/a/staging"), Path("/a/backup"))
            journal.complete(record.promotion_id)
            self.assertEqual(journal.pending(), [])

    def test_pending_is_empty_when_no_journal_file_exists_yet(self):
        with TemporaryDirectory() as tmp:
            journal = PromotionJournal(Path(tmp) / "does-not-exist.json")
            self.assertEqual(journal.pending(), [])

    def test_a_corrupt_journal_file_is_treated_as_empty_not_a_crash(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            path.write_text("{not valid json", encoding="utf-8")
            journal = PromotionJournal(path)
            self.assertEqual(journal.pending(), [])

    def test_multiple_pending_promotions_are_sorted_by_start_time(self):
        with TemporaryDirectory() as tmp:
            journal = PromotionJournal(Path(tmp) / "journal.json")
            first = journal.begin("a", Path("/a"), Path("/a-s"), Path("/a-b"))
            second = journal.begin("b", Path("/b"), Path("/b-s"), Path("/b-b"))
            ids = [r.promotion_id for r in journal.pending()]
            self.assertEqual(ids, [first.promotion_id, second.promotion_id])


class RecoverTests(unittest.TestCase):
    def test_recovers_a_backed_up_promotion_by_restoring_the_backup(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            backup = root / "project.backup"
            backup.mkdir()
            (backup / "marker.txt").write_text("old install", encoding="utf-8")
            target = root / "project"  # does not exist - the crash happened after the first rename

            journal = PromotionJournal(root / "journal.json")
            record = journal.begin("demo", target, root / "project.staging", backup)
            journal.advance(record.promotion_id, PromotionPhase.BACKED_UP)

            actions = recover(journal)

            self.assertTrue(target.exists())
            self.assertFalse(backup.exists())
            self.assertEqual((target / "marker.txt").read_text(encoding="utf-8"), "old install")
            self.assertEqual(journal.pending(), [])
            self.assertIn("restored", actions[0])

    def test_a_promoted_promotion_needs_no_filesystem_action(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            target.mkdir()

            journal = PromotionJournal(root / "journal.json")
            record = journal.begin("demo", target, root / "project.staging", root / "project.backup")
            journal.advance(record.promotion_id, PromotionPhase.PROMOTED)

            actions = recover(journal)

            self.assertTrue(target.exists())
            self.assertEqual(journal.pending(), [])
            self.assertIn("nothing to recover", actions[0])

    def test_a_started_promotion_is_pruned_with_no_filesystem_action(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            journal = PromotionJournal(root / "journal.json")
            journal.begin("demo", root / "target", root / "staging", root / "backup")

            actions = recover(journal)

            self.assertEqual(journal.pending(), [])
            self.assertIn("stale record complete", actions[0])

    def test_backed_up_with_target_already_restored_by_something_else_is_left_alone(self):
        # A real, if unusual, case: an operator manually restored the
        # backup by hand before this recovery ever ran. Must not
        # overwrite whatever is now at target_path.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            target.mkdir()
            (target / "manually-restored.txt").write_text("operator did this", encoding="utf-8")
            backup = root / "project.backup"
            backup.mkdir()

            journal = PromotionJournal(root / "journal.json")
            record = journal.begin("demo", target, root / "project.staging", backup)
            journal.advance(record.promotion_id, PromotionPhase.BACKED_UP)

            recover(journal)

            self.assertTrue((target / "manually-restored.txt").exists())
            self.assertTrue(backup.exists())  # untouched - never deleted out from under an operator

    def test_backed_up_with_neither_target_nor_backup_present_is_left_pending_for_a_human(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            journal = PromotionJournal(root / "journal.json")
            record = journal.begin("demo", root / "target", root / "staging", root / "backup")
            journal.advance(record.promotion_id, PromotionPhase.BACKED_UP)

            actions = recover(journal)

            self.assertEqual(len(journal.pending()), 1, "an unrecoverable case must not be silently pruned")
            self.assertIn("nothing this journal can recover", actions[0])

    def test_recover_with_nothing_pending_returns_an_empty_list(self):
        with TemporaryDirectory() as tmp:
            journal = PromotionJournal(Path(tmp) / "journal.json")
            self.assertEqual(recover(journal), [])

    def test_a_promoted_promotion_with_no_health_check_url_needs_no_action(self):
        # Same real case as test_a_promoted_promotion_needs_no_filesystem_action
        # above, made explicit for a project that declares no health
        # endpoint at all (health_check_url=None) - must behave exactly
        # as it always did, not silently start requiring one.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            target.mkdir()
            journal = PromotionJournal(root / "journal.json")
            record = journal.begin("demo", target, root / "project.staging", root / "project.backup")
            journal.advance(record.promotion_id, PromotionPhase.PROMOTED)

            actions = recover(journal)

            self.assertEqual(journal.pending(), [])
            self.assertIn("nothing to recover", actions[0])

    def test_i13_a_promoted_promotion_with_a_passing_health_check_completes(self):
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer

        class _Handler(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                self.send_response(200)
                self.end_headers()

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), _Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            port = server.server_address[1]
            with TemporaryDirectory() as tmp:
                root = Path(tmp)
                target = root / "project"
                target.mkdir()
                journal = PromotionJournal(root / "journal.json")
                record = journal.begin(
                    "demo", target, root / "project.staging", root / "project.backup",
                    health_check_url=f"http://127.0.0.1:{port}/health",
                )
                journal.advance(record.promotion_id, PromotionPhase.PROMOTED)

                actions = recover(journal)

                self.assertEqual(journal.pending(), [], "a passing health check must complete the promotion, not leave it pending forever")
                self.assertIn("now passes", actions[0])
        finally:
            server.shutdown()
            thread.join(timeout=5)

    def test_i13_a_promoted_promotion_with_a_failing_health_check_stays_pending(self):
        # I13's own real acceptance test: cut the process after PROMOTED
        # and before the health check ever ran (simulated here by simply
        # never having a real server listening) - recovery must run the
        # real pending check, find it failing, and refuse to announce
        # success by leaving the record pending rather than completing it.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            target.mkdir()
            journal = PromotionJournal(root / "journal.json")
            # A real, guaranteed-closed local port - nothing is listening.
            import socket as _socket
            probe = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
            probe.bind(("127.0.0.1", 0))
            closed_port = probe.getsockname()[1]
            probe.close()

            record = journal.begin(
                "demo", target, root / "project.staging", root / "project.backup",
                health_check_url=f"http://127.0.0.1:{closed_port}/health",
            )
            journal.advance(record.promotion_id, PromotionPhase.PROMOTED)

            actions = recover(journal)

            self.assertEqual(len(journal.pending()), 1, "a failing health check must never be silently completed")
            self.assertIn("still fails", actions[0])

    def test_health_check_url_survives_advance_across_phases(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            journal = PromotionJournal(root / "journal.json")
            record = journal.begin(
                "demo", root / "target", root / "staging", root / "backup",
                health_check_url="http://127.0.0.1:9/health",
            )
            journal.advance(record.promotion_id, PromotionPhase.BACKED_UP)
            journal.advance(record.promotion_id, PromotionPhase.PROMOTED)
            reloaded = PromotionJournal(root / "journal.json").pending()[0]
            self.assertEqual(reloaded.health_check_url, "http://127.0.0.1:9/health")

    def test_a_journal_file_written_before_health_check_url_existed_still_loads(self):
        # Real backward compatibility: an old journal entry on disk simply
        # has no "health_check_url" key at all - from_dict() must default
        # it to None, never KeyError.
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            old_shaped_payload = {
                "schema_version": "1.0",
                "promotions": {
                    "abc123": {
                        "promotion_id": "abc123", "project": "demo",
                        "target_path": "/a", "staging_path": "/a-s", "backup_path": "/a-b",
                        "phase": "promoted", "started_at_utc": "2020-01-01T00:00:00Z",
                        "updated_at_utc": "2020-01-01T00:00:00Z",
                        # no health_check_url key - matches a real pre-I13 journal
                    }
                },
            }
            path.write_text(json.dumps(old_shaped_payload), encoding="utf-8")
            journal = PromotionJournal(path)
            pending = journal.pending()
            self.assertEqual(len(pending), 1)
            self.assertIsNone(pending[0].health_check_url)


class CheckServiceHealthTests(unittest.TestCase):
    def test_a_real_2xx_response_is_healthy(self):
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer

        class _Handler(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                self.send_response(200)
                self.end_headers()

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), _Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            port = server.server_address[1]
            healthy, reason = check_service_health(f"http://127.0.0.1:{port}/health")
            self.assertTrue(healthy)
            self.assertEqual(reason, "HTTP 200")
        finally:
            server.shutdown()
            thread.join(timeout=5)

    def test_a_real_500_response_is_not_healthy(self):
        # The key real difference from a bare reachability probe: the
        # endpoint DID answer, but a 5xx means the freshly-promoted
        # service itself is not well - this must not be waved through.
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer

        class _Handler(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                self.send_response(500)
                self.end_headers()

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), _Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            port = server.server_address[1]
            healthy, reason = check_service_health(f"http://127.0.0.1:{port}/health")
            self.assertFalse(healthy)
            self.assertEqual(reason, "HTTP 500")
        finally:
            server.shutdown()
            thread.join(timeout=5)

    def test_a_real_closed_port_is_not_healthy(self):
        import socket

        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe.bind(("127.0.0.1", 0))
        closed_port = probe.getsockname()[1]
        probe.close()

        healthy, reason = check_service_health(f"http://127.0.0.1:{closed_port}/health", timeout=1.0)

        self.assertFalse(healthy)
        self.assertTrue(reason)  # some real, non-empty reason - never silently empty


class AtomicWriteTests(unittest.TestCase):
    def test_journal_file_is_valid_json_after_every_write(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            journal = PromotionJournal(path)
            journal.begin("demo", Path("/a"), Path("/a-s"), Path("/a-b"))
            # Read the raw file directly (not through PromotionJournal) -
            # proves _atomic_write_json() never leaves a torn/partial file.
            json.loads(path.read_text(encoding="utf-8"))

    def test_no_tmp_file_is_left_behind_after_a_successful_write(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "journal.json"
            journal = PromotionJournal(path)
            journal.begin("demo", Path("/a"), Path("/a-s"), Path("/a-b"))
            leftovers = [p for p in Path(tmp).iterdir() if p.name != "journal.json"]
            self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
