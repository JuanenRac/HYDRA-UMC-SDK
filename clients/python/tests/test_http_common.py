# =============================================================================
# HYDRA-UMC-SDK - Tests of tools/canonical/http_common.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The canonical HTTP helpers of a standard library service, against a real server on a free port."""

from __future__ import annotations

import http.client
import importlib.util
import json
import socket
import threading
import unittest
from http.server import BaseHTTPRequestHandler
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[3] / "tools" / "canonical" / "http_common.py"
spec = importlib.util.spec_from_file_location("http_common", SOURCE)
COMMON = importlib.util.module_from_spec(spec)
spec.loader.exec_module(COMMON)

TOKEN = "s3cret-token-of-16"


def make_handler(limit: int = 1024, gate: threading.Event | None = None, entered: threading.Event | None = None):
    class Handler(BaseHTTPRequestHandler):
        timeout = COMMON.SOCKET_TIMEOUT_SECONDS

        def log_message(self, format: str, *args: object) -> None:  # noqa: A002
            pass

        def do_GET(self) -> None:  # noqa: N802
            if self.path.startswith("/slow"):
                if entered is not None:
                    entered.set()
                if gate is not None:
                    gate.wait(5)
                COMMON.write_json(self, 200, {"slow": True})
                return
            if self.path.startswith("/secret") and not COMMON.bearer_matches(self, TOKEN):
                COMMON.reject_unauthorized(self)
                return
            try:
                first = self.path.startswith("/first")
                params = COMMON.query_params(self, "first" if first else "error")
            except ValueError as error:
                COMMON.write_error(self, 400, str(error))
                return
            COMMON.write_json(self, 200, {"params": params})

        def do_POST(self) -> None:  # noqa: N802
            try:
                body = COMMON.read_json_object(self, limit) if self.path == "/object" else COMMON.read_json_body(self, limit)
            except ValueError as error:
                COMMON.write_error(self, 400, str(error))
                return
            COMMON.write_json(self, 200, {"body": body}, default=str)

    return Handler


