# =============================================================================
# HYDRA-UMC-SDK - tests of the shared redaction, the port registry and the validator adoption
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The canonical redaction passes its own vectors; sync_ports and the validator adoption work on a throwaway workspace."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[3]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REDACTION = _load("shared_redaction", SDK / "tools" / "canonical" / "redaction.py")
PORTS = _load("sync_ports", SDK / "tools" / "sync_ports.py")
SYNC = _load("sync_repo_tools_b", SDK / "tools" / "sync_repo_tools.py")
VECTORS = json.loads((SDK / "contracts" / "redaction" / "vectors.json").read_text(encoding="utf-8"))


class RedactionVectorTests(unittest.TestCase):
    def test_text(self):
        for case in VECTORS["text"]:
            with self.subTest(case["name"]):
                self.assertEqual(REDACTION.redact_secrets(case["input"]), case["expected"])

    def test_json(self):
        for case in VECTORS["json"]:
            with self.subTest(case["name"]):
                self.assertEqual(REDACTION.redact_json(case["input"]), case["expected"])

    def test_lines(self):
        for case in VECTORS["lines"]:
            with self.subTest(case["name"]):
                self.assertEqual(REDACTION.redact_lines(case["input"]), case["expected"])

    def test_the_marker_is_the_one_the_vectors_name(self):
        self.assertEqual(REDACTION._REDACTED, VECTORS["marker"])


class Workspace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.workspace = Path(self._tmp.name)

    def repo(self, name, service=None, unit_text=None, extra=None):
        path = self.workspace / name
        path.mkdir()
        manifest = {"name": name}
        if service is not None:
            manifest["service"] = service
        (path / "hydra-umc.project.json").write_text(json.dumps(manifest), encoding="utf-8")
        if unit_text is not None and service and service.get("systemd_unit"):
            (path / "systemd").mkdir()
            (path / "systemd" / service["systemd_unit"]).write_text(unit_text, encoding="utf-8")
        for relative, content in (extra or {}).items():
            target = self.workspace / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        return path


class PortRegistryTests(Workspace):
    def test_a_port_missing_in_the_manifest_comes_from_the_unit(self):
        self.repo("HYDRA-UMC-A", {"systemd_unit": "hydra-umc-a.service"}, "ExecStart=x --port 8200\n")
        services, problems = PORTS.collect(self.workspace)
        self.assertEqual(services[0]["port"], 8200)
        self.assertEqual(problems, [])

    def test_a_manifest_and_a_unit_that_disagree_are_reported(self):
        self.repo("HYDRA-UMC-A", {"port": 8100, "systemd_unit": "hydra-umc-a.service"}, "ExecStart=x --port 8200\n")
        _, problems = PORTS.collect(self.workspace)
        self.assertTrue(any("8100" in p and "8200" in p for p in problems))

    def test_two_services_on_one_port_are_reported(self):
        self.repo("HYDRA-UMC-A", {"port": 8100})
        self.repo("HYDRA-UMC-B", {"port": 8100})
        _, problems = PORTS.collect(self.workspace)
        self.assertTrue(any("8100" in p and "HYDRA-UMC-A" in p and "HYDRA-UMC-B" in p for p in problems))

    def test_a_unit_without_a_file_is_reported(self):
        self.repo("HYDRA-UMC-A", {"port": 8100, "systemd_unit": "hydra-umc-a.service"})
        _, problems = PORTS.collect(self.workspace)
        self.assertTrue(any("has no file" in p for p in problems))

    def test_an_installer_naming_an_unknown_unit_is_reported_and_a_known_one_is_not(self):
        self.repo("HYDRA-UMC-A", {"port": 8100, "systemd_unit": "hydra-umc-a.service"}, "x\n", {
            "HYDRA-UMC-OS/provisioning/install_a.sh":
                "systemctl enable --now hydra-umc-a.service\nsystemctl start hydra-umc-ghost.service\n# hydra-umc-comment.service\n",
        })
        services, _ = PORTS.collect(self.workspace)
        problems = PORTS.installer_problems(self.workspace, services)
        self.assertEqual(len(problems), 1)
        self.assertIn("hydra-umc-ghost.service", problems[0])

    def test_the_registry_round_trips(self):
        services = [{"name": "HYDRA-UMC-A", "port": 8100, "health_path": "/health", "systemd_unit": None}]
        self.assertEqual(PORTS.parse(PORTS.render(services)), services)

    def test_check_passes_after_a_write_and_fails_on_drift(self):
        self.repo("HYDRA-UMC-A", {"port": 8100, "health_path": "/health"})
        registry = self.workspace / "ports.yaml"
        args = ["--workspace", str(self.workspace), "--registry", str(registry)]
        self.assertEqual(PORTS.main(["--check", *args]), 1)
        self.assertEqual(PORTS.main(args), 0)
        self.assertEqual(PORTS.main(["--check", *args]), 0)
        self.repo("HYDRA-UMC-B", {"port": 8101})
        self.assertEqual(PORTS.main(["--check", *args]), 1)


