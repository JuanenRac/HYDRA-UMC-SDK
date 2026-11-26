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
spaces and ASCII escapes. The message is retained, so it carries no expiry. Without a key file everything behaves as before.

**The mark on disk.** With a key file the guard also keeps on disk the `issued_at_ms` of the newest signed announcement it accepted and of the signed `READY` in
force, so an old signed `READY` published again after a restart ends nothing. The file is `HYDRA_UMC_<name>_GLOBAL_STOP_STATE_FILE` (`ready_state_file`); without
one it is in `$STATE_DIRECTORY` (systemd), else in `$XDG_STATE_HOME/hydra-umc` or `~/.local/state/hydra-umc`. It is written atomically and carries a MAC made with
the key. Everything doubtful leaves the machine still:

* a file that cannot be read, is damaged, altered, or made for another topic or key: nothing moves, whatever the broker says, until an operator removes the file and
  restarts the bridge;
* a file that cannot be written: a `READY` is not accepted (a `SAFE_STOP` is obeyed as always);
* a file that says the bridge was stopped: it starts stopped.

A file that does not exist is a first start. In a container keep it on a volume, or the memory does not survive the container.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import tempfile
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

MARK_DOMAIN = b"hydra-umc-global-stop-mark-v1"
_MARK_FIELDS = {"version", "topic", "newest_signed_ms", "ready_signed_ms", "mac"}
_MAX_MARK_BYTES = 4096

_TRUE = {"1", "true", "yes", "on"}


def default_state_file(topic: str, key_file: str) -> str:
    """Where the mark is kept when no file is named: one per topic and key file, in the state folder of the service or of its user."""
    base = os.environ.get("STATE_DIRECTORY", "").split(os.pathsep if os.name != "posix" else ":")[0].strip()
    if not base:
        home = os.environ.get("XDG_STATE_HOME", "").strip() or os.path.join(os.path.expanduser("~"), ".local", "state")
        base = os.path.join(home, "hydra-umc")
    name = hashlib.sha256(f"{topic}\n{os.path.abspath(key_file)}".encode("utf-8", "surrogateescape")).hexdigest()[:16]
    return os.path.join(base, f"global-stop-{name}.json")


