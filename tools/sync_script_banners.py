#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - tools/sync_script_banners.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Generate the header and the banner of the launcher scripts of every repository from one place.

The launchers (`build`, `build-test`, `run`, as `.sh` and `.bat`) of a repository open with a header comment and print a banner. They used to be copied by
hand, and the copies drifted (a licence line that still said GPL-3.0, boxes whose right edge no longer lined up). The text now lives once, in
`tools/canonical/script_banners.json`, with the name of the repository written `<REPO>`:

* `standard`: the header block and the banner block, between the `HYDRA_UMC_SCRIPT_STANDARD_*` markers, of every repository that has them. Only those two blocks are
  rewritten; whatever a repository has around them is its own.
* `bridge`: the four launchers of the eight bridges (`HYDRA-UMC-BRIDGE-*`), which are the same script apart from the name, as a whole file. `<PAD>` is the
  spaces that bring the right edge of the box of `build-test` to the same column whatever the length of the name.

    python tools/sync_script_banners.py --check               # report, exit 1 on drift
    python tools/sync_script_banners.py                       # rewrite what differs
    python tools/sync_script_banners.py --repos A B           # only these repositories
    python tools/sync_script_banners.py --workspace DIR       # another folder holding the repositories

Nothing is changed in a launcher outside those blocks (or, for a bridge, outside the four files). Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parents[1]
BANNERS = SDK_ROOT / "tools" / "canonical" / "script_banners.json"
PLACEHOLDER = "<REPO>"
BOX_WIDTH = 69  # the stars of the box of a bridge's build-test; the lines of its text end with a star in the last column
BOX_TITLE_ENDS = "(NO VERSION CHANGE)"
MARKERS = (
    ("header", "SCRIPT_STANDARD_HEADER_BEGIN", "SCRIPT_STANDARD_HEADER_END"),
    ("banner", "SCRIPT_STANDARD_BANNER_BEGIN", "SCRIPT_STANDARD_BANNER_END"),
)


def load(path: Path = BANNERS) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {"standard": data["standard"], "bridge": data["bridge"]}


def family_repos(workspace: Path) -> list[Path]:
    return sorted(p for p in workspace.iterdir() if p.is_dir() and (p.name == "HYDRA-UMC" or p.name.startswith("HYDRA-UMC-")) and (p / "hydra-umc.project.json").is_file())


def is_bridge(path: Path) -> bool:
    return path.name.startswith("HYDRA-UMC-BRIDGE-")


def replace_block(text: str, begin: str, end: str, wanted: str) -> str | None:
    """`text` with the whole lines from the one holding `begin` to the one holding `end` replaced; None when the markers are not there."""
    lines = text.split("\n")
    first = next((i for i, line in enumerate(lines) if begin in line), None)
    if first is None:
        return None
    last = next((i for i in range(first, len(lines)) if end in lines[i]), None)
    if last is None:
        return None
    return "\n".join(lines[:first] + wanted.split("\n") + lines[last + 1 :])


def render_standard(text: str, name: str, blocks: dict[str, str]) -> str:
    """The launcher with its header and banner blocks as the canonical ones say; a launcher without the markers is returned as it is."""
    for key, begin, end in MARKERS:
        changed = replace_block(text, begin, end, blocks[key].replace(PLACEHOLDER, name))
        if changed is None:
            return text
        text = changed
    return text


def render_bridge(template: str, name: str) -> str:
    """A whole launcher of a bridge: the name written in, and the box lined up to the same column whatever the name."""
    out = []
    for line in template.split("\n"):
        if "<PAD>" in line:
            line = line.replace(PLACEHOLDER, name)
            head, _, tail = line.partition("<PAD>")
            lead = head[: head.index("*")]  # the quote or the `echo ` before the first star of the line
            used = len(head) - len(lead)
            line = lead + head[len(lead) :] + " " * max(1, BOX_WIDTH - 1 - used) + tail
        out.append(line.replace(PLACEHOLDER, name))
    return "\n".join(out)


def read_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), newline


def plan(workspace: Path, names: list[str] | None = None, banners: dict[str, dict] | None = None) -> list[tuple[Path, str, str]]:
    """(path, new text, newline) of every launcher whose text differs from what the canonical file generates."""
    banners = banners or load()
    todo: list[tuple[Path, str, str]] = []
    for repo in family_repos(workspace):
        if names and repo.name not in names:
            continue
        for script, blocks in banners["standard"].items():
            target = repo / script
            if not target.is_file() or (is_bridge(repo) and script in banners["bridge"]):
                continue
            current, newline = read_text(target)
            wanted = render_standard(current, repo.name, blocks)
            if wanted != current:
                todo.append((target, wanted, newline))
        if is_bridge(repo):
            for script, template in banners["bridge"].items():
                target = repo / script
                wanted = render_bridge(template, repo.name)
                current, newline = read_text(target) if target.is_file() else ("", "\n")
                if wanted != current:
                    todo.append((target, wanted, newline))
    return todo


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 when a launcher differs from the generated text")
    parser.add_argument("--workspace", type=Path, default=SDK_ROOT.parent)
    parser.add_argument("--repos", nargs="*", help="only these repositories")
    args = parser.parse_args(argv)
    workspace = args.workspace.resolve()
    todo = plan(workspace, args.repos)
    for target, text, newline in todo:
        label = f"{target.parent.name}/{target.name}"
        if args.check:
            print("differs from the generated text: " + label)
        else:
            target.write_bytes(text.replace("\n", newline).encode("utf-8"))
            print("rewritten: " + label)
    if args.check:
        print(f"SCRIPT_BANNERS={'FAIL' if todo else 'PASS'} drift={len(todo)}")
        return 1 if todo else 0
    print(f"SCRIPT_BANNERS=WRITTEN files={len(todo)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
