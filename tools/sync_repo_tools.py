#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - tools/sync_repo_tools.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""One place to keep the shared tooling of the repositories identical.

Two kinds of files are handled.

* Files with ONE canonical copy in `tools/canonical/` (`bump_manifest_version.py`,
  `tools/hydra_project_tool.py`, `.github/workflows/dashboard-dispatch.yml`): every repository must carry exactly
  that text (line endings are the repository's own). `--check` fails when one
  differs, the default run rewrites them.
* Files that legitimately differ by technology (`tools/ci_validate.py`,
  `tools/build_test.py`, `.github/workflows/ci.yml`): they are grouped into
  families by a fingerprint that ignores line endings, the licence line and the
  repository name in the banner, and the families are printed so a stray
  one-off copy is visible. These are only reported, never rewritten.

`tools/_doc_policy.py`, `tools/_readme_parity.py` and the four-part version
handling have their own scripts (`sync_doc_policy.py`, `sync_readme_parity.py`,
`sync_version_tools.py`); `--all` runs them too, in the same mode.

    python tools/sync_repo_tools.py --check       # report, exit 1 on drift of a canonical file
    python tools/sync_repo_tools.py               # rewrite the canonical files
    python tools/sync_repo_tools.py --all --check # also the three other scripts, in check mode
    python tools/sync_repo_tools.py --workspace DIR  # another folder holding the repositories
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DIR = SDK_ROOT / "tools" / "canonical"

# repository-relative path -> canonical file name in tools/canonical
CANONICAL_FILES = {
    "bump_manifest_version.py": "bump_manifest_version.py",
    ".github/workflows/dashboard-dispatch.yml": "dashboard-dispatch.yml",
    "tools/hydra_project_tool.py": "hydra_project_tool.py",
}
# Files with one canonical copy that only some repositories carry, each at its own path:
# canonical file (relative to the SDK root) -> {repository: path inside it}. The secret redaction is vendored into
# the Python projects that send text out of their process, with the cases every implementation must pass.
PER_REPOSITORY_FILES = {
    "tools/canonical/redaction.py": {
        "HYDRA-UMC-OPS-AGENT": "src/hydra_umc_ops_agent/log_redaction.py",
        "HYDRA-UMC-LOCAL-TECHNICIAN": "src/hydra_umc_local_technician/knowledge/redaction.py",
        "HYDRA-UMC-VISION-STREAMER": "src/hydra_umc_vision_streamer/log_redaction.py",
    },
    "contracts/redaction/vectors.json": {
        "HYDRA-UMC-OPS-AGENT": "tests/redaction_vectors.json",
        "HYDRA-UMC-LOCAL-TECHNICIAN": "tests/redaction_vectors.json",
        "HYDRA-UMC-VISION-STREAMER": "tests/redaction_vectors.json",
    },
}
# only repositories that already carry the file get it (the eight bridges keep their own bump script)
ONLY_WHERE_PRESENT = frozenset({"bump_manifest_version.py"})
# reported by family only
FAMILY_FILES = (
    "tools/ci_validate.py",
    "tools/build_test.py",
    ".github/workflows/ci.yml",
)
OTHER_SYNCS = ("sync_doc_policy.py", "sync_readme_parity.py", "sync_version_tools.py")

# `tools/ci_validate.py` has one canonical text too, but a few repositories legitimately extend or adapt it
# (the bridges name their own bump script, STUDIO checks its Work catalogue, ...). A repository adopts the canonical
# text when its own copy holds nothing of its own: ignoring comments, blank lines, `import subprocess` and the
# licence/banner lines, every line it has is also in the canonical file. That covers stale copies (a validator
# that predates a shared check) and copies that only differ in comments, and leaves the real adaptations alone.
NL = chr(10)
UNIFIED_FILE = "tools/ci_validate.py"
UNIFIED_CANONICAL = "ci_validate.py"

_LICENCE = re.compile(r"GPL-3\.0(?:-or-later|-only)?")
_BANNER_NAME = re.compile(r"(?m)^((?:#|//) )(?:HYDRA-UMC|ELECTRO-HOBBY-3D)[A-Za-z0-9-]*( - )")


def is_family_repo(path: Path) -> bool:
    name = path.name
    return (
        path.is_dir()
        and (name == "HYDRA-UMC" or name.startswith("HYDRA-UMC-"))
        and (path / "hydra-umc.project.json").is_file()
    )


def repos(workspace: Path) -> list[Path]:
    return sorted(p for p in workspace.iterdir() if is_family_repo(p))


def read_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), newline


