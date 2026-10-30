# =============================================================================
# HYDRA-UMC-SDK - Python validator vs. normative JSON Schema (differential)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The Python validator is hand written, the Go, TypeScript and Rust clients
validate with the JSON Schemas themselves. When the two disagree about the same
payload, a service in one language accepts what a service in another rejects.
This test runs both on the conformance fixtures, on a set of boundary cases and
on the real manifests of the sibling repositories (when they are checked out
next to this one) and requires the same verdict.

It needs the optional `jsonschema` package and is skipped without it.
"""
import copy
import json
import unittest
from pathlib import Path

from hydra_umc_sdk.validation import ContractValidationError, validate

try:
    import jsonschema
except ImportError:  # pragma: no cover - optional test dependency
    jsonschema = None

REPO = Path(__file__).resolve().parents[3]
SCHEMAS = REPO / "contracts" / "json-schema" / "v1"
FIXTURES = REPO / "conformance" / "fixtures" / "v1"

CONTRACT_FILES = {
    "DeviceDescriptor": "device-descriptor",
    "HealthReport": "health-report",
    "SafetyState": "safety-state",
    "UpdateManifest": "update-manifest",
    "EventEnvelope": "event-envelope",
    "ScenarioOutcome": "scenario-outcome",
    "Operation": "operation",
    "Capability": "capability",
    "ServerDiscovery": "server-discovery",
    "ProjectManifest": "project-manifest",
    "ConnectionEvent": "connection-event",
    "ConnectionClient": "connection-client",
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@unittest.skipIf(jsonschema is None, "the optional jsonschema package is not installed")
class SchemaDifferentialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validators = {}
        for contract, stem in CONTRACT_FILES.items():
            schema = _load(SCHEMAS / f"{stem}.schema.json")
            cls.validators[contract] = jsonschema.Draft202012Validator(schema)

    def verdicts(self, contract, payload):
        schema_ok = self.validators[contract].is_valid(payload)
        try:
            validate(contract, payload)
            python_ok = True
        except ContractValidationError:
            python_ok = False
        return schema_ok, python_ok

    def assert_same(self, contract, payload, label):
        schema_ok, python_ok = self.verdicts(contract, payload)
        self.assertEqual(
            schema_ok, python_ok,
            f"{contract} / {label}: the JSON Schema says {'valid' if schema_ok else 'invalid'}, "
            f"the Python validator says {'valid' if python_ok else 'invalid'}",
        )

    def test_conformance_fixtures_get_the_same_verdict(self):
        for contract, stem in CONTRACT_FILES.items():
            for kind in ("valid", "invalid"):
                path = FIXTURES / f"{stem}.{kind}.json"
                if path.exists():
                    self.assert_same(contract, _load(path), path.name)

    def test_boundary_cases_get_the_same_verdict(self):
        update = _load(FIXTURES / "update-manifest.valid.json")
        device = _load(FIXTURES / "device-descriptor.valid.json")
        event = _load(FIXTURES / "event-envelope.valid.json")
        operation = _load(FIXTURES / "operation.valid.json")
        manifest = _load(FIXTURES / "project-manifest.valid.json")

        def changed(base, **over):
            payload = copy.deepcopy(base)
            payload.update(over)
            return payload

        cases = [
            ("UpdateManifest", changed(update, artifact_url="http://example.com/a.zip"), "http artifact url"),
            ("UpdateManifest", changed(update, artifact_url="https://example.com/a.zip"), "https artifact url"),
            ("DeviceDescriptor", changed(device, interfaces=[""]), "empty interface name"),
            ("DeviceDescriptor", changed(device, interfaces=["can0"]), "interface name"),
            ("EventEnvelope", changed(event, correlation_id=5), "numeric correlation id"),
            ("EventEnvelope", changed(event, correlation_id="abc"), "string correlation id"),
            ("ProjectManifest", changed(manifest, unexpected="x"), "extra manifest field"),
            ("ProjectManifest", changed(manifest, deployment_target="dev-server"), "dev-server target"),
            ("ProjectManifest", changed(manifest, ecosystem="URTC"), "URTC ecosystem"),
            ("ProjectManifest", changed(manifest, ecosystem="OTHER"), "unknown ecosystem"),
            ("ProjectManifest", changed(manifest, deployment_target_note="why"), "target note"),
            ("ProjectManifest", changed(manifest, service={"port": 8080, "health_path": "/h", "systemd_unit": "u.service"}), "service block"),
            ("ProjectManifest", changed(manifest, service={"port": "8080"}), "service port as text"),
            ("ProjectManifest", changed(manifest, service={"other": 1}), "unknown service key"),
            ("ProjectManifest", changed(manifest, evidence="bench"), "evidence bench"),
            ("ProjectManifest", changed(manifest, evidence="magic"), "unknown evidence"),
            ("ProjectManifest", changed(manifest, evidence=5), "numeric evidence"),
            ("ProjectManifest", changed(manifest, hardware_bound=False), "hardware_bound false"),
            ("ProjectManifest", changed(manifest, hardware_bound="no"), "hardware_bound as text"),
            ("ProjectManifest", changed(manifest, depends_on=["HYDRA-UMC-OS"]), "depends_on one name"),
            ("ProjectManifest", changed(manifest, depends_on=[]), "depends_on empty"),
            ("ProjectManifest", changed(manifest, depends_on=["HYDRA-UMC-OS", "HYDRA-UMC-OS"]), "depends_on repeated"),
            ("ProjectManifest", changed(manifest, depends_on=["not a name"]), "depends_on bad name"),
            ("ProjectManifest", changed(manifest, depends_on="HYDRA-UMC-OS"), "depends_on as text"),
            ("ConnectionEvent", {"schema_version": "1.0", "id": 1, "at_utc": "2026-01-01T10:00:00Z", "action": "login", "client_kind": "studio", "client_id": "0123456789abcdef"}, "minimal connection event"),
            ("ConnectionEvent", {"schema_version": "1.0", "id": 1, "at_utc": "2026-01-01T10:00:00Z", "action": "login", "client_kind": "studio", "client_id": "0123456789abcdef", "password": "x"}, "password in an event"),
            ("ConnectionEvent", {"schema_version": "1.0", "id": 0, "at_utc": "2026-01-01T10:00:00Z", "action": "login", "client_kind": "studio", "client_id": "0123456789abcdef"}, "event id zero"),
            ("ConnectionEvent", {"schema_version": "1.0", "id": 1, "at_utc": "2026-01-01T10:00:00Z", "action": "login", "client_kind": "toaster", "client_id": "0123456789abcdef"}, "client kind outside the list"),
            ("ConnectionEvent", {"schema_version": "1.0", "id": 1, "at_utc": "2026-01-01T10:00:00Z", "action": "login", "client_kind": "studio", "client_id": "ABC"}, "client id not a hash"),
            ("ConnectionEvent", {"schema_version": "1.0", "id": 1, "at_utc": "2026-01-01T10:00:00Z", "action": "login", "client_kind": "studio", "client_id": "0123456789abcdef", "two_factor": 1}, "two factor as a number"),
            ("ConnectionEvent", {"schema_version": "1.0", "id": 1, "at_utc": "2026-01-01T10:00:00Z", "action": "login", "client_kind": "studio", "client_id": "0123456789abcdef", "app_version": "1 2"}, "app version with a space"),
            ("ConnectionClient", {"schema_version": "1.0", "id": "0123456789abcdef", "kind": "voice", "first_seen_utc": "2026-01-01T10:00:00Z", "last_seen_utc": "2026-01-01T10:00:00Z", "active_sessions": 0, "logins_ok": 0, "logins_failed": 0}, "minimal client"),
            ("ConnectionClient", {"schema_version": "1.0", "id": "0123456789abcdef", "kind": "voice", "first_seen_utc": "2026-01-01T10:00:00Z", "last_seen_utc": "2026-01-01T10:00:00Z", "active_sessions": -1, "logins_ok": 0, "logins_failed": 0}, "negative sessions"),
            ("ConnectionClient", {"schema_version": "1.0", "id": "0123456789abcdef", "kind": "voice", "first_seen_utc": "2026-01-01T10:00:00Z", "last_seen_utc": "2026-01-01T10:00:00Z", "active_sessions": "1", "logins_ok": 0, "logins_failed": 0}, "sessions as text"),
            ("ConnectionClient", {"schema_version": "1.0", "id": "0123456789abcdef", "kind": "voice", "first_seen_utc": "2026-01-01T10:00:00Z", "last_seen_utc": "2026-01-01T10:00:00Z", "active_sessions": 0, "logins_ok": 0, "logins_failed": 0, "cookie": "x"}, "cookie in a client"),
            ("ConnectionClient", {"schema_version": "1.0", "id": "0123456789abcdef", "kind": "fridge", "first_seen_utc": "2026-01-01T10:00:00Z", "last_seen_utc": "2026-01-01T10:00:00Z", "active_sessions": 0, "logins_ok": 0, "logins_failed": 0}, "kind outside the list"),
            ("ConnectionClient", {"schema_version": "1.0", "id": "0123456789abcdef", "kind": "voice", "last_seen_utc": "2026-01-01T10:00:00Z", "active_sessions": 0, "logins_ok": 0, "logins_failed": 0}, "no first seen"),
        ]
        result = copy.deepcopy(operation.get("result", {"run_id": "r", "origin": "real", "observers_enabled": True, "outcome": "success"}))
        result["outcome_reason"] = 5
        cases.append(("Operation", changed(operation, result=result), "numeric outcome_reason"))
        for contract, payload, label in cases:
            self.assert_same(contract, payload, label)

    def test_real_manifests_of_sibling_repositories_validate_in_both(self):
        workspace = REPO.parent
        found = 0
        for manifest_path in sorted(list(workspace.glob("*/hydra-umc.project.json")) + list(workspace.glob("*/urtc.project.json"))):
            if not (manifest_path.parent.name.startswith(("HYDRA-UMC", "URTC"))):
                continue
            try:
                payload = _load(manifest_path)
            except (OSError, ValueError):
                continue
            found += 1
            self.assert_same("ProjectManifest", payload, str(manifest_path.relative_to(workspace)))
        if not found:
            self.skipTest("no sibling repositories next to this checkout")


if __name__ == "__main__":
    unittest.main()
