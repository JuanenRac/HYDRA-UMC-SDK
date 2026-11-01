# =============================================================================
# HYDRA-UMC-SDK - Signed, expiring commands for the command topics of a bridge
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Signed commands with an expiry: a message on a `cmd/job` topic that proves who sent it and that says how long it may be acted on.

Without this, anyone who may publish on a command topic can make a bridge act, and an old message that the network delivers late is carried out as if it were new.
A signed command carries three more fields next to the job:

* `issued_at_ms`: when the sender made it, in milliseconds since the epoch;
* `expires_in_ms`: how long after that the bridge may still act on it;
* `signature`: the HMAC-SHA256, in 64 lowercase hexadecimal digits, of the topic and of everything else in the payload, made with a key that only the sender and the
  bridge know (one key per bridge, kept in a file that only the service can read).

The bytes that are signed are `hydra-umc-cmd-v1`, a newline, the topic, a newline and the payload without `signature` written as JSON with sorted keys, no spaces and
ASCII escapes. The job of a bridge holds strings, booleans and whole numbers only, so every language writes the same bytes.

It is off unless the service switches it on (`HYDRA_UMC_<NAME>_SIGNED_COMMANDS=yes`): a bridge that is not told to ask for signatures behaves exactly as before. When it is
on, a command that is unsigned, signed with another key, altered after it was signed, expired, issued in the future (a clock that is off by more than the allowed skew),
or that asks to stay valid longer than the largest expiry the bridge accepts, is refused, and a missing or unreadable key stops the start of the service instead of
leaving the bridge open. Pure standard library.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import time
from dataclasses import dataclass
from typing import Callable, Mapping, Optional

SIGNING_FIELDS = ("issued_at_ms", "expires_in_ms", "signature")
DOMAIN = b"hydra-umc-cmd-v1"
MIN_KEY_CHARS = 32
DEFAULT_MAX_CLOCK_SKEW_MS = 5_000
DEFAULT_MAX_EXPIRES_IN_MS = 300_000
DEFAULT_EXPIRES_IN_MS = 30_000
_SIGNATURE = re.compile(r"[0-9a-f]{64}")
_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"", "0", "false", "no", "off"}


class CommandSigningError(ValueError):
    """The signing settings or the key cannot be used."""


@dataclass(frozen=True)
class SignedCommandSettings:
    """What a bridge asks of its commands. `enabled=False` (the default) asks nothing."""

    enabled: bool = False
    key_file: Optional[str] = None
    max_clock_skew_ms: int = DEFAULT_MAX_CLOCK_SKEW_MS
    max_expires_in_ms: int = DEFAULT_MAX_EXPIRES_IN_MS

    def __post_init__(self) -> None:
        for name in ("max_clock_skew_ms", "max_expires_in_ms"):
            value = getattr(self, name)
            if type(value) is not int or value < 0 or (name == "max_expires_in_ms" and value == 0):
                raise CommandSigningError(f"{name} must be a whole number of milliseconds (the expiry above zero)")
        if self.enabled and not self.key_file:
            raise CommandSigningError("signed commands are on but no key file is configured")


def settings_from_environment(name: str, environ: Optional[Mapping[str, str]] = None) -> SignedCommandSettings:
    """`HYDRA_UMC_<name>_SIGNED_COMMANDS` (yes switches it on; off by default and then nothing else is read) with `..._COMMAND_KEY_FILE`, `..._COMMAND_MAX_SKEW_MS`
    and `..._COMMAND_MAX_EXPIRES_MS`. A value that is neither a clear yes nor a clear no raises `CommandSigningError` naming the variable: a misspelt switch must not
    be taken for off."""
    env = os.environ if environ is None else environ
    base = f"HYDRA_UMC_{name}_"
    raw = env.get(base + "SIGNED_COMMANDS", "").strip().lower()
    if raw in _FALSE:
        return SignedCommandSettings()
    if raw not in _TRUE:
        raise CommandSigningError(f"{base}SIGNED_COMMANDS must be yes or no, not {raw!r}")

    def whole(suffix: str, default: int) -> int:
        text = env.get(base + suffix, "").strip()
        if text == "":
            return default
        try:
            return int(text)
        except ValueError as error:
            raise CommandSigningError(f"{base}{suffix} must be a whole number, not {text!r}") from error

    return SignedCommandSettings(
        enabled=True,
        key_file=env.get(base + "COMMAND_KEY_FILE", "").strip() or None,
        max_clock_skew_ms=whole("COMMAND_MAX_SKEW_MS", DEFAULT_MAX_CLOCK_SKEW_MS),
        max_expires_in_ms=whole("COMMAND_MAX_EXPIRES_MS", DEFAULT_MAX_EXPIRES_IN_MS),
    )


def load_key(path: str) -> bytes:
    """The key in `path`: one line of at least 32 characters (for example 64 hexadecimal digits from `openssl rand -hex 32`). The key is never put in a message of an error.

    On a system with POSIX permissions a file that the group or the others can read is refused: the key is only worth something while it is secret.
    """
    try:
        info = os.stat(path)
        with open(path, "rb") as handle:
            raw = handle.read(4096)
    except OSError as error:
        raise CommandSigningError(f"the command key file cannot be read: {type(error).__name__}") from error
    if os.name == "posix" and info.st_mode & 0o077:
        raise CommandSigningError("the command key file must not be readable by the group or by others (mode 600)")
    key = raw.strip()
    if len(key) < MIN_KEY_CHARS:
        raise CommandSigningError(f"the command key must have at least {MIN_KEY_CHARS} characters")
    return key


