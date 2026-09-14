#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - tools/sync_doc_policy.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""H045: propagates this repo's own canonical
`clients/python/src/hydra_umc_sdk/doc_policy.py` to every sibling repo's
`tools/_doc_policy.py` (a plain vendored copy, never hand-edited there),
and rewrites each sibling's own `tools/ci_validate.py` to call it instead
of carrying its own independent copy of the same logic.

Real design decision this module's own docstring already explains: no
sibling repo gains a live runtime dependency on this package (most of
them are not even Python projects, and this ecosystem's own CI already
has enough real fragility from cross-repo checkouts) - each repo's own
per-commit CI stays fully self-contained. The actual problem H045 found
(a future rule change needs editing ~60 byte-for-byte copies by hand) is
what this script fixes: edit the ONE canonical module above, then run
this script once to re-propagate it everywhere mechanically.

Usage: run from this repo's own root, with every sibling repo checked
out alongside it (this ecosystem's own standard local-dev layout, the
same one every other cross-repo tool here already assumes):
    python tools/sync_doc_policy.py [--check]
--check reports which repos are out of sync without writing anything -
exit code 1 if any are (for a future CI use, not run in per-repo CI
today - that would reintroduce exactly the live cross-repo dependency
this design deliberately avoids for the common per-commit path).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "clients" / "python" / "src" / "hydra_umc_sdk" / "doc_policy.py"
SIBLINGS_ROOT = ROOT.parent

VENDORED_HEADER = """# =============================================================================
# {name} - tools/_doc_policy.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
# VENDORED - do not hand-edit. This is a byte-for-byte copy of
# HYDRA-UMC-SDK's own canonical
# clients/python/src/hydra_umc_sdk/doc_policy.py (H045), kept in sync by
# that repo's own tools/sync_doc_policy.py. Edit the rule there, then
# re-run that script to update every repo that vendors it, this one
# included.
"""

# The canonical file's own header (everything up to and including its
# own closing "======" banner + docstring) is replaced by VENDORED_HEADER
# above - the sibling-facing copy needs a different, shorter notice, not
# the canonical module's own design-rationale docstring repeated ~60
# times.
_CANONICAL_BODY_MARKER = "from __future__ import annotations"

# The exact call-site snippet that replaces each repo's own previously
# duplicated inline doc-policy block inside ci_validate.py.
CALL_SITE = '''    doc_policy_error = check_public_private_boundary(ROOT)
    if doc_policy_error:
        fail(doc_policy_error)
'''
IMPORT_LINE = "from _doc_policy import check_public_private_boundary\n"

# Matches the start of the old inline block (either "private_marker ="
# for a single-marker repo, or "private_markers =" for the 2-marker
# SEMANTIC-PLANNER variant) through the LAST line still containing this
# block's own real failure message - covers every real stylistic
# variant found across the ecosystem (some one-line `if`s, some
# multi-line).
_BLOCK_RE = re.compile(
    r"[ \t]*private_marker(?:s)? = .*could not check public/private documentation boundary\"\)\n",
    re.DOTALL,
)


def canonical_body() -> str:
    text = CANONICAL.read_text(encoding="utf-8")
    idx = text.index(_CANONICAL_BODY_MARKER)
    return text[idx:]


def iter_sibling_repos():
    for entry in sorted(SIBLINGS_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if not (entry.name.startswith("HYDRA-UMC-") or entry.name.startswith("URTC")):
            continue
        if not (entry / "tools" / "ci_validate.py").is_file():
            continue
        yield entry


def vendored_text(repo_name: str) -> str:
    return VENDORED_HEADER.format(name=repo_name) + "\n" + canonical_body()


def sync_one(repo: Path, check_only: bool) -> str:
    vendored_path = repo / "tools" / "_doc_policy.py"
    ci_validate_path = repo / "tools" / "ci_validate.py"

    new_vendored = vendored_text(repo.name)
    vendored_changed = not vendored_path.is_file() or vendored_path.read_text(encoding="utf-8") != new_vendored

    ci_text = ci_validate_path.read_text(encoding="utf-8")
    if IMPORT_LINE in ci_text:
        ci_changed = False
        new_ci_text = ci_text
    else:
        match = _BLOCK_RE.search(ci_text)
        if match is None:
            return "no-block-found"
        new_ci_text = ci_text[: match.start()] + CALL_SITE + ci_text[match.end() :]
        if IMPORT_LINE not in new_ci_text:
            # Insert the import right after the existing stdlib imports,
            # immediately before the module-level ROOT assignment.
            root_decl = "\nROOT = Path(__file__)"
            insert_at = new_ci_text.index(root_decl)
            new_ci_text = new_ci_text[:insert_at] + "\n" + IMPORT_LINE + new_ci_text[insert_at:]
        ci_changed = True

    if not vendored_changed and not ci_changed:
        return "already-in-sync"
    if check_only:
        return "out-of-sync"

    vendored_path.write_text(new_vendored, encoding="utf-8")
    ci_validate_path.write_text(new_ci_text, encoding="utf-8")
    return "synced"


def main() -> int:
    check_only = "--check" in sys.argv[1:]
    results: dict[str, list[str]] = {}
    for repo in iter_sibling_repos():
        status = sync_one(repo, check_only)
        results.setdefault(status, []).append(repo.name)

    for status, repos in sorted(results.items()):
        print(f"{status} ({len(repos)}): {', '.join(repos)}")

    if check_only and results.get("out-of-sync"):
        return 1
    if results.get("no-block-found"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
