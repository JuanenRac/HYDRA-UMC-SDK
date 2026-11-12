# =============================================================================
# HYDRA-UMC-SDK - Whether an update manifest fits the board and the bootloader it is meant for
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The compatibility rule of an `UpdateManifest`, as one function the updater calls before it flashes anything.

A manifest may carry `target` (the board family the image is built for, such as `g474` or `h745-cm7`) and `min_bootloader` (the oldest bootloader that can take the
image). `check_update_compat` compares them with the board in front of the updater and returns the reasons the image must not be flashed; an empty list means the
manifest does not forbid it. The rule is strict where it can be:

* a manifest with `target` and a board of another target is refused;
* a manifest with `target` and a board that did not say its target is refused (the updater cannot tell it fits);
* a manifest with `min_bootloader` and a bootloader older than that is refused, and so is one whose version is missing or unreadable;
* a manifest with neither field forbids nothing (the fields are optional in the contract).

This is the compatibility part only. It does not verify the signature: that needs the key, which the updater holds.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

_SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?")


def _version(text: Any) -> tuple[int, int, int, int] | None:
    if not isinstance(text, str):
        return None
    match = _SEMVER.fullmatch(text)
    return None if match is None else (int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4) or 0))


def check_update_compat(manifest: Mapping[str, Any], board_target: str | None, bootloader_version: str | None) -> list[str]:
    """Reasons the image of `manifest` must not be flashed on a board of `board_target` whose bootloader is `bootloader_version`; empty when none."""
    reasons: list[str] = []
    wanted_target = manifest.get("target")
    if wanted_target is not None:
        if not board_target:
            reasons.append(f"the image is for target {wanted_target} and the board did not say its target")
        elif board_target != wanted_target:
            reasons.append(f"the image is for target {wanted_target} and the board is {board_target}")
    minimum = manifest.get("min_bootloader")
    if minimum is not None:
        needed = _version(minimum)
        have = _version(bootloader_version)
        if needed is None:
            reasons.append(f"min_bootloader {minimum!r} is not MAJOR.MINOR.PATCH (or four parts)")
        elif have is None:
            reasons.append(f"the image needs bootloader {minimum} and the board did not give a readable bootloader version")
        elif have < needed:
            reasons.append(f"the image needs bootloader {minimum} and the board has {bootloader_version}")
    return reasons
