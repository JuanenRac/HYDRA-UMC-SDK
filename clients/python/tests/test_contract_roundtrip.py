# =============================================================================
# HYDRA-UMC-SDK - Cross-language contract round-trip tests (Python side)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Real serialize/deserialize round-trip coverage over the exact same real
conformance fixtures `test_validation.py` already validates - one per real
v1 contract (see `conformance/fixtures/v1/*.valid.json`).

This is a different, complementary check from schema validation: a fixture
can validate cleanly against its schema while still losing or reordering
data on its way through a language's own JSON encode/decode path (a real
risk for the languages here that decode into hand-written structs instead
of a generic map - see `clients/go/roundtrip_test.go` and
`clients/rust/tests/roundtrip.rs`, the same fixtures decoded into THEIR own
native representations). The Python reference client keeps every one of
these 10 contracts as a plain `dict` (no hand-written dataclass mirrors the
way Go/Rust/TypeScript's `types.go`/`types.rs`/`types.ts` do), so this
mostly proves `json.dumps`/`json.loads` themselves never drop or reorder a
real payload's fields - still a real, worthwhile floor, and the same
fixture set every other language's own round-trip test uses.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "conformance" / "fixtures" / "v1"

# Every real top-level contract with a `<stem>.valid.json` conformance
# fixture - the same 10 contracts clients/typescript/tests/validation.test.mts'
# own CONTRACT_FIXTURE_STEM lists, so all 4 languages round-trip the exact
# same real payloads.
CONTRACT_FIXTURE_STEMS = [
    "capability",
    "device-descriptor",
    "event-envelope",
    "health-report",
    "operation",
    "project-manifest",
    "safety-state",
    "scenario-outcome",
    "server-discovery",
    "update-manifest",
]


class ContractRoundtripTests(unittest.TestCase):
    def fixture_text(self, stem: str) -> str:
        return (FIXTURES / f"{stem}.valid.json").read_text(encoding="utf-8")

    def test_every_real_fixture_exists_for_every_named_contract(self):
        # A stem here with no matching fixture file would make every other
        # test in this class silently skip that contract - fail loudly
        # instead.
        missing = [stem for stem in CONTRACT_FIXTURE_STEMS if not (FIXTURES / f"{stem}.valid.json").exists()]
        self.assertEqual(missing, [])

    def test_roundtrip_preserves_every_field_structurally(self):
        for stem in CONTRACT_FIXTURE_STEMS:
            with self.subTest(contract=stem):
                original = json.loads(self.fixture_text(stem))
                reencoded = json.dumps(original)
                roundtripped = json.loads(reencoded)
                self.assertEqual(roundtripped, original)

    def test_roundtrip_is_stable_under_a_second_pass(self):
        # Real proof this isn't a lucky single pass: encode/decode twice
        # more and it must still match the original exactly.
        for stem in CONTRACT_FIXTURE_STEMS:
            with self.subTest(contract=stem):
                original = json.loads(self.fixture_text(stem))
                twice = json.loads(json.dumps(json.loads(json.dumps(original))))
                self.assertEqual(twice, original)


if __name__ == "__main__":
    unittest.main()
