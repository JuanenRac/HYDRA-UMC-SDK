# =============================================================================
# HYDRA-UMC-SDK - Error vocabulary of the MCU adapters
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The closed list of error codes an MCU adapter reports, with the safe action a planner proposes for each.

A component that recovers from a failure (the semantic planner, a dispatcher, a client) needs the same words as the adapter that fails. They are defined here once:
`INVALID_STATE`, `OUT_OF_RANGE`, `ESTOP_ACTIVE`, `TOOL_INCOMPATIBLE`, `TIMEOUT`, `UNSUPPORTED` and `GRIP_LOST_SEAL`. `default_action` gives the action proposed for a code;
a code that is not in the list is never guessed: it escalates to an operator, and a physical emergency stop is never cleared by software.

New codes need a meaning, a deterministic default action and a test; the meaning and the default action of an existing code do not change inside a minor release line.
"""

from __future__ import annotations

from dataclasses import dataclass

RETRY = "RETRY"
INCREASE_PRESSURE = "INCREASE_PRESSURE"
SWAP_TOOL = "SWAP_TOOL"
ABORT = "ABORT"
ESCALATE_TO_OPERATOR = "ESCALATE_TO_OPERATOR"

RECOVERY_ACTIONS: tuple[str, ...] = (RETRY, INCREASE_PRESSURE, SWAP_TOOL, ABORT, ESCALATE_TO_OPERATOR)


@dataclass(frozen=True)
class McuErrorCode:
    """One code of the vocabulary: what it means and what is proposed by default."""

    code: str
    meaning: str
    default_action: str


MCU_ERROR_CODES: tuple[McuErrorCode, ...] = (
    McuErrorCode("INVALID_STATE", "The reported component state is incompatible with the plan.", ABORT),
    McuErrorCode("OUT_OF_RANGE", "The request exceeds the declared range of the tool.", ABORT),
    McuErrorCode("ESTOP_ACTIVE", "A physical emergency stop is active.", ESCALATE_TO_OPERATOR),
    McuErrorCode("TOOL_INCOMPATIBLE", "The mounted tool cannot perform the request.", SWAP_TOOL),
    McuErrorCode("TIMEOUT", "No response arrived before the declared deadline.", RETRY),
    McuErrorCode("UNSUPPORTED", "The downstream component does not implement the request.", ESCALATE_TO_OPERATOR),
    McuErrorCode("GRIP_LOST_SEAL", "A declared gripper vacuum seal was lost.", INCREASE_PRESSURE),
)

_BY_CODE = {entry.code: entry for entry in MCU_ERROR_CODES}


def is_known_mcu_error(code: object) -> bool:
    """True only for a text that is exactly one of the codes of the vocabulary."""
    return isinstance(code, str) and code in _BY_CODE


def describe_mcu_error(code: object) -> McuErrorCode | None:
    """The entry of a code, or None when it is not in the vocabulary."""
    return _BY_CODE.get(code) if isinstance(code, str) else None


def default_mcu_error_action(code: object) -> str:
    """The action proposed for a code; anything that is not in the vocabulary escalates to an operator."""
    entry = describe_mcu_error(code)
    return entry.default_action if entry is not None else ESCALATE_TO_OPERATOR
