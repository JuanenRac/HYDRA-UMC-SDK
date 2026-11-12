# =============================================================================
# HYDRA-UMC-SDK - Tests of the Kinematics contract
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""contracts/kinematics.json: the canonical document, its schema and its fixtures, and the copies the apps keep of its ranges."""
from __future__ import annotations

import copy
import json
import math
import unittest
from pathlib import Path

from hydra_umc_sdk.kinematics import MAX_CHAIN_JOINTS, validate_kinematics
from hydra_umc_sdk.validation import ContractValidationError, validate

try:
    import jsonschema
except ImportError:  # the optional package
    jsonschema = None

ROOT = Path(__file__).resolve().parents[3]
CANONICAL = ROOT / "contracts" / "kinematics.json"
SCHEMA = ROOT / "contracts" / "json-schema" / "v1" / "kinematics.schema.json"
FIXTURES = ROOT / "conformance" / "fixtures" / "v1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class KinematicsDocumentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = load(CANONICAL)

    def refused(self, mutate) -> None:
        document = copy.deepcopy(self.document)
        mutate(document)
        with self.assertRaises(ContractValidationError):
            validate_kinematics(document)

    def test_the_canonical_document_passes(self) -> None:
        validate_kinematics(self.document)
        validate("Kinematics", self.document)

    def test_the_fixtures_get_their_verdict(self) -> None:
        validate("Kinematics", load(FIXTURES / "kinematics.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("Kinematics", load(FIXTURES / "kinematics.invalid.json"))

    @unittest.skipIf(jsonschema is None, "the optional jsonschema package is not installed")
    def test_the_schema_and_the_validator_agree(self) -> None:
        validator = jsonschema.Draft202012Validator(load(SCHEMA))
        self.assertTrue(validator.is_valid(self.document))
        self.assertTrue(validator.is_valid(load(FIXTURES / "kinematics.valid.json")))
        self.assertFalse(validator.is_valid(load(FIXTURES / "kinematics.invalid.json")))

    def test_every_range_is_ordered_and_every_home_pose_is_inside_it(self) -> None:
        for name, model in self.document["models"].items():
            self.assertEqual(set(model["limits"]), set(model["home"]), name)
            for joint, (low, high) in model["limits"].items():
                self.assertLessEqual(low, high, f"{name} {joint}")
                self.assertTrue(low <= model["home"][joint] <= high, f"{name} {joint}: home outside the range")

    def test_a_universal_robots_chain_is_what_its_numbers_say(self) -> None:
        checked = 0
        for name, model in self.document["models"].items():
            chain = model.get("chain")
            if not chain:
                continue
            p, joints = chain["parameters"], chain["joints"]
            wrist = p["d4"] - p["shoulderOffset"] - p["elbowOffset"]
            self.assertEqual(len(joints), 6, name)
            self.assertAlmostEqual(joints[0]["pos"][2], p["d1"], places=9)
            self.assertAlmostEqual(joints[1]["pos"][1], p["shoulderOffset"], places=9)
            self.assertAlmostEqual(joints[2]["pos"][1], p["elbowOffset"], places=9)
            self.assertAlmostEqual(joints[2]["pos"][2], -p["a2"], places=9)
            self.assertAlmostEqual(joints[3]["pos"][2], -p["a3"], places=9)
            self.assertAlmostEqual(joints[4]["pos"][1], wrist, places=9)
            self.assertAlmostEqual(joints[5]["pos"][2], p["d5"], places=9)
            self.assertAlmostEqual(joints[1]["rpy"][1], math.pi / 2, places=9)
            self.assertAlmostEqual(joints[3]["rpy"][1], math.pi / 2, places=9)
            for joint in joints:
                self.assertAlmostEqual(math.sqrt(sum(v * v for v in joint["axis"])), 1.0, places=9)
            checked += 1
        self.assertEqual(checked, 3)

    def test_each_refusal_one_field_at_a_time(self) -> None:
        first = next(iter(self.document["models"]))
        ur = "UR5 (6-DOF)"
        self.refused(lambda d: d.update(schema_version="2.0"))
        self.refused(lambda d: d.update(extra=1))
        self.refused(lambda d: d.update(models={}))
        self.refused(lambda d: d.update(note=3))
        self.refused(lambda d: d["models"][first].update(extra=1))
        self.refused(lambda d: d["models"][first]["limits"].update(j0=[0, 1]))
        self.refused(lambda d: d["models"][first]["limits"].update(j1=[5, -5]))
        self.refused(lambda d: d["models"][first]["limits"].update(j1=[0, 1, 2]))
        self.refused(lambda d: d["models"][first]["limits"].update(j1=[0, True]))
        self.refused(lambda d: d["models"][first]["home"].update(j1="0"))
        self.refused(lambda d: d["models"][first]["home"].update(j1=float("nan")))
        self.refused(lambda d: d["models"][first].update(limits={}))
        self.refused(lambda d: d["models"][ur]["chain"].update(convention="dh"))
        self.refused(lambda d: d["models"][ur]["chain"].update(joints=[]))
        self.refused(lambda d: d["models"][ur]["chain"].update(joints=d["models"][ur]["chain"]["joints"] * 2))
        self.refused(lambda d: d["models"][ur]["chain"]["joints"][0].update(axis=[0, 1]))
        self.refused(lambda d: d["models"][ur]["chain"]["joints"][0].update(pos=[0, 0, "x"]))
        self.refused(lambda d: d["models"][ur]["chain"]["joints"][0].pop("rpy"))
        self.refused(lambda d: d["models"][ur]["chain"]["joints"][0].update(extra=0))
        self.refused(lambda d: d["models"][ur]["chain"].update(parameters={"d1": "0.1"}))
        self.refused(lambda d: d["models"][ur]["chain"].update(extra=1))
        self.assertEqual(MAX_CHAIN_JOINTS, 9)

    def test_a_document_that_is_not_an_object_is_refused(self) -> None:
        for payload in ([], "x", None, 3):
            with self.assertRaises(ContractValidationError):
                validate_kinematics(payload)  # type: ignore[arg-type]

    def test_the_ranges_equal_the_copies_of_the_apps_when_they_are_next_to_this_one(self) -> None:
        copies = [
            ROOT.parent / "HYDRA-UMC-STUDIO" / "src" / "data" / "kinematicData.json",
            ROOT.parent / "HYDRA-UMC-SERVER" / "src" / "data" / "kinematicData.json",
            ROOT.parent / "HYDRA-UMC-SUITE" / "assets" / "kinematic_data.json",
        ]
        present = [path for path in copies if path.is_file()]
        if not present:
            self.skipTest("no app repository is next to this checkout")
        for path in present:
            theirs = load(path)["models"]
            ours = {name: {"limits": m["limits"], "home": m["home"]} for name, m in self.document["models"].items()}
            self.assertEqual(theirs, ours, str(path))


if __name__ == "__main__":
    unittest.main()
