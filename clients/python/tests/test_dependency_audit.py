# =============================================================================
# HYDRA-UMC-SDK - Tests of tools/dependency_audit.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The inventory, the bill of materials and the OSV query, with the network replaced by a function."""

from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
import urllib.error
from pathlib import Path

TOOL = Path(__file__).resolve().parents[3] / "tools" / "dependency_audit.py"
spec = importlib.util.spec_from_file_location("dependency_audit", TOOL)
AUDIT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AUDIT)


class Workspace(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))

    def repo(self, name: str, files: dict[str, str]) -> Path:
        repo = self.root / name
        (repo / ".git").mkdir(parents=True)
        for relative, body in files.items():
            target = repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")
        return repo


class InventoryTests(Workspace):
    def test_npm_cargo_go_pub_and_python_are_read(self) -> None:
        repo = self.repo("HYDRA-UMC-X", {
            "package-lock.json": json.dumps({"packages": {"": {"name": "x"}, "node_modules/@a/b": {"version": "1.2.3"}, "node_modules/c": {"version": "4.5.6", "link": True}}}),
            "Cargo.lock": '[[package]]\nname = "serde"\nversion = "1.0.1"\nsource = "registry+https://github.com/rust-lang/crates.io-index"\n[[package]]\nname = "me"\nversion = "0.1.0"\n',
            "go.mod": "module m\n\nrequire (\n\tgithub.com/x/y v1.2.3 // indirect\n)\nrequire a.b/c v0.1.0\n",
            "pubspec.lock": 'packages:\n  http:\n    dependency: "direct main"\n    description: {}\n    version: "1.2.0"\n',
            "pyproject.toml": '[project]\nname = "x"\ndependencies = ["requests>=2.31", "cryptography==42.0.0", "numpy", "sdk @ git+https://x/y.git@v1"]\n[project.optional-dependencies]\ndev = ["pytest>=9"]\n',
            "requirements-dev.txt": "ruff==0.17.1\n# comment\n-r other.txt\n",
        })
        found = {(d.ecosystem, d.name, d.version): d for d in AUDIT.inventory(repo)}
        self.assertIn(("npm", "@a/b", "1.2.3"), found)
        self.assertNotIn(("npm", "c", "4.5.6"), found)
        self.assertIn(("crates.io", "serde", "1.0.1"), found)
        self.assertNotIn(("crates.io", "me", "0.1.0"), found)
        self.assertIn(("Go", "github.com/x/y", "1.2.3"), found)
        self.assertIn(("Go", "a.b/c", "0.1.0"), found)
        self.assertIn(("Pub", "http", "1.2.0"), found)
        self.assertTrue(found[("PyPI", "requests", "2.31")].floor)
        self.assertFalse(found[("PyPI", "cryptography", "42.0.0")].floor)
        self.assertIn(("PyPI", "numpy", ""), found)
        self.assertIn(("PyPI", "pytest", "9"), found)
        self.assertIn(("PyPI", "ruff", "0.17.1"), found)
        self.assertFalse(any(k[1] == "sdk" for k in found))

    def test_dependency_folders_are_not_read(self) -> None:
        repo = self.repo("HYDRA-UMC-X", {"node_modules/p/package-lock.json": json.dumps({"packages": {"node_modules/z": {"version": "1.0.0"}}})})
        self.assertEqual(AUDIT.inventory(repo), [])

    def test_the_bill_of_materials_names_every_component_with_a_purl(self) -> None:
        bom = AUDIT.bill_of_materials("R", [AUDIT.Dependency("npm", "@a/b", "1.2.3", "package-lock.json"), AUDIT.Dependency("PyPI", "requests", "2.31", "pyproject.toml", floor=True)])
        self.assertEqual(bom["bomFormat"], "CycloneDX")
        self.assertEqual(bom["components"][0]["purl"], "pkg:npm/%40a/b@1.2.3")
        self.assertEqual(bom["components"][1]["properties"][0]["value"], "lower-bound")

    def test_only_the_three_families_are_audited(self) -> None:
        for name in ("ARMOR-X", "URTC", "HYDRA-UMC-Y", "EH3D-Z", "ELECTRO-HOBBY-3D-UPDATER", "OTHER"):
            self.repo(name, {})
        names = [p.name for p in AUDIT.family_repositories(self.root, AUDIT.FAMILY_PREFIXES)]
        self.assertEqual(names, ["ARMOR-X", "HYDRA-UMC-Y", "URTC"])


class QueryTests(unittest.TestCase):
    def test_advisories_carry_the_fixed_version_and_the_severity(self) -> None:
        def post(url, body):
            return {"results": [{"vulns": [{"id": "GHSA-1"}]}, {}]}

        def get(url):
            return {"summary": "bad", "database_specific": {"severity": "high"}, "affected": [{"package": {"name": "a"}, "ranges": [{"events": [{"introduced": "0"}, {"fixed": "2.0.0"}]}]}]}

        found, problems = AUDIT.query_osv([("npm", "a", "1.0.0"), ("npm", "b", "1.0.0"), ("PyPI", "c", "")], post, get)
        self.assertEqual(problems, [])
        self.assertEqual(list(found), [("npm", "a", "1.0.0")])
        self.assertEqual(found[("npm", "a", "1.0.0")][0]["fixed"], ["2.0.0"])
        self.assertEqual(found[("npm", "a", "1.0.0")][0]["severity"], "HIGH")

    def test_a_failed_request_is_a_problem_and_never_a_clean_result(self) -> None:
        def post(url, body):
            raise urllib.error.URLError("offline")

        found, problems = AUDIT.query_osv([("npm", "a", "1.0.0")], post, lambda url: {})
        self.assertEqual(found, {})
        self.assertEqual(len(problems), 1)


if __name__ == "__main__":
    unittest.main()
