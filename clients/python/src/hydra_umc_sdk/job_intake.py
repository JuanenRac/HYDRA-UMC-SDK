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
  one that was already handled and, when the service switched signed commands on (`signed_commands.py`), not one that is unsigned, forged or expired.
* `read_job_message`: the whole first half of the handler of `cmd/job` that the bridges each wrote for themselves (size limit, JSON, intake, the answer to a repeat), so that a
  bridge only decides about the job.

Pure standard library. Neither piece decides anything about safety: the gate (`evaluate_job`, with the state the bridge OBSERVES) still does.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from dataclasses import dataclass
from typing import Callable, Mapping

from .bridge_contract import BridgeError, BridgeJob, job_from_dict
from .signed_commands import CommandVerifier

DEFAULT_TTL_SECONDS = 24 * 3600
IN_DOUBT_POLICIES = ("consult", "refuse")
KEY_SEPARATOR = "\x1f"
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
        self._db = sqlite3.connect(path or ":memory:", check_same_thread=False, isolation_level=None, timeout=5.0)
        # Several bridge processes may share one file: wait for a lock instead of
        # failing the message, and let readers and the writer work side by side.
        self._db.execute("PRAGMA busy_timeout = 5000")
        if path:
            self._db.execute("PRAGMA journal_mode = WAL")
        self._db.execute("CREATE TABLE IF NOT EXISTS keys (k TEXT PRIMARY KEY, at REAL NOT NULL, result TEXT)")
        self._db.execute("CREATE INDEX IF NOT EXISTS keys_at ON keys (at)")

    def close(self) -> None:
        with self._lock:
            self._db.close()

    @staticmethod
    def _stored_key(key: str, source: str | None) -> str:
        """The key as it is stored: a key without a source is stored as it is (so files written before the source existed keep working); with a source the pair is the key."""
        if not isinstance(key, str) or not key.strip():
            raise BridgeError("an idempotency key must be a non-empty string")
        if source is None:
            return key
        if not isinstance(source, str) or not source.strip() or KEY_SEPARATOR in source:
            raise BridgeError("the source of an idempotency key must be a non-empty string without control separators")
        return f"{source}{KEY_SEPARATOR}{key}"

    def claim(self, key: str, source: str | None = None) -> bool:
        """True when `key` (of `source`, when given) has not been handled (it is recorded now), False when it has.

        Two senders may use the same key text; with `source` they no longer shadow each other. Without `source` the behaviour is the one it always had.
        """
        key = self._stored_key(key, source)
        now = self._clock()
        with self._lock:
            self._forget_old(now)
            cursor = self._db.execute("INSERT OR IGNORE INTO keys (k, at, result) VALUES (?, ?, NULL)", (key, now))
            return cursor.rowcount == 1

    def remember(self, key: str, result: str, source: str | None = None) -> None:
        """Stores the answer given for `key`, so that a repeat can be answered the same way. Only keys that were claimed keep one."""
        key = self._stored_key(key, source)
        with self._lock:
            self._db.execute("UPDATE keys SET result = ? WHERE k = ?", (str(result)[:MAX_RESULT_CHARS], key))

    def release(self, key: str, source: str | None = None) -> bool:
        """Gives a claimed key back when the bridge could not handle the job at all (it failed before doing anything), so that the sender retry is not taken for a repeat.

        Only a key that has no stored answer can be released: once an answer exists the job was handled and a repeat must get that answer. Returns True when the key was released.
        """
        key = self._stored_key(key, source)
        with self._lock:
            cursor = self._db.execute("DELETE FROM keys WHERE k = ? AND result IS NULL", (key,))
            return cursor.rowcount == 1

    def recall(self, key: str, source: str | None = None) -> str | None:
        """The answer stored for `key`, or None (never seen, forgotten, or no answer stored)."""
        key = self._stored_key(key, source)
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
    # True for a duplicate whose key was claimed but never got an answer
    # (`store.remember`): the first attempt may have died before running the
    # job, so the bridge must decide whether to run it (when running it twice
    # is physically harmless) or to ask the sender, instead of staying silent.
    in_doubt: bool = False
    # True when the command was refused because of its signature or its expiry (signed commands on); the reason says which.
    unsigned: bool = False