def _mark_mac(body: Mapping[str, object], key: bytes) -> str:
    raw = json.dumps({name: value for name, value in body.items() if name != "mac"}, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hmac.new(key, MARK_DOMAIN + b"\n" + raw, hashlib.sha256).hexdigest()


def _read_mark(path: str, topic: str, key: bytes) -> tuple[int, int | None] | None:
    """(newest signed, signed READY in force or None); None when there is no file. ValueError for anything that cannot be trusted."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read(_MAX_MARK_BYTES + 1)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise ValueError(f"cannot be read ({type(error).__name__})") from error
    try:
        body = json.loads(raw) if len(raw) <= _MAX_MARK_BYTES else None
    except (ValueError, RecursionError) as error:
        raise ValueError("is damaged") from error
    if not isinstance(body, dict) or set(body) != _MARK_FIELDS or body["version"] != 1:
        raise ValueError("is damaged")
    mac = body["mac"]
    if not isinstance(mac, str) or not _SIGNATURE.fullmatch(mac) or not hmac.compare_digest(_mark_mac(body, key), mac):
        raise ValueError("was altered or made with another key")
    newest, ready = body["newest_signed_ms"], body["ready_signed_ms"]
    if body["topic"] != topic:
        raise ValueError("was made for another topic")
    if type(newest) is not int or newest < -1 or not (ready is None or (type(ready) is int and 0 <= ready <= newest)):
        raise ValueError("is damaged")
    return newest, ready


def _write_mark(path: str, topic: str, key: bytes, newest: int, ready: int | None) -> None:
    """Writes the mark so that a power cut leaves the old file or the new one, never half of one. OSError when it cannot."""
    body: dict[str, object] = {"version": 1, "topic": topic, "newest_signed_ms": newest, "ready_signed_ms": ready}
    body["mac"] = _mark_mac(body, key)
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, mode=0o700, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".global-stop-", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(json.dumps(body, sort_keys=True).encode("ascii") + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)
    if os.name == "posix":
        directory = os.open(folder, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)


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
    signed `READY` ends a stop, and `ready_state_file` names the file of the mark that survives a restart (a default one without it)."""

    enabled: bool = False
    topic: str = DEFAULT_TOPIC
    strict: bool = False
    ready_key_file: str | None = None
    ready_state_file: str | None = None

    def __post_init__(self) -> None:
        topic = self.topic
        if not isinstance(topic, str) or not topic or topic.startswith("/") or topic.endswith("/") or "+" in topic or "#" in topic or "\x00" in topic:
            raise ValueError("the global stop topic must be a plain MQTT topic without wildcards")


def settings_from_environment(name: str) -> GlobalStopSettings:
    """`HYDRA_UMC_<name>_GLOBAL_STOP` (1 switches it on), `..._GLOBAL_STOP_TOPIC`, `..._GLOBAL_STOP_STRICT` (1 also refuses before the first message) and
    `..._GLOBAL_STOP_KEY_FILE` (only a `READY` signed with the key of that file ends a stop) and `..._GLOBAL_STOP_STATE_FILE` (the mark on disk)."""
    base = f"HYDRA_UMC_{name}_GLOBAL_STOP"
    enabled = os.environ.get(base, "").strip().lower() in _TRUE
    topic = os.environ.get(f"{base}_TOPIC", "").strip() or DEFAULT_TOPIC
    strict = os.environ.get(f"{base}_STRICT", "").strip().lower() in _TRUE
    key_file = os.environ.get(f"{base}_KEY_FILE", "").strip() or None
    state_file = os.environ.get(f"{base}_STATE_FILE", "").strip() or None
    return GlobalStopSettings(enabled, topic, strict, key_file, state_file)


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
        self._restored_ready: int | None = None  # the signed READY that was in force before a restart: the same one may be delivered again
        self._saved: tuple[int, int | None] | None = None  # what the file holds
        self._broken = ""  # why the file of the mark cannot be trusted (nothing moves then)
        self._unsaved = False  # a READY was refused because the mark could not be written
        self._state_file = self.settings.ready_state_file
        if self._state_file is None and key is not None and self.settings.ready_key_file:
            self._state_file = default_state_file(self.settings.topic, self.settings.ready_key_file)
        if key is not None and self._state_file:
            self._restore(self._state_file, key)

    def _restore(self, path: str, key: bytes) -> None:
        try:
            mark = _read_mark(path, self.settings.topic, key)
        except ValueError as error:
            self._broken = f"the memory of the last signed release ({path}) {error}"
            self._state = STATE_UNVERIFIED
            return
        if mark is None:
            return
        self._saved = mark
        self._newest_signed, self._restored_ready = mark
        if self._restored_ready is None:
            self._state = STATE_UNVERIFIED  # it was stopped when it last knew: only a newer signed READY ends that

    def _remember(self, newest: int, ready: int | None) -> bool:
        """Writes the mark when it changed; False when it could not."""
        if self._key is None or not self._state_file or self._saved == (newest, ready):
            return True
        try:
            _write_mark(self._state_file, self.settings.topic, self._key, newest, ready)
        except OSError:
            self._saved = None
            return False
        self._saved = (newest, ready)
        return True

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
            if self._broken:  # a stop is still recorded; nothing ends it until the file is dealt with
                if state != STATE_READY:
                    self._state = state
                return self._state
            if self._key is not None and state == STATE_READY:
                again = (self._state == STATE_READY and signed_at == self._ready_signed) or signed_at == self._restored_ready
                fresh = signed_at is not None and (signed_at > self._newest_signed or again)
                if not fresh:
                    # it ends nothing: a stop stays a stop, a release in force stays; with nothing known yet the bridge stays still
                    if self._state not in (STATE_READY, STATE_SAFE_STOP):
                        self._state = STATE_UNVERIFIED
                    return self._state
            newest = self._newest_signed if signed_at is None else max(self._newest_signed, signed_at)
            ready = signed_at if state == STATE_READY else None
            saved = self._remember(newest, ready)
            self._unsaved = not saved and state == STATE_READY
            if self._unsaved:  # a release that cannot be remembered is not believed
                if self._state not in (STATE_READY, STATE_SAFE_STOP):
                    self._state = STATE_UNVERIFIED
                return self._state
            self._ready_signed, self._restored_ready = ready, None
            self._newest_signed = newest
            self._state = state
        return state

    def blocks(self) -> bool:
        """True when a command that moves something has to be refused now."""
        if not self.settings.enabled:
            return False
        with self._lock:
            state, broken = self._state, self._broken
        if broken:
            return True
        if state == STATE_READY:
            return False
        if state == STATE_UNKNOWN:
            return self.settings.strict
        return True

    def reason(self) -> str:
        if self._broken:
            return f"{self._broken} - nothing moves until an operator removes the file and restarts the bridge"
        if self._unsaved:
            return f"the signed release could not be remembered in {self._state_file} - nothing moves until the file can be written and the server announces READY again"
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
