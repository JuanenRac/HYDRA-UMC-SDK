# =============================================================================
# HYDRA-UMC-SDK - Shared reading of the state word of a GRBL status report
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""One reading of the state word of a GRBL controller for every bridge that has one.

A GRBL v1.1 status report starts with the state (``Idle``, ``Run``, ``Hold:0``, ``Door:1``, ``Alarm``, ``Jog``, ``Home``, ``Check``, ``Sleep``). Hold and Door carry a numeric substate
after a colon, and a bridge that matched only the bare word would send a real controller to OFFLINE. The CNC and the laser bridge each kept their own copy of this table; this is
the one they share. Nothing here decides about safety: the gate still judges the state this function returns, and an unknown word is OFFLINE, never a state that allows work.
"""

from __future__ import annotations

from typing import Mapping

from .bridge_contract import MachineState

GRBL_STATES: Mapping[str, MachineState] = {
    "IDLE": MachineState.IDLE,
    "RUN": MachineState.RUNNING,
    "RUNNING": MachineState.RUNNING,
    "JOG": MachineState.RUNNING,
    "HOME": MachineState.RUNNING,
    "HOLD": MachineState.HOLDING,
    "PAUSED": MachineState.HOLDING,
    "STOPPED": MachineState.STOPPED,
    "ALARM": MachineState.FAULT,
    "FAULT": MachineState.FAULT,
    "ERROR": MachineState.FAULT,
    "DOOR": MachineState.SAFE_STOP,
}


def grbl_machine_state(word: object, extra: Mapping[str, MachineState] | None = None) -> MachineState:
    """The machine state for the state word of a GRBL report; the numeric substate after a colon is dropped and the case is ignored.

    `extra` lets a bridge add words of its own (the CNC bridge also takes OFF as a fault); it can add but never makes an unknown word allow work, because the result
    is still a MachineState that the gate judges. Anything that is not text, or a word nobody knows, is OFFLINE.
    """
    if not isinstance(word, str):
        return MachineState.OFFLINE
    token = word.strip().upper().split(":")[0]
    if extra and token in extra:
        return extra[token]
    return GRBL_STATES.get(token, MachineState.OFFLINE)
