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

    def test_rejects_non_https_update_artifact(self):
        with self.assertRaises(ContractValidationError):
            validate("UpdateManifest", {"schema_version":"1.0","project":"os","version":"0.0.2","artifact_url":"http://example.invalid/a","sha256":"a" * 64})


if __name__ == "__main__":
    unittest.main()
