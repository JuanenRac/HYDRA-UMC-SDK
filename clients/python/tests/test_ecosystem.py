# =============================================================================
# HYDRA-UMC-SDK - EcosystemHealth and RobotLiveness contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from hydra_umc_sdk import (
    CERTIFICATE_STATES,
    LIVENESS_SOURCES,
    LIVENESS_STATES,
    SERVICE_REASONS,
    SERVICE_STATES,
    WARNING_CODES,
    ContractValidationError,
    validate,
)

try:
    import jsonschema
except ImportError:  # pragma: no cover - optional test dependency
    jsonschema = None

REPO = Path(__file__).resolve().parents[3]
FIXTURES = REPO / "conformance" / "fixtures" / "v1"
SCHEMAS = REPO / "contracts" / "json-schema" / "v1"


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _cases() -> list[tuple[str, dict, str]]:
    """(contract, payload, label): the same list is judged by the schema and by the Python validator."""
    health = _fixture("ecosystem-health.valid.json")
    liveness = _fixture("robot-liveness.valid.json")
    cases: list[tuple[str, dict, str]] = [("EcosystemHealth", health, "valid health"), ("RobotLiveness", liveness, "valid liveness")]

    def health_with(mutate) -> dict:
        payload = copy.deepcopy(health)
        mutate(payload)
        return payload

    def liveness_with(mutate) -> dict:
        payload = copy.deepcopy(liveness)
        mutate(payload)
        return payload

    cases += [
        ("EcosystemHealth", health_with(lambda p: p.update(certificate=None)), "no certificate"),
        ("EcosystemHealth", health_with(lambda p: p.update(available=False, services=[], warnings=[], summary=dict.fromkeys(p["summary"], 0))), "nothing scanned"),
        ("EcosystemHealth", health_with(lambda p: p.update(extra=1)), "unknown top field"),
        ("EcosystemHealth", health_with(lambda p: p.pop("warnings")), "no warnings list"),
        ("EcosystemHealth", health_with(lambda p: p.update(schema_version="2.0")), "other schema version"),
        ("EcosystemHealth", health_with(lambda p: p.update(generated_at_utc="yesterday")), "bad date"),
        ("EcosystemHealth", health_with(lambda p: p.update(available="yes")), "available as text"),
        ("EcosystemHealth", health_with(lambda p: p["summary"].update(down=-1)), "negative count"),
        ("EcosystemHealth", health_with(lambda p: p["summary"].update(extra=1)), "unknown summary field"),
        ("EcosystemHealth", health_with(lambda p: p["summary"].pop("drift")), "summary without drift"),
        ("EcosystemHealth", health_with(lambda p: p["services"][0].update(state="sleeping")), "state outside the list"),
        ("EcosystemHealth", health_with(lambda p: p["services"][0].update(reason="because")), "reason outside the list"),
        ("EcosystemHealth", health_with(lambda p: p["services"][0].update(token="x")), "a secret in a service"),
        ("EcosystemHealth", health_with(lambda p: p["services"][0].update(version_reported="1 2")), "version with a space"),
        ("EcosystemHealth", health_with(lambda p: p["services"][0].update(version_reported="x" * 25)), "version of 25 characters"),
        ("EcosystemHealth", health_with(lambda p: p["services"][0].update(drift=1)), "drift as a number"),
        ("EcosystemHealth", health_with(lambda p: p["services"][0].update(latency_ms=-1)), "negative latency"),
        ("EcosystemHealth", health_with(lambda p: p["services"][0].update(latency_ms=1.5)), "fractional latency"),
        ("EcosystemHealth", health_with(lambda p: p["services"][0].update(port=0)), "port zero"),
        ("EcosystemHealth", health_with(lambda p: p["services"][0].update(port=65536)), "port over 65535"),
        ("EcosystemHealth", health_with(lambda p: p["services"][0].update(port=None)), "port null"),
        ("EcosystemHealth", health_with(lambda p: p["services"][0].update(name="")), "empty name"),
        ("EcosystemHealth", health_with(lambda p: p["services"][0].pop("last_seen_utc")), "service without last_seen_utc"),
        ("EcosystemHealth", health_with(lambda p: [s.pop("port") for s in p["services"]]), "operator view without admin fields"),
        ("EcosystemHealth", health_with(lambda p: p["certificate"].update(state="fine")), "certificate state outside the list"),
        ("EcosystemHealth", health_with(lambda p: p["certificate"].update(path="/etc/key.pem")), "a path in the certificate"),
        ("EcosystemHealth", health_with(lambda p: p["certificate"].update(warn_days=0)), "warn days zero"),
        ("EcosystemHealth", health_with(lambda p: p["certificate"].update(warn_days=366)), "warn days over a year"),
        ("EcosystemHealth", health_with(lambda p: p["certificate"].update(days_left=-3)), "certificate already expired"),
        ("EcosystemHealth", health_with(lambda p: p["certificate"].update(days_left=1.5)), "fractional days left"),
        ("EcosystemHealth", health_with(lambda p: p["certificate"].update(not_after_utc=None, days_left=None, state="unreadable")), "unreadable certificate"),
        ("EcosystemHealth", health_with(lambda p: p["warnings"].append({"code": "service_down"})), "warning without a service"),
        ("EcosystemHealth", health_with(lambda p: p["warnings"].append({"code": "boom"})), "warning code outside the list"),
        ("EcosystemHealth", health_with(lambda p: p["warnings"].append({"code": "service_down", "service": ""})), "warning with an empty service"),
        ("EcosystemHealth", health_with(lambda p: p["warnings"].append({"code": "service_down", "extra": 1})), "unknown warning field"),
        ("RobotLiveness", liveness_with(lambda p: p.update(robots=[])), "empty roster"),
        ("RobotLiveness", liveness_with(lambda p: p.update(extra=1)), "unknown top field"),
        ("RobotLiveness", liveness_with(lambda p: p.update(stale_after_s=0)), "stale after zero"),
        ("RobotLiveness", liveness_with(lambda p: p.update(stale_after_s=3601)), "stale after over an hour"),
        ("RobotLiveness", liveness_with(lambda p: p.update(stale_after_s="30")), "stale after as text"),
        ("RobotLiveness", liveness_with(lambda p: p["robots"][0].update(state="alive")), "state outside the list"),
        ("RobotLiveness", liveness_with(lambda p: p["robots"][0].update(source="guess")), "source outside the list"),
        ("RobotLiveness", liveness_with(lambda p: p["robots"][0].update(age_s=-1)), "negative age"),
        ("RobotLiveness", liveness_with(lambda p: p["robots"][0].update(robot_id="1")), "robot id as text"),
        ("RobotLiveness", liveness_with(lambda p: p["robots"][0].update(robot_id=True)), "robot id as a boolean"),
        ("RobotLiveness", liveness_with(lambda p: p["robots"][0].update(online=True)), "the online flag is not part of it"),
        ("RobotLiveness", liveness_with(lambda p: p["robots"][0].update(last_update_utc="soon")), "bad update date"),
        ("RobotLiveness", liveness_with(lambda p: p["robots"][0].pop("controller_id")), "robot without a controller"),
    ]
    return cases


