# =============================================================================
# HYDRA-UMC-SDK - Keeping the CI quick without taking a check away
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D)
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The baseline action, the workflow of the SDK and its other workflows keep the CI quick (the text of the files is read, nothing runs).

* the slow steps of the baseline action (Rust, Flutter, Android or Wear OS, firmware) can be switched off with the input `slow`, which is on by default;
* the validation of the manifest and of the documents, the compilation of the Python sources and the tests of the tools never depend on it;
* a newer push to a branch cancels the run before it, and main and the tags are never cancelled;
* the workflow waits for the changed-paths answer only for the slow steps, and a question that cannot be answered counts as yes;
* the CHANGELOG files merge as a union."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ACTION = ROOT / "tools" / "canonical" / "hydra-baseline-action.yml"
WORKFLOWS = ROOT / ".github" / "workflows"
CANCEL_EXPRESSION = "${{ github.ref != 'refs/heads/main' && !startsWith(github.ref, 'refs/tags/') }}"
SLOW = ("Set up Rust", "Cache the Cargo registry and the build directory", "Validate Rust project", "Set up Flutter", "Validate Flutter project",
        "Set up Java for Android or Wear OS", "Validate Android or Wear OS project", "Install ARM GNU Toolchain", "Compile firmware")
ALWAYS = ("Validate manifest, version, documentation and secret policy", "Compile Python sources", "Validate v1 SDK contract fixtures")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def steps(text: str, indent: str) -> dict[str, str]:
    """The text of each named step; `indent` is the indentation of the dash."""
    parts = re.split(rf"(?m)^{indent}- name: ", text)
    return {part.split("\n", 1)[0].strip(): part for part in parts[1:]}


class ActionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = read(ACTION)
        self.steps = steps(self.text, "    ")

    def test_the_input_is_on_by_default_so_a_caller_that_does_not_know_it_runs_everything(self) -> None:
        block = self.text.split("  slow:\n", 1)[1].split("\nruns:", 1)[0]
        self.assertIn('default: "true"', block)

    def test_every_slow_step_follows_the_input(self) -> None:
        for wanted in SLOW:
            found = [body for name, body in self.steps.items() if name.startswith(wanted)]
            self.assertTrue(found, wanted)
            for body in found:
                self.assertIn("inputs.slow != 'false'", body.split("shell:")[0].split("uses:")[0], wanted)

    def test_the_validation_of_the_repository_never_depends_on_it(self) -> None:
        for wanted in ALWAYS:
            found = [body for name, body in self.steps.items() if name.startswith(wanted)]
            self.assertTrue(found, wanted)
            for body in found:
                self.assertNotIn("inputs.slow", body, wanted)

    def test_the_checks_of_python_and_node_and_go_are_not_slow_steps(self) -> None:
        for name, body in self.steps.items():
            if re.search(r"Python|Node|Go\b|Lint|Type-check", name) and "Android" not in name:
                self.assertNotIn("inputs.slow", body, name)


class WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = read(WORKFLOWS / "ci.yml")

    def test_only_branch_runs_are_cancelled(self) -> None:
        for path in sorted(WORKFLOWS.glob("*.yml")):
            text = read(path)
            if re.search(r"(?m)^on:\n(?:.*\n)*?  push:", text) or re.search(r"(?m)^on:.*\bpush\b", text):
                self.assertNotRegex(text, r"cancel-in-progress:\s*true", path.name)
        self.assertIn(f"cancel-in-progress: {CANCEL_EXPRESSION}", self.text)
        self.assertIn(f"cancel-in-progress: {CANCEL_EXPRESSION}", read(WORKFLOWS / "codeql.yml"))

    def test_the_slow_steps_follow_the_answer_of_the_changed_paths_workflow(self) -> None:
        self.assertRegex(self.text, r"uses: JuanenRac/HYDRA-UMC-DOCS/\.github/workflows/changed-paths\.yml@[0-9a-f]{40}\n")
        self.assertIn("label: full-ci", self.text)
        baseline = self.text.split("\n  baseline:\n", 1)[1]
        self.assertIn("needs: changes", baseline)
        self.assertIn("if: ${{ !cancelled() }}", baseline)   # a question that could not be answered must not skip the validation
        decide = baseline.split("id: slow", 1)[1].split("- name:", 1)[0]
        for forced in ('"refs/heads/main"', "refs/tags/", '"$MATCHED" != "false"'):
            self.assertIn(forced, decide)
        named = steps(baseline, "      ")
        for wanted in SLOW:
            for name, body in named.items():
                if name.startswith(wanted):
                    self.assertIn("steps.slow.outputs.run == 'true'", body, name)
        for wanted in ALWAYS:
            for name, body in named.items():
                if name.startswith(wanted):
                    self.assertNotIn("steps.slow", body, name)

    def test_every_job_has_a_time_limit_and_the_token_is_read_only(self) -> None:
        self.assertRegex(self.text, r"(?m)^permissions:\n  contents: read$")
        self.assertRegex(self.text.split("\n  baseline:\n", 1)[1], r"(?m)^    timeout-minutes: \d+$")

    def test_the_bench_of_the_pull_requests_cancels_the_run_it_replaces(self) -> None:
        self.assertIn(f"cancel-in-progress: {CANCEL_EXPRESSION}", read(WORKFLOWS / "integration.yml"))

    def test_no_macos_job_starts_on_every_pull_request(self) -> None:
        for path in sorted(WORKFLOWS.glob("*.yml")):
            text = read(path)
            if "macos-" in text and re.search(r"(?m)^  pull_request:", text):
                self.assertRegex(text, r"github\.event_name", path.name)

    def test_the_changelog_files_merge_as_a_union(self) -> None:
        attributes = read(ROOT / ".gitattributes")
        for pattern in ("CHANGELOG.md", "CHANGELOG_*.md", "CHANGELOG.*.md"):
            self.assertIn(f"{pattern} merge=union", attributes)


if __name__ == "__main__":
    unittest.main()
