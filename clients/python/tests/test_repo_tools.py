# =============================================================================
# HYDRA-UMC-SDK - tests of tools/pin_sdk.py and tools/sync_repo_tools.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Both tools run against a throwaway workspace of fake repositories."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[3] / "tools"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PIN = _load("pin_sdk")
SYNC = _load("sync_repo_tools")

PYPROJECT = (
    '[project]\nname = "x"\ndependencies = ["hydra-umc-sdk @ git+https://github.com/JuanenRac/'
    'HYDRA-UMC-SDK.git@{ref}#subdirectory=clients/python"]\n'
)
WORKFLOW_INLINE = (
    "steps:\n  - uses: actions/checkout@v5\n"
    "    with: {{repository: JuanenRac/HYDRA-UMC-SDK, path: .sdk, ref: {ref}}}\n"
)
WORKFLOW_BLOCK = (
    "steps:\n  - uses: actions/checkout@v5\n    with:\n      repository: JuanenRac/HYDRA-UMC-SDK\n"
    "      path: sdk\n      ref: {ref}\n  - uses: actions/checkout@v5\n    with:\n      repository: JuanenRac/OTHER\n      ref: main\n"
)


class RepinTests(unittest.TestCase):
    def test_a_branch_a_commit_and_an_older_tag_are_all_moved_to_the_tag(self):
        for ref in ("main", "9d06c7bb535a4beb3f633e2917a03277542e3818", "v0.3.2"):
            new, replaced = PIN.repin(PYPROJECT.format(ref=ref), "v0.3.4")
            self.assertIn("HYDRA-UMC-SDK.git@v0.3.4#subdirectory=clients/python", new)
            self.assertEqual(replaced, [ref])

    def test_a_reference_already_on_the_tag_is_not_reported(self):
        text = PYPROJECT.format(ref="v0.3.4")
        new, replaced = PIN.repin(text, "v0.3.4")
        self.assertEqual(new, text)
        self.assertEqual(replaced, [])

    def test_the_inline_and_the_block_form_of_a_workflow(self):
        new, replaced = PIN.repin(WORKFLOW_INLINE.format(ref="main"), "v0.3.4")
        self.assertIn("ref: v0.3.4}", new)
        self.assertEqual(replaced, ["main"])
        new, replaced = PIN.repin(WORKFLOW_BLOCK.format(ref="main"), "v0.3.4")
        self.assertEqual(replaced, ["main"])
        self.assertIn("repository: JuanenRac/HYDRA-UMC-SDK\n      path: sdk\n      ref: v0.3.4\n", new)

    def test_another_repository_in_the_same_workflow_keeps_its_ref(self):
        new, _ = PIN.repin(WORKFLOW_BLOCK.format(ref="main"), "v0.3.4")
        self.assertIn("repository: JuanenRac/OTHER\n      ref: main\n", new)

    def test_crlf_files_keep_their_line_endings(self):
        text = PYPROJECT.format(ref="main").replace("\n", "\r\n")
        new, _ = PIN.repin(text, "v0.3.4")
        self.assertNotIn("\n", new.replace("\r\n", ""))


class WorkspaceFixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)

    def repo(self, name: str, files: dict[str, str] | None = None) -> Path:
        path = self.workspace / name
        path.mkdir()
        (path / "hydra-umc.project.json").write_text(json.dumps({"name": name}), encoding="utf-8")
        for relative, content in (files or {}).items():
            target = path / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content.encode("utf-8"))
        return path


class PinWorkspaceTests(WorkspaceFixture):
    def test_check_lists_unpinned_files_and_writes_nothing(self):
        self.repo("HYDRA-UMC-BRIDGE-X", {"pyproject.toml": PYPROJECT.format(ref="main")})
        self.repo("HYDRA-UMC-SDK", {"pyproject.toml": PYPROJECT.format(ref="main")})
        changes = PIN.process(self.workspace, "v0.3.4", write=False)
        self.assertEqual([where for where, _ in changes], ["HYDRA-UMC-BRIDGE-X/pyproject.toml"])
        self.assertIn("@main#", (self.workspace / "HYDRA-UMC-BRIDGE-X" / "pyproject.toml").read_text())

    def test_write_pins_and_a_second_run_finds_nothing(self):
        self.repo("HYDRA-UMC-BRIDGE-X", {
            "pyproject.toml": PYPROJECT.format(ref="main"),
            ".github/workflows/ci.yml": WORKFLOW_INLINE.format(ref="main"),
        })
        self.assertEqual(len(PIN.process(self.workspace, "v0.3.4", write=True)), 2)
        self.assertEqual(PIN.process(self.workspace, "v0.3.4", write=False), [])

    def test_main_exit_codes(self):
        self.repo("HYDRA-UMC-BRIDGE-X", {"pyproject.toml": PYPROJECT.format(ref="main")})
        args = ["--workspace", str(self.workspace), "--tag", "v0.3.4"]
        self.assertEqual(PIN.main(["--check", *args]), 1)
        self.assertEqual(PIN.main(args), 0)
        self.assertEqual(PIN.main(["--check", *args]), 0)

    def test_a_tag_that_is_not_a_release_tag_is_refused(self):
        self.assertEqual(PIN.main(["--workspace", str(self.workspace), "--tag", "main"]), 2)


