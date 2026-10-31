# =============================================================================
# HYDRA-UMC-SDK - The MQTT transport every command/state bridge shares
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""What the CNC, laser, OpenPnP, 3D-printer and ROS 2 bridges each used to carry their own copy of, once.

A bridge listens on `hydra/bridges/<name>/cmd/#`, answers on `.../<verb>/result`, keeps a retained `.../state` and announces itself on a retained `.../availability`
topic ("online" once connected; "offline" is the Last Will the broker publishes if the link dies). The parts that are the same for all of them live here:

* `MqttPublish`: one message a bridge wants published (topic, payload, retained, QoS 0 by default).
* `connect_with_retry`: the first connect is retried on `OSError` (a systemd unit may start before the broker listens); a TLS failure is never retried.
* `MessageDispatcher`: takes the messages off the network thread. Ordinary commands run one at a time, in order, on one lane; the stop verbs run on a second lane, so a stop never
  waits behind a slow status query. A retained delivery is a replay by the broker and is never treated as a request.
* `open_bridge_client`: builds the paho client (credentials and TLS from `hydra_umc_sdk.mqtt_connection`), sets the Last Will, subscribes and announces "online" after every
  (re)connect, and connects with retry. The bridge-specific part (what each topic means) stays in the bridge.

The paho client is imported lazily and can be passed in, so every line here is testable without a broker or paho installed.
"""

from __future__ import annotations

import logging
import random
import ssl
import threading
import time
from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable, Optional, Protocol

from .mqtt_connection import apply_connection_settings, settings_from_env

_LOG = logging.getLogger(__name__)


class MqttPublish:
    """One message a bridge wants published (QoS 0 unless the bridge asks for 1 or 2)."""

    __slots__ = ("topic", "payload", "retain", "qos")

    def __init__(self, topic: str, payload: str, retain: bool = False, qos: int = 0) -> None:
        if type(qos) is not int or qos not in (0, 1, 2):
            raise ValueError(f"qos must be 0, 1 or 2, not {qos!r}")
        self.topic = topic
        self.payload = payload
        self.retain = retain
        self.qos = qos

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, MqttPublish)
            and (self.topic, self.payload, self.retain, self.qos) == (other.topic, other.payload, other.retain, other.qos)
        )

    def __hash__(self) -> int:
        return hash((self.topic, self.payload, self.retain, self.qos))

    def __repr__(self) -> str:
        return f"MqttPublish(topic={self.topic!r}, payload={self.payload!r}, retain={self.retain!r}, qos={self.qos!r})"


class MessageHandler(Protocol):
    """What the dispatcher needs of a bridge."""

    def handle_message(self, topic: str, payload: bytes, *, retained: bool = False) -> list[MqttPublish]: ...


def connect_with_retry(
    connect: Callable[[], None],
    *,
    max_attempts: int = 5,
    retry_delay_seconds: float = 2.0,
    sleep: Callable[[float], None] = time.sleep,
    backoff_factor: float = 1.0,
    max_delay_seconds: Optional[float] = None,
    jitter: float = 0.0,
    rng: Callable[[], float] = random.random,
) -> None:
    """Retry `connect()` on OSError (what an unreachable broker raises: refused, timeout).

    Only OSError is retried; anything else is a real bug and propagates at once. A TLS error (an invalid certificate) will not get better by waiting: it gives up at
    once as well. `sleep` is injectable so a test proves the retry and the give-up without a real wait.

    By default every wait is `retry_delay_seconds`. Opt-in: a `backoff_factor` above 1 multiplies the wait after every failed attempt (`retry_delay_seconds * factor ** n`),
    `max_delay_seconds` caps it, and `jitter` (0 to 1) spreads each wait randomly by up to that fraction either way, so a fleet of bridges does not retry in step (`rng`
    returns a float in [0, 1) and is injectable).
    """
    if backoff_factor < 1:
        raise ValueError("backoff_factor must be 1 or more")
    if not 0 <= jitter <= 1:
        raise ValueError("jitter must be between 0 and 1")
    if max_delay_seconds is not None and max_delay_seconds < 0:
        raise ValueError("max_delay_seconds must not be negative")
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
                delay = retry_delay_seconds * backoff_factor ** (attempt - 1)
                if max_delay_seconds is not None:
                    delay = min(delay, max_delay_seconds)
                if jitter:
                    delay = max(0.0, delay * (1 + jitter * (2 * rng() - 1)))
                sleep(delay)
    raise RuntimeError(
        f"could not reach the MQTT broker after {max_attempts} attempts "
        f"({retry_delay_seconds}s apart): {last_error}"
    ) from last_error


class _Lane:
    """One worker thread plus the futures that have not started yet, so the oldest can be dropped when the lane is bounded."""

    def __init__(self, thread_name_prefix: str, max_queue: Optional[int]) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix=thread_name_prefix)
        self._max_queue = max_queue
        self._futures: deque[Future[None]] = deque()
        self._lock = threading.Lock()
        self.dropped = 0

    def submit(self, function: Callable[..., None], *arguments: object) -> None:
        with self._lock:
            self._futures.append(self._executor.submit(function, *arguments))
            while self._futures and self._futures[0].done():
                self._futures.popleft()
            if self._max_queue is None:
                return
            waiting = [future for future in self._futures if not future.running() and not future.done()]
            for future in waiting[: max(0, len(waiting) - self._max_queue)]:
                if future.cancel():
                    self.dropped += 1
                    self._futures.remove(future)

    def waiting(self) -> int:
        with self._lock:
            return sum(1 for future in self._futures if not future.running() and not future.done())

    def shutdown(self, wait: bool) -> None:
        self._executor.shutdown(wait=wait)


class MessageDispatcher:
    """Takes the messages off the network thread: a status query that waits on a serial port or a service must not hold up the MQTT keep-alive, and a stop must not wait behind anything.

    Ordinary commands run one at a time, in order, on one lane; the commands named in `stop_verbs` (the topic below the prefix, for example `cmd/soft_reset`) run on a second lane.

    Two limits, both off by default (no limit, which is how it always behaved):

    * `max_queue`: how many ordinary commands may wait behind the one that is running. When a new one arrives with the queue full, the OLDEST waiting command is dropped
      (the newest state of the world wins) and counted in `stats()["dropped"]`. The stop lane is never bounded or dropped: a stop must always get through.
    * `max_payload_bytes`: a payload bigger than this is refused before it is queued, logged and counted in `stats()["oversized"]`. Stop verbs are exempt.
    """

    def __init__(
        self,
        bridge: MessageHandler,
        topic_prefix: str,
        stop_verbs: frozenset[str] = frozenset(),
        *,
        max_queue: Optional[int] = None,
        max_payload_bytes: Optional[int] = None,
    ) -> None:
        if max_queue is not None and (type(max_queue) is not int or max_queue < 1):
            raise ValueError("max_queue must be a whole number of 1 or more, or None for no limit")
        if max_payload_bytes is not None and (type(max_payload_bytes) is not int or max_payload_bytes < 1):
            raise ValueError("max_payload_bytes must be a whole number of 1 or more, or None for no limit")
        self._bridge = bridge
        self._prefix = topic_prefix
        self._stop_verbs = frozenset(stop_verbs)
        self._max_payload_bytes = max_payload_bytes
        self._lane = _Lane("hydra-bridge", max_queue)
        self._stop_lane = _Lane("hydra-bridge-stop", None)
        self._oversized = 0

    def on_message(self, client: object, userdata: object, message: object) -> None:
        if bool(getattr(message, "retain", False)):
            return  # a replay by the broker, never a request
        topic = message.topic  # type: ignore[attr-defined]
        suffix = topic[len(self._prefix) :] if topic.startswith(self._prefix) else ""
        is_stop = suffix in self._stop_verbs
        payload = bytes(message.payload)  # type: ignore[attr-defined]
        if not is_stop and self._max_payload_bytes is not None and len(payload) > self._max_payload_bytes:
            self._oversized += 1
            _LOG.warning("refused %s: payload of %d bytes is over the limit of %d", topic, len(payload), self._max_payload_bytes)
            return
        (self._stop_lane if is_stop else self._lane).submit(self._handle, client, topic, payload)

    def stats(self) -> dict[str, int]:
        """Counters since the start: commands dropped from a full queue, payloads refused as oversized, and commands waiting now."""
        return {"dropped": self._lane.dropped, "oversized": self._oversized, "queued": self._lane.waiting()}

    def _handle(self, client: object, topic: str, payload: bytes) -> None:
        try:
            for publish in self._bridge.handle_message(topic, payload, retained=False):
                client.publish(publish.topic, publish.payload, qos=getattr(publish, "qos", 0), retain=publish.retain)  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001 - one bad message never ends the loop
            _LOG.exception("could not answer %s", topic)

    def close(self, wait: bool = True) -> None:
        self._lane.shutdown(wait)
        self._stop_lane.shutdown(wait)


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
    connect_backoff_factor: float = 1.0,
    connect_max_delay_seconds: Optional[float] = None,
    connect_jitter: float = 0.0,
    reconnect_min_delay_seconds: float = 1,
    reconnect_max_delay_seconds: float = 30,
    mqtt_module: object = None,
    on_connected: Optional[Callable[[object], None]] = None,
) -> object:
    """Build the paho client of a bridge and connect it (the caller then runs `client.loop_forever()` or `loop_start()`).

    * the credentials and the TLS of the service's environment (`HYDRA_MQTT_*`), unless `username` is given explicitly;
    * the Last Will: the retained `availability` topic turns "offline" if the link dies;
    * after every (re)connect that the broker accepted: subscribe to `<prefix>cmd/#`, publish "online" on `<prefix>availability` (retained, QoS 1), then `on_connected(client)`;
    * a refused login is left to paho, which reports it and retries on its own;
    * `reconnect_min_delay_seconds` / `reconnect_max_delay_seconds` (1 and 30) bound paho's own exponential reconnect delay after the link drops;
    * `connect_backoff_factor`, `connect_max_delay_seconds` and `connect_jitter` shape the wait between the retries of the FIRST connect (see `connect_with_retry`; by default
      it is the fixed `connect_retry_delay_seconds`).

    `mqtt_module` is `paho.mqtt.client` unless a test passes a fake.
    """
    if password is not None and username is None:
        raise ValueError("password was given without a username - MQTT credentials need both")
    if not 0 < reconnect_min_delay_seconds <= reconnect_max_delay_seconds:
        raise ValueError("the reconnect delays need 0 < min <= max")
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
    client.reconnect_delay_set(min_delay=reconnect_min_delay_seconds, max_delay=reconnect_max_delay_seconds)
    client.will_set(availability, "offline", qos=1, retain=True)
    client.on_connect = on_connect
    client.on_message = dispatcher.on_message
    connect_with_retry(
        lambda: client.connect(host, port),
        max_attempts=max_connect_attempts,
        retry_delay_seconds=connect_retry_delay_seconds,
        backoff_factor=connect_backoff_factor,
        max_delay_seconds=connect_max_delay_seconds,
        jitter=connect_jitter,
    )
    return client
