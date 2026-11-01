# =============================================================================
# HYDRA-UMC-SDK - Tests of the inventory sources of the server routes
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The whole inventory of the server routes is declared in the sources of the SDK: the full document is generated from them, nothing is lost in the move, and
every kind of drift between the sources, the shapes, the generated document and the server is caught by the check."""
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

SOURCES = cs.load_sources()
SHAPES = cs.load_shapes()
UNION = cs.build_union(SOURCES, SHAPES)
FULL = json.loads(cs.UNION_OUTPUT.read_text(encoding="utf-8"))
METHODS = ("get", "post", "put", "patch", "delete")


def routes_of(document: dict) -> set[tuple[str, str]]:
    return {(method, path) for path, item in document["paths"].items() for method in item if method in METHODS}


class TheUnionIsTheFullDocument(unittest.TestCase):
    def test_the_file_is_exactly_what_the_sources_and_the_shapes_generate(self):
        self.assertEqual(cs.check_union(SOURCES, SHAPES), [])
        self.assertEqual(cs.render(UNION), cs.UNION_OUTPUT.read_text(encoding="utf-8").replace("\r\n", "\n"))

    def test_every_route_of_the_server_is_declared_once(self):
        self.assertEqual(cs.duplicate_routes(SOURCES), [])
        declared = [(r["method"], r["path"]) for source in SOURCES.values() for r in source["routes"]]
        self.assertEqual(len(declared), len(set(declared)))
        self.assertEqual(set(declared), routes_of(FULL))
        self.assertGreaterEqual(len(declared), 76)

    def test_the_groups_are_the_tags_of_the_document(self):
        for name, source in SOURCES.items():
            self.assertEqual(name, source["group"])
            tags = {FULL["paths"][r["path"]][r["method"]]["tags"][0] for r in source["routes"]}
            self.assertEqual(tags, {name})

    def test_the_paths_are_in_alphabetical_order_and_the_methods_too(self):
        self.assertEqual(list(FULL["paths"]), sorted(FULL["paths"]))
        for item in FULL["paths"].values():
            self.assertEqual(list(item), sorted(item))

    def test_a_public_route_has_no_security_and_every_other_one_asks_for_the_token(self):
        for path, item in FULL["paths"].items():
            for method, operation in item.items():
                if operation["x-access"] == "public":
                    self.assertNotIn("security", operation, f"{method} {path}")
                else:
                    self.assertEqual(operation["security"], [{"bearerAuth": []}], f"{method} {path}")

    def test_every_shape_an_answer_names_is_declared_and_no_shape_is_left_over_by_accident(self):
        used = set()
        for item in FULL["paths"].values():
            for operation in item.values():
                for response in operation["responses"].values():
                    for content in response.get("content", {}).values():
                        used.add(content["schema"]["$ref"].rsplit("/", 1)[1])
        declared = set(SHAPES["shapes"])
        self.assertEqual(used - declared, set(), "an answer names a shape the SDK does not declare")
        # the shapes no response names directly are reached through another shape (the lists of connections) or are used by the clients of the typed slice; they are
        # listed, so a new one that nothing uses has to be a decision
        self.assertLessEqual(declared - used, {"ConnectionClient", "ConnectionEvent", "VoiceReply", "WatchStatus"})

    def test_a_new_route_is_not_taken_for_a_route_of_another_group(self):
        mutated = copy.deepcopy(SOURCES)
        mutated["audit"]["routes"].append(copy.deepcopy(mutated["claims"]["routes"][0]))
        self.assertTrue(cs.duplicate_routes(mutated))


class WhatTheMoveKept(unittest.TestCase):
    """The move from the hand-refreshed document to the sources lost nothing: the only operations that changed are the two the pilot source describes better."""

    def test_the_operations_that_are_not_the_pilot_are_those_of_the_inventory_of_the_server(self):
        for path, item in FULL["paths"].items():
            for method, operation in item.items():
                if operation["tags"] == ["connections"]:
                    continue
                self.assertIn("summary", operation)
                self.assertIn("description", operation)
                self.assertIn("x-access", operation)
                self.assertTrue(operation["responses"], f"{method} {path}")

    def test_the_two_connection_routes_carry_their_typed_query_parameters_now(self):
        events = FULL["paths"]["/api/connections/events"]["get"]
        names = {p["name"]: p["schema"] for p in events["parameters"]}
        self.assertEqual(set(names), {"kind", "action", "user", "before", "limit"})
        self.assertEqual(names["before"]["pattern"], "^\\d{1,9}$")

    def test_the_info_the_security_scheme_and_the_shapes_come_from_the_shapes_file(self):
        self.assertEqual(FULL["info"], SHAPES["document"])
        self.assertEqual(FULL["components"]["securitySchemes"], SHAPES["security_schemes"])
        self.assertEqual(FULL["components"]["schemas"], SHAPES["shapes"])


def server_view(document: dict) -> dict:
    """What the inventory the server generates from its own code looks like: the same document."""
    return copy.deepcopy(document)


class TheCheckCatchesDrift(unittest.TestCase):
    def test_a_server_that_matches_has_no_difference(self):
        server = server_view(FULL)
        self.assertEqual(cs.compare_shapes(SHAPES, server), [])
        for name, source in SOURCES.items():
            self.assertEqual(cs.compare_with_server_document(source, server), [], name)

    def test_a_route_the_server_added_and_no_source_declares_is_found(self):
        server = server_view(FULL)
        server["paths"]["/api/new"] = {"get": {"tags": ["new"], "x-access": "user", "responses": {"200": {"description": "ok"}}, "security": [{"bearerAuth": []}]}}
        offered = routes_of(server)
        declared = {(r["method"], r["path"]) for source in SOURCES.values() for r in source["routes"]}
        self.assertEqual(offered - declared, {("get", "/api/new")})

    def test_a_route_a_source_declares_and_the_server_dropped_is_found(self):
        server = server_view(FULL)
        del server["paths"]["/api/users"]["post"]
        problems = cs.compare_with_server_document(SOURCES["users"], server)
        self.assertTrue(any("POST /api/users" in p and "does not register" in p for p in problems))

    def test_another_access_another_status_code_and_another_query_parameter_are_found(self):
        server = server_view(FULL)
        users = server["paths"]["/api/users"]["get"]
        users["security"] = []
        users["responses"]["418"] = {"description": "teapot"}
        server["paths"]["/api/telemetry/query"]["get"].setdefault("parameters", []).append({"name": "extra", "in": "query", "required": False, "schema": {"type": "string"}})
        problems = cs.compare_with_server_document(SOURCES["users"], server) + cs.compare_with_server_document(SOURCES["telemetry"], server)
        text = "\n".join(problems)
        self.assertIn("access differs", text)
        self.assertIn("status 418", text)
        self.assertIn("'extra'", text)

    def test_a_shape_that_differs_missing_or_extra_is_found(self):
        server = server_view(FULL)
        server["components"]["schemas"]["Success"]["required"] = []
        del server["components"]["schemas"]["Passthrough"]
        server["components"]["schemas"]["Invented"] = {"type": "object"}
        text = "\n".join(cs.compare_shapes(SHAPES, server))
        self.assertIn("shape Success: the server copy differs", text)
        self.assertIn("shape Passthrough: the SDK declares it", text)
        self.assertIn("shape Invented: the server inventory carries it", text)

    def test_a_document_edited_by_hand_is_found(self):
        edited = copy.deepcopy(UNION)
        edited["paths"]["/api/users"]["get"]["summary"] = "edited"
        self.assertNotEqual(cs.render(edited), cs.render(UNION))
        saved = cs.UNION_OUTPUT
        try:
            import tempfile

            with tempfile.TemporaryDirectory() as folder:
                cs.UNION_OUTPUT = Path(folder) / "server.full.openapi.json"
                cs.UNION_OUTPUT.write_text(cs.render(edited), encoding="utf-8")
                self.assertTrue(cs.check_union(SOURCES, SHAPES))
                cs.UNION_OUTPUT.write_text(cs.render(UNION), encoding="utf-8")
                self.assertEqual(cs.check_union(SOURCES, SHAPES), [])
        finally:
            cs.UNION_OUTPUT = saved

    def test_a_source_changed_without_regenerating_the_document_is_found(self):
        mutated = copy.deepcopy(SOURCES)
        mutated["users"]["routes"][0]["description"] = "changed in the source only"
        self.assertTrue(cs.check_union(mutated, SHAPES))

    def test_the_inventory_is_not_scanned_against_the_clients(self):
        self.assertEqual(cs.scan_consumer(SOURCES["users"], ROOT.parent / "HYDRA-UMC-STUDIO"), [])

    def test_the_query_names_of_a_route_are_the_parameters_in_the_query(self):
        route = next(r for r in SOURCES["telemetry"]["routes"] if r["path"] == "/api/telemetry/query")
        self.assertEqual(cs.query_names(route), {p["name"] for p in route.get("parameters", []) if p["in"] == "query"})
        self.assertEqual(cs.query_names({"query": [{"name": "a"}]}), {"a"})
        self.assertEqual(cs.query_names({}), set())


if __name__ == "__main__":
    unittest.main()
