# =============================================================================
# HYDRA-UMC-SDK - The ecosystem, liveness and stop-release routes in the OpenAPI documents
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OPENAPI = REPO / "contracts" / "openapi" / "v1"
SCHEMAS = REPO / "contracts" / "json-schema" / "v1"

NEW_ROUTES = [
    ("get", "/api/ecosystem/health"),
    ("get", "/api/robots/liveness"),
    ("post", "/api/robot/{id}/heartbeat"),
    ("post", "/api/stop-all/release"),
]
FULL_ROUTES = NEW_ROUTES + [
    ("get", "/api/connections/clients"),
    ("get", "/api/connections/events"),
    ("get", "/health"),
]


def _load(name: str) -> dict:
    return json.loads((OPENAPI / name).read_text(encoding="utf-8"))


def _closed(schema: dict) -> dict:
    schema = dict(schema)
    schema.pop("$schema", None)
    schema.pop("$id", None)
    return schema


class OpenApiEcosystemRoutesTests(unittest.TestCase):
    def test_the_typed_document_describes_the_four_routes(self):
        paths = _load("server.openapi.json")["paths"]
        for method, route in NEW_ROUTES:
            with self.subTest(route=route):
                self.assertIn(method, paths[route])
                self.assertTrue(paths[route][method]["security"], "every one of them needs a signed-in account")

    def test_the_full_document_lists_every_route_the_server_added(self):
        paths = _load("server.full.openapi.json")["paths"]
        for method, route in FULL_ROUTES:
            with self.subTest(route=route):
                self.assertIn(method, paths.get(route, {}))

    def test_the_typed_schemas_are_the_closed_json_schemas(self):
        schemas = _load("server.openapi.json")["components"]["schemas"]
        for name, file in (("EcosystemHealth", "ecosystem-health.schema.json"), ("RobotLiveness", "robot-liveness.schema.json")):
            with self.subTest(schema=name):
                closed = _closed(json.loads((SCHEMAS / file).read_text(encoding="utf-8")))
                self.assertEqual(schemas[name], closed)
                self.assertIs(schemas[name]["additionalProperties"], False)

    def test_the_release_of_the_stop_says_whether_it_was_announced(self):
        released = _load("server.openapi.json")["components"]["schemas"]["GlobalStopReleased"]
        self.assertEqual(sorted(released["required"]), ["announced", "success"])
        self.assertEqual(released["properties"]["announced"]["type"], "boolean")

    def test_every_new_route_answers_with_a_schema_that_exists(self):
        document = _load("server.openapi.json")
        for method, route in NEW_ROUTES:
            for code, response in document["paths"][route][method]["responses"].items():
                reference = response["content"]["application/json"]["schema"]["$ref"].rsplit("/", 1)[-1]
                with self.subTest(route=route, code=code):
                    self.assertIn(reference, document["components"]["schemas"])

    def test_the_full_copy_carries_the_schemas_of_the_new_answers(self):
        schemas = _load("server.full.openapi.json")["components"]["schemas"]
        for name in ("EcosystemHealth", "RobotLiveness", "GlobalStopReleased", "ConnectionClientList", "ConnectionEventList", "HealthReport"):
            with self.subTest(schema=name):
                self.assertIn(name, schemas)

    def test_the_typed_document_and_the_full_copy_agree_on_the_access_of_each_route(self):
        typed = _load("server.openapi.json")["paths"]
        full = _load("server.full.openapi.json")["paths"]
        for method, route in NEW_ROUTES:
            with self.subTest(route=route):
                self.assertEqual(bool(typed[route][method].get("security")), full[route][method].get("x-access") != "public")


if __name__ == "__main__":
    unittest.main()
