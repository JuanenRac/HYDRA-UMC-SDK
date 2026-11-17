# =============================================================================
# HYDRA-UMC-SDK - ConfirmationProof contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import json
import unittest
from pathlib import Path

from hydra_umc_sdk import ContractValidationError, sign_confirmation_proof, validate, verify_confirmation_proof
from hydra_umc_sdk.confirmation_proof import MAX_PROOF_VALIDITY_MS, proof_message

FIXTURES = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1"
KEY = b"0123456789abcdef0123456789abcdef"
NOW = 1_767_261_600_000
ACTION = "3f786850e387550fdab836ed7e6dc881de23001b9d1d6c5b0f2d8a8b2f7e1a90"


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _signed(**changes) -> dict:
    fields = dict(kind="approval", action_id=ACTION, subject_id="arm-1", operator="ana", approved_at_ms=NOW, expires_at_ms=NOW + 30_000)
    fields.update(changes)
    return sign_confirmation_proof(KEY, **fields)


class ConfirmationProofTests(unittest.TestCase):
    def test_the_fixtures_are_judged_as_their_names_say(self):
        validate("ConfirmationProof", _fixture("confirmation-proof.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("ConfirmationProof", _fixture("confirmation-proof.invalid.json"))

    def test_the_shape_is_closed_and_typed(self):
        base = _fixture("confirmation-proof.valid.json")
        for field, bad in (("kind", "voice2"), ("action_id", ""), ("subject_id", "a b"), ("operator", "x" * 65), ("approved_at_ms", -1), ("approved_at_ms", True),
                           ("expires_at_ms", 1.5), ("approval_id", "ABC"), ("approval_id", "0" * 31), ("signature", "A" * 64), ("signature", "a" * 63), ("signature", None)):
            with self.subTest(field=field, bad=bad), self.assertRaises(ContractValidationError):
                validate("ConfirmationProof", dict(base, **{field: bad}))
        with self.assertRaises(ContractValidationError):
            validate("ConfirmationProof", dict(base, extra=1))
        without = {key: value for key, value in base.items() if key != "approval_id"}
        validate("ConfirmationProof", without)
        for required in ("kind", "action_id", "subject_id", "operator", "approved_at_ms", "expires_at_ms", "signature"):
            with self.subTest(missing=required), self.assertRaises(ContractValidationError):
                validate("ConfirmationProof", {key: value for key, value in base.items() if key != required})

    def test_a_signed_proof_for_the_same_action_and_subject_passes(self):
        for kind in ("approval", "voice"):
            proof = _signed(kind=kind, approval_id="0123456789abcdef0123456789abcdef")
            self.assertEqual(verify_confirmation_proof(KEY, proof, expected_action_id=ACTION, expected_subject_id="arm-1", now_ms=NOW + 1), (True, ""))
        self.assertEqual(verify_confirmation_proof(KEY, _signed(), expected_action_id=ACTION, expected_subject_id="arm-1", now_ms=NOW), (True, ""))

    def test_each_field_is_covered_by_the_signature(self):
        proof = _signed(approval_id="0123456789abcdef0123456789abcdef")
        for field, other in (("kind", "voice"), ("action_id", "other-action"), ("subject_id", "arm-2"), ("operator", "bob"), ("approved_at_ms", NOW + 1),
                             ("expires_at_ms", NOW + 29_999), ("approval_id", "f" * 32)):
            tampered = dict(proof, **{field: other})
            good, why = verify_confirmation_proof(KEY, tampered, expected_action_id=tampered["action_id"], expected_subject_id=tampered["subject_id"], now_ms=NOW + 1)
            self.assertFalse(good, field)
            self.assertIn("signature", why, field)
        dropped = {key: value for key, value in proof.items() if key != "approval_id"}
        self.assertFalse(verify_confirmation_proof(KEY, dropped, expected_action_id=ACTION, expected_subject_id="arm-1", now_ms=NOW + 1)[0])

    def test_another_key_or_a_short_key_never_passes(self):
        proof = _signed()
        self.assertFalse(verify_confirmation_proof(b"f" * 32, proof, expected_action_id=ACTION, expected_subject_id="arm-1", now_ms=NOW)[0])
        self.assertFalse(verify_confirmation_proof(b"short", proof, expected_action_id=ACTION, expected_subject_id="arm-1", now_ms=NOW)[0])
        self.assertFalse(verify_confirmation_proof("a-text-key-of-enough-length", proof, expected_action_id=ACTION, expected_subject_id="arm-1", now_ms=NOW)[0])  # type: ignore[arg-type]
        with self.assertRaises(ContractValidationError):
            sign_confirmation_proof(b"short", kind="approval", action_id=ACTION, subject_id="arm-1", operator="ana", approved_at_ms=NOW, expires_at_ms=NOW + 1)

    def test_it_must_be_for_exactly_this_action_and_subject(self):
        proof = _signed()
        good, why = verify_confirmation_proof(KEY, proof, expected_action_id="another", expected_subject_id="arm-1", now_ms=NOW)
        self.assertEqual((good, "action" in why), (False, True))
        good, why = verify_confirmation_proof(KEY, proof, expected_action_id=ACTION, expected_subject_id="arm-2", now_ms=NOW)
        self.assertEqual((good, "subject" in why), (False, True))
        for empty in ("", None):
            self.assertFalse(verify_confirmation_proof(KEY, proof, expected_action_id=empty, expected_subject_id="arm-1", now_ms=NOW)[0])  # type: ignore[arg-type]
            self.assertFalse(verify_confirmation_proof(KEY, proof, expected_action_id=ACTION, expected_subject_id=empty, now_ms=NOW)[0])  # type: ignore[arg-type]

    def test_the_window_has_edges(self):
        proof = _signed()
        check = lambda now: verify_confirmation_proof(KEY, proof, expected_action_id=ACTION, expected_subject_id="arm-1", now_ms=now)  # noqa: E731
        self.assertTrue(check(NOW - 5_000)[0], "a clock a few seconds behind is tolerated")
        self.assertFalse(check(NOW - 5_001)[0])
        self.assertTrue(check(NOW + 29_999)[0])
        self.assertFalse(check(NOW + 30_000)[0], "the proof expires at its last millisecond")
        backwards = _signed(approved_at_ms=NOW, expires_at_ms=NOW)
        self.assertFalse(verify_confirmation_proof(KEY, backwards, expected_action_id=ACTION, expected_subject_id="arm-1", now_ms=NOW)[0])
        long_lived = _signed(expires_at_ms=NOW + MAX_PROOF_VALIDITY_MS + 1)
        self.assertFalse(verify_confirmation_proof(KEY, long_lived, expected_action_id=ACTION, expected_subject_id="arm-1", now_ms=NOW)[0])
        at_limit = _signed(expires_at_ms=NOW + MAX_PROOF_VALIDITY_MS)
        self.assertTrue(verify_confirmation_proof(KEY, at_limit, expected_action_id=ACTION, expected_subject_id="arm-1", now_ms=NOW)[0])

    def test_a_proof_without_an_identity_is_refused_when_one_is_required(self):
        plain = _signed()
        self.assertFalse(verify_confirmation_proof(KEY, plain, expected_action_id=ACTION, expected_subject_id="arm-1", now_ms=NOW, require_approval_id=True)[0])
        identified = _signed(approval_id="0123456789abcdef0123456789abcdef")
        self.assertTrue(verify_confirmation_proof(KEY, identified, expected_action_id=ACTION, expected_subject_id="arm-1", now_ms=NOW, require_approval_id=True)[0])

    def test_garbage_is_a_refusal_not_an_error(self):
        for garbage in (None, 5, "proof", [], {}, {"signature": "a" * 64}):
            with self.subTest(garbage=garbage):
                self.assertFalse(verify_confirmation_proof(KEY, garbage, expected_action_id=ACTION, expected_subject_id="arm-1", now_ms=NOW)[0])

    def test_the_message_cannot_be_confused_between_two_proofs(self):
        a = _signed(action_id="ab", subject_id="c")
        b = _signed(action_id="a", subject_id="bc")
        self.assertNotEqual(proof_message(a), proof_message(b))
        self.assertNotEqual(a["signature"], b["signature"])
        self.assertEqual(proof_message(a), proof_message(dict(a, signature="b" * 64)), "the signature is not part of the message")
