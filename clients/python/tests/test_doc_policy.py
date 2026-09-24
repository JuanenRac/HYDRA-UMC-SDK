# =============================================================================
# HYDRA-UMC-SDK - doc_policy unit tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Real regression coverage for this project's own canonical public/private
documentation boundary check - a real, throwaway git repository per test
(this check shells out to `git grep`, so a fake filesystem alone would
never exercise the actual command it runs), not a mock of subprocess."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from hydra_umc_sdk.doc_policy import check_public_private_boundary


class DocPolicyTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self._run("git", "init", "-q")
        self._run("git", "config", "user.email", "test@example.com")
        self._run("git", "config", "user.name", "Test")

    def _run(self, *args: str) -> None:
        subprocess.run(args, cwd=self.root, check=True, capture_output=True, text=True)

    def _commit(self, name: str, content: str) -> None:
        (self.root / name).write_text(content, encoding="utf-8")
        self._run("git", "add", "--", name)
        self._run("git", "commit", "-q", "-m", f"add {name}")

    def test_a_clean_tree_passes(self):
        self._commit("README.md", "Nothing private here.\n")
        self.assertIsNone(check_public_private_boundary(self.root))

    def test_rejects_the_bare_private_marker(self):
        self._commit("README.md", "See SON" + "NET for internal notes.\n")
        self.assertEqual(
            check_public_private_boundary(self.root),
            "public files must not reference private documentation",
        )

    def test_rejects_the_second_bare_marker(self):
        self._commit("README.md", "The BIB" + "LIA has the full plan.\n")
        self.assertEqual(
            check_public_private_boundary(self.root),
            "public files must not reference private documentation",
        )

    def test_rejects_a_private_phrase_even_without_the_bare_marker(self):
        self._commit("CHANGELOG.md", "See this repo's own internal work" + " log.\n")
        self.assertEqual(
            check_public_private_boundary(self.root),
            "public files must not reference private planning or audit documents",
        )

    def test_rejects_the_spanish_phrase_too(self):
        self._commit("README_spa.md", "Consulta el registro de trabajo" + " interno.\n")
        self.assertEqual(
            check_public_private_boundary(self.root),
            "public files must not reference private planning or audit documents",
        )

    def test_phrase_match_is_case_insensitive(self):
        self._commit("README.md", "See the Internal Work" + " Log.\n")
        self.assertEqual(
            check_public_private_boundary(self.root),
            "public files must not reference private planning or audit documents",
        )

    def test_an_unrelated_use_of_a_common_word_does_not_trip_the_phrase_check(self):
        self._commit("README.md", "This service keeps an audit trail and a work log of its own runs.\n")
        self.assertIsNone(check_public_private_boundary(self.root))

    def test_rejects_an_internal_tracking_code(self):
        for code in ("V07" + "-012", "REV" + "-004", "PROM" + "-HUB-F02", "DOC" + "-BUG-7"):
            with self.subTest(code=code):
                self._commit("notes.md", f"// {code}: a leaked label" + chr(10))
                self.assertEqual(
                    check_public_private_boundary(self.root),
                    "public files must not carry internal tracking codes",
                )
                self._run("git", "rm", "-q", "-f", "notes.md")
                self._run("git", "commit", "-q", "-m", "remove")

    def test_rejects_a_private_memory_link(self):
        link = "[" + "[project_" + "some_note]" + "]"
        self._commit("main.py", "# see " + link + chr(10))
        self.assertEqual(
            check_public_private_boundary(self.root),
            "public files must not carry internal tracking codes",
        )

    def test_part_numbers_and_ordinary_names_are_not_tracking_codes(self):
        self._commit("README.md", "Capacitor C10, the H745 MCU, UTF-8 and SHA-256, REV A board." + chr(10))
        self.assertIsNone(check_public_private_boundary(self.root))
