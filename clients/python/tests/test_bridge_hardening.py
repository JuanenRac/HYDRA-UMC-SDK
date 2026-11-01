# =============================================================================
# HYDRA-UMC-SDK - Bridge transport hardening settings tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The opt-in limits of a bridge transport: off by default (nothing changes), read from the environment of the service, strictly checked, and what they hand the dispatcher."""

from __future__ import annotations

import threading
import unittest

from hydra_umc_sdk.bridge_transport import BridgeHardening, MessageDispatcher, MqttPublish, hardening_from_environment


def env(**values: str) -> dict[str, str]:
    return {f"HYDRA_UMC_TEST_{key}": value for key, value in values.items()}


class TheSettings(unittest.TestCase):
    def test_by_default_nothing_is_limited_and_nothing_is_handed_over(self):
        settings = hardening_from_environment("TEST", {})
        self.assertEqual(settings, BridgeHardening())
        self.assertFalse(settings.enabled)
        self.assertEqual((settings.dispatcher_kwargs(), settings.connect_kwargs()), ({}, {}))

    def test_only_a_plain_yes_switches_it_on(self):
        for value in ("", "0", "no", "off", "false", "hardened", "2", "enabled"):
            with self.subTest(value=value):
                self.assertFalse(hardening_from_environment("TEST", env(HARDENED=value)).enabled)
        for value in ("1", "true", "YES", " on "):
            with self.subTest(value=value):
                settings = hardening_from_environment("TEST", env(HARDENED=value))
                self.assertTrue(settings.enabled)
                self.assertEqual((settings.max_queue, settings.max_payload_bytes), (64, None))
                self.assertEqual(settings.dispatcher_kwargs(), {"max_queue": 64})
                self.assertEqual(settings.connect_kwargs(), {"connect_backoff_factor": 2.0, "connect_max_delay_seconds": 30.0, "connect_jitter": 0.25})

    def test_the_other_variables_are_not_even_read_while_the_switch_is_off(self):
        self.assertFalse(hardening_from_environment("TEST", env(MAX_QUEUE="not a number", CONNECT_JITTER="9")).enabled)

    def test_the_name_keeps_the_bridges_apart(self):
        self.assertFalse(hardening_from_environment("OTHER", env(HARDENED="1")).enabled)

    def test_every_limit_can_be_tuned(self):
        settings = hardening_from_environment(
            "TEST", env(HARDENED="1", MAX_QUEUE="8", MAX_PAYLOAD_BYTES="4096", CONNECT_BACKOFF_FACTOR="1.5", CONNECT_MAX_DELAY_SECONDS="10", CONNECT_JITTER="0"))
        self.assertEqual(settings.dispatcher_kwargs(), {"max_queue": 8, "max_payload_bytes": 4096})
        self.assertEqual(settings.connect_kwargs(), {"connect_backoff_factor": 1.5, "connect_max_delay_seconds": 10.0, "connect_jitter": 0.0})

    def test_a_wrong_limit_stops_the_start_instead_of_being_taken_for_no_limit(self):
        wrong = [
            ("MAX_QUEUE", "0"), ("MAX_QUEUE", "-3"), ("MAX_QUEUE", "x"), ("MAX_QUEUE", "1.5"), ("MAX_PAYLOAD_BYTES", "0"), ("MAX_PAYLOAD_BYTES", "big"),
            ("CONNECT_BACKOFF_FACTOR", "0.5"), ("CONNECT_BACKOFF_FACTOR", "11"), ("CONNECT_BACKOFF_FACTOR", "nan"), ("CONNECT_MAX_DELAY_SECONDS", "0"),
            ("CONNECT_MAX_DELAY_SECONDS", "99999"), ("CONNECT_MAX_DELAY_SECONDS", "inf"), ("CONNECT_JITTER", "-0.1"), ("CONNECT_JITTER", "1.5"),
        ]
        for name, value in wrong:
            with self.subTest(name=name, value=value), self.assertRaises(ValueError) as caught:
                hardening_from_environment("TEST", env(HARDENED="1", **{name: value}))
            self.assertIn("HYDRA_UMC_TEST_", str(caught.exception))

    def test_the_settings_object_refuses_booleans_and_wrong_types_too(self):
        for bad in ({"max_queue": True}, {"max_queue": 0}, {"max_payload_bytes": 0}, {"connect_jitter": True}, {"connect_backoff_factor": "2"}, {"connect_max_delay_seconds": True}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                BridgeHardening(enabled=True, **bad)  # type: ignore[arg-type]


class SlowBridge:
    def __init__(self) -> None:
        self.release = threading.Event()
        self.started = threading.Event()
        self.seen: list[str] = []

    def handle_message(self, topic: str, payload: bytes, *, retained: bool = False) -> list[MqttPublish]:
        self.started.set()
        self.release.wait(5)
        self.seen.append(topic)
        return []


class Msg:
    def __init__(self, topic: str, payload: bytes = b"x") -> None:
        self.topic, self.payload, self.retain = topic, payload, False


class Client:
    def publish(self, *args: object, **kwargs: object) -> None:
        pass


class WhatTheDispatcherDoesWithIt(unittest.TestCase):
    def test_a_hardened_dispatcher_drops_the_oldest_waiting_command_and_counts_it(self):
        bridge = SlowBridge()
        settings = hardening_from_environment("TEST", env(HARDENED="1", MAX_QUEUE="2"))
        dispatcher = MessageDispatcher(bridge, "hydra/bridges/t/", frozenset({"cmd/stop"}), **settings.dispatcher_kwargs())
        try:
            dispatcher.on_message(Client(), None, Msg("hydra/bridges/t/cmd/a"))
            self.assertTrue(bridge.started.wait(5))
            for name in ("b", "c", "d", "e"):
                dispatcher.on_message(Client(), None, Msg(f"hydra/bridges/t/cmd/{name}"))
            self.assertEqual((dispatcher.stats()["dropped"], dispatcher.stats()["queued"]), (2, 2))
        finally:
            bridge.release.set()
            dispatcher.close(wait=True)
        self.assertEqual(bridge.seen, ["hydra/bridges/t/cmd/a", "hydra/bridges/t/cmd/d", "hydra/bridges/t/cmd/e"])

    def test_a_hardened_dispatcher_refuses_an_oversized_payload_but_never_a_stop(self):
        bridge = SlowBridge()
        bridge.release.set()
        settings = hardening_from_environment("TEST", env(HARDENED="1", MAX_PAYLOAD_BYTES="16"))
        dispatcher = MessageDispatcher(bridge, "hydra/bridges/t/", frozenset({"cmd/stop"}), **settings.dispatcher_kwargs())
        try:
            dispatcher.on_message(Client(), None, Msg("hydra/bridges/t/cmd/a", b"y" * 100))
            dispatcher.on_message(Client(), None, Msg("hydra/bridges/t/cmd/stop", b"y" * 100))
        finally:
            dispatcher.close(wait=True)
        self.assertEqual(dispatcher.stats()["oversized"], 1)
        self.assertEqual(bridge.seen, ["hydra/bridges/t/cmd/stop"])


if __name__ == "__main__":
    unittest.main()
