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
    python tools/i18n_common.py render lng --lang pt          the lines of a SUITE language file (keys COMMON_<ID>)
    python tools/i18n_common.py check-suite --repo <SUITE>    every language/<name>.lng carries the COMMON_<ID> lines of the contract
    python tools/i18n_common.py check-android --repo <APP>    every res/values[-lang]/strings.xml carries the common_<id> lines of the contract
    python tools/i18n_common.py check-arb --repo <APP>        every lib/l10n/app_<lang>.arb carries the common<Id> entries of the contract

Each app keeps its own format; this file is the one place where the words are written. `check-studio` exits 0 when the eight catalogs carry every common
text as the contract writes it (a catalog may carry more under "common") and 1 with the list of what differs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xml.etree import ElementTree
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


# The language files of the SUITE are named in English and carry one KEY=text line per sentence; the common texts are the keys COMMON_<ID> (the id in capitals).
SUITE_FILES = {"en": "english", "es": "spanish", "de": "german", "fr": "french", "it": "italian", "ja": "japanese", "zh": "chinese", "pt": "portuguese"}


def render_lng(contract: dict, lang: str) -> str:
    return "".join(f"COMMON_{key.upper()}={value}\n" for key, value in texts(contract, lang).items())


def check_suite(contract: dict, repo: Path) -> list[str]:
    """What differs between the language files of a SUITE checkout and the contract; empty when it carries every common text."""
    problems: list[str] = []
    for lang in contract["languages"]:
        path = repo / "language" / f"{SUITE_FILES[lang]}.lng"
        if not path.is_file():
            problems.append(f"{lang}: {path} does not exist")
            continue
        carried: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            key, sep, value = line.partition("=")
            if sep and key.startswith("COMMON_"):
                carried[key] = value
        for key, want in texts(contract, lang).items():
            name = f"COMMON_{key.upper()}"
            if name not in carried:
                problems.append(f"{lang}: {name} is missing")
            elif carried[name] != want:
                problems.append(f"{lang}: {name} is {carried[name]!r}, the contract says {want!r}")
    return problems


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


def _android_unescape(text: str) -> str:
    return text.replace("\\'", "'").replace('\\"', '"')


def check_android(contract: dict, repo: Path) -> list[str]:
    """What differs between the `strings.xml` files of an Android checkout (values/ and values-<lang>/) and the contract; empty when it carries every common text."""
    problems: list[str] = []
    for lang in contract["languages"]:
        folder = "values" if lang == "en" else f"values-{lang}"
        path = repo / "app" / "src" / "main" / "res" / folder / "strings.xml"
        if not path.is_file():
            problems.append(f"{lang}: {path} does not exist")
            continue
        try:
            root = ElementTree.fromstring(path.read_bytes())
        except ElementTree.ParseError as error:
            problems.append(f"{lang}: {path} is not valid XML ({error})")
            continue
        carried = {element.get("name"): _android_unescape("".join(element.itertext())) for element in root.findall("string")}
        for key, want in texts(contract, lang).items():
            name = f"common_{key}"
            if name not in carried:
                problems.append(f"{lang}: {name} is missing")
            elif carried[name] != want:
                problems.append(f"{lang}: {name} is {carried[name]!r}, the contract says {want!r}")
    return problems


def check_arb(contract: dict, repo: Path) -> list[str]:
    """What differs between the ARB files of a Flutter checkout (lib/l10n/app_<lang>.arb) and the contract; empty when it carries every common text."""
    problems: list[str] = []
    for lang in contract["languages"]:
        path = repo / "lib" / "l10n" / f"app_{lang}.arb"
        if not path.is_file():
            problems.append(f"{lang}: {path} does not exist")
            continue
        try:
            carried = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as error:
            problems.append(f"{lang}: {path} is not valid JSON ({error})")
            continue
        for key, want in texts(contract, lang).items():
            name = f"common{_camel(key)}"
            if name not in carried:
                problems.append(f"{lang}: {name} is missing")
            elif carried[name] != want:
                problems.append(f"{lang}: {name} is {carried[name]!r}, the contract says {want!r}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The common texts of the apps, in the format of each app.")
    sub = parser.add_subparsers(dest="command", required=True)
    render = sub.add_parser("render", help="write the texts in the format of an app")
    render.add_argument("format", choices=["studio", "android", "arb", "lng"])
    render.add_argument("--lang", required=True)
    check = sub.add_parser("check-studio", help="check that a STUDIO checkout carries the texts")
    check.add_argument("--repo", required=True, type=Path)
    check_suite_parser = sub.add_parser("check-suite", help="check that a SUITE checkout carries the texts")
    check_suite_parser.add_argument("--repo", required=True, type=Path)
    check_android_parser = sub.add_parser("check-android", help="check that an Android checkout carries the texts")
    check_android_parser.add_argument("--repo", required=True, type=Path)
    check_arb_parser = sub.add_parser("check-arb", help="check that a Flutter (ARB) checkout carries the texts")
    check_arb_parser.add_argument("--repo", required=True, type=Path)
    arguments = parser.parse_args(argv)
    contract = load()
    if arguments.command == "render":
        try:
            writer = {"studio": render_studio, "android": render_android, "arb": render_arb, "lng": render_lng}[arguments.format]
            sys.stdout.write(writer(contract, arguments.lang))
        except ValueError as error:
            print(f"I18N_COMMON=FAIL {error}", file=sys.stderr)
            return 2
        return 0
    checkers = {"check-suite": check_suite, "check-studio": check_studio, "check-android": check_android, "check-arb": check_arb}
    problems = checkers[arguments.command](contract, arguments.repo)
    for problem in problems:
        print(problem)
    print(f"I18N_COMMON={'FAIL' if problems else 'PASS'} {len(contract['strings'])} texts x {len(contract['languages'])} languages")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
