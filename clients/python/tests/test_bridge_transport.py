# =============================================================================
# HYDRA-UMC-SDK - Shared bridge MQTT transport tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import os
import ssl
import threading
import types
import unittest
from unittest import mock

from hydra_umc_sdk.bridge_transport import MessageDispatcher, MqttPublish, connect_with_retry, open_bridge_client

PREFIX = "hydra/bridges/test/"


class FakeBridge:
    def __init__(self, release=None):
        self.seen = []
        self.release = release
        self.done = threading.Event()
        self.expected = 1

    def handle_message(self, topic, payload, *, retained=False):
        if self.release is not None and topic.endswith("cmd/slow"):
            self.release.wait(5)
        self.seen.append((topic, payload, retained))
        if len(self.seen) >= self.expected:
            self.done.set()
        if topic.endswith("boom"):
            raise RuntimeError("bridge failure")
        return [MqttPublish(topic + "/result", "ok", retain=False)]


class FakeMessage:
    def __init__(self, topic, payload=b"{}", retain=False):
        self.topic, self.payload, self.retain = topic, payload, retain


class FakeClient:
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs
        self.published, self.subscribed = [], []
        self.will = None
        self.connect_calls = []
        self.connect_failures = []
        self.credentials = None
        self.tls = None
        self.reconnect = None

    def username_pw_set(self, user, password=None):
        self.credentials = (user, password)

    def tls_set(self, **arguments):
        self.tls = arguments

    def reconnect_delay_set(self, min_delay, max_delay):
        self.reconnect = (min_delay, max_delay)

    def will_set(self, topic, payload, qos=0, retain=False):
        self.will = (topic, payload, qos, retain)

    def connect(self, host, port):
        self.connect_calls.append((host, port))
        if self.connect_failures:
            raise self.connect_failures.pop(0)

    def subscribe(self, topic):
        self.subscribed.append(topic)

    def publish(self, topic, payload, qos=0, retain=False):
        self.published.append((topic, payload, qos, retain))


def fake_paho():
    created = []

    def factory(*args, **kwargs):
        client = FakeClient(*args, **kwargs)
        created.append(client)
        return client

    module = types.SimpleNamespace(Client=factory, CallbackAPIVersion=types.SimpleNamespace(VERSION2="v2"))
    return module, created


class ConnectWithRetryTests(unittest.TestCase):
    def test_retries_oserror_then_succeeds(self):
        calls, sleeps = [], []

        def connect():
            calls.append(1)
            if len(calls) < 3:
                raise ConnectionRefusedError("refused")

        connect_with_retry(connect, max_attempts=5, retry_delay_seconds=1.5, sleep=sleeps.append)
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [1.5, 1.5])

    def test_gives_up_after_the_attempts(self):
        calls = []

        def connect():
            calls.append(1)
            raise OSError("down")

        with self.assertRaisesRegex(RuntimeError, "after 3 attempts"):
            connect_with_retry(connect, max_attempts=3, sleep=lambda _s: None)
        self.assertEqual(len(calls), 3)

    def test_a_tls_error_is_not_retried(self):
        calls = []

        def connect():
            calls.append(1)
            raise ssl.SSLError("bad certificate")

        with self.assertRaisesRegex(RuntimeError, "TLS handshake"):
            connect_with_retry(connect, max_attempts=5, sleep=lambda _s: None)
        self.assertEqual(len(calls), 1)

    def test_another_error_propagates_at_once(self):
        calls = []

        def connect():
            calls.append(1)
            raise ValueError("a bug")

        with self.assertRaises(ValueError):
            connect_with_retry(connect, sleep=lambda _s: None)
        self.assertEqual(len(calls), 1)


class MqttPublishTests(unittest.TestCase):
    def test_value_equality_and_hash(self):
        a, b = MqttPublish("t", "p", True), MqttPublish("t", "p", True)
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(a, MqttPublish("t", "p", False))
        self.assertNotEqual(a, "t")


