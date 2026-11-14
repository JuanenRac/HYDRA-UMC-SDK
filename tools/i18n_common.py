#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - tools/i18n_common.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The common texts of the apps (contracts/i18n/common.json) written in the format of each app, and the check that an app carries them.

    python tools/i18n_common.py render studio --lang pt       the "common" object of a STUDIO catalog (JSON)
    python tools/i18n_common.py render android --lang pt      the lines of a strings.xml (names common_<id>)
    python tools/i18n_common.py render arb --lang pt          the entries of an ARB file (keys common<Id>)
    python tools/i18n_common.py check-studio --repo <STUDIO>  every src/locales/<lang>.json carries the "common" texts of the contract

Each app keeps its own format; this file is the one place where the words are written. `check-studio` exits 0 when the eight catalogs carry every common
text as the contract writes it (a catalog may carry more under "common") and 1 with the list of what differs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "i18n" / "common.json"


def load(path: Path = CONTRACT) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def texts(contract: dict, lang: str) -> dict[str, str]:
    """The text of every common string in `lang`, by id."""
    if lang not in contract["languages"]:
        raise ValueError(f"unknown language {lang!r}")
    return {entry["id"]: entry["text"][lang] for entry in contract["strings"]}


def render_studio(contract: dict, lang: str) -> str:
    return json.dumps(texts(contract, lang), ensure_ascii=False, indent=2) + "\n"


def _android_escape(text: str) -> str:
    return escape(text).replace("'", "\\'").replace('"', '\\"')


def render_android(contract: dict, lang: str) -> str:
    return "".join(f'    <string name="common_{key}">{_android_escape(value)}</string>\n' for key, value in texts(contract, lang).items())


def _camel(key: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in key.split("_"))


def render_arb(contract: dict, lang: str) -> str:
    entries = {f"common{_camel(key)}": value for key, value in texts(contract, lang).items()}
    return json.dumps(entries, ensure_ascii=False, indent=2) + "\n"


def check_studio(contract: dict, repo: Path) -> list[str]:
    """What differs between the catalogs of a STUDIO checkout and the contract; empty when it carries every common text."""
    problems: list[str] = []
    for lang in contract["languages"]:
        path = repo / "src" / "locales" / f"{lang}.json"
        if not path.is_file():
            problems.append(f"{lang}: {path} does not exist")
            continue
        carried = json.loads(path.read_text(encoding="utf-8")).get("common", {})
        for key, want in texts(contract, lang).items():
            if key not in carried:
                problems.append(f"{lang}: common.{key} is missing")
            elif carried[key] != want:
                problems.append(f"{lang}: common.{key} is {carried[key]!r}, the contract says {want!r}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The common texts of the apps, in the format of each app.")
    sub = parser.add_subparsers(dest="command", required=True)
    render = sub.add_parser("render", help="write the texts in the format of an app")
    render.add_argument("format", choices=["studio", "android", "arb"])
    render.add_argument("--lang", required=True)
    check = sub.add_parser("check-studio", help="check that a STUDIO checkout carries the texts")
    check.add_argument("--repo", required=True, type=Path)
    arguments = parser.parse_args(argv)
    contract = load()
    if arguments.command == "render":
        try:
            writer = {"studio": render_studio, "android": render_android, "arb": render_arb}[arguments.format]
            sys.stdout.write(writer(contract, arguments.lang))
        except ValueError as error:
            print(f"I18N_COMMON=FAIL {error}", file=sys.stderr)
            return 2
        return 0
    problems = check_studio(contract, arguments.repo)
    for problem in problems:
        print(problem)
    print(f"I18N_COMMON={'FAIL' if problems else 'PASS'} {len(contract['strings'])} texts x {len(contract['languages'])} languages")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
