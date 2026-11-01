# =============================================================================
# HYDRA-UMC-SDK - Signed commands, bridge health and the shared reading of a job message
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import json
import os
import stat
import tempfile
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path

from hydra_umc_sdk import (
    BridgeHealth,
    CommandSigningError,
    CommandVerifier,
    ContractValidationError,
    IdempotencyStore,
    JobIntake,
    SignedCommandSettings,
    health_enabled_from_environment,
    health_report,
    health_topic,
    load_command_key,
    read_health,
    read_job_message,
    sign_command,
    signed_command_settings_from_environment,
    verify_command,
)
from hydra_umc_sdk.bridge_transport import MessageDispatcher, open_bridge_client

KEY = b"0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
OTHER_KEY = b"fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210"
TOPIC = "hydra/bridges/cnc/cmd/job"
NOW_MS = 1_767_261_600_000
JOB = {"job_id": "job-1", "idempotency_key": "job-1-v1", "source": "HYDRA-UMC-ORCHESTRATOR", "phase": "LOAD", "machine_state": "IDLE", "parameters": {}}


def _verifier(now_ms: int = NOW_MS, **settings) -> CommandVerifier:
    return CommandVerifier(SignedCommandSettings(enabled=True, key_file="unused", **settings), key=KEY, clock=lambda: now_ms / 1000)


class SignAndVerifyTests(unittest.TestCase):
    def test_a_signed_command_is_accepted_until_it_expires(self):
        signed = sign_command(TOPIC, JOB, KEY, now_ms=NOW_MS, expires_in_ms=10_000)
        self.assertEqual(signed["issued_at_ms"], NOW_MS)
        self.assertEqual(len(signed["signature"]), 64)
        for moment, ok in ((NOW_MS, True), (NOW_MS + 10_000, True), (NOW_MS + 10_001, False)):
            with self.subTest(moment=moment):
                self.assertIs(verify_command(TOPIC, signed, KEY, now_ms=moment).ok, ok)

    def test_the_sender_must_not_change_the_job_after_signing(self):
        signed = sign_command(TOPIC, JOB, KEY, now_ms=NOW_MS)
        for field, value in (("phase", "ABORT"), ("source", "someone-else"), ("parameters", {"x": "1"}), ("expires_in_ms", 29_999), ("issued_at_ms", NOW_MS + 1)):
            with self.subTest(field=field):
                altered = dict(signed, **{field: value})
                verdict = verify_command(TOPIC, altered, KEY, now_ms=NOW_MS)
                self.assertFalse(verdict.ok)
                self.assertIn("signature", verdict.reason)

    def test_another_key_or_another_topic_does_not_verify(self):
        signed = sign_command(TOPIC, JOB, KEY, now_ms=NOW_MS)
        self.assertFalse(verify_command(TOPIC, signed, OTHER_KEY, now_ms=NOW_MS).ok)
        self.assertFalse(verify_command("hydra/bridges/laser/cmd/job", signed, KEY, now_ms=NOW_MS).ok)

    def test_a_command_from_the_future_is_refused_beyond_the_skew(self):
        signed = sign_command(TOPIC, JOB, KEY, now_ms=NOW_MS + 5_000)
        self.assertTrue(verify_command(TOPIC, signed, KEY, now_ms=NOW_MS, max_clock_skew_ms=5_000).ok)
        verdict = verify_command(TOPIC, signed, KEY, now_ms=NOW_MS, max_clock_skew_ms=4_999)
        self.assertFalse(verdict.ok)
        self.assertIn("future", verdict.reason)

    def test_a_command_cannot_ask_to_stay_valid_for_longer_than_the_bridge_accepts(self):
        signed = sign_command(TOPIC, JOB, KEY, now_ms=NOW_MS, expires_in_ms=600_000)
        verdict = verify_command(TOPIC, signed, KEY, now_ms=NOW_MS, max_expires_in_ms=300_000)
        self.assertFalse(verdict.ok)
        self.assertIn("at most", verdict.reason)

    def test_what_is_missing_or_malformed_is_refused_without_raising(self):
        signed = sign_command(TOPIC, JOB, KEY, now_ms=NOW_MS)
        cases = [{k: v for k, v in signed.items() if k != "signature"}, {k: v for k, v in signed.items() if k != "issued_at_ms"}, JOB]
        cases += [dict(signed, signature="X" * 64), dict(signed, signature=5), dict(signed, issued_at_ms="1"), dict(signed, issued_at_ms=True), dict(signed, expires_in_ms=0), dict(signed, expires_in_ms=1.5)]
        for payload in cases:
            with self.subTest(payload=payload):
                self.assertFalse(verify_command(TOPIC, payload, KEY, now_ms=NOW_MS).ok)
        self.assertFalse(verify_command(TOPIC, ["not", "an", "object"], KEY, now_ms=NOW_MS).ok)  # type: ignore[arg-type]

    def test_the_bytes_that_are_signed_do_not_depend_on_the_order_of_the_fields(self):
        reordered = dict(reversed(list(JOB.items())))
        first = sign_command(TOPIC, JOB, KEY, now_ms=NOW_MS)
        second = sign_command(TOPIC, reordered, KEY, now_ms=NOW_MS)
        self.assertEqual(first["signature"], second["signature"])

    def test_a_signature_over_known_bytes_stays_the_same(self):
        # a fixed vector, so that a client in another language can check that it writes the same bytes
        signed = sign_command("t", {"a": "1"}, KEY, now_ms=1, expires_in_ms=2)
        self.assertEqual(signed["signature"], "565dbcce245291a8824fe9eba1c630ff5c0fcedf9af9814aa3966b8964083715")

    def test_signing_asks_for_a_real_key_and_a_real_expiry(self):
        with self.assertRaises(CommandSigningError):
            sign_command(TOPIC, JOB, b"short")
        with self.assertRaises(CommandSigningError):
            sign_command(TOPIC, JOB, KEY, expires_in_ms=0)
        with self.assertRaises(CommandSigningError):
            sign_command("", JOB, KEY)