class DispatcherTests(unittest.TestCase):
    def test_a_command_is_answered_on_the_client(self):
        bridge = FakeBridge()
        dispatcher = MessageDispatcher(bridge, PREFIX)
        client = FakeClient()
        dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/status"))
        dispatcher.close(wait=True)
        self.assertEqual(client.published, [(PREFIX + "cmd/status/result", "ok", 0, False)])
        self.assertEqual(bridge.seen, [(PREFIX + "cmd/status", b"{}", False)])

    def test_the_qos_of_an_answer_is_kept(self):
        class QosBridge(FakeBridge):
            def handle_message(self, topic, payload, *, retained=False):
                return [MqttPublish(topic + "/result", "ok", retain=True, qos=1), MqttPublish(topic + "/plain", "ok")]

        dispatcher = MessageDispatcher(QosBridge(), PREFIX)
        client = FakeClient()
        dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/status"))
        dispatcher.close(wait=True)
        self.assertEqual(
            client.published,
            [(PREFIX + "cmd/status/result", "ok", 1, True), (PREFIX + "cmd/status/plain", "ok", 0, False)],
        )

    def test_a_publish_defaults_to_qos_zero_and_compares_by_qos(self):
        self.assertEqual(MqttPublish("t", "p").qos, 0)
        self.assertEqual(MqttPublish("t", "p"), MqttPublish("t", "p", False, 0))
        self.assertNotEqual(MqttPublish("t", "p", qos=1), MqttPublish("t", "p"))
        self.assertEqual(len({MqttPublish("t", "p"), MqttPublish("t", "p", qos=2)}), 2)
        self.assertIn("qos=1", repr(MqttPublish("t", "p", qos=1)))

    def test_a_qos_outside_zero_to_two_is_refused(self):
        for bad in (3, -1, True, 1.0, "1", None):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                MqttPublish("t", "p", qos=bad)  # type: ignore[arg-type]

    def test_a_duck_typed_publish_without_qos_goes_out_at_zero(self):
        class Plain:
            topic, payload, retain = "x/result", "ok", False

        class PlainBridge(FakeBridge):
            def handle_message(self, topic, payload, *, retained=False):
                return [Plain()]

        dispatcher = MessageDispatcher(PlainBridge(), PREFIX)
        client = FakeClient()
        dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/status"))
        dispatcher.close(wait=True)
        self.assertEqual(client.published, [("x/result", "ok", 0, False)])

    def test_a_retained_replay_is_never_a_request(self):
        bridge = FakeBridge()
        dispatcher = MessageDispatcher(bridge, PREFIX)
        client = FakeClient()
        dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/job", retain=True))
        dispatcher.close(wait=True)
        self.assertEqual(bridge.seen, [])
        self.assertEqual(client.published, [])

    def test_a_failing_bridge_does_not_end_the_loop(self):
        bridge = FakeBridge()
        bridge.expected = 2
        dispatcher = MessageDispatcher(bridge, PREFIX)
        client = FakeClient()
        with self.assertLogs("hydra_umc_sdk.bridge_transport", level="ERROR"):
            dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/boom"))
            dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/status"))
            dispatcher.close(wait=True)
        self.assertEqual(len(bridge.seen), 2)
        self.assertEqual(client.published, [(PREFIX + "cmd/status/result", "ok", 0, False)])

    def test_a_stop_verb_does_not_wait_behind_a_slow_command(self):
        release = threading.Event()
        bridge = FakeBridge(release=release)
        dispatcher = MessageDispatcher(bridge, PREFIX, frozenset({"cmd/stop"}))
        client = FakeClient()
        dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/slow"))
        dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/stop"))
        self.assertTrue(bridge.done.wait(5), "the stop must be handled while the slow command still waits")
        self.assertEqual([seen[0] for seen in bridge.seen], [PREFIX + "cmd/stop"])
        release.set()
        dispatcher.close(wait=True)
        self.assertEqual([seen[0] for seen in bridge.seen], [PREFIX + "cmd/stop", PREFIX + "cmd/slow"])

    def test_without_the_stop_lane_the_stop_would_queue(self):
        # the contrast that proves the previous test measures the lane: with no stop verb the same two messages run in order
        release = threading.Event()
        bridge = FakeBridge(release=release)
        bridge.expected = 2
        dispatcher = MessageDispatcher(bridge, PREFIX)
        client = FakeClient()
        dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/slow"))
        dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/stop"))
        self.assertFalse(bridge.done.wait(0.3))
        self.assertEqual(bridge.seen, [])
        release.set()
        dispatcher.close(wait=True)
        self.assertEqual([seen[0] for seen in bridge.seen], [PREFIX + "cmd/slow", PREFIX + "cmd/stop"])

    def test_a_topic_outside_the_prefix_is_an_ordinary_command(self):
        bridge = FakeBridge()
        dispatcher = MessageDispatcher(bridge, PREFIX, frozenset({""}))
        client = FakeClient()
        dispatcher.on_message(client, None, FakeMessage("other/topic"))
        dispatcher.close(wait=True)
        self.assertEqual(len(bridge.seen), 1)