class JobIntake:
    """The first look at a job that arrived over a transport: a retained message is ignored, a malformed one is refused and a repeat is recognised.

    A bridge calls `accept(payload, retained=message.retain)` for every command message and goes on only when `accepted` is True. A duplicate comes back with `duplicate=True`
    and the stored answer is `store.recall(job.idempotency_key)`: the bridge can send that again instead of running the job a second time. When no answer was ever stored for that key
    `in_doubt` is True: the first attempt may have stopped before it finished, and the bridge decides what to do. Without a store nothing is
    deduplicated (the bridge says so by passing none), but retained and malformed messages are still stopped.
    """

    def __init__(self, store: IdempotencyStore | None = None, verifier: CommandVerifier | None = None, *, source: str | None = None,
                 in_doubt_policy: str = "consult", status_query: Callable[[BridgeJob], str | None] | None = None) -> None:
        if in_doubt_policy not in IN_DOUBT_POLICIES:
            raise ValueError(f"in_doubt_policy must be one of {IN_DOUBT_POLICIES}; a bridge never runs an in-doubt job again by itself")
        self._store = store
        self._verifier = verifier
        self._source = source
        self._in_doubt_policy = in_doubt_policy
        self._status_query = status_query

    @property
    def in_doubt_policy(self) -> str:
        return self._in_doubt_policy

    def recall(self, key: str) -> str | None:
        """The answer the bridge stored for `key` (see `IdempotencyStore.remember`), or None."""
        return self._store.recall(key, self._source) if self._store is not None else None

    def remember(self, key: str, result: str) -> None:
        """Stores the answer for `key` under the source of this intake."""
        if self._store is not None:
            self._store.remember(key, result, self._source)

    def release(self, key: str) -> bool:
        """Gives `key` back after a failure that did nothing (see `IdempotencyStore.release`)."""
        return self._store.release(key, self._source) if self._store is not None else False

    def resolve_in_doubt(self, job: BridgeJob) -> str | None:
        """What happened to a job whose first attempt left no answer: with the policy `consult` the bridge asks the machine through `status_query` and the answer is stored
        and returned; the job is never run again. None when the policy is `refuse`, when no query was given, or when the query has no answer or fails."""
        if self._in_doubt_policy != "consult" or self._status_query is None:
            return None
        try:
            answer = self._status_query(job)
        except Exception:  # noqa: BLE001 - a failing query must leave the job refused, not stop the bridge
            return None
        if not isinstance(answer, str) or not answer.strip():
            return None
        self.remember(job.idempotency_key, answer)
        return answer

    def accept(self, payload: Mapping[str, object], *, retained: bool = False, topic: str | None = None) -> Intake:
        """`topic` is the topic the message arrived on; it is part of what a signed command signs, so it is required once the verifier asks for signatures."""
        if retained:
            return Intake(False, "a retained message is a replay by the broker, not a request: it is ignored", retained=True)
        if self._verifier is not None and self._verifier.enabled:
            if topic is None:
                return Intake(False, "the topic of the command is needed to check its signature", unsigned=True)
            verdict = self._verifier.check(topic, payload)
            if not verdict.ok:
                return Intake(False, verdict.reason, unsigned=True)
        try:
            job = job_from_dict(payload)
        except BridgeError as error:
            return Intake(False, f"malformed job: {error}")
        if self._store is not None and not self._store.claim(job.idempotency_key, self._source):
            in_doubt = self._store.recall(job.idempotency_key, self._source) is None
            reason = "this idempotency key was already handled"
            if in_doubt:
                reason += " but no answer was stored for it: the first attempt may not have finished"
            return Intake(False, reason, job=job, duplicate=True, in_doubt=in_doubt)
        return Intake(True, "accepted", job=job)


MAX_JOB_PAYLOAD_BYTES = 16 * 1024


@dataclass(frozen=True)
class JobMessage:
    """What `read_job_message` made of one message on a `cmd/job` topic: exactly one of the four is set.

    * `ignore`: nothing to do and nothing to answer (a retained replay);
    * `refusal`: the answer to publish on the result topic, `{"allowed": False, "reason": ...}` (too large, not JSON, malformed, unsigned or expired, or a repeat whose first
      attempt may not have finished);
    * `repeat_answer`: the answer that was stored for this idempotency key, to publish again instead of running the job a second time;
    * `job`: a job that is new, well formed and (when asked) signed: the bridge decides about it and then calls `store.remember(job.idempotency_key, answer)`.
    """

    job: BridgeJob | None = None
    ignore: bool = False
    refusal: dict[str, object] | None = None
    repeat_answer: str | None = None


def read_job_message(
    intake: JobIntake,
    topic: str,
    payload: bytes,
    *,
    retained: bool = False,
    max_payload_bytes: int = MAX_JOB_PAYLOAD_BYTES,
) -> JobMessage:
    """The first half of the handler of `cmd/job`, the same for every bridge. Never raises."""
    if retained:
        return JobMessage(ignore=True)
    if len(payload) > max_payload_bytes:
        return JobMessage(refusal={"allowed": False, "reason": f"payload is larger than {max_payload_bytes} bytes"})
    try:
        raw = json.loads(payload)
    except (ValueError, UnicodeDecodeError) as error:
        return JobMessage(refusal={"allowed": False, "reason": f"malformed job payload: {error}"})
    taken = intake.accept(raw if isinstance(raw, dict) else {}, topic=topic)
    if taken.accepted:
        return JobMessage(job=taken.job)
    if taken.unsigned:
        return JobMessage(refusal={"allowed": False, "reason": taken.reason})
    if taken.duplicate and taken.job is not None:
        stored = intake.recall(taken.job.idempotency_key)
        if stored is not None:
            return JobMessage(repeat_answer=stored)
        if taken.in_doubt:
            consulted = intake.resolve_in_doubt(taken.job)
            if consulted is not None:
                return JobMessage(repeat_answer=consulted)
            return JobMessage(refusal={"allowed": False, "reason": taken.reason + "; the job is not run again until the machine state is known"})
        return JobMessage(refusal={"allowed": False, "reason": taken.reason})
    return JobMessage(refusal={"allowed": False, "reason": f"malformed job payload: {taken.reason.removeprefix('malformed job: ')}"})
