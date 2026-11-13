# =============================================================================
# HYDRA-UMC-SDK - Tests of the correlation of command answers and of the start metadata
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import random
import unittest

from hydra_umc_sdk.bridge_contract import BridgeError
from hydra_umc_sdk.command_correlation import (
    StartMetadata,
    answer_with_request_id,
    parse_start_metadata,
    read_request_id,
    start_matches,
)

DIGEST = "ab" * 32


class RequestIdTests(unittest.TestCase):
    def test_absent_is_none_and_valid_is_returned(self):
        self.assertIsNone(read_request_id({}))
        self.assertEqual(read_request_id({"request_id": "ui-7:a.b_c"}), "ui-7:a.b_c")

    def test_a_bad_request_id_is_refused(self):
        for value in ("", "x" * 65, "a b", "a/b", 5, ["a"], "\n"):
            with self.assertRaises(BridgeError, msg=repr(value)):
                read_request_id({"request_id": value})

    def test_the_answer_carries_it_and_the_original_is_untouched(self):
        answer = {"allowed": True}
        out = answer_with_request_id(answer, "r1")
        self.assertEqual(out, {"allowed": True, "request_id": "r1"})
        self.assertNotIn("request_id", answer)
        self.assertEqual(answer_with_request_id(answer, None), answer)
        self.assertEqual(answer_with_request_id({"request_id": "r1"}, "r1")["request_id"], "r1")
        with self.assertRaises(BridgeError):
            answer_with_request_id({"request_id": "other"}, "r1")

    def test_random_texts_never_raise_anything_but_a_bridge_error(self):
        rng = random.Random(11)
        alphabet = "abZ09-_.: /\\\né"
        for _ in range(3000):
            text = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 80)))
            try:
                got = read_request_id({"request_id": text})
            except BridgeError:
                continue
            self.assertEqual(got, text)
            self.assertTrue(1 <= len(text) <= 64)


class StartMetadataTests(unittest.TestCase):
    def test_absent_metadata_is_not_present(self):
        self.assertFalse(parse_start_metadata({}).present)

    def test_valid_metadata_is_read_and_the_digest_is_lower_case(self):
        meta = parse_start_metadata({"sha256": DIGEST.upper(), "profile_id": "pla-0.2"})
        self.assertEqual(meta, StartMetadata(DIGEST, "pla-0.2"))
        self.assertTrue(meta.present)

    def test_malformed_metadata_is_refused(self):
        for payload in ({"sha256": "abc"}, {"sha256": 5}, {"sha256": "g" * 64}, {"profile_id": ""}, {"profile_id": "a b"}, {"profile_id": 3}):
            with self.assertRaises(BridgeError, msg=str(payload)):
                parse_start_metadata(payload)

    def test_what_the_command_names_must_be_confirmed_by_the_machine(self):
        meta = StartMetadata(DIGEST, "p1")
        self.assertEqual(start_matches(meta, file_sha256=DIGEST.upper(), profile_id="p1"), (True, "ok"))
        self.assertFalse(start_matches(meta, file_sha256="cd" * 32, profile_id="p1")[0])
        self.assertFalse(start_matches(meta, file_sha256=None, profile_id="p1")[0])
        self.assertFalse(start_matches(meta, file_sha256=DIGEST, profile_id="p2")[0])
        self.assertFalse(start_matches(meta, file_sha256=DIGEST, profile_id=None)[0])

    def test_what_the_command_does_not_name_is_not_checked(self):
        self.assertTrue(start_matches(StartMetadata(), file_sha256=None, profile_id=None)[0])
        self.assertTrue(start_matches(StartMetadata(DIGEST, None), file_sha256=DIGEST, profile_id=None)[0])


if __name__ == "__main__":
    unittest.main()
