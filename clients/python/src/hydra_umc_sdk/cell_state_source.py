# =============================================================================
# HYDRA-UMC-SDK - Where a bridge reads the state of its cell (the one copy every bridge uses)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The state of the cell a bridge acts in: `READY`, `INHIBITED`, `FAULT` or `SAFE_STOP`, read from one of three sources.

* `fixed`: a word given in the configuration (what a bench without a safety service uses).
* `file`: the first word of a small text file somebody else keeps up to date; a file that is missing, unreadable, empty, with another word or older than
  `max_age_seconds` reads as `SAFE_STOP`.
* `safety_zones`: the verdict of the safety zones service, a `SafetyZonesState` JSON read from a file or from an HTTP address. It is accepted only when it is
  signed with the key the bridge holds (HMAC-SHA256 with a shared key, or Ed25519 with the public key), its timestamp is fresh and its counter does not go
  back; anything else reads as `SAFE_STOP`. Only the signed state counts, never the counts or the breaches next to it.

The reader never raises and never invents `READY`: whatever cannot be trusted is `SAFE_STOP`. `describe()` says which source answered and why, so a bridge can put
`cell_source` in its answers. A bridge that does not configure a source keeps the behaviour it had.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
import time
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .safety_zones_state import validate_safety_zones_state
from .validation import ContractValidationError

STATES: tuple[str, ...] = ("READY", "INHIBITED", "FAULT", "SAFE_STOP")
SOURCES: tuple[str, ...] = ("fixed", "file", "safety_zones")
ALGORITHM_HMAC = "HMAC-SHA256"
ALGORITHM_ED25519 = "Ed25519"
DOMAIN = b"hydra-umc-safety-state-v1\n"
MIN_KEY_CHARS = 32
DEFAULT_MAX_AGE_SECONDS = 5.0
MAX_BYTES = 65536
HTTP_TIMEOUT_SECONDS = 2.0
_FAIL = "SAFE_STOP"


class CellStateSourceError(ValueError):
    """The configuration of the source is not usable (raised when it is built, never when it is read)."""


@dataclass(frozen=True)
class CellStateSourceConfig:
    """Which source and how it is trusted. The key files are read when the source is built and never printed."""

    source: str = "fixed"
    value: str = "READY"
    path: str | None = None
    url: str | None = None
    max_age_seconds: float = DEFAULT_MAX_AGE_SECONDS
    key_file: str | None = None
    public_key_file: str | None = None
    algorithm: str = ALGORITHM_HMAC
    key_id: str | None = None

    def __post_init__(self) -> None:
        if self.source not in SOURCES:
            raise CellStateSourceError(f"the cell state source must be one of {', '.join(SOURCES)}")
        if self.value not in STATES:
            raise CellStateSourceError(f"the fixed cell state must be one of {', '.join(STATES)}")
        if not isinstance(self.max_age_seconds, (int, float)) or isinstance(self.max_age_seconds, bool) or not 0 < self.max_age_seconds <= 86400:
            raise CellStateSourceError("max_age_seconds must be a number above 0 and at most 86400")
        if self.algorithm not in (ALGORITHM_HMAC, ALGORITHM_ED25519):
            raise CellStateSourceError("the algorithm must be HMAC-SHA256 or Ed25519")
        if self.source == "file" and not self.path:
            raise CellStateSourceError("the file source needs a path")
        if self.source == "safety_zones":
            if bool(self.path) == bool(self.url):
                raise CellStateSourceError("the safety zones source needs a path or a url, and not both")
            if self.url is not None and not self.url.startswith(("http://", "https://")):
                raise CellStateSourceError("the url must start with http:// or https://")
            if self.algorithm == ALGORITHM_HMAC and not self.key_file:
                raise CellStateSourceError("the safety zones source needs a key file (an unsigned verdict is never accepted)")
            if self.algorithm == ALGORITHM_ED25519 and not self.public_key_file:
                raise CellStateSourceError("the safety zones source with Ed25519 needs the public key file")


