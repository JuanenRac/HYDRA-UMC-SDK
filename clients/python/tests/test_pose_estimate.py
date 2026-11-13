# =============================================================================
# HYDRA-UMC-SDK - Tests of the PoseEstimate contract (third stage of the vision pipeline)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import copy
import json
import math
import random
import unittest
from pathlib import Path

from hydra_umc_sdk.validation import ContractValidationError, validate
from hydra_umc_sdk.vision_pipeline import check_estimates_match_detections, validate_pose_estimate

FIXTURES = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1"


def fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def detections(count=3, frame_id="f-000123", stamp="2026-01-02T10:00:00Z"):
    box = {"x_min": 0.1, "y_min": 0.1, "x_max": 0.2, "y_max": 0.2}
    return {
        "schema_version": "1.0",
        "frame_id": frame_id,
        "capture_ts_utc": stamp,
        "box_unit": "normalized",
        "detections": [{"class_id": 0, "label": "fiducial", "score": 0.9, "box": dict(box)} for _ in range(count)],
    }


class PoseEstimateTests(unittest.TestCase):
    def test_the_fixtures(self):
        validate("PoseEstimate", fixture("pose-estimate.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("PoseEstimate", fixture("pose-estimate.invalid.json"))

    def test_each_rule_is_checked(self):
        base = fixture("pose-estimate.valid.json")
        mutations = (
            lambda p: p.update(schema_version="2.0"),
            lambda p: p.update(extra=1),
            lambda p: p.update(frame_id="bad id"),
            lambda p: p.update(capture_ts_utc="yesterday"),
            lambda p: p.update(estimates="no"),
            lambda p: p["estimates"][0].update(detection_index=-1),
            lambda p: p["estimates"][0].update(detection_index=1000),
            lambda p: p["estimates"][0].update(detection_index=True),
            lambda p: p["estimates"][1].update(detection_index=0),
            lambda p: p["estimates"][0]["position"].update(z=math.inf),
            lambda p: p["estimates"][0]["position"].pop("z"),
            lambda p: p["estimates"][0]["orientation"].update(w=0.9),
            lambda p: p["estimates"][0]["orientation"].update(x=2),
            lambda p: p["estimates"][0].update(confidence=1.01),
            lambda p: p["estimates"][0].update(confidence=-0.1),
            lambda p: p["estimates"][0].pop("confidence"),
            lambda p: p["estimates"][0].update(extra=1),
            lambda p: p.update(estimates=[p["estimates"][0]] * 2),
        )
        for mutate in mutations:
            payload = copy.deepcopy(base)
            mutate(payload)
            with self.assertRaises(ContractValidationError):
                validate_pose_estimate(payload)

    def test_no_estimates_is_valid_because_a_pose_may_not_be_found(self):
        validate_pose_estimate({"schema_version": "1.0", "frame_id": "f1", "capture_ts_utc": "2026-01-02T10:00:00Z", "estimates": []})

    def test_random_unit_quaternions_pass_and_scaled_ones_do_not(self):
        rng = random.Random(3)
        for _ in range(500):
            raw = [rng.gauss(0, 1) for _ in range(4)]
            norm = math.sqrt(sum(v * v for v in raw))
            w, x, y, z = (v / norm for v in raw)
            payload = fixture("pose-estimate.valid.json")
            payload["estimates"][0]["orientation"] = {"w": w, "x": x, "y": y, "z": z}
            validate_pose_estimate(payload)
            payload["estimates"][0]["orientation"] = {"w": w * 0.99, "x": x * 0.99, "y": y * 0.99, "z": z * 0.99}
            with self.assertRaises(ContractValidationError):
                validate_pose_estimate(payload)


class MatchTests(unittest.TestCase):
    def test_estimates_that_belong_to_the_detections_pass(self):
        check_estimates_match_detections(fixture("pose-estimate.valid.json"), detections(3))

    def test_another_frame_or_instant_is_refused(self):
        estimate = fixture("pose-estimate.valid.json")
        with self.assertRaises(ContractValidationError):
            check_estimates_match_detections(estimate, detections(3, frame_id="f-other"))
        with self.assertRaises(ContractValidationError):
            check_estimates_match_detections(estimate, detections(3, stamp="2026-01-02T10:00:01Z"))

    def test_an_estimate_that_points_past_the_detections_is_refused(self):
        with self.assertRaisesRegex(ContractValidationError, "points past"):
            check_estimates_match_detections(fixture("pose-estimate.valid.json"), detections(2))

    def test_an_invalid_side_is_refused_first(self):
        bad = detections(3)
        bad["box_unit"] = "furlong"
        with self.assertRaises(ContractValidationError):
            check_estimates_match_detections(fixture("pose-estimate.valid.json"), bad)


if __name__ == "__main__":
    unittest.main()
