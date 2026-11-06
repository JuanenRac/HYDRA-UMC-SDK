# =============================================================================
# HYDRA-UMC-SDK - Tests of the route tables generated for the clients
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The route tables in generated/ are the output of tools/generate_routes.py and list every route of the full inventory."""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("generate_routes", ROOT / "tools" / "generate_routes.py")
gr = importlib.util.module_from_spec(_spec)
sys.modules["generate_routes"] = gr
_spec.loader.exec_module(gr)

FULL = json.loads((ROOT / "contracts" / "openapi" / "v1" / "server.full.openapi.json").read_text(encoding="utf-8"))
TABLE = gr.rows(FULL)


class RouteTableTests(unittest.TestCase):
    def test_every_generated_file_is_the_committed_one(self):
        for name, text in gr.outputs().items():
            committed = (ROOT / "generated" / name).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(committed, text.encode("utf-8"), name)

    def test_every_route_of_the_inventory_has_one_row(self):
        expected = {(m.upper(), p) for p, item in FULL["paths"].items() for m in item}
        self.assertEqual({(r["method"], r["path"]) for r in TABLE}, expected)
        self.assertEqual(len(TABLE), len(expected))

    def test_the_rows_carry_access_query_and_statuses(self):
        row = next(r for r in TABLE if r["method"] == "GET" and r["path"] == "/api/connections/clients")
        self.assertEqual(row["access"], "user")
        self.assertIn("200", row["statuses"])
        self.assertTrue(row["query"])
        self.assertEqual({r["access"] for r in TABLE} - {"public", "user", "admin"}, set())

    def test_the_typed_slice_routes_are_all_in_the_table(self):
        slice_document = json.loads((ROOT / "contracts" / "openapi" / "v1" / "server.openapi.json").read_text(encoding="utf-8"))
        have = {(r["method"], r["path"]) for r in TABLE}
        for path, item in slice_document["paths"].items():
            for method in item:
                self.assertIn((method.upper(), path), have)

    def test_the_languages_list_the_same_number_of_routes(self):
        generated = ROOT / "generated"
        self.assertEqual(len(json.loads((generated / "hydra-routes.json").read_text(encoding="utf-8"))["routes"]), len(TABLE))
        self.assertEqual((generated / "hydra-routes.ts").read_text(encoding="utf-8").count("{ method:"), len(TABLE))
        self.assertEqual((generated / "HydraRoutes.kt").read_text(encoding="utf-8").count('HydraRoute("'), len(TABLE))
        self.assertEqual((generated / "hydra_routes.dart").read_text(encoding="utf-8").count("HydraRoute('"), len(TABLE))


if __name__ == "__main__":
    unittest.main()
