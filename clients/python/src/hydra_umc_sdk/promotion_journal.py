# =============================================================================
# HYDRA-UMC-SDK - P01: durable, transactional promotion journal
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""A durable journal for the "swap 2 directories" promotion dance any
installer that stages a verified candidate before promoting it over a
live installation ends up needing - HYDRA-UMC-UPDATER's own
`install.py` (`clone_or_pull()`) and HYDRA-UMC-OPS-AGENT's own
`canary_deploy.py` each independently do this and each already added
their own in-process self-heal for the narrow gap between the two
renames (V07-004) - but that mitigation only survives an exception
inside the SAME Python call stack. A full process crash, a `kill -9`,
a power loss, or a Windows update rebooting the host mid-promotion
leaves no in-memory `try/except` to run at all.

This module is the durable version those fixes' own comments already
call for: a journal ENTRY is written to disk, atomically, BEFORE the
first real filesystem mutation - so `recover()` can find and finish (or
safely undo) an interrupted promotion the next time the installer
starts, not only within the same run that started it.

Deliberately a single small JSON file per installer, not a database:
a real installer's own promotions are infrequent (on the order of one
per real update), so one atomically-rewritten file is proportionate -
see `PromotionJournal`'s own docstring for the exact write discipline
that keeps it crash-safe.
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4


class PromotionPhase(str, Enum):
    """The real, ordered stages of one promotion. Only the transition
    BACKED_UP -> PROMOTED is the genuinely unsafe window (the target
    path briefly does not exist at all) - STARTED -> BACKED_UP and
    PROMOTED -> COMPLETE each still have a real, un-promoted fallback
    (the staging clone, or the backup) sitting untouched on disk."""

    STARTED = "started"  # journal entry written; no filesystem mutation yet
    BACKED_UP = "backed_up"  # target renamed aside to backup_path; staging not yet promoted
    PROMOTED = "promoted"  # staging renamed into target_path - the unsafe window is over
    COMPLETE = "complete"  # promotion fully finished; entry is retained for audit until pruned


@dataclass(frozen=True)
class PromotionRecord:
    """One real promotion attempt. `target_path`/`staging_path`/
    `backup_path` are always absolute, plain strings (not `Path`, so this
    round-trips through `json.dumps`/`json.loads` with no custom codec)."""

    promotion_id: str
    project: str
    target_path: str
    staging_path: str
    backup_path: str
    phase: PromotionPhase
    started_at_utc: str
    updated_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["phase"] = self.phase.value
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PromotionRecord":
        return cls(
            promotion_id=payload["promotion_id"],
            project=payload["project"],
            target_path=payload["target_path"],
            staging_path=payload["staging_path"],
            backup_path=payload["backup_path"],
            phase=PromotionPhase(payload["phase"]),
            started_at_utc=payload["started_at_utc"],
            updated_at_utc=payload["updated_at_utc"],
        )


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write-to-temp-then-`os.replace()` - the same atomic-rename
    discipline `install.py`'s own promotion itself relies on, applied to
    the journal file describing that promotion. A crash mid-write leaves
    either the OLD complete journal or nothing (a `.tmp` file the next
    read never looks at), never a half-written, unparseable one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