class ValidatorAdoptionTests(Workspace):
    CANONICAL = (
        "import json\nfrom _doc_policy import (\n    check_a,\n    check_b,\n)\n"
        "# a comment\ndef main():\n    check_a()\n    check_b()\n"
    )

    def setUp(self):
        super().setUp()
        self.canonical = self.workspace / "_canonical"
        self.canonical.mkdir()
        (self.canonical / "ci_validate.py").write_text(self.CANONICAL, encoding="utf-8")

    def put(self, name, text):
        repo = self.workspace / name
        (repo / "tools").mkdir(parents=True)
        (repo / "hydra-umc.project.json").write_text("{}", encoding="utf-8")
        (repo / "tools" / "ci_validate.py").write_text(text, encoding="utf-8")

    def test_comment_only_differences_are_not_drift(self):
        self.put("HYDRA-UMC-A", self.CANONICAL.replace("# a comment", "# another"))
        self.assertEqual(SYNC.unified_status(self.workspace, self.canonical), ([], []))

    def test_a_copy_that_lacks_a_shared_check_is_stale_and_gets_the_canonical_text(self):
        self.put("HYDRA-UMC-A", "import json\nfrom _doc_policy import check_a\ndef main():\n    check_a()\n")
        stale, adapted = SYNC.unified_status(self.workspace, self.canonical)
        self.assertEqual((stale, adapted), (["HYDRA-UMC-A"], []))
        self.assertEqual(SYNC.write_unified(self.workspace, self.canonical), ["HYDRA-UMC-A/tools/ci_validate.py"])
        self.assertEqual(SYNC.unified_status(self.workspace, self.canonical), ([], []))

    def test_a_copy_with_a_check_of_its_own_is_left_alone(self):
        self.put("HYDRA-UMC-A", self.CANONICAL + "    check_own()\n")
        self.assertEqual(SYNC.unified_status(self.workspace, self.canonical), ([], ["HYDRA-UMC-A"]))
        self.assertEqual(SYNC.write_unified(self.workspace, self.canonical), [])


class PreviousCanonicalTests(ValidatorAdoptionTests):
    def test_a_copy_of_the_previous_canonical_text_is_stale_not_an_adaptation(self):
        previous = self.canonical / "previous"
        previous.mkdir()
        (previous / "ci_validate.py").write_text(self.CANONICAL.replace("check_b", "check_old"), encoding="utf-8")
        # without the previous text the old lines would look like an adaptation of the repository
        self.put("HYDRA-UMC-A", self.CANONICAL.replace("check_b", "check_old"))
        stale, adapted = SYNC.unified_status(self.workspace, self.canonical)
        self.assertEqual((stale, adapted), (["HYDRA-UMC-A"], []))
        self.assertEqual(SYNC.write_unified(self.workspace, self.canonical), ["HYDRA-UMC-A/tools/ci_validate.py"])
        self.assertEqual(SYNC.unified_status(self.workspace, self.canonical), ([], []))

    def test_without_the_previous_text_old_lines_are_the_repositorys_own(self):
        self.put("HYDRA-UMC-A", self.CANONICAL.replace("check_b", "check_old"))
        self.assertEqual(SYNC.unified_status(self.workspace, self.canonical), ([], ["HYDRA-UMC-A"]))


