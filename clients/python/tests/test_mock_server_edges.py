# =============================================================================
# HYDRA-UMC-SDK - Mock server edge tests with a small OpenAPI document
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The mock server on a document of its own: the routes it answers, a method the path does not have (405 with Allow), a path the document does not have,
a request body that is read and ignored, the 401 of a protected operation, the entity tag, the contract list and its 404s, and the command line."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

from hydra_umc_sdk import mock_server
from hydra_umc_sdk.openapi_mock import OpenApiRouter

DOCUMENT = {
    "openapi": "3.0.3",
    "info": {"title": "tiny", "version": "1"},
    "security": [{"bearer": []}],
    "paths": {
        "/api/open": {
            "get": {"security": [], "responses": {"200": {"description": "ok", "content": {"application/json": {"schema": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}}}}}},
        },
        "/api/items/{id}": {
            "get": {
                "responses": {
                    "200": {"description": "ok", "headers": {"ETag": {"schema": {"type": "string"}}, "X-Other": {"schema": {"type": "string"}}},
                            "content": {"application/json": {"schema": {"type": "object", "required": ["id"], "properties": {"id": {"type": "integer"}}}}}},
                    "401": {"description": "no", "content": {"application/json": {"schema": {"type": "object", "required": ["error"], "properties": {"error": {"type": "string"}}}}}},
                },
            },
            "put": {"responses": {"204": {"description": "saved"}, "401": {"description": "no"}}},
            "delete": {"security": [], "responses": {"default": {"description": "whatever"}}},
        },
    },
}


class OpenApiRoutesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.folder = tempfile.TemporaryDirectory()
        path = Path(cls.folder.name) / "tiny.openapi.json"
        path.write_text(json.dumps(DOCUMENT), encoding="utf-8")
        cls.server = mock_server.create_server(port=0, openapi=str(path))  # the path of the document, not a router
        cls.base = "http://{}:{}".format(*cls.server.server_address)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()
        cls.folder.cleanup()

    def call(self, method: str, path: str, body: bytes | None = None, headers: dict[str, str] | None = None):
        request = urllib.request.Request(self.base + path, data=body, method=method, headers=headers or {})
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, dict(response.headers), response.read()
        except urllib.error.HTTPError as error:
            with error:
                return error.code, dict(error.headers), error.read()

    def test_an_operation_without_security_answers_its_success_example(self) -> None:
        status, headers, body = self.call("GET", "/api/open")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(int(headers["Content-Length"]), len(body))
        self.assertIn("name", json.loads(body))

    def test_a_protected_operation_wants_a_bearer_and_answers_401_with_the_example_of_the_document(self) -> None:
        status, _, body = self.call("GET", "/api/items/7")
        self.assertEqual(status, 401)
        self.assertIn("error", json.loads(body))
        for bad in ("Basic abc", "Bearer", "token abc", ""):
            self.assertEqual(self.call("GET", "/api/items/7", headers={"Authorization": bad} if bad else {})[0], 401, bad)

    def test_with_a_bearer_it_answers_200_with_the_entity_tag_and_only_that_header(self) -> None:
        status, headers, body = self.call("GET", "/api/items/7?verbose=1", headers={"Authorization": "bearer abc"})
        self.assertEqual(status, 200)
        self.assertEqual(headers["ETag"], '"1"')
        self.assertNotIn("X-Other", headers)
        self.assertIn("id", json.loads(body))

    def test_a_method_the_path_does_not_have_is_405_with_the_allowed_ones(self) -> None:
        status, headers, body = self.call("PATCH", "/api/items/7", body=b"{}")
        self.assertEqual(status, 405)
        self.assertEqual(headers["Allow"], "DELETE, GET, PUT")
        self.assertEqual(json.loads(body), {"error": "method not allowed", "allowed": ["DELETE", "GET", "PUT"]})
        self.assertEqual(self.call("POST", "/api/open", body=b"x")[0], 405)

    def test_a_path_the_document_does_not_have_is_404_for_every_method(self) -> None:
        for method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
            body = None if method == "GET" else b'{"a":1}'
            status, _, answer = self.call(method, "/api/nowhere", body=body)
            self.assertEqual(status, 404, method)
            self.assertIn("error", json.loads(answer))

    def test_a_request_body_is_read_and_ignored_and_the_success_status_comes_from_the_document(self) -> None:
        status, _, body = self.call("PUT", "/api/items/3", body=b'{"big": "' + b"x" * 5000 + b'"}', headers={"Authorization": "Bearer t", "Content-Type": "application/json"})
        self.assertIn(status, (200, 204))
        self.assertEqual(self.call("GET", "/api/open")[0], 200, "the server still answers after a body of that size")

    def test_an_operation_with_only_a_default_response_answers_200_with_an_empty_object(self) -> None:
        status, _, body = self.call("DELETE", "/api/items/3")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {})

    def test_the_mock_paths_still_win_over_the_document(self) -> None:
        status, _, body = self.call("GET", "/mock/")
        self.assertEqual(status, 200)
        self.assertIn("ProjectManifest", json.loads(body)["contracts"])
        self.assertEqual(self.call("GET", "/mock/NoSuchContract")[0], 404)
        self.assertEqual(self.call("POST", "/mock/ProjectManifest", body=b"{}")[0], 404, "the contract examples are read-only")

    def test_a_contract_example_is_served_with_its_own_content(self) -> None:
        status, _, body = self.call("GET", "/mock/ProjectManifest")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), mock_server.EXAMPLE_PAYLOADS["ProjectManifest"])


