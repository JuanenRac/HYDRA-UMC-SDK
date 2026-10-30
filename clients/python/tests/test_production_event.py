# =============================================================================
# HYDRA-UMC-SDK - ProductionEvent contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import json
import unittest
from pathlib import Path

from hydra_umc_sdk import ContractValidationError, production_event_fields, validate

FIXTURES = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1"


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ProductionEventTests(unittest.TestCase):
    def test_the_fixtures_are_judged_as_their_names_say(self):
        validate("ProductionEvent", _fixture("production-event.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("ProductionEvent", _fixture("production-event.invalid.json"))

    def test_the_date_must_be_an_rfc_3339_date_time(self):
        for bad in ("yesterday", "2026-01-01", "2026-13-45T00:00:00Z", 5):
            with self.subTest(bad=bad), self.assertRaises(ContractValidationError):
                validate("ProductionEvent", dict(_fixture("production-event.valid.json"), at_utc=bad))

    def test_a_cycle_time_must_be_a_positive_finite_number_of_at_most_a_week(self):
        base = _fixture("production-event.valid.json")
        for good in (0.001, 1, 604800):
            validate("ProductionEvent", dict(base, cycle_time_s=good))
        for bad in (0, -1, 604801, float("nan"), float("inf"), True, "3", None):
            with self.subTest(bad=bad), self.assertRaises(ContractValidationError):
                validate("ProductionEvent", dict(base, cycle_time_s=bad))

    def test_good_is_a_boolean_and_nothing_else_can_be_added(self):
        base = _fixture("production-event.valid.json")
        for bad in (1, 0, "true", None):
            with self.subTest(bad=bad), self.assertRaises(ContractValidationError):
                validate("ProductionEvent", dict(base, good=bad))
        with self.assertRaises(ContractValidationError):
            validate("ProductionEvent", dict(base, operator="ana"))

    def test_the_source_and_the_job_are_short_identifiers(self):
        base = _fixture("production-event.valid.json")
        for field in ("source_id", "job_id"):
            for bad in ("", "a b", "x" * 65, 3):
                with self.subTest(field=field, bad=bad), self.assertRaises(ContractValidationError):
                    validate("ProductionEvent", dict(base, **{field: bad}))

    def test_the_reject_reason_is_limited(self):
        base = _fixture("production-event.valid.json")
        validate("ProductionEvent", dict(base, good=False, reject_reason="burr on the edge"))
        for bad in ("", "x" * 121, 4):
            with self.subTest(bad=bad), self.assertRaises(ContractValidationError):
                validate("ProductionEvent", dict(base, reject_reason=bad))

    def test_the_fields_of_the_data_lake_sample(self):
        base = _fixture("production-event.valid.json")
        self.assertEqual(production_event_fields(base), {"good": 1.0, "cycleTimeS": 42.5})
        self.assertEqual(production_event_fields(dict(base, good=False, cycle_time_s=7)), {"good": 0.0, "cycleTimeS": 7.0})
        with self.assertRaises(ContractValidationError):
            production_event_fields(dict(base, good="no"))


if __name__ == "__main__":
    unittest.main()
