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
behavior: it never claims a machine is READY, never stores a write, and
every answer is a static example (the /mock/ routes are plain GETs; with an
OpenAPI document the paths of that document answer too, see openapi_mock). Ports, timing,
concurrency, and multi-request state are all real HTTP hardware would
differ on - this only proves "does my client code parse a real,
schema-valid response correctly," nothing about actual device behavior.
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .openapi_mock import OpenApiRouter
from .validation import REQUIRED

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
        "state": "INHIBITED",
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "checks": {"storage": {"state": "PASS"}},
    },
    "ScenarioOutcome": {
        "schema_version": "1.0",
        "scenario_id": "mock/scenario/example",
        "run_id": "mock-run-01",
        "base_fingerprint": "mock-base-00",
        "phase": "after",
        "repro_case": "mock-repro-case",
        "observed": {"outcome": "not-reproduced", "exit_code": 0, "evidence": "mock example"},
        "timestamp_utc": "2026-01-01T00:00:00Z",
    },
    "SafetyState": {
        "schema_version": "1.0",
        "state": "INHIBITED",
        "source": "mock-server",
        "timestamp_utc": "2026-01-01T00:00:00Z",
    },
    "Operation": {
        "schema_version": "1.0",
        "operation_id": "mock-op-01",
        "correlation_id": "mock-mission-01",
        "kind": "move_to_pose",
        "target": {"kind": "robot", "id": "mock-controller:mock-robot"},
        "status": "queued",
        "requested_at_utc": "2026-01-01T00:00:00Z",
        "updated_at_utc": "2026-01-01T00:00:00Z",
        "params": {},
    },
    "Capability": {
        "schema_version": "1.0",
        "target": {"kind": "robot", "id": "mock-controller:mock-robot"},
        "kind": "move_to_pose",
        "declared": True,
        "last_checked_at_utc": "2026-01-01T00:00:00Z",
        "checked_configuration": "mock-config-01",
        "max_age_seconds": 3600,
        "last_check_outcome": "verified",
    },
    "Pose": {
        "schema_version": "1.0",
        "frame": "base",
        "position": {"x": 0.25, "y": 0.0, "z": 0.3},
        "orientation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
    },
    "CommandLifecycleEvent": {
        "schema_version": "1.0",
        "operation_id": "op-0001",
        "robot_id": "3",
        "command": "move",
        "state": "RUNNING",
        "at_utc": "2026-01-01T10:00:00Z",
        "sequence": 2
    },
    "VisualTargetRequest": {
        "schema_version": "1.0",
        "frame_id": "frame-0001",
        "current": {
            "x": 0.25,
            "y": 0.0,
            "z": 0.3,
            "roll": 0.0,
            "pitch": 0.0,
            "yaw": 0.0
        },
        "target": {
            "x": 0.3,
            "y": 0.02,
            "z": 0.3,
            "roll": 0.0,
            "pitch": 0.0,
            "yaw": 0.1
        },
        "confidence": 0.9,
        "safety_state": "READY",
        "data_age_ms": 40
    },
    "VelocityCommand": {
        "schema_version": "1.0",
        "vx": 0.01,
        "vy": 0.0,
        "vz": -0.005,
        "wroll": 0.0,
        "wpitch": 0.0,
        "wyaw": 0.02,
        "hold": False,
        "issued_at_ms": 1767261600000,
        "valid_for_ms": 200,
        "seq": 7,
        "frame_id": "frame-0001"
    },
    "FrameMeta": {
        "schema_version": "1.0",
        "frame_id": "frame-0001",
        "capture_ts_utc": "2026-01-01T10:00:00.250Z",
        "width": 1280,
        "height": 720,
        "pixel_format": "RGB",
        "session_id": "run-1",
        "source_id": "cam-top",
        "sequence": 1
    },
    "DetectionFrame": {
        "schema_version": "1.0",
        "frame_id": "frame-0001",
        "capture_ts_utc": "2026-01-01T10:00:00.250Z",
        "box_unit": "normalized",
        "detections": [
            {
                "class_id": 0,
                "label": "fiducial",
                "score": 0.93,
                "box": {
                    "x_min": 0.4,
                    "y_min": 0.35,
                    "x_max": 0.52,
                    "y_max": 0.49
                }
            }
        ],
        "session_id": "run-1",
        "model": {
            "model_name": "yolov8n",
            "model_version": "1.2.0",
            "model_sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "hailo_arch": "hailo8",
            "pipeline_version": "0.1.5"
        }
    },
    "MaintenanceIncident": {
        "incidentId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
        "sourceNode": "cm5-1",
        "detectedAt": "2026-01-01T10:00:00+00:00",
        "severity": "critical",
        "component": "hydra-umc-server.service",
        "symptom": "The unit is not active.",
        "evidenceRefs": [
            "systemctl:hydra-umc-server.service"
        ],
        "redactionLevel": "sanitized",
        "requestedBy": None,
        "correlationId": "0d3f1f0c-6a43-4f3a-9a53-6a1d0c4b8e11"
    },
    "NodeSnapshot": {
        "sourceNode": "cm5-1",
        "collectedAt": "2026-01-01T10:00:05+00:00",
        "correlationId": "0d3f1f0c-6a43-4f3a-9a53-6a1d0c4b8e11",
        "projects": [
            {
                "name": "HYDRA-UMC-SERVER",
                "version": "0.7.2",
                "maturity": "established",
                "manifestPath": "/opt/hydra-umc/server/hydra-umc.project.json"
            }
        ],
        "manifestIssues": [
            {
                "path": "/opt/hydra-umc/old",
                "reason": "manifest is not valid JSON"
            }
        ],
        "systemdAvailable": True,
        "systemdUnavailableReason": None,
        "serviceHealth": [
            {
                "unitName": "hydra-umc-server.service",
                "active": False,
                "detail": "inactive"
            }
        ],
        "httpHealth": [
            {
                "url": "http://127.0.0.1:3000/health",
                "reachable": True,
                "statusCode": 200,
                "detail": "HTTP 200"
            }
        ],
        "incidents": [
            {
                "incidentId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "sourceNode": "cm5-1",
                "detectedAt": "2026-01-01T10:00:00+00:00",
                "severity": "critical",
                "component": "hydra-umc-server.service",
                "symptom": "systemd unit is not active: inactive",
                "evidenceRefs": [
                    "systemctl is-active hydra-umc-server.service"
                ],
                "redactionLevel": "sanitized",
                "requestedBy": "edge-agent:auto",
                "correlationId": "0d3f1f0c-6a43-4f3a-9a53-6a1d0c4b8e11"
            }
        ],
        "hostHealth": {
            "disks": [
                {
                    "path": "/",
                    "freeBytes": 12000000000,
                    "totalBytes": 29000000000,
                    "freePercent": 41.4,
                    "error": None
                }
            ],
            "thermal": {
                "celsius": 52.3,
                "throttledRaw": 0,
                "throttledNow": [],
                "throttledPast": [],
                "vcgencmdAvailable": True
            },
            "backups": {
                "directory": "/var/backups/hydra-umc",
                "count": 3,
                "newestAgeDays": 1.5,
                "error": None
            }
        }
    },
    "ChangeProposal": {
        "proposalId": "b0d3f2a4-5c1e-4f7a-9d1e-2a6f3c8e7b10",
        "incidentId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
        "correlationId": "0d3f1f0c-6a43-4f3a-9a53-6a1d0c4b8e11",
        "createdAt": "2026-01-01T10:05:00+00:00",
        "projectName": "HYDRA-UMC-SERVER",
        "description": "Raise the health timeout from 2 to 5 seconds.",
        "diff": "--- a/config.json\n+++ b/config.json\n@@ -1 +1 @@\n-{\"timeout\": 2}\n+{\"timeout\": 5}\n",
        "rationale": "The route answers in 3 seconds on a loaded board.",
        "status": "approved",
        "decidedBy": "ana",
        "decidedAt": "2026-01-01T10:10:00+00:00",
        "decisionReason": "Checked on the bench.",
        "approvedContentDigest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "allowProtectedPaths": False,
        "approvalExpiresAt": "2026-01-02T10:10:00+00:00",
        "approvedBaseCommit": "0123456789abcdef0123456789abcdef01234567",
        "approvalSignature": "c2lnbmF0dXJl",
        "generatedBy": None
    },
    "CanaryDeployResult": {
        "deployId": "4f1c0b52-8d3a-4e7b-a1c9-5d2e6f7a8b90",
        "proposalId": "b0d3f2a4-5c1e-4f7a-9d1e-2a6f3c8e7b10",
        "projectName": "HYDRA-UMC-SERVER",
        "startedAt": "2026-01-01T10:20:00+00:00",
        "finishedAt": "2026-01-01T10:21:30+00:00",
        "promoted": True,
        "stageReached": "promoted",
        "buildOutput": "ok",
        "detail": "promoted - the previous checkout was kept, never deleted",
        "backupPath": "/opt/hydra-umc/backups/server-1",
        "patchPath": None
    },
    "ToolDescriptor": {
        "schema_version": "1.0",
        "tool_id": 0,
        "name": "SOLDERING_IRON",
        "title": "Soldering Iron",
        "kind": "motion",
        "hero_metric": {"label": "TIP TEMP", "unit": "C"},
        "limits": {"default": 320, "min": 150, "max": 445},
        "watchdog_ms": 250
    },
    "ToolState": {
        "schema_version": "1.0",
        "tool_id": 0,
        "state": "active",
        "source": "mock-head",
        "timestamp_utc": "2026-01-01T10:00:00Z",
        "can": {"state": "ok", "tec": 0, "rec": 0, "bus_off_count": 0},
        "temperature_c": 318.5,
        "setpoint_c": 320
    },
    "ProductionEvent": {
        "schema_version": "1.0",
        "source_id": "cnc-1",
        "at_utc": "2024-01-01T00:00:00Z",
        "good": True,
        "cycle_time_s": 42.5,
    },
    "EcosystemHealth": {
        "schema_version": "1.0",
        "generated_at_utc": "2024-01-01T00:00:00Z",
        "available": True,
        "summary": {"total": 1, "ok": 1, "degraded": 0, "down": 0, "unknown": 0, "drift": 0},
        "services": [
            {
                "name": "HYDRA-UMC-DATALAKE",
                "family": "hydra-umc",
                "role": "service",
                "state": "ok",
                "reason": "health_ok",
                "version_expected": "0.1.0",
                "version_reported": "0.1.0",
                "drift": False,
                "last_seen_utc": "2024-01-01T00:00:00Z",
                "latency_ms": 4,
            }
        ],
        "certificate": None,
        "warnings": [],
    },
    "RobotLiveness": {
        "schema_version": "1.0",
        "stale_after_s": 30,
        "robots": [
            {"controller_id": "c1", "robot_id": 1, "state": "live", "last_update_utc": "2024-01-01T00:00:00Z", "age_s": 4, "source": "state"},
            {"controller_id": "c1", "robot_id": 2, "state": "unknown"},
        ],
    },
    "ConnectionEvent": {
        "schema_version": "1.0",
        "id": 1,
        "at_utc": "2024-01-01T00:00:00Z",
        "action": "login",
        "client_kind": "studio",
        "client_id": "0123456789abcdef",
        "user": "operator",
        "origin": "local",
        "two_factor": False,
    },
    "ConnectionClient": {
        "schema_version": "1.0",
        "id": "0123456789abcdef",
        "kind": "studio",
        "user": "operator",
        "first_seen_utc": "2024-01-01T00:00:00Z",
        "last_seen_utc": "2024-01-01T00:00:00Z",
        "active_sessions": 1,
        "logins_ok": 1,
        "logins_failed": 0,
    },
    "RobotState": {
        "schema_version": "1.0",
        "robot_id": "arm-1",
        "state": "idle",
        "source": "simulated",
        "updated_at_utc": "2024-01-01T00:00:00Z",
    },
    "TwinState": {
        "schema_version": "1.0",
        "source": "simulated",
        "frame": "base",
        "timestamp_utc": "2024-01-01T00:00:00Z",
        "joint_states": [{"name": "shoulder", "position": 0.5, "velocity": 0.0}],
        "poses": [
            {
                "name": "tool_center_point",
                "pose": {
                    "schema_version": "1.0",
                    "frame": "base",
                    "position": {"x": 0.25, "y": 0.0, "z": 0.3},
                    "orientation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
                },
            }
        ],
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
    # Set by create_server(openapi=...): the routes of a published OpenAPI
    # document, answered with examples built from its own schemas. None keeps
    # the server to the /mock/ contract examples.
    router: OpenApiRouter | None = None

    # Quiet by default - a test suite spinning this server up per-test
    # doesn't need BaseHTTPRequestHandler's own request-log line on stderr
    # for every GET.
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - stdlib signature
        pass

    def _write_json(self, status: int, body: Any, headers: dict[str, str] | None = None) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _serve_openapi(self, method: str) -> bool:
        router = self.router
        if router is None or self.path.startswith("/mock/"):
            return False
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        template, operation, allowed = router.match(method, self.path)
        if not template:
            return False
        if operation is None:
            self._write_json(405, {"error": "method not allowed", "allowed": allowed}, {"Allow": ", ".join(allowed)})
            return True
        status, headers, body = router.answer(operation, self.headers.get("Authorization"))
        self._write_json(status, body if body is not None else {}, headers)
        return True

    def do_POST(self) -> None:  # noqa: N802 - stdlib method name
        if not self._serve_openapi(self.command):
            self._write_json(404, {"error": "not found"})

    do_PUT = do_PATCH = do_DELETE = do_POST

    def do_GET(self) -> None:  # noqa: N802 - stdlib method name
        if self._serve_openapi("GET"):
            return
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


def create_server(host: str = "127.0.0.1", port: int = 0, openapi: OpenApiRouter | str | None = None) -> ThreadingHTTPServer:
    """Real HTTP server, not started - `.server_address` reports the actual
    bound port once serving (useful with port=0 for an ephemeral port in
    tests). With `openapi` (a router or the path of an OpenAPI document) the
    server also answers the paths and methods of that document."""
    if isinstance(openapi, str):
        openapi = OpenApiRouter.from_file(openapi)
    handler = type("OpenApiMockHandler", (MockContractHandler,), {"router": openapi}) if openapi else MockContractHandler
    return ThreadingHTTPServer((host, port), handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Serve example v1 HYDRA-UMC SDK contract payloads over real HTTP for client testing."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8790)
    parser.add_argument("--openapi", help="path of an OpenAPI document whose routes are answered with examples built from its schemas")
    args = parser.parse_args(argv)

    server = create_server(args.host, args.port, args.openapi)
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