class SettingsAndKeyTests(unittest.TestCase):
    def test_it_is_off_unless_the_service_says_yes(self):
        for env in ({}, {"HYDRA_UMC_CNC_SIGNED_COMMANDS": "no"}, {"HYDRA_UMC_CNC_SIGNED_COMMANDS": "0"}, {"HYDRA_UMC_CNC_SIGNED_COMMANDS": ""}):
            with self.subTest(env=env):
                settings = signed_command_settings_from_environment("CNC", env)
                self.assertFalse(settings.enabled)
        verifier = CommandVerifier.from_environment("CNC", {})
        self.assertTrue(verifier.check(TOPIC, JOB).ok)  # nothing is asked, and no key is read

    def test_a_misspelt_switch_is_an_error_not_an_off(self):
        with self.assertRaises(CommandSigningError):
            signed_command_settings_from_environment("CNC", {"HYDRA_UMC_CNC_SIGNED_COMMANDS": "ye"})

    def test_on_without_a_key_file_stops_the_start(self):
        with self.assertRaises(CommandSigningError):
            signed_command_settings_from_environment("CNC", {"HYDRA_UMC_CNC_SIGNED_COMMANDS": "yes"})

    def test_the_limits_come_from_the_environment(self):
        env = {"HYDRA_UMC_CNC_SIGNED_COMMANDS": "yes", "HYDRA_UMC_CNC_COMMAND_KEY_FILE": "k", "HYDRA_UMC_CNC_COMMAND_MAX_SKEW_MS": "100", "HYDRA_UMC_CNC_COMMAND_MAX_EXPIRES_MS": "2000"}
        settings = signed_command_settings_from_environment("CNC", env)
        self.assertEqual((settings.enabled, settings.max_clock_skew_ms, settings.max_expires_in_ms), (True, 100, 2000))
        with self.assertRaises(CommandSigningError):
            signed_command_settings_from_environment("CNC", dict(env, HYDRA_UMC_CNC_COMMAND_MAX_SKEW_MS="soon"))

    def test_the_key_file_is_read_and_its_content_never_shows_in_an_error(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cmd.key"
            path.write_bytes(KEY + b"\n")
            if os.name == "posix":
                path.chmod(stat.S_IRUSR | stat.S_IWUSR)
            self.assertEqual(load_command_key(str(path)), KEY)
            short = Path(folder) / "short.key"
            short.write_bytes(b"secret-but-short")
            if os.name == "posix":
                short.chmod(stat.S_IRUSR | stat.S_IWUSR)
            with self.assertRaises(CommandSigningError) as raised:
                load_command_key(str(short))
            self.assertNotIn("secret-but-short", str(raised.exception))
            with self.assertRaises(CommandSigningError):
                load_command_key(str(Path(folder) / "missing.key"))

    @unittest.skipUnless(os.name == "posix", "POSIX permissions")
    def test_a_key_file_that_others_can_read_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cmd.key"
            path.write_bytes(KEY)
            path.chmod(0o644)
            with self.assertRaises(CommandSigningError):
                load_command_key(str(path))

    def test_the_verifier_reads_the_key_when_it_is_switched_on(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cmd.key"
            path.write_bytes(KEY)
            if os.name == "posix":
                path.chmod(0o600)
            env = {"HYDRA_UMC_CNC_SIGNED_COMMANDS": "yes", "HYDRA_UMC_CNC_COMMAND_KEY_FILE": str(path)}
            verifier = CommandVerifier.from_environment("CNC", env, clock=lambda: NOW_MS / 1000)
            self.assertTrue(verifier.enabled)
            self.assertFalse(verifier.check(TOPIC, JOB).ok)
            self.assertTrue(verifier.check(TOPIC, sign_command(TOPIC, JOB, KEY, now_ms=NOW_MS)).ok)


class IntakeTests(unittest.TestCase):
    def test_with_signing_on_an_unsigned_or_expired_job_is_not_accepted(self):
        intake = JobIntake(IdempotencyStore(), _verifier())
        unsigned = intake.accept(JOB, topic=TOPIC)
        self.assertFalse(unsigned.accepted)
        self.assertTrue(unsigned.unsigned)
        expired = intake.accept(sign_command(TOPIC, JOB, KEY, now_ms=NOW_MS - 60_000, expires_in_ms=1_000), topic=TOPIC)
        self.assertFalse(expired.accepted)
        self.assertIn("expired", expired.reason)

    def test_a_signed_job_is_accepted_once(self):
        intake = JobIntake(IdempotencyStore(), _verifier())
        signed = sign_command(TOPIC, JOB, KEY, now_ms=NOW_MS)
        first = intake.accept(signed, topic=TOPIC)
        self.assertTrue(first.accepted)
        self.assertEqual(first.job.job_id, "job-1")
        second = intake.accept(signed, topic=TOPIC)
        self.assertTrue(second.duplicate)

    def test_the_topic_is_needed_to_check_a_signature(self):
        intake = JobIntake(None, _verifier())
        self.assertFalse(intake.accept(sign_command(TOPIC, JOB, KEY, now_ms=NOW_MS)).accepted)

    def test_a_retained_message_is_ignored_even_when_it_is_signed(self):
        intake = JobIntake(None, _verifier())
        result = intake.accept(sign_command(TOPIC, JOB, KEY, now_ms=NOW_MS), retained=True, topic=TOPIC)
        self.assertTrue(result.retained)
        self.assertFalse(result.accepted)

    def test_with_signing_off_nothing_changes(self):
        intake = JobIntake(None, CommandVerifier(SignedCommandSettings()))
        self.assertTrue(intake.accept(JOB, topic=TOPIC).accepted)
        self.assertTrue(JobIntake(None).accept(JOB).accepted)


class ReadJobMessageTests(unittest.TestCase):
    def setUp(self):
        self.store = IdempotencyStore()
        self.intake = JobIntake(self.store)

    def read(self, payload, **kwargs):
        raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        return read_job_message(self.intake, TOPIC, raw, **kwargs)

    def test_a_retained_message_is_ignored(self):
        self.assertTrue(self.read(JOB, retained=True).ignore)

    def test_what_cannot_be_a_job_is_refused_with_a_reason(self):
        for label, payload in (("too large", b"{" + b" " * 20000 + b"}"), ("not json", b"{nope"), ("not an object", b"[1]"), ("missing fields", b"{}")):
            with self.subTest(label=label):
                message = self.read(payload)
                self.assertIsNone(message.job)
                self.assertFalse(message.refusal["allowed"])
        self.assertIn("larger than", self.read(b"{" + b" " * 20000 + b"}").refusal["reason"])
        self.assertTrue(self.read(b"{nope").refusal["reason"].startswith("malformed job payload"))

    def test_a_new_job_comes_back_and_a_repeat_gets_the_stored_answer(self):
        first = self.read(JOB)
        self.assertEqual(first.job.idempotency_key, "job-1-v1")
        self.store.remember("job-1-v1", '{"allowed": true}')
        again = self.read(JOB)
        self.assertEqual(again.repeat_answer, '{"allowed": true}')
        self.assertIsNone(again.job)

    def test_a_repeat_without_an_answer_is_refused_as_in_doubt(self):
        self.read(JOB)
        again = self.read(JOB)
        self.assertIsNone(again.repeat_answer)
        self.assertIn("may not have finished", again.refusal["reason"])

    def test_an_unsigned_job_is_refused_when_signing_is_on(self):
        self.intake = JobIntake(self.store, _verifier())
        message = self.read(JOB)
        self.assertIsNone(message.job)
        self.assertIn("not signed", message.refusal["reason"])
        self.assertTrue(self.read(sign_command(TOPIC, JOB, KEY, now_ms=NOW_MS)).job is not None)


class FakeClient:
    def __init__(self, *args, **kwargs):
        self.published, self.subscribed, self.will = [], [], None
        self.on_connect = None
        self.on_message = None

    def username_pw_set(self, user, password=None): ...
    def tls_set(self, *args, **kwargs): ...
    def tls_insecure_set(self, *args, **kwargs): ...
    def reconnect_delay_set(self, **kwargs): ...
    def will_set(self, topic, payload, qos=0, retain=False): self.will = (topic, payload, qos, retain)
    def connect(self, host, port): ...
    def subscribe(self, topic): self.subscribed.append(topic)
    def publish(self, topic, payload, qos=0, retain=False): self.published.append((topic, payload, qos, retain))


class HealthTests(unittest.TestCase):
    FIXED = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

    def health(self) -> BridgeHealth:
        return BridgeHealth("cnc", clock=lambda: self.FIXED)

    def test_the_topic_is_the_one_of_the_bridge(self):
        self.assertEqual(health_topic("cnc"), "hydra/bridges/cnc/health")
        for bad in ("", "CNC", "a/b", "a b", "x" * 33, "../x", "+", "#"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                health_topic(bad)

    def test_a_report_is_a_valid_health_report(self):
        report = health_report("DEGRADED", {"spindle": {"state": "FAIL", "detail": "no feedback"}}, now=self.FIXED)
        self.assertEqual(report["timestamp_utc"], "2026-01-01T10:00:00Z")
        read_health(json.dumps(report).encode())
        with self.assertRaises(ValueError):
            health_report("GREEN")

    def test_what_is_not_a_report_is_refused(self):
        for payload in (b"offline", b"[]", b'{"state": "READY"}', b""):
            with self.subTest(payload=payload), self.assertRaises(ContractValidationError):
                read_health(payload)

    def test_online_the_will_and_the_report_are_retained_at_qos_1(self):
        health = self.health()
        online, will, report = health.online(), health.will(), health.report("INHIBITED", {"door": {"state": "FAIL"}})
        for message in (online, will, report):
            self.assertEqual((message.topic, message.retain, message.qos), ("hydra/bridges/cnc/health", True, 1))
        self.assertEqual(json.loads(online.payload)["state"], "READY")
        self.assertEqual(json.loads(will.payload)["state"], "FAULT")
        self.assertEqual(json.loads(will.payload)["checks"]["link"]["state"], "FAIL")
        body = json.loads(report.payload)
        self.assertEqual((body["state"], body["checks"]["link"]["state"], body["checks"]["door"]["state"]), ("INHIBITED", "PASS", "FAIL"))
        self.assertEqual(json.loads(health.goodbye().payload)["state"], "FAULT")

    def test_it_is_off_unless_the_service_says_yes(self):
        self.assertFalse(health_enabled_from_environment("CNC", {}))
        self.assertFalse(health_enabled_from_environment("CNC", {"HYDRA_UMC_CNC_BRIDGE_HEALTH": "no"}))
        self.assertTrue(health_enabled_from_environment("CNC", {"HYDRA_UMC_CNC_BRIDGE_HEALTH": "yes"}))
        with self.assertRaises(ValueError):
            health_enabled_from_environment("CNC", {"HYDRA_UMC_CNC_BRIDGE_HEALTH": "maybe"})

    def connect(self, health):
        created = []

        def factory(*args, **kwargs):
            client = FakeClient(*args, **kwargs)
            created.append(client)
            return client

        module = types.SimpleNamespace(Client=factory, CallbackAPIVersion=types.SimpleNamespace(VERSION2="v2"))
        dispatcher = MessageDispatcher(types.SimpleNamespace(handle_message=lambda *a, **k: []), "hydra/bridges/cnc/")
        self.addCleanup(dispatcher.close, False)
        client = open_bridge_client("h", 1, client_id="c", topic_prefix="hydra/bridges/cnc/", dispatcher=dispatcher, mqtt_module=module, health=health)
        client.on_connect(client, None, None, types.SimpleNamespace(is_failure=False))
        return created[0]

    def test_without_the_switch_the_bridge_keeps_its_availability_topic(self):
        client = self.connect(None)
        self.assertEqual(client.will, ("hydra/bridges/cnc/availability", "offline", 1, True))
        self.assertIn(("hydra/bridges/cnc/availability", "online", 1, True), client.published)
        self.assertFalse([p for p in client.published if p[0].endswith("/health")])

    def test_with_the_switch_the_last_will_is_the_fault_report(self):
        client = self.connect(self.health())
        topic, payload, qos, retain = client.will
        self.assertEqual((topic, qos, retain), ("hydra/bridges/cnc/health", 1, True))
        self.assertEqual(json.loads(payload)["state"], "FAULT")
        published = {p[0]: p for p in client.published}
        self.assertEqual(json.loads(published["hydra/bridges/cnc/health"][1])["state"], "READY")
        # the retained availability message of an earlier run is cleared, not left saying "online"
        self.assertEqual(published["hydra/bridges/cnc/availability"][1:], (b"", 1, True))
        self.assertEqual(client.subscribed, ["hydra/bridges/cnc/cmd/#"])


if __name__ == "__main__":
    unittest.main()