def config_from_environment(name: str) -> CellStateSourceConfig | None:
    """`HYDRA_UMC_<name>_CELL_STATE_SOURCE` (`fixed`, `file` or `safety_zones`) with `..._VALUE`, `..._PATH`, `..._URL`, `..._MAX_AGE`, `..._KEY_FILE`,
    `..._PUBLIC_KEY_FILE`, `..._ALGORITHM` and `..._KEY_ID`. None when the source is not set: the bridge keeps its own behaviour."""
    base = f"HYDRA_UMC_{name}_CELL_STATE"

    def text(suffix: str) -> str:
        return os.environ.get(f"{base}_{suffix}", "").strip()

    source = text("SOURCE").lower()
    if not source:
        return None
    try:
        max_age = float(text("MAX_AGE")) if text("MAX_AGE") else DEFAULT_MAX_AGE_SECONDS
    except ValueError as error:
        raise CellStateSourceError("max_age must be a number") from error
    return CellStateSourceConfig(
        source=source,
        value=text("VALUE").upper() or "READY",
        path=text("PATH") or None,
        url=text("URL") or None,
        max_age_seconds=max_age,
        key_file=text("KEY_FILE") or None,
        public_key_file=text("PUBLIC_KEY_FILE") or None,
        algorithm=text("ALGORITHM") or ALGORITHM_HMAC,
        key_id=text("KEY_ID") or None,
    )


def fresh_text(path: str, max_age_seconds: float, clock: Callable[[], float] = time.time) -> str | None:
    """The first word of a small file written by someone else; None when it is missing, unreadable, empty or older (or newer) than `max_age_seconds`."""
    try:
        age = clock() - os.stat(path).st_mtime
        if age > max_age_seconds or age < -max_age_seconds:
            return None
        with open(path, encoding="utf-8") as handle:
            words = handle.read(256).split()
    except (OSError, UnicodeDecodeError):
        return None
    return words[0] if words else None


def _message(state: dict[str, Any], counter: int, key_id: str) -> bytes:
    body = {"state": state, "counter": counter, "key_id": key_id}
    return DOMAIN + json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def _age_ms(state: dict[str, Any], now_ms: int) -> float | None:
    stamp = state.get("timestamp_utc")
    if not isinstance(stamp, str):
        return None
    try:
        when = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return now_ms - when.timestamp() * 1000.0


def _load_key(path: str) -> bytes:
    try:
        text = Path(path).read_text(encoding="utf-8").strip()
    except OSError as error:
        raise CellStateSourceError(f"the key file cannot be read: {error.strerror or type(error).__name__}") from error
    if len(text) < MIN_KEY_CHARS:
        raise CellStateSourceError(f"the key file must hold at least {MIN_KEY_CHARS} characters")
    return text.encode("utf-8")


def _load_public_key(path: str) -> object:
    try:
        from cryptography.hazmat.primitives import serialization  # noqa: PLC0415
        from cryptography.hazmat.primitives.asymmetric import ed25519  # noqa: PLC0415
    except ImportError as error:
        raise CellStateSourceError("Ed25519 needs the cryptography package") from error
    try:
        key = serialization.load_pem_public_key(Path(path).read_bytes())
    except (OSError, ValueError, TypeError) as error:
        raise CellStateSourceError("the public key file cannot be used") from error
    if not isinstance(key, ed25519.Ed25519PublicKey):
        raise CellStateSourceError("the public key file does not hold an Ed25519 key")
    return key


def _http_fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT_SECONDS) as response:  # noqa: S310 - the scheme is checked in the configuration
        return response.read(MAX_BYTES + 1)


