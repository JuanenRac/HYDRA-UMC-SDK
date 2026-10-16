# =============================================================================
# HYDRA-UMC-SDK - Job intake for bridges: idempotency store and retained-message guard
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""What every bridge has to do before it looks at a job that arrived from the broker, once, here instead of eight times.

docs/BRIDGE_CONTRACT.md asks bridges to ignore retained messages (a retained command is replayed by the broker at every reconnect and would start a physical action again) and
to persist or deduplicate the `idempotency_key` (QoS 1 may deliver a command twice, and a client may retry). Both are small and easy to get wrong, so the SDK carries them:

* `IdempotencyStore`: remembers the keys it has seen for a while (SQLite when it is given a file, so that a restart does not forget; in memory otherwise), and the result a
  bridge stored for each key, so that a repeated request can be answered with the same answer instead of being run again.
* `JobIntake`: takes the raw payload and the retained flag of an MQTT message and says whether the bridge should look at the job: not a retained one, not a malformed one, not
  one that was already handled.

Pure standard library. Neither piece decides anything about safety: the gate (`evaluate_job`, with the state the bridge OBSERVES) still does.
"""

from __future__ import annotations

import sqlite3
import threading
import time
from dataclasses import dataclass
from typing import Callable, Mapping

from .bridge_contract import BridgeError, BridgeJob, job_from_dict

DEFAULT_TTL_SECONDS = 24 * 3600
DEFAULT_MAX_ENTRIES = 10_000
MAX_RESULT_CHARS = 2_000


class IdempotencyStore:
    """The idempotency keys a bridge has already handled, kept for `ttl_seconds` (and at most `max_entries`, the oldest forgotten first).

    `path=None` keeps them in memory (they are lost when the process ends); a file name keeps them in SQLite, so a restarted bridge still refuses a command it ran before.
    `claim()` is the whole interface a bridge needs: True the first time a key is seen, False after that, and it is atomic, so two threads cannot both win.
    """

    def __init__(self, path: str | None = None, *, ttl_seconds: float = DEFAULT_TTL_SECONDS, max_entries: int = DEFAULT_MAX_ENTRIES,
                 clock: Callable[[], float] = time.time) -> None:
        if ttl_seconds <= 0 or max_entries <= 0:
            raise ValueError("ttl_seconds and max_entries must be positive")
        self._ttl = float(ttl_seconds)
        self._max = int(max_entries)
        self._clock = clock
        self._lock = threading.Lock()
        self._db = sqlite3.connect(path or ":memory:", check_same_thread=False, isolation_level=None)
        self._db.execute("CREATE TABLE IF NOT EXISTS keys (k TEXT PRIMARY KEY, at REAL NOT NULL, result TEXT)")
        self._db.execute("CREATE INDEX IF NOT EXISTS keys_at ON keys (at)")

    def close(self) -> None:
        with self._lock:
            self._db.close()

    def claim(self, key: str) -> bool:
        """True when `key` has not been handled (it is recorded now), False when it has."""
        if not isinstance(key, str) or not key.strip():
            raise BridgeError("an idempotency key must be a non-empty string")
        now = self._clock()
        with self._lock:
            self._forget_old(now)
            cursor = self._db.execute("INSERT OR IGNORE INTO keys (k, at, result) VALUES (?, ?, NULL)", (key, now))
            return cursor.rowcount == 1

    def remember(self, key: str, result: str) -> None:
        """Stores the answer given for `key`, so that a repeat can be answered the same way. Only keys that were claimed keep one."""
        with self._lock:
            self._db.execute("UPDATE keys SET result = ? WHERE k = ?", (str(result)[:MAX_RESULT_CHARS], key))

    def recall(self, key: str) -> str | None:
        """The answer stored for `key`, or None (never seen, forgotten, or no answer stored)."""
        with self._lock:
            self._forget_old(self._clock())
            row = self._db.execute("SELECT result FROM keys WHERE k = ?", (key,)).fetchone()
        return row[0] if row else None

    def __len__(self) -> int:
        with self._lock:
            return int(self._db.execute("SELECT COUNT(*) FROM keys").fetchone()[0])

    def _forget_old(self, now: float) -> None:
        self._db.execute("DELETE FROM keys WHERE at < ?", (now - self._ttl,))
        count = int(self._db.execute("SELECT COUNT(*) FROM keys").fetchone()[0])
        if count >= self._max:
            self._db.execute("DELETE FROM keys WHERE k IN (SELECT k FROM keys ORDER BY at ASC LIMIT ?)", (count - self._max + 1,))


@dataclass(frozen=True)
class Intake:
    """What `JobIntake.accept` decided. `job` is set only when `accepted` is True."""

    accepted: bool
    reason: str
    job: BridgeJob | None = None
    duplicate: bool = False
    retained: bool = False


class JobIntake:
    """The first look at a job that arrived over a transport: a retained message is ignored, a malformed one is refused and a repeat is recognised.

    A bridge calls `accept(payload, retained=message.retain)` for every command message and goes on only when `accepted` is True. A duplicate comes back with `duplicate=True`
    and the stored answer is `store.recall(job.idempotency_key)`: the bridge can send that again instead of running the job a second time. Without a store nothing is
    deduplicated (the bridge says so by passing none), but retained and malformed messages are still stopped.
    """

    def __init__(self, store: IdempotencyStore | None = None) -> None:
        self._store = store

    def accept(self, payload: Mapping[str, object], *, retained: bool = False) -> Intake:
        if retained:
            return Intake(False, "a retained message is a replay by the broker, not a request: it is ignored", retained=True)
        try:
            job = job_from_dict(payload)
        except BridgeError as error:
            return Intake(False, f"malformed job: {error}")
        if self._store is not None and not self._store.claim(job.idempotency_key):
            return Intake(False, "this idempotency key was already handled", job=job, duplicate=True)
        return Intake(True, "accepted", job=job)
