# =============================================================================
# HYDRA-UMC-SDK - Global stop guard tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The guard every bridge shares: off by default, SAFE_STOP refuses what moves, READY resumes, anything unreadable fails closed, and the rules about jobs and assertions."""

from __future__ import annotations

import json
import os
import threading
import unittest
from unittest import mock

from hydra_umc_sdk import global_stop as gs
from hydra_umc_sdk.global_stop import (
    DEFAULT_TOPIC,
    STATE_READY,
    STATE_SAFE_STOP,
    STATE_UNKNOWN,
    STATE_UNREADABLE,
    GlobalStopGuard,
    GlobalStopSettings,
    follow_on_connect,
    process_wide_guard,
    settings_from_environment,
)

READY = json.dumps({"schema_version": "1.0", "state": "READY", "source": "hydra-umc-server"}).encode()
SAFE_STOP = json.dumps({"schema_version": "1.0", "state": "SAFE_STOP", "source": "hydra-umc-server"}).encode()


def on(strict: bool = False) -> GlobalStopGuard:
    return GlobalStopGuard(GlobalStopSettings(enabled=True, strict=strict))


class FakeClient:
    def __init__(self) -> None:
        self.subscriptions: list[tuple[str, int]] = []

    def subscribe(self, topic: str, qos: int = 0) -> None:
        self.subscriptions.append((topic, qos))


class TheSwitch(unittest.TestCase):
    def test_everything_is_off_by_default_and_the_guard_never_blocks(self):
        guard = GlobalStopGuard()
        self.assertFalse(guard.enabled)
        self.assertEqual((guard.topic, guard.state), (DEFAULT_TOPIC, STATE_UNKNOWN))
        guard.observe(SAFE_STOP)
        self.assertFalse(guard.blocks())
        self.assertIsNone(guard.refusal("cmd/x", b"", moving=frozenset({"cmd/x"})))

    def test_the_settings_come_from_the_environment_and_only_a_plain_yes_switches_them_on(self):
        for value in ("", "0", "no", "off", "true2", "enabled"):
            with mock.patch.dict(os.environ, {"HYDRA_UMC_CNC_GLOBAL_STOP": value}):
                self.assertFalse(settings_from_environment("CNC").enabled, value)
        for value in ("1", "true", "YES", " on "):
            with mock.patch.dict(os.environ, {"HYDRA_UMC_CNC_GLOBAL_STOP": value}):
                self.assertTrue(settings_from_environment("CNC").enabled, value)
        with mock.patch.dict(os.environ, {"HYDRA_UMC_CNC_GLOBAL_STOP": "1", "HYDRA_UMC_CNC_GLOBAL_STOP_TOPIC": "site/estop", "HYDRA_UMC_CNC_GLOBAL_STOP_STRICT": "1"}):
            self.assertEqual(settings_from_environment("CNC"), GlobalStopSettings(True, "site/estop", True))
            self.assertFalse(settings_from_environment("LASER").enabled)        # the name keeps the bridges apart

    def test_a_topic_with_a_wildcard_or_a_bad_shape_is_refused(self):
        for topic in ("", "/a", "a/", "a/+/b", "a/#", "a\x00b", 5, None):
            with self.subTest(topic=topic), self.assertRaises(ValueError):
                GlobalStopSettings(True, topic)  # type: ignore[arg-type]

    def test_the_environment_with_a_bad_topic_raises_instead_of_guessing(self):
        with mock.patch.dict(os.environ, {"HYDRA_UMC_CNC_GLOBAL_STOP_TOPIC": "a/#"}), self.assertRaises(ValueError):
            settings_from_environment("CNC")


class TheState(unittest.TestCase):
    def test_a_bridge_that_never_heard_the_topic_is_left_alone_unless_strict(self):
        self.assertFalse(on().blocks())
        self.assertEqual(on().state, STATE_UNKNOWN)
        strict = on(strict=True)
        self.assertTrue(strict.blocks())
        self.assertIn("not known yet", strict.reason())
        strict.observe(READY)
        self.assertFalse(strict.blocks())

    def test_safe_stop_blocks_and_only_a_clear_ready_ends_it(self):
        guard = on()
        self.assertEqual(guard.observe(SAFE_STOP), STATE_SAFE_STOP)
        self.assertTrue(guard.blocks())
        self.assertIn("SAFE_STOP", guard.reason())
        self.assertEqual(guard.observe(READY), STATE_READY)
        self.assertFalse(guard.blocks())

    def test_anything_unclear_is_a_stop_and_never_an_exception(self):
        for payload in (b"", b"{", b"null", b"[]", b'"READY"', b"{}", b'{"state": "ready"}', b'{"state": "PAUSED"}', b'{"state": 1}', b"\xff\xfe", b"[" * 100_000):
            with self.subTest(payload=payload[:20]):
                guard = on()
                guard.observe(READY)
                self.assertIn(guard.observe(payload), (STATE_UNREADABLE, STATE_SAFE_STOP))
                self.assertTrue(guard.blocks())
                self.assertTrue("could not be read" in guard.reason() or "SAFE_STOP" in guard.reason())


