# =============================================================================
# HYDRA-UMC-SDK - Zone occupancy tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The occupancy message: the optional `known` field, the stamp in the future and the closed schema."""

from __future__ import annotations

import json
import unittest

from hydra_umc_sdk.zone_occupancy import MAX_ZONES, Occupancy, OccupancyError, parse_occupancy

NOW = 1_800_000_000_000


class TheMessage(unittest.TestCase):
    def test_a_message_without_known_reads_as_before(self):
        got = parse_occupancy({"occupied": ["press-1", "press-1", "door"], "observed_at": NOW}, now_ms=NOW)
        self.assertEqual(got, Occupancy(frozenset({"press-1", "door"}), NOW, True))

    def test_known_false_says_that_nobody_could_see_and_drops_the_zones(self):
        got = parse_occupancy({"occupied": ["press-1"], "observed_at": NOW, "known": False}, now_ms=NOW)
        self.assertFalse(got.known)
        self.assertEqual(got.occupied, frozenset())
        self.assertFalse(parse_occupancy({"observed_at": NOW, "known": False}, now_ms=NOW).known)

    def test_text_and_bytes_are_read_too(self):
        text = json.dumps({"occupied": [], "observed_at": NOW})
        self.assertTrue(parse_occupancy(text, now_ms=NOW).known)
        self.assertTrue(parse_occupancy(text.encode(), now_ms=NOW).known)

    def test_a_stamp_in_the_future_is_refused_beyond_the_allowance(self):
        parse_occupancy({"occupied": [], "observed_at": NOW + 2000}, now_ms=NOW)
        with self.assertRaises(OccupancyError):
            parse_occupancy({"occupied": [], "observed_at": NOW + 3_600_000}, now_ms=NOW)
        with self.assertRaises(OccupancyError):
            parse_occupancy({"occupied": [], "observed_at": NOW + 2001}, now_ms=NOW)
        parse_occupancy({"occupied": [], "observed_at": NOW + 5000}, now_ms=NOW, max_future_ms=5000)

    def test_anything_that_is_not_the_contract_is_refused(self):
        bad: list[object] = [
            "not json",
            "[]",
            {},
            {"occupied": [], "observed_at": "now"},
            {"occupied": [], "observed_at": True},
            {"occupied": [], "observed_at": -1},
            {"occupied": [], "observed_at": float("inf")},
            {"occupied": "press-1", "observed_at": NOW},
            {"occupied": [1], "observed_at": NOW},
            {"occupied": [""], "observed_at": NOW},
            {"occupied": ["x" * 129], "observed_at": NOW},
            {"occupied": ["z"] * (MAX_ZONES + 1), "observed_at": NOW},
            {"occupied": [], "observed_at": NOW, "known": "no"},
            {"occupied": [], "observed_at": NOW, "known": None},
            {"occupied": [], "observed_at": NOW, "surprise": 1},
            b"x" * 70000,
        ]
        for message in bad:
            with self.assertRaises(OccupancyError, msg=str(message)[:40]):
                parse_occupancy(message, now_ms=NOW)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
