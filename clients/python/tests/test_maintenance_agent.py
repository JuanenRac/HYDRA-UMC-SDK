# =============================================================================
# HYDRA-UMC-SDK - Tests of the snapshot, proposal and canary result contracts
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import copy
import json
import unittest
from pathlib import Path

from hydra_umc_sdk.validation import ContractValidationError, validate

FIXTURES = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1"


def _fixture(stem: str) -> dict:
    return json.loads((FIXTURES / f"{stem}.valid.json").read_text(encoding="utf-8"))


class NodeSnapshotTests(unittest.TestCase):
    def test_the_fixture_and_a_snapshot_without_host_checks_are_valid(self):
        snapshot = _fixture("node-snapshot")
        validate("NodeSnapshot", snapshot)
        del snapshot["hostHealth"]
        validate("NodeSnapshot", snapshot)

    def test_systemd_never_asked_is_null_and_still_valid(self):
        snapshot = _fixture("node-snapshot")
        snapshot["systemdAvailable"] = None
        snapshot["serviceHealth"] = []
        validate("NodeSnapshot", snapshot)

    def test_an_incident_inside_is_checked_as_an_incident(self):
        snapshot = _fixture("node-snapshot")
        snapshot["incidents"][0]["severity"] = "fatal"
        with self.assertRaises(ContractValidationError):
            validate("NodeSnapshot", snapshot)

    def test_a_field_outside_the_contract_is_refused_at_every_level(self):
        for path in ((), ("projects", 0), ("serviceHealth", 0), ("httpHealth", 0), ("hostHealth",), ("hostHealth", "thermal"), ("hostHealth", "disks", 0), ("hostHealth", "backups")):
            snapshot = _fixture("node-snapshot")
            holder = snapshot
            for key in path:
                holder = holder[key]
            holder["extra"] = 1
            with self.assertRaises(ContractValidationError, msg=str(path)):
                validate("NodeSnapshot", snapshot)

    def test_readings_the_machine_could_not_give_are_null(self):
        snapshot = _fixture("node-snapshot")
        snapshot["hostHealth"]["thermal"].update({"celsius": None, "throttledRaw": None, "vcgencmdAvailable": False})
        snapshot["hostHealth"]["disks"][0].update({"freeBytes": None, "totalBytes": None, "freePercent": None, "error": "OSError"})
        snapshot["hostHealth"]["backups"] = None
        validate("NodeSnapshot", snapshot)

    def test_numbers_that_cannot_be_true_are_refused(self):
        for mutate in (lambda s: s["hostHealth"]["disks"][0].update(freePercent=-1), lambda s: s["hostHealth"]["disks"][0].update(freeBytes=True),
                       lambda s: s["httpHealth"][0].update(statusCode=99), lambda s: s["httpHealth"][0].update(statusCode="200"),
                       lambda s: s["hostHealth"]["backups"].update(count=1.5)):
            snapshot = _fixture("node-snapshot")
            mutate(snapshot)
            with self.assertRaises(ContractValidationError):
                validate("NodeSnapshot", snapshot)


class ChangeProposalTests(unittest.TestCase):
    def test_a_pending_proposal_has_no_decision_fields(self):
        proposal = _fixture("change-proposal")
        for name in ("decidedBy", "decidedAt", "decisionReason", "approvedContentDigest", "allowProtectedPaths", "approvalExpiresAt", "approvedBaseCommit", "approvalSignature", "generatedBy"):
            del proposal[name]
        proposal["status"] = "pending"
        validate("ChangeProposal", proposal)

    def test_an_approved_proposal_with_null_optional_fields_is_valid(self):
        proposal = _fixture("change-proposal")
        proposal.update({"decisionReason": None, "approvalExpiresAt": None, "approvedBaseCommit": None, "approvalSignature": None, "generatedBy": "model-x"})
        validate("ChangeProposal", proposal)

    def test_the_digest_must_be_a_lowercase_sha256(self):
        for bad in ("A" * 64, "a" * 63, "g" * 64, 5):
            proposal = _fixture("change-proposal")
            proposal["approvedContentDigest"] = bad
            with self.assertRaises(ContractValidationError, msg=str(bad)):
                validate("ChangeProposal", proposal)

    def test_an_empty_diff_or_rationale_is_refused(self):
        for name in ("diff", "rationale", "description", "projectName"):
            proposal = _fixture("change-proposal")
            proposal[name] = ""
            with self.assertRaises(ContractValidationError, msg=name):
                validate("ChangeProposal", proposal)


class CanaryDeployResultTests(unittest.TestCase):
    def test_every_stage_is_accepted_and_others_are_not(self):
        for stage in ("staged", "diff_applied", "build_verified", "diff_committed", "promoted", "rolled_back"):
            result = _fixture("canary-deploy-result")
            result["stageReached"] = stage
            validate("CanaryDeployResult", result)
        result = _fixture("canary-deploy-result")
        result["stageReached"] = "done"
        with self.assertRaises(ContractValidationError):
            validate("CanaryDeployResult", result)

    def test_the_paths_are_optional_and_nullable(self):
        result = _fixture("canary-deploy-result")
        del result["backupPath"]
        del result["patchPath"]
        validate("CanaryDeployResult", result)
        result["backupPath"] = None
        validate("CanaryDeployResult", result)

    def test_an_empty_build_output_is_valid_a_missing_one_is_not(self):
        result = _fixture("canary-deploy-result")
        result["buildOutput"] = ""
        validate("CanaryDeployResult", result)
        del result["buildOutput"]
        with self.assertRaises(ContractValidationError):
            validate("CanaryDeployResult", result)

    def test_the_mock_server_serves_the_three_contracts(self):
        from hydra_umc_sdk.mock_server import EXAMPLE_PAYLOADS

        for name in ("NodeSnapshot", "ChangeProposal", "CanaryDeployResult"):
            validate(name, copy.deepcopy(EXAMPLE_PAYLOADS[name]))


if __name__ == "__main__":
    unittest.main()
