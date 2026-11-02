# =============================================================================
# HYDRA-UMC-SDK - tests of the error vocabulary of the MCU adapters
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from hydra_umc_sdk.mcu_errors import (
    ESCALATE_TO_OPERATOR,
    MCU_ERROR_CODES,
    RECOVERY_ACTIONS,
    default_mcu_error_action,
    describe_mcu_error,
    is_known_mcu_error,
)


def test_the_vocabulary_is_closed_and_every_default_is_a_known_action():
    codes = [entry.code for entry in MCU_ERROR_CODES]
    assert len(codes) == len(set(codes)) == 7
    assert all(entry.default_action in RECOVERY_ACTIONS and entry.meaning for entry in MCU_ERROR_CODES)


def test_the_defaults_are_the_safe_ones():
    assert default_mcu_error_action("ESTOP_ACTIVE") == ESCALATE_TO_OPERATOR
    assert default_mcu_error_action("UNSUPPORTED") == ESCALATE_TO_OPERATOR
    assert default_mcu_error_action("OUT_OF_RANGE") == "ABORT"
    assert default_mcu_error_action("TIMEOUT") == "RETRY"
    assert default_mcu_error_action("GRIP_LOST_SEAL") == "INCREASE_PRESSURE"


def test_an_unknown_code_is_never_guessed():
    for odd in ("estop_active", "ESTOP_ACTIVE ", "", "NOPE", None, 7, ["TIMEOUT"]):
        assert not is_known_mcu_error(odd)
        assert describe_mcu_error(odd) is None
        assert default_mcu_error_action(odd) == ESCALATE_TO_OPERATOR
