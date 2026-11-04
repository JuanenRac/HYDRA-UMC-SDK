# =============================================================================
# HYDRA-UMC-SDK - Tests of the catalogue of the URTC tools
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""contracts/urtc_tools.json: the common list of the tool modes of the URTC family, as the services and apps resolve them."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOGUE = ROOT / "contracts" / "urtc_tools.json"


class UrtcToolsCatalogueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads(CATALOGUE.read_text(encoding="utf-8"))

    def test_the_ids_are_consecutive_and_the_invalid_one_follows(self) -> None:
        ids = [tool["tool_id"] for tool in self.data["tools"]]
        self.assertEqual(ids, list(range(len(ids))))
        self.assertEqual(self.data["invalid_tool_id"], len(ids))

    def test_names_and_titles_are_unique_and_the_names_are_constants(self) -> None:
        names = [tool["name"] for tool in self.data["tools"]]
        titles = [tool["title"] for tool in self.data["tools"]]
        self.assertEqual(len(set(names)), len(names))
        self.assertEqual(len(set(titles)), len(titles))
        for name in names:
            self.assertRegex(name, r"^TOOL_[A-Z0-9_]+$")

    def test_the_copy_equals_the_one_of_the_documentation_repository_when_it_is_next_to_this_one(self) -> None:
        other = ROOT.parent / "HYDRA-UMC-DOCS" / "data" / "urtc_tools.json"
        if not other.is_file():
            self.skipTest("HYDRA-UMC-DOCS is not next to this checkout")
        self.assertEqual(json.loads(other.read_text(encoding="utf-8")), self.data)


if __name__ == "__main__":
    unittest.main()
