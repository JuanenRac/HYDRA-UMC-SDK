# =============================================================================
# HYDRA-UMC-SDK - tests of the time limits of the shared tools and workflows
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Every child process of the shared tools has a time limit that a setting can change, and the jobs of the workflow templates have one too.

Evidence: simulator (a child process that never ends is stood in for by an exception; no runner was held).
"""

from __future__ import annotations

import ast
import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools"
CANONICAL = TOOLS / "canonical"
SHARED = [
    CANONICAL / "hydra_project_tool.py", CANONICAL / "ci_validate.py", CANONICAL / "build_test.py",
    TOOLS / "hydra_project_tool.py", TOOLS / "ci_validate.py", TOOLS / "build_test.py", TOOLS / "_doc_policy.py", TOOLS / "make_structure.py",
]
RUNNERS = {"run", "check_output", "check_call", "call"}


def load(path: Path, name: str):
    sys.path.insert(0, str(TOOLS))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(TOOLS))


def calls_without_timeout(path: Path) -> list[int]:
    missing = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in RUNNERS:
            owner = node.func.value
            if isinstance(owner, ast.Name) and owner.id == "subprocess" and not any(k.arg == "timeout" for k in node.keywords):
                missing.append(node.lineno)
    return missing


def expired(*args, **kwargs):
    raise subprocess.TimeoutExpired(args[0] if args else "x", kwargs.get("timeout", 1))


class EveryCallHasALimitTests(unittest.TestCase):
    def test_no_child_process_of_the_shared_tools_runs_without_a_timeout(self):
        for path in SHARED:
            self.assertEqual(calls_without_timeout(path), [], str(path.relative_to(ROOT)))

    def test_the_scan_sees_a_call_without_a_limit(self):
        with tempfile.TemporaryDirectory() as folder:
            sample = Path(folder) / "sample.py"
            sample.write_text("import subprocess\nsubprocess.run(['git'])\nsubprocess.check_output(['git'], timeout=5)\n", encoding="utf-8")
            self.assertEqual(calls_without_timeout(sample), [2])

    def test_the_canonical_copy_and_the_copy_in_tools_agree_on_the_limits(self):
        for name in ("hydra_project_tool.py", "ci_validate.py", "build_test.py"):
            a = re.findall(r"timeout=\w+", (CANONICAL / name).read_text(encoding="utf-8"))
            b = re.findall(r"timeout=\w+", (TOOLS / name).read_text(encoding="utf-8"))
            self.assertEqual(a, b, name)


class SettingTests(unittest.TestCase):
    def test_the_defaults_and_the_environment(self):
        module = load(CANONICAL / "hydra_project_tool.py", "timeouts_hpt")
        self.assertEqual((module.GIT_TIMEOUT_S, module.COMMAND_TIMEOUT_S), (120.0, 3600.0))
        read = module._seconds_from_environment
        for raw, expected in (("45", 45.0), ("0.5", 0.5), ("0", 7.0), ("-3", 7.0), ("abc", 7.0), ("", 7.0), ("nan", 7.0), ("inf", 7.0)):
            with mock.patch.dict("os.environ", {"HYDRA_UMC_TEST_S": raw}):
                self.assertEqual(read("HYDRA_UMC_TEST_S", 7.0), expected, raw)

    def test_every_tool_reads_the_same_two_settings(self):
        for path in SHARED:
            text = path.read_text(encoding="utf-8")
            self.assertIn("HYDRA_UMC_GIT_TIMEOUT_S", text, path.name)
            self.assertIn("HYDRA_UMC_COMMAND_TIMEOUT_S", text, path.name)


class StuckProcessTests(unittest.TestCase):
    def test_a_stuck_git_in_the_project_tool_is_a_failed_result_not_a_hang(self):
        module = load(CANONICAL / "hydra_project_tool.py", "timeouts_hpt2")
        with mock.patch.object(module.subprocess, "run", side_effect=expired):
            result = module._git(ROOT, "status")
            self.assertEqual(result.returncode, 124)
            self.assertIn("timed out", result.stderr)
            self.assertIsNone(module._newest_sdk_tag(ROOT))
            self.assertEqual(module._capture(["x"], ROOT).returncode, 124)

    def test_a_stuck_command_in_the_project_tool_returns_124_and_says_so(self):
        module = load(CANONICAL / "hydra_project_tool.py", "timeouts_hpt3")
        with mock.patch.object(module.subprocess, "run", side_effect=expired), mock.patch("sys.stderr") as err:
            self.assertEqual(module._run(["sleep", "9"], ROOT), 124)
        self.assertTrue(err.write.called)

    def test_the_limit_is_passed_to_the_child_process(self):
        module = load(CANONICAL / "hydra_project_tool.py", "timeouts_hpt4")
        with mock.patch.object(module.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")) as run:
            module._git(ROOT, "status")
            module._run(["true"], ROOT)
        self.assertEqual([call.kwargs["timeout"] for call in run.call_args_list], [module.GIT_TIMEOUT_S, module.COMMAND_TIMEOUT_S])

    def test_a_stuck_build_step_fails_the_build_test_with_a_message(self):
        module = load(CANONICAL / "build_test.py", "timeouts_bt")
        with mock.patch.object(module.subprocess, "run", side_effect=expired), self.assertRaises(SystemExit) as stop:
            module.run("sleep", "9")
        self.assertEqual(stop.exception.code, 1)

    def test_a_stuck_git_ls_files_means_no_tracked_list(self):
        module = load(TOOLS / "make_structure.py", "timeouts_ms")
        with mock.patch.object(module.subprocess, "run", side_effect=expired):
            self.assertIsNone(module.tracked_files(ROOT))

    def test_a_stuck_git_in_the_documentation_policy_is_no_git_or_could_not_check(self):
        module = load(TOOLS / "_doc_policy.py", "timeouts_dp")
        with mock.patch.object(module.subprocess, "run", side_effect=expired):
            self.assertFalse(module._is_git_work_tree(ROOT))
            grep = module._git_grep(ROOT, ("git", "grep", "x"))
        self.assertEqual(grep.returncode, 2)


class WorkflowTemplateTests(unittest.TestCase):
    JOB = re.compile(r"^  ([A-Za-z0-9_-]+):\n((?:    .*\n|\n)+)", re.M)

    def jobs(self, path: Path):
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        return [(m.group(1), m.group(2)) for m in self.JOB.finditer(text.split("\njobs:\n", 1)[1] + "\n")]

    def test_the_jobs_of_the_templates_and_of_this_repository_have_a_time_limit(self):
        files = [CANONICAL / "dashboard-dispatch.yml"]
        files += list((ROOT / ".github" / "workflows").glob("*.yml"))
        checked = 0
        for path in files:
            for name, body in self.jobs(path):
                if re.search(r"(?m)^    uses:", body):  # a call of a reusable workflow cannot carry the key
                    continue
                self.assertRegex(body, r"(?m)^    timeout-minutes: \d+$", f"{path.name}:{name}")
                checked += 1
        self.assertGreaterEqual(checked, 6)

    def test_the_notifier_limit_is_short(self):
        body = dict(self.jobs(CANONICAL / "dashboard-dispatch.yml"))["notify"]
        self.assertLessEqual(int(re.search(r"timeout-minutes: (\d+)", body).group(1)), 15)


if __name__ == "__main__":
    unittest.main()
