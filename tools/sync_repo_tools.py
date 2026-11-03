#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - tools/sync_repo_tools.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""One place to keep the shared tooling of the repositories identical.

Two kinds of files are handled.

* Files with ONE canonical copy in `tools/canonical/` (`bump_manifest_version.py`,
  `tools/hydra_project_tool.py`, `tools/universal_readme_check.py`, `tools/pretty_run.py`, `tools/status_lights.py`, `.github/workflows/dashboard-dispatch.yml`, the issue forms and the pull request template): every repository must carry exactly
  that text (line endings are the repository's own). `--check` fails when one
  differs, the default run rewrites them.
* Files that legitimately differ by technology (`tools/ci_validate.py`,
  `tools/build_test.py`, `.github/workflows/ci.yml`): they are grouped into
  families by a fingerprint that ignores line endings, the licence line and the
  repository name in the banner, and the families are printed so a stray
  one-off copy is visible. These are only reported, never rewritten.

`tools/_doc_policy.py`, `tools/_readme_parity.py`, the four-part version
handling and the header and banner of the launcher scripts have their own scripts (`sync_doc_policy.py`, `sync_readme_parity.py`,
`sync_version_tools.py`, `sync_script_banners.py`); `--all` runs them too, in the same mode.

    python tools/sync_repo_tools.py --check       # report, exit 1 on drift of a canonical file
    python tools/sync_repo_tools.py               # rewrite the canonical files
    python tools/sync_repo_tools.py --all --check # also the three other scripts, in check mode
    python tools/sync_repo_tools.py --workspace DIR  # another folder holding the repositories

The files that are also the same text in the other families (the live panel, the README layout check, ...) are listed in the registry of
URTC-DEVTOOLS (`tools/tooling_registry.json`). When that repository is next to this one, `--check` also compares the sources the registry says
must be equal (`CROSS_FAMILY=PASS|FAIL`); without it the comparison is skipped. Nothing is ever written to a repository of another family.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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
    "tools/universal_readme_check.py": "universal_readme_check.py",
    "tools/pretty_run.py": "pretty_run.py",
    "tools/status_lights.py": "status_lights.py",
    # The baseline steps of every workflow, as one composite action (the workflows call it and keep what is their own).
    ".github/actions/hydra-baseline/action.yml": "hydra-baseline-action.yml",
    # The issue forms and the pull request template are the same text in every repository.
    ".github/ISSUE_TEMPLATE/bug-report.yml": "community/bug-report.yml",
    ".github/ISSUE_TEMPLATE/config.yml": "community/config.yml",
    ".github/ISSUE_TEMPLATE/documentation.yml": "community/documentation.yml",
    ".github/ISSUE_TEMPLATE/hardware-validation.yml": "community/hardware-validation.yml",
    ".github/ISSUE_TEMPLATE/improvement.yml": "community/improvement.yml",
    ".github/PULL_REQUEST_TEMPLATE.md": "community/PULL_REQUEST_TEMPLATE.md",
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
    # The `GET /metrics` of a service that answers with the standard library HTTP server: the numbers of the service in the text format of Prometheus,
    # the aggregate of its health checks, and nothing a request carried.
    "tools/canonical/service_metrics.py": {
        f"HYDRA-UMC-{name}": f"src/hydra_umc_{name.lower().replace('-', '_')}/service_metrics.py"
        for name in (
            "ANOMALY-DETECTOR", "COGNITIVE-NODE", "CONNECTOR-HUB", "DATALAKE", "DETECTION-HEF", "DOCS-QA", "PRODUCTION-REPORTS", "SAFETY-ZONES",
            "SEMANTIC-PLANNER", "VISION-NODE", "VISUAL-SERVOING-API", "VLA-ENGINE",
        )
    },
    # What a Python service on the standard library HTTP server does the same way: the bounded JSON body, the JSON answers, the query string, the optional bearer
    # token and the limit on the requests handled at the same time. A service adopts it by importing it; the others will follow.
    "tools/canonical/http_common.py": {
        f"HYDRA-UMC-{name}": f"src/hydra_umc_{name.lower().replace('-', '_')}/http_common.py"
        for name in ("COGNITIVE-NODE", "VISION-NODE", "VLA-ENGINE")
    },
    # The uniform `GET /health` of the Python services: closed (404) unless the operator opens it, on loopback or with the bearer token, with a body that names
    # the service and its version and nothing else. Standard library only; the name of the service and of the environment variable come from the package.
    "tools/canonical/health_route.py": {
        f"HYDRA-UMC-{name}": f"src/hydra_umc_{name.lower().replace('-', '_')}/health_route.py"
        for name in (
            "ANOMALY-DETECTOR", "COGNITIVE-NODE", "DATALAKE", "DETECTION-HEF", "DEV-SERVER", "DOCS-QA", "PRODUCTION-REPORTS", "SAFETY-ZONES", "SEMANTIC-PLANNER",
            "VISION-NODE", "VISUAL-SERVOING-API",
        )
    },
    # The same `GET /metrics` for the services written in Rust (tiny_http) and in Go (net/http): the same series, the same rules.
    "tools/canonical/service_metrics.rs": {
        "HYDRA-UMC-ORCHESTRATOR": "src/service_metrics.rs",
        "HYDRA-UMC-SWARM-SYNC": "src/service_metrics.rs",
        "HYDRA-UMC-PATH-PLANNER-3D": "src/service_metrics.rs",
        "HYDRA-UMC-PHYSICS-REPLICA": "src/service_metrics.rs",
    },
    "tools/canonical/service_metrics.go": {
        "HYDRA-UMC-JOB-DISPATCHER": "src/api/service_metrics.go",
    },
    # The installers of the OS read the port, the health route and the unit of a service from this registry.
    "contracts/ports.yaml": {
        "HYDRA-UMC-OS": "provisioning/ports.yaml",
    },
}
# only repositories that already carry the file get it (the eight bridges keep their own bump script; a workflow with steps between the ones of the
# baseline, as the server and the studio have, keeps its own steps and does not call the action)
ONLY_WHERE_PRESENT = frozenset({"bump_manifest_version.py", ".github/actions/hydra-baseline/action.yml"})
# reported by family only
FAMILY_FILES = (
    "tools/ci_validate.py",
    "tools/build_test.py",
    ".github/workflows/ci.yml",
)
OTHER_SYNCS = ("sync_doc_policy.py", "sync_readme_parity.py", "sync_version_tools.py", "sync_script_banners.py")

