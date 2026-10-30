# =============================================================================
# HYDRA-UMC-SDK - Tests of the workspace contract check
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The contract check reports a bad manifest, a wrong folder name and a service missing from the port registry."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("contract_check", SDK / "tools" / "contract_check.py")
CHECK = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CHECK)

VALID = json.loads((SDK / "conformance" / "fixtures" / "v1" / "project-manifest.valid.json").read_text(encoding="utf-8"))


class ContractCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)

    def repo(self, folder: str, manifest: dict) -> Path:
        path = self.workspace / folder
        path.mkdir()
        (path / "hydra-umc.project.json").write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def problems_of(self, report: dict, name: str) -> list[str]:
        return next(r["problems"] for r in report["repositories"] if r["name"] == name)

    def test_a_manifest_that_fails_the_validator_is_reported(self) -> None:
        self.repo("HYDRA-UMC-BAD", {"name": "HYDRA-UMC-BAD"})
        report = CHECK.check_workspace(self.workspace)
        self.assertTrue(any(p.startswith("manifest:") for p in self.problems_of(report, "HYDRA-UMC-BAD")))
        self.assertGreater(report["summary"]["problems"], 0)

    def test_a_manifest_name_that_is_not_the_folder_is_reported(self) -> None:
        self.repo("HYDRA-UMC-ONE", dict(VALID, name="HYDRA-UMC-OTHER"))
        problems = self.problems_of(CHECK.check_workspace(self.workspace), "HYDRA-UMC-ONE")
        self.assertTrue(any("folder name" in p for p in problems))

    def test_a_service_missing_from_the_port_registry_is_reported(self) -> None:
        self.repo("HYDRA-UMC-NEWSVC", dict(VALID, name="HYDRA-UMC-NEWSVC", service={"port": 9999, "health_path": "/health"}))
        problems = self.problems_of(CHECK.check_workspace(self.workspace), "HYDRA-UMC-NEWSVC")
        self.assertTrue(any("port registry" in p for p in problems))

    def test_folders_that_are_not_family_repositories_are_ignored(self) -> None:
        (self.workspace / "SOMETHING-ELSE").mkdir()
        self.assertEqual(CHECK.check_workspace(self.workspace)["summary"]["repositories"], 0)

    def test_the_exit_status_follows_the_problems_unless_report_only(self) -> None:
        self.repo("HYDRA-UMC-BAD", {"name": "HYDRA-UMC-BAD"})
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(CHECK.main([str(self.workspace)]), 1)
            self.assertEqual(CHECK.main([str(self.workspace), "--report-only"]), 0)


if __name__ == "__main__":
    unittest.main()