class OpenBridgeClientTests(unittest.TestCase):
    def open(self, **overrides):
        module, created = fake_paho()
        dispatcher = MessageDispatcher(FakeBridge(), PREFIX)
        self.addCleanup(dispatcher.close, False)
        arguments = dict(client_id="hydra-umc-bridge-test", topic_prefix=PREFIX, dispatcher=dispatcher, mqtt_module=module, connect_retry_delay_seconds=0)
        arguments.update(overrides)
        with mock.patch.dict(os.environ, {}, clear=False):
            for name in [n for n in os.environ if n.startswith("HYDRA_MQTT_")]:
                os.environ.pop(name)
            client = open_bridge_client("broker.local", 1883, **arguments)
        return client, created, dispatcher

    def test_the_client_is_configured_and_connected(self):
        client, created, dispatcher = self.open()
        self.assertIs(client, created[0])
        self.assertEqual(client.args, ("v2",))
        self.assertEqual(client.kwargs, {"client_id": "hydra-umc-bridge-test"})
        self.assertEqual(client.will, (PREFIX + "availability", "offline", 1, True))
        self.assertEqual(client.reconnect, (1, 30))
        self.assertEqual(client.connect_calls, [("broker.local", 1883)])
        self.assertEqual(client.on_message, dispatcher.on_message)

    def test_an_accepted_connection_subscribes_and_announces_online(self):
        announced = []
        client, _created, _dispatcher = self.open(on_connected=announced.append)
        client.on_connect(client, None, {}, types.SimpleNamespace(is_failure=False), None)
        self.assertEqual(client.subscribed, [PREFIX + "cmd/#"])
        self.assertEqual(client.published, [(PREFIX + "availability", "online", 1, True)])
        self.assertEqual(announced, [client])

    def test_a_refused_connection_neither_subscribes_nor_announces(self):
        client, _created, _dispatcher = self.open()
        client.on_connect(client, None, {}, types.SimpleNamespace(is_failure=True), None)
        self.assertEqual(client.subscribed, [])
        self.assertEqual(client.published, [])

    def test_credentials_come_from_the_call_or_the_environment(self):
        client, _c, _d = self.open(username="bridge-cnc", password="s3cret")
        self.assertEqual(client.credentials, ("bridge-cnc", "s3cret"))
        module, _created = fake_paho()
        dispatcher = MessageDispatcher(FakeBridge(), PREFIX)
        self.addCleanup(dispatcher.close, False)
        with mock.patch.dict(os.environ, {"HYDRA_MQTT_USERNAME": "env-user", "HYDRA_MQTT_PASSWORD": "env-pass", "HYDRA_MQTT_TLS_CA": "/etc/ca.pem"}):
            client = open_bridge_client("h", 1, client_id="c", topic_prefix=PREFIX, dispatcher=dispatcher, mqtt_module=module)
        self.assertEqual(client.credentials, ("env-user", "env-pass"))
        self.assertEqual(client.tls, {"ca_certs": "/etc/ca.pem"})

    def test_a_password_without_a_user_is_refused(self):
        with self.assertRaises(ValueError):
            self.open(password="s3cret")

    def test_the_first_connect_is_retried(self):
        module, created = fake_paho()
        dispatcher = MessageDispatcher(FakeBridge(), PREFIX)
        self.addCleanup(dispatcher.close, False)
        original = module.Client

        def factory(*args, **kwargs):
            client = original(*args, **kwargs)
            client.connect_failures = [ConnectionRefusedError("a"), ConnectionRefusedError("b")]
            return client

        module.Client = factory
        client = open_bridge_client("h", 1, client_id="c", topic_prefix=PREFIX, dispatcher=dispatcher, mqtt_module=module, connect_retry_delay_seconds=0)
        self.assertEqual(len(client.connect_calls), 3)

    def test_a_missing_paho_says_so(self):
        dispatcher = MessageDispatcher(FakeBridge(), PREFIX)
        self.addCleanup(dispatcher.close, False)
        with mock.patch.dict("sys.modules", {"paho": None, "paho.mqtt": None, "paho.mqtt.client": None}):
            with self.assertRaisesRegex(RuntimeError, "paho-mqtt is not installed"):
                open_bridge_client("h", 1, client_id="c", topic_prefix=PREFIX, dispatcher=dispatcher)


