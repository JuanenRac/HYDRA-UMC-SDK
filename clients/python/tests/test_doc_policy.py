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

from hydra_umc_sdk.doc_policy import (
    check_build_scripts_do_not_bump,
    check_public_private_boundary,
    check_scripts_do_not_activate_venv,
)


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


class BuildScriptsDoNotBumpTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _write(self, name: str, content: str) -> None:
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def test_a_repository_without_scripts_passes(self):
        self.assertIsNone(check_build_scripts_do_not_bump(self.root))

    def test_a_build_that_only_reads_the_version_passes(self):
        self._write("build.sh", "#!/usr/bin/env bash\npython3 -m pytest\n")
        self._write("build.bat", "@echo off\npython -m pytest\n")
        self.assertIsNone(check_build_scripts_do_not_bump(self.root))

    def test_comments_and_printed_hints_may_name_the_bump_command(self):
        self._write("build.sh", "# bump_version.py is not run here\nprintf 'run: python tools/hydra_project_tool.py bump'\n")
        self._write("build.bat", "REM bump_manifest_version.py is not run here\necho run: python tools\\hydra_project_tool.py bump\n")
        self.assertIsNone(check_build_scripts_do_not_bump(self.root))

    def test_a_shell_build_that_runs_a_bump_script_fails(self):
        self._write("build.sh", "python3 bump_version.py || exit 1\n")
        self.assertIn("build.sh:1", check_build_scripts_do_not_bump(self.root))

    def test_a_batch_build_that_runs_the_manifest_bump_fails(self):
        self._write("build.bat", 'python "%~dp0bump_manifest_version.py" --sync\n')
        self.assertIn("build.bat:1", check_build_scripts_do_not_bump(self.root))

    def test_the_android_version_code_bump_fails_too(self):
        self._write("build-android.sh", "python3 bump_version_code.py\n")
        self.assertIn("build-android.sh:1", check_build_scripts_do_not_bump(self.root))

    def test_running_the_explicit_bump_command_from_a_build_fails(self):
        self._write("build.sh", "python3 tools/hydra_project_tool.py bump\n")
        self.assertIn("build.sh:1", check_build_scripts_do_not_bump(self.root))

    def test_scripts_in_the_scripts_folder_are_checked(self):
        self._write("scripts/release.sh", "python3 bump.py\n")
        self.assertIn("release.sh:1", check_build_scripts_do_not_bump(self.root))

    def test_an_npm_build_that_bumps_fails_but_a_bump_script_is_fine(self):
        self._write(
            "package.json",
            '{"scripts": {"build": "node scripts/bump-version.mjs && tsc", "bump": "node scripts/bump-version.mjs"}}',
        )
        message = check_build_scripts_do_not_bump(self.root)
        self.assertIn("package.json:build", message)
        self.assertNotIn("package.json:bump", message)


class VenvIsNeverActivatedTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _write(self, name: str, content: str) -> None:
        (self.root / name).write_text(content, encoding="utf-8")

    def test_scripts_that_run_the_venv_python_directly_pass(self):
        self._write("build.sh", '"$VPY" -m pytest\n')
        self._write("build.bat", '"%VPY%" -m pytest\n')
        self.assertIsNone(check_scripts_do_not_activate_venv(self.root))

    def test_comments_and_printed_text_may_mention_activate(self):
        self._write("build.sh", "# no activate script is used\necho 'activate the venv'\n")
        self._write("build.bat", "REM no activate.bat here\necho .venv has no activate script\n")
        self.assertIsNone(check_scripts_do_not_activate_venv(self.root))

    def test_sourcing_the_activate_script_fails(self):
        self._write("run.sh", "source .venv/bin/activate\n")
        self.assertIn("run.sh:1", check_scripts_do_not_activate_venv(self.root))

    def test_calling_activate_bat_fails(self):
        self._write("build.bat", "call .venv\\Scripts\\activate.bat\n")
        self.assertIn("build.bat:1", check_scripts_do_not_activate_venv(self.root))

    def test_probing_for_the_activate_script_fails_too(self):
        self._write("build.sh", "if [ -f .venv/bin/activate ]; then\n")
        self.assertIn("build.sh:1", check_scripts_do_not_activate_venv(self.root))