class PlainServerTests(unittest.TestCase):
    def test_without_a_document_every_other_path_is_404_and_points_to_the_list(self) -> None:
        server = mock_server.create_server(port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = "http://{}:{}".format(*server.server_address)
            for method, path in (("GET", "/"), ("GET", "/api/anything"), ("POST", "/mock/"), ("DELETE", "/x")):
                request = urllib.request.Request(base + path, data=b"{}" if method != "GET" else None, method=method)
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    urllib.request.urlopen(request, timeout=5)
                self.assertEqual(raised.exception.code, 404, f"{method} {path}")
                text = raised.exception.read().decode()
                raised.exception.close()
                if method == "GET":
                    self.assertIn("GET /mock/", text)
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()

    def test_a_router_object_is_used_as_it_is(self) -> None:
        router = OpenApiRouter(DOCUMENT)
        server = mock_server.create_server(port=0, openapi=router)
        try:
            self.assertIs(server.RequestHandlerClass.router, router)
        finally:
            server.server_close()

    def test_no_document_means_no_router(self) -> None:
        server = mock_server.create_server(port=0)
        try:
            self.assertIsNone(server.RequestHandlerClass.router)
        finally:
            server.server_close()


class CommandLineTests(unittest.TestCase):
    def test_main_serves_until_interrupted_prints_where_and_closes_the_socket(self) -> None:
        fake = mock.Mock()
        fake.server_address = ("127.0.0.1", 4321)
        fake.serve_forever.side_effect = KeyboardInterrupt
        out = io.StringIO()
        with mock.patch.object(mock_server, "create_server", return_value=fake) as created, contextlib.redirect_stdout(out):
            self.assertEqual(mock_server.main(["--port", "4321"]), 0)
        created.assert_called_once_with("127.0.0.1", 4321, None)
        fake.server_close.assert_called_once()
        self.assertIn("http://127.0.0.1:4321/mock/", out.getvalue())
        self.assertIn(f"{len(mock_server.EXAMPLE_PAYLOADS)} contracts", out.getvalue())

    def test_main_passes_the_host_and_the_document_and_closes_even_when_serving_fails(self) -> None:
        fake = mock.Mock()
        fake.server_address = ("0.0.0.0", 1)
        fake.serve_forever.side_effect = RuntimeError("boom")
        with mock.patch.object(mock_server, "create_server", return_value=fake) as created, contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(RuntimeError):
                mock_server.main(["--host", "0.0.0.0", "--openapi", "doc.json"])
        created.assert_called_once_with("0.0.0.0", 8790, "doc.json")
        fake.server_close.assert_called_once()

    def test_a_port_that_is_not_a_number_is_a_usage_error(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            mock_server.main(["--port", "many"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
