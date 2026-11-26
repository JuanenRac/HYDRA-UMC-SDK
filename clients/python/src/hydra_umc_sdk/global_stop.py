# =============================================================================
# HYDRA-UMC-SDK - Obey the global stop of the server (the one copy every bridge uses)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The announcement of the global stop, as a bridge reads it: the one copy the CNC, laser, OpenPnP, 3D-printer, ROS 2 and AMR bridges share.

When the server stops every robot it can announce it on `<mqtt prefix>/safety/estop` (a retained `SafetyState` message: `SAFE_STOP`, later `READY`). This module
keeps the last state the bridge heard of that topic and says whether a command that moves something may run.

Off by default: with the switch off the bridge does not even subscribe to the topic and behaves exactly as before. With the switch on:

* while the last message says `SAFE_STOP` (or says anything else than `READY`, or cannot be read), every command that moves something is refused with a reason;
  stops and read-only requests keep working, and the refusal is an answer, never silence;
* only a message that says `READY` ends it;
* a bridge that never heard the topic is left as it was, unless `strict` is also on: then it refuses until the first message arrives (a bridge that must not move
  before it knows the state of the installation).

The state lives in this process: it is read again from the broker (the message is retained) after every reconnect.

**Signed announcements.** Anyone who may publish on the topic could say `READY` and end a stop. With a key file (`HYDRA_UMC_<name>_GLOBAL_STOP_KEY_FILE`, or
`ready_key_file`; the same key the server signs with, at least 32 characters, mode 600) a `SAFE_STOP` is still always obeyed, signed or not, but a `READY` ends a stop
only when it is signed with that key and newer than the last signed announcement the bridge accepted. The announcement carries `issued_at_ms` and `signature`, the
HMAC-SHA256 (64 lowercase hexadecimal digits) of `hydra-umc-global-stop-v1`, a newline, the topic, a newline and the other fields as JSON with sorted keys, no
spaces and ASCII escapes. The message is retained, so it carries no expiry; the memory of the newest one lives in the process, so a bridge that was just started
cannot tell an old signed `READY` that somebody published again from the current one. Without a key file everything behaves as before.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass

from .signed_commands import MIN_KEY_CHARS, CommandSigningError, load_key

DEFAULT_TOPIC = "hydra/swarm/safety/estop"
STATE_UNKNOWN = "UNKNOWN"
STATE_READY = "READY"
STATE_SAFE_STOP = "SAFE_STOP"
STATE_UNREADABLE = "UNREADABLE"
STATE_UNVERIFIED = "UNVERIFIED"  # a READY that is not signed as asked, heard before any state that could be trusted
SIGNING_DOMAIN = b"hydra-umc-global-stop-v1"
_SIGNATURE = re.compile(r"[0-9a-f]{64}")

_TRUE = {"1", "true", "yes", "on"}


def _signature(topic: str, payload: Mapping[str, object], key: bytes) -> str:
    body = {name: value for name, value in payload.items() if name != "signature"}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")
    return hmac.new(key, SIGNING_DOMAIN + b"\n" + topic.encode("utf-8") + b"\n" + raw, hashlib.sha256).hexdigest()


def sign_announcement(topic: str, payload: Mapping[str, object], key: bytes, *, now_ms: int | None = None) -> dict[str, object]:
    """A copy of `payload` with `issued_at_ms` and `signature` added for `topic`: what the layer that announces the stop publishes when it has a key."""
    if not isinstance(topic, str) or not topic:
        raise CommandSigningError("an announcement is signed for a topic")
    if len(key) < MIN_KEY_CHARS:
        raise CommandSigningError(f"the global stop key must have at least {MIN_KEY_CHARS} characters")
    signed = {name: value for name, value in payload.items() if name != "signature"}
    signed["issued_at_ms"] = int(time.time() * 1000) if now_ms is None else now_ms
    signed["signature"] = _signature(topic, signed, key)
    return signed


