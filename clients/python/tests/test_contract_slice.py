# =============================================================================
# HYDRA-UMC-SDK - Tests of the source of the typed slice (server.openapi.json)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The typed slice of the server contract is generated from `contracts/sources/slice`: the committed document is the
byte-for-byte output of the generator, every route of it is in the full inventory, and the check fails on each drift."""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("contract_source", ROOT / "tools" / "contract_source.py")
cs = importlib.util.module_from_spec(_spec)
sys.modules["contract_source"] = cs
_spec.loader.exec_module(cs)

SLICE = cs.load_slice()
SOURCES = cs.load_sources()
COMMITTED = (ROOT / "contracts" / "openapi" / "v1" / "server.openapi.json").read_bytes()


class GeneratedSliceTests(unittest.TestCase):
    def test_the_committed_document_is_the_generated_one_byte_for_byte(self):
        self.assertEqual(cs.render(cs.build_slice(SLICE)).encode("utf-8"), COMMITTED.replace(b"\r\n", b"\n"))

    def test_the_document_keeps_its_shape(self):
        document = json.loads(COMMITTED)
        self.assertEqual(list(document), ["openapi", "info", "servers", "tags", "paths", "components"])
        self.assertEqual(list(document["components"]), ["securitySchemes", "schemas", "parameters"])
        self.assertEqual(len(document["paths"]), 19)
        self.assertEqual(sum(len(item) for item in document["paths"].values()), 20)

    def test_every_route_is_in_the_full_inventory(self):
        self.assertEqual(cs.check_slice(SLICE, SOURCES), [])

    def test_the_order_of_the_paths_and_methods_follows_the_source(self):
        document = cs.build_slice(SLICE)
        listed = [f"{method} {path}" for path, item in document["paths"].items() for method in item]
        self.assertEqual(listed, SLICE["head"]["path_order"])

    def test_each_operation_is_in_the_file_of_its_tag(self):
        for tag, group in SLICE["groups"].items():
            self.assertEqual(group["tag"], tag)
            for entry in group["operations"]:
                self.assertEqual(entry["operation"]["tags"][0], tag)


class SliceDriftTests(unittest.TestCase):
    def mutated(self):
        return copy.deepcopy(SLICE)

    def test_an_edited_operation_makes_the_document_out_of_date(self):
        changed = self.mutated()
        changed["groups"]["auth"]["operations"][0]["operation"]["summary"] = "something else"
        problems = cs.check_slice(changed, SOURCES)
        self.assertTrue(any("out of date" in p for p in problems), problems)

    def test_an_edited_schema_makes_the_document_out_of_date(self):
        changed = self.mutated()
        name = next(iter(changed["schemas"]))
        changed["schemas"][name]["description"] = "changed"
        self.assertTrue(any("out of date" in p for p in cs.check_slice(changed, SOURCES)))

    def test_a_route_the_inventory_does_not_have_is_reported(self):
        changed = self.mutated()
        entry = copy.deepcopy(changed["groups"]["fleet"]["operations"][0])
        entry["path"] = "/api/not-a-route"
        changed["groups"]["fleet"]["operations"].append(entry)
        changed["head"]["path_order"].append(f"{entry['method']} {entry['path']}")
        self.assertTrue(any("not in the full inventory" in p for p in cs.check_slice(changed, SOURCES)))

    def test_a_different_access_is_reported(self):
        changed = self.mutated()
        for entry in changed["groups"]["auth"]["operations"]:
            entry["operation"]["x-access"] = "nobody"
        self.assertTrue(any("has access" in p for p in cs.check_slice(changed, SOURCES)))

    def test_an_order_that_does_not_list_the_same_routes_is_refused(self):
        changed = self.mutated()
        changed["head"]["path_order"].pop()
        with self.assertRaises(cs.SourceError):
            cs.build_slice(changed)

    def test_a_route_declared_twice_is_refused(self):
        changed = self.mutated()
        changed["groups"]["safety"]["operations"].append(copy.deepcopy(changed["groups"]["safety"]["operations"][0]))
        with self.assertRaises(cs.SourceError):
            cs.slice_operations(changed)

    def test_an_operation_in_the_file_of_another_tag_is_refused(self):
        changed = self.mutated()
        changed["groups"]["claims"]["operations"][0]["operation"]["tags"] = ["safety"]
        with self.assertRaises(cs.SourceError):
            cs.slice_operations(changed)


if __name__ == "__main__":
    unittest.main()
