# =============================================================================
# HYDRA-UMC-SDK - Dependency-free mock server for contract testing
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

"""A real, dependency-free HTTP server that serves example v1 contract
payloads - built so a UI, adapter or integration test can be written and
exercised against a real HTTP endpoint before any real CM5/robot/MCU
hardware exists to talk to.

Every payload this server can return is one of the module-level
EXAMPLE_PAYLOADS below, and every one of those is proven, by this module's
own tests, to pass `validation.validate()` for its declared contract - the
mock can never silently drift from what the real SDK considers valid,
because both are checked against the exact same validator.

This is not a fake robot, a fake MCU or a simulation of real device
behavior: it never claims a machine is READY, never accepts a write, and
every route is a plain GET returning a static example. Ports, timing,
concurrency, and multi-request state are all real HTTP hardware would
differ on - this only proves "does my client code parse a real,
schema-valid response correctly," nothing about actual device behavior.
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .validation import REQUIRED, validate

# One real, minimal, schema-valid example per contract this SDK's own
# validator knows about. Field values are deliberately generic/obviously
# synthetic (node_id "mock-node-01", etc.) so nothing here is mistaken for
# a real deployment's own data if it ever leaks into a log or screenshot.
EXAMPLE_PAYLOADS: dict[str, dict[str, Any]] = {
    "DeviceDescriptor": {
        "schema_version": "1.0",
        "node_id": "mock-node-01",
        "profile": "base",
        "hostname": "mock-cm5-01",
        "machine": "aarch64",
        "operating_system": "Linux",
        "kernel": "6.6",
        "interfaces": ["eth0"],
    },
    "HealthReport": {
        "schema_version": "1.0",
        "state": "READY",
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "checks": {"storage": {"state": "PASS"}},
    },
    "SafetyState": {
        "schema_version": "1.0",
        "state": "READY",
        "source": "mock-server",
        "timestamp_utc": "2026-01-01T00:00:00Z",
    },
    "UpdateManifest": {
        "schema_version": "1.0",
        "project": "HYDRA-UMC-MOCK",
        "version": "0.0.1",
        "artifact_url": "https://example.invalid/mock.tar.gz",
        "sha256": "0" * 64,
    },
    "EventEnvelope": {
        "schema_version": "1.0",
        "event_id": "mock-evt-001",
        "type": "health.reported",
        "source": "mock-server",
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "sequence": 0,
    },
    "ServerDiscovery": {
        "schema_version": "1.0",
        "product": "HYDRA-UMC MOCK",
        "remoteApiVersion": 2,
        "appVersion": "0.0.1",
        "hostname": "mock-server",
        "controllerCount": 0,
        "robotCount": 0,
        "uptimeSeconds": 0,
    },
    "ProjectManifest": {
        "schema_version": "1.0",
        "ecosystem": "HYDRA-UMC",
        "name": "HYDRA-UMC-MOCK",
        "version": "0.0.1",
        "role": "service",
        "stack": "python",
        "technologies": ["Python"],
        "deployment_target": "user-pc",
        "maturity": "scaffolding",
        "family": "Mock",
        "parent": None,
        "native_version": {"file": "CHANGELOG.md", "pattern": "(\\d+)\\.(\\d+)\\.(\\d+)"},
        "build": "",
        "notes": "",
    },
}

# Fails loudly at import time (not silently at first request) if a new
# contract is ever added to validation.py without a matching example here,
# or vice versa - this module's own README claim ("one real example per
# known contract") stays true by construction, not by convention.
_missing_examples = sorted(set(REQUIRED) - set(EXAMPLE_PAYLOADS))
if _missing_examples:
    raise RuntimeError(f"mock_server.py: no EXAMPLE_PAYLOADS entry for: {', '.join(_missing_examples)}")
_unknown_examples = sorted(set(EXAMPLE_PAYLOADS) - set(REQUIRED))
if _unknown_examples:
    raise RuntimeError(f"mock_server.py: EXAMPLE_PAYLOADS has no matching contract for: {', '.join(_unknown_examples)}")


class MockContractHandler(BaseHTTPRequestHandler):
    # Quiet by default - a test suite spinning this server up per-test
    # doesn't need BaseHTTPRequestHandler's own request-log line on stderr
    # for every GET.
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - stdlib signature
        pass

    def _write_json(self, status: int, body: dict[str, Any]) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802 - stdlib method name
        if self.path == "/mock/":
            self._write_json(200, {"contracts": sorted(EXAMPLE_PAYLOADS)})
            return
        if self.path.startswith("/mock/"):
            contract = self.path[len("/mock/"):]
            example = EXAMPLE_PAYLOADS.get(contract)
            if example is None:
                self._write_json(404, {"error": f"unknown contract: {contract}"})
                return
            self._write_json(200, example)
            return
        self._write_json(404, {"error": "not found - see GET /mock/ for the contract list"})


def create_server(host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    """Real HTTP server, not started - `.server_address` reports the actual
    bound port once serving (useful with port=0 for an ephemeral port in
    tests)."""
    return ThreadingHTTPServer((host, port), MockContractHandler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Serve example v1 HYDRA-UMC SDK contract payloads over real HTTP for client testing."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8790)
    args = parser.parse_args(argv)

    server = create_server(args.host, args.port)
    host, port = server.server_address
    print(f"hydra-umc-sdk-mock-server: serving {len(EXAMPLE_PAYLOADS)} contracts on http://{host}:{port}/mock/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