def verified_issued_at(topic: str, payload: Mapping[str, object], key: bytes) -> int | None:
    """`issued_at_ms` of an announcement signed with `key` for `topic`; None when it is unsigned, signed otherwise or altered."""
    issued, signature = payload.get("issued_at_ms"), payload.get("signature")
    if type(issued) is not int or issued < 0 or not isinstance(signature, str) or not _SIGNATURE.fullmatch(signature):
        return None
    try:
        expected = _signature(topic, payload, key)
    except (TypeError, ValueError):
        return None
    return issued if hmac.compare_digest(expected, signature) else None


@dataclass(frozen=True)
class GlobalStopSettings:
    """`enabled` is the switch (off by default); `topic` is where the server announces; `strict` also refuses before the first message; with `ready_key_file` only a
    signed `READY` ends a stop."""

    enabled: bool = False
    topic: str = DEFAULT_TOPIC
    strict: bool = False
    ready_key_file: str | None = None

    def __post_init__(self) -> None:
        topic = self.topic
        if not isinstance(topic, str) or not topic or topic.startswith("/") or topic.endswith("/") or "+" in topic or "#" in topic or "\x00" in topic:
            raise ValueError("the global stop topic must be a plain MQTT topic without wildcards")


def settings_from_environment(name: str) -> GlobalStopSettings:
    """`HYDRA_UMC_<name>_GLOBAL_STOP` (1 switches it on), `..._GLOBAL_STOP_TOPIC`, `..._GLOBAL_STOP_STRICT` (1 also refuses before the first message) and
    `..._GLOBAL_STOP_KEY_FILE` (only a `READY` signed with the key of that file ends a stop)."""
    base = f"HYDRA_UMC_{name}_GLOBAL_STOP"
    enabled = os.environ.get(base, "").strip().lower() in _TRUE
    topic = os.environ.get(f"{base}_TOPIC", "").strip() or DEFAULT_TOPIC
    strict = os.environ.get(f"{base}_STRICT", "").strip().lower() in _TRUE
    key_file = os.environ.get(f"{base}_KEY_FILE", "").strip() or None
    return GlobalStopSettings(enabled, topic, strict, key_file)


