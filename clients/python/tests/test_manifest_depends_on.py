# =============================================================================
# HYDRA-UMC-SDK - depends_on field of the project manifest
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from hydra_umc_sdk import ContractValidationError, validate

FIXTURE = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1" / "project-manifest.valid.json"


def _manifest(**changes):
    payload = copy.deepcopy(json.loads(FIXTURE.read_text(encoding="utf-8")))
    payload.update(changes)
    return payload


class DependsOnTests(unittest.TestCase):
    def test_a_manifest_without_the_field_is_still_valid(self):
        validate("ProjectManifest", _manifest())

    def test_a_list_of_other_repositories_is_valid(self):
        validate("ProjectManifest", _manifest(depends_on=["HYDRA-UMC-OS", "URTC-COMMON"]))

    def test_an_empty_list_is_valid(self):
        validate("ProjectManifest", _manifest(depends_on=[]))

    def test_the_repository_cannot_depend_on_itself(self):
        with self.assertRaises(ContractValidationError):
            validate("ProjectManifest", _manifest(depends_on=["HYDRA-UMC-SDK"]))

    def test_repeated_or_malformed_names_are_refused(self):
        for bad in (["HYDRA-UMC-OS", "HYDRA-UMC-OS"], ["os"], [5], "HYDRA-UMC-OS", None):
            with self.subTest(bad=bad), self.assertRaises(ContractValidationError):
                validate("ProjectManifest", _manifest(depends_on=bad))


if __name__ == "__main__":
    unittest.main()
