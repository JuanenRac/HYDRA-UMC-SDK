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


if __name__ == "__main__":
    unittest.main()
