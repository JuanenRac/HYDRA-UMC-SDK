# =============================================================================
# HYDRA-UMC-SDK - Incident transport: the signed envelope that carries an evidence bundle
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `incident-transport/1` message: a typed envelope for the `EvidenceBundle` of `evidence_bundle.py`.

A node that has an incident it cannot solve hands the development node a message with `contract_version`, `kind` ("incident"), `to_node`, `sent_at` (seconds), a `nonce`,
a `payload` with the `escalationId` and the `evidenceBundle`, and a `mac`: the HMAC-SHA256 (hex) of the canonical JSON of the message without its `mac`. This module builds and
checks it, so that the writer and the reader share one definition instead of a loose dictionary. The reader supplies what only it knows: the secret, its own node name, the clock
and a function that remembers nonces (`remember_nonce` returns False for a nonce already seen, which is a replay). No secret is stored here and none is ever put in an error.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from typing import Any, Callable, Mapping

from .evidence_bundle import bundle_matches_checksum
from .validation import ContractValidationError

CONTRACT_VERSION = "incident-transport/1"
KIND_INCIDENT = "incident"
MIN_SECRET_LENGTH = 24
DEFAULT_MAX_CLOCK_SKEW_SECONDS = 300.0
_ESCALATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


class IncidentTransportError(ContractValidationError):
    """The message is refused; the text says why and never contains the secret."""


def _need_secret(secret: str) -> bytes:
    if not isinstance(secret, str) or len(secret) < MIN_SECRET_LENGTH:
        raise IncidentTransportError(f"the transport secret is missing or shorter than {MIN_SECRET_LENGTH} characters")
    return secret.encode("utf-8")


def sign_message(body: Mapping[str, Any], secret: str) -> str:
    """The `mac` of a message: HMAC-SHA256 (hex) of its canonical JSON without the `mac` field."""
    canonical = json.dumps({key: value for key, value in body.items() if key != "mac"}, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac.new(_need_secret(secret), canonical, hashlib.sha256).hexdigest()


def build_incident_message(bundle: Mapping[str, Any], escalation_id: str, to_node: str, nonce: str, sent_at: float, secret: str) -> dict[str, Any]:
    """A signed incident message for an already sealed bundle (`seal_bundle`). Refuses a bundle whose checksum is not its content."""
    if not isinstance(escalation_id, str) or not _ESCALATION_ID.match(escalation_id):
        raise IncidentTransportError("the escalation id must be a plain identifier")
    if not isinstance(to_node, str) or not to_node.strip() or not isinstance(nonce, str) or not nonce:
        raise IncidentTransportError("to_node and nonce must be non-empty texts")
    if isinstance(sent_at, bool) or not isinstance(sent_at, (int, float)):
        raise IncidentTransportError("sent_at must be a number of seconds")
    if not bundle_matches_checksum(dict(bundle)):
        raise IncidentTransportError("the checksum of the bundle is not that of its content")
    message: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "kind": KIND_INCIDENT,
        "to_node": to_node,
        "sent_at": sent_at,
        "nonce": nonce,
        "payload": {"escalationId": escalation_id, "evidenceBundle": dict(bundle)},
    }
    message["mac"] = sign_message(message, secret)
    return message


def verify_incident_message(
    message: object,
    *,
    secret: str,
    expected_to_node: str,
    now: float,
    remember_nonce: Callable[[str], bool],
    max_clock_skew_seconds: float = DEFAULT_MAX_CLOCK_SKEW_SECONDS,
) -> tuple[str, dict[str, Any]]:
    """Checks a message and returns the escalation id and the bundle. The signature is checked first and the nonce is remembered last, so a refused message never uses one up."""
    if not isinstance(message, dict):
        raise IncidentTransportError("the message is not a JSON object")
    mac = message.get("mac")
    if not isinstance(mac, str) or not hmac.compare_digest(mac, sign_message(message, secret)):
        raise IncidentTransportError("the signature of the message is wrong")
    if message.get("contract_version") != CONTRACT_VERSION or message.get("kind") != KIND_INCIDENT:
        raise IncidentTransportError("the message is not an incident of incident-transport/1")
    if message.get("to_node") != expected_to_node:
        raise IncidentTransportError("the message is addressed to another node")
    sent_at = message.get("sent_at")
    if isinstance(sent_at, bool) or not isinstance(sent_at, (int, float)) or abs(now - sent_at) > max_clock_skew_seconds:
        raise IncidentTransportError("the message is too old or too new")
    nonce = message.get("nonce")
    if not isinstance(nonce, str) or not nonce:
        raise IncidentTransportError("the message has no nonce")
    payload = message.get("payload")
    if not isinstance(payload, dict) or not isinstance(payload.get("evidenceBundle"), dict):
        raise IncidentTransportError("the message carries no evidence bundle")
    escalation_id = payload.get("escalationId")
    if not isinstance(escalation_id, str) or not _ESCALATION_ID.match(escalation_id):
        raise IncidentTransportError("the escalation id of the message is not a plain identifier")
    bundle = payload["evidenceBundle"]
    try:
        matches = bundle_matches_checksum(bundle)
    except ContractValidationError as error:
        raise IncidentTransportError(f"the bundle is not a valid EvidenceBundle: {error}") from error
    if not matches:
        raise IncidentTransportError("the checksum of the bundle is not that of its content")
    if not remember_nonce(nonce):
        raise IncidentTransportError("the message was already received (replay)")
    return escalation_id, bundle
