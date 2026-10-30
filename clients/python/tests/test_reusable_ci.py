# =============================================================================
# HYDRA-UMC-SDK - The reusable CI workflow and its caller
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REUSABLE = ROOT / ".github" / "workflows" / "reusable-ci.yml"
CALLER = ROOT / "tools" / "canonical" / "ci-caller.yml"

# the stacks one baseline has to serve, each with the file that switches its steps on
STACKS = {
    "Python": "pyproject.toml",
    "Node": "package.json",
    "Rust": "Cargo.toml",
    "Go": "go.mod",
    "Flutter": "pubspec.yaml",
    "Android": "gradlew",
    "firmware": "build_firmware.sh",
}


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


class ReusableWorkflowTests(unittest.TestCase):
    def test_it_is_callable_and_does_not_run_on_its_own(self) -> None:
        body = text(REUSABLE)
        self.assertRegex(body, r"(?m)^on:\n  workflow_call:\n")
        self.assertNotRegex(body, r"(?m)^  (push|pull_request|schedule):")

    def test_it_asks_for_read_access_only(self) -> None:
        self.assertRegex(text(REUSABLE), r"(?m)^permissions:\n  contents: read\n")

    def test_validation_goes_through_the_project_tool(self) -> None:
        body = text(REUSABLE)
        self.assertIn("python tools/hydra_project_tool.py validate", body)
        self.assertNotIn("run: python tools/ci_validate.py", body)

    def test_every_stack_has_a_step_switched_on_by_its_own_file(self) -> None:
        body = text(REUSABLE)
        for stack, marker in STACKS.items():
            with self.subTest(stack=stack):
                self.assertRegex(body, r"hashFiles\('" + re.escape(marker) + r"'\)", stack)

    def test_a_build_never_bumps_a_version(self) -> None:
        body = text(REUSABLE)
        for needle in ("./gradlew test", "./build_firmware.sh"):
            index = body.index(needle)
            self.assertIn('HYDRA_UMC_CI: "1"', body[max(0, index - 400):index], needle)

    def test_versions_are_inputs_with_defaults(self) -> None:
        body = text(REUSABLE)
        self.assertIn("${{ inputs.python-version }}", body)
        self.assertIn("${{ inputs.node-version }}", body)
        self.assertRegex(body, r'python-version:\n(?:.*\n){2}\s+default: "3\.12"')

    def test_actions_are_pinned_to_a_major_version(self) -> None:
        for line in text(REUSABLE).splitlines():
            match = re.match(r"\s+uses: (\S+)", line)
            if match:
                self.assertRegex(match.group(1), r"@(v\d+|stable)$", line)


class CallerTests(unittest.TestCase):
    def test_it_calls_the_reusable_workflow_of_the_sdk(self) -> None:
        self.assertRegex(
            text(CALLER),
            r"(?m)^    uses: JuanenRac/HYDRA-UMC-SDK/\.github/workflows/reusable-ci\.yml@\S+$",
        )

    def test_it_runs_on_push_pull_request_and_by_hand(self) -> None:
        body = text(CALLER)
        for trigger in ("push:", "pull_request:", "workflow_dispatch:"):
            self.assertIn("\n  " + trigger, body)

    def test_it_carries_no_step_of_its_own(self) -> None:
        self.assertNotIn("steps:", text(CALLER))


if __name__ == "__main__":
    unittest.main()