class BuildTestUnificationTests(Workspace):
    """The build test follows the same rule as the validator, in the same run."""

    def test_both_files_are_handled_in_one_run(self):
        self.assertEqual([relative for relative, _ in SYNC.UNIFIED_FILES], ["tools/ci_validate.py", "tools/build_test.py"])
        canonical = self.workspace / "_canonical"
        canonical.mkdir()
        (canonical / "build_test.py").write_text("import sys\ndef main():\n    run()\n    extra()\n", encoding="utf-8")
        repo = self.workspace / "HYDRA-UMC-A"
        (repo / "tools").mkdir(parents=True)
        (repo / "hydra-umc.project.json").write_text("{}", encoding="utf-8")
        (repo / "tools" / "build_test.py").write_text("import sys\ndef main():\n    run()\n", encoding="utf-8")
        relative, name = SYNC.UNIFIED_FILES[1]
        self.assertEqual(SYNC.unified_status(self.workspace, canonical, relative, name), (["HYDRA-UMC-A"], []))
        self.assertEqual(SYNC.write_unified(self.workspace, canonical, relative, name), ["HYDRA-UMC-A/tools/build_test.py"])
        self.assertEqual(SYNC.unified_status(self.workspace, canonical, relative, name), ([], []))


class ExtraHooksTests(unittest.TestCase):
    """The canonical validator and build test run the steps a repository keeps in tools/extra_*.py."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "tools").mkdir()
        # the canonical validator imports _doc_policy and _readme_parity from the tools folder next to it
        sys.path.insert(0, str(SDK / "tools"))
        self.addCleanup(sys.path.remove, str(SDK / "tools"))
        self.validate = _load("canonical_ci_validate", SDK / "tools" / "canonical" / "ci_validate.py")
        self.validate.ROOT = self.root

    def extra(self, text):
        (self.root / "tools" / "extra_checks.py").write_text(text, encoding="utf-8")

    def test_no_extra_file_is_no_extra_check(self):
        self.validate.run_extra_checks()

    def test_a_clean_extra_check_passes(self):
        self.extra("def check(root):\n    return []\n")
        self.validate.run_extra_checks()

    def test_a_problem_of_the_extra_check_fails_the_validation_with_its_words(self):
        self.extra("def check(root):\n    return ['the catalogue is out of date', 'a second problem']\n")
        import contextlib
        import io

        captured = io.StringIO()
        with contextlib.redirect_stderr(captured), self.assertRaises(SystemExit):
            self.validate.run_extra_checks()
        self.assertIn("the catalogue is out of date; a second problem", captured.getvalue())
        self.assertIn("CI_VALIDATION=FAIL", captured.getvalue())

    def test_an_extra_file_without_check_is_refused(self):
        self.extra("x = 1\n")
        with self.assertRaises(SystemExit):
            self.validate.run_extra_checks()

    def test_the_extra_check_receives_the_repository_root(self):
        self.extra("def check(root):\n    return [] if (root / 'tools').is_dir() else ['no tools folder']\n")
        self.validate.run_extra_checks()

    def test_the_canonical_build_test_names_the_extra_steps_hook(self):
        text = (SDK / "tools" / "canonical" / "build_test.py").read_text(encoding="utf-8")
        self.assertIn('ROOT / "tools" / "extra_build_steps.py"', text)
        self.assertLess(text.index("extra_build_steps.py"), text.index("BUILD_TEST=PASS"))


class PerRepositoryCopyTests(Workspace):
    def test_the_redaction_copies_are_checked_and_written(self):
        name = "HYDRA-UMC-OPS-AGENT"
        self.repo(name)
        self.assertEqual(len(SYNC.check_per_repository(self.workspace)), 2)
        self.assertEqual(len(SYNC.write_per_repository(self.workspace)), 2)
        self.assertEqual(SYNC.check_per_repository(self.workspace), [])
        self.assertEqual(SYNC.write_per_repository(self.workspace), [])


if __name__ == "__main__":
    unittest.main()