def _canonical_body(payload: Mapping[str, object]) -> bytes:
    body = {name: value for name, value in payload.items() if name != "signature"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def _signature(topic: str, payload: Mapping[str, object], key: bytes) -> str:
    message = DOMAIN + b"\n" + topic.encode("utf-8") + b"\n" + _canonical_body(payload)
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def sign_command(
    topic: str,
    payload: Mapping[str, object],
    key: bytes,
    *,
    now_ms: Optional[int] = None,
    expires_in_ms: int = DEFAULT_EXPIRES_IN_MS,
) -> dict[str, object]:
    """A copy of `payload` with `issued_at_ms`, `expires_in_ms` and `signature` added for `topic`. Fields that were already there are replaced."""
    if not isinstance(topic, str) or not topic:
        raise CommandSigningError("a command is signed for a topic")
    if len(key) < MIN_KEY_CHARS:
        raise CommandSigningError(f"the command key must have at least {MIN_KEY_CHARS} characters")
    if type(expires_in_ms) is not int or expires_in_ms <= 0:
        raise CommandSigningError("expires_in_ms must be a whole number of milliseconds above zero")
    signed = {name: value for name, value in payload.items() if name not in SIGNING_FIELDS}
    signed["issued_at_ms"] = int(time.time() * 1000) if now_ms is None else now_ms
    signed["expires_in_ms"] = expires_in_ms
    signed["signature"] = _signature(topic, signed, key)
    return signed


@dataclass(frozen=True)
class CommandVerdict:
    """Whether a command may be acted on, and why not."""

    ok: bool
    reason: str


def verify_command(
    topic: str,
    payload: Mapping[str, object],
    key: bytes,
    *,
    now_ms: int,
    max_clock_skew_ms: int = DEFAULT_MAX_CLOCK_SKEW_MS,
    max_expires_in_ms: int = DEFAULT_MAX_EXPIRES_IN_MS,
) -> CommandVerdict:
    """Checks the signature first, then the time. Never raises for a bad command; the verdict says why it is refused."""
    if not isinstance(payload, Mapping):
        return CommandVerdict(False, "the command is not a JSON object")
    missing = [name for name in SIGNING_FIELDS if name not in payload]
    if missing:
        return CommandVerdict(False, f"the command is not signed (missing {', '.join(missing)})")
    issued, expires, signature = payload["issued_at_ms"], payload["expires_in_ms"], payload["signature"]
    if type(issued) is not int or issued < 0 or type(expires) is not int or expires <= 0:
        return CommandVerdict(False, "issued_at_ms and expires_in_ms must be whole numbers of milliseconds")
    if not isinstance(signature, str) or not _SIGNATURE.fullmatch(signature):
        return CommandVerdict(False, "the signature must be 64 lowercase hexadecimal digits")
    try:
        expected = _signature(topic, payload, key)
    except (TypeError, ValueError):
        return CommandVerdict(False, "the command cannot be written the way it was signed")
    if not hmac.compare_digest(expected, signature):
        return CommandVerdict(False, "the signature does not match: wrong key, another topic or an altered command")
    if expires > max_expires_in_ms:
        return CommandVerdict(False, f"the command asks to stay valid for {expires} ms; this bridge accepts at most {max_expires_in_ms} ms")
    if issued > now_ms + max_clock_skew_ms:
        return CommandVerdict(False, "the command was issued in the future: the clock of the sender is off")
    if now_ms > issued + expires:
        return CommandVerdict(False, "the command has expired")
    return CommandVerdict(True, "signed and current")


class CommandVerifier:
    """The settings of a bridge and its key, ready to judge a command. With `enabled` false every command passes (nothing is asked), and no key is read."""

    def __init__(self, settings: SignedCommandSettings, *, key: Optional[bytes] = None, clock: Callable[[], float] = time.time) -> None:
        self.settings = settings
        self._clock = clock
        self._key: Optional[bytes] = None
        if settings.enabled:
            self._key = key if key is not None else load_key(settings.key_file or "")
            if len(self._key) < MIN_KEY_CHARS:
                raise CommandSigningError(f"the command key must have at least {MIN_KEY_CHARS} characters")

    @classmethod
    def from_environment(cls, name: str, environ: Optional[Mapping[str, str]] = None, *, clock: Callable[[], float] = time.time) -> "CommandVerifier":
        """The verifier of the bridge `name` from its environment; raises `CommandSigningError` at the start when the switch is on and the key is unusable."""
        return cls(settings_from_environment(name, environ), clock=clock)

    @property
    def enabled(self) -> bool:
        return self.settings.enabled

    def check(self, topic: str, payload: Mapping[str, object]) -> CommandVerdict:
        if not self.settings.enabled or self._key is None:
            return CommandVerdict(True, "signed commands are off")
        return verify_command(
            topic,
            payload,
            self._key,
            now_ms=int(self._clock() * 1000),
            max_clock_skew_ms=self.settings.max_clock_skew_ms,
            max_expires_in_ms=self.settings.max_expires_in_ms,
        )
