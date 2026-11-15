# =============================================================================
# HYDRA-UMC-SDK - Tests of the common texts of the apps
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""contracts/i18n/common.json and tools/i18n_common.py: the words every app shows the same way, in the eight languages."""
from __future__ import annotations

import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "contracts" / "i18n" / "common.json"
LANGS = ["en", "es", "de", "fr", "it", "ja", "zh", "pt"]

_spec = importlib.util.spec_from_file_location("i18n_common", ROOT / "tools" / "i18n_common.py")
assert _spec is not None and _spec.loader is not None
TOOL = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TOOL)


class ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_the_eight_languages_in_the_order_of_the_project(self) -> None:
        self.assertEqual(self.data["languages"], LANGS)

    def test_every_text_is_written_in_every_language_and_none_is_empty(self) -> None:
        for entry in self.data["strings"]:
            self.assertEqual(sorted(entry["text"]), sorted(LANGS), entry["id"])
            for lang, text in entry["text"].items():
                self.assertTrue(text.strip(), f"{entry['id']} in {lang}")

    def test_the_ids_are_unique_lowercase_words(self) -> None:
        ids = [entry["id"] for entry in self.data["strings"]]
        self.assertEqual(len(ids), len(set(ids)))
        for key in ids:
            self.assertRegex(key, r"^[a-z]+(_[a-z]+)*$")

    def test_portuguese_is_the_one_of_portugal(self) -> None:
        pt = TOOL.texts(self.data, "pt")
        self.assertEqual(pt["loading"], "A carregar…")
        self.assertEqual(pt["offline"], "Desligado")
        for word in ("carregando", "arquivo", "tela"):
            self.assertFalse(any(word in text.lower() for text in pt.values()), word)

    def test_no_text_keeps_a_marker_of_unfinished_work(self) -> None:
        for entry in self.data["strings"]:
            for text in entry["text"].values():
                self.assertIsNone(re.search(r"TODO|FIXME|XXX|\?\?\?", text), entry["id"])


    def test_a_text_has_no_form_that_belongs_to_the_screen(self) -> None:
        # capitals, a colon, a leading lower case: the screen applies them (CSS, a label with a colon), the contract keeps one plain form
        for entry in self.data["strings"]:
            for lang, text in entry["text"].items():
                self.assertFalse(text.rstrip().endswith((":", "\uff1a")), f"{entry['id']} in {lang} ends with a colon")
                if len(text) > 3 and text.isascii():
                    self.assertFalse(text.isupper(), f"{entry['id']} in {lang} is all capitals")
                self.assertFalse(text[:1].islower(), f"{entry['id']} in {lang} starts in lower case")

    def test_the_hundred_common_words_include_the_ones_the_apps_wrote_alike(self) -> None:
        ids = {entry["id"] for entry in self.data["strings"]}
        self.assertEqual(len(ids), 100)
        for word in ("stop", "start", "off", "default", "continue", "connecting", "settings", "security", "sign_out", "username",
                     "dashboard", "voice_assistant", "all_robots", "select_a_robot", "system_default"):
            self.assertIn(word, ids)
        es = TOOL.texts(self.data, "es")
        self.assertEqual(es["stop"], "Detener")
        self.assertEqual(TOOL.texts(self.data, "fr")["username"], "Nom d'utilisateur")


class RendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = TOOL.load()

    def test_studio_is_a_json_object_of_the_ids(self) -> None:
        block = json.loads(TOOL.render_studio(self.data, "de"))
        self.assertEqual(block["cancel"], "Abbrechen")
        self.assertEqual(list(block), [entry["id"] for entry in self.data["strings"]])

    def test_android_lines_are_escaped_and_named_common_id(self) -> None:
        xml = TOOL.render_android(self.data, "fr")
        self.assertIn('<string name="common_retry">Réessayer</string>', xml)
        self.assertEqual(xml.count("<string "), len(self.data["strings"]))
        # an apostrophe, a quote and an ampersand cannot break the XML of an app
        fake = {"languages": ["en"], "strings": [{"id": "odd", "text": {"en": "It's \"a\" & <b>"}}]}
        self.assertEqual(TOOL.render_android(fake, "en"), '    <string name="common_odd">It\\\'s \\"a\\" &amp; &lt;b&gt;</string>\n')

    def test_arb_keys_are_camel_case(self) -> None:
        arb = json.loads(TOOL.render_arb(self.data, "es"))
        self.assertEqual(arb["commonSave"], "Guardar")
        self.assertEqual(len(arb), len(self.data["strings"]))
        fake = {"languages": ["en"], "strings": [{"id": "two_words", "text": {"en": "x"}}]}
        self.assertEqual(list(json.loads(TOOL.render_arb(fake, "en"))), ["commonTwoWords"])

    def test_an_unknown_language_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            TOOL.texts(self.data, "xx")
        self.assertEqual(TOOL.main(["render", "studio", "--lang", "xx"]), 2)

    def test_the_command_line_prints_the_block(self) -> None:
        import contextlib
        import io

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(TOOL.main(["render", "arb", "--lang", "ja"]), 0)
        self.assertEqual(json.loads(out.getvalue())["commonSave"], "保存")


class CheckStudioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = TOOL.load()

    def _repo(self, tmp: str, change=None) -> Path:
        repo = Path(tmp)
        (repo / "src" / "locales").mkdir(parents=True)
        for lang in LANGS:
            catalogue = {"other": {"x": "y"}, "common": TOOL.texts(self.data, lang)}
            if change:
                change(lang, catalogue)
            (repo / "src" / "locales" / f"{lang}.json").write_text(json.dumps(catalogue, ensure_ascii=False), encoding="utf-8")
        return repo

    def test_a_catalogue_that_carries_every_text_passes_and_may_carry_more(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(tmp, lambda lang, cat: cat["common"].update({"own": "only here"}))
            self.assertEqual(TOOL.check_studio(self.data, repo), [])
            self.assertEqual(TOOL.main(["check-studio", "--repo", str(repo)]), 0)

    def test_a_missing_or_different_text_is_listed(self) -> None:
        def change(lang: str, cat: dict) -> None:
            if lang == "pt":
                del cat["common"]["save"]
            if lang == "it":
                cat["common"]["close"] = "Chiudere"

        with tempfile.TemporaryDirectory() as tmp:
            problems = TOOL.check_studio(self.data, self._repo(tmp, change))
            self.assertEqual(len(problems), 2)
            self.assertTrue(any(p.startswith("pt: common.save is missing") for p in problems))
            self.assertTrue(any(p.startswith("it: common.close is 'Chiudere'") for p in problems))
            self.assertEqual(TOOL.main(["check-studio", "--repo", tmp]), 1)

    def test_a_missing_catalogue_is_listed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(tmp)
            (repo / "src" / "locales" / "zh.json").unlink()
            problems = TOOL.check_studio(self.data, repo)
            self.assertEqual(len(problems), 1)
            self.assertIn("zh", problems[0])

    def test_the_studio_next_to_this_checkout_carries_the_texts_when_it_is_there(self) -> None:
        repo = ROOT.parent / "HYDRA-UMC-STUDIO"
        if not (repo / "src" / "locales" / "en.json").is_file():
            self.skipTest("HYDRA-UMC-STUDIO is not next to this checkout")
        # the sibling can be one commit behind this contract: what is checked is that the texts it carries are the ones of the contract
        for problem in TOOL.check_studio(self.data, repo):
            self.assertIn("is missing", problem, problem)


class SuiteLanguageFileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = TOOL.load()

    def _repo(self, tmp: str, change=None) -> Path:
        repo = Path(tmp)
        (repo / "language").mkdir(parents=True)
        for lang in LANGS:
            lines = ["BTN_SAVE=Own save", "TITLE=A title with = inside"] + TOOL.render_lng(self.data, lang).splitlines()
            if change:
                lines = change(lang, lines)
            (repo / "language" / f"{TOOL.SUITE_FILES[lang]}.lng").write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")
        return repo

    def test_the_lines_are_one_key_per_common_text_in_capitals(self) -> None:
        lines = TOOL.render_lng(self.data, "pt").splitlines()
        self.assertEqual(len(lines), len(self.data["strings"]))
        self.assertEqual(lines[0], "COMMON_CONFIRM=Confirmar")
        self.assertTrue(all(re.fullmatch(r"COMMON_[A-Z_]+=.+", line) for line in lines))
        self.assertEqual(TOOL.main(["render", "lng", "--lang", "xx"]), 2)

    def test_a_language_file_that_carries_every_text_passes_and_may_carry_more(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(tmp)
            self.assertEqual(TOOL.check_suite(self.data, repo), [])
            self.assertEqual(TOOL.main(["check-suite", "--repo", str(repo)]), 0)

    def test_a_missing_or_different_text_is_listed(self) -> None:
        def change(lang: str, lines: list[str]) -> list[str]:
            if lang == "pt":
                return [line for line in lines if not line.startswith("COMMON_SAVE=")]
            if lang == "it":
                return [line.replace("COMMON_CLOSE=Chiudi", "COMMON_CLOSE=Chiudere") for line in lines]
            return lines

        with tempfile.TemporaryDirectory() as tmp:
            problems = TOOL.check_suite(self.data, self._repo(tmp, change))
            self.assertEqual(len(problems), 2)
            self.assertTrue(any(p.startswith("pt: COMMON_SAVE is missing") for p in problems))
            self.assertTrue(any(p.startswith("it: COMMON_CLOSE is 'Chiudere'") for p in problems))
            self.assertEqual(TOOL.main(["check-suite", "--repo", tmp]), 1)

    def test_a_missing_file_is_listed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(tmp)
            (repo / "language" / "chinese.lng").unlink()
            problems = TOOL.check_suite(self.data, repo)
            self.assertEqual(len(problems), 1)
            self.assertIn("zh", problems[0])

    def test_the_suite_next_to_this_checkout_carries_the_texts_when_it_is_there(self) -> None:
        repo = ROOT.parent / "HYDRA-UMC-SUITE"
        if not (repo / "language" / "english.lng").is_file():
            self.skipTest("no HYDRA-UMC-SUITE checkout next to this one")
        problems = TOOL.check_suite(self.data, repo)
        if problems and not any("COMMON_" in problem and "is missing" not in problem for problem in problems):
            self.skipTest("the SUITE next to this checkout has not taken the common texts yet")
        self.assertEqual(problems, [])


class CheckAppFormatTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = TOOL.load()

    def _android(self, tmp: str, change=None) -> Path:
        repo = Path(tmp)
        for lang in LANGS:
            folder = repo / "app" / "src" / "main" / "res" / ("values" if lang == "en" else f"values-{lang}")
            folder.mkdir(parents=True)
            lines = ['    <string name="app_name">Own</string>'] + TOOL.render_android(self.data, lang).splitlines()
            if change:
                lines = change(lang, lines)
            (folder / "strings.xml").write_text('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n' + "\n".join(lines) + "\n</resources>\n", encoding="utf-8")
        return repo

    def _arb(self, tmp: str, change=None) -> Path:
        repo = Path(tmp)
        (repo / "lib" / "l10n").mkdir(parents=True)
        for lang in LANGS:
            entries = {"@@locale": lang, "ownKey": "Own", **json.loads(TOOL.render_arb(self.data, lang))}
            if change:
                change(lang, entries)
            (repo / "lib" / "l10n" / f"app_{lang}.arb").write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
        return repo

    def test_an_android_app_that_carries_every_text_passes_and_may_carry_more(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._android(tmp)
            self.assertEqual(TOOL.check_android(self.data, repo), [])
            self.assertEqual(TOOL.main(["check-android", "--repo", str(repo)]), 0)

    def test_an_android_text_that_is_missing_or_different_is_listed(self) -> None:
        def change(lang: str, lines: list[str]) -> list[str]:
            if lang == "pt":
                return [line for line in lines if 'name="common_save"' not in line]
            if lang == "fr":
                return [line.replace("Nom d\\'utilisateur", "Identifiant") for line in lines]
            return lines

        with tempfile.TemporaryDirectory() as tmp:
            problems = TOOL.check_android(self.data, self._android(tmp, change))
            self.assertEqual(len(problems), 2)
            self.assertTrue(any(p.startswith("pt: common_save is missing") for p in problems))
            self.assertTrue(any(p.startswith("fr: common_username is 'Identifiant'") for p in problems))
            self.assertEqual(TOOL.main(["check-android", "--repo", tmp]), 1)

    def test_an_android_file_that_is_missing_or_broken_is_listed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._android(tmp)
            (repo / "app" / "src" / "main" / "res" / "values-zh" / "strings.xml").unlink()
            (repo / "app" / "src" / "main" / "res" / "values-ja" / "strings.xml").write_text("<resources>", encoding="utf-8")
            problems = TOOL.check_android(self.data, repo)
            self.assertEqual(len(problems), 2)
            self.assertTrue(any(p.startswith("zh:") and "does not exist" in p for p in problems))
            self.assertTrue(any(p.startswith("ja:") and "not valid XML" in p for p in problems))

    def test_an_arb_app_that_carries_every_text_passes_and_may_carry_more(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._arb(tmp)
            self.assertEqual(TOOL.check_arb(self.data, repo), [])
            self.assertEqual(TOOL.main(["check-arb", "--repo", str(repo)]), 0)

    def test_an_arb_text_that_is_missing_or_different_is_listed(self) -> None:
        def change(lang: str, entries: dict) -> None:
            if lang == "de":
                del entries["commonSave"]
            if lang == "it":
                entries["commonStop"] = "Stop"

        with tempfile.TemporaryDirectory() as tmp:
            problems = TOOL.check_arb(self.data, self._arb(tmp, change))
            self.assertEqual(len(problems), 2)
            self.assertTrue(any(p.startswith("de: commonSave is missing") for p in problems))
            self.assertTrue(any(p.startswith("it: commonStop is 'Stop'") for p in problems))
            self.assertEqual(TOOL.main(["check-arb", "--repo", tmp]), 1)

    def test_an_arb_file_that_is_missing_or_broken_is_listed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._arb(tmp)
            (repo / "lib" / "l10n" / "pt.arb").write_text("x", encoding="utf-8")
            (repo / "lib" / "l10n" / "app_pt.arb").write_text("{", encoding="utf-8")
            (repo / "lib" / "l10n" / "app_es.arb").unlink()
            problems = TOOL.check_arb(self.data, repo)
            self.assertEqual(len(problems), 2)
            self.assertTrue(any(p.startswith("es:") and "does not exist" in p for p in problems))
            self.assertTrue(any(p.startswith("pt:") and "not valid JSON" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