# `tools/ci_validate.py` has one canonical text too, but a few repositories legitimately extend or adapt it
# (the bridges name their own bump script, STUDIO checks its Work catalogue, ...). A repository adopts the canonical
# text when its own copy holds nothing of its own: ignoring comments, blank lines, `import subprocess` and the
# licence/banner lines, every line it has is also in the canonical file. That covers stale copies (a validator
# that predates a shared check) and copies that only differ in comments, and leaves the real adaptations alone.
NL = chr(10)
UNIFIED_FILE = "tools/ci_validate.py"
UNIFIED_CANONICAL = "ci_validate.py"
# The same rule for the build test. What a repository has of its own (its tests, its verifiers, a second toolchain)
# goes in `tools/extra_build_steps.py`, which the canonical build test runs when it exists; what a repository checks
# of its own besides the shared validator goes in `tools/extra_checks.py`, which the canonical validator runs.
UNIFIED_FILES = (
    (UNIFIED_FILE, UNIFIED_CANONICAL),
    ("tools/build_test.py", "build_test.py"),
)
# The text a canonical file had before its latest change, kept in `tools/canonical/previous/`: a copy that holds
# nothing but those older lines is a stale copy of the canonical file (it is rewritten), not an adaptation.
PREVIOUS_DIR = CANONICAL_DIR / "previous"

_LICENCE = re.compile(r"GPL-3\.0(?:-or-later|-only)?")
_BANNER_NAME = re.compile(r"(?m)^((?:#|//) )(?:HYDRA-UMC|ELECTRO-HOBBY-3D)[A-Za-z0-9-]*( - )")


def canonical_items(canonical_dir: Path = CANONICAL_DIR):
    """(repository path, canonical file name) pairs; a community form or the baseline action whose canonical copy is absent is skipped."""
    for relative, canonical_name in CANONICAL_FILES.items():
        if (canonical_name.startswith("community/") or canonical_name == BASELINE_ACTION) and not (canonical_dir / canonical_name).is_file():
            continue
        yield relative, canonical_name


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
    for relative, canonical_name in canonical_items(canonical_dir):
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