class EcosystemHealthTests(unittest.TestCase):
    def test_the_fixtures_are_judged_as_their_names_say(self):
        validate("EcosystemHealth", _fixture("ecosystem-health.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("EcosystemHealth", _fixture("ecosystem-health.invalid.json"))

    def test_every_state_reason_certificate_state_and_warning_is_accepted(self):
        base = _fixture("ecosystem-health.valid.json")
        for state in SERVICE_STATES:
            for reason in SERVICE_REASONS:
                payload = copy.deepcopy(base)
                payload["services"][0].update(state=state, reason=reason)
                with self.subTest(state=state, reason=reason):
                    validate("EcosystemHealth", payload)
        for cert in CERTIFICATE_STATES:
            payload = copy.deepcopy(base)
            payload["certificate"]["state"] = cert
            with self.subTest(certificate=cert):
                validate("EcosystemHealth", payload)
        for code in WARNING_CODES:
            payload = copy.deepcopy(base)
            payload["warnings"] = [{"code": code}]
            with self.subTest(warning=code):
                validate("EcosystemHealth", payload)

    def test_the_lists_match_the_server_documentation(self):
        self.assertEqual(len(SERVICE_REASONS), 13)
        self.assertEqual(set(SERVICE_STATES), {"ok", "degraded", "down", "unknown"})

    def test_an_operator_view_has_no_address_of_the_host(self):
        payload = _fixture("ecosystem-health.valid.json")
        for service in payload["services"]:
            for name in ("port", "health_path", "systemd_unit", "active_state"):
                service.pop(name)
        validate("EcosystemHealth", payload)


class RobotLivenessTests(unittest.TestCase):
    def test_the_fixtures_are_judged_as_their_names_say(self):
        validate("RobotLiveness", _fixture("robot-liveness.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("RobotLiveness", _fixture("robot-liveness.invalid.json"))

    def test_every_state_and_source_is_accepted(self):
        base = _fixture("robot-liveness.valid.json")
        for state in LIVENESS_STATES:
            for source in LIVENESS_SOURCES:
                payload = copy.deepcopy(base)
                payload["robots"][0].update(state=state, source=source)
                with self.subTest(state=state, source=source):
                    validate("RobotLiveness", payload)

    def test_a_robot_nobody_heard_from_has_no_date(self):
        payload = _fixture("robot-liveness.valid.json")
        self.assertNotIn("last_update_utc", payload["robots"][2])
        validate("RobotLiveness", payload)


@unittest.skipIf(jsonschema is None, "jsonschema is not installed")
class DifferentialTests(unittest.TestCase):
    def test_the_schema_and_the_python_validator_agree_on_every_case(self):
        disagreements = []
        # The date-time format is only asserted when the optional RFC 3339 checker is installed.
        dates_asserted = not jsonschema.FormatChecker().conforms("yesterday", "date-time")
        for contract, payload, label in _cases():
            if not dates_asserted and "date" in label:
                continue
            stem = "ecosystem-health" if contract == "EcosystemHealth" else "robot-liveness"
            schema = json.loads((SCHEMAS / f"{stem}.schema.json").read_text(encoding="utf-8"))
            validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
            by_schema = validator.is_valid(payload)
            try:
                validate(contract, payload)
                by_python = True
            except ContractValidationError:
                by_python = False
            if by_schema != by_python:
                disagreements.append(f"{contract}: {label}: schema={by_schema} python={by_python}")
        self.assertEqual(disagreements, [])

    def test_the_cases_cover_both_verdicts(self):
        verdicts = set()
        for contract, payload, _ in _cases():
            try:
                validate(contract, payload)
                verdicts.add(True)
            except ContractValidationError:
                verdicts.add(False)
        self.assertEqual(verdicts, {True, False})


if __name__ == "__main__":
    unittest.main()