class CurrentLimitsCharacterizationTests(unittest.TestCase):
    """Fix what the transport does with no limit configured, so the opt-in limits can never change it."""

    def test_the_queue_has_no_limit_and_nothing_is_dropped(self):
        release = threading.Event()
        bridge = FakeBridge(release=release)
        bridge.expected = 201
        dispatcher = MessageDispatcher(bridge, PREFIX)
        client = FakeClient()
        dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/slow"))
        for index in range(200):
            dispatcher.on_message(client, None, FakeMessage(PREFIX + f"cmd/n{index}"))
        release.set()
        dispatcher.close(wait=True)
        self.assertEqual(len(bridge.seen), 201)

    def test_a_huge_payload_is_handed_to_the_bridge(self):
        bridge = FakeBridge()
        dispatcher = MessageDispatcher(bridge, PREFIX)
        dispatcher.on_message(FakeClient(), None, FakeMessage(PREFIX + "cmd/big", payload=b"x" * 5_000_000))
        dispatcher.close(wait=True)
        self.assertEqual(len(bridge.seen[0][1]), 5_000_000)

    def test_the_first_connect_waits_a_fixed_delay(self):
        sleeps = []

        def connect():
            raise OSError("down")

        with self.assertRaises(RuntimeError):
            connect_with_retry(connect, max_attempts=5, retry_delay_seconds=2.0, sleep=sleeps.append)
        self.assertEqual(sleeps, [2.0, 2.0, 2.0, 2.0])

    def test_the_reconnect_delay_is_one_to_thirty_seconds(self):
        module, created = fake_paho()
        dispatcher = MessageDispatcher(FakeBridge(), PREFIX)
        self.addCleanup(dispatcher.close, False)
        open_bridge_client("h", 1, client_id="c", topic_prefix=PREFIX, dispatcher=dispatcher, mqtt_module=module)
        self.assertEqual(created[0].reconnect, (1, 30))


