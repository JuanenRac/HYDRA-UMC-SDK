# =============================================================================
# HYDRA-UMC-SDK - ecosystem release file tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The tool that writes `ecosystem-release.json`, and the check of the shared validator, on throw-away repositories."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[3] / "tools"


def _load(name: str, path: Path):
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))  # the validator imports the vendored helpers that sit next to it in a repository
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class EcosystemReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tool = _load("ecosystem_release_tool", TOOLS / "ecosystem_release.py")
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)

    def _git(self, repo: Path, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()

    def _repo(self, name: str, version: str) -> Path:
        repo = self.workspace / name
        repo.mkdir()
        self._git(repo, "init", "-q")
        self._git(repo, "config", "user.email", "test@example.com")
        self._git(repo, "config", "user.name", "Test")
        (repo / "hydra-umc.project.json").write_text(json.dumps({"version": version}) + "\n", encoding="utf-8")
        self._git(repo, "add", "--", "hydra-umc.project.json")
        self._git(repo, "commit", "-q", "-m", "start")
        return repo

    def test_the_file_lists_every_repository_sorted_with_version_and_commit(self):
        b = self._repo("HYDRA-UMC-B", "0.8.0.2")
        a = self._repo("HYDRA-UMC-A", "0.1.5")
        (self.workspace / "other").mkdir()
        data = self.tool.build(self.workspace)
        self.assertEqual(
            data["repositories"],
            [
                {"name": "HYDRA-UMC-A", "version": "0.1.5", "commit": self._git(a, "rev-parse", "HEAD")},
                {"name": "HYDRA-UMC-B", "version": "0.8.0.2", "commit": self._git(b, "rev-parse", "HEAD")},
            ],
        )
        self.assertEqual(self.tool.problems_of_file(data), [])
        self.assertEqual(self.tool.check(data, self.workspace), [])

    def test_a_listed_version_ahead_of_the_manifest_is_refused(self):
        self._repo("HYDRA-UMC-A", "0.1.5")
        data = self.tool.build(self.workspace)
        data["repositories"][0]["version"] = "0.1.6"
        self.assertTrue(any("ahead of the manifest" in line for line in self.tool.check(data, self.workspace)))

    def test_a_later_manifest_version_and_a_later_commit_are_fine(self):
        repo = self._repo("HYDRA-UMC-A", "0.1.5")
        data = self.tool.build(self.workspace)
        (repo / "hydra-umc.project.json").write_text(json.dumps({"version": "0.1.6"}) + "\n", encoding="utf-8")
        self._git(repo, "commit", "-q", "-am", "next")
        self.assertEqual(self.tool.check(data, self.workspace), [])

    def test_a_commit_that_is_not_in_the_history_is_refused(self):
        self._repo("HYDRA-UMC-A", "0.1.5")
        data = self.tool.build(self.workspace)
        data["repositories"][0]["commit"] = "0" * 40
        self.assertTrue(any("not in the history" in line for line in self.tool.check(data, self.workspace)))

    def test_a_malformed_file_is_described(self):
        bad = {"schema_version": "9", "ecosystem": "X", "repositories": [{"name": "HYDRA-UMC-B", "version": "1", "commit": "z"}, {"name": "HYDRA-UMC-A"}]}
        text = " ".join(self.tool.problems_of_file(bad))
        for needle in ("schema_version", "ecosystem", "version", "commit", "exactly name, version and commit"):
            self.assertIn(needle, text)

    def test_the_shared_validator_applies_the_same_two_rules(self):
        validator = _load("canonical_ci_validate_for_release", TOOLS / "canonical" / "ci_validate.py")
        repo = self._repo("HYDRA-UMC-A", "0.1.5")
        docs = self.workspace / "HYDRA-UMC-DOCS"
        (docs / "data").mkdir(parents=True)
        data = self.tool.build(self.workspace)
        target = docs / "data" / "ecosystem-release.json"
        target.write_text(self.tool.render(data), encoding="utf-8")
        self.assertEqual(validator.check_ecosystem_release(repo, {}), [])
        data["repositories"][0]["version"] = "0.2.0"
        target.write_text(self.tool.render(data), encoding="utf-8")
        self.assertTrue(any("ahead of the manifest" in line for line in validator.check_ecosystem_release(repo, {})))
        data["repositories"][0]["version"] = "0.1.5"
        data["repositories"][0]["commit"] = "1" * 40
        target.write_text(self.tool.render(data), encoding="utf-8")
        self.assertTrue(any("not in the history" in line for line in validator.check_ecosystem_release(repo, {})))

    def test_the_validator_skips_when_there_is_no_file_or_no_entry(self):
        validator = _load("canonical_ci_validate_for_release_skip", TOOLS / "canonical" / "ci_validate.py")
        repo = self._repo("HYDRA-UMC-A", "0.1.5")
        self.assertEqual(validator.check_ecosystem_release(repo, {}), [])
        (self.workspace / "HYDRA-UMC-DOCS" / "data").mkdir(parents=True)
        (self.workspace / "HYDRA-UMC-DOCS" / "data" / "ecosystem-release.json").write_text(
            json.dumps({"repositories": [{"name": "HYDRA-UMC-Z"}]}), encoding="utf-8"
        )
        self.assertEqual(validator.check_ecosystem_release(repo, {}), [])


if __name__ == "__main__":
    unittest.main()