class WhatIsRefused(unittest.TestCase):
    def test_a_moving_command_is_refused_while_stopped_and_a_reading_is_not(self):
        guard = on()
        guard.observe(SAFE_STOP)
        moving = frozenset({"cmd/move"})
        self.assertIsNotNone(guard.refusal("cmd/move", b"", moving=moving))
        self.assertIsNone(guard.refusal("cmd/status", b"", moving=moving))
        guard.observe(READY)
        self.assertIsNone(guard.refusal("cmd/move", b"", moving=moving))

    def test_a_job_is_refused_while_stopped_except_an_abort(self):
        guard = on()
        guard.observe(SAFE_STOP)
        self.assertTrue(guard.blocks_job(b'{"phase": "START"}'))
        self.assertFalse(guard.blocks_job(b'{"phase": " abort "}'))
        self.assertTrue(guard.blocks_job(b"not json"))
        self.assertTrue(guard.blocks_job(b"[]"))
        self.assertIsNone(guard.refusal("cmd/job", b'{"phase": "ABORT"}'))
        self.assertIsNotNone(guard.refusal("cmd/job", b'{"phase": "START"}'))
        guard.observe(READY)
        self.assertFalse(guard.blocks_job(b'{"phase": "START"}'))

    def test_asserting_a_line_is_refused_while_stopped_and_withdrawing_it_is_not(self):
        guard = on()
        guard.observe(SAFE_STOP)
        assertions = {"cmd/estop": "active"}
        self.assertIsNotNone(guard.refusal("cmd/estop", b'{"active": true}', assertions=assertions))
        self.assertIsNone(guard.refusal("cmd/estop", b'{"active": false}', assertions=assertions))
        self.assertIsNotNone(guard.refusal("cmd/estop", b"junk", assertions=assertions))
        self.assertIsNone(guard.refusal("cmd/other", b'{"active": true}', assertions=assertions))


class FollowingTheTopic(unittest.TestCase):
    def test_the_bridge_subscribes_after_every_connect_only_when_the_switch_is_on(self):
        self.assertIsNone(follow_on_connect(GlobalStopGuard()))
        callback = follow_on_connect(GlobalStopGuard(GlobalStopSettings(True, "site/estop")))
        self.assertIsNotNone(callback)
        client = FakeClient()
        callback(client)  # type: ignore[misc]
        callback(client)  # type: ignore[misc]
        self.assertEqual(client.subscriptions, [("site/estop", 1), ("site/estop", 1)])

    def test_the_process_wide_guard_is_one_per_name_and_reads_the_environment_once(self):
        with mock.patch.object(gs, "_PROCESS_WIDE", {}), mock.patch.dict(os.environ, {"HYDRA_UMC_TESTBRIDGE_GLOBAL_STOP": "1"}):
            first = process_wide_guard("TESTBRIDGE")
            self.assertTrue(first.enabled)
            self.assertIs(process_wide_guard("TESTBRIDGE"), first)
            os.environ["HYDRA_UMC_TESTBRIDGE_GLOBAL_STOP"] = "0"
            self.assertTrue(process_wide_guard("TESTBRIDGE").enabled)       # read once; a new process reads the setting again
            self.assertIsNot(process_wide_guard("OTHER"), first)

    def test_the_guard_is_safe_under_threads_and_never_reports_a_state_it_was_not_given(self):
        guard = on()
        seen: set[str] = set()

        def feed() -> None:
            for index in range(300):
                guard.observe(READY if index % 2 else SAFE_STOP)

        def read() -> None:
            for _ in range(600):
                seen.add(guard.state)
                guard.blocks()

        threads = [threading.Thread(target=feed), threading.Thread(target=read), threading.Thread(target=read)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertTrue(seen <= {STATE_UNKNOWN, STATE_READY, STATE_SAFE_STOP})


if __name__ == "__main__":
    unittest.main()
