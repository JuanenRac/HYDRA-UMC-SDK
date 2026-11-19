# =============================================================================
# HYDRA-UMC-SDK - Manifest signature tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone

from hydra_umc_sdk.manifest_signing import (
    KeyListError,
    canonical_message,
    key_id_of,
    keys_from_json,
    public_key_from_seed,
    sign,
    sign_manifest,
    verify,
    verify_manifest,
)
from manifest_signing_vectors import MANIFEST, OUT, SEED_CURRENT, render

# RFC 8032 section 7.1, test 1 (empty message) and test 2 (one byte)
RFC1_SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
RFC1_PUBLIC = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
RFC1_SIGNATURE = bytes.fromhex("e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b")
RFC2_SEED = bytes.fromhex("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb")
RFC2_PUBLIC = bytes.fromhex("3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c")
RFC2_SIGNATURE = bytes.fromhex("92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00")


def _moment(text: str) -> datetime:
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


class Ed25519Test(unittest.TestCase):
    def test_rfc_8032_vectors(self) -> None:
        self.assertEqual(public_key_from_seed(RFC1_SEED), RFC1_PUBLIC)
        self.assertEqual(sign(RFC1_SEED, b""), RFC1_SIGNATURE)
        self.assertTrue(verify(RFC1_PUBLIC, b"", RFC1_SIGNATURE))
        self.assertEqual(public_key_from_seed(RFC2_SEED), RFC2_PUBLIC)
        self.assertEqual(sign(RFC2_SEED, b"\x72"), RFC2_SIGNATURE)
        self.assertTrue(verify(RFC2_PUBLIC, b"\x72", RFC2_SIGNATURE))

    def test_a_changed_message_signature_or_key_is_refused(self) -> None:
        self.assertFalse(verify(RFC1_PUBLIC, b"x", RFC1_SIGNATURE))
        self.assertFalse(verify(RFC1_PUBLIC, b"", RFC1_SIGNATURE[:-1] + b"\x0c"))
        self.assertFalse(verify(RFC2_PUBLIC, b"", RFC1_SIGNATURE))

    def test_wrong_lengths_and_a_non_canonical_scalar_are_refused(self) -> None:
        self.assertFalse(verify(RFC1_PUBLIC[:-1], b"", RFC1_SIGNATURE))
        self.assertFalse(verify(RFC1_PUBLIC, b"", RFC1_SIGNATURE[:-1]))
        order = 2**252 + 27742317777372353535851937790883648493
        high_s = RFC1_SIGNATURE[:32] + (int.from_bytes(RFC1_SIGNATURE[32:], "little") + order).to_bytes(32, "little")
        self.assertFalse(verify(RFC1_PUBLIC, b"", high_s))


class VectorsTest(unittest.TestCase):
    def test_the_committed_vectors_are_the_generated_ones(self) -> None:
        self.assertEqual(OUT.read_text(encoding="utf-8"), render(), "run: py -3 clients/python/tests/manifest_signing_vectors.py --write")

    def test_every_vector_gives_its_verdict(self) -> None:
        data = json.loads(OUT.read_text(encoding="utf-8"))
        keys = keys_from_json(json.dumps(data["keys"]))
        self.assertGreaterEqual(len(data["cases"]), 18)
        for case in data["cases"]:
            with self.subTest(case["name"]):
                verdict = verify_manifest(case["manifest"], keys, _moment(case["now"]), require_asymmetric_signature=case["require_asymmetric_signature"])
                self.assertEqual((verdict.accepted, verdict.code), (case["accepted"], case["code"]))


class RuleTest(unittest.TestCase):
    def setUp(self) -> None:
        public = public_key_from_seed(SEED_CURRENT)
        self.keys = keys_from_json(json.dumps({"schema": 1, "keys": [{"key_id": key_id_of(public), "public": public.hex(), "state": "current", "not_before": None, "not_after": None}]}))
        self.now = _moment("2030-03-01T00:00:00Z")

    def test_a_good_signature_a_bad_one_and_the_key_of_the_verdict(self) -> None:
        good = sign_manifest(MANIFEST, SEED_CURRENT)
        verdict = verify_manifest(good, self.keys, self.now)
        self.assertEqual((verdict.accepted, verdict.code, verdict.key_id), (True, "ok", good["key_id"]))
        bad = dict(good, version="9.9.9")
        self.assertEqual(verify_manifest(bad, self.keys, self.now).code, "bad_signature")

    def test_the_signature_covers_the_algorithm_and_the_key_id(self) -> None:
        good = sign_manifest(MANIFEST, SEED_CURRENT)
        self.assertIn(b'"key_id"', canonical_message(good))
        self.assertIn(b'"signature_alg"', canonical_message(good))
        self.assertNotIn(b'"signature"', canonical_message(good).replace(b'"signature_alg"', b""))

    def test_downgrade_to_legacy_is_refused_only_when_the_switch_is_on(self) -> None:
        self.assertEqual(verify_manifest(MANIFEST, self.keys, self.now).code, "legacy")
        self.assertTrue(verify_manifest(MANIFEST, self.keys, self.now).legacy)
        on = verify_manifest(MANIFEST, self.keys, self.now, require_asymmetric_signature=True)
        self.assertEqual((on.accepted, on.code), (False, "downgrade_refused"))

    def test_a_manifest_that_is_not_an_object_is_malformed(self) -> None:
        self.assertEqual(verify_manifest([], self.keys, self.now).code, "malformed")  # type: ignore[arg-type]

    def test_a_clock_without_a_zone_is_a_programming_error(self) -> None:
        with self.assertRaises(ValueError):
            verify_manifest(MANIFEST, self.keys, datetime(2030, 1, 1))

    def test_an_empty_list_trusts_nothing(self) -> None:
        good = sign_manifest(MANIFEST, SEED_CURRENT)
        self.assertEqual(verify_manifest(good, (), self.now).code, "unknown_key")


class KeyListTest(unittest.TestCase):
    def _list(self, **changes: object) -> str:
        public = public_key_from_seed(SEED_CURRENT)
        entry = {"key_id": key_id_of(public), "public": public.hex(), "state": "current", "not_before": None, "not_after": None}
        entry.update(changes)
        return json.dumps({"schema": 1, "keys": [entry]})

    def test_a_good_list_loads(self) -> None:
        self.assertEqual(len(keys_from_json(self._list())), 1)

    def test_every_fault_refuses_the_whole_list(self) -> None:
        public = public_key_from_seed(SEED_CURRENT)
        faults = [
            "not json",
            "[]",
            json.dumps({"schema": 2, "keys": []}),
            self._list(key_id="0" * 16),
            self._list(public="zz"),
            self._list(state="trusted"),
            self._list(not_before="yesterday"),
            self._list(extra="x"),
            json.dumps({"schema": 1, "keys": [json.loads(self._list())["keys"][0]] * 2}),
        ]
        for text in faults:
            with self.subTest(text[:40]):
                with self.assertRaises(KeyListError):
                    keys_from_json(text)
        self.assertEqual(len(public), 32)

    def test_a_label_is_allowed(self) -> None:
        self.assertEqual(len(keys_from_json(self._list(label="release 2030"))), 1)


if __name__ == "__main__":
    unittest.main()
