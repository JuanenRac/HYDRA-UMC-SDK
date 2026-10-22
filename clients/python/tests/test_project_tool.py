# =============================================================================
# HYDRA-UMC-SDK - tests of tools/canonical/hydra_project_tool.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The project tool runs against a throwaway git repository with the real
canonical bump utility copied in, so `bump` is exercised for real."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

CANONICAL = Path(__file__).resolve().parents[3] / "tools" / "canonical"


def _load():
    spec = importlib.util.spec_from_file_location("hydra_project_tool", CANONICAL / "hydra_project_tool.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TOOL = _load()


class ProjectToolTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "tools").mkdir()
        shutil.copy(CANONICAL / "bump_manifest_version.py", self.root / "bump_manifest_version.py")
        (self.root / "VERSION.txt").write_text("version=0.1.4\n", encoding="utf-8")
        (self.root / "CHANGELOG.md").write_text("# Changelog\n\n## [0.1.4]\n\n- first\n", encoding="utf-8")
        self.write_manifest("0.1.4")
        self.git("init", "-q")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "T")
        self.commit("start")

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, check=True)

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def write_manifest(self, version: str) -> None:
        manifest = {
            "version": version,
            "native_version": {"file": "VERSION.txt", "pattern": r"version=(\d+)\.(\d+)\.(\d+)"},
        }
        (self.root / "hydra-umc.project.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    def script(self, name: str, body: str) -> None:
        (self.root / "tools" / name).write_text(body, encoding="utf-8")

    def test_next_version_follows_the_odometer(self):
        self.assertEqual(TOOL.next_version(self.root), "0.1.5")
        self.write_manifest("0.7.9")
        self.assertEqual(TOOL.next_version(self.root), "0.8.0.0")

    def test_a_passing_check_succeeds_and_sees_the_ci_flag(self):
        self.script("ci_validate.py", "import os, sys\nsys.exit(0 if os.environ.get('HYDRA_UMC_CI') == '1' else 3)\n")
        self.assertEqual(TOOL.non_mutating("ci_validate.py", self.root), 0)

    def test_a_failing_check_returns_its_exit_code(self):
        self.script("build_test.py", "raise SystemExit(7)\n")
        self.assertEqual(TOOL.non_mutating("build_test.py", self.root), 7)

    def test_a_check_that_bumps_the_version_fails(self):
        self.script(
            "build_test.py",
            "import json, pathlib\n"
            "p = pathlib.Path(__file__).resolve().parent.parent / 'hydra-umc.project.json'\n"
            "d = json.loads(p.read_text()); d['version'] = '0.1.5'; p.write_text(json.dumps(d))\n",
        )
        self.assertEqual(TOOL.non_mutating("build_test.py", self.root), 1)

    def test_a_missing_script_fails(self):
        self.assertEqual(TOOL.non_mutating("build_test.py", self.root), 1)

    def test_dry_run_writes_nothing(self):
        self.assertEqual(TOOL.bump(self.root, dry_run=True), 0)
        self.assertEqual(TOOL.declared_version(self.root), "0.1.4")
        self.assertEqual(self.git("status", "--porcelain").stdout, "")

    def test_bump_moves_the_manifest_the_native_file_and_the_changelog(self):
        self.assertEqual(TOOL.bump(self.root), 0)
        self.assertEqual(TOOL.declared_version(self.root), "0.1.5")
        self.assertIn("version=0.1.5", (self.root / "VERSION.txt").read_text())
        self.assertIn("## [0.1.5]", (self.root / "CHANGELOG.md").read_text())

    def test_a_repository_with_only_its_own_bump_script_is_bumped_by_it(self):
        (self.root / "bump_manifest_version.py").unlink()
        (self.root / "tools" / "bump_version.py").write_text(
            "import json, pathlib\n"
            "root = pathlib.Path(__file__).resolve().parent.parent\n"
            "p = root / 'hydra-umc.project.json'\n"
            "d = json.loads(p.read_text())\n"
            "d['version'] = '0.1.5'\n"
            "p.write_text(json.dumps(d))\n",
            encoding="utf-8",
        )
        self.commit("bridge style")
        self.assertIsNone(TOOL.next_version(self.root))
        self.assertEqual(TOOL.bump(self.root), 0)
        self.assertEqual(TOOL.declared_version(self.root), "0.1.5")

    def test_a_repository_with_no_bump_script_at_all_cannot_be_bumped(self):
        (self.root / "bump_manifest_version.py").unlink()
        self.commit("no bump tool")
        self.assertEqual(TOOL.bump(self.root), 1)

    def test_bump_refuses_a_dirty_tree_unless_allowed(self):
        (self.root / "notes.txt").write_text("work in progress\n", encoding="utf-8")
        self.assertEqual(TOOL.bump(self.root), 1)
        self.assertEqual(TOOL.declared_version(self.root), "0.1.4")
        self.assertEqual(TOOL.bump(self.root, allow_dirty=True), 0)
        self.assertEqual(TOOL.declared_version(self.root), "0.1.5")

    def test_bump_runs_the_repository_own_script_first(self):
        # An own bump script that already moved the native file; the shared tool then only synchronises.
        (self.root / "bump_version.py").write_text(
            "import pathlib\np = pathlib.Path(__file__).resolve().parent / 'VERSION.txt'\n"
            "p.write_text('version=0.1.5\\n')\n",
            encoding="utf-8",
        )
        self.commit("own bump script")
        self.assertEqual(TOOL.bump(self.root), 0)
        self.assertEqual(TOOL.declared_version(self.root), "0.1.5")

    def test_status_flags_a_dirty_tree_and_a_version_behind_the_tag(self):
        self.assertEqual(TOOL.status(self.root), 0)
        self.git("tag", "v0.1.4")
        self.assertEqual(TOOL.status(self.root), 0)
        self.git("tag", "v0.2.0")
        self.assertEqual(TOOL.status(self.root), 1)
        self.git("tag", "-d", "v0.2.0")
        (self.root / "x.txt").write_text("x", encoding="utf-8")
        self.assertEqual(TOOL.status(self.root), 1)

    def test_the_last_tag_is_the_highest_version_not_the_latest_name(self):
        for tag in ("v0.1.9", "v0.1.10", "v0.1.2"):
            self.git("tag", tag)
        self.assertEqual(TOOL.last_tag_version(self.root), "0.1.10")


if __name__ == "__main__":
    unittest.main()
