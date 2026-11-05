"""The lock on builds that compile on the PC of the developer (tools/local_build.py) and the places that ask it. Nothing here compiles."""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import local_build  # noqa: E402

NO_CI = {name: "" for name in ("CI", "GITHUB_ACTIONS", "ALLOW_LOCAL_BUILD")}


class LockTests(unittest.TestCase):
    def test_plain_environment_is_locked(self):
        self.assertFalse(local_build.local_build_allowed({}))
        self.assertIn("ALLOW_LOCAL_BUILD=1", local_build.local_build_refusal({}))

    def test_ci_and_the_owner_switch_allow_it(self):
        self.assertTrue(local_build.local_build_allowed({"CI": "true"}))
        self.assertTrue(local_build.local_build_allowed({"GITHUB_ACTIONS": "true"}))
        self.assertTrue(local_build.local_build_allowed({"ALLOW_LOCAL_BUILD": "1"}))
        self.assertFalse(local_build.local_build_allowed({"CI": "false", "ALLOW_LOCAL_BUILD": "0"}))
        self.assertIsNone(local_build.local_build_refusal({"CI": "1"}))

    def test_the_go_program_of_the_chain_is_not_built_on_a_plain_pc(self):
        import chain_support

        with mock.patch.dict(os.environ, NO_CI), mock.patch.object(chain_support.subprocess, "run", side_effect=AssertionError("compiled")):
            os.environ.pop("HYDRA_UMC_NODE_HEALING_BIN", None)
            self.assertIsNone(chain_support.build_node_healing(Path(".")))

    def test_the_native_clients_are_skipped_on_a_plain_pc(self):
        import io
        import contextlib
        import extra_build_steps

        out = io.StringIO()
        with mock.patch.dict(os.environ, NO_CI), mock.patch.object(extra_build_steps, "run", side_effect=lambda *command, **kw: self.assertNotIn(command[0], ("go", "cargo"))), \
                mock.patch.object(extra_build_steps.shutil, "which", return_value="/bin/tool"), contextlib.redirect_stdout(out):
            os.environ.pop("CI", None)
            os.environ.pop("GITHUB_ACTIONS", None)
            extra_build_steps.run_native_clients()
        self.assertIn("GO_CLIENT=SKIPPED", out.getvalue())
        self.assertIn("RUST_CLIENT=SKIPPED", out.getvalue())


if __name__ == "__main__":
    unittest.main()
