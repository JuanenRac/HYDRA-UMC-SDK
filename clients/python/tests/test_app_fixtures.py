# =============================================================================
# HYDRA-UMC-SDK - Tests of the answers generated for the apps
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The generated answers (conformance/app-fixtures) follow the full inventory and every body conforms to its shape."""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

from hydra_umc_sdk.openapi_mock import conforms

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("make_app_fixtures", ROOT / "tools" / "make_app_fixtures.py")
assert SPEC and SPEC.loader
TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOL)


class AppFixturesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = json.loads(TOOL.INVENTORY.read_text(encoding="utf-8"))

    def test_the_file_is_what_the_inventory_produces(self) -> None:
        self.assertEqual(TOOL.OUTPUT.read_text(encoding="utf-8"), TOOL.render(self.doc))

    def test_every_body_conforms_to_the_shape_it_was_built_from(self) -> None:
        checked = 0
        for key, answers in json.loads(TOOL.OUTPUT.read_text(encoding="utf-8"))["routes"].items():
            method, path = key.split(" ", 1)
            for status, bodies in answers.items():
                schema = self.doc["paths"][path][method.lower()]["responses"][status]["content"]["application/json"]["schema"]
                for kind, body in bodies.items():
                    self.assertIsNone(conforms(body, schema, self.doc), f"{key} {status} {kind}")
                    checked += 1
        self.assertGreater(checked, 100)

    def test_the_full_body_has_at_least_the_fields_of_the_minimal_one(self) -> None:
        for key, answers in TOOL.build(self.doc)["routes"].items():
            for status, bodies in answers.items():
                if isinstance(bodies["minimal"], dict) and isinstance(bodies["full"], dict):
                    self.assertTrue(set(bodies["minimal"]) <= set(bodies["full"]), f"{key} {status}")


if __name__ == "__main__":
    unittest.main()
