# =============================================================================
# HYDRA-UMC-SDK - clients/python/src/hydra_umc_sdk/doc_policy.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""H045: the ecosystem's own public/private documentation boundary check,
as ONE real, tested, canonical module - not the ~60 byte-for-byte copies
of the same logic every repo's own `tools/ci_validate.py` used to carry
before this module existed.

That duplication was a real, found gap: nothing here needed a live
cross-repo dependency to fix - it needed a single source of truth a
future rule change edits ONCE, plus a mechanical way to re-propagate it
everywhere (`tools/sync_doc_policy.py`, this repo's own root) rather than
either a) 60 hand-edits every time the rule changes, or b) a new runtime
dependency on this package for every repo's own per-commit CI (most of
which are not otherwise Python projects at all, and whose CI already has
enough real fragility from cross-repo checkouts - see this ecosystem's
own recent HYDRA-UMC-OS CI history). Every consuming repo VENDORS a copy
of this exact file (`tools/_doc_policy.py`, kept in sync by the script
above, never hand-edited there) - self-contained per-commit CI, a single
canonical source to edit when the rule itself changes.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

# Split across string concatenation so this module's own source is never
# itself flagged by the very check it defines.
PRIVATE_MARKERS: tuple[str, ...] = ("SON" + "NET", "BIB" + "LIA")

# Prose that names this ecosystem's private planning or audit material,
# beyond the bare marker names above.
PRIVATE_PHRASES: tuple[str, ...] = (
    "BIB" + "LIA HYDRA" + "-UMC",
    "private development" + " plan",
    "plan de desarrollo" + " privado",
    "internal work" + " log",
    "registro de trabajo" + " interno",
)


def check_public_private_boundary(root: Path) -> str | None:
    """Runs this ecosystem's real, two-part public/private documentation
    boundary check against `root`'s own git-tracked files: no PRIVATE_MARKERS
    name anywhere, and no PRIVATE_PHRASES prose anywhere. Returns a real,
    ready-to-`fail()` error message on the first violation or check failure,
    or `None` if the boundary genuinely holds.

    `root` must be a real git working tree (this shells out to `git grep`
    there) - the same boundary this repo and every sibling repo's own CI
    already enforced individually before this module existed.
    """
    for marker in PRIVATE_MARKERS:
        result = subprocess.run(
            ("git", "grep", "-n", "-I", "--", marker),
            cwd=root,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode == 0:
            return "public files must not reference private documentation"
        if result.returncode not in (0, 1):
            return "could not check public/private documentation boundary"

    phrase_cmd = ["git", "grep", "-n", "-I", "-i", "-F"]
    for phrase in PRIVATE_PHRASES:
        phrase_cmd += ["-e", phrase]
    prose_result = subprocess.run(
        tuple(phrase_cmd),
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if prose_result.returncode == 0:
        return "public files must not reference private planning or audit documents"
    if prose_result.returncode not in (0, 1):
        return "could not check public/private documentation boundary"

    return None
