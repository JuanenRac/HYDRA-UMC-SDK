# =============================================================================
# HYDRA-UMC-SDK - Tests of the client of blocks 2 to 5 of the second server contract
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Replays conformance/server-routes/cases_v2.json (the same file the Go, TypeScript
and Rust clients replay): the revision of a robot, If-Match, the table command, the
audit record and the claims message of the WebSocket."""
import json
import unittest
from pathlib import Path

from hydra_umc_sdk import server_api as api

ROOT = Path(__file__).resolve().parents[3]
CASES = json.loads((ROOT / "conformance" / "server-routes" / "cases_v2.json").read_text(encoding="utf-8"))

KIND_TYPES = {
    "revision-mismatch": api.RevisionMismatchError,
    "table-move": api.TableMoveError,
}


def build(call: str, args: dict) -> api.Request:
    robot = args.get("robotId")
    if call == "getRobot":
        return api.get_robot_request(robot)
    if call == "claim":
        return api.claim_request(robot, controller_id=args.get("controllerId"), if_match=args.get("ifMatch"))
    if call == "release":
        return api.release_request(robot, controller_id=args.get("controllerId"), if_match=args.get("ifMatch"))
    if call == "command":
        return api.command_request(robot, args["command"], args.get("params"), controller_id=args.get("controllerId"), if_match=args.get("ifMatch"))
    if call == "table":
        kwargs = {"controller_id": args.get("controllerId"), "if_match": args.get("ifMatch")}
        if "rz" in args:
            kwargs["rz"] = args["rz"]
        if "mode" in args:
            kwargs["mode"] = args["mode"]
        return api.table_command_request(robot, args["x"], args["y"], **kwargs)
    if call == "audit":
        return api.audit_request(
            limit=args.get("limit"), after_seq=args.get("afterSeq"), type=args.get("type"),
            robot_id=args.get("robotId"), verify=bool(args.get("verify")),
        )
    raise AssertionError(call)


class RequestTests(unittest.TestCase):
    def test_every_case_builds_the_expected_request(self):
        for case in CASES["requests"]:
            with self.subTest(case["name"]):
                request = build(case["call"], case["args"])
                expect = case["expect"]
                self.assertEqual(request.method, expect["method"])
                self.assertEqual(request.path, expect["path"])
                self.assertEqual(request.body, expect["body"])
                self.assertEqual(dict(request.headers), expect["headers"])

    def test_invalid_requests_are_refused_before_sending(self):
        for case in CASES["invalidRequests"]:
            with self.subTest(case["name"]):
                with self.assertRaises(api.ServerRequestError):
                    build(case["call"], case["args"])


class ErrorTests(unittest.TestCase):
    def test_every_error_case_gets_its_typed_error(self):
        for case in CASES["errors"]:
            with self.subTest(case["name"]):
                error = api.parse_api_error(case["status"], case["body"])
                expect = case["expect"]
                self.assertIs(type(error), KIND_TYPES[expect["kind"]])
                self.assertEqual(error.status, case["status"])
                self.assertEqual(error.code, expect["code"])
                if expect["kind"] == "revision-mismatch":
                    self.assertEqual(error.revision, expect["revision"])

    def test_a_revision_mismatch_is_an_api_error(self):
        self.assertIsInstance(api.parse_api_error(412, {"error": "x", "code": "revision-mismatch"}), api.ApiError)


class ResponseTests(unittest.TestCase):
    def test_robot_and_its_revision(self):
        view = api.parse_robot(CASES["responses"]["robot"])
        self.assertEqual(view.revision, "0123456789abcdef")
        self.assertEqual(view.robot["name"], "B")
        self.assertEqual(view.cell_id, "c1")
        with self.assertRaises(api.ServerRequestError):
            api.parse_robot({"robot": {}})

    def test_command_results(self):
        plain = api.parse_command_result(CASES["responses"]["commandPlain"])
        self.assertTrue(plain.success)
        self.assertEqual(plain.revision, "fedcba9876543210")
        self.assertIsNone(plain.applied)
        table = api.parse_command_result(CASES["responses"]["commandTable"])
        self.assertEqual((table.applied.x, table.applied.y, table.applied.rz), (40, 65, 15))

    def test_a_claim_answer_carries_the_new_revision(self):
        self.assertEqual(api.parse_claim_result(CASES["responses"]["claimWithRevision"]).revision, "0123456789abcdef")
        self.assertIsNone(api.parse_claim_result({"success": True, "reservation": None}).revision)

    def test_audit(self):
        view = api.parse_audit(CASES["responses"]["audit"])
        self.assertTrue(view.enabled)
        self.assertFalse(view.locked_off)
        self.assertEqual([e.seq for e in view.entries], [1, 2])
        self.assertEqual(view.entries[0].controller_id, "tab-1")
        self.assertEqual(view.entries[0].detail["action"], "claimed")
        self.assertIsNone(view.entries[1].username)
        self.assertEqual(view.verification["entries"], 2)

    def test_claims_event(self):
        claims = api.parse_claims_event(CASES["responses"]["claimsEvent"])
        self.assertEqual([c.robot_id for c in claims], [1, 2])
        self.assertEqual(claims[0].jog_armed_until, 31000)
        self.assertIsNone(claims[1].jog_armed_until)
        self.assertIsNone(api.parse_claims_event(CASES["responses"]["otherMessage"]))
        self.assertIsNone(api.parse_claims_event("not a message"))


class ClientTests(unittest.TestCase):
    def client(self, status, body):
        sent = []

        def transport(method, url, headers, data):
            sent.append((method, url, dict(headers), data))
            return status, json.dumps(body).encode()

        return api.ServerClient("http://hydra.local:3000", "tok", transport=transport, controller_id="tab-1"), sent

    def test_the_revision_read_is_sent_back_as_if_match(self):
        client, sent = self.client(200, CASES["responses"]["robot"])
        view = client.robot(3)
        self.assertEqual(sent[0][1], "http://hydra.local:3000/api/robot/3")
        again, sent2 = self.client(200, CASES["responses"]["commandTable"])
        result = again.move_table(3, 40, 65, rz=15, if_match=view.revision)
        self.assertEqual(sent2[0][2]["If-Match"], '"0123456789abcdef"')
        self.assertEqual(json.loads(sent2[0][3])["params"], {"x": 40, "y": 65, "mode": "absolute", "rz": 15})
        self.assertEqual(json.loads(sent2[0][3])["controllerId"], "tab-1")
        self.assertEqual(result.applied.robot_id, 1)

    def test_a_stale_revision_raises_with_the_current_one(self):
        case = next(c for c in CASES["errors"] if c["name"] == "revision-mismatch")
        client, _ = self.client(case["status"], case["body"])
        with self.assertRaises(api.RevisionMismatchError) as raised:
            client.command(1, "jog", {"axis": "x", "amount": 1}, if_match="old")
        self.assertEqual(raised.exception.revision, "0123456789abcdef")

    def test_a_refused_table_move_raises(self):
        case = next(c for c in CASES["errors"] if c["name"] == "table-out-of-limit")
        client, _ = self.client(case["status"], case["body"])
        with self.assertRaises(api.TableMoveError):
            client.move_table(1, 5000, 0)

    def test_audit_goes_to_the_route_with_the_filters(self):
        client, sent = self.client(200, CASES["responses"]["audit"])
        view = client.audit(limit=5, type="claim", verify=True)
        self.assertEqual(sent[0][1], "http://hydra.local:3000/api/audit?limit=5&type=claim&verify=1")
        self.assertEqual(len(view.entries), 2)


if __name__ == "__main__":
    unittest.main()
