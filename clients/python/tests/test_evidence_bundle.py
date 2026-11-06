# =============================================================================
# HYDRA-UMC-SDK - Evidence bundle contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""`EvidenceBundle`: the shape, the checksum and the sealing agree with the schema and with what the development node reads."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from hydra_umc_sdk import (
    ContractValidationError,
    bundle_checksum,
    bundle_matches_checksum,
    seal_bundle,
    validate,
)

FIXTURES = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1"


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class EvidenceBundleTests(unittest.TestCase):
    def test_the_fixtures(self):
        validate("EvidenceBundle", fixture("evidence-bundle.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("EvidenceBundle", fixture("evidence-bundle.invalid.json"))

    def test_the_valid_fixture_carries_the_checksum_of_its_content(self):
        bundle = fixture("evidence-bundle.valid.json")
        self.assertTrue(bundle_matches_checksum(bundle))
        bundle["impact"] = "something else"
        self.assertFalse(bundle_matches_checksum(bundle))

    def test_the_checksum_ignores_its_own_field_and_the_order_of_the_keys(self):
        bundle = fixture("evidence-bundle.valid.json")
        reordered = dict(reversed(list(bundle.items())))
        reordered["checksum"] = "anything"
        self.assertEqual(bundle_checksum(reordered), bundle["checksum"])

    def test_sealing_fills_the_checksum_and_validates(self):
        bundle = fixture("evidence-bundle.valid.json")
        bundle["failedTests"] = ["tests/other.test.ts"]
        sealed = seal_bundle(bundle)
        self.assertNotEqual(sealed["checksum"], fixture("evidence-bundle.valid.json")["checksum"])
        self.assertTrue(bundle_matches_checksum(sealed))
        bundle["reproductionSteps"] = []
        with self.assertRaises(ContractValidationError):
            seal_bundle(bundle)

    def test_every_required_field_is_named_when_missing_and_extras_are_refused(self):
        for name in list(fixture("evidence-bundle.valid.json")):
            payload = fixture("evidence-bundle.valid.json")
            del payload[name]
            with self.assertRaisesRegex(ContractValidationError, name):
                validate("EvidenceBundle", payload)
        with self.assertRaises(ContractValidationError):
            validate("EvidenceBundle", fixture("evidence-bundle.valid.json") | {"extra": 1})

    def test_the_types_are_never_converted(self):
        for name, value in (("componentVersions", []), ("relevantManifests", "x"), ("failedTests", [1]), ("impact", ""), ("checksum", 5), ("date", "yesterday"), ("localValidationResult", None)):
            payload = copy.deepcopy(fixture("evidence-bundle.valid.json"))
            payload[name] = value
            with self.assertRaises(ContractValidationError, msg=name):
                validate("EvidenceBundle", payload)


if __name__ == "__main__":
    unittest.main()
