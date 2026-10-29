# =============================================================================
# HYDRA-UMC-SDK - The MQTT transport every command/state bridge shares
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""What the CNC, laser, OpenPnP, 3D-printer and ROS 2 bridges each used to carry their own copy of, once.

A bridge listens on `hydra/bridges/<name>/cmd/#`, answers on `.../<verb>/result`, keeps a retained `.../state` and announces itself on a retained `.../availability`
topic ("online" once connected; "offline" is the Last Will the broker publishes if the link dies). The parts that are the same for all of them live here:

* `MqttPublish`: one message a bridge wants published (topic, payload, retained).
* `connect_with_retry`: the first connect is retried on `OSError` (a systemd unit may start before the broker listens); a TLS failure is never retried.
* `MessageDispatcher`: takes the messages off the network thread. Ordinary commands run one at a time, in order, on one lane; the stop verbs run on a second lane, so a stop never
  waits behind a slow status query. A retained delivery is a replay by the broker and is never treated as a request.
* `open_bridge_client`: builds the paho client (credentials and TLS from `hydra_umc_sdk.mqtt_connection`), sets the Last Will, subscribes and announces "online" after every
  (re)connect, and connects with retry. The bridge-specific part (what each topic means) stays in the bridge.

The paho client is imported lazily and can be passed in, so every line here is testable without a broker or paho installed.
"""

from __future__ import annotations

import logging
import ssl
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional, Protocol

from .mqtt_connection import apply_connection_settings, settings_from_env

_LOG = logging.getLogger(__name__)


class MqttPublish:
    """One message a bridge wants published."""

    __slots__ = ("topic", "payload", "retain")

    def __init__(self, topic: str, payload: str, retain: bool = False) -> None:
        self.topic = topic
        self.payload = payload
        self.retain = retain

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, MqttPublish)
            and (self.topic, self.payload, self.retain) == (other.topic, other.payload, other.retain)
        )

    def __hash__(self) -> int:
        return hash((self.topic, self.payload, self.retain))

    def __repr__(self) -> str:
        return f"MqttPublish(topic={self.topic!r}, payload={self.payload!r}, retain={self.retain!r})"


class MessageHandler(Protocol):
    """What the dispatcher needs of a bridge."""

    def handle_message(self, topic: str, payload: bytes, *, retained: bool = False) -> list[MqttPublish]: ...


def connect_with_retry(
    connect: Callable[[], None],
    *,
    max_attempts: int = 5,
    retry_delay_seconds: float = 2.0,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    """Retry `connect()` on OSError (what an unreachable broker raises: refused, timeout).

    Only OSError is retried; anything else is a real bug and propagates at once. A TLS error (an invalid certificate) will not get better by waiting: it gives up at
    once as well. `sleep` is injectable so a test proves the retry and the give-up without a real wait.
    """
    last_error: Optional[OSError] = None
    for attempt in range(1, max_attempts + 1):
        try:
            connect()
            return
        except ssl.SSLError as error:
            raise RuntimeError(f"the TLS handshake with the MQTT broker failed, not retrying: {error}") from error
        except OSError as error:
            last_error = error
            if attempt < max_attempts:
                sleep(retry_delay_seconds)
    raise RuntimeError(
        f"could not reach the MQTT broker after {max_attempts} attempts "
        f"({retry_delay_seconds}s apart): {last_error}"
    ) from last_error


class MessageDispatcher:
    """Takes the messages off the network thread: a status query that waits on a serial port or a service must not hold up the MQTT keep-alive, and a stop must not wait behind anything.

    Ordinary commands run one at a time, in order, on one lane; the commands named in `stop_verbs` (the topic below the prefix, for example `cmd/soft_reset`) run on a second lane.
    """

    def __init__(self, bridge: MessageHandler, topic_prefix: str, stop_verbs: frozenset[str] = frozenset()) -> None:
        self._bridge = bridge
        self._prefix = topic_prefix
        self._stop_verbs = frozenset(stop_verbs)
        self._lane = ThreadPoolExecutor(max_workers=1, thread_name_prefix="hydra-bridge")
        self._stop_lane = ThreadPoolExecutor(max_workers=1, thread_name_prefix="hydra-bridge-stop")

    def on_message(self, client: object, userdata: object, message: object) -> None:
        if bool(getattr(message, "retain", False)):
            return  # a replay by the broker, never a request
        topic = message.topic  # type: ignore[attr-defined]
        suffix = topic[len(self._prefix) :] if topic.startswith(self._prefix) else ""
        lane = self._stop_lane if suffix in self._stop_verbs else self._lane
        lane.submit(self._handle, client, topic, bytes(message.payload))  # type: ignore[attr-defined]

    def _handle(self, client: object, topic: str, payload: bytes) -> None:
        try:
            for publish in self._bridge.handle_message(topic, payload, retained=False):
                client.publish(publish.topic, publish.payload, qos=getattr(publish, "qos", 0), retain=publish.retain)  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001 - one bad message never ends the loop
            _LOG.exception("could not answer %s", topic)

    def close(self, wait: bool = True) -> None:
        self._lane.shutdown(wait=wait)
        self._stop_lane.shutdown(wait=wait)


def open_bridge_client(
    host: str,
    port: int,
    *,
    client_id: str,
    topic_prefix: str,
    dispatcher: MessageDispatcher,
    username: Optional[str] = None,
    password: Optional[str] = None,
    max_connect_attempts: int = 5,
    connect_retry_delay_seconds: float = 2.0,
    mqtt_module: object = None,
    on_connected: Optional[Callable[[object], None]] = None,
) -> object:
    """Build the paho client of a bridge and connect it (the caller then runs `client.loop_forever()` or `loop_start()`).

    * the credentials and the TLS of the service's environment (`HYDRA_MQTT_*`), unless `username` is given explicitly;
    * the Last Will: the retained `availability` topic turns "offline" if the link dies;
    * after every (re)connect that the broker accepted: subscribe to `<prefix>cmd/#`, publish "online" on `<prefix>availability` (retained, QoS 1), then `on_connected(client)`;
    * a refused login is left to paho, which reports it and retries on its own.

    `mqtt_module` is `paho.mqtt.client` unless a test passes a fake.
    """
    if password is not None and username is None:
        raise ValueError("password was given without a username - MQTT credentials need both")
    mqtt = mqtt_module
    if mqtt is None:
        try:
            import paho.mqtt.client as mqtt  # type: ignore[import-untyped,no-redef]
        except ImportError as error:
            raise RuntimeError(
                "paho-mqtt is not installed - install it to connect to a real HYDRA-UMC-MQTT-BROKER "
                "(the topic-dispatch and gating logic works and is tested without it)"
            ) from error
    availability = f"{topic_prefix}availability"

    def on_connect(client: object, userdata: object, flags: object, reason_code: object, properties: object = None) -> None:
        if getattr(reason_code, "is_failure", False):
            return  # the broker refused us: paho reports it and retries on its own
        client.subscribe(f"{topic_prefix}cmd/#")  # type: ignore[attr-defined]
        client.publish(availability, "online", qos=1, retain=True)  # type: ignore[attr-defined]
        if on_connected is not None:
            on_connected(client)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)  # type: ignore[attr-defined]
    apply_connection_settings(client, settings_from_env(), username=username, password=password)
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    client.will_set(availability, "offline", qos=1, retain=True)
    client.on_connect = on_connect
    client.on_message = dispatcher.on_message
    connect_with_retry(
        lambda: client.connect(host, port),
        max_attempts=max_connect_attempts,
        retry_delay_seconds=connect_retry_delay_seconds,
    )
    return client
