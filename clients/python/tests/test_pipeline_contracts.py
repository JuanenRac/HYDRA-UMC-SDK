# =============================================================================
# HYDRA-UMC-SDK - Command lifecycle, visual servoing, vision pipeline and maintenance contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from hydra_umc_sdk import (
    COMMAND_STATES,
    ContractValidationError,
    box_to_pixels,
    command_is_current,
    command_state_from_operation,
    incident_may_be_stored,
    is_terminal_state,
    validate,
    validate_state_transition,
)

FIXTURES = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1"
NAMES = {
    "CommandLifecycleEvent": "command-lifecycle-event",
    "VisualTargetRequest": "visual-target-request",
    "VelocityCommand": "velocity-command",
    "FrameMeta": "frame-meta",
    "DetectionFrame": "detection-frame",
    "MaintenanceIncident": "maintenance-incident",
    "ToolDescriptor": "tool-descriptor",
    "ToolState": "tool-state",
    "NodeSnapshot": "node-snapshot",
    "ChangeProposal": "change-proposal",
    "CanaryDeployResult": "canary-deploy-result",
    "FaultEvent": "fault-event",
}


def _fixture(stem: str, kind: str) -> dict:
    return json.loads((FIXTURES / f"{stem}.{kind}.json").read_text(encoding="utf-8"))


def _changed(payload: dict, **fields) -> dict:
    result = copy.deepcopy(payload)
    result.update(fields)
    return result


class FixtureTests(unittest.TestCase):
    def test_the_fixtures_are_judged_as_their_names_say(self):
        for contract, stem in NAMES.items():
            with self.subTest(contract=contract):
                validate(contract, _fixture(stem, "valid"))
                with self.assertRaises(ContractValidationError):
                    validate(contract, _fixture(stem, "invalid"))


class CommandLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.event = _fixture("command-lifecycle-event", "valid")

    def test_failed_and_cancelled_need_a_reason(self):
        for state in ("FAILED", "CANCELLED"):
            with self.subTest(state=state):
                with self.assertRaises(ContractValidationError):
                    validate("CommandLifecycleEvent", _changed(self.event, state=state))
                validate("CommandLifecycleEvent", _changed(self.event, state=state, reason="the controller refused it"))

    def test_a_step_never_goes_back(self):
        self.assertTrue(validate_state_transition("ACCEPTED", "RUNNING"))
        self.assertTrue(validate_state_transition("RUNNING", "COMPLETED"))
        self.assertFalse(validate_state_transition("RUNNING", "ACCEPTED"))
        self.assertFalse(validate_state_transition("ACCEPTED", "COMPLETED"))
        for state in ("COMPLETED", "FAILED", "CANCELLED"):
            self.assertTrue(is_terminal_state(state))
            for following in COMMAND_STATES:
                self.assertFalse(validate_state_transition(state, following))
        self.assertFalse(validate_state_transition("ACCEPTED", "DONE"))
        self.assertFalse(validate_state_transition("DONE", "RUNNING"))

    def test_the_state_follows_the_operation(self):
        for status, expected in (("received", "ACCEPTED"), ("authorized", "ACCEPTED"), ("queued", "ACCEPTED"), ("sent", "RUNNING"), ("confirmed", "RUNNING")):
            self.assertEqual(command_state_from_operation(status), (expected, None))
        state, reason = command_state_from_operation("rejected")
        self.assertEqual(state, "FAILED")
        self.assertTrue(reason)
        with self.assertRaises(ContractValidationError):
            command_state_from_operation("done")

    def test_terminated_is_completed_only_with_real_evidence(self):
        proof = {"run_id": "r1", "origin": "real", "observers_enabled": True, "outcome": "success", "observed_at_utc": "2026-01-01T10:00:00Z"}
        self.assertEqual(command_state_from_operation("terminated", proof), ("COMPLETED", None))
        for label, result in (
            ("no result", None),
            ("never observed", {k: v for k, v in proof.items() if k != "observed_at_utc"}),
            ("observers off", dict(proof, observers_enabled=False)),
            ("simulation", dict(proof, origin="simulated")),
            ("failure", dict(proof, outcome="failure", outcome_reason="the axis stalled")),
            ("not a result", {"run_id": "r1"}),
        ):
            with self.subTest(label=label):
                state, reason = command_state_from_operation("terminated", result)
                self.assertEqual(state, "FAILED")
                self.assertTrue(reason)
        self.assertEqual(command_state_from_operation("terminated", dict(proof, origin="simulated"), allow_simulated=True), ("COMPLETED", None))


