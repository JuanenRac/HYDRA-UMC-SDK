#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - tools/sync_version_tools.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Bring every sibling repository's version tooling up to the current rule.

What it does, all idempotent (running it twice changes nothing more):

1. Copies `tools/canonical/bump_manifest_version.py` over each repo's own
   `bump_manifest_version.py`.
2. Loosens the version regexes in each repo's `tools/ci_validate.py` so a
   four-part version is read, compared and accepted like a three-part one.
3. Makes each repo's own `bump_version.py` hand over to the shared utility
   whenever the next step would produce a four-part version.
4. Loosens the same regex in the few workflow/shell files that carry it.

`--check` reports drift without writing (exit 1 when anything would change).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = SDK_ROOT.parent
CANONICAL = SDK_ROOT / "tools" / "canonical" / "bump_manifest_version.py"

HELPER_MARK = "_delegate_to_shared_utility"
DELEGATION = '''def _delegate_to_shared_utility():
    """Hand the bump over to the shared utility once the version has four parts.

    Returns its exit code, or None when this step is an ordinary three-part one.
    """
    import importlib.util
    import json as _json
    from pathlib import Path as _Path

    here = _Path(__file__).resolve().parent
    root = here if (here / "bump_manifest_version.py").is_file() else here.parent
    utility, manifest = root / "bump_manifest_version.py", root / "hydra-umc.project.json"
    if not utility.is_file() or not manifest.is_file():
        return None
    spec = importlib.util.spec_from_file_location("_shared_bump", utility)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    version = _json.loads(manifest.read_text(encoding="utf-8")).get("version", "")
    if not hasattr(module, "FOUR_PART_FROM") or module.next_version(version).count(".") != 3:
        return None
    return module.main()


if __name__ == "__main__":
    _shared_exit = _delegate_to_shared_utility()
    if _shared_exit is not None:
        raise SystemExit(_shared_exit)


'''

CI_REPLACEMENTS = [
    ('SEMVER = re.compile(r"^\\d+\\.\\d+\\.\\d+$")', 'SEMVER = re.compile(r"^\\d+\\.\\d+\\.\\d+(?:\\.\\d+)?$")'),
    ('VERSION_PROSE_TOKEN = re.compile(r"\\bv?(\\d+\\.\\d+\\.\\d+)\\b")', 'VERSION_PROSE_TOKEN = re.compile(r"\\bv?(\\d+\\.\\d+\\.\\d+(?:\\.\\d+)?)\\b")'),
    ('r"\\s+v(\\d+\\.\\d+\\.\\d+)")', 'r"\\s+v(\\d+\\.\\d+\\.\\d+(?:\\.\\d+)?)")'),
    ('(\\d+\\.\\d+\\.\\d+)(?:\\]|\\s|$)', '(\\d+\\.\\d+\\.\\d+(?:\\.\\d+)?)(?:\\]|\\s|$)'),
]
DICT_OLD = '            values.append(match.group(1))\n        return ".".join(values)'
DICT_NEW = (
    '            values.append(match.group(1))\n'
    '        if "build" in pattern and tuple(int(v) for v in values) >= (0, 8, 0):\n'
    '            build = re.search(pattern["build"], text, re.MULTILINE)\n'
    '            if build is not None:\n'
    '                values.append(build.group(1))\n'
    '        return ".".join(values)'
)
NATIVE_OLD = '    return ".".join(match.group(index) for index in (1, 2, 3))'
NATIVE_NEW = (
    '    parts = [match.group(index) for index in (1, 2, 3)]\n'
    '    if len(match.groups()) >= 4 and match.group(4) is not None:\n'
    '        parts.append(match.group(4))\n'
    '    return ".".join(parts)'
)
NATIVE_SEARCH_OLD = '    match = re.search(pattern, text, re.MULTILINE)\n    if match is None or len(match.groups()) < 3:\n        raise ValueError("native version pattern did not expose major.minor.patch")'
NATIVE_SEARCH_COMPACT_OLD = (
    '    match = re.search(pattern, text, re.MULTILINE)\n'
    '    if match is None or len(match.groups()) < 3: raise ValueError("native version pattern did not expose major.minor.patch")'
)
NATIVE_SEARCH_COMPACT_NEW = NATIVE_SEARCH_COMPACT_OLD.replace("re.search(pattern", "re.search(_with_optional_fourth_group(pattern)")
NATIVE_SEARCH_NEW = (
    '    match = re.search(_with_optional_fourth_group(pattern), text, re.MULTILINE)\n'
    '    if match is None or len(match.groups()) < 3:\n'
    '        raise ValueError("native version pattern did not expose major.minor.patch")'
)
HELPER = '''_THREE_GROUPS = re.compile(r"(\\([^()]*\\))\\\\\\.(\\([^()]*\\))\\\\\\.(\\([^()]*\\))(?!\\(\\?:\\\\\\.)")


def _with_optional_fourth_group(pattern: str) -> str:
    """The native-version pattern, made to accept a fourth `.N` component too."""
    match = _THREE_GROUPS.search(pattern)
    if match is None:
        return pattern
    return pattern[: match.end()] + r"(?:\\." + match.group(3) + ")?" + pattern[match.end() :]


'''


