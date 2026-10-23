# =============================================================================
# HYDRA-UMC-SDK - Tests of the claim, jog arming and safety-limit client
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Replays conformance/server-routes/cases.json (the same file the Go,
TypeScript and Rust clients replay) and checks every route against the
OpenAPI copies."""
import json
import re
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from hydra_umc_sdk import server_api as api

ROOT = Path(__file__).resolve().parents[3]
CASES = json.loads((ROOT / "conformance" / "server-routes" / "cases.json").read_text(encoding="utf-8"))
SUBSET = json.loads((ROOT / "contracts" / "openapi" / "v1" / "server.openapi.json").read_text(encoding="utf-8"))
FULL = json.loads((ROOT / "contracts" / "openapi" / "v1" / "server.full.openapi.json").read_text(encoding="utf-8"))

KIND_TYPES = {
    "claim-conflict": api.ClaimConflictError,
    "controller-id-required": api.ControllerIdRequiredError,
    "invalid-controller-id": api.InvalidControllerIdError,
    "jog-not-armed": api.JogNotArmedError,
    "api-error": api.ApiError,
}


def build(call: str, args: dict) -> api.Request:
    controller = args.get("controllerId")
    robot = args.get("robotId")
    if call == "claim":
        return api.claim_request(robot, ttl_ms=args.get("ttlMs"), force=args.get("force"), reason=args.get("reason"), controller_id=controller)
    if call == "release":
        return api.release_request(robot, reason=args.get("reason"), controller_id=controller)
    if call == "jogArm":
        return api.jog_arm_request(robot, args["armed"], ttl_ms=args.get("ttlMs"), controller_id=controller)
    if call == "listClaims":
        return api.list_claims_request()
    if call == "getSafetyLimits":
        return api.safety_limits_request(robot)
    if call == "updateSafetyLimits":
        return api.update_safety_limits_request(args["patch"])
    if call == "command":
        return api.command_request(robot, args["command"], args.get("params"), controller_id=controller)
    raise AssertionError(call)


def template(path: str) -> str:
    """'/api/robot/3/claim?x=1' -> '/api/robot/{id}/claim'."""
    return re.sub(r"/robot/\d+/", "/robot/{id}/", path.split("?")[0])


class RequestBuilderTests(unittest.TestCase):
    def test_every_case_builds_the_expected_request(self):
        for case in CASES["requests"]:
            with self.subTest(case["name"]):
                request = build(case["call"], case["args"])
                self.assertEqual(request.method, case["expect"]["method"])
                self.assertEqual(request.path, case["expect"]["path"])
                self.assertEqual(request.body, case["expect"]["body"])

    def test_invalid_requests_are_refused_before_sending(self):
        for case in CASES["invalidRequests"]:
            with self.subTest(case["name"]):
                with self.assertRaises(api.ServerRequestError):
                    build(case["call"], case["args"])

    def test_robot_id_must_be_an_integer(self):
        for bad in ("1", 1.5, True, None):
            with self.subTest(bad=bad):
                with self.assertRaises(api.ServerRequestError):
                    api.claim_request(bad)

    def test_armed_must_be_a_boolean(self):
        with self.assertRaises(api.ServerRequestError):
            api.jog_arm_request(1, "yes")

    def test_a_request_without_controller_id_is_the_v1_request(self):
        self.assertNotIn("controllerId", api.command_request(1, "jog", {"axis": "x", "amount": 1}).body)


class ErrorTests(unittest.TestCase):
    def test_every_error_case_gets_its_typed_error(self):
        for case in CASES["errors"]:
            with self.subTest(case["name"]):
                error = api.parse_api_error(case["status"], case["body"])
                expect = case["expect"]
                self.assertIs(type(error), KIND_TYPES[expect["kind"]])
                self.assertEqual(error.status, case["status"])
                self.assertEqual(error.code, expect["code"])
                if expect["hasReservation"]:
                    self.assertIsNotNone(error.reservation)
                else:
                    self.assertFalse(getattr(error, "reservation", None))

    def test_controller_required_is_a_claim_conflict_and_an_api_error(self):
        error = api.parse_api_error(409, {"error": "x", "code": "controller-id-required"})
        self.assertIsInstance(error, api.ClaimConflictError)
        self.assertIsInstance(error, api.ApiError)

    def test_reservation_details_survive(self):
        case = next(c for c in CASES["errors"] if c["name"] == "other-controller")
        error = api.parse_api_error(case["status"], case["body"])
        self.assertEqual(error.reservation.controller_id, "tab-1")
        self.assertEqual(error.reservation.owner_username, "alice")


class ResponseTests(unittest.TestCase):
    def test_claim_result(self):
        result = api.parse_claim_result(CASES["responses"]["claim"])
        self.assertEqual(result.reservation.controller_id, "tab-1")
        self.assertEqual(result.history[0]["action"], "claimed")

    def test_release_result_has_no_reservation(self):
        self.assertIsNone(api.parse_claim_result({"success": True, "reservation": None}).reservation)

    def test_jog_arm_results(self):
        on = api.parse_jog_arm_result(CASES["responses"]["jogArmOn"])
        self.assertTrue(on.armed)
        self.assertEqual(on.ttl_ms, 30000)
        off = api.parse_jog_arm_result(CASES["responses"]["jogArmOff"])
        self.assertFalse(off.armed)
        self.assertIsNone(off.expires_at)
        with self.assertRaises(api.ServerRequestError):
            api.parse_jog_arm_result({"success": True})

    def test_claims(self):
        claims = api.parse_claims(CASES["responses"]["claims"])
        self.assertEqual([c.robot_id for c in claims], [1, 2])
        self.assertEqual(claims[0].controller_id, "tab-1")
        self.assertIsNone(claims[1].controller_id)
        self.assertIsNone(claims[1].robot_name)

    def test_safety_limits_with_robot(self):
        view = api.parse_safety_limits(CASES["responses"]["safetyLimits"])
        self.assertFalse(view.limits["claims"]["requireControllerId"])
        self.assertEqual(view.hard_limits["armTtlMs"]["max"], 600000)
        self.assertEqual(view.robot.jog_armed_until, 31000)
        self.assertEqual(view.robot.model, "Parol6 (6-DOF)")

    def test_unknown_fields_are_ignored(self):
        body = dict(CASES["responses"]["jogArmOn"], futureField=1)
        self.assertTrue(api.parse_jog_arm_result(body).armed)


class ClientTests(unittest.TestCase):
    def client(self, status, body, **kwargs):
        sent = []

        def transport(method, url, headers, data):
            sent.append((method, url, dict(headers), data))
            return status, (json.dumps(body).encode() if body is not None else b"not json")

        return api.ServerClient("http://hydra.local:3000/", "tok", transport=transport, **kwargs), sent

    def test_claim_sends_token_and_default_controller(self):
        client, sent = self.client(200, CASES["responses"]["claim"], controller_id="tab-1")
        result = client.claim(1, ttl_ms=1000)
        method, url, headers, data = sent[0]
        self.assertEqual((method, url), ("POST", "http://hydra.local:3000/api/robot/1/claim"))
        self.assertEqual(headers["Authorization"], "Bearer tok")
        self.assertEqual(json.loads(data), {"ttlMs": 1000, "controllerId": "tab-1"})
        self.assertEqual(result.reservation.owner_username, "alice")

    def test_call_controller_wins_over_the_default(self):
        client, sent = self.client(200, CASES["responses"]["claim"], controller_id="tab-1")
        client.release(1, controller_id="tab-2")
        self.assertEqual(json.loads(sent[0][3])["controllerId"], "tab-2")

    def test_no_default_controller_sends_none(self):
        client, sent = self.client(200, CASES["responses"]["jogArmOff"])
        client.jog_arm(1, False)
        self.assertEqual(json.loads(sent[0][3]), {"armed": False})

    def test_conflict_raises_typed_error(self):
        case = next(c for c in CASES["errors"] if c["name"] == "other-account")
        client, _ = self.client(case["status"], case["body"])
        with self.assertRaises(api.ClaimConflictError) as raised:
            client.claim(1)
        self.assertEqual(raised.exception.code, "other-account")

    def test_jog_not_armed_on_command(self):
        case = next(c for c in CASES["errors"] if c["name"] == "jog-not-armed")
        client, _ = self.client(case["status"], case["body"])
        with self.assertRaises(api.JogNotArmedError):
            client.command(1, "jog", {"axis": "x", "amount": 1})

    def test_non_json_error_is_still_an_api_error(self):
        client, _ = self.client(502, None)
        with self.assertRaises(api.ApiError) as raised:
            client.list_claims()
        self.assertEqual(raised.exception.status, 502)

    def test_invalid_default_controller_is_refused(self):
        with self.assertRaises(api.ServerRequestError):
            api.ServerClient("http://x", controller_id="no good")

    def test_default_transport_over_http(self):
        seen = {}

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                seen["auth"] = self.headers.get("Authorization")
                seen["path"] = self.path
                payload = json.dumps(CASES["responses"]["claims"]).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = api.ServerClient(f"http://127.0.0.1:{server.server_port}", "tok")
            self.assertEqual(len(client.list_claims()), 2)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(5)
        self.assertEqual(seen, {"auth": "Bearer tok", "path": "/api/claims"})


class OpenApiContractTests(unittest.TestCase):
    def test_every_route_of_every_case_is_in_both_documents(self):
        for case in CASES["requests"]:
            expect = case["expect"]
            for name, document in (("subset", SUBSET), ("full", FULL)):
                with self.subTest(case=case["name"], document=name):
                    item = document["paths"].get(template(expect["path"]))
                    self.assertIsNotNone(item, template(expect["path"]))
                    self.assertIn(expect["method"].lower(), item)

    def test_the_subset_never_invents_a_route(self):
        for path, item in SUBSET["paths"].items():
            self.assertIn(path, FULL["paths"], path)
            for method in set(item) & {"get", "put", "post", "delete", "patch"}:
                self.assertIn(method, FULL["paths"][path], f"{method} {path}")

    def test_request_body_fields_are_declared_by_the_subset(self):
        for case in CASES["requests"]:
            expect = case["expect"]
            body = expect["body"]
            if not body or case["call"] == "updateSafetyLimits":
                continue
            operation = SUBSET["paths"][template(expect["path"])][expect["method"].lower()]
            schema = operation["requestBody"]["content"]["application/json"]["schema"]
            if case["call"] == "command":
                continue  # a oneOf over the command schemas; its params are covered by the v1 slice
            declared = set(SUBSET["components"]["schemas"][schema["$ref"].rsplit("/", 1)[1]]["properties"])
            with self.subTest(case["name"]):
                self.assertLessEqual(set(body), declared)

    def test_the_full_copy_declares_what_the_full_document_declares_for_jog_arm(self):
        props = FULL["paths"]["/api/robot/{id}/jog-arm"]["post"]["requestBody"]["content"]["application/json"]["schema"]["properties"]
        self.assertLessEqual({"armed", "ttlMs", "controllerId"}, set(props))

    def test_every_error_code_is_documented_in_the_subset(self):
        text = json.dumps(SUBSET)
        for code in api.KNOWN_ERROR_CODES:
            with self.subTest(code):
                self.assertIn(code, text)

    def test_the_controller_id_pattern_is_the_one_of_the_client(self):
        pattern = SUBSET["components"]["schemas"]["ControllerId"]["pattern"]
        for value, valid in (("tab-1", True), ("a.b_c:d-e", True), ("a" * 64, True), ("a" * 65, False), ("a b", False), ("", False), ("a/b", False)):
            with self.subTest(value=value):
                self.assertEqual(re.fullmatch(pattern, value) is not None, valid)
                self.assertEqual(api.is_valid_controller_id(value), valid)

    def test_the_header_parameter_is_on_every_route_that_takes_a_controller(self):
        for path in ("/api/robot/{id}/claim", "/api/robot/{id}/release", "/api/robot/{id}/jog-arm", "/api/robot/{id}/command"):
            refs = [p.get("$ref") for p in SUBSET["paths"][path]["post"]["parameters"]]
            self.assertIn("#/components/parameters/ControllerIdHeader", refs, path)
        self.assertEqual(SUBSET["components"]["parameters"]["ControllerIdHeader"]["name"], api.CONTROLLER_ID_HEADER)

    def test_command_documents_403_and_the_three_conflict_codes(self):
        responses = SUBSET["paths"]["/api/robot/{id}/command"]["post"]["responses"]
        self.assertIn("403", responses)
        self.assertIn("jog-not-armed", responses["403"]["description"])
        for code in ("other-account", "other-controller", "controller-id-required"):
            self.assertIn(code, responses["409"]["description"])


if __name__ == "__main__":
    unittest.main()
