# =============================================================================
# HYDRA-UMC-SDK - Python validator vs. normative JSON Schema (mutations)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Starts from every valid conformance fixture and damages it one field at a
time (removed, wrong type, empty, out of range, malformed date, extra field),
at the top level and one object level down. The hand written Python validator
and the normative JSON Schema (what the Go, TypeScript and Rust clients use)
must give the same verdict for every damaged payload, otherwise a service in one
language accepts what a service in another language rejects.

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

CONTRACTS = {
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
}

# The Python validator is deliberately stricter than the schema here: the schema
# allows an empty string for a manifest's parent, the validator asks for a name
# or null.
STRICTER_ON_PURPOSE = [("ProjectManifest", "parent", "")]

REMOVE = object()
REPLACEMENTS = [
    REMOVE, None, True, False, 0, -1, 1, 1.5, 65536, "", " ", "x", [], [""], ["x"], {}, {"a": 1},
    "2026-13-45T00:00:00Z", "not-a-date", "2026-01-01", "2026-01-01T00:00:00",
]


def _walk(value, path=()):
    """Every path to a field of an object, top level and one object level down."""
    if isinstance(value, dict):
        for key, child in value.items():
            yield path + (key,)
            if len(path) == 0 and isinstance(child, dict):
                yield from _walk(child, path + (key,))


def _mutated(payload, path, replacement):
    result = copy.deepcopy(payload)
    holder = result
    for key in path[:-1]:
        holder = holder[key]
    if replacement is REMOVE:
        del holder[path[-1]]
    else:
        holder[path[-1]] = copy.deepcopy(replacement)
    return result


@unittest.skipIf(jsonschema is None, "the optional jsonschema package is not installed")
class MutationDifferentialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = {
            contract: jsonschema.Draft202012Validator(json.loads((SCHEMAS / f"{stem}.schema.json").read_text(encoding="utf-8")))
            for contract, stem in CONTRACTS.items()
        }

    def setUp(self):
        self.crashes = set()

    def verdicts(self, contract, payload):
        schema_ok = self.schemas[contract].is_valid(payload)
        try:
            validate(contract, payload)
            python_ok = True
        except ContractValidationError:
            python_ok = False
        except Exception as exc:  # a validator must refuse, never crash
            self.crashes.add(f"{contract}: {type(exc).__name__}: {exc}")
            python_ok = False
        return schema_ok, python_ok

    def test_every_valid_fixture_is_still_valid_in_both(self):
        for contract, stem in CONTRACTS.items():
            payload = json.loads((FIXTURES / f"{stem}.valid.json").read_text(encoding="utf-8"))
            self.assertEqual(self.verdicts(contract, payload), (True, True), contract)

    def test_damaged_payloads_get_the_same_verdict(self):
        disagreements = []
        checked = 0
        for contract, stem in CONTRACTS.items():
            payload = json.loads((FIXTURES / f"{stem}.valid.json").read_text(encoding="utf-8"))
            for path in _walk(payload):
                for replacement in REPLACEMENTS:
                    # `format: date-time` is only an annotation for a plain JSON Schema
                    # validator; the date forms are covered by the validator's own tests.
                    if path[-1].endswith("_utc") and isinstance(replacement, str):
                        continue
                    damaged = _mutated(payload, path, replacement)
                    schema_ok, python_ok = self.verdicts(contract, damaged)
                    checked += 1
                    if (contract, ".".join(path), replacement) in STRICTER_ON_PURPOSE and python_ok is False and schema_ok is True:
                        continue
                    if schema_ok != python_ok:
                        shown = "<removed>" if replacement is REMOVE else json.dumps(replacement)
                        disagreements.append(
                            f"{contract} {'.'.join(path)} = {shown}: schema={'valid' if schema_ok else 'invalid'} "
                            f"python={'valid' if python_ok else 'invalid'}"
                        )
            extra = copy.deepcopy(payload)
            extra["zz_unknown_field"] = "x"
            schema_ok, python_ok = self.verdicts(contract, extra)
            checked += 1
            if schema_ok != python_ok:
                disagreements.append(f"{contract} extra field: schema={schema_ok} python={python_ok}")
        self.assertGreater(checked, 500)
        self.assertEqual(sorted(self.crashes), [], "the validator raised something other than ContractValidationError")
        self.assertEqual(disagreements, [], "\n" + "\n".join(disagreements[:40]))


class ValidatorNeverCrashesTests(unittest.TestCase):
    """These need no jsonschema: a malformed payload is a ContractValidationError, never another exception."""

    def fixture(self, stem):
        return json.loads((FIXTURES / f"{stem}.valid.json").read_text(encoding="utf-8"))

    def test_a_list_or_object_where_an_enum_belongs_is_refused_not_a_crash(self):
        for contract, stem, path in [
            ("Operation", "operation", ("status",)),
            ("ScenarioOutcome", "scenario-outcome", ("phase",)),
            ("ScenarioOutcome", "scenario-outcome", ("observed", "outcome")),
            ("HealthReport", "health-report", ("state",)),
            ("SafetyState", "safety-state", ("state",)),
            ("ProjectManifest", "project-manifest", ("ecosystem",)),
            ("ProjectManifest", "project-manifest", ("role",)),
            ("ProjectManifest", "project-manifest", ("maturity",)),
            ("Capability", "capability", ("last_check_outcome",)),
        ]:
            for bad in ([], ["x"], {}, {"a": 1}, 5, None):
                payload = self.fixture(stem)
                holder = payload
                for key in path[:-1]:
                    holder = holder[key]
                holder[path[-1]] = bad
                with self.assertRaises(ContractValidationError, msg=f"{contract} {path} = {bad!r}"):
                    validate(contract, payload)

    def test_optional_text_fields_must_be_text(self):
        for contract, stem, field in [
            ("Operation", "operation", "status_reason"),
            ("Capability", "capability", "checked_configuration"),
        ]:
            ok = self.fixture(stem)
            ok[field] = "a reason"
            validate(contract, ok)
            for bad in (5, [], {}, None, True):
                payload = self.fixture(stem)
                payload[field] = bad
                with self.assertRaises(ContractValidationError, msg=f"{contract}.{field} = {bad!r}"):
                    validate(contract, payload)

    def test_scenario_evidence_must_be_text(self):
        payload = self.fixture("scenario-outcome")
        payload["observed"]["evidence"] = ["log"]
        with self.assertRaises(ContractValidationError):
            validate("ScenarioOutcome", payload)


if __name__ == "__main__":
    unittest.main()