class GlobalStopGuard:
    """Thread safe: the network thread feeds `observe()`, the command lanes ask `blocks()`."""

    def __init__(self, settings: GlobalStopSettings | None = None, *, key: bytes | None = None) -> None:
        """`key` replaces the key of `ready_key_file`. A key file that cannot be used raises `CommandSigningError`: the bridge does not start believing it is
        protected."""
        self.settings = settings if settings is not None else GlobalStopSettings()
        if key is None and self.settings.ready_key_file:  # also with the switch off: a bridge may switch it on later
            key = load_key(self.settings.ready_key_file)
        if key is not None and len(key) < MIN_KEY_CHARS:
            raise CommandSigningError(f"the global stop key must have at least {MIN_KEY_CHARS} characters")
        self._key = key
        self._lock = threading.Lock()
        self._state = STATE_UNKNOWN
        self._newest_signed = -1  # issued_at_ms of the newest signed announcement accepted
        self._ready_signed: int | None = None  # issued_at_ms of the signed READY that is in force

    @classmethod
    def from_environment(cls, name: str) -> "GlobalStopGuard":
        return cls(settings_from_environment(name))

    @property
    def enabled(self) -> bool:
        return self.settings.enabled

    @property
    def topic(self) -> str:
        return self.settings.topic

    @property
    def state(self) -> str:
        with self._lock:
            return self._state

    def observe(self, payload: bytes) -> str:
        """One message of the announcement topic; returns the state it leaves the guard in. Anything but a clear `READY` is a stop; with a key, a `READY` counts only
        when it is signed and newer than the last signed announcement (or is the one already in force, delivered again)."""
        state = STATE_UNREADABLE
        try:
            body = json.loads(payload)
        except (ValueError, RecursionError):
            body = None
        if isinstance(body, dict):
            declared = body.get("state")
            if declared == STATE_READY:
                state = STATE_READY
            elif declared == STATE_SAFE_STOP:
                state = STATE_SAFE_STOP
        signed_at = None
        if self._key is not None and isinstance(body, dict):
            signed_at = verified_issued_at(self.settings.topic, body, self._key)
        with self._lock:
            if self._key is not None and state == STATE_READY:
                fresh = signed_at is not None and (signed_at > self._newest_signed or (self._state == STATE_READY and signed_at == self._ready_signed))
                if not fresh:
                    # it ends nothing: a stop stays a stop, a release in force stays; with nothing known yet the bridge stays still
                    if self._state not in (STATE_READY, STATE_SAFE_STOP):
                        self._state = STATE_UNVERIFIED
                    return self._state
                self._ready_signed = signed_at
            if signed_at is not None:
                self._newest_signed = max(self._newest_signed, signed_at)
            self._state = state
        return state

    def blocks(self) -> bool:
        """True when a command that moves something has to be refused now."""
        if not self.settings.enabled:
            return False
        with self._lock:
            state = self._state
        if state == STATE_READY:
            return False
        if state == STATE_UNKNOWN:
            return self.settings.strict
        return True

    def reason(self) -> str:
        state = self.state
        if state == STATE_UNKNOWN:
            return "the global stop state is not known yet - nothing moves until the server announces READY"
        if state == STATE_UNVERIFIED:
            return "the global stop release is not signed as this bridge asks - nothing moves until the server announces a signed READY"
        if state == STATE_UNREADABLE:
            return "the global stop announcement could not be read - nothing moves until the server announces READY"
        return "global stop active (SAFE_STOP) - nothing moves until the server announces READY"

    def blocks_job(self, payload: bytes) -> bool:
        """A job is refused while stopped, except an abort: it only ever stops things."""
        if not self.blocks():
            return False
        try:
            body = json.loads(payload)
        except (ValueError, RecursionError):
            return True
        phase = body.get("phase") if isinstance(body, dict) else None
        return not (isinstance(phase, str) and phase.strip().upper() == "ABORT")

    def blocks_assertion(self, payload: bytes, key: str) -> bool:
        """For a message that asserts or withdraws a line (`key` true/false): withdrawing is always allowed, asserting is refused while stopped."""
        if not self.blocks():
            return False
        try:
            body = json.loads(payload)
        except (ValueError, RecursionError):
            return True
        return not (isinstance(body, dict) and body.get(key) is False)

    def refusal(
        self,
        suffix: str,
        payload: bytes,
        *,
        moving: frozenset[str] = frozenset(),
        jobs: frozenset[str] = frozenset({"cmd/job"}),
        assertions: dict[str, str] | None = None,
    ) -> str | None:
        """The reason to refuse the command `suffix` (the topic below the prefix) now, or None when it may run: `moving` always refused while stopped, `jobs` unless they abort, `assertions` unless they withdraw."""
        if not self.settings.enabled:
            return None
        if suffix in moving and self.blocks():
            return self.reason()
        if suffix in jobs and self.blocks_job(payload):
            return self.reason()
        if assertions and suffix in assertions and self.blocks_assertion(payload, assertions[suffix]):
            return self.reason()
        return None


def follow_on_connect(guard: GlobalStopGuard):
    """The `on_connected` callback for `open_bridge_client`: subscribes to the announcement (QoS 1) after every (re)connect, so the retained state arrives at once; None when the switch is off."""
    if not guard.enabled:
        return None

    def on_connected(client: object) -> None:
        client.subscribe(guard.topic, qos=1)  # type: ignore[attr-defined]

    return on_connected


_PROCESS_WIDE: dict[str, GlobalStopGuard] = {}
_PROCESS_WIDE_LOCK = threading.Lock()


def process_wide_guard(name: str) -> GlobalStopGuard:
    """The one guard of this process for `HYDRA_UMC_<name>_GLOBAL_STOP`: the MQTT client feeds it and the publisher asks it, without the caller passing it around."""
    with _PROCESS_WIDE_LOCK:
        guard = _PROCESS_WIDE.get(name)
        if guard is None:
            guard = _PROCESS_WIDE[name] = GlobalStopGuard.from_environment(name)
        return guard
