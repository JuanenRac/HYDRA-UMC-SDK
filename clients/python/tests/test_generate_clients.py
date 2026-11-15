# =============================================================================
# HYDRA-UMC-SDK - Tests of the typed client generated from the server contract
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""generated/hydra-server-client.ts is the output of tools/generate_clients.py and has one method per route."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("generate_clients", ROOT / "tools" / "generate_clients.py")
gc = importlib.util.module_from_spec(_spec)
sys.modules["generate_clients"] = gc
_spec.loader.exec_module(gc)

FULL = json.loads((ROOT / "contracts" / "openapi" / "v1" / "server.full.openapi.json").read_text(encoding="utf-8"))
OPS = gc.operations(FULL)
SOURCE = (ROOT / "generated" / gc.TS_NAME).read_text(encoding="utf-8")


class GeneratedClientTests(unittest.TestCase):
    def test_the_committed_file_is_the_generator_output(self):
        committed = (ROOT / "generated" / gc.TS_NAME).read_bytes().replace(b"\r\n", b"\n")
        self.assertEqual(committed, gc.outputs()[gc.TS_NAME].encode("utf-8"))

    def test_every_route_has_one_method_and_the_names_are_unique(self):
        routes = {(m.upper(), p) for p, item in FULL["paths"].items() for m in item if m in gc.METHODS}
        self.assertEqual({(o["method"], o["path"]) for o in OPS}, routes)
        self.assertEqual(len({o["name"] for o in OPS}), len(OPS))
        for op in OPS:
            self.assertIn(f"  {op['name']}(", SOURCE)

    def test_every_named_schema_is_an_exported_type(self):
        for name in FULL["components"]["schemas"]:
            self.assertRegex(SOURCE, rf"export (interface|type) {name}\b")

    def test_a_route_with_path_parameters_asks_for_them_all(self):
        for op in OPS:
            names = re.findall(r"\{([^}]+)\}", op["path"])
            self.assertEqual([p["name"] for p in op["path_parameters"]], names)
            signature, required = gc.arguments(op)
            if names:
                self.assertTrue(required)
            for name in names:
                self.assertIn(name, signature)

    def test_the_method_name_is_made_from_the_verb_and_the_path(self):
        self.assertEqual(gc.operation_name("get", "/api/robot/{id}/state"), "getRobotByIdState")
        self.assertEqual(gc.operation_name("post", "/api/bridges/{name}/cmd/{verb}"), "postBridgesByNameCmdByVerb")
        self.assertEqual(gc.operation_name("get", "/.well-known/jwks.json"), "getWellKnownJwksJson")

    def test_the_schema_subset_maps_to_typescript(self):
        self.assertEqual(gc.type_of({"type": "integer"}), "number")
        self.assertEqual(gc.type_of({"type": "string", "nullable": True}), "string | null")
        self.assertEqual(gc.type_of({"enum": ["a", "b"]}), '"a" | "b"')
        self.assertEqual(gc.type_of({"type": "array", "items": {"$ref": "#/components/schemas/Thing"}}), "Thing[]")
        self.assertEqual(gc.type_of({"type": "array", "items": {"enum": ["a", "b"]}}), '("a" | "b")[]')
        self.assertEqual(gc.type_of({"type": "object"}), "Record<string, unknown>")
        self.assertEqual(gc.type_of({"type": "object", "required": ["x"], "properties": {"x": {"type": "string"}, "y-z": {"type": "boolean"}}}),
                         '{ x: string; "y-z"?: boolean }')
        self.assertEqual(gc.type_of(None), "unknown")

    def test_a_clash_of_method_names_stops_the_generator(self):
        document = {"paths": {"/a/{x}": {"get": {}}, "/a/ByX": {"get": {}}}, "components": {"schemas": {}}}
        with self.assertRaises(SystemExit):
            gc.operations(document)

    def test_the_transport_helpers_refuse_a_missing_path_value(self):
        self.assertIn("missing path parameter", SOURCE)
        self.assertIn("encodeURIComponent", SOURCE)

    def test_the_operation_list_matches_the_methods(self):
        listed = re.findall(r'^  "([A-Za-z0-9]+)",$', SOURCE, flags=re.M)
        self.assertEqual(listed, [o["name"] for o in OPS])


if __name__ == "__main__":
    unittest.main()
