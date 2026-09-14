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
    readme_section_signature,
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

    def test_a_missing_translation_file_is_not_itself_a_parity_violation(self):
        # ci_validate.py's own REQUIRED_DOCUMENTS check already covers a
        # missing translation file - this check is only about the
        # STRUCTURE of translations that do exist.
        self.assertEqual(check_readme_section_parity(self.root), [])

    def test_multiple_translations_are_all_checked_and_reported(self):
        self._write("README_spa.md", "## 🎯 Resumen\n\n## 👤 AUTOR\n")
        self._write("README_fra.md", "## 🎯 Aperçu\n\n## 🔗 Projets\n\n## 👤 AUTEUR\n")
        problems = check_readme_section_parity(self.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("README_spa.md", problems[0])
