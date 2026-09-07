# =============================================================================
# HYDRA-UMC-SDK - Contract validation unit tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

import json
import unittest
from pathlib import Path

from hydra_umc_sdk.validation import ContractValidationError, validate


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "conformance" / "fixtures" / "v1"


class ValidationTests(unittest.TestCase):
    def fixture(self, name: str):
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def test_accepts_device_descriptor(self):
        validate("DeviceDescriptor", self.fixture("device-descriptor.valid.json"))

    def test_accepts_health_report(self):
        validate("HealthReport", self.fixture("health-report.valid.json"))

    def test_rejects_unsafe_health_state(self):
        with self.assertRaises(ContractValidationError):
            validate("HealthReport", self.fixture("health-report.invalid.json"))

    def test_rejects_bad_update_digest(self):
        with self.assertRaises(ContractValidationError):
            validate("UpdateManifest", {"schema_version": "1.0", "project": "HYDRA-UMC-OS", "version": "0.0.2", "artifact_url": "https://example.invalid/a", "sha256": "bad"})

    def test_accepts_hydra_umc_os_producer_fixtures(self):
        producer = FIXTURES / "producers" / "hydra-umc-os"
        validate("DeviceDescriptor", json.loads((producer / "device-descriptor.json").read_text(encoding="utf-8")))
        validate("HealthReport", json.loads((producer / "health-report.json").read_text(encoding="utf-8")))

    def test_accepts_event_envelope(self):
        validate("EventEnvelope", self.fixture("event-envelope.valid.json"))

    def test_rejects_negative_event_sequence(self):
        with self.assertRaises(ContractValidationError):
            validate("EventEnvelope", {"schema_version":"1.0","event_id":"e","type":"x","source":"os","timestamp_utc":"2026-08-26T12:00:00Z","sequence":-1})

    def test_rejects_boolean_event_sequence(self):
        with self.assertRaises(ContractValidationError):
            validate("EventEnvelope", {"schema_version":"1.0","event_id":"e","type":"x","source":"os","timestamp_utc":"2026-08-26T12:00:00Z","sequence":True})

    def test_rejects_invalid_health_timestamp(self):
        with self.assertRaises(ContractValidationError):
            validate("HealthReport", {"schema_version":"1.0","state":"READY","timestamp_utc":"2026-02-30T12:00:00Z","checks":{}})

    def test_rejects_boolean_server_discovery_counter(self):
        with self.assertRaises(ContractValidationError):
            validate("ServerDiscovery", {"schema_version":"1.0","product":"server","remoteApiVersion":1,"appVersion":"0.0.1","hostname":"host","controllerCount":True,"robotCount":0,"uptimeSeconds":0})

    def test_rejects_non_https_update_artifact(self):
        with self.assertRaises(ContractValidationError):
            validate("UpdateManifest", {"schema_version":"1.0","project":"os","version":"0.0.2","artifact_url":"http://example.invalid/a","sha256":"a" * 64})

    def test_rejects_https_update_artifact_without_a_hostname(self):
        with self.assertRaises(ContractValidationError):
            validate("UpdateManifest", {"schema_version":"1.0","project":"os","version":"0.0.2","artifact_url":"https:///artifact.deb","sha256":"a" * 64})

    def test_accepts_server_discovery(self):
        validate("ServerDiscovery", self.fixture("server-discovery.valid.json"))

    def test_rejects_invalid_server_discovery_version(self):
        with self.assertRaises(ContractValidationError):
            validate("ServerDiscovery", {"schema_version":"1.0","product":"server","remoteApiVersion":0,"appVersion":"0.0.1","hostname":"host","controllerCount":0,"robotCount":0,"uptimeSeconds":0})

    def test_accepts_project_manifest(self):
        validate("ProjectManifest", self.fixture("project-manifest.valid.json"))

    def test_rejects_unsupported_project_manifest_role(self):
        with self.assertRaises(ContractValidationError):
            validate("ProjectManifest", self.fixture("project-manifest.invalid.json"))

    def _valid_project_manifest(self) -> dict:
        return dict(self.fixture("project-manifest.valid.json"))

    def test_rejects_wrong_ecosystem(self):
        payload = self._valid_project_manifest()
        payload["ecosystem"] = "OTHER"
        with self.assertRaises(ContractValidationError):
            validate("ProjectManifest", payload)

    def test_rejects_malformed_name(self):
        payload = self._valid_project_manifest()
        payload["name"] = "not-a-real-project-name"
        with self.assertRaises(ContractValidationError):
            validate("ProjectManifest", payload)

    def test_rejects_non_semver_version(self):
        payload = self._valid_project_manifest()
        payload["version"] = "v1"
        with self.assertRaises(ContractValidationError):
            validate("ProjectManifest", payload)

    def test_rejects_unsupported_deployment_target(self):
        payload = self._valid_project_manifest()
        payload["deployment_target"] = "cloud"
        with self.assertRaises(ContractValidationError):
            validate("ProjectManifest", payload)

    def test_rejects_unsupported_maturity(self):
        payload = self._valid_project_manifest()
        payload["maturity"] = "beta"
        with self.assertRaises(ContractValidationError):
            validate("ProjectManifest", payload)

    def test_rejects_empty_technologies(self):
        payload = self._valid_project_manifest()
        payload["technologies"] = []
        with self.assertRaises(ContractValidationError):
            validate("ProjectManifest", payload)

    def test_rejects_duplicate_technologies(self):
        payload = self._valid_project_manifest()
        payload["technologies"] = ["Python", "Python"]
        with self.assertRaises(ContractValidationError):
            validate("ProjectManifest", payload)

    def test_accepts_null_parent(self):
        payload = self._valid_project_manifest()
        payload["parent"] = None
        validate("ProjectManifest", payload)

    def test_rejects_empty_string_parent(self):
        payload = self._valid_project_manifest()
        payload["parent"] = ""
        with self.assertRaises(ContractValidationError):
            validate("ProjectManifest", payload)

    def test_accepts_empty_build_and_notes(self):
        payload = self._valid_project_manifest()
        payload["build"] = ""
        payload["notes"] = ""
        validate("ProjectManifest", payload)

    def test_rejects_native_version_missing_pattern(self):
        payload = self._valid_project_manifest()
        payload["native_version"] = {"file": "CHANGELOG.md"}
        with self.assertRaises(ContractValidationError):
            validate("ProjectManifest", payload)

    def test_accepts_native_version_component_pattern(self):
        payload = self._valid_project_manifest()
        payload["native_version"] = {
            "file": "version.go",
            "pattern": {"major": "MAJOR", "minor": "MINOR", "patch": "PATCH"},
        }
        validate("ProjectManifest", payload)

    def test_rejects_unknown_contract_name(self):
        with self.assertRaises(ContractValidationError):
            validate("NotARealContract", self._valid_project_manifest())

    def test_rejects_incompatible_schema_version(self):
        payload = self._valid_project_manifest()
        payload["schema_version"] = "2.0"
        with self.assertRaises(ContractValidationError):
            validate("ProjectManifest", payload)


if __name__ == "__main__":
    unittest.main()
