# =============================================================================
# HYDRA-UMC-SDK - Conformance vectors of the manifest signature (generator)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Builds conformance/fixtures/v1/manifest-signing-vectors.json. Ed25519 is deterministic, so the file is reproducible: the test compares it with this output.
The three seeds are TEST seeds written here on purpose (their public halves are in the vectors); they are not, and never become, a real key.
Run `py -3 manifest_signing_vectors.py --write` after changing a case."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from hydra_umc_sdk.manifest_signing import key_id_of, public_key_from_seed, sign_manifest

OUT = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1" / "manifest-signing-vectors.json"
SEED_OLD, SEED_CURRENT, SEED_NEXT, SEED_OTHER = (bytes([n]) * 32 for n in (0x11, 0x22, 0x33, 0x44))

MANIFEST = {
    "schema_version": "1.0",
    "project": "HYDRA-UMC-SERVER",
    "version": "0.2.4",
    "artifact_url": "https://github.com/JuanenRac/HYDRA-UMC-SERVER/releases/download/v0.2.4/server.tar.gz",
    "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    "min_bootloader": "0.1.0",
    "target": "h745-cm7",
}


def _entry(seed: bytes, state: str, not_before: str | None, not_after: str | None) -> dict:
    public = public_key_from_seed(seed)
    return {"key_id": key_id_of(public), "public": public.hex(), "state": state, "not_before": not_before, "not_after": not_after}


def build() -> dict:
    keys = {
        "schema": 1,
        "keys": [
            _entry(SEED_OLD, "retired", None, "2030-06-01T00:00:00Z"),
            _entry(SEED_CURRENT, "current", "2030-01-01T00:00:00Z", None),
            _entry(SEED_NEXT, "next", "2031-01-01T00:00:00Z", None),
            _entry(SEED_OTHER, "revoked", None, None),
        ],
    }
    good = sign_manifest(MANIFEST, SEED_CURRENT)
    tampered = copy.deepcopy(good)
    tampered["sha256"] = "f" * 64
    no_key_id = {k: v for k, v in good.items() if k != "key_id"}
    wrong_alg = dict(good, signature_alg="hmac-sha256")
    alg_without_signature = dict(MANIFEST, signature_alg="ed25519")
    short = dict(good, signature=good["signature"][:-2])
    stranger = sign_manifest(MANIFEST, bytes([0x55]) * 32)

    def case(name: str, manifest: dict, now: str, require: bool, accepted: bool, code: str) -> dict:
        return {"name": name, "manifest": manifest, "now": now, "require_asymmetric_signature": require, "accepted": accepted, "code": code}

    t = "2030-03-01T00:00:00Z"
    cases = [
        case("a good signature passes with the switch off", good, t, False, True, "ok"),
        case("a good signature passes with the switch on", good, t, True, True, "ok"),
        case("a changed manifest is refused with the switch off too", tampered, t, False, False, "bad_signature"),
        case("a changed manifest is refused with the switch on", tampered, t, True, False, "bad_signature"),
        case("a legacy manifest passes with the switch off", MANIFEST, t, False, True, "legacy"),
        case("a legacy manifest is refused with the switch on (downgrade)", MANIFEST, t, True, False, "downgrade_refused"),
        case("a stripped signature is the same as a legacy manifest", {k: v for k, v in good.items() if k != "signature"} | {"signature_alg": None, "key_id": None}, t, True, False, "downgrade_refused"),
        case("a signature algorithm without a signature is damaged", alg_without_signature, t, False, False, "malformed"),
        case("a signature without its key_id is damaged", no_key_id, t, False, False, "malformed"),
        case("another algorithm name is damaged, not legacy", wrong_alg, t, False, False, "malformed"),
        case("a short signature is damaged", short, t, False, False, "malformed"),
        case("a key that is not in the list is refused", stranger, t, False, False, "unknown_key"),
        case("the retired key still counts inside its grace period", sign_manifest(MANIFEST, SEED_OLD), "2030-05-31T23:59:59Z", True, True, "ok"),
        case("the retired key is refused after its grace period", sign_manifest(MANIFEST, SEED_OLD), "2030-06-01T00:00:00Z", True, False, "key_expired"),
        case("the next key is refused before its start", sign_manifest(MANIFEST, SEED_NEXT), t, False, False, "key_not_yet_valid"),
        case("the next key counts after its start", sign_manifest(MANIFEST, SEED_NEXT), "2031-01-01T00:00:00Z", True, True, "ok"),
        case("the current key is refused before its start", good, "2029-12-31T23:59:59Z", False, False, "key_not_yet_valid"),
        case("a revoked key is refused", sign_manifest(MANIFEST, SEED_OTHER), t, False, False, "key_revoked"),
    ]
    return {
        "about": "Conformance vectors of the UpdateManifest signature (hydra_umc_sdk.manifest_signing). Test keys only. A consumer in any language must give the same accepted and code for every case.",
        "keys": keys,
        "cases": cases,
    }


def render() -> str:
    return json.dumps(build(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    if "--write" in sys.argv:
        OUT.write_text(render(), encoding="utf-8", newline="\n")
        print("wrote", OUT)
    else:
        sys.stdout.write(render())
