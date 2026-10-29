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
        class QosPublish(MqttPublish):
            __slots__ = ("qos",)

            def __init__(self, topic, payload, retain=False, qos=1):
                super().__init__(topic, payload, retain)
                self.qos = qos

        class QosBridge(FakeBridge):
            def handle_message(self, topic, payload, *, retained=False):
                return [QosPublish(topic + "/result", "ok", retain=True, qos=1), MqttPublish(topic + "/plain", "ok")]

        dispatcher = MessageDispatcher(QosBridge(), PREFIX)
        client = FakeClient()
        dispatcher.on_message(client, None, FakeMessage(PREFIX + "cmd/status"))
        dispatcher.close(wait=True)
        self.assertEqual(
            client.published,
            [(PREFIX + "cmd/status/result", "ok", 1, True), (PREFIX + "cmd/status/plain", "ok", 0, False)],
        )

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


if __name__ == "__main__":
    unittest.main()