def _read(path: Path) -> tuple[str, str]:
    raw = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), newline


def _write(path: Path, text: str, newline: str) -> None:
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


def repos() -> list[Path]:
    return sorted(p for p in WORKSPACE.iterdir() if (p / "hydra-umc.project.json").is_file() and (p / ".git").exists())


def patch_ci_validate(path: Path) -> bool:
    text, newline = _read(path)
    new = text
    for old, repl in CI_REPLACEMENTS:
        new = new.replace(old, repl)
    if DICT_OLD in new and "\"build\" in pattern" not in new:
        new = new.replace(DICT_OLD, DICT_NEW, 1)
    if "_with_optional_fourth_group(pattern)" in new and "def _with_optional_fourth_group" not in new:
        target = "def read_native_version(" if "def read_native_version(" in new else "def native_version("
        new = new.replace(target, HELPER + target, 1)
    if NATIVE_OLD in new and "_with_optional_fourth_group" not in new:
        new = new.replace(NATIVE_OLD, NATIVE_NEW, 1)
        if NATIVE_SEARCH_OLD in new:
            new = new.replace(NATIVE_SEARCH_OLD, NATIVE_SEARCH_NEW, 1)
        if NATIVE_SEARCH_COMPACT_OLD in new:
            new = new.replace(NATIVE_SEARCH_COMPACT_OLD, NATIVE_SEARCH_COMPACT_NEW, 1)
        target = "def read_native_version(" if "def read_native_version(" in new else "def native_version("
        new = new.replace(target, HELPER + target, 1)
    if new == text:
        return False
    _write(path, new, newline)
    return True


def patch_bump_version(path: Path) -> bool:
    text, newline = _read(path)
    if HELPER_MARK in text:
        return False
    guard = re.search(r"(?m)^if __name__ == [\"']__main__[\"']:", text)
    if guard is None:
        return False
    new = text[: guard.start()] + DELEGATION + text[guard.start() :]
    _write(path, new, newline)
    return True


def patch_simple(path: Path, old: str, new: str) -> bool:
    if not path.is_file():
        return False
    text, newline = _read(path)
    if old not in text:
        return False
    _write(path, text.replace(old, new), newline)
    return True


def main() -> int:
    check = "--check" in sys.argv
    canonical_text, _ = _read(CANONICAL)
    changed: list[str] = []
    for repo in repos():
        utility = repo / "bump_manifest_version.py"
        if utility.is_file():
            current, newline = _read(utility)
            if current != canonical_text:
                changed.append(f"{repo.name}/bump_manifest_version.py")
                if not check:
                    _write(utility, canonical_text, newline)
        ci = repo / "tools" / "ci_validate.py"
        if ci.is_file():
            before = ci.read_bytes()
            if check:
                text, _ = _read(ci)
                if any(old in text for old, _ in CI_REPLACEMENTS) or (NATIVE_OLD in text and "_with_optional_fourth_group" not in text):
                    changed.append(f"{repo.name}/tools/ci_validate.py")
            elif patch_ci_validate(ci) and ci.read_bytes() != before:
                changed.append(f"{repo.name}/tools/ci_validate.py")
        for bump in (repo / "bump_version.py", repo / "tools" / "bump_version.py"):
            if not bump.is_file():
                continue
            text, _ = _read(bump)
            if HELPER_MARK in text:
                continue
            if re.search(r"(?m)^if __name__ == [\"']__main__[\"']:", text) is None:
                continue
            changed.append(f"{repo.name}/{bump.relative_to(repo)}")
            if not check:
                patch_bump_version(bump)
        workflow = repo / ".github" / "workflows" / "ci.yml"
        old = "(\\d+\\.\\d+\\.\\d+)\"', (root / \"pyproject.toml\")"
        new = "(\\d+\\.\\d+\\.\\d+(?:\\.\\d+)?)\"', (root / \"pyproject.toml\")"
        if workflow.is_file() and old in workflow.read_text(encoding="utf-8"):
            changed.append(f"{repo.name}/.github/workflows/ci.yml")
            if not check:
                patch_simple(workflow, old, new)
        watch = repo / "update-from-github.sh"
        if watch.is_file() and patch_simple(watch, 'r"v?\\d+\\.\\d+\\.\\d+"', 'r"v?\\d+\\.\\d+\\.\\d+(?:\\.\\d+)?"') if not check else False:
            changed.append(f"{repo.name}/update-from-github.sh")
    missing_build = []
    for repo in repos():
        try:
            manifest = json.loads((repo / "hydra-umc.project.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        pattern = manifest.get("native_version", {}).get("pattern")
        if isinstance(pattern, dict) and "build" not in pattern:
            missing_build.append(f"{repo.name} (v{manifest.get('version')})")
    for entry in missing_build:
        print("no build entry in native_version.pattern: " + entry)
    changed.extend("build entry: " + entry for entry in missing_build)
    for line in changed:
        print(("would change: " if check else "changed: ") + line)
    print(f"{len(changed)} file(s) {'out of date' if check else 'updated'}")
    return 1 if (check and changed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
