# =============================================================================
# HYDRA-UMC-SDK - tests of tools/canonical/hydra_project_tool.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The project tool runs against a throwaway git repository with the real
canonical bump utility copied in, so `bump` is exercised for real."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
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

    def test_bump_also_raises_the_android_version_code_when_the_repository_has_one(self):
        (self.root / "versionCode.txt").write_text("7\n", encoding="utf-8")
        (self.root / "bump_version_code.py").write_text(
            "import pathlib\np = pathlib.Path(__file__).resolve().parent / 'versionCode.txt'\n"
            "p.write_text(str(int(p.read_text()) + 1) + '\\n')\n",
            encoding="utf-8",
        )
        self.commit("android style")
        self.assertEqual(TOOL.bump(self.root), 0)
        self.assertEqual((self.root / "versionCode.txt").read_text().strip(), "8")
        self.assertEqual(TOOL.declared_version(self.root), "0.1.5")

    def _flutter_style(self, version: str, pubspec: str) -> None:
        bs = chr(92)
        pattern = "^version:" + bs + "s*(" + bs + "d+)" + bs + ".(" + bs + "d+)" + bs + ".(" + bs + "d+)" + bs + "+" + bs + "d+"
        manifest = json.loads((self.root / "hydra-umc.project.json").read_text(encoding="utf-8"))
        manifest["version"] = version
        manifest["native_version"] = {"file": "pubspec.yaml", "pattern": pattern}
        (self.root / "hydra-umc.project.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        (self.root / "pubspec.yaml").write_text(pubspec, encoding="utf-8")
        (self.root / "CHANGELOG.md").write_text("# Changelog\n\n## [%s]\n\n- first\n" % version, encoding="utf-8")
        self.commit("flutter style")

    def test_a_flutter_app_is_bumped_by_the_shared_utility_with_three_components_and_a_build_number(self):
        self._flutter_style("0.7.9", "name: app\nversion: 0.7.9+40\n")
        self.assertEqual(TOOL.bump(self.root), 0)
        self.assertEqual(TOOL.declared_version(self.root), "0.8.0.0")
        self.assertIn("version: 0.8.0+41", (self.root / "pubspec.yaml").read_text(encoding="utf-8"))
        self.assertIsNone(TOOL.native_version_problem(self.root))

    def test_a_native_version_the_toolchain_would_reject_is_reported_and_stops_the_bump(self):
        self._flutter_style("0.8.0.0", "name: app\nversion: 0.8.0.0+40\n")
        self.assertIn("a.b.c+N", TOOL.native_version_problem(self.root))
        self.assertIn("cannot build", " ".join(f[0] for f in TOOL.doctor_manifest(self.root, {})))

    def test_a_cargo_version_with_build_metadata_is_accepted(self):
        bs = chr(92)
        manifest = json.loads((self.root / "hydra-umc.project.json").read_text(encoding="utf-8"))
        manifest["native_version"] = {"file": "Cargo.toml", "pattern": "^version" + bs + "s*=" + bs + 's*"(' + bs + "d+)" + bs + ".(" + bs + "d+)" + bs + ".(" + bs + 'd+)"'}
        (self.root / "hydra-umc.project.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        (self.root / "Cargo.toml").write_text('[package]\nname = "x"\nversion = "0.8.0+2"\n', encoding="utf-8")
        self.assertIsNone(TOOL.native_version_problem(self.root))
        (self.root / "Cargo.toml").write_text('[package]\nname = "x"\nversion = "0.8.0.2"\n', encoding="utf-8")
        self.assertIn("a.b.c", TOOL.native_version_problem(self.root))

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


class DoctorTests(unittest.TestCase):
    """`doctor` against throwaway repositories: it reports, it never writes."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)
        self.root = self.workspace / "HYDRA-UMC-DEMO"
        self.root.mkdir()
        (self.root / "tools").mkdir()
        self.write_manifest()
        (self.root / "CHANGELOG.md").write_text("# Changelog\n\n## [0.1.4] - first\n\n- the first note\n", encoding="utf-8")
        self.env = {"HYDRA_UMC_DOCS_DIR": str(self.workspace / "none"), "HYDRA_UMC_SDK_DIR": str(self.workspace / "none")}

    def write_manifest(self, **overrides) -> None:
        manifest = {
            "schema_version": "1.0", "ecosystem": "HYDRA-UMC", "name": "HYDRA-UMC-DEMO", "version": "0.1.4",
            "role": "tool", "stack": "python", "technologies": ["python"], "deployment_target": "user-pc",
            "maturity": "functional", "family": "tools", "parent": None, "build": "none", "notes": "demo",
            "native_version": {"file": "VERSION.txt", "pattern": r"(\d+)\.(\d+)\.(\d+)"},
        }
        manifest.update(overrides)
        (self.root / "hydra-umc.project.json").write_text(json.dumps(manifest), encoding="utf-8")

    def findings(self, check):
        return getattr(TOOL, "doctor_" + check)(self.root, self.env)

    def test_a_good_manifest_has_no_finding(self):
        self.assertEqual(self.findings("manifest"), [])

    def test_manifest_enums_name_and_version_are_checked(self):
        self.write_manifest(role="robot", deployment_target="mcu", maturity="done", name="OTHER", version="1.2")
        text = " | ".join(problem for problem, _ in self.findings("manifest"))
        for expected in ("role 'robot'", "maturity 'done'", "name 'OTHER'", "version '1.2'"):
            self.assertIn(expected, text)
        self.assertNotIn("deployment_target", text)

    def test_a_missing_key_is_named(self):
        manifest = json.loads((self.root / "hydra-umc.project.json").read_text(encoding="utf-8"))
        del manifest["family"]
        (self.root / "hydra-umc.project.json").write_text(json.dumps(manifest), encoding="utf-8")
        self.assertIn("family", self.findings("manifest")[0][0])

    def test_the_changelog_needs_the_heading_and_a_note(self):
        self.assertEqual(self.findings("changelog"), [])
        (self.root / "CHANGELOG.md").write_text("# Changelog\n\n## [0.1.3] - old\n\n- note\n", encoding="utf-8")
        self.assertIn("0.1.3", self.findings("changelog")[0][0])
        (self.root / "CHANGELOG.md").write_text("# Changelog\n\n## [0.1.4] - empty\n\n## [0.1.3]\n\n- note\n", encoding="utf-8")
        self.assertIn("no note", self.findings("changelog")[0][0])

    def test_a_missing_readme_checker_is_reported_with_its_fix(self):
        problem, fix = self.findings("readme")[0]
        self.assertIn("universal_readme_check.py", problem)
        self.assertIn("sync_repo_tools.py", fix)

    def test_checks_that_need_a_sibling_checkout_skip(self):
        for check in ("glance", "shared_tools"):
            with self.assertRaises(TOOL.Skipped):
                self.findings(check)

    def test_the_sdk_pin_must_be_a_tag_and_the_newest_one(self):
        sdk = self.workspace / "HYDRA-UMC-SDK"
        sdk.mkdir()
        for args in (("init", "-q"), ("config", "user.email", "t@example.com"), ("config", "user.name", "T"),
                     ("commit", "-q", "--allow-empty", "-m", "start"), ("tag", "v0.3.4"), ("tag", "v0.3.10")):
            subprocess.run(["git", *args], cwd=sdk, check=True, capture_output=True)
        self.env["HYDRA_UMC_SDK_DIR"] = str(sdk)
        pyproject = self.root / "pyproject.toml"
        line = '"hydra-umc-sdk @ git+https://github.com/JuanenRac/HYDRA-UMC-SDK.git@{}#subdirectory=clients/python"\n'
        pyproject.write_text(line.format("v0.3.10"), encoding="utf-8")
        self.assertEqual(self.findings("sdk_pin"), [])
        pyproject.write_text(line.format("v0.3.4"), encoding="utf-8")
        self.assertIn("newest release is v0.3.10", self.findings("sdk_pin")[0][0])
        pyproject.write_text(line.format("main"), encoding="utf-8")
        self.assertIn("not by a release tag", self.findings("sdk_pin")[0][0])

    def test_doctor_reports_and_writes_nothing(self):
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = TOOL.doctor(self.root, self.env)
        self.assertEqual(code, 1)
        self.assertIn("DOCTOR=FAIL", out.getvalue())
        self.assertIn("-> ", out.getvalue())
        self.assertIn("SKIP  glance", out.getvalue())
        self.assertEqual(before, sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*")))

    def test_the_manifest_enums_match_the_published_schema(self):
        schema = json.loads((CANONICAL.parents[1] / "contracts" / "json-schema" / "v1" / "project-manifest.schema.json").read_text(encoding="utf-8"))
        for key, allowed in TOOL.MANIFEST_ENUMS.items():
            self.assertEqual(set(allowed), set(schema["properties"][key]["enum"]), key)

    def test_every_client_type_file_names_every_schema_enum_value(self):
        sdk = CANONICAL.parents[1]
        schema = json.loads((sdk / "contracts" / "json-schema" / "v1" / "project-manifest.schema.json").read_text(encoding="utf-8"))
        files = [sdk / "clients" / "go" / "types.go", sdk / "clients" / "rust" / "src" / "types.rs", sdk / "clients" / "typescript" / "src" / "types.ts"]
        for key in ("role", "deployment_target", "maturity"):
            for value in schema["properties"][key]["enum"]:
                for path in files:
                    text = path.read_text(encoding="utf-8")
                    variant = "".join(part.capitalize() for part in re.split(r"[-_]", value))   # serde rename_all spelling
                    self.assertTrue(f'"{value}"' in text or f"{variant}," in text, f"{path.name} lacks {key} {value}")


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "tools").mkdir()

    def floor(self, *entries):
        (self.root / "tools" / "coverage_floor.json").write_text(json.dumps(list(entries)), encoding="utf-8")

    def run_coverage(self, value, strict=False):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = TOOL.coverage(self.root, strict, measure=lambda entry, root: value)
        return code, out.getvalue()

    def test_without_a_floor_file_it_skips(self):
        code, out = self.run_coverage(50.0)
        self.assertEqual(code, 0)
        self.assertIn("COVERAGE=SKIP", out)

    def test_at_or_above_the_floor_passes(self):
        self.floor({"stack": "python", "floor": 90})
        code, out = self.run_coverage(90.0)
        self.assertEqual((code, "COVERAGE=PASS" in out), (0, True))

    def test_below_the_floor_warns_and_only_strict_fails(self):
        self.floor({"stack": "python", "floor": 90})
        code, out = self.run_coverage(80.0)
        self.assertEqual(code, 0)
        self.assertIn("COVERAGE=WARN 1", out)
        self.assertEqual(self.run_coverage(80.0, strict=True)[0], 1)

    def test_no_figure_is_a_skip_not_a_failure(self):
        self.floor({"stack": "go", "floor": 70})
        code, out = self.run_coverage(None, strict=True)
        self.assertEqual(code, 0)
        self.assertIn("SKIP  go", out)

    def test_the_go_profile_is_summed_by_statements(self):
        profile = "mode: set\na.go:1.1,2.2 4 1\na.go:3.1,4.2 6 0\n"
        self.assertAlmostEqual(TOOL.parse_go_profile(profile), 40.0)
        self.assertIsNone(TOOL.parse_go_profile("mode: set\n"))

    def test_the_node_total_is_read_from_the_all_files_row(self):
        self.assertEqual(TOOL.parse_node_total("x\nℹ all files      |  95.07 |    83.67 |   85.42 | \n"), 95.07)
        self.assertIsNone(TOOL.parse_node_total("nothing"))


if __name__ == "__main__":
    unittest.main()