def fingerprint(text: str) -> str:
    """Stable hash that ignores line endings, the licence line and the banner name."""
    text = text.replace("\r\n", "\n").rstrip("\n")
    text = _LICENCE.sub("GPL", text)
    text = _BANNER_NAME.sub(r"\1NAME\2", text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def check_canonical(workspace: Path, canonical_dir: Path = CANONICAL_DIR) -> list[str]:
    """Paths (repository/relative) whose text differs from the canonical copy or is missing."""
    drift: list[str] = []
    for relative, canonical_name in CANONICAL_FILES.items():
        wanted, _ = read_text(canonical_dir / canonical_name)
        for repo in repos(workspace):
            target = repo / relative
            if not target.is_file():
                if relative not in ONLY_WHERE_PRESENT:
                    drift.append(f"{repo.name}/{relative} (missing)")
                continue
            current, _ = read_text(target)
            if current.rstrip("\n") != wanted.rstrip("\n"):
                drift.append(f"{repo.name}/{relative}")
    return drift


def per_repository_targets(workspace: Path, sdk_root: Path = SDK_ROOT):
    """(canonical text, target path, repository name) for every per-repository copy whose repository exists."""
    for canonical, targets in PER_REPOSITORY_FILES.items():
        wanted, _ = read_text(sdk_root / canonical)
        for name, relative in targets.items():
            if (workspace / name / "hydra-umc.project.json").is_file():
                yield wanted, workspace / name / relative, f"{name}/{relative}"


def check_per_repository(workspace: Path, sdk_root: Path = SDK_ROOT) -> list[str]:
    drift: list[str] = []
    for wanted, target, label in per_repository_targets(workspace, sdk_root):
        if not target.is_file():
            drift.append(f"{label} (missing)")
        elif read_text(target)[0].rstrip(NL) != wanted.rstrip(NL):
            drift.append(label)
    return drift


def write_per_repository(workspace: Path, sdk_root: Path = SDK_ROOT) -> list[str]:
    changed: list[str] = []
    for wanted, target, label in per_repository_targets(workspace, sdk_root):
        newline = NL
        if target.is_file():
            current, newline = read_text(target)
            if current.rstrip(NL) == wanted.rstrip(NL):
                continue
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((wanted.rstrip(NL).replace(NL, newline) + newline).encode("utf-8"))
        changed.append(label)
    return changed


def write_canonical(workspace: Path, canonical_dir: Path = CANONICAL_DIR) -> list[str]:
    """Rewrite every differing canonical file (keeping the repository's line endings)."""
    changed: list[str] = []
    for relative, canonical_name in CANONICAL_FILES.items():
        wanted, _ = read_text(canonical_dir / canonical_name)
        for repo in repos(workspace):
            target = repo / relative
            if target.is_file():
                current, newline = read_text(target)
                if current.rstrip("\n") == wanted.rstrip("\n"):
                    continue
            else:
                if relative in ONLY_WHERE_PRESENT:
                    continue
                newline = "\n"
                target.parent.mkdir(parents=True, exist_ok=True)
            body = wanted.rstrip("\n").replace("\n", newline) + newline
            target.write_bytes(body.encode("utf-8"))
            changed.append(f"{repo.name}/{relative}")
    return changed


def own_lines(text: str) -> set[str]:
    """The lines of a validator that carry logic: no comments, blanks, `import subprocess`, licence or banner."""
    lines: set[str] = set()
    text = re.sub(
        r"from (\S+) import \(([^)]*)\)",
        lambda m: "\n".join(f"from {m.group(1)} import {n.strip()}" for n in m.group(2).split(",") if n.strip()),
        text.replace("\r\n", "\n"),
    )
    text = re.sub(
        r"(?m)^from (\S+) import ([^(\n]+)$",
        lambda m: "\n".join(f"from {m.group(1)} import {n.strip()}" for n in m.group(2).split(",")),
        text,
    )
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped == "import subprocess":
            continue
        lines.add(stripped)
    return lines


def adopts_unified(current: str, canonical: str) -> bool:
    """True when a copy has no line of its own beyond the canonical validator."""
    return own_lines(current) <= own_lines(canonical)


def unified_status(workspace: Path, canonical_dir: Path = CANONICAL_DIR) -> tuple[list[str], list[str]]:
    """(repositories that adopt the canonical validator but differ from it, repositories with an own adaptation)."""
    wanted, _ = read_text(canonical_dir / UNIFIED_CANONICAL)
    stale: list[str] = []
    adapted: list[str] = []
    for repo in repos(workspace):
        target = repo / UNIFIED_FILE
        if not target.is_file():
            continue
        current, _ = read_text(target)
        if adopts_unified(current, wanted):
            if own_lines(current) != own_lines(wanted):
                stale.append(repo.name)
        else:
            adapted.append(repo.name)
    return stale, adapted


def write_unified(workspace: Path, canonical_dir: Path = CANONICAL_DIR) -> list[str]:
    """Give the canonical validator to every repository that holds nothing of its own in its copy."""
    wanted, _ = read_text(canonical_dir / UNIFIED_CANONICAL)
    stale, _ = unified_status(workspace, canonical_dir)
    changed: list[str] = []
    for name in stale:
        target = workspace / name / UNIFIED_FILE
        _, newline = read_text(target)
        target.write_bytes((wanted.rstrip("\n").replace("\n", newline) + newline).encode("utf-8"))
        changed.append(f"{name}/{UNIFIED_FILE}")
    return changed


def families(workspace: Path, relative: str) -> dict[str, list[str]]:
    """Repository names grouped by the fingerprint of one file; absent files under ''."""
    groups: dict[str, list[str]] = defaultdict(list)
    for repo in repos(workspace):
        target = repo / relative
        if not target.is_file():
            groups[""].append(repo.name)
            continue
        text, _ = read_text(target)
        groups[fingerprint(text)].append(repo.name)
    return dict(groups)


def report_families(workspace: Path) -> None:
    for relative in FAMILY_FILES:
        groups = families(workspace, relative)
        present = [key for key in groups if key]
        missing = len(groups.get("", []))
        print(f"{relative}: {len(present)} variant(s)" + (f", {missing} repositories without it" if missing else ""))
        for key, names in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0])):
            if not key:
                continue
            shown = ", ".join(names[:4]) + (f", +{len(names) - 4}" if len(names) > 4 else "")
            print(f"  {len(names):3d} x {key}  {shown}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 on drift of a canonical file")
    parser.add_argument("--all", action="store_true", help="also run the other three sync scripts")
    parser.add_argument("--workspace", type=Path, default=SDK_ROOT.parent)
    args = parser.parse_args(argv)
    workspace = args.workspace.resolve()

    status = 0
    if args.check:
        drift = check_canonical(workspace) + check_per_repository(workspace)
        stale, _ = unified_status(workspace)
        for line in drift:
            print("differs from the canonical copy: " + line)
        for name in stale:
            print(f"differs from the canonical copy: {name}/{UNIFIED_FILE} (holds nothing of its own)")
        drift = drift + stale
        verdict = "FAIL" if drift else "PASS"
        print(f"CANONICAL_TOOLS={verdict} drift={len(drift)} repositories={len(repos(workspace))}")
        status = 1 if drift else 0
    else:
        for line in write_canonical(workspace) + write_per_repository(workspace) + write_unified(workspace):
            print("rewritten: " + line)
        print(f"CANONICAL_TOOLS=WRITTEN repositories={len(repos(workspace))}")
    _, adapted = unified_status(workspace)
    print(f"{UNIFIED_FILE}: {len(adapted)} repositories keep an adaptation of their own: " + ", ".join(adapted))
    report_families(workspace)

    if args.all:
        for script in OTHER_SYNCS:
            command = [sys.executable, str(SDK_ROOT / "tools" / script)] + (["--check"] if args.check else [])
            print(f"== {script}")
            if subprocess.run(command, cwd=SDK_ROOT).returncode != 0:
                status = 1
    return status


if __name__ == "__main__":
    raise SystemExit(main())
