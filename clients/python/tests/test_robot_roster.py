# =============================================================================
# HYDRA-UMC-SDK - Tests of the RobotRoster contract and of the roster read from the settings
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import json
import random
import unittest
from pathlib import Path

from hydra_umc_sdk.robot_roster import MAX_ROBOTS, roster_from_settings, validate_robot_roster
from hydra_umc_sdk.validation import ContractValidationError, validate

FIXTURES = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1"


def fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class RosterContractTests(unittest.TestCase):
    def test_the_valid_fixture_passes_and_the_invalid_one_is_refused(self):
        validate("RobotRoster", fixture("robot-roster.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("RobotRoster", fixture("robot-roster.invalid.json"))

    def test_each_field_is_checked(self):
        base = fixture("robot-roster.valid.json")
        for mutate in (
            lambda p: p.update(schema_version="2.0"),
            lambda p: p.update(extra=1),
            lambda p: p.update(robots="no"),
            lambda p: p["robots"][0].update(controller_id=""),
            lambda p: p["robots"][0].update(controller_id="x" * 101),
            lambda p: p["robots"][0].update(robot_id=-1),
            lambda p: p["robots"][0].update(robot_id=True),
            lambda p: p["robots"][0].update(online=1),
            lambda p: p["robots"][0].update(playback="stopped"),
            lambda p: p["robots"][0].pop("online"),
            lambda p: p["robots"][0].update(extra=1),
            lambda p: p.update(robots=[p["robots"][0]] * (MAX_ROBOTS + 1)),
        ):
            payload = json.loads(json.dumps(base))
            mutate(payload)
            with self.assertRaises(ContractValidationError):
                validate_robot_roster(payload)

    def test_an_empty_roster_is_valid(self):
        validate_robot_roster({"schema_version": "1.0", "robots": []})


class RosterFromSettingsTests(unittest.TestCase):
    def test_the_walk_of_the_controllers(self):
        roster = roster_from_settings({
            "controllers": [
                {"id": "c1", "robots": [{"id": 1, "online": True, "playbackState": {"isPlaying": True}}, {"id": 2, "playbackState": {"isPaused": True, "isPlaying": True}}]},
                {"robots": [{"id": 0, "online": True, "playbackState": {"isFinished": True, "isPlaying": True}}, {"id": 7}]},
            ]
        })
        self.assertEqual(roster["robots"], [
            {"controller_id": "c1", "robot_id": 1, "online": True, "playback": "playing"},
            {"controller_id": "c1", "robot_id": 2, "online": False, "playback": "paused"},
            {"controller_id": "controller-2", "robot_id": 0, "online": True, "playback": "finished"},
            {"controller_id": "controller-2", "robot_id": 7, "online": False, "playback": "idle"},
        ])
        validate("RobotRoster", roster)

    def test_what_is_not_understood_is_skipped(self):
        for settings in (None, 5, "x", [], {}, {"controllers": "no"},
                         {"controllers": [None, 3, {"robots": "no"}, {"robots": [None, {"id": -1}, {"id": 1.5}, {"id": True}, {"id": "1"}]}]}):
            self.assertEqual(roster_from_settings(settings), {"schema_version": "1.0", "robots": []})

    def test_the_roster_stops_at_the_limit(self):
        settings = {"controllers": [{"id": "c", "robots": [{"id": i} for i in range(MAX_ROBOTS + 200)]}]}
        self.assertEqual(len(roster_from_settings(settings)["robots"]), MAX_ROBOTS)

    def test_random_documents_never_raise_and_always_give_a_valid_roster(self):
        rng = random.Random(5)
        atoms = [None, True, 0, 3, -2, 2.5, "", "a", "x" * 150, [], {}]

        def junk(depth):
            if depth == 0 or rng.random() < 0.3:
                return rng.choice(atoms)
            if rng.random() < 0.5:
                return [junk(depth - 1) for _ in range(rng.randrange(0, 4))]
            keys = ("controllers", "robots", "id", "controllerId", "online", "playbackState", "isPlaying", "isPaused", "isFinished", "other")
            return {rng.choice(keys): junk(depth - 1) for _ in range(rng.randrange(0, 5))}

        for _ in range(2000):
            validate("RobotRoster", roster_from_settings(junk(5)))


if __name__ == "__main__":
    unittest.main()
