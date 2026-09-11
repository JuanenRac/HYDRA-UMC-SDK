#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Example: P01's own durable promotion recovery
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Simulates exactly the crash HYDRA-UMC-UPDATER's own install.py already
mitigates in-process (V07-004) - but here the process itself is gone: a
NEW PromotionJournal instance, pointed at the same journal file, finds
the interrupted promotion and recovers it.

    PYTHONPATH=clients/python/src python examples/python/recover_interrupted_promotion.py
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from hydra_umc_sdk import PromotionJournal, PromotionPhase, recover

workspace = Path(tempfile.mkdtemp(prefix="hydra-umc-sdk-example-"))
target = workspace / "hydra-umc-server"
backup = workspace / "hydra-umc-server.backup-abc123"
journal_path = workspace / "promotion_journal.json"

# Set up the real "before the crash" state: the previous installation
# was already renamed aside to backup_path, but staging was never
# promoted into target_path - target_path is genuinely missing.
backup.mkdir()
(backup / "version.txt").write_text("0.6.1", encoding="utf-8")

journal = PromotionJournal(journal_path)
record = journal.begin("HYDRA-UMC-SERVER", target, workspace / "hydra-umc-server.staging", backup)
journal.advance(record.promotion_id, PromotionPhase.BACKED_UP)
print(f"Journal written to {journal_path} - simulating a process crash right here, before the second rename.")

# --- the process "restarts" here: a fresh PromotionJournal, no memory of the run above ---
fresh_journal = PromotionJournal(journal_path)
print(f"\nOn restart, {len(fresh_journal.pending())} pending promotion(s) found in the journal.")
actions = recover(fresh_journal)
for action in actions:
    print(f"  - {action}")

print(f"\n{target} exists again: {target.exists()}")
print(f"{target}/version.txt: {(target / 'version.txt').read_text(encoding='utf-8')}")

shutil.rmtree(workspace, ignore_errors=True)