def drift_of_repository(repo: Path) -> list[str]:
    """What differs from the shared tooling in ONE repository: the same rules as `--check`, for the `doctor` command.

    Paths are relative to the repository. The unified files (`ci_validate.py`, `build_test.py`) only count when the
    copy holds nothing of its own (an adaptation is legitimate and is not drift).
    """
    drift: list[str] = []
    for relative, canonical_name in canonical_items():
        wanted, _ = read_text(CANONICAL_DIR / canonical_name)
        target = repo / relative
        if not target.is_file():
            if relative not in ONLY_WHERE_PRESENT:
                drift.append(f"{relative} (missing)")
        elif read_text(target)[0].rstrip(NL) != wanted.rstrip(NL):
            drift.append(relative)
    for canonical, targets in PER_REPOSITORY_FILES.items():
        relative = targets.get(repo.name)
        if relative is None:
            continue
        wanted, _ = read_text(SDK_ROOT / canonical)
        target = repo / relative
        if not target.is_file():
            drift.append(f"{relative} (missing)")
        elif read_text(target)[0].rstrip(NL) != wanted.rstrip(NL):
            drift.append(relative)
    for relative, canonical_name in UNIFIED_FILES:
        target = repo / relative
        if not target.is_file():
            continue
        wanted, _ = read_text(CANONICAL_DIR / canonical_name)
        current, _ = read_text(target)
        previous = previous_text(canonical_name)
        if adopts_unified(current, wanted, previous) and own_lines(current) != own_lines(wanted):
            drift.append(f"{relative} (holds nothing of its own)")
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
    for relative, canonical_name in canonical_items(canonical_dir):
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


def adopts_unified(current: str, canonical: str, previous: str = "") -> bool:
    """True when a copy has no line of its own beyond the canonical file (or the text it had before its last change)."""
    return own_lines(current) <= own_lines(canonical) | (own_lines(previous) if previous else set())


def previous_text(canonical_name: str, previous_dir: Path | None = None) -> str:
    """The text the canonical file had before its latest change, or '' when there is none."""
    path = (previous_dir if previous_dir is not None else PREVIOUS_DIR) / canonical_name
    return read_text(path)[0] if path.is_file() else ""


def unified_status(
    workspace: Path,
    canonical_dir: Path = CANONICAL_DIR,
    relative: str = UNIFIED_FILE,
    canonical_name: str = UNIFIED_CANONICAL,
) -> tuple[list[str], list[str]]:
    """(repositories that adopt the canonical file but differ from it, repositories with an own adaptation)."""
    wanted, _ = read_text(canonical_dir / canonical_name)
    previous = previous_text(canonical_name, canonical_dir / "previous")
    stale: list[str] = []
    adapted: list[str] = []
    for repo in repos(workspace):
        target = repo / relative
        if not target.is_file():
            continue
        current, _ = read_text(target)
        if adopts_unified(current, wanted, previous):
            if own_lines(current) != own_lines(wanted):
                stale.append(repo.name)
        else:
            adapted.append(repo.name)
    return stale, adapted


def write_unified(
    workspace: Path,
    canonical_dir: Path = CANONICAL_DIR,
    relative: str = UNIFIED_FILE,
    canonical_name: str = UNIFIED_CANONICAL,
) -> list[str]:
    """Give the canonical file to every repository that holds nothing of its own in its copy."""
    wanted, _ = read_text(canonical_dir / canonical_name)
    stale, _ = unified_status(workspace, canonical_dir, relative, canonical_name)
    changed: list[str] = []
    for name in stale:
        target = workspace / name / relative
        _, newline = read_text(target)
        target.write_bytes((wanted.rstrip("\n").replace("\n", newline) + newline).encode("utf-8"))
        changed.append(f"{name}/{relative}")
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

BASELINE_ACTION = "hydra-baseline-action.yml"
_LINT_PIN = re.compile(r"(ruff|mypy)==([0-9][0-9.]*)")


def lint_pins(text: str) -> dict[str, set[str]]:
    """The pinned versions of ruff and mypy a text names, by tool."""
    pins: dict[str, set[str]] = defaultdict(set)
    for tool, version in _LINT_PIN.findall(text):
        pins[tool].add(version)
    return dict(pins)


def lint_pin_drift(workspace: Path, canonical_dir: Path = CANONICAL_DIR) -> list[str]:
    """Workflows (and the lint pins of the A.R.M.O.R. tool) that name another version of ruff or mypy than the baseline action does.

    One pin for the three families: the repositories of the other two that sit next to this one are read too, nothing is written to them."""
    wanted = lint_pins(read_text(canonical_dir / BASELINE_ACTION)[0])
    drift: list[str] = []
    candidates = sorted(p for p in workspace.iterdir() if p.is_dir() and p.name.startswith(("HYDRA-UMC", "ARMOR", "URTC")))
    for repo in candidates:
        workflows = repo / ".github" / "workflows"
        files = sorted(workflows.glob("*.yml")) if workflows.is_dir() else []
        files += [f for f in (repo / "tools" / "armor_project_tool.py",) if f.is_file()]
        for path in files:
            for tool, versions in lint_pins(read_text(path)[0]).items():
                if tool in wanted and versions - wanted[tool]:
                    drift.append(f"{repo.name}/{path.relative_to(repo).as_posix()} pins {tool}=={', '.join(sorted(versions))}")
    return drift


