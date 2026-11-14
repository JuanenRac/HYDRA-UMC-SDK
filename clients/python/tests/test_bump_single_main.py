# =============================================================================
# HYDRA-UMC-SDK - tests of the single main guard that tools/sync_version_tools.py leaves in a bump script
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from __future__ import annotations

import ast
import importlib.util
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[3] / "tools"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VERSIONS = _load("sync_version_tools")

BLOCK_FORM = 'def main():\n    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n'
INLINE_FORM = 'def main():\n    return 0\n\n\nif __name__ == "__main__": main()\n'


def guards(text: str) -> int:
    return sum(
        1
        for node in ast.parse(text).body
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare) and getattr(node.test.left, "id", "") == "__name__"
    )


class SingleMainGuardTests(unittest.TestCase):
    def patched(self, source: str, newline: str = "\n") -> str:
        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / "bump_version.py"
            script.write_bytes(source.replace("\n", newline).encode("utf-8"))
            self.assertTrue(VERSIONS.patch_bump_version(script))
            return script.read_bytes().decode("utf-8").replace("\r\n", "\n")

    def test_a_new_hand_over_leaves_one_guard_with_the_script_body_after_it(self):
        for source in (BLOCK_FORM, INLINE_FORM):
            text = self.patched(source)
            self.assertEqual(guards(text), 1)
            self.assertLess(text.index("_delegate_to_shared_utility()"), text.index("main()", text.index('if __name__')))
            self.assertIn("raise SystemExit(_shared_exit)", text)

    def test_the_inline_body_moves_to_its_own_line_and_still_runs(self):
        text = self.patched(INLINE_FORM)
        self.assertTrue(text.rstrip().endswith("    main()"))

    def test_line_endings_are_kept(self):
        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / "bump_version.py"
            script.write_bytes(BLOCK_FORM.replace("\n", "\r\n").encode("utf-8"))
            VERSIONS.patch_bump_version(script)
            raw = script.read_bytes()
            self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))

    def test_a_second_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / "bump_version.py"
            script.write_text(BLOCK_FORM, encoding="utf-8")
            VERSIONS.patch_bump_version(script)
            first = script.read_bytes()
            self.assertFalse(VERSIONS.patch_bump_version(script))
            self.assertFalse(VERSIONS.unify_double_guard(script))
            self.assertEqual(script.read_bytes(), first)

    def test_a_script_patched_by_an_older_run_is_folded_into_one_guard(self):
        for tail in ('if __name__ == "__main__": main()\n', 'if __name__ == "__main__":\n    raise SystemExit(main())\n'):
            old = "def main():\n    return 0\n\n\n" + VERSIONS.DELEGATION + VERSIONS.OLD_GUARD_BLOCK + tail
            self.assertEqual(guards(old), 2)
            with tempfile.TemporaryDirectory() as folder:
                script = Path(folder) / "bump_version.py"
                script.write_text(old, encoding="utf-8")
                self.assertTrue(VERSIONS.has_double_guard(old))
                self.assertTrue(VERSIONS.unify_double_guard(script))
                text = script.read_text(encoding="utf-8")
                self.assertEqual(guards(text), 1)
                self.assertFalse(VERSIONS.has_double_guard(text))
                self.assertFalse(VERSIONS.unify_double_guard(script))

    def test_the_hand_over_text_has_no_guard_of_its_own(self):
        self.assertNotIn("__main__", VERSIONS.DELEGATION)


if __name__ == "__main__":
    unittest.main()
