#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - tools/sync_readme_parity.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Propagates this repo's own canonical
`clients/python/src/hydra_umc_sdk/readme_parity.py` to every sibling
repo's `tools/_readme_parity.py` (a plain vendored copy, never
hand-edited there) and adds a real README section-structure-parity call
to each sibling's own `tools/ci_validate.py`, right after its existing
public/private documentation boundary check (see
`sync_doc_policy.py`, the same real distribution design this reuses:
no live runtime dependency on this package for any repo's own
per-commit CI).

The Portuguese README (README_por.md) is required: the vendored rule reports
its absence, and this script also adds it to each repo's own
REQUIRED_DOCUMENTS in `tools/ci_validate.py`. A repo that does not have its
README_por.md yet is reported as `skipped-no-readme-por` and left on the
previous rule, so adding the requirement never turns its CI red before the
file exists; write the README, then re-run this script.

Usage: run from this repo's own root, with every sibling repo checked
out alongside it:
    python tools/sync_readme_parity.py [--check]
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "clients" / "python" / "src" / "hydra_umc_sdk" / "readme_parity.py"
SIBLINGS_ROOT = ROOT.parent

VENDORED_HEADER = """# =============================================================================
# {name} - tools/_readme_parity.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
# VENDORED - do not hand-edit. This is a byte-for-byte copy of
# HYDRA-UMC-SDK's own canonical
# clients/python/src/hydra_umc_sdk/readme_parity.py, kept in sync
# by that repo's own tools/sync_readme_parity.py. Edit the rule there,
# then re-run that script to update every repo that vendors it, this one
# included.
"""

_CANONICAL_BODY_MARKER = "from __future__ import annotations"

CALL_SITE = '''    for readme_problem in check_readme_section_parity(ROOT):
        fail(readme_problem)
'''
IMPORT_LINE = "from _readme_parity import check_readme_section_parity\n"

# Anchor for the required-documents entry: the Japanese README line of the
# REQUIRED_DOCUMENTS tuple every repo's ci_validate.py carries.
_REQUIRED_ANCHOR = '    "README_jpn.md",\n'
_REQUIRED_POR = '    "README_por.md",\n'
# A few repos write the tuple several names per line instead of one per line.
_REQUIRED_INLINE_ANCHOR = '"README_jpn.md", '
_REQUIRED_INLINE_POR = '"README_jpn.md", "README_por.md", '

# Anchor: insert right after the doc-policy import this same repo's own
# earlier sync_doc_policy.py pass already added - keeps both new checks
# grouped together, and gives every repo an unambiguous, idempotent
# anchor to insert after.
_DOC_POLICY_IMPORT = "from _doc_policy import check_public_private_boundary\n"
# Anchor for the CALL_SITE: right after that earlier call-site block.
_DOC_POLICY_CALL = '''    doc_policy_error = check_public_private_boundary(ROOT)
    if doc_policy_error:
        fail(doc_policy_error)
'''


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
    if not (repo / "README_por.md").is_file():
        return "skipped-no-readme-por"
    vendored_path = repo / "tools" / "_readme_parity.py"
    ci_validate_path = repo / "tools" / "ci_validate.py"

    new_vendored = vendored_text(repo.name)
    vendored_changed = not vendored_path.is_file() or vendored_path.read_text(encoding="utf-8") != new_vendored

    ci_text = ci_validate_path.read_text(encoding="utf-8")
    new_ci_text = ci_text
    if IMPORT_LINE not in new_ci_text:
        if _DOC_POLICY_IMPORT not in new_ci_text or _DOC_POLICY_CALL not in new_ci_text:
            return "no-h045-anchor-found"
        new_ci_text = new_ci_text.replace(_DOC_POLICY_IMPORT, _DOC_POLICY_IMPORT + IMPORT_LINE, 1)
        new_ci_text = new_ci_text.replace(_DOC_POLICY_CALL, _DOC_POLICY_CALL + CALL_SITE, 1)
    if '"README_por.md"' not in new_ci_text:
        if _REQUIRED_ANCHOR in new_ci_text:
            new_ci_text = new_ci_text.replace(_REQUIRED_ANCHOR, _REQUIRED_ANCHOR + _REQUIRED_POR, 1)
        elif _REQUIRED_INLINE_ANCHOR in new_ci_text:
            new_ci_text = new_ci_text.replace(_REQUIRED_INLINE_ANCHOR, _REQUIRED_INLINE_POR, 1)
        else:
            return "no-required-documents-anchor"
    ci_changed = new_ci_text != ci_text

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
    if results.get("no-h045-anchor-found") or results.get("no-required-documents-anchor"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
