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
renames - but that mitigation only survives an exception
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
import urllib.error
import urllib.request
from urllib.parse import urlsplit
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
    round-trips through `json.dumps`/`json.loads` with no custom codec).

    `health_check_url`: the real URL to probe AFTER promoting,
    before this promotion may be marked COMPLETE - only ever set when
    the project's own `hydra-umc.project.json` declares a
    `service_health_path` (see HYDRA-UMC-UPDATER's `project_manifest.py`);
    `None` means this project declares no health endpoint, so promotion
    completes the moment the rename itself succeeds, same as before this
    field existed."""

    promotion_id: str
    project: str
    target_path: str
    staging_path: str
    backup_path: str
    phase: PromotionPhase
    started_at_utc: str
    updated_at_utc: str
    health_check_url: str | None = None

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
            # .get(), not [...]: a journal file written before this field
            # existed has no such key at all - that must read back as "no
            # health check declared", never a KeyError crashing recover()
            # on an old, otherwise-valid journal.
            health_check_url=payload.get("health_check_url"),
        )


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fsync_directory(directory: Path) -> None:
    """Makes a rename inside `directory` durable (POSIX only; a no-op where a
    directory cannot be opened, e.g. Windows)."""
    try:
        fd = os.open(str(directory), os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


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
            # The data must be on disk before the rename makes it the journal:
            # after a power cut some file systems keep the rename but lose an
            # unsynced file body, which would read back as an empty journal.
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
        _fsync_directory(path.parent)
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
        # Files this journal set aside because they could not be read (see
        # `_load`). `recover()` reports them so a human can look at them.
        self.preserved_files: list[Path] = []

    def _preserve(self, *, move: bool) -> None:
        """Keeps the unreadable journal for a human instead of letting the next
        write replace it: a corrupt file is moved aside, a file with some
        unreadable records is copied (the readable ones stay in the journal)."""
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        target = self.journal_path.with_name(f"{self.journal_path.name}.corrupt-{stamp}")
        try:
            if move:
                os.replace(self.journal_path, target)
            else:
                target.write_bytes(self.journal_path.read_bytes())
        except OSError:
            return
        self.preserved_files.append(target)

    def _load(self) -> dict[str, PromotionRecord]:
        if not self.journal_path.exists():
            return {}
        try:
            raw = json.loads(self.journal_path.read_text(encoding="utf-8"))
        except OSError:
            return {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            # A corrupt or partially-written journal must never crash the
            # installer that depends on it, and must not be silently replaced
            # by the next write either: whatever it said about pending
            # promotions is kept in a `.corrupt-<time>` file next to it.
            self._preserve(move=True)
            return {}
        records_raw = raw.get("promotions", {}) if isinstance(raw, dict) else None
        if not isinstance(records_raw, dict):
            self._preserve(move=True)
            return {}
        records: dict[str, PromotionRecord] = {}
        skipped = False
        for key, value in records_raw.items():
            try:
                records[key] = PromotionRecord.from_dict(value)
            except (KeyError, ValueError, TypeError, AttributeError):
                skipped = True
        if skipped:
            self._preserve(move=False)
        return records

    def _save(self, records: dict[str, PromotionRecord]) -> None:
        payload = {"schema_version": "1.0", "promotions": {key: record.to_dict() for key, record in records.items()}}
        _atomic_write_json(self.journal_path, payload)

    def begin(
        self, project: str, target_path: Path, staging_path: Path, backup_path: Path,
        *, health_check_url: str | None = None,
    ) -> PromotionRecord:
        """Writes a new STARTED record BEFORE the caller performs the
        first real rename - the durable analogue of install.py's own
        in-memory bookkeeping right before its promotion step.
        `health_check_url`: pass this project's real health
        endpoint when it declares one, so a later crash between
        promoting and checking it is recoverable - see this module's own
        header and `recover()`'s PROMOTED branch below."""
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
            health_check_url=health_check_url,
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
            health_check_url=existing.health_check_url,
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


def check_service_health(url: str, *, timeout: float = 5.0) -> tuple[bool, str]:
    """this project's own real "servicio comprobado" step: a real, minimal HTTP GET
    against `url`, never raising. Deliberately STRICTER than a bare
    reachability probe (compare HYDRA-UMC-LOCAL-TECHNICIAN's own
    `network.connectivity`, where any real HTTP response - even a 5xx -
    counts as "reachable"): here the question is "did the promotion I
    just performed actually come up healthy", so only a real 2xx counts
    as healthy - a 4xx/5xx means the newly-promoted code IS running and
    answering, but is not well, and must not be waved through as success.
    Returns (healthy, reason) - reason is always a real, human-readable
    fact (the status code, or the real connection failure), never a
    guess."""
    if urlsplit(url).scheme not in ("http", "https"):
        return False, "only http and https health checks are supported"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            status = response.getcode()
            if not isinstance(status, int):
                return False, "no HTTP status in the response"
            return (200 <= status < 300), f"HTTP {status}"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return False, str(exc.reason)
    except Exception as exc:  # the function promises never to raise
        return False, str(exc) or type(exc).__name__


def recover(journal: PromotionJournal) -> list[str]:
    """The real point of this module: finds every promotion `journal`
    itself recorded as started but never completed, and applies the
    exact same self-heal rule `install.py`'s own in-process code already
    uses for the narrow window between its two renames - generalized so
    it also survives a full process crash, not only an exception inside
    the same call stack.

    For each pending record:
      - phase STARTED: the record is written before the first rename, so
        this only proves the promotion began. If `target_path` still exists
        nothing was touched and the stale record is just completed (the
        caller decides whether to retry from scratch). If it is missing and
        `backup_path` exists, the crash came between the rename and
        `advance()`: the backup is restored. If neither exists (a first
        install that never created anything) the stale record is completed.
      - phase BACKED_UP: `target_path` was renamed to `backup_path`, but
        staging was never promoted - `target_path` is genuinely missing.
        Restores `backup_path` back to `target_path`, exactly reversing
        the one completed step.
      - phase PROMOTED: `staging_path` was already renamed into
        `target_path` before the crash - the promotion in fact
        succeeded, only the journal never got to record COMPLETE. No
        filesystem action needed; the promotion is real. If this record
        declares a `health_check_url`, the pending health check
        itself is run for real right now, exactly as `install.py` would
        have run it had the crash not interrupted things - never
        skipped, and never repeating the actual install/build. A check
        that still fails leaves the record pending (same "leave it for a
        human" precedent the BACKED_UP branch already sets below), so
        recovery never announces success prematurely.

    Every real, distinct outcome (including a state that does not match
    what the filesystem actually shows - e.g. BACKED_UP but
    `target_path` is not actually missing) is reported as its own
    action string rather than silently guessed at, so a caller can log
    or surface exactly what recovery did.
    """
    actions: list[str] = []
    for preserved in getattr(journal, "preserved_files", []):
        actions.append(f"journal: an unreadable journal or record was kept at {preserved} for a human to review")
    for record in journal.pending():
        target = Path(record.target_path)
        backup = Path(record.backup_path)
        try:
            if record.phase == PromotionPhase.STARTED:
                # The record is written before the first rename, so STARTED
                # does not prove that nothing moved: a crash between the
                # rename and `advance()` leaves it here with the live
                # directory already set aside. Look at the disk.
                if not target.exists() and backup.exists():
                    backup.rename(target)
                    actions.append(
                        f"{record.project}: restored {backup} -> {target} (interrupted promotion, phase was STARTED "
                        "but the live directory had already been set aside)"
                    )
                else:
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
                if record.health_check_url:
                    healthy, reason = check_service_health(record.health_check_url)
                    if healthy:
                        actions.append(
                            f"{record.project}: promotion {record.promotion_id} had already reached {target}; "
                            f"its pending health check now passes ({reason}) - completing"
                        )
                    else:
                        actions.append(
                            f"{record.project}: promotion {record.promotion_id} had already reached {target}, but its "
                            f"pending health check still fails ({reason}) - leaving pending for a human/next run, not "
                            "announcing success"
                        )
                        continue  # do NOT mark complete - same precedent as the BACKED_UP branch above
                else:
                    actions.append(f"{record.project}: promotion {record.promotion_id} had already reached {target} before the interruption - nothing to recover")
        except OSError as exc:
            # One record that cannot be restored (permissions, another
            # volume) must not stop the others from being processed.
            actions.append(f"{record.project}: could not restore promotion {record.promotion_id}: {exc} - leaving the record pending for a human")
            continue
        journal.complete(record.promotion_id)
    return actions
