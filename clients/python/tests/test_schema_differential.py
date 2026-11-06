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
    "ProductionEvent": "production-event",
    "EcosystemHealth": "ecosystem-health",
    "RobotLiveness": "robot-liveness",
    "CommandLifecycleEvent": "command-lifecycle-event",
    "VisualTargetRequest": "visual-target-request",
    "VelocityCommand": "velocity-command",
    "FrameMeta": "frame-meta",
    "DetectionFrame": "detection-frame",
    "MaintenanceIncident": "maintenance-incident",
    "ToolDescriptor": "tool-descriptor",
    "ToolState": "tool-state",
    "NodeSnapshot": "node-snapshot",
    "ChangeProposal": "change-proposal",
    "CanaryDeployResult": "canary-deploy-result",
    "FaultEvent": "fault-event",
    "EvidenceBundle": "evidence-bundle",
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
            ("UpdateManifest", changed(update, signature="a" * 128, signature_alg="ed25519", key_id="0123456789abcdef", min_bootloader="0.1.0", target="h745-cm7"), "signed manifest"),
            ("UpdateManifest", changed(update, signature="A" * 128), "signature in capitals"),
            ("UpdateManifest", changed(update, signature="a" * 127), "short signature"),
            ("UpdateManifest", changed(update, signature_alg="rsa"), "unknown signature algorithm"),
            ("UpdateManifest", changed(update, key_id="0123"), "short key id"),
            ("UpdateManifest", changed(update, min_bootloader="1.x"), "bad minimum bootloader"),
            ("UpdateManifest", changed(update, target="G474"), "target in capitals"),
            ("UpdateManifest", changed(update, target=5), "target as number"),
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
            ("ProjectManifest", changed(manifest, service={"port": 8114, "grpc_port": 50114, "grpc_service": "hydra.common.v1.HealthService"}), "service with a gRPC health port"),
            ("ProjectManifest", changed(manifest, service={"grpc_port": "50114", "grpc_service": "x.v1.S"}), "gRPC port as text"),
            ("ProjectManifest", changed(manifest, service={"grpc_port": 70000, "grpc_service": "x.v1.S"}), "gRPC port above 65535"),
            ("ProjectManifest", changed(manifest, service={"grpc_port": 50114, "grpc_service": ""}), "empty gRPC service name"),
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
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": 42.5}, "minimal production event"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "good": False, "cycle_time_s": 0.001, "job_id": "j-1", "reject_reason": "burr"}, "scrap with job and reason"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": 604800}, "cycle of exactly one week"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": 604801}, "cycle over one week"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": 0}, "cycle of zero"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": -3}, "negative cycle"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": "42"}, "cycle as text"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": True}, "cycle as a boolean"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "good": 1, "cycle_time_s": 4}, "good as a number"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "cycle_time_s": 4}, "no good"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc 1", "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": 4}, "source with a space"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "", "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": 4}, "empty source"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "x" * 65, "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": 4}, "source of 65 characters"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": 4, "operator": "ana"}, "unknown field"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": 4, "reject_reason": ""}, "empty reason"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": 4, "reject_reason": "x" * 121}, "reason of 121 characters"),
            ("ProductionEvent", {"schema_version": "1.0", "source_id": "cnc-1", "at_utc": "2026-01-01T10:00:00Z", "good": True, "cycle_time_s": 4, "job_id": "a b"}, "job with a space"),
            ("CommandLifecycleEvent", {'schema_version': '1.0', 'operation_id': 'op-1', 'robot_id': '3', 'command': 'move', 'state': 'ACCEPTED', 'at_utc': '2026-01-01T10:00:00Z', 'sequence': 1}, "accepted command"),
            ("CommandLifecycleEvent", {'schema_version': '1.0', 'operation_id': 'op-1', 'robot_id': '3', 'command': 'move', 'state': 'FAILED', 'at_utc': '2026-01-01T10:00:00Z', 'sequence': 1, 'reason': 'the controller refused it'}, "failed with a reason"),
            ("CommandLifecycleEvent", {'schema_version': '1.0', 'operation_id': 'op-1', 'robot_id': '3', 'command': 'move', 'state': 'FAILED', 'at_utc': '2026-01-01T10:00:00Z', 'sequence': 1}, "failed without a reason"),
            ("CommandLifecycleEvent", {'schema_version': '1.0', 'operation_id': 'op-1', 'robot_id': '3', 'command': 'move', 'state': 'CANCELLED', 'at_utc': '2026-01-01T10:00:00Z', 'sequence': 1}, "cancelled without a reason"),
            ("CommandLifecycleEvent", {'schema_version': '1.0', 'operation_id': 'op-1', 'robot_id': '3', 'command': 'move', 'state': 'COMPLETED', 'at_utc': '2026-01-01T10:00:00Z', 'sequence': 1, 'reason': 'done'}, "completed with a reason"),
            ("CommandLifecycleEvent", {'schema_version': '1.0', 'operation_id': 'op-1', 'robot_id': '3', 'command': 'move', 'state': 'accepted', 'at_utc': '2026-01-01T10:00:00Z', 'sequence': 1}, "state in lower case"),
            ("CommandLifecycleEvent", {'schema_version': '1.0', 'operation_id': 'op-1', 'robot_id': '3', 'command': 'move', 'state': 'ACCEPTED', 'at_utc': '2026-01-01T10:00:00Z', 'sequence': 0}, "sequence zero"),
            ("CommandLifecycleEvent", {'schema_version': '1.0', 'operation_id': 'op-1', 'robot_id': '3', 'command': 'move', 'state': 'ACCEPTED', 'at_utc': '2026-01-01T10:00:00Z', 'sequence': 1, 'reason': ''}, "empty reason"),
            ("CommandLifecycleEvent", {'schema_version': '1.0', 'operation_id': 'op-1', 'robot_id': 3, 'command': 'move', 'state': 'ACCEPTED', 'at_utc': '2026-01-01T10:00:00Z', 'sequence': 1}, "robot id as a number"),
            ("CommandLifecycleEvent", {'schema_version': '1.0', 'operation_id': 'op-1', 'robot_id': '3', 'command': 'move', 'state': 'ACCEPTED', 'at_utc': '2026-01-01T10:00:00Z', 'sequence': 1, 'extra': 1}, "unknown field"),
            ("VisualTargetRequest", {'schema_version': '1.0', 'frame_id': 'f1', 'current': {'x': 0.1, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'target': {'x': 0.2, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'confidence': 0.8, 'safety_state': 'READY', 'data_age_ms': 30}, "minimal request"),
            ("VisualTargetRequest", {'schema_version': '1.0', 'frame_id': 'f1', 'current': {'x': 0.1, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'target': {'x': 0.2, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'confidence': 0.8, 'safety_state': 'READY'}, "request without any age"),
            ("VisualTargetRequest", {'schema_version': '1.0', 'frame_id': 'f1', 'current': {'x': 0.1, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'target': {'x': 0.2, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'confidence': 0.8, 'safety_state': 'READY', 'captured_at_utc': '2026-01-01T10:00:00Z'}, "request with a capture time"),
            ("VisualTargetRequest", {'schema_version': '1.0', 'frame_id': 'f1', 'current': {'x': 0.1, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'target': {'x': 0.2, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'confidence': 0.8, 'safety_state': 'OK', 'data_age_ms': 30}, "safety state outside the list"),
            ("VisualTargetRequest", {'schema_version': '1.0', 'frame_id': 'f1', 'current': {'x': 0.1, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0, 'qw': 1}, 'target': {'x': 0.2, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'confidence': 0.8, 'safety_state': 'READY', 'data_age_ms': 30}, "pose with an extra field"),
            ("VisualTargetRequest", {'schema_version': '1.0', 'frame_id': 'f1', 'current': {'x': 0.1, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'target': {'x': 0.1, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0}, 'confidence': 0.8, 'safety_state': 'READY', 'data_age_ms': 30}, "pose without yaw"),
            ("VisualTargetRequest", {'schema_version': '1.0', 'frame_id': 'f1', 'current': {'x': 0.1, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'target': {'x': 0.2, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'confidence': -0.1, 'safety_state': 'READY', 'data_age_ms': 30}, "negative confidence"),
            ("VisualTargetRequest", {'schema_version': '1.0', 'frame_id': 'f1', 'current': {'x': 0.1, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'target': {'x': 0.2, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'confidence': 0.8, 'safety_state': 'READY', 'data_age_ms': 30, 'calibration_age_days': -1}, "negative calibration age"),
            ("VisualTargetRequest", {'schema_version': '1.0', 'frame_id': 'f1', 'current': {'x': '0.1', 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'target': {'x': 0.2, 'y': 0.0, 'z': 0.2, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}, 'confidence': 0.8, 'safety_state': 'READY', 'data_age_ms': 30}, "pose value as text"),
            ("VelocityCommand", {'schema_version': '1.0', 'vx': 0.0, 'vy': 0.0, 'vz': 0.0, 'wroll': 0.0, 'wpitch': 0.0, 'wyaw': 0.0, 'hold': True, 'issued_at_ms': 1767261600000, 'valid_for_ms': 200, 'seq': 0}, "hold command"),
            ("VelocityCommand", {'schema_version': '1.0', 'vx': 0.0, 'vy': 0.0, 'vz': 0.0, 'wroll': 0.0, 'wpitch': 0.0, 'wyaw': 0.0, 'hold': True, 'issued_at_ms': 1767261600000, 'valid_for_ms': 200, 'seq': 0, 'frame_id': None}, "command with a null frame"),
            ("VelocityCommand", {'schema_version': '1.0', 'vx': 0.0, 'vy': 0.0, 'vz': 0.0, 'wroll': 0.0, 'wpitch': 0.0, 'wyaw': 0.0, 'hold': True, 'issued_at_ms': 1767261600000, 'valid_for_ms': 60000, 'seq': 0}, "validity of exactly one minute"),
            ("VelocityCommand", {'schema_version': '1.0', 'vx': 0.0, 'vy': 0.0, 'vz': 0.0, 'wroll': 0.0, 'wpitch': 0.0, 'wyaw': 0.0, 'hold': True, 'issued_at_ms': 1767261600000, 'valid_for_ms': 60001, 'seq': 0}, "validity over a minute"),
            ("VelocityCommand", {'schema_version': '1.0', 'vx': 0.0, 'vy': 0.0, 'vz': 0.0, 'wroll': 0.0, 'wpitch': 0.0, 'wyaw': 0.0, 'hold': True, 'issued_at_ms': 1767261600000, 'valid_for_ms': 0, 'seq': 0}, "validity of zero"),
            ("VelocityCommand", {'schema_version': '1.0', 'vx': 0.0, 'vy': 0.0, 'vz': 0.0, 'wroll': 0.0, 'wpitch': 0.0, 'wyaw': 0.0, 'hold': True, 'issued_at_ms': -1, 'valid_for_ms': 200, 'seq': 0}, "issued before the epoch"),
            ("VelocityCommand", {'schema_version': '1.0', 'vx': 0.0, 'vy': 0.0, 'vz': 0.0, 'wroll': 0.0, 'wpitch': 0.0, 'wyaw': 0.0, 'hold': True, 'issued_at_ms': 1767261600000, 'valid_for_ms': 200, 'seq': 1.5}, "sequence as a fraction"),
            ("VelocityCommand", {'schema_version': '1.0', 'vx': True, 'vy': 0.0, 'vz': 0.0, 'wroll': 0.0, 'wpitch': 0.0, 'wyaw': 0.0, 'hold': True, 'issued_at_ms': 1767261600000, 'valid_for_ms': 200, 'seq': 0}, "velocity as a boolean"),
            ("FrameMeta", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'width': 640, 'height': 480, 'pixel_format': 'NV12'}, "minimal frame"),
            ("FrameMeta", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'width': 8192, 'height': 8192, 'pixel_format': 'NV12'}, "frame of the largest size"),
            ("FrameMeta", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'width': 8193, 'height': 480, 'pixel_format': 'NV12'}, "frame wider than the limit"),
            ("FrameMeta", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'width': 0, 'height': 480, 'pixel_format': 'NV12'}, "frame of zero width"),
            ("FrameMeta", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'width': 640, 'height': 480, 'pixel_format': 'NV12', 'stride': 0}, "stride of zero"),
            ("FrameMeta", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'width': 640, 'height': 480, 'pixel_format': 'NV12', 'sequence': -1}, "negative sequence"),
            ("FrameMeta", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'width': 640, 'height': 480, 'pixel_format': 'rgb'}, "pixel format in lower case"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'pixel', 'detections': [{'class_id': 1, 'label': 'tag', 'score': 0.5, 'box': {'x_min': 10, 'y_min': 20, 'x_max': 30, 'y_max': 40}}]}, "detections in pixels"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'pixel', 'detections': []}, "no detections"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'normalized', 'detections': [{'class_id': 1, 'label': 'tag', 'score': 0.5, 'box': {'x_min': 10, 'y_min': 20, 'x_max': 30, 'y_max': 40}}]}, "pixel boxes declared normalized"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'normalized', 'detections': [{'class_id': 1, 'label': 'tag', 'score': 0.5, 'box': {'x_min': 0.1, 'y_min': 0.2, 'x_max': 0.3, 'y_max': 0.4}}]}, "normalized boxes"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'pixel', 'detections': [{'class_id': 1, 'label': 'tag', 'score': 1.01, 'box': {'x_min': 10, 'y_min': 20, 'x_max': 30, 'y_max': 40}}]}, "score over one"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'pixel', 'detections': [{'class_id': -1, 'label': 'tag', 'score': 0.5, 'box': {'x_min': 10, 'y_min': 20, 'x_max': 30, 'y_max': 40}}]}, "negative class"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'pixel', 'detections': [{'class_id': 1, 'label': '', 'score': 0.5, 'box': {'x_min': 10, 'y_min': 20, 'x_max': 30, 'y_max': 40}}]}, "empty label"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'pixel', 'detections': [{'class_id': 1, 'label': 'tag', 'score': 0.5, 'box': {'x_min': 10, 'y_min': 20, 'x_max': 30, 'y_max': 40}, 'extra': 1}]}, "detection with an extra field"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'pixel', 'detections': [{'class_id': 1, 'label': 'tag', 'score': 0.5, 'box': {'x_min': 10, 'y_min': 20, 'x_max': None, 'y_max': 40}}]}, "box corner missing a value"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'pixel', 'detections': [{'class_id': 1, 'label': 'tag', 'score': 0.5, 'box': {'x_min': 10, 'y_min': 20, 'x_max': 30}}]}, "box without a corner"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'pixel', 'detections': [{'class_id': 1, 'label': 'tag', 'score': 0.5, 'box': {'x_min': -1, 'y_min': 20, 'x_max': 30, 'y_max': 40}}]}, "negative corner"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'pixel', 'detections': [{'class_id': 1, 'label': 'tag', 'score': 0.5, 'box': {'x_min': 10, 'y_min': 20, 'x_max': 30, 'y_max': 40}}], 'model': {'model_name': 'm', 'model_version': '1', 'model_sha256': '0000000000000000000000000000000000000000000000000000000000000000', 'hailo_arch': 'hailo8', 'pipeline_version': '0.1.0'}}, "detections with a model"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'pixel', 'detections': [{'class_id': 1, 'label': 'tag', 'score': 0.5, 'box': {'x_min': 10, 'y_min': 20, 'x_max': 30, 'y_max': 40}}], 'model': {'model_name': 'm', 'model_version': '1', 'model_sha256': 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'hailo_arch': 'hailo8', 'pipeline_version': '0.1.0'}}, "model digest in capitals"),
            ("DetectionFrame", {'schema_version': '1.0', 'frame_id': 'f1', 'capture_ts_utc': '2026-01-01T10:00:00Z', 'box_unit': 'pixel', 'detections': [{'class_id': 1, 'label': 'tag', 'score': 0.5, 'box': {'x_min': 10, 'y_min': 20, 'x_max': 30, 'y_max': 40}}], 'model': {'model_name': 'm'}}, "model with only a name"),
            ("MaintenanceIncident", {'incidentId': 'i-1', 'sourceNode': 'n1', 'detectedAt': '2026-01-01T10:00:00Z', 'severity': 'info', 'component': 'c', 'symptom': 's', 'evidenceRefs': ['e'], 'redactionLevel': 'sanitized', 'requestedBy': 'ana', 'correlationId': 'c-1'}, "incident"),
            ("MaintenanceIncident", {'incidentId': 'i-1', 'sourceNode': 'n1', 'detectedAt': '2026-01-01T10:00:00Z', 'severity': 'info', 'component': 'c', 'symptom': 's', 'evidenceRefs': ['e'], 'redactionLevel': 'sanitized', 'requestedBy': 'ana', 'correlationId': 'c-1', 'schema_version': '1.0'}, "incident with the version"),
            ("MaintenanceIncident", {'incidentId': 'i-1', 'sourceNode': 'n1', 'detectedAt': '2026-01-01T10:00:00Z', 'severity': 'info', 'component': 'c', 'symptom': 's', 'evidenceRefs': ['e'], 'redactionLevel': 'sanitized', 'requestedBy': 'ana', 'correlationId': 'c-1', 'schema_version': '2.0'}, "incident with another version"),
            ("MaintenanceIncident", {'incidentId': 'i-1', 'sourceNode': 'n1', 'detectedAt': '2026-01-01T10:00:00Z', 'severity': 'info', 'component': 'c', 'symptom': 's', 'evidenceRefs': ['e'], 'redactionLevel': 'sanitized', 'requestedBy': None, 'correlationId': 'c-1'}, "incident nobody asked for"),
            ("MaintenanceIncident", {'incidentId': 'i-1', 'sourceNode': 'n1', 'detectedAt': '2026-01-01T10:00:00Z', 'severity': 'info', 'component': 'c', 'symptom': 's', 'evidenceRefs': ['e'], 'redactionLevel': 'raw', 'requestedBy': 'ana', 'correlationId': 'c-1'}, "raw incident"),
            ("MaintenanceIncident", {'incidentId': 'i-1', 'sourceNode': 'n1', 'detectedAt': '2026-01-01T10:00:00Z', 'severity': 'info', 'component': 'c', 'symptom': 's', 'evidenceRefs': ['e'], 'redactionLevel': 'none', 'requestedBy': 'ana', 'correlationId': 'c-1'}, "redaction level outside the list"),
            ("MaintenanceIncident", {'incidentId': 'i-1', 'sourceNode': 'n1', 'detectedAt': '2026-01-01T10:00:00Z', 'severity': 'info', 'component': 'c', 'symptom': 's', 'evidenceRefs': ['e'], 'redactionLevel': 'sanitized', 'requestedBy': 'ana', 'correlationId': 'c-1', 'incident_id': 'i-1'}, "snake case twin of a field"),
            ("MaintenanceIncident", {'incidentId': 'i-1', 'sourceNode': 'n1', 'detectedAt': '2026-01-01T10:00:00Z', 'severity': 'info', 'component': 'c', 'symptom': 's', 'evidenceRefs': ['e'], 'redactionLevel': 'sanitized', 'correlationId': 'c-1'}, "incident without requestedBy"),
            ("MaintenanceIncident", {'incidentId': 'i-1', 'sourceNode': 'n1', 'detectedAt': '2026-01-01T10:00:00Z', 'severity': 'info', 'component': 'c', 'symptom': 's', 'evidenceRefs': [1], 'redactionLevel': 'sanitized', 'requestedBy': 'ana', 'correlationId': 'c-1'}, "evidence as numbers"),
            ("MaintenanceIncident", {'incidentId': 'i-1', 'sourceNode': 'n1', 'detectedAt': '2026-01-01T10:00:00Z', 'severity': 'info', 'component': 'c', 'symptom': 's', 'evidenceRefs': ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'], 'redactionLevel': 'sanitized', 'requestedBy': 'ana', 'correlationId': 'c-1'}, "51 evidence references"),
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
