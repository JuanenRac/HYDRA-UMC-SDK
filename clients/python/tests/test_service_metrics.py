# =============================================================================
# HYDRA-UMC-SDK - Tests of tools/canonical/service_metrics.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The canonical /metrics of a standard library HTTP service, against a real server on a free port."""

from __future__ import annotations

import importlib.util
import re
import threading
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[3] / "tools" / "canonical" / "service_metrics.py"
spec = importlib.util.spec_from_file_location("service_metrics", SOURCE)
METRICS = importlib.util.module_from_spec(spec)
spec.loader.exec_module(METRICS)

TOKEN = "s3cret-token"


def make_handler(checks: dict[str, bool] | None = None, raises: bool = False, protected: bool = False):
    class Handler(METRICS.MetricsHandlerMixin, BaseHTTPRequestHandler):
        metrics_service = "hydra-umc-example"
        metrics_version = "1.2.3"

        def log_message(self, format: str, *args: object) -> None:  # noqa: A002
            pass

        def metrics_checks(self) -> dict[str, bool]:
            if raises:
                raise RuntimeError("the registry cannot be read")
            return dict(checks or {})

        def do_GET(self) -> None:  # noqa: N802
            authorized = not protected or self.headers.get("Authorization") == f"Bearer {TOKEN}"
            if self.serve_metrics(authorized=authorized):
                return
            body = b"{}"
            self.send_response(404 if self.path != "/stats" else 200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


class Served:
    def __init__(self, handler) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self) -> "Served":
        self.thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.server.shutdown()
        self.server.server_close()

    def get(self, path: str, token: str | None = None) -> tuple[int, str, str]:
        request = urllib.request.Request(f"http://127.0.0.1:{self.server.server_address[1]}{path}")
        if token:
            request.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, response.headers.get("Content-Type", ""), response.read().decode()
        except urllib.error.HTTPError as error:
            with error:
                return error.code, error.headers.get("Content-Type", ""), error.read().decode()


def sample(text: str, name: str, **labels: str) -> float:
    for line in text.splitlines():
        match = re.fullmatch(rf"{name}(?:\{{(.*)\}})? (\S+)", line)
        if match and all(f'{k}="{v}"' in (match.group(1) or "") for k, v in labels.items()):
            return float(match.group(2))
    raise AssertionError(f"{name}{labels} not in the text")


class MetricsTests(unittest.TestCase):
    def test_the_text_is_the_prometheus_format_with_the_version_and_the_health(self) -> None:
        with Served(make_handler()) as served:
            status, kind, text = served.get("/metrics")
        self.assertEqual(status, 200)
        self.assertEqual(kind, "text/plain; version=0.0.4; charset=utf-8")
        self.assertEqual(sample(text, "hydra_umc_service_info", version="1.2.3", service="hydra-umc-example"), 1)
        self.assertEqual(sample(text, "hydra_umc_service_health", service="hydra-umc-example"), 1)
        for line in text.splitlines():
            self.assertRegex(line, r'^(# (HELP|TYPE) [a-z_]+ .+|[a-z_]+\{[a-z_]+="[^"]*"(,[a-z_]+="[^"]*")*\} [0-9]+)$')
        self.assertTrue(text.endswith("\n"))

    def test_responses_are_counted_by_the_class_of_the_status(self) -> None:
        with Served(make_handler()) as served:
            served.get("/stats")
            served.get("/stats")
            served.get("/nothing")
            _, _, text = served.get("/metrics")
        self.assertEqual(sample(text, "hydra_umc_service_http_responses_total", **{"class": "2xx"}), 2)
        self.assertEqual(sample(text, "hydra_umc_service_http_responses_total", **{"class": "4xx"}), 1)
        self.assertEqual(sample(text, "hydra_umc_service_http_responses_total", **{"class": "5xx"}), 0)

    def test_the_health_is_the_aggregate_of_the_checks(self) -> None:
        with Served(make_handler({"Registry": True, "signing key": False})) as served:
            _, _, text = served.get("/metrics")
        self.assertEqual(sample(text, "hydra_umc_service_health"), 0)
        self.assertEqual(sample(text, "hydra_umc_service_health_check", check="registry"), 1)
        self.assertEqual(sample(text, "hydra_umc_service_health_check", check="signing_key"), 0)

    def test_a_check_that_raises_is_a_failed_check_not_a_failed_answer(self) -> None:
        with Served(make_handler(raises=True)) as served:
            status, _, text = served.get("/metrics")
        self.assertEqual(status, 200)
        self.assertEqual(sample(text, "hydra_umc_service_health"), 0)
        self.assertNotIn("the registry cannot be read", text)

    def test_a_protected_service_refuses_the_numbers_without_the_token(self) -> None:
        with Served(make_handler(protected=True)) as served:
            refused = served.get("/metrics")
            allowed = served.get("/metrics", TOKEN)
        self.assertEqual(refused[0], 401)
        self.assertNotIn("hydra_umc", refused[2])
        self.assertEqual(allowed[0], 200)

    def test_nothing_a_request_carried_reaches_the_text(self) -> None:
        with Served(make_handler()) as served:
            served.get("/stats?name=very-private-name")
            served.get("/metrics?token=leaked-secret", "another-secret")
            _, _, text = served.get("/metrics")
        for needle in ("very-private-name", "leaked-secret", "another-secret", "127.0.0.1", "/stats"):
            self.assertNotIn(needle, text)

    def test_a_label_value_is_escaped(self) -> None:
        text = METRICS.ServiceMetrics('a"b\nc', "1").render()
        self.assertIn('service="a\\"b c"', text)

    def test_the_other_paths_are_left_to_the_handler(self) -> None:
        with Served(make_handler()) as served:
            self.assertEqual(served.get("/stats")[0], 200)
            self.assertEqual(served.get("/metricsx")[0], 404)


if __name__ == "__main__":
    unittest.main()
