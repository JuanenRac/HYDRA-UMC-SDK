# =============================================================================
# HYDRA-UMC-SDK - Tests of tools/canonical/health_route.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The canonical `GET /health` of a standard library service, against a real server on a free port."""

from __future__ import annotations

import http.client
import importlib.util
import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

SOURCE = Path(__file__).resolve().parents[3] / "tools" / "canonical" / "health_route.py"
PACKAGE = "hydra_umc_example_service"
TOKEN = "s3cret-token-of-16"


def load_module(package: str = PACKAGE):
    """Load the canonical file as the module `health_route` of a package, the way a service carries its copy."""
    name = f"{package}.health_route"
    spec = importlib.util.spec_from_file_location(name, SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


HEALTH = load_module()


class Handler(HEALTH.HealthRouteMixin, BaseHTTPRequestHandler):
    token: str | None = None

    def do_GET(self) -> None:
        if self.serve_health(self.token):
            return
        HEALTH._write(self, 200, {"other": True})

    def log_message(self, *args) -> None:
        pass


class NamedHandler(Handler):
    metrics_service = "hydra-umc-named"
    metrics_version = "1.2.3"


class HealthRouteTests(unittest.TestCase):
    def serve(self, handler=Handler, token: str | None = None, health_open: bool = False, loopback: bool = True):
        attributes = {"token": token}
        server = ThreadingHTTPServer(("127.0.0.1", 0), type("H", (handler,), attributes))
        server.health_open = health_open
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(lambda: (server.shutdown(), server.server_close(), thread.join(timeout=2)))
        if not loopback:
            patch = mock.patch.object(HEALTH, "_is_loopback", lambda address: False)
            patch.start()
            self.addCleanup(patch.stop)
        return server.server_address[1]

    def get(self, port: int, path: str = "/health", token: str | None = None):
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        try:
            connection.request("GET", path, headers={"Authorization": f"Bearer {token}"} if token else {})
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_closed_by_default_answers_404_and_nothing_else(self) -> None:
        status, body = self.get(self.serve())
        self.assertEqual((status, body), (404, {"error": "not found"}))

    def test_other_paths_are_left_to_the_handler_even_when_closed(self) -> None:
        self.assertEqual(self.get(self.serve(), "/other"), (200, {"other": True}))
        self.assertEqual(self.get(self.serve(health_open=True), "/healthz"), (200, {"other": True}))

    def test_open_answers_a_loopback_caller_with_name_and_version_only(self) -> None:
        status, body = self.get(self.serve(health_open=True), "/health?x=1")
        self.assertEqual(status, 200)
        self.assertEqual(body, {"status": "ok", "service": "hydra-umc-example-service", "version": "unknown"})

    def test_the_handler_names_the_service_and_its_version(self) -> None:
        _, body = self.get(self.serve(NamedHandler, health_open=True))
        self.assertEqual((body["service"], body["version"]), ("hydra-umc-named", "1.2.3"))

    def test_outside_loopback_needs_the_token_and_without_one_is_refused(self) -> None:
        port = self.serve(token=TOKEN, health_open=True, loopback=False)
        self.assertEqual(self.get(port)[0], 401)
        self.assertEqual(self.get(port, token="wrong")[0], 401)
        status, body = self.get(port, token=TOKEN)
        self.assertEqual(status, 200)
        self.assertNotIn(TOKEN, json.dumps(body))
        self.assertEqual(self.get(self.serve(token=None, health_open=True, loopback=False), token=TOKEN)[0], 401)

    def test_closed_stays_404_outside_loopback_whatever_the_token(self) -> None:
        self.assertEqual(self.get(self.serve(token=TOKEN, loopback=False), token=TOKEN)[0], 404)

    def test_the_switch_comes_from_the_flag_or_the_environment_named_after_the_package(self) -> None:
        self.assertEqual(HEALTH.ENV_HEALTH_OPEN, "HYDRA_UMC_EXAMPLE_SERVICE_HEALTH_OPEN")
        with mock.patch.dict(os.environ, clear=False):
            os.environ.pop(HEALTH.ENV_HEALTH_OPEN, None)
            self.assertFalse(HEALTH.health_open_requested(False))
            self.assertTrue(HEALTH.health_open_requested(True))
            for value, expected in (("1", True), ("true", True), ("ON", True), ("no", False), ("", False)):
                os.environ[HEALTH.ENV_HEALTH_OPEN] = value
                self.assertEqual(HEALTH.health_open_requested(False), expected, value)

    def test_loopback_detection(self) -> None:
        for address, expected in (("127.0.0.1", True), ("::1", True), ("::1%lo", True), ("10.0.0.5", False), ("not-an-address", False)):
            self.assertEqual(HEALTH._is_loopback(address), expected, address)

    def test_another_package_gets_its_own_names(self) -> None:
        other = load_module("hydra_umc_other_node")
        self.assertEqual(other.ENV_HEALTH_OPEN, "HYDRA_UMC_OTHER_NODE_HEALTH_OPEN")


if __name__ == "__main__":
    unittest.main()