class HardenedDispatcherTests(unittest.TestCase):
    def test_a_slow_client_fills_the_queue_and_the_oldest_are_dropped(self):
        release = threading.Event()
        bridge = FakeBridge(release=release)
        dispatcher = MessageDispatcher(bridge, PREFIX, max_queue=3)
        client = FakeClient()
        dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/slow"))
        for _ in range(100):  # let the slow command start so it is running, not waiting
            if dispatcher._lane._futures and dispatcher._lane._futures[0].running():
                break
            threading.Event().wait(0.01)
        for index in range(10):
            dispatcher.on_message(client, None, FakeMessage(PREFIX + f"cmd/n{index}"))
        self.assertEqual(dispatcher.stats(), {"dropped": 7, "oversized": 0, "queued": 3})
        release.set()
        dispatcher.close(wait=True)
        self.assertEqual([seen[0] for seen in bridge.seen], [PREFIX + "cmd/slow", PREFIX + "cmd/n7", PREFIX + "cmd/n8", PREFIX + "cmd/n9"])
        self.assertEqual(dispatcher.stats()["queued"], 0)

    def test_a_bound_that_is_not_reached_drops_nothing(self):
        bridge = FakeBridge()
        bridge.expected = 5
        dispatcher = MessageDispatcher(bridge, PREFIX, max_queue=50)
        client = FakeClient()
        for index in range(5):
            dispatcher.on_message(client, None, FakeMessage(PREFIX + f"cmd/n{index}"))
        dispatcher.close(wait=True)
        self.assertEqual(len(bridge.seen), 5)
        self.assertEqual(dispatcher.stats()["dropped"], 0)

    def test_the_stop_lane_is_never_bounded(self):
        release = threading.Event()
        bridge = FakeBridge(release=release)
        dispatcher = MessageDispatcher(bridge, PREFIX, frozenset({"cmd/stop"}), max_queue=1)
        client = FakeClient()
        dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/slow"))
        for _ in range(20):
            dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/stop"))
        release.set()
        dispatcher.close(wait=True)
        self.assertEqual(sum(1 for seen in bridge.seen if seen[0].endswith("cmd/stop")), 20)
        self.assertEqual(dispatcher.stats()["dropped"], 0)

    def test_a_giant_payload_is_refused_before_it_is_queued(self):
        bridge = FakeBridge()
        dispatcher = MessageDispatcher(bridge, PREFIX, max_payload_bytes=1000)
        client = FakeClient()
        with self.assertLogs("hydra_umc_sdk.bridge_transport", level="WARNING"):
            dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/big", payload=b"x" * 1001))
        dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/ok", payload=b"x" * 1000))
        dispatcher.close(wait=True)
        self.assertEqual([seen[0] for seen in bridge.seen], [PREFIX + "cmd/ok"])
        self.assertEqual(dispatcher.stats()["oversized"], 1)

    def test_a_stop_verb_is_exempt_from_the_payload_limit(self):
        bridge = FakeBridge()
        dispatcher = MessageDispatcher(bridge, PREFIX, frozenset({"cmd/stop"}), max_payload_bytes=10)
        dispatcher.on_message(FakeClient(), None, FakeMessage(PREFIX + "cmd/stop", payload=b"x" * 500))
        dispatcher.close(wait=True)
        self.assertEqual(len(bridge.seen), 1)
        self.assertEqual(dispatcher.stats()["oversized"], 0)

    def test_the_limits_are_validated(self):
        for bad in (0, -1, True, 1.5, "3"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    MessageDispatcher(FakeBridge(), PREFIX, max_queue=bad)  # type: ignore[arg-type]
                with self.assertRaises(ValueError):
                    MessageDispatcher(FakeBridge(), PREFIX, max_payload_bytes=bad)  # type: ignore[arg-type]

    def test_a_broker_that_stays_down_backs_off_exponentially_with_a_cap(self):
        sleeps = []

        def connect():
            raise ConnectionRefusedError("down")

        with self.assertRaises(RuntimeError):
            connect_with_retry(connect, max_attempts=6, retry_delay_seconds=1.0, sleep=sleeps.append, backoff_factor=2.0, max_delay_seconds=6.0)
        self.assertEqual(sleeps, [1.0, 2.0, 4.0, 6.0, 6.0])

    def test_jitter_spreads_the_wait_with_an_injected_random_source(self):
        sleeps = []

        def connect():
            raise OSError("down")

        values = iter([0.0, 0.5, 0.999999])
        with self.assertRaises(RuntimeError):
            connect_with_retry(connect, max_attempts=4, retry_delay_seconds=10.0, sleep=sleeps.append, jitter=0.5, rng=lambda: next(values))
        self.assertAlmostEqual(sleeps[0], 5.0)
        self.assertAlmostEqual(sleeps[1], 10.0)
        self.assertAlmostEqual(sleeps[2], 15.0, places=3)

    def test_the_backoff_options_are_validated(self):
        for options in ({"backoff_factor": 0.5}, {"jitter": 1.5}, {"jitter": -0.1}, {"max_delay_seconds": -1}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                connect_with_retry(lambda: None, **options)

    def test_a_broker_that_comes_back_stops_the_waiting(self):
        sleeps, calls = [], []

        def connect():
            calls.append(1)
            if len(calls) < 3:
                raise TimeoutError("slow")

        connect_with_retry(connect, retry_delay_seconds=1.0, backoff_factor=3.0, sleep=sleeps.append)
        self.assertEqual(sleeps, [1.0, 3.0])

    def test_the_reconnect_delays_are_configurable_and_validated(self):
        module, created = fake_paho()
        dispatcher = MessageDispatcher(FakeBridge(), PREFIX)
        self.addCleanup(dispatcher.close, False)
        open_bridge_client(
            "h", 1, client_id="c", topic_prefix=PREFIX, dispatcher=dispatcher, mqtt_module=module,
            reconnect_min_delay_seconds=0.5, reconnect_max_delay_seconds=120,
        )
        self.assertEqual(created[0].reconnect, (0.5, 120))
        for low, high in ((0, 30), (5, 2), (-1, 3)):
            with self.subTest(low=low, high=high), self.assertRaises(ValueError):
                open_bridge_client(
                    "h", 1, client_id="c", topic_prefix=PREFIX, dispatcher=dispatcher, mqtt_module=module,
                    reconnect_min_delay_seconds=low, reconnect_max_delay_seconds=high,
                )

    def test_open_bridge_client_passes_the_first_connect_backoff_on(self):
        module, _created = fake_paho()
        dispatcher = MessageDispatcher(FakeBridge(), PREFIX)
        self.addCleanup(dispatcher.close, False)
        with mock.patch("hydra_umc_sdk.bridge_transport.connect_with_retry") as retry:
            open_bridge_client(
                "h", 1, client_id="c", topic_prefix=PREFIX, dispatcher=dispatcher, mqtt_module=module,
                connect_retry_delay_seconds=1.0, connect_backoff_factor=4.0, connect_max_delay_seconds=3.0, connect_jitter=0.2,
            )
        kwargs = retry.call_args.kwargs
        self.assertEqual((kwargs["retry_delay_seconds"], kwargs["backoff_factor"], kwargs["max_delay_seconds"], kwargs["jitter"]), (1.0, 4.0, 3.0, 0.2))


if __name__ == "__main__":
    unittest.main()
