# =============================================================================
# HYDRA-UMC-SDK - T07/I60 scenario before/after comparison (reference consumer)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The shared T07/I60 check: given a `ScenarioOutcome` for the same fixed
reproduction scenario run BEFORE a candidate fix and one run AFTER it,
decide whether the fix actually closed the failure - and, above all,
refuse to call it fixed when nothing really changed.

`compare_runs()` is the reference consumer of the `ScenarioOutcome`
contract (`contracts/json-schema/v1/scenario-outcome.schema.json`). It is
the same "apparent success" control HYDRA-UMC-DEV-SERVER's own DS08 repair
cycle applies, published here so HYDRA-UMC-OPS-AGENT, DEV-SERVER and any
other promotion path judge a before/after pair identically.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .validation import ContractValidationError, validate

# The verdict vocabulary, most-to-least good:
#   regression-fixed   - the failure reproduced before, did not after, and
#                        the base genuinely moved between the two runs.
#   still-broken        - the failure still reproduces after the fix.
#   apparent-success    - the failure stopped reproducing but the base
#                        fingerprint is unchanged: nothing was actually
#                        applied, so this "pass" is meaningless (I60/T07).
#   inconclusive        - the pair cannot be compared: phases out of order,
#                        a different scenario_id or repro_case (evidence for
#                        the wrong case), the after-run errored, or the
#                        before-run never reproduced the failure in the
#                        first place.
VERDICTS = ("regression-fixed", "still-broken", "apparent-success", "inconclusive")


@dataclass(frozen=True)
class ScenarioComparison:
    verdict: str
    reason: str
    scenario_id: str
    before_run_id: str
    after_run_id: str

    @property
    def is_promotable(self) -> bool:
        """True only for a genuine `regression-fixed` - never for an
        `apparent-success`, which is the whole point of this check."""
        return self.verdict == "regression-fixed"

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "reason": self.reason,
            "scenario_id": self.scenario_id,
            "before_run_id": self.before_run_id,
            "after_run_id": self.after_run_id,
            "is_promotable": self.is_promotable,
        }


def compare_runs(before: dict[str, Any], after: dict[str, Any]) -> ScenarioComparison:
    """Compare a before/after `ScenarioOutcome` pair. Both payloads are
    validated against the contract first (a `ContractValidationError` is
    raised for a malformed one - callers pass real recorded runs, not
    hand-typed dicts)."""
    validate("ScenarioOutcome", before)
    validate("ScenarioOutcome", after)

    def result(verdict: str, reason: str) -> ScenarioComparison:
        return ScenarioComparison(
            verdict=verdict,
            reason=reason,
            scenario_id=before["scenario_id"],
            before_run_id=before["run_id"],
            after_run_id=after["run_id"],
        )

    if before["phase"] != "before" or after["phase"] != "after":
        return result("inconclusive", "the runs are not a before/after pair (check each run's phase)")
    if before["scenario_id"] != after["scenario_id"]:
        return result("inconclusive", "the two runs are for different scenarios")
    if before["repro_case"] != after["repro_case"]:
        return result(
            "inconclusive",
            "the after-run's evidence is for a different repro case than the before-run",
        )

    after_outcome = after["observed"]["outcome"]
    if after_outcome == "error":
        return result("inconclusive", "the after-run errored, so it proves nothing about the fix")
    if after_outcome == "reproduced":
        return result("still-broken", "the failure still reproduces after the candidate fix")

    # after_outcome == "not-reproduced" from here.
    if before["observed"]["outcome"] != "reproduced":
        return result(
            "inconclusive",
            "the before-run did not reproduce the failure, so there is nothing to have fixed",
        )
    if after["base_fingerprint"] == before["base_fingerprint"]:
        return result(
            "apparent-success",
            "the failure stopped reproducing but the base fingerprint is unchanged - "
            "nothing was actually applied",
        )
    return result(
        "regression-fixed",
        "the failure reproduced before, does not after, and the base genuinely moved between the two runs",
    )


__all__ = ["ScenarioComparison", "compare_runs", "VERDICTS", "ContractValidationError"]
