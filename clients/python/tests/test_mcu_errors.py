# =============================================================================
# HYDRA-UMC-SDK - tests of the error vocabulary of the MCU adapters
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import unittest

from hydra_umc_sdk.mcu_errors import (
    ESCALATE_TO_OPERATOR,
    MCU_ERROR_CODES,
    RECOVERY_ACTIONS,
    default_mcu_error_action,
    describe_mcu_error,
    is_known_mcu_error,
)


class McuErrorVocabularyTests(unittest.TestCase):
    def test_the_vocabulary_is_closed_and_every_default_is_a_known_action(self):
        codes = [entry.code for entry in MCU_ERROR_CODES]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(len(codes), 7)
        for entry in MCU_ERROR_CODES:
            self.assertIn(entry.default_action, RECOVERY_ACTIONS)
            self.assertTrue(entry.meaning)

    def test_the_defaults_are_the_safe_ones(self):
        self.assertEqual(default_mcu_error_action("ESTOP_ACTIVE"), ESCALATE_TO_OPERATOR)
        self.assertEqual(default_mcu_error_action("UNSUPPORTED"), ESCALATE_TO_OPERATOR)
        self.assertEqual(default_mcu_error_action("OUT_OF_RANGE"), "ABORT")
        self.assertEqual(default_mcu_error_action("TIMEOUT"), "RETRY")
        self.assertEqual(default_mcu_error_action("GRIP_LOST_SEAL"), "INCREASE_PRESSURE")

    def test_an_unknown_code_is_never_guessed(self):
        for odd in ("estop_active", "ESTOP_ACTIVE ", "", "NOPE", None, 7, ["TIMEOUT"], b"TIMEOUT", {"TIMEOUT": 1}):
            self.assertFalse(is_known_mcu_error(odd))
            self.assertIsNone(describe_mcu_error(odd))
            self.assertEqual(default_mcu_error_action(odd), ESCALATE_TO_OPERATOR)

    def test_every_known_code_describes_itself(self):
        for entry in MCU_ERROR_CODES:
            self.assertTrue(is_known_mcu_error(entry.code))
            self.assertIs(describe_mcu_error(entry.code), entry)
            self.assertEqual(default_mcu_error_action(entry.code), entry.default_action)


if __name__ == "__main__":
    unittest.main()
