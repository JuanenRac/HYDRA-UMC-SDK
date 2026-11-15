# =============================================================================
# HYDRA-UMC-SDK - Tests of the bodies, queries and answers the contract declares
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The routes whose body, query or answer used to be left out of the contract declare them, and the generated clients carry them."""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("generate_clients", ROOT / "tools" / "generate_clients.py")
gc = importlib.util.module_from_spec(_spec)
sys.modules["generate_clients_bodies"] = gc
_spec.loader.exec_module(gc)

FULL = json.loads((ROOT / "contracts" / "openapi" / "v1" / "server.full.openapi.json").read_text(encoding="utf-8"))
OPS = {(o["method"], o["path"]): o for o in gc.operations(FULL)}
TS = (ROOT / "generated" / gc.TS_NAME).read_text(encoding="utf-8")
KT = (ROOT / "generated" / gc.KT_NAME).read_text(encoding="utf-8")
DART = (ROOT / "generated" / gc.DART_NAME).read_text(encoding="utf-8")

SWITCHES = [
    "/api/droid-estop/settings", "/api/hil-bridge/settings", "/api/ros2-bridge/settings",
    "/api/connector-hub/gate/settings", "/api/semantic-planner/settings",
]
SETTING_BODIES = {
    "/api/droid-estop/settings": {"enabled", "confirm"},
    "/api/hil-bridge/settings": {"requireTwinPass", "confirm"},
    "/api/ros2-bridge/settings": {"requireSros2", "confirm"},
    "/api/connector-hub/gate/settings": {"allowLoopbackNoIdentity", "confirm"},
    "/api/semantic-planner/settings": {"requireIdentity", "confirm"},
}


class DeclaredBodiesTests(unittest.TestCase):
    def test_the_settings_switches_declare_their_body_and_their_answers(self):
        for path in SWITCHES:
            post, get = OPS[("POST", path)], OPS[("GET", path)]
            self.assertIsNotNone(post["body_schema"], path)
            self.assertEqual(set(post["body_schema"]["properties"]), SETTING_BODIES[path], path)
            self.assertNotEqual(post["result"], "void", path)
            self.assertNotEqual(get["result"], "void", path)

    def test_the_server_config_body_carries_more_than_the_port(self):
        schema = OPS[("PUT", "/api/admin/server-config")]["body_schema"]
        self.assertEqual(schema.get("required", []), [])
        for name in ("port", "detectionHef", "push", "auth", "bridges", "jobDispatcher"):
            self.assertIn(name, schema["properties"])
        self.assertIn("warnings", OPS[("PUT", "/api/admin/server-config")]["result"])

    def test_the_safety_limits_patch_and_the_telemetry_queries_are_declared(self):
        self.assertIn("jog", OPS[("PUT", "/api/admin/safety-limits")]["body_schema"]["properties"])
        self.assertIn("limits", OPS[("PUT", "/api/admin/safety-limits")]["result"])
        for path, needed in (("/api/telemetry/query", {"sourceId", "kind", "field", "start", "end", "limit", "cursor"}),
                             ("/api/telemetry/aggregate", {"kind", "field", "bucketMs", "start", "end", "agg"})):
            self.assertLessEqual(needed, {p["name"] for p in OPS[("GET", path)]["query"]}, path)
        plan = OPS[("PUT", "/api/telemetry/downsample-plan")]["body_schema"]
        self.assertEqual(plan["required"], ["plan"])
        self.assertIn("expectedHash", plan["properties"])
        self.assertIn("hash", OPS[("GET", "/api/telemetry/downsample-plan")]["result"])

    def test_settings_upload_and_hardware_are_declared(self):
        for method in ("POST", "PUT"):
            op = OPS[(method, "/api/settings")]
            self.assertEqual(op["body"], "Settings")
            self.assertIn("revision", op["result"])
        self.assertEqual([h["name"] for h in OPS[("PUT", "/api/settings")]["headers"]], ["If-Match"])
        self.assertTrue(OPS[("PUT", "/api/settings")]["headers"][0]["required"])
        self.assertEqual(OPS[("POST", "/api/hardware/fram/erase")]["body_schema"]["properties"]["confirm"]["enum"], ["ERASE"])
        flash = FULL["paths"]["/api/hardware/canota/flash"]["post"]
        self.assertIn("application/octet-stream", flash["requestBody"]["content"])
        self.assertLessEqual({"tier", "slot", "signature", "version_patch"}, {p["name"] for p in flash["parameters"]})
        content = OPS[("POST", "/api/upload-work")]["body_schema"]["properties"]["content"]
        self.assertNotIn("type", content, "the points are an array, not a string")

    def test_the_robot_routes_declare_the_headers_and_the_answers(self):
        base = "/api/robot/{id}"
        for suffix, names in (("/command", {"If-Match", "X-Controller-Id", "X-Correlation-Id"}), ("/claim", {"If-Match", "X-Controller-Id"}),
                              ("/release", {"If-Match", "X-Controller-Id"}), ("/jog-arm", {"X-Controller-Id"})):
            op = OPS[("POST", base + suffix)]
            self.assertEqual({h["name"] for h in op["headers"]}, names, suffix)
            self.assertNotEqual(op["result"], "void", suffix)
        self.assertIn("revision", OPS[("GET", base)]["result"])
        self.assertIn("ETag", FULL["paths"][base]["get"]["responses"]["200"]["headers"])
        self.assertIn("operation_id", OPS[("POST", base + "/command")]["result"])

    def test_every_client_sends_the_headers(self):
        self.assertIn("readonly headers: Readonly<Record<string, string>>;", TS)
        self.assertIn('headers?: { "If-Match"?: string; "X-Controller-Id"?: string', TS)
        self.assertIn("headers: queryOf(args?.headers)", TS)
        self.assertIn("val headers: Map<String, String> = emptyMap()", KT)
        self.assertIn('headers = queryOf(mapOf("If-Match" to headerIfMatch', KT)
        self.assertIn("final Map<String, String> headers;", DART)
        self.assertIn("headers: queryOf({'If-Match': headerIfMatch", DART)

    def test_a_route_without_headers_sends_an_empty_set(self):
        self.assertIn('path: "/api/droid-estop/settings", query: {}, headers: {}', TS)


class IngestAndWatchdogTests(unittest.TestCase):
    def test_the_server_config_body_declares_the_ingest_block_and_stays_closed(self):
        schema = OPS[("PUT", "/api/admin/server-config")]["body_schema"]
        ingest = schema["properties"]["ingest"]
        self.assertIs(ingest["additionalProperties"], False)
        self.assertEqual(
            set(ingest["properties"]),
            {"faultFeed", "scenario", "developerNode", "anomalyFeed", "anomalyVoiceRelay", "voiceChain", "proposalVerify", "proposalKeysFile"},
        )
        self.assertEqual(ingest["properties"]["proposalKeysFile"]["type"], "string")
        for name in ingest["properties"]:
            if name != "proposalKeysFile":
                self.assertEqual(ingest["properties"][name]["type"], "boolean", name)

    def test_the_watchdog_decision_declares_its_body_and_the_relay_statuses(self):
        decide = OPS[("POST", "/api/ops-agent/proposals/decide")]
        schema = decide["body_schema"]
        self.assertEqual(set(schema["properties"]), {"incidentId", "decision", "confirm"})
        self.assertEqual(schema["required"], ["incidentId", "decision"])
        self.assertEqual(schema["properties"]["decision"]["enum"], ["approved", "rejected"])
        listing = OPS[("GET", "/api/ops-agent/proposals")]
        self.assertNotEqual(listing["result"], "void")
        routes = {(r["method"].lower(), r["path"]): r for r in json.loads((ROOT / "generated" / "hydra-routes.json").read_text(encoding="utf-8"))["routes"]}
        for key in (("get", "/api/ops-agent/proposals"), ("post", "/api/ops-agent/proposals/decide")):
            self.assertTrue({"404", "502", "503"} <= set(routes[key]["statuses"]), key)

    def test_the_generated_clients_carry_the_decision_body(self):
        self.assertIn("postOpsAgentProposalsDecide(args: { body:", TS)
        self.assertIn("postOpsAgentProposalsDecide(body: HydraPostOpsAgentProposalsDecideBody)", KT)
        self.assertIn("postOpsAgentProposalsDecide({required HydraPostOpsAgentProposalsDecideBody body})", DART)


if __name__ == "__main__":
    unittest.main()
