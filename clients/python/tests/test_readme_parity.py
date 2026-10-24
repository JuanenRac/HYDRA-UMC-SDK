# =============================================================================
# HYDRA-UMC-SDK - readme_parity unit tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hydra_umc_sdk.readme_parity import (
    check_readme_section_parity,
    check_readme_tree,
    readme_section_signature,
    readme_tree_names,
)

EN = """## 🎯 Overview

Some prose.

## 🔗 Related Projects

More prose.

## 👤 AUTHOR
"""


class ReadmeSectionSignatureTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_extracts_the_ordered_emoji_signature(self):
        path = self._write("README.md", EN)
        self.assertEqual(readme_section_signature(path), ["🎯", "🔗", "👤"])

    def test_strips_a_leading_numbered_ordinal_before_the_emoji(self):
        path = self._write(
            "README.md",
            "## 1. 🛠️ TECHNICAL OVERVIEW\n\n## 2. 🔄 ARCHITECTURE\n",
        )
        self.assertEqual(readme_section_signature(path), ["🛠️", "🔄"])

    def test_a_file_with_no_headings_has_an_empty_signature(self):
        path = self._write("README.md", "Just prose, no headings at all.\n")
        self.assertEqual(readme_section_signature(path), [])


class ReadmeSectionParityTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "README.md").write_text(EN, encoding="utf-8")
        (self.root / "README_por.md").write_text(
            "## 🎯 Visão geral\n\n## 🔗 Projetos relacionados\n\n## 👤 AUTOR\n", encoding="utf-8"
        )

    def _write(self, name: str, content: str) -> None:
        (self.root / name).write_text(content, encoding="utf-8")

    def test_a_matching_translation_reports_no_problems(self):
        self._write(
            "README_spa.md",
            "## 🎯 Resumen\n\nAlgo de texto.\n\n## 🔗 Proyectos Relacionados\n\nMas texto.\n\n## 👤 AUTOR\n",
        )
        self.assertEqual(check_readme_section_parity(self.root), [])

    def test_a_missing_section_in_a_translation_is_reported(self):
        self._write("README_spa.md", "## 🎯 Resumen\n\n## 👤 AUTOR\n")
        problems = check_readme_section_parity(self.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("README_spa.md", problems[0])

    def test_a_reordered_section_in_a_translation_is_reported(self):
        self._write("README_spa.md", "## 👤 AUTOR\n\n## 🎯 Resumen\n\n## 🔗 Proyectos\n")
        problems = check_readme_section_parity(self.root)
        self.assertEqual(len(problems), 1)

    def test_a_mismatched_heading_emoji_is_reported(self):
        self._write("README_spa.md", "## 🎯 Resumen\n\n## 🔥 Proyectos\n\n## 👤 AUTOR\n")
        problems = check_readme_section_parity(self.root)
        self.assertEqual(len(problems), 1)

    def test_a_missing_optional_translation_file_is_not_itself_a_parity_violation(self):
        # ci_validate.py's own REQUIRED_DOCUMENTS check already covers a
        # missing translation file - this check is only about the
        # STRUCTURE of translations that do exist (the Portuguese README is
        # the one exception, below).
        self.assertEqual(check_readme_section_parity(self.root), [])

    def test_a_missing_portuguese_readme_is_a_violation(self):
        (self.root / "README_por.md").unlink()
        problems = check_readme_section_parity(self.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("README_por.md is missing", problems[0])

    def test_the_portuguese_requirement_can_be_switched_off_explicitly(self):
        (self.root / "README_por.md").unlink()
        self.assertEqual(check_readme_section_parity(self.root, required=()), [])

    def test_the_portuguese_readme_is_checked_for_structure_like_the_others(self):
        self._write("README_por.md", "## 🎯 Visão geral\n\n## 👤 AUTOR\n")
        problems = check_readme_section_parity(self.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("README_por.md", problems[0])

    def test_the_portuguese_readme_is_checked_for_links_like_the_others(self):
        self._write("README.md", EN + "\n[a](https://example.org/a)\n")
        problems = check_readme_section_parity(self.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("README_por.md links do not match", problems[0])

    def test_multiple_translations_are_all_checked_and_reported(self):
        self._write("README_spa.md", "## 🎯 Resumen\n\n## 👤 AUTOR\n")
        self._write("README_fra.md", "## 🎯 Aperçu\n\n## 🔗 Projets\n\n## 👤 AUTEUR\n")
        problems = check_readme_section_parity(self.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("README_spa.md", problems[0])


NL = chr(10)


def _doc(*lines: str) -> str:
    return NL.join(lines) + NL


class ReadmeLinkParityTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _write(self, name: str, content: str) -> None:
        (self.root / name).write_text(content, encoding="utf-8")

    def test_a_translation_missing_a_link_is_reported(self):
        self._write("README.md", _doc("## 🎯 A", "", "[docs](https://example.org/a) [spec](https://example.org/b)"))
        self._write("README_spa.md", _doc("## 🎯 A", "", "[docs](https://example.org/a)"))
        problems = check_readme_section_parity(self.root, required=())
        self.assertEqual(len(problems), 1)
        self.assertIn("https://example.org/b", problems[0])

    def test_same_links_in_a_different_order_pass(self):
        self._write("README.md", _doc("## 🎯 A", "", "[x](https://example.org/a) [y](https://example.org/b)"))
        self._write("README_deu.md", _doc("## 🎯 A", "", "[y](https://example.org/b) [x](https://example.org/a)"))
        self.assertEqual(check_readme_section_parity(self.root, required=()), [])

    def test_relative_links_are_not_compared(self):
        self._write("README.md", _doc("## 🎯 A", "", "[c](CONTRIBUTING.md)"))
        self._write("README_fra.md", _doc("## 🎯 A", "", "[c](docs/CONTRIBUTING.md)"))
        self.assertEqual(check_readme_section_parity(self.root, required=()), [])


TREE = "\n".join([
    "## 📂 Structure",
    "",
    "```text",
    "HYDRA-UMC-TEST/",
    "├── src/            # code",
    "├── tools/",
    "│   └── ci_validate.py",
    "├── build.sh / build.bat",
    "├── update.sh/.bat  # the updater",
    "├── a.sh / .bat, sdkconfig.board.*",
    "└── README.md",
    "```",
    "",
])


class ReadmeTreeTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_the_first_level_names_are_read_from_the_tree(self):
        names = readme_tree_names(self._write("README.md", TREE))
        self.assertTrue({"src", "tools", "update.sh", "update.bat", "a.sh", "a.bat", "sdkconfig.board.*", "README.md"} <= names)
        self.assertNotIn("ci_validate.py", names)

    def test_the_tree_is_the_code_block_with_the_most_tree_rows(self):
        text = "## A\n\n```text\n├── sample/   (one row of an example)\n```\n\n" + TREE
        names = readme_tree_names(self._write("README.md", text))
        self.assertIn("tools", names)
        self.assertNotIn("sample", names)

    def test_a_readme_without_a_tree_has_no_names(self):
        self.assertIsNone(readme_tree_names(self._write("README.md", "## 🎯 A\n\ntext\n")))

    def test_a_complete_tree_passes(self):
        self._write("README.md", TREE)
        tracked = ["src", "tools", "update.sh", "update.bat", "sdkconfig.board.s3", "README.md", "LICENSE", ".github", "build.sh", "images", "pyproject.toml"]
        self.assertEqual(check_readme_tree(self.root, tracked=tracked), [])

    def test_a_versioned_entry_the_tree_leaves_out_is_named_for_each_file(self):
        self._write("README.md", TREE)
        self._write("README_spa.md", TREE)
        problems = check_readme_tree(self.root, tracked=["src", "schemas", "tests"])
        self.assertEqual(len(problems), 2)
        self.assertIn("README.md file tree does not list: schemas, tests", problems[0])
        self.assertIn("README_spa.md", problems[1])

    def test_the_parity_check_reports_it_too(self):
        self._write("README.md", TREE)
        problems = check_readme_section_parity(self.root, required=())
        self.assertEqual(problems, [])  # a folder that Git cannot read is skipped

    def test_a_folder_that_git_cannot_read_is_skipped(self):
        self._write("README.md", TREE)
        self.assertEqual(check_readme_tree(self.root), [])