class CellStateSource:
    """The current state of the cell. Call it (or `read()`) for the word; `describe()` for the source, the word and the reason."""

    def __init__(
        self,
        config: CellStateSourceConfig,
        *,
        clock: Callable[[], float] = time.time,
        wall_clock_ms: Callable[[], int] | None = None,
        fetch: Callable[[str], bytes] | None = None,
    ) -> None:
        self.config = config
        self._clock = clock
        self._wall_ms = wall_clock_ms or (lambda: int(clock() * 1000))
        self._fetch = fetch or _http_fetch
        self._key: bytes | None = None
        self._public_key: object | None = None
        if config.source == "safety_zones":
            if config.algorithm == ALGORITHM_HMAC:
                self._key = _load_key(config.key_file or "")
            else:
                self._public_key = _load_public_key(config.public_key_file or "")
        self._lock = threading.Lock()
        self._last_counter = 0
        self._last: tuple[str, str] = (_FAIL, "not read yet")

    def __call__(self) -> str:
        return self.read()

    def read(self) -> str:
        """The state to act on: one of `STATES`, `SAFE_STOP` whenever the source cannot be trusted. Never raises."""
        try:
            state, reason = self._read()
        except Exception as error:  # noqa: BLE001 - a reader that raises would stop the bridge; unreadable means SAFE_STOP
            state, reason = _FAIL, f"the source failed: {type(error).__name__}"
        if state not in STATES:
            state, reason = _FAIL, "the source answered a word that is not a cell state"
        with self._lock:
            self._last = (state, reason)
        return state

    def describe(self) -> dict[str, str]:
        """`{"cell_source": ..., "state": ..., "reason": ...}` for the last reading (read once first when none was made)."""
        with self._lock:
            made = self._last[1] != "not read yet"
        if not made:
            self.read()
        with self._lock:
            state, reason = self._last
        return {"cell_source": self.config.source, "state": state, "reason": reason}

    def _read(self) -> tuple[str, str]:
        config = self.config
        if config.source == "fixed":
            return config.value, "configured"
        if config.source == "file":
            word = fresh_text(config.path or "", config.max_age_seconds, self._clock)
            if word is None:
                return _FAIL, "the file is missing, empty or not fresh"
            if word not in STATES:
                return _FAIL, "the file holds a word that is not a cell state"
            return word, "file"
        return self._read_safety_zones()

    def _read_safety_zones(self) -> tuple[str, str]:
        config = self.config
        try:
            if config.url is not None:
                raw = self._fetch(config.url)
            else:
                with open(config.path or "", "rb") as handle:
                    raw = handle.read(MAX_BYTES + 1)
        except (OSError, ValueError):
            return _FAIL, "the verdict cannot be read"
        if len(raw) > MAX_BYTES:
            return _FAIL, "the verdict is too large"
        try:
            payload = json.loads(raw)
            validate_safety_zones_state(payload)
        except (ValueError, ContractValidationError):
            return _FAIL, "the verdict is not a SafetyZonesState"
        reason = self._verify(payload)
        if reason:
            return _FAIL, reason
        return str(payload["sdkSafetyState"]["state"]), "signed verdict"

    def _verify(self, payload: dict[str, Any]) -> str:
        """Why the verdict cannot be trusted, or an empty text when it can (and its counter is then remembered)."""
        config = self.config
        state, signature = payload["sdkSafetyState"], payload.get("sdkSafetyStateSignature")
        if not isinstance(signature, dict):
            return "the verdict is not signed"
        if signature["alg"] != config.algorithm:
            return f"the verdict is signed with {signature['alg']}, this bridge accepts {config.algorithm}"
        if config.key_id is not None and signature["key_id"] != config.key_id:
            return "the signature was made with another key id"
        counter = signature["counter"]
        if counter < 1:
            return "the signature is malformed"
        message = _message(state, counter, signature["key_id"])
        if config.algorithm == ALGORITHM_HMAC:
            expected = hmac.new(self._key or b"", message, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected, signature["sig"]):
                return "the signature does not match"
        else:
            try:
                self._public_key.verify(bytes.fromhex(signature["sig"]), message)  # type: ignore[attr-defined]
            except Exception:  # noqa: BLE001 - InvalidSignature or a key of the wrong kind: both are "does not match"
                return "the signature does not match"
        age = _age_ms(state, self._wall_ms())
        if age is None:
            return "the verdict has no readable timestamp"
        limit = config.max_age_seconds * 1000.0
        if age > limit or age < -limit:
            return f"the verdict is {int(age)} ms old (limit {int(limit)} ms)"
        with self._lock:
            if counter < self._last_counter:
                return "the verdict is older than one already seen (replay)"
            self._last_counter = counter
        return ""
