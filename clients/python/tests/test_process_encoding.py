# =============================================================================
# HYDRA-UMC-SDK - clients/python/tests/test_process_encoding.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The shared tools read what a child process writes as UTF-8: text mode without an encoding reads with the code page of Windows."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCES = {name: ROOT / "tools" / "canonical" / (name + ".py") for name in ("status_lights", "universal_readme_check")}


def text_calls_without_encoding(source: str) -> list[int]:
    """The lines where a process is started in text mode without saying which encoding."""
    lines = []
    for node in ast.walk(ast.parse(source)):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"run", "Popen", "check_output"}):
            continue
        keywords = {k.arg: k.value for k in node.keywords}
        given = [keywords.get(name) for name in ("text", "universal_newlines")]
        text_mode = any(isinstance(value, ast.Constant) and value.value is True for value in given)
        if text_mode and not {"encoding", "errors"} <= set(keywords):
            lines.append(node.lineno)
    return lines


class ProcessEncodingTests(unittest.TestCase):
    def test_the_scan_finds_a_call_without_encoding(self):
        self.assertEqual(text_calls_without_encoding("import subprocess\nsubprocess.run(['x'], text=True)\n"), [2])

    def test_the_shared_tools_name_the_encoding_of_what_they_read(self):
        found = {name: text_calls_without_encoding(path.read_text(encoding="utf-8")) for name, path in SOURCES.items()}
        self.assertEqual({name: lines for name, lines in found.items() if lines}, {})


if __name__ == "__main__":
    unittest.main()