CROSS_FAMILY_REGISTRY = ("URTC-DEVTOOLS", "tools", "tooling_registry.json")
_BANNER_LINES = 12
_FAMILY_WORDS = re.compile(r"(?:URTC|HYDRA-UMC|ARMOR|A\.R\.M\.O\.R)[A-Za-z0-9.-]*|<REPO>")


def _cross_family_prints(text: str, repository: str, kind: str) -> set[str]:
    """Two readings of a source (as it is, and with the name of its repository as a placeholder); sources are equal when they share one.

    `same_after_banner` also ignores any family or repository name in the first lines. The rule is the one of `tools/tooling_registry.py`."""
    prints: set[str] = set()
    for name in (None, repository):
        reading = text.replace("\r\n", "\n").rstrip("\n")
        if name:
            reading = reading.replace(name, "<REPO>")
        if kind == "same_after_banner":
            lines = reading.split("\n")
            lines[:_BANNER_LINES] = [_FAMILY_WORDS.sub("<NAME>", line) for line in lines[:_BANNER_LINES]]
            reading = "\n".join(lines)
        prints.add(hashlib.sha256(reading.encode("utf-8")).hexdigest())
    return prints


def cross_family_drift(workspace: Path) -> tuple[list[str], str]:
    """(files whose sources must be the same text in several families and are not, the reason the comparison did not run or '')."""
    registry = workspace.joinpath(*CROSS_FAMILY_REGISTRY)
    if not registry.is_file():
        return [], "URTC-DEVTOOLS is not next to this repository"
    try:
        entries = json.loads(registry.read_text(encoding="utf-8"))["files"]
    except (OSError, ValueError, KeyError) as error:
        return [f"the registry cannot be read: {error}"], ""
    drift: list[str] = []
    for entry in entries:
        if "HYDRA" not in entry.get("same_in", []):
            continue
        prints: dict[str, set[str]] = {}
        for family in entry["same_in"]:
            source = entry["sources"][family]
            target = workspace / source["repo"] / source["path"]
            if target.is_file():
                prints[family] = _cross_family_prints(target.read_bytes().decode("utf-8"), source["repo"], entry["kind"])
        first = next(iter(prints.values()), set())
        if any(not (first & other) for other in prints.values()):
            drift.append(f"{entry['path']} ({', '.join(sorted(prints))})")
    return drift, ""


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
        stale: list[str] = []
        for relative, canonical_name in UNIFIED_FILES:
            stale += [f"{name}/{relative}" for name in unified_status(workspace, CANONICAL_DIR, relative, canonical_name)[0]]
        for line in drift:
            print("differs from the canonical copy: " + line)
        for label in stale:
            print(f"differs from the canonical copy: {label} (holds nothing of its own)")
        drift = drift + stale
        verdict = "FAIL" if drift else "PASS"
        print(f"CANONICAL_TOOLS={verdict} drift={len(drift)} repositories={len(repos(workspace))}")
        status = 1 if drift else 0
    else:
        rewritten = write_canonical(workspace) + write_per_repository(workspace)
        for relative, canonical_name in UNIFIED_FILES:
            rewritten += write_unified(workspace, CANONICAL_DIR, relative, canonical_name)
        for line in rewritten:
            print("rewritten: " + line)
        print(f"CANONICAL_TOOLS=WRITTEN repositories={len(repos(workspace))}")
    for relative, canonical_name in UNIFIED_FILES:
        _, adapted = unified_status(workspace, CANONICAL_DIR, relative, canonical_name)
        print(f"{relative}: {len(adapted)} repositories keep an adaptation of their own: " + ", ".join(adapted))
    report_families(workspace)

    pins = lint_pin_drift(workspace)
    for line in pins:
        print("differs from the pins of the baseline action: " + line)
    print(f"LINT_PINS={'FAIL' if pins else 'PASS'} drift={len(pins)}")
    if args.check and pins:
        status = 1

    cross, skipped = cross_family_drift(workspace)
    for line in cross:
        print("differs between the families: " + line)
    if skipped:
        print(f"CROSS_FAMILY=SKIPPED ({skipped})")
    else:
        print(f"CROSS_FAMILY={'FAIL' if cross else 'PASS'} drift={len(cross)}")
        if args.check and cross:
            status = 1

    if args.all:
        for script in OTHER_SYNCS:
            command = [sys.executable, str(SDK_ROOT / "tools" / script)] + (["--check"] if args.check else [])
            print(f"== {script}")
            if subprocess.run(command, cwd=SDK_ROOT).returncode != 0:
                status = 1
    return status


if __name__ == "__main__":
    raise SystemExit(main())
