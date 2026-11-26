# =============================================================================
# HYDRA-UMC-SDK - The proof that a person confirmed one exact action
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `ConfirmationProof` contract: the proof that a person confirmed one exact action.

The layer that records a confirmation (the approval of a proposal, or the signed result of the voice interface) signs it with a key it shares with the layer that
acts. The layer that acts calls `verify_confirmation_proof` with the action it is about to take, the subject it is for and the key: only a genuine, current proof for
exactly that action and subject passes. The schema alone proves nothing, because it cannot check a signature, so a consumer never acts on `validate` alone.

The signature is HMAC-SHA256 over a message made of length-prefixed parts (`<bytes>:<text>`), so no two different proofs can build the same message.

**What the fields name.** `subject_id` is the machine the action is for, as the layer that acts knows it: the robot id of a trajectory; for a spoken command, the robot
it names, or the id of the installation when it names none. `action_id` is the fingerprint of a trajectory, or the request id of a spoken command. A name that does
not fit the identifier pattern is replaced by `proof_identifier`. **The key** is a file of one line of at least 32 characters, mode 600 (`load_confirmation_key`),
one per `kind`, shared by the layer that records that kind and the layer that acts; it is not the key of the proposals, of the commands or of the global stop.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import time
from typing import Any

from .contract_rules import check_fields, identifier, one_of, require_object, whole
from .signed_commands import CommandSigningError, load_key
from .validation import ContractValidationError

KINDS = ("approval", "voice")
MAX_PROOF_VALIDITY_MS = 3_600_000  # a proof that counts for more than an hour is refused by the verifier
FUTURE_TOLERANCE_MS = 5_000  # a clock that is a few seconds ahead is not a forged proof
_REQUIRED = ("schema_version", "kind", "action_id", "subject_id", "operator", "approved_at_ms", "expires_at_ms", "signature")
_OPTIONAL = ("approval_id",)
_APPROVAL_ID = re.compile(r"[0-9a-f]{32}")
_SIGNATURE = re.compile(r"[0-9a-f]{64}")
_IDENTIFIER = re.compile(r"[A-Za-z0-9._:-]{1,64}")
_TAG = "hydra-umc-confirmation-proof-v1"


def proof_identifier(text: str) -> str:
    """`text` when it fits the identifier of a proof, else `sha256:` and the first 57 hexadecimal digits of its SHA-256 (an operator written as an e-mail address)."""
    if not isinstance(text, str) or not text:
        raise ContractValidationError("an identifier of a proof cannot be empty")
    return text if _IDENTIFIER.fullmatch(text) else "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:57]


def load_confirmation_key(path: str) -> bytes:
    """The key of a proof from its file (the rules of the key of a signed command: one line, at least 32 characters, not readable by others)."""
    try:
        return load_key(path)
    except CommandSigningError as error:
        raise ContractValidationError(str(error).replace("command key", "confirmation key")) from error


def validate_confirmation_proof(payload: dict[str, Any]) -> None:
    """The checks of the ConfirmationProof contract (the shape; the signature is checked by `verify_confirmation_proof`)."""
    require_object(payload)
    check_fields(payload, _REQUIRED, _OPTIONAL)
    one_of(payload, "kind", KINDS)
    for name in ("action_id", "subject_id", "operator"):
        identifier(payload, name)
    whole(payload, "approved_at_ms", 0)
    whole(payload, "expires_at_ms", 0)
    if "approval_id" in payload and not (isinstance(payload["approval_id"], str) and _APPROVAL_ID.fullmatch(payload["approval_id"])):
        raise ContractValidationError("approval_id must be 32 lowercase hexadecimal digits")
    if not (isinstance(payload["signature"], str) and _SIGNATURE.fullmatch(payload["signature"])):
        raise ContractValidationError("signature must be 64 lowercase hexadecimal digits")


def _part(text: str) -> bytes:
    raw = text.encode("utf-8")
    return str(len(raw)).encode("ascii") + b":" + raw


def proof_message(proof: dict[str, Any]) -> bytes:
    """The bytes that are signed: every field except the signature, in a fixed order; a missing approval_id is an empty part."""
    parts = (_TAG, proof["kind"], proof["action_id"], proof["subject_id"], proof["operator"], str(proof["approved_at_ms"]), str(proof["expires_at_ms"]), proof.get("approval_id", ""))
    return b"".join(_part(part) for part in parts)


def sign_confirmation_proof(key: bytes, *, kind: str, action_id: str, subject_id: str, operator: str, approved_at_ms: int, expires_at_ms: int, approval_id: str | None = None) -> dict[str, Any]:
    """A signed proof; it is validated before it is returned, so a layer cannot sign a shape the others would refuse."""
    if not isinstance(key, (bytes, bytearray)) or len(key) < 16:
        raise ContractValidationError("the signing key must be at least 16 bytes")
    proof: dict[str, Any] = {
        "schema_version": "1.0",
        "kind": kind,
        "action_id": action_id,
        "subject_id": subject_id,
        "operator": operator,
        "approved_at_ms": approved_at_ms,
        "expires_at_ms": expires_at_ms,
    }
    if approval_id is not None:
        proof["approval_id"] = approval_id
    proof["signature"] = "0" * 64
    validate_confirmation_proof(proof)
    proof["signature"] = hmac.new(bytes(key), proof_message(proof), hashlib.sha256).hexdigest()
    return proof


def verify_confirmation_proof(
    key: bytes,
    proof: Any,
    *,
    expected_action_id: str,
    expected_subject_id: str,
    now_ms: int | None = None,
    require_approval_id: bool = False,
) -> tuple[bool, str]:
    """(True, '') when the proof is genuine, current, and for exactly this action and subject; otherwise (False, why). The layer that acts calls this."""
    now = int(time.time() * 1000) if now_ms is None else now_ms
    try:
        validate_confirmation_proof(proof)
    except ContractValidationError:
        return False, "the proof is not a well formed confirmation"
    if not isinstance(key, (bytes, bytearray)) or len(key) < 16:
        return False, "no usable key to check the proof"
    expected = hmac.new(bytes(key), proof_message(proof), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected.encode("ascii"), proof["signature"].encode("ascii")):
        return False, "the signature of the proof does not match"
    if not expected_action_id or proof["action_id"] != expected_action_id:
        return False, "the proof is for a different action"
    if not expected_subject_id or proof["subject_id"] != expected_subject_id:
        return False, "the proof is for a different subject"
    if proof["expires_at_ms"] <= proof["approved_at_ms"] or proof["expires_at_ms"] - proof["approved_at_ms"] > MAX_PROOF_VALIDITY_MS:
        return False, "the validity of the proof is not acceptable"
    if proof["approved_at_ms"] > now + FUTURE_TOLERANCE_MS:
        return False, "the proof was given in the future"
    if now >= proof["expires_at_ms"]:
        return False, "the proof has expired"
    if require_approval_id and "approval_id" not in proof:
        return False, "the proof has no identity to accept it only once"
    return True, ""
