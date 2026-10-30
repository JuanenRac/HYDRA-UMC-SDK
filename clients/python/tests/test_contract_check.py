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


class ContractTablesTests(unittest.TestCase):
    def test_the_ports_table_follows_the_registry_ordered_by_port(self) -> None:
        text = CHECK.ports_table(SDK / "contracts" / "ports.yaml")
        rows = [line.split("|")[1:-1] for line in text.splitlines()[2:]]
        ports = [int(row[0]) for row in rows]
        self.assertEqual(ports, sorted(ports))
        self.assertIn("HYDRA-UMC-SERVER", text)
        self.assertNotIn("null", text)

    def test_the_routes_table_lists_every_operation_of_the_documents(self) -> None:
        text = CHECK.routes_table(SDK / "contracts" / "openapi" / "v1")
        expected = 0
        for path in (SDK / "contracts" / "openapi" / "v1").glob("*.openapi.json"):
            for item in json.loads(path.read_text(encoding="utf-8"))["paths"].values():
                expected += sum(1 for method in CHECK.HTTP_METHODS if isinstance(item.get(method), dict))
        self.assertEqual(len(text.splitlines()) - 2, expected)
        self.assertIn("/api/hydra-info", text)

    def test_the_versions_table_reads_the_manifests_of_the_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            for name, version in (("HYDRA-UMC-ZED", "1.2.3"), ("HYDRA-UMC-ALPHA", "0.0.9")):
                repo = workspace / name
                repo.mkdir()
                (repo / "hydra-umc.project.json").write_text(json.dumps(dict(VALID, name=name, version=version)), encoding="utf-8")
            lines = CHECK.versions_table(workspace).splitlines()[2:]
            self.assertEqual([line.split("|")[1].strip() for line in lines], ["HYDRA-UMC-ALPHA", "HYDRA-UMC-ZED"])
            self.assertIn("1.2.3", lines[1])

    def test_a_pipe_in_a_cell_does_not_break_the_table(self) -> None:
        self.assertEqual(CHECK._cell("a|b\nc"), r"a\|b c")

    def test_the_tables_flag_prints_the_three_tables_and_nothing_else(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(CHECK.main([str(SDK.parent), "--tables"]), 0)
        text = out.getvalue()
        self.assertTrue(text.startswith("### Ports"))
        for heading in ("### Versions", "### Routes"):
            self.assertIn(heading, text)
