# =============================================================================
# HYDRA-UMC-SDK - Tests of the shared reading of the state word of a GRBL report
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import random
import unittest

from hydra_umc_sdk.bridge_contract import MachineState
from hydra_umc_sdk.grbl_status import GRBL_STATES, grbl_machine_state


class GrblStatusTests(unittest.TestCase):
    def test_the_substate_and_the_case_do_not_matter(self):
        for word, expected in (("Idle", MachineState.IDLE), ("Hold:0", MachineState.HOLDING), ("hold:1", MachineState.HOLDING), ("Door:3", MachineState.SAFE_STOP),
                               ("Alarm:1", MachineState.FAULT), ("Run", MachineState.RUNNING), ("Jog", MachineState.RUNNING), ("Home", MachineState.RUNNING),
                               (" Idle ", MachineState.IDLE), ("STOPPED", MachineState.STOPPED)):
            self.assertEqual(grbl_machine_state(word), expected, word)

    def test_unknown_or_non_text_is_offline_and_never_allows_work(self):
        for word in (None, 7, b"Idle", "", "Check", "Sleep", "Idle2", ":0", "Id le"):
            self.assertEqual(grbl_machine_state(word), MachineState.OFFLINE, repr(word))

    def test_only_idle_maps_to_a_state_where_work_may_start(self):
        rng = random.Random(7)
        alphabet = "abcdefghijklmnopqrstuvwxyz:0123 "
        for _ in range(2000):
            word = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 9)))
            if grbl_machine_state(word) == MachineState.IDLE:
                self.assertEqual(word.strip().upper().split(":")[0], "IDLE")
        self.assertEqual([w for w, s in GRBL_STATES.items() if s == MachineState.IDLE], ["IDLE"])

    def test_a_bridge_can_add_a_word_of_its_own(self):
        self.assertEqual(grbl_machine_state("Off", {"OFF": MachineState.FAULT}), MachineState.FAULT)
        self.assertEqual(grbl_machine_state("Off"), MachineState.OFFLINE)


if __name__ == "__main__":
    unittest.main()
