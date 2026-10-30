# =============================================================================
# HYDRA-UMC-SDK - version rule tests (tools/canonical/bump_manifest_version.py)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The shared version utility: three components below 0.8.0, four from there."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CANONICAL = Path(__file__).resolve().parents[3] / "tools" / "canonical" / "bump_manifest_version.py"
B = chr(92)
PACKAGE_JSON_PATTERN = '"version":' + B + "s*" + '"(' + B + "d+)" + B + ".(" + B + "d+)" + B + ".(" + B + "d+)" + '"'


def _load():
    spec = importlib.util.spec_from_file_location("canonical_bump", CANONICAL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NextVersionTests(unittest.TestCase):
    def setUp(self):
        self.m = _load()

    def test_three_part_versions_below_the_threshold_are_unchanged(self):
        self.assertEqual(self.m.next_version("0.0.1"), "0.0.2")
        self.assertEqual(self.m.next_version("0.0.9"), "0.1.0")
        self.assertEqual(self.m.next_version("0.6.9"), "0.7.0")
        self.assertEqual(self.m.next_version("0.7.8"), "0.7.9")

    def test_reaching_0_8_0_becomes_0_8_0_0(self):
        self.assertEqual(self.m.next_version("0.7.9"), "0.8.0.0")

    def test_the_fourth_component_counts_up_and_carries(self):
        self.assertEqual(self.m.next_version("0.8.0.0"), "0.8.0.1")
        self.assertEqual(self.m.next_version("0.8.0.9"), "0.8.1.0")
        self.assertEqual(self.m.next_version("0.8.1.9"), "0.8.2.0")
        self.assertEqual(self.m.next_version("0.8.9.9"), "0.9.0.0")
        self.assertEqual(self.m.next_version("0.9.9.9"), "1.0.0.0")

    def test_a_long_run_never_skips_or_repeats(self):
        version, seen = "0.7.8", []
        for _ in range(250):
            version = self.m.next_version(version)
            seen.append(version)
        self.assertEqual(len(seen), len(set(seen)))
        self.assertEqual(seen[1], "0.8.0.0")
        self.assertIn("0.8.0.9", seen)
        self.assertEqual(seen[seen.index("0.8.0.9") + 1], "0.8.1.0")


class NativePatternTests(unittest.TestCase):
    def setUp(self):
        self.m = _load()

    def test_a_three_group_pattern_reads_both_forms(self):
        self.assertEqual(self.m.read_version('"version": "0.7.9"', PACKAGE_JSON_PATTERN), "0.7.9")
        self.assertEqual(self.m.read_version('"version": "0.8.0.3"', PACKAGE_JSON_PATTERN), "0.8.0.3")

    def test_replacing_grows_and_shrinks_the_number_of_components(self):
        grown = self.m.replace_version('{"version": "0.7.9"}', PACKAGE_JSON_PATTERN, "0.8.0.0")
        self.assertEqual(grown, '{"version": "0.8.0.0"}')
        stepped = self.m.replace_version(grown, PACKAGE_JSON_PATTERN, "0.8.0.1")
        self.assertEqual(stepped, '{"version": "0.8.0.1"}')

    def test_extending_a_pattern_twice_changes_nothing_more(self):
        once = self.m.with_optional_fourth_group(PACKAGE_JSON_PATTERN)
        self.assertNotEqual(once, PACKAGE_JSON_PATTERN)
        self.assertEqual(self.m.with_optional_fourth_group(once), once)

    def test_widening_a_pattern_stored_in_separate_fields_returns_it_unchanged(self):
        fields = {"major": r"MAJOR (\d+)", "minor": r"MINOR (\d+)", "patch": r"PATCH (\d+)"}
        self.assertIs(self.m.widen_pattern(fields), fields)
        self.assertEqual(self.m.widen_pattern(PACKAGE_JSON_PATTERN), self.m.with_optional_fourth_group(PACKAGE_JSON_PATTERN))
        self.assertEqual(self.m.read_version("MAJOR 0\nMINOR 7\nPATCH 9\n", fields), "0.7.9")


class EndToEndTests(unittest.TestCase):
    """Runs the copied utility inside a throw-away project, the way a build does."""

    def _project(self, version: str) -> Path:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, True)
        shutil.copy(CANONICAL, root / "bump_manifest_version.py")
        (root / "package.json").write_text('{"name": "x", "version": "%s"}\n' % version, encoding="utf-8")
        manifest = {"version": version, "native_version": {"file": "package.json", "pattern": PACKAGE_JSON_PATTERN}}
        (root / "hydra-umc.project.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        (root / "CHANGELOG.md").write_text("# Changelog\n\n## [%s]\n\n- start\n" % version, encoding="utf-8")
        return root

    def _run(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "bump_manifest_version.py", *args], cwd=root, capture_output=True, text=True)

    def test_a_build_at_0_7_9_becomes_0_8_0_0_everywhere(self):
        root = self._project("0.7.9")
        result = self._run(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"version": "0.8.0.0"', (root / "package.json").read_text(encoding="utf-8"))
        manifest = json.loads((root / "hydra-umc.project.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "0.8.0.0")
        self.assertIn("## [0.8.0.0]", (root / "CHANGELOG.md").read_text(encoding="utf-8"))
        again = self._run(root)
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertIn('"version": "0.8.0.1"', (root / "package.json").read_text(encoding="utf-8"))

    def test_sync_after_a_three_part_native_step_appends_the_fourth_component(self):
        root = self._project("0.7.9")
        (root / "package.json").write_text('{"name": "x", "version": "0.8.0"}\n', encoding="utf-8")
        result = self._run(root, "--sync")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"version": "0.8.0.0"', (root / "package.json").read_text(encoding="utf-8"))
        manifest = json.loads((root / "hydra-umc.project.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "0.8.0.0")

    def test_the_package_version_line_follows_the_native_version(self):
        root = self._project("0.7.9")
        package = root / "src" / "demo"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text('__version__ = "0.7.9"\n', encoding="utf-8")
        other = root / "src" / "other"
        other.mkdir()
        (other / "__init__.py").write_text('__version__ = "3.1.4"\n', encoding="utf-8")
        self.assertEqual(self._run(root).returncode, 0)
        self.assertEqual((package / "__init__.py").read_text(encoding="utf-8"), '__version__ = "0.8.0.0"\n')
        self.assertEqual((other / "__init__.py").read_text(encoding="utf-8"), '__version__ = "3.1.4"\n')

    def test_a_skipped_version_is_still_refused(self):
        root = self._project("0.8.0.1")
        (root / "package.json").write_text('{"name": "x", "version": "0.8.0.5"}\n', encoding="utf-8")
        self.assertNotEqual(self._run(root, "--sync").returncode, 0)


class SeparateFieldPatternTests(unittest.TestCase):
    """Versions kept in separate fields (a properties file, C defines) use an optional build entry."""

    def setUp(self):
        self.m = _load()
        keys = {"major": "Major", "minor": "Minor", "patch": "Patch", "build": "Build"}
        self.pattern = {k: "^version" + v + B + "s*=" + B + "s*(" + B + "d+)" for k, v in keys.items()}
        self.text = "versionMajor=0" + chr(10) + "versionMinor=7" + chr(10) + "versionPatch=9" + chr(10) + "versionBuild=0" + chr(10)

    def test_below_the_threshold_the_build_field_is_ignored(self):
        self.assertEqual(self.m.read_version(self.text, self.pattern), "0.7.9")

    def test_crossing_writes_and_reads_the_build_field(self):
        grown = self.m.replace_version(self.text, self.pattern, "0.8.0.0")
        self.assertEqual(self.m.read_version(grown, self.pattern), "0.8.0.0")
        stepped = self.m.replace_version(grown, self.pattern, self.m.next_version("0.8.0.9"))
        self.assertEqual(self.m.read_version(stepped, self.pattern), "0.8.1.0")

    def test_a_pattern_without_a_build_entry_refuses_a_fourth_component(self):
        without = {k: v for k, v in self.pattern.items() if k != "build"}
        with self.assertRaises(ValueError):
            self.m.replace_version(self.text, without, "0.8.0.0")



if __name__ == "__main__":
    unittest.main()


CARGO_PATTERN = '^version' + B + 's*=' + B + 's*"(' + B + 'd+)' + B + '.(' + B + 'd+)' + B + '.(' + B + 'd+)"'
PUBSPEC_PATTERN = '^version:' + B + 's*(' + B + 'd+)' + B + '.(' + B + 'd+)' + B + '.(' + B + 'd+)' + B + '+' + B + 'd+'


class NativeTranslationTests(unittest.TestCase):
    """Cargo and Flutter cannot hold four dotted components: the manifest keeps four, the native file a fixed translation."""

    def setUp(self):
        self.m = _load()

    def test_the_translation_is_fixed_per_toolchain(self):
        self.assertEqual(self.m.to_native("0.8.0.3", "plain"), "0.8.0.3")
        self.assertEqual(self.m.to_native("0.8.0.3", "cargo"), "0.8.0+3")
        self.assertEqual(self.m.to_native("0.8.0.3", "pubspec"), "0.8.0")
        self.assertEqual(self.m.to_native("0.7.9", "cargo"), "0.7.9")

    def test_native_style_follows_the_file_name(self):
        self.assertEqual(self.m.native_style(Path("x/Cargo.toml")), "cargo")
        self.assertEqual(self.m.native_style(Path("pubspec.yaml")), "pubspec")
        self.assertEqual(self.m.native_style(Path("pyproject.toml")), "plain")

    def test_a_cargo_version_reads_back_as_four_components(self):
        text = 'name = "x"\nversion = "0.8.0+3"\n'
        self.assertEqual(self.m.read_version(text, CARGO_PATTERN, "cargo"), "0.8.0.3")
        self.assertEqual(self.m.read_version('version = "0.7.9"\n', CARGO_PATTERN, "cargo"), "0.7.9")

    def test_a_pubspec_reads_three_components_and_compares_by_prefix(self):
        text = "version: 0.8.0+21\n"
        self.assertEqual(self.m.read_version(text, PUBSPEC_PATTERN, "pubspec"), "0.8.0")
        self.assertTrue(self.m.same_version("0.8.0", "0.8.0.4", "pubspec"))
        self.assertFalse(self.m.same_version("0.8.1", "0.8.0.4", "pubspec"))


class ToolchainEndToEndTests(unittest.TestCase):
    def _project(self, native_file: str, pattern: str, native_text: str, version: str) -> Path:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, True)
        shutil.copy(CANONICAL, root / "bump_manifest_version.py")
        (root / native_file).write_text(native_text, encoding="utf-8")
        manifest = {"version": version, "native_version": {"file": native_file, "pattern": pattern}}
        (root / "hydra-umc.project.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        (root / "CHANGELOG.md").write_text("# Changelog\n\n## [%s]\n\n- start\n" % version, encoding="utf-8")
        return root

    def _run(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "bump_manifest_version.py", *args], cwd=root, capture_output=True, text=True)

    def test_a_rust_project_crosses_0_8_0_with_build_metadata_and_a_matching_lock(self):
        root = self._project("Cargo.toml", CARGO_PATTERN, '[package]\nname = "demo"\nversion = "0.7.9"\n', "0.7.9")
        (root / "Cargo.lock").write_text('[[package]]\nname = "dep"\nversion = "1.0.0"\n\n[[package]]\nname = "demo"\nversion = "0.7.9"\n', encoding="utf-8")
        first = self._run(root)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertIn('version = "0.8.0+0"', (root / "Cargo.toml").read_text(encoding="utf-8"))
        lock = (root / "Cargo.lock").read_text(encoding="utf-8")
        self.assertIn('name = "demo"\nversion = "0.8.0+0"', lock)
        self.assertIn('name = "dep"\nversion = "1.0.0"', lock)
        self.assertEqual(json.loads((root / "hydra-umc.project.json").read_text(encoding="utf-8"))["version"], "0.8.0.0")
        again = self._run(root)
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertIn('version = "0.8.0+1"', (root / "Cargo.toml").read_text(encoding="utf-8"))
        self.assertEqual(json.loads((root / "hydra-umc.project.json").read_text(encoding="utf-8"))["version"], "0.8.0.1")

    def test_a_flutter_project_keeps_three_components_and_counts_the_build_number(self):
        root = self._project("pubspec.yaml", PUBSPEC_PATTERN, "name: app\nversion: 0.7.9+30\n", "0.7.9")
        (root / "lib").mkdir()
        (root / "lib" / "app_version.dart").write_text("const String kAppVersion = '0.7.9';\nconst int kAppBuildNumber = 30;\nconst String kAppVersionFull = '0.7.9+30';\n", encoding="utf-8")
        self.assertEqual(self._run(root).returncode, 0)
        self.assertIn("version: 0.8.0+31", (root / "pubspec.yaml").read_text(encoding="utf-8"))
        self.assertIn("kAppVersionFull = '0.8.0+31'", (root / "lib" / "app_version.dart").read_text(encoding="utf-8"))
        self.assertEqual(self._run(root).returncode, 0)
        self.assertIn("version: 0.8.0+32", (root / "pubspec.yaml").read_text(encoding="utf-8"))
        self.assertEqual(json.loads((root / "hydra-umc.project.json").read_text(encoding="utf-8"))["version"], "0.8.0.1")
