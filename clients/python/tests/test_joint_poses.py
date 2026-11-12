# =============================================================================
# HYDRA-UMC-SDK - Tests of the JointPoses contract
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The answer of forward kinematics: its schema, its validator and its fixtures agree, and each rule has a case that breaks it."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from hydra_umc_sdk.joint_poses import MAX_POSES, validate_joint_poses
from hydra_umc_sdk.validation import ContractValidationError, validate

try:
    import jsonschema
except ImportError:  # the optional package
    jsonschema = None

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "contracts" / "json-schema" / "v1" / "joint-poses.schema.json"
FIXTURES = ROOT / "conformance" / "fixtures" / "v1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class JointPosesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = load(FIXTURES / "joint-poses.valid.json")

    def refused(self, mutate) -> None:
        document = copy.deepcopy(self.document)
        mutate(document)
        with self.assertRaises(ContractValidationError):
            validate_joint_poses(document)

    def test_the_fixtures_get_their_verdict(self) -> None:
        validate("JointPoses", self.document)
        with self.assertRaises(ContractValidationError):
            validate("JointPoses", load(FIXTURES / "joint-poses.invalid.json"))

    @unittest.skipIf(jsonschema is None, "the optional jsonschema package is not installed")
    def test_the_schema_and_the_validator_agree(self) -> None:
        validator = jsonschema.Draft202012Validator(load(SCHEMA))
        self.assertTrue(validator.is_valid(self.document))
        self.assertFalse(validator.is_valid(load(FIXTURES / "joint-poses.invalid.json")))

    def test_the_optional_fields_may_be_left_out(self) -> None:
        document = copy.deepcopy(self.document)
        del document["checked"], document["note"]
        validate_joint_poses(document)

    def test_a_field_missing_or_unknown_is_refused(self) -> None:
        self.refused(lambda d: d.pop("frame"))
        self.refused(lambda d: d.pop("poses"))
        self.refused(lambda d: d.update(surprise=1))
        self.refused(lambda d: d["poses"][0].update(surprise=1))
        self.refused(lambda d: d["poses"][0]["position"].pop("z"))
        self.refused(lambda d: d["poses"][0]["quaternion"].update(extra=0))

    def test_the_version_and_the_frame_are_the_declared_ones(self) -> None:
        self.refused(lambda d: d.update(schema_version="2.0"))
        self.refused(lambda d: d.update(frame="world"))
        self.refused(lambda d: d.update(checked="yes"))
        self.refused(lambda d: d.update(note=5))

    def test_the_list_of_poses_is_bounded_and_a_joint_appears_once(self) -> None:
        self.refused(lambda d: d.update(poses=[]))
        self.refused(lambda d: d.update(poses="none"))
        self.refused(lambda d: d.update(poses=[dict(d["poses"][0], joint=f"j{i}") for i in range(MAX_POSES + 1)]))
        self.refused(lambda d: d["poses"][1].update(joint=d["poses"][0]["joint"]))
        self.refused(lambda d: d["poses"][0].update(joint=""))
        self.refused(lambda d: d["poses"][0].update(joint=5))

    def test_numbers_are_finite_real_numbers(self) -> None:
        self.refused(lambda d: d["poses"][0]["position"].update(x=float("nan")))
        self.refused(lambda d: d["poses"][0]["position"].update(y=float("inf")))
        self.refused(lambda d: d["poses"][0]["position"].update(z=True))
        self.refused(lambda d: d["poses"][0]["position"].update(z="0.1"))

    def test_a_quaternion_has_to_be_a_unit_quaternion(self) -> None:
        self.refused(lambda d: d["poses"][1]["quaternion"].update(w=0.9))
        self.refused(lambda d: d["poses"][1]["quaternion"].update(w=0.0))
        document = copy.deepcopy(self.document)
        document["poses"][1]["quaternion"]["w"] = 1.000001  # inside the tolerance of 1e-5
        validate_joint_poses(document)


if __name__ == "__main__":
    unittest.main()