class ServoingTests(unittest.TestCase):
    def test_a_request_must_say_how_old_the_estimate_is(self):
        request = _fixture("visual-target-request", "valid")
        del request["data_age_ms"]
        with self.assertRaises(ContractValidationError):
            validate("VisualTargetRequest", request)
        validate("VisualTargetRequest", _changed(request, captured_at_utc="2026-01-01T10:00:00Z"))

    def test_a_pose_is_exactly_six_finite_numbers(self):
        request = _fixture("visual-target-request", "valid")
        for label, pose in (
            ("missing yaw", {k: v for k, v in request["current"].items() if k != "yaw"}),
            ("extra field", dict(request["current"], w=1.0)),
            ("text", dict(request["current"], x="0.1")),
            ("boolean", dict(request["current"], z=True)),
            ("not finite", dict(request["current"], roll=float("nan"))),
            ("not an object", [0, 0, 0, 0, 0, 0]),
        ):
            with self.subTest(label=label), self.assertRaises(ContractValidationError):
                validate("VisualTargetRequest", _changed(request, current=pose))

    def test_a_command_is_current_only_inside_its_validity(self):
        command = _fixture("velocity-command", "valid")
        issued, valid = command["issued_at_ms"], command["valid_for_ms"]
        self.assertTrue(command_is_current(command, issued))
        self.assertTrue(command_is_current(command, issued + int(valid)))
        self.assertFalse(command_is_current(command, issued + int(valid) + 1))
        self.assertFalse(command_is_current(command, issued - 1))

    def test_a_velocity_must_be_finite(self):
        command = _fixture("velocity-command", "valid")
        for bad in (float("inf"), float("nan"), "0.1", None, True):
            with self.subTest(bad=bad), self.assertRaises(ContractValidationError):
                validate("VelocityCommand", _changed(command, vx=bad))


class VisionPipelineTests(unittest.TestCase):
    def test_a_box_cannot_end_before_it_starts(self):
        frame = _fixture("detection-frame", "valid")
        frame["detections"][0]["box"].update(x_min=0.6, x_max=0.5)
        with self.assertRaises(ContractValidationError):
            validate("DetectionFrame", frame)

    def test_normalized_boxes_stay_inside_the_frame(self):
        frame = _fixture("detection-frame", "valid")
        frame["detections"][0]["box"]["x_max"] = 1.2
        with self.assertRaises(ContractValidationError):
            validate("DetectionFrame", frame)
        validate("DetectionFrame", _changed(frame, box_unit="pixel"))

    def test_boxes_convert_to_pixels(self):
        box = {"x_min": 0.25, "y_min": 0.5, "x_max": 0.75, "y_max": 1.0}
        self.assertEqual(box_to_pixels(box, "normalized", 640, 480), {"x_min": 160.0, "y_min": 240.0, "x_max": 480.0, "y_max": 480.0})
        self.assertEqual(box_to_pixels({"x_min": 1, "y_min": 2, "x_max": 3, "y_max": 4}, "pixel", 640, 480), {"x_min": 1.0, "y_min": 2.0, "x_max": 3.0, "y_max": 4.0})
        with self.assertRaises(ContractValidationError):
            box_to_pixels(box, "percent", 640, 480)

    def test_the_model_is_the_compatibility_record(self):
        frame = _fixture("detection-frame", "valid")
        for field in ("model_name", "model_version", "model_sha256", "hailo_arch", "pipeline_version"):
            broken = copy.deepcopy(frame)
            del broken["model"][field]
            with self.subTest(field=field), self.assertRaises(ContractValidationError):
                validate("DetectionFrame", broken)

    def test_a_frame_meta_of_a_compressed_frame_is_valid(self):
        validate("FrameMeta", _changed(_fixture("frame-meta", "valid"), pixel_format="JPEG"))


class MaintenanceTests(unittest.TestCase):
    def test_the_snake_case_twin_is_refused(self):
        incident = _fixture("maintenance-incident", "valid")
        twin = dict(incident, incident_id=incident["incidentId"])
        del twin["incidentId"]
        with self.assertRaises(ContractValidationError):
            validate("MaintenanceIncident", twin)

    def test_an_incident_older_than_the_contract_still_validates(self):
        incident = _fixture("maintenance-incident", "valid")
        self.assertNotIn("schema_version", incident)
        validate("MaintenanceIncident", incident)
        validate("MaintenanceIncident", _changed(incident, schema_version="1.0"))

    def test_a_raw_incident_is_stored_only_when_the_consumer_allows_it(self):
        incident = _fixture("maintenance-incident", "valid")
        self.assertTrue(incident_may_be_stored(incident))
        raw = _changed(incident, redactionLevel="raw")
        self.assertFalse(incident_may_be_stored(raw))
        self.assertTrue(incident_may_be_stored(raw, allow_raw=True))


if __name__ == "__main__":
    unittest.main()