class SyncCanonicalTests(WorkspaceFixture):
    def setUp(self):
        super().setUp()
        self.canonical = self.workspace / "_canonical"
        self.canonical.mkdir()
        (self.canonical / "bump_manifest_version.py").write_text("print('bump')\n", encoding="utf-8")
        (self.canonical / "dashboard-dispatch.yml").write_text("name: notify\n", encoding="utf-8")
        (self.canonical / "hydra_project_tool.py").write_text("x = 1\n", encoding="utf-8")
        (self.canonical / "universal_readme_check.py").write_text("y = 2\n", encoding="utf-8")
        (self.canonical / "pretty_run.py").write_text("z = 3\n", encoding="utf-8")

    def test_matching_copies_pass_whatever_their_line_endings(self):
        files = {
            "bump_manifest_version.py": "print('bump')\r\n",
            ".github/workflows/dashboard-dispatch.yml": "name: notify\n",
            "tools/hydra_project_tool.py": "x = 1\n",
            "tools/universal_readme_check.py": "y = 2\n",
            "tools/pretty_run.py": "z = 3\n",
        }
        self.repo("HYDRA-UMC-A", files)
        self.assertEqual(SYNC.check_canonical(self.workspace, self.canonical), [])

    def test_a_stale_and_a_missing_copy_are_reported(self):
        self.repo("HYDRA-UMC-A", {"bump_manifest_version.py": "print('old')\n"})
        drift = SYNC.check_canonical(self.workspace, self.canonical)
        self.assertEqual(drift, [
            "HYDRA-UMC-A/bump_manifest_version.py",
            "HYDRA-UMC-A/.github/workflows/dashboard-dispatch.yml (missing)",
            "HYDRA-UMC-A/tools/hydra_project_tool.py (missing)",
            "HYDRA-UMC-A/tools/universal_readme_check.py (missing)",
            "HYDRA-UMC-A/tools/pretty_run.py (missing)",
        ])

    def test_write_fixes_them_keeps_crlf_and_is_idempotent(self):
        repo = self.repo("HYDRA-UMC-A", {"bump_manifest_version.py": "print('old')\r\nx\r\n"})
        changed = SYNC.write_canonical(self.workspace, self.canonical)
        self.assertEqual(len(changed), 5)
        self.assertEqual((repo / "bump_manifest_version.py").read_bytes(), b"print('bump')\r\n")
        self.assertEqual((repo / ".github/workflows/dashboard-dispatch.yml").read_bytes(), b"name: notify\n")
        self.assertEqual(SYNC.write_canonical(self.workspace, self.canonical), [])
        self.assertEqual(SYNC.check_canonical(self.workspace, self.canonical), [])

    def test_the_bump_utility_is_not_forced_onto_a_repository_that_does_not_use_it(self):
        repo = self.repo("HYDRA-UMC-BRIDGE-A", {
            "tools/bump_version.py": "pass\n",
            ".github/workflows/dashboard-dispatch.yml": "name: notify\n",
            "tools/hydra_project_tool.py": "x = 1\n",
            "tools/universal_readme_check.py": "y = 2\n",
            "tools/pretty_run.py": "z = 3\n",
        })
        self.assertEqual(SYNC.check_canonical(self.workspace, self.canonical), [])
        SYNC.write_canonical(self.workspace, self.canonical)
        self.assertFalse((repo / "bump_manifest_version.py").exists())

    def test_folders_that_are_not_family_repositories_are_ignored(self):
        (self.workspace / "HYDRA-UMC-NOT-A-REPO").mkdir()
        (self.workspace / "URTC").mkdir()
        self.repo("HYDRA-UMC-A")
        self.assertEqual([r.name for r in SYNC.repos(self.workspace)], ["HYDRA-UMC-A"])


class FingerprintTests(WorkspaceFixture):
    def test_licence_line_banner_name_and_line_endings_do_not_matter(self):
        a = "# HYDRA-UMC-FOO - ci_validate.py\n# GPL-3.0 - see LICENSE\nx = 1\n"
        b = "# HYDRA-UMC-BAR - ci_validate.py\r\n# GPL-3.0-or-later - see LICENSE\r\nx = 1\r\n"
        self.assertEqual(SYNC.fingerprint(a), SYNC.fingerprint(b))

    def test_a_real_difference_changes_the_fingerprint(self):
        self.assertNotEqual(SYNC.fingerprint("x = 1\n"), SYNC.fingerprint("x = 2\n"))

    def test_families_group_repositories_and_name_the_absent_ones(self):
        self.repo("HYDRA-UMC-A", {"tools/ci_validate.py": "x = 1\n"})
        self.repo("HYDRA-UMC-B", {"tools/ci_validate.py": "x = 1\r\n"})
        self.repo("HYDRA-UMC-C", {"tools/ci_validate.py": "x = 2\n"})
        self.repo("HYDRA-UMC-D")
        groups = SYNC.families(self.workspace, "tools/ci_validate.py")
        sizes = sorted(len(names) for key, names in groups.items() if key)
        self.assertEqual(sizes, [1, 2])
        self.assertEqual(groups[""], ["HYDRA-UMC-D"])


if __name__ == "__main__":
    unittest.main()