class Served:
    def __init__(self, handler, max_threads: int | None = None) -> None:
        self.server = (
            COMMON.BoundedThreadingHTTPServer(("127.0.0.1", 0), handler, max_threads)
            if max_threads is not None
            else COMMON.BoundedThreadingHTTPServer(("127.0.0.1", 0), handler)
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]

    def request(self, method: str, path: str, body: bytes | None = None, headers: dict[str, str] | None = None) -> tuple[int, dict]:
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        data = response.read()
        connection.close()
        return response.status, json.loads(data) if data else {}

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class HttpCommonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.served = Served(make_handler())
        self.addCleanup(self.served.close)

    def test_a_json_body_comes_back_as_it_was_sent(self) -> None:
        status, answer = self.served.request("POST", "/object", b'{"a": [1, 2.5, "x"], "b": null}')
        self.assertEqual((status, answer["body"]), (200, {"a": [1, 2.5, "x"], "b": None}))

    def test_an_absent_body_is_an_empty_object(self) -> None:
        self.assertEqual(self.served.request("POST", "/object")[1]["body"], {})
        self.assertEqual(self.served.request("POST", "/any")[1]["body"], {})

    def test_what_is_not_json_or_not_an_object_is_a_400(self) -> None:
        for body in (b"not json", b"\xff\xfe", b"[1, 2]", b'"text"', b"5", b"null"):
            status, answer = self.served.request("POST", "/object", body)
            self.assertEqual(status, 400, body)
            self.assertIn("error", answer)
        self.assertEqual(self.served.request("POST", "/any", b"[1, 2]")[0], 200)  # read_json_body takes any JSON value

    def test_nan_and_infinity_are_not_numbers(self) -> None:
        for body in (b'{"a": NaN}', b'{"a": Infinity}', b'{"a": -Infinity}'):
            status, answer = self.served.request("POST", "/object", body)
            self.assertEqual(status, 400)
            self.assertIn("not a valid JSON number", answer["error"])

    def test_a_body_over_the_limit_is_refused_after_it_was_read_and_thrown_away(self) -> None:
        status, answer = self.served.request("POST", "/object", b'{"x": "' + b"a" * 5000 + b'"}')
        self.assertEqual(status, 400)
        self.assertIn("0-1024 bytes", answer["error"])

    def test_a_content_length_that_is_not_a_number_or_negative_is_refused(self) -> None:
        for value in ("abc", "-5"):
            with socket.create_connection(("127.0.0.1", self.served.port), timeout=5) as sock:
                sock.sendall(f"POST /object HTTP/1.1\r\nHost: x\r\nContent-Length: {value}\r\nConnection: close\r\n\r\n".encode())
                reply = sock.recv(4096)
            self.assertTrue(reply.startswith(b"HTTP/1.0 400") or reply.startswith(b"HTTP/1.1 400"), reply[:40])

    def test_the_query_string_refuses_a_repeated_name_or_takes_the_first(self) -> None:
        self.assertEqual(self.served.request("GET", "/q?a=1&b=")[1]["params"], {"a": "1", "b": ""})
        status, answer = self.served.request("GET", "/q?a=1&a=2")
        self.assertEqual(status, 400)
        self.assertIn("exactly once", answer["error"])
        self.assertEqual(self.served.request("GET", "/first?a=1&a=2")[1]["params"], {"a": "1"})

    def test_the_bearer_token_is_compared_exactly(self) -> None:
        self.assertEqual(self.served.request("GET", "/secret")[0], 401)
        self.assertEqual(self.served.request("GET", "/secret", headers={"Authorization": "Bearer wrong"})[0], 401)
        self.assertEqual(self.served.request("GET", "/secret", headers={"Authorization": f"Basic {TOKEN}"})[0], 401)
        self.assertEqual(self.served.request("GET", "/secret", headers={"Authorization": f"Bearer {TOKEN}"})[0], 200)

    def test_an_empty_token_means_no_token(self) -> None:
        class Fake:
            headers: dict[str, str] = {}

        self.assertTrue(COMMON.bearer_matches(Fake(), ""))  # type: ignore[arg-type]
        self.assertFalse(COMMON.bearer_matches(Fake(), TOKEN))  # type: ignore[arg-type]

    def test_write_json_uses_the_default_for_what_json_cannot_write(self) -> None:
        status, answer = self.served.request("POST", "/any", b'{"a": 1}')
        self.assertEqual(status, 200)
        self.assertEqual(answer["body"], {"a": 1})

    def test_the_limit_of_threads_must_be_a_sensible_number(self) -> None:
        for bad in (0, -1, 1025, True, "4", 2.5):
            with self.assertRaises(ValueError):
                COMMON.BoundedThreadingHTTPServer(("127.0.0.1", 0), make_handler(), bad)  # type: ignore[arg-type]


class BoundedServerTests(unittest.TestCase):
    def test_a_request_beyond_the_limit_gets_503_at_once_and_the_slot_is_given_back(self) -> None:
        gate, entered = threading.Event(), threading.Event()
        served = Served(make_handler(gate=gate, entered=entered), max_threads=1)
        self.addCleanup(served.close)
        holder = threading.Thread(target=lambda: served.request("GET", "/slow"), daemon=True)
        holder.start()
        self.assertTrue(entered.wait(5))
        with socket.create_connection(("127.0.0.1", served.port), timeout=5) as sock:
            sock.sendall(b"GET /q HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n")
            reply = sock.recv(4096)
        self.assertTrue(reply.startswith(b"HTTP/1.1 503"), reply[:40])
        self.assertIn(b"Retry-After: 1", reply)
        self.assertEqual(served.server.refused, 1)
        gate.set()
        holder.join(timeout=5)
        status = 0
        for _ in range(100):
            status, _answer = served.request("GET", "/q")
            if status == 200:
                break
            threading.Event().wait(0.02)
        self.assertEqual(status, 200)


if __name__ == "__main__":
    unittest.main()
