# =============================================================================
# HYDRA-UMC-SDK - Correlation of the answers to commands and the checks that go with a start command
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Two small shared rules for the commands of a bridge, so that every bridge reads them the same way.

* ``request_id``: the answer of ``cmd/<verb>/result`` is published on one topic, so two clients that sent a pause cannot tell which answer is theirs. A command may carry a
  ``request_id`` (text, at most 64 characters of letters, digits and ``-_.:``); ``answer_with_request_id`` copies it into the answer. A command without one gets the answer it always got.
* ``cmd/start`` metadata: a start command may name the file by its ``sha256`` and the print ``profile_id`` it was prepared for. ``parse_start_metadata`` validates both, so that the bridge
  can compare them with what the machine reports before it starts; a value that is present but malformed is an error, never ignored.

Pure standard library. Neither rule decides about safety.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping

from .bridge_contract import BridgeError

MAX_REQUEST_ID_CHARS = 64
_REQUEST_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")
_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
_PROFILE_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


def read_request_id(payload: Mapping[str, object]) -> str | None:
    """The request id of a command, or None when it has none. A request id that is present but not valid is refused with a BridgeError."""
    value = payload.get("request_id")
    if value is None:
        return None
    if not isinstance(value, str) or not _REQUEST_ID.match(value):
        raise BridgeError(f"request_id must be 1 to {MAX_REQUEST_ID_CHARS} characters of letters, digits and -_.:")
    return value


def answer_with_request_id(answer: Mapping[str, object], request_id: str | None) -> dict[str, object]:
    """A copy of `answer` that carries `request_id` (an answer that already has a different one is a bug and is refused)."""
    result = dict(answer)
    if request_id is None:
        return result
    if result.get("request_id", request_id) != request_id:
        raise BridgeError("the answer already carries another request_id")
    result["request_id"] = request_id
    return result


@dataclass(frozen=True)
class StartMetadata:
    """What a start command says about the file: `sha256` in lower case and `profile_id`, each None when the command did not carry it."""

    sha256: str | None = None
    profile_id: str | None = None

    @property
    def present(self) -> bool:
        return self.sha256 is not None or self.profile_id is not None


def parse_start_metadata(payload: Mapping[str, object]) -> StartMetadata:
    """Reads `sha256` and `profile_id` of a start command. Absent is fine (None); present and malformed is a BridgeError."""
    digest = payload.get("sha256")
    profile = payload.get("profile_id")
    if digest is not None and (not isinstance(digest, str) or not _SHA256.match(digest)):
        raise BridgeError("sha256 must be 64 hexadecimal characters")
    if profile is not None and (not isinstance(profile, str) or not _PROFILE_ID.match(profile)):
        raise BridgeError("profile_id must be 1 to 128 characters of letters, digits and -_.:")
    return StartMetadata(digest.lower() if isinstance(digest, str) else None, profile)


def start_matches(metadata: StartMetadata, *, file_sha256: str | None, profile_id: str | None) -> tuple[bool, str]:
    """Compares what the command named with what the machine reports. Whatever the command did not name is not checked; whatever it named and the machine cannot confirm is a mismatch."""
    if metadata.sha256 is not None:
        if file_sha256 is None:
            return False, "the command names a sha256 and the file has none to compare"
        if metadata.sha256 != file_sha256.lower():
            return False, "the sha256 of the file is not the one the command names"
    if metadata.profile_id is not None:
        if profile_id is None:
            return False, "the command names a profile and none is loaded"
        if metadata.profile_id != profile_id:
            return False, "the loaded profile is not the one the command names"
    return True, "ok"
