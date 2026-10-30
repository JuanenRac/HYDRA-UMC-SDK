# =============================================================================
# HYDRA-UMC-SDK - Shared model weights probe
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hydra_umc_sdk import ANY_WEIGHT_SUFFIXES, COMPILED_MODEL_SUFFIXES, contains_model_artifact


class ModelWeightsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def write(self, relative: str, data: bytes = b"x") -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def test_missing_directory_has_no_weights(self) -> None:
        self.assertFalse(contains_model_artifact(self.root / "nope"))

    def test_documents_placeholders_and_tokenizers_are_not_weights(self) -> None:
        for name in (".gitkeep", "README.md", "tokenizer.json", "config.yaml"):
            self.write(name)
        self.assertFalse(contains_model_artifact(self.root))

    def test_empty_weight_file_is_not_a_weight(self) -> None:
        self.write("a.gguf", b"")
        self.assertFalse(contains_model_artifact(self.root))

    def test_any_format_counts_for_the_default_list(self) -> None:
        for suffix in sorted(ANY_WEIGHT_SUFFIXES):
            with self.subTest(suffix=suffix):
                folder = self.root / suffix.strip(".")
                self.write(f"{folder.name}/model{suffix}")
                self.assertTrue(contains_model_artifact(folder))

    def test_suffix_match_is_case_insensitive_and_found_in_subfolders(self) -> None:
        self.write("deep/er/MODEL.GGUF")
        self.assertTrue(contains_model_artifact(self.root))

    def test_the_compiled_list_only_accepts_hef(self) -> None:
        self.write("llm.gguf")
        self.assertFalse(contains_model_artifact(self.root, COMPILED_MODEL_SUFFIXES))
        self.write("net.hef")
        self.assertTrue(contains_model_artifact(self.root, COMPILED_MODEL_SUFFIXES))

    def test_the_walk_stops_after_the_file_limit(self) -> None:
        for index in range(5):
            self.write(f"a{index}.txt")
        self.write("z.hef")
        self.assertFalse(contains_model_artifact(self.root, max_files=3))
        self.assertTrue(contains_model_artifact(self.root, max_files=100))

    def test_a_symbolic_link_is_not_followed(self) -> None:
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        target = Path(outside.name) / "real.hef"
        target.write_bytes(b"x")
        try:
            (self.root / "link.hef").symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symbolic links are not available here")
        self.assertFalse(contains_model_artifact(self.root))


if __name__ == "__main__":
    unittest.main()
