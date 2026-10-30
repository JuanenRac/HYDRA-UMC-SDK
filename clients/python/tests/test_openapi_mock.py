# =============================================================================
# HYDRA-UMC-SDK - Tests of the OpenAPI-derived mock routes
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

import json
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from hydra_umc_sdk.mock_server import create_server
from hydra_umc_sdk.openapi_mock import OpenApiRouter, conforms, synthesize

OPENAPI_DIR = Path(__file__).resolve().parents[3] / "contracts" / "openapi" / "v1"
DOCUMENTS = sorted(OPENAPI_DIR.glob("*.openapi.json"))


class SynthesisTests(unittest.TestCase):
    def test_every_success_body_of_every_document_conforms_to_its_schema(self) -> None:
        self.assertTrue(DOCUMENTS)
        for path in DOCUMENTS:
            router = OpenApiRouter.from_file(path)
            for method, template, operation in router.operations():
                for status, response in operation.get("responses", {}).items():
                    schema = response.get("content", {}).get("application/json", {}).get("schema")
                    if schema is None:
                        continue
                    body = synthesize(schema, router.doc)
                    self.assertIsNone(conforms(body, schema, router.doc), f"{path.name} {method} {template} {status}")

    def test_example_enum_and_required_are_used(self) -> None:
        doc = {"components": {}}
        self.assertEqual(synthesize({"type": "string", "enum": ["b", "a"]}, doc), "b")
        self.assertEqual(synthesize({"type": "integer", "example": 7}, doc), 7)
        self.assertEqual(
            synthesize({"type": "object", "required": ["n"], "properties": {"n": {"type": "integer"}, "x": {"type": "string"}}}, doc),
            {"n": 0},
        )

    def test_conforms_reports_a_missing_property_and_a_wrong_type(self) -> None:
        doc = {"components": {}}
        schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "integer"}}}
        self.assertIn("missing", conforms({}, schema, doc))
        self.assertIn("integer", conforms({"a": "x"}, schema, doc))
        self.assertIsNone(conforms({"a": 1}, schema, doc))


class OpenApiServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = OPENAPI_DIR / "server.openapi.json"
        self.router = OpenApiRouter.from_file(self.document)
        self.server = create_server(port=0, openapi=self.router)
        self.base = "http://{}:{}".format(*self.server.server_address)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=5)
        self.server.server_close()

    def call(self, method: str, path: str, token: bool = True) -> tuple[int, dict, object]:
        request = urllib.request.Request(self.base + path, method=method, data=b"{}" if method != "GET" else None)
        request.add_header("Content-Type", "application/json")
        if token:
            request.add_header("Authorization", "Bearer mock")
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, dict(response.headers), json.loads(response.read() or b"{}")
        except urllib.error.HTTPError as error:
            with error:
                return error.code, dict(error.headers), json.loads(error.read() or b"{}")

    def test_every_operation_of_the_document_is_served_with_its_success_status(self) -> None:
        for method, template, operation in self.router.operations():
            path = template.replace("{id}", "1")
            status, _, body = self.call(method, path)
            declared = [int(s) for s in operation["responses"] if s.startswith("2")]
            self.assertIn(status, declared, f"{method} {template}")
            schema = operation["responses"][str(status)].get("content", {}).get("application/json", {}).get("schema")
            if schema is not None:
                self.assertIsNone(conforms(body, schema, self.router.doc), f"{method} {template}")

    def test_a_protected_operation_without_a_token_answers_401(self) -> None:
        status, _, body = self.call("GET", "/api/claims", token=False)
        self.assertEqual(status, 401)
        self.assertIn("error", body)

    def test_the_login_operation_needs_no_token(self) -> None:
        status, _, _ = self.call("POST", "/api/login", token=False)
        self.assertEqual(status, 200)

    def test_a_method_the_path_does_not_declare_answers_405_with_allow(self) -> None:
        status, headers, _ = self.call("DELETE", "/api/claims")
        self.assertEqual(status, 405)
        self.assertEqual(headers["Allow"], "GET")

    def test_an_unknown_path_answers_404_and_the_contract_examples_still_work(self) -> None:
        self.assertEqual(self.call("GET", "/api/nope")[0], 404)
        self.assertEqual(self.call("GET", "/mock/")[0], 200)

    def test_the_robot_answer_carries_an_etag(self) -> None:
        _, headers, _ = self.call("GET", "/api/robot/1")
        self.assertEqual(headers.get("ETag"), '"1"')


if __name__ == "__main__":
    unittest.main()
