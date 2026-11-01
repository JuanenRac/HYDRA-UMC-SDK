# =============================================================================
# HYDRA-UMC-SDK - The baseline composite action every workflow calls
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ACTION = ROOT / "tools" / "canonical" / "hydra-baseline-action.yml"

# the stacks one baseline has to serve, each with the file that switches its steps on
STACKS = {
    "Node": "package.json",
    "Rust": "Cargo.toml",
    "Go": "go.mod",
    "Flutter": "pubspec.yaml",
    "Android": "gradlew",
    "firmware": "build_firmware.sh",
}


def _sync():
    spec = importlib.util.spec_from_file_location("sync_repo_tools", ROOT / "tools" / "sync_repo_tools.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SYNC = _sync()


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


class ActionTests(unittest.TestCase):
    def test_it_is_a_composite_action_and_every_run_step_names_its_shell(self) -> None:
        body = text(ACTION)
        self.assertRegex(body, r"(?m)^runs:\n  using: composite\n")
        steps = body.split("\n  steps:\n", 1)[1].split("\n    - name: ")
        for step in steps[1:]:
            if "\n      run:" in step:
                self.assertIn("shell: bash", step, step.splitlines()[0])

    def test_validation_goes_through_the_validator_of_the_repository(self) -> None:
        self.assertIn("run: python tools/ci_validate.py", text(ACTION))

    def test_every_stack_has_a_step_switched_on_by_its_own_file(self) -> None:
        body = text(ACTION)
        for stack, marker in STACKS.items():
            with self.subTest(stack=stack):
                self.assertRegex(body, r"hashFiles\('" + re.escape(marker) + r"'\)")

    def test_a_build_never_bumps_a_version(self) -> None:
        body = text(ACTION)
        for needle in ("./gradlew $ANDROID_TASKS", "./build_firmware.sh"):
            index = body.index(needle)
            self.assertIn('HYDRA_UMC_CI: "1"', body[max(0, index - 400):index], needle)

    def test_the_caches_are_there(self) -> None:
        body = text(ACTION)
        for needle in ("cache: pip", "cache: npm", "cache: gradle", "Swatinem/rust-cache@", "cache: true"):
            self.assertIn(needle, body)

    def test_third_party_actions_are_pinned_to_a_commit(self) -> None:
        for line in text(ACTION).splitlines():
            match = re.match(r"\s+uses: (\S+)", line)
            if match and not match.group(1).startswith(("actions/", "dtolnay/", "subosito/")):
                self.assertRegex(match.group(1), r"@[0-9a-f]{40}$", line)

    def test_the_inputs_have_defaults_that_keep_the_plain_repository_working(self) -> None:
        body = text(ACTION)
        for name, default in (("python-version", '"3.12"'), ("python-tests", "none"), ("lint", "none"), ("go-checks", "basic")):
            self.assertRegex(body, rf"(?m)^  {name}:\n(?:    .*\n)*?    default: {re.escape(default)}\n", name)


class NodeChecksTests(unittest.TestCase):
    def test_node_checks_default_to_full_and_none_leaves_the_node_steps_to_the_workflow(self) -> None:
        body = text(ACTION)
        self.assertRegex(body, r"(?m)^  node-checks:\n(?:    .*\n)*?    default: full\n")
        steps = body.split("\n    - name: ")
        node_steps = [step for step in steps if step.startswith(("Set up Node.js", "Validate Node.js or TypeScript project"))]
        self.assertEqual(len(node_steps), 2)
        for step in node_steps:
            self.assertIn("inputs.node-checks != 'none'", step, step.splitlines()[0])


class PinTests(unittest.TestCase):
    def workspace(self, workflow: str) -> Path:
        base = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(base, ignore_errors=True))
        repo = base / "HYDRA-UMC-FAKE"
        (repo / ".github" / "workflows").mkdir(parents=True)
        (repo / "hydra-umc.project.json").write_text("{}", encoding="utf-8")
        (repo / ".github" / "workflows" / "ci.yml").write_text(workflow, encoding="utf-8")
        return base

    def test_the_pins_of_the_action_are_the_ones_every_workflow_must_have(self) -> None:
        pins = SYNC.lint_pins(text(ACTION))
        self.assertEqual(set(pins), {"ruff", "mypy"})
        same = self.workspace(f"run: pip install ruff=={next(iter(pins['ruff']))} mypy=={next(iter(pins['mypy']))}\n")
        self.assertEqual(SYNC.lint_pin_drift(same), [])

    def test_another_pin_is_drift(self) -> None:
        other = self.workspace("run: pip install ruff==0.0.1\n")
        drift = SYNC.lint_pin_drift(other)
        self.assertEqual(len(drift), 1)
        self.assertIn("ruff==0.0.1", drift[0])

    def test_the_action_is_one_of_the_canonical_files(self) -> None:
        self.assertEqual(dict(SYNC.canonical_items())[".github/actions/hydra-baseline/action.yml"], "hydra-baseline-action.yml")


if __name__ == "__main__":
    unittest.main()
