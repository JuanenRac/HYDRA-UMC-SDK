# =============================================================================
# HYDRA-UMC-SDK - Update compatibility tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The rule that keeps an image away from a board or a bootloader it was not built for."""

from __future__ import annotations

import unittest

from hydra_umc_sdk.update_compat import check_update_compat


class UpdateCompatTests(unittest.TestCase):
    def test_a_manifest_without_the_fields_forbids_nothing(self) -> None:
        self.assertEqual(check_update_compat({"version": "1.0.0"}, None, None), [])

    def test_a_matching_target_and_a_new_enough_bootloader_pass(self) -> None:
        manifest = {"target": "g474", "min_bootloader": "1.2.0"}
        for have in ("1.2.0", "1.10.0", "2.0.0"):
            self.assertEqual(check_update_compat(manifest, "g474", have), [], have)

    def test_another_target_is_refused(self) -> None:
        reasons = check_update_compat({"target": "h745-cm7"}, "g474", "1.0.0")
        self.assertEqual(len(reasons), 1)
        self.assertIn("h745-cm7", reasons[0])

    def test_a_board_that_does_not_say_its_target_is_refused(self) -> None:
        self.assertEqual(len(check_update_compat({"target": "g474"}, None, "1.0.0")), 1)
        self.assertEqual(len(check_update_compat({"target": "g474"}, "", "1.0.0")), 1)

    def test_an_older_bootloader_is_refused_comparing_numbers_not_text(self) -> None:
        self.assertEqual(len(check_update_compat({"min_bootloader": "1.10.0"}, None, "1.9.0")), 1)
        self.assertEqual(check_update_compat({"min_bootloader": "1.9.0"}, None, "1.10.0"), [])

    def test_a_fourth_component_is_compared(self) -> None:
        self.assertEqual(len(check_update_compat({"min_bootloader": "1.2.0.3"}, None, "1.2.0.2")), 1)
        self.assertEqual(check_update_compat({"min_bootloader": "1.2.0.3"}, None, "1.2.0.3"), [])
        self.assertEqual(check_update_compat({"min_bootloader": "1.2.0"}, None, "1.2.0.1"), [])

    def test_a_missing_or_unreadable_bootloader_version_is_refused(self) -> None:
        for have in (None, "", "v1.2.0", "1.2", "1.2.0-rc1"):
            self.assertEqual(len(check_update_compat({"min_bootloader": "1.0.0"}, None, have)), 1, have)

    def test_an_unreadable_minimum_is_refused_and_a_bad_target_and_bootloader_give_two_reasons(self) -> None:
        self.assertEqual(len(check_update_compat({"min_bootloader": "one"}, None, "1.0.0")), 1)
        self.assertEqual(len(check_update_compat({"target": "h745-cm7", "min_bootloader": "2.0.0"}, "g474", "1.0.0")), 2)


if __name__ == "__main__":
    unittest.main()