class PromotionJournal:
    """Durable store for `PromotionRecord`s, backed by one JSON file at
    `journal_path`. Every mutating call rewrites the whole file
    atomically (`_atomic_write_json`) - proportionate for the real,
    low-frequency call pattern here (a handful of records at most, not a
    high-throughput log)."""

    def __init__(self, journal_path: Path):
        self.journal_path = journal_path

    def _load(self) -> dict[str, PromotionRecord]:
        if not self.journal_path.exists():
            return {}
        try:
            raw = json.loads(self.journal_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            # A corrupt or partially-written journal (e.g. a crash during
            # a non-atomic write from before this module existed) must
            # never crash the installer that depends on it - treat it as
            # empty rather than raising, the same "fail open to no known
            # pending promotions" choice this journal's own recover()
            # already makes for a missing file.
            return {}
        records = raw.get("promotions", {})
        return {key: PromotionRecord.from_dict(value) for key, value in records.items()}

    def _save(self, records: dict[str, PromotionRecord]) -> None:
        payload = {"schema_version": "1.0", "promotions": {key: record.to_dict() for key, record in records.items()}}
        _atomic_write_json(self.journal_path, payload)

    def begin(self, project: str, target_path: Path, staging_path: Path, backup_path: Path) -> PromotionRecord:
        """Writes a new STARTED record BEFORE the caller performs the
        first real rename - the durable analogue of install.py's own
        in-memory bookkeeping right before its promotion step."""
        now = _now_iso()
        record = PromotionRecord(
            promotion_id=uuid4().hex,
            project=project,
            target_path=str(target_path),
            staging_path=str(staging_path),
            backup_path=str(backup_path),
            phase=PromotionPhase.STARTED,
            started_at_utc=now,
            updated_at_utc=now,
        )
        records = self._load()
        records[record.promotion_id] = record
        self._save(records)
        return record

    def advance(self, promotion_id: str, phase: PromotionPhase) -> None:
        """Records that `promotion_id` reached `phase` - called right
        after each real rename actually succeeds, never before."""
        records = self._load()
        if promotion_id not in records:
            raise KeyError(f"no such promotion: {promotion_id!r}")
        existing = records[promotion_id]
        records[promotion_id] = PromotionRecord(
            promotion_id=existing.promotion_id, project=existing.project,
            target_path=existing.target_path, staging_path=existing.staging_path,
            backup_path=existing.backup_path, phase=phase,
            started_at_utc=existing.started_at_utc, updated_at_utc=_now_iso(),
        )
        self._save(records)

    def complete(self, promotion_id: str) -> None:
        """Marks a promotion COMPLETE and prunes it from the journal -
        a completed promotion needs no further recovery, and an
        unbounded journal would otherwise grow forever."""
        records = self._load()
        records.pop(promotion_id, None)
        self._save(records)

    def pending(self) -> list[PromotionRecord]:
        """Every record not yet COMPLETE - what `recover()` below acts
        on. Sorted by `started_at_utc` so recovery is deterministic."""
        return sorted(
            (record for record in self._load().values() if record.phase != PromotionPhase.COMPLETE),
            key=lambda record: record.started_at_utc,
        )


def recover(journal: PromotionJournal) -> list[str]:
    """The real point of this module: finds every promotion `journal`
    itself recorded as started but never completed, and applies the
    exact same self-heal rule `install.py`'s own in-process code already
    uses for the narrow window between its two renames - generalized so
    it also survives a full process crash, not only an exception inside
    the same call stack.

    For each pending record:
      - phase STARTED: no filesystem mutation had happened yet when the
        journal was last updated - nothing to undo. The caller (not this
        function) decides whether to retry the promotion from scratch;
        this only marks the stale record complete so it stops being
        reported as pending forever.
      - phase BACKED_UP: `target_path` was renamed to `backup_path`, but
        staging was never promoted - `target_path` is genuinely missing.
        Restores `backup_path` back to `target_path`, exactly reversing
        the one completed step.
      - phase PROMOTED: `staging_path` was already renamed into
        `target_path` before the crash - the promotion in fact
        succeeded, only the journal never got to record COMPLETE. No
        filesystem action needed; the promotion is real.

    Every real, distinct outcome (including a state that does not match
    what the filesystem actually shows - e.g. BACKED_UP but
    `target_path` is not actually missing) is reported as its own
    action string rather than silently guessed at, so a caller can log
    or surface exactly what recovery did.
    """
    actions: list[str] = []
    for record in journal.pending():
        target = Path(record.target_path)
        backup = Path(record.backup_path)
        if record.phase == PromotionPhase.STARTED:
            actions.append(f"{record.project}: promotion {record.promotion_id} never reached a filesystem change - marking stale record complete")
        elif record.phase == PromotionPhase.BACKED_UP:
            if target.exists():
                actions.append(
                    f"{record.project}: promotion {record.promotion_id} recorded BACKED_UP but {target} already "
                    "exists - not touching it; marking complete without restoring backup"
                )
            elif not backup.exists():
                actions.append(
                    f"{record.project}: promotion {record.promotion_id} recorded BACKED_UP but neither {target} "
                    f"nor {backup} exist - nothing this journal can recover; leaving the record pending for a human"
                )
                continue  # do NOT mark complete - a human needs to see this, not have it silently pruned
            else:
                backup.rename(target)
                actions.append(f"{record.project}: restored {backup} -> {target} (interrupted promotion, phase was BACKED_UP)")
        elif record.phase == PromotionPhase.PROMOTED:
            actions.append(f"{record.project}: promotion {record.promotion_id} had already reached {target} before the interruption - nothing to recover")
        journal.complete(record.promotion_id)
    return actions
