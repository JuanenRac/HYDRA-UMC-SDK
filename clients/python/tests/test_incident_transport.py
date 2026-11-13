# =============================================================================
# HYDRA-UMC-SDK - Tests of the incident-transport/1 envelope
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import copy
import unittest

from hydra_umc_sdk.evidence_bundle import seal_bundle
from hydra_umc_sdk.incident_transport import (
    IncidentTransportError,
    build_incident_message,
    sign_message,
    verify_incident_message,
)

SECRET = "transport-secret-of-test-0123456789"
NOW = 1_700_000_000.0


def bundle():
    return seal_bundle({
        "componentVersions": {"server": "1.0.0"},
        "relevantManifests": [],
        "redactedLogExcerpts": ["line"],
        "reproductionSteps": ["start the server"],
        "failedTests": [],
        "impact": "a route answers 500",
        "actionsAttempted": ["restart"],
        "date": "2026-01-01T00:00:00Z",
        "localValidationResult": "failed",
    })


class Seen:
    def __init__(self):
        self.nonces = set()

    def __call__(self, nonce):
        if nonce in self.nonces:
            return False
        self.nonces.add(nonce)
        return True


def check(message, seen=None, **overrides):
    options = {"secret": SECRET, "expected_to_node": "dev-1", "now": NOW, "remember_nonce": seen or Seen()}
    options.update(overrides)
    return verify_incident_message(message, **options)


def signed(mutate):
    message = build_incident_message(bundle(), "esc-1", "dev-1", "n1", NOW, SECRET)
    mutate(message)
    message["mac"] = sign_message(message, SECRET)
    return message


class IncidentTransportTests(unittest.TestCase):
    def test_a_built_message_is_accepted_and_returns_the_case_and_the_bundle(self):
        message = build_incident_message(bundle(), "esc-1", "dev-1", "n1", NOW, SECRET)
        case, got = check(message)
        self.assertEqual(case, "esc-1")
        self.assertEqual(got, bundle())

    def test_a_replay_is_refused_and_a_refused_message_does_not_use_up_its_nonce(self):
        seen = Seen()
        message = build_incident_message(bundle(), "esc-1", "dev-1", "n1", NOW, SECRET)
        forged = copy.deepcopy(message)
        forged["to_node"] = "dev-2"
        with self.assertRaises(IncidentTransportError):
            check(forged, seen)
        self.assertEqual(seen.nonces, set())
        check(message, seen)
        with self.assertRaisesRegex(IncidentTransportError, "replay"):
            check(message, seen)

    def test_signature_destination_clock_and_shape_are_checked(self):
        good = build_incident_message(bundle(), "esc-1", "dev-1", "n1", NOW, SECRET)
        wrong_secret = "another-secret-of-test-0123456789"
        with self.assertRaisesRegex(IncidentTransportError, "signature"):
            check(good, secret=wrong_secret)
        with self.assertRaisesRegex(IncidentTransportError, "another node"):
            check(good, expected_to_node="dev-9")
        with self.assertRaisesRegex(IncidentTransportError, "too old"):
            check(good, now=NOW + 10_000)
        for mutate, text in (
            (lambda m: m.update(kind="other"), "not an incident"),
            (lambda m: m.update(contract_version="incident-transport/2"), "not an incident"),
            (lambda m: m.update(nonce=""), "no nonce"),
            (lambda m: m.update(sent_at=True), "too old"),
            (lambda m: m["payload"].update(escalationId="../x"), "plain identifier"),
            (lambda m: m["payload"].pop("evidenceBundle"), "no evidence bundle"),
        ):
            with self.assertRaisesRegex(IncidentTransportError, text):
                check(signed(mutate))

    def test_a_bundle_edited_after_sealing_is_refused_even_with_a_valid_signature(self):
        message = signed(lambda m: m["payload"]["evidenceBundle"].update(impact="something else"))
        with self.assertRaisesRegex(IncidentTransportError, "checksum"):
            check(message)

    def test_a_malformed_bundle_is_refused(self):
        message = signed(lambda m: m["payload"]["evidenceBundle"].pop("impact"))
        with self.assertRaisesRegex(IncidentTransportError, "not a valid EvidenceBundle"):
            check(message)

    def test_a_short_secret_is_refused_and_never_echoed(self):
        with self.assertRaises(IncidentTransportError) as raised:
            build_incident_message(bundle(), "esc-1", "dev-1", "n1", NOW, "short")
        self.assertNotIn("short", str(raised.exception).replace("shorter", ""))
        with self.assertRaises(IncidentTransportError):
            check("not an object")

    def test_building_refuses_bad_inputs(self):
        for kwargs in ({"escalation_id": "a b"}, {"to_node": " "}, {"nonce": ""}, {"sent_at": True}):
            args = {"escalation_id": "esc-1", "to_node": "dev-1", "nonce": "n1", "sent_at": NOW}
            args.update(kwargs)
            with self.assertRaises(IncidentTransportError, msg=str(kwargs)):
                build_incident_message(bundle(), secret=SECRET, **args)
        tampered = bundle()
        tampered["impact"] = "changed"
        with self.assertRaises(IncidentTransportError):
            build_incident_message(tampered, "esc-1", "dev-1", "n1", NOW, SECRET)


if __name__ == "__main__":
    unittest.main()
