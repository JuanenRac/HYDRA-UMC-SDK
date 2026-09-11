# =============================================================================
# HYDRA-UMC-SDK - T07/I60 scenario comparison tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import copy
import unittest

from hydra_umc_sdk.scenario import ContractValidationError, compare_runs


def _before(**over):
    run = {
        "schema_version": "1.0",
        "scenario_id": "dev-server/I60/base-moved",
        "run_id": "run-before-1",
        "base_fingerprint": "base-A",
        "phase": "before",
        "repro_case": "malformed-origin-xyz",
        "observed": {"outcome": "reproduced", "exit_code": 1, "evidence": "assert failed at line 42"},
        "timestamp_utc": "2026-01-02T08:00:00Z",
    }
    run.update(over)
    return run


def _after(**over):
    run = {
        "schema_version": "1.0",
        "scenario_id": "dev-server/I60/base-moved",
        "run_id": "run-after-1",
        "base_fingerprint": "base-B",
        "phase": "after",
        "repro_case": "malformed-origin-xyz",
        "observed": {"outcome": "not-reproduced", "exit_code": 0, "evidence": "suite green"},
        "timestamp_utc": "2026-01-02T09:00:00Z",
    }
    run.update(over)
    return run


class CompareRunsTests(unittest.TestCase):
    def test_genuine_fix_is_regression_fixed_and_promotable(self):
        c = compare_runs(_before(), _after())
        self.assertEqual(c.verdict, "regression-fixed")
        self.assertTrue(c.is_promotable)
        self.assertEqual(c.scenario_id, "dev-server/I60/base-moved")
        self.assertEqual((c.before_run_id, c.after_run_id), ("run-before-1", "run-after-1"))

    def test_base_unchanged_is_apparent_success_never_promotable(self):
        c = compare_runs(_before(base_fingerprint="base-X"), _after(base_fingerprint="base-X"))
        self.assertEqual(c.verdict, "apparent-success")
        self.assertFalse(c.is_promotable)
        self.assertIn("unchanged", c.reason)

    def test_still_reproducing_after_is_still_broken(self):
        c = compare_runs(_before(), _after(observed={"outcome": "reproduced", "exit_code": 1}))
        self.assertEqual(c.verdict, "still-broken")
        self.assertFalse(c.is_promotable)

    def test_after_run_errored_is_inconclusive(self):
        c = compare_runs(_before(), _after(observed={"outcome": "error", "evidence": "toolchain missing"}))
        self.assertEqual(c.verdict, "inconclusive")

    def test_evidence_for_a_different_repro_case_is_inconclusive(self):
        c = compare_runs(_before(), _after(repro_case="some-other-case"))
        self.assertEqual(c.verdict, "inconclusive")
        self.assertIn("different repro case", c.reason)

    def test_different_scenario_id_is_inconclusive(self):
        c = compare_runs(_before(), _after(scenario_id="dev-server/I60/other"))
        self.assertEqual(c.verdict, "inconclusive")

    def test_phases_out_of_order_is_inconclusive(self):
        c = compare_runs(_before(phase="after"), _after(phase="before"))
        self.assertEqual(c.verdict, "inconclusive")

    def test_before_never_reproduced_is_inconclusive(self):
        c = compare_runs(_before(observed={"outcome": "not-reproduced"}), _after())
        self.assertEqual(c.verdict, "inconclusive")
        self.assertIn("nothing to have fixed", c.reason)

    def test_a_malformed_run_is_rejected(self):
        bad = _after()
        bad["observed"]["outcome"] = "maybe"
        with self.assertRaises(ContractValidationError):
            compare_runs(_before(), bad)

    def test_to_dict_carries_the_promotable_flag(self):
        d = compare_runs(_before(), _after()).to_dict()
        self.assertEqual(d["verdict"], "regression-fixed")
        self.assertTrue(d["is_promotable"])

    def test_inputs_are_not_mutated(self):
        b, a = _before(), _after()
        b_copy, a_copy = copy.deepcopy(b), copy.deepcopy(a)
        compare_runs(b, a)
        self.assertEqual(b, b_copy)
        self.assertEqual(a, a_copy)


if __name__ == "__main__":
    unittest.main()
