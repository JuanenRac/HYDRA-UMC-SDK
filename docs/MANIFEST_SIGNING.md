# Signing the update manifest

The `UpdateManifest` names an artifact (`artifact_url`, `sha256`) and, optionally, the controller it is for (`target`) and the oldest bootloader it can be installed over (`min_bootloader`). Whoever can change a manifest changes what is installed, so the manifest carries an Ed25519 signature that a consumer can check against keys it trusts. The firmware images themselves are signed apart, by the bootloader format (see the bootloader trust table of HYDRA-UMC); this page is about the manifest.

## What is signed

The manifest without its `signature` field, written as canonical JSON: keys sorted, no spaces (separators `,` and `:`), UTF-8. `signature_alg` (`ed25519`) and `key_id` are part of what is signed, so neither can be removed or swapped without breaking the signature. `key_id` is the first eight bytes of the SHA-512 of the public key, in lowercase hexadecimal. The reference is `hydra_umc_sdk.manifest_signing` and the language-neutral vectors are `conformance/fixtures/v1/manifest-signing-vectors.json`: a consumer in any language must give the same `accepted` and `code` for every case.

## The list of trusted keys

A consumer reads a file of public keys, never a private one:

```json
{"schema": 1, "keys": [
  {"key_id": "<16 hex>", "public": "<64 hex>", "state": "current", "not_before": null, "not_after": null}
]}
```

`state` is `current` (signs now), `next` (published ahead of its use), `retired` (no longer signs, still trusted until `not_after`) or `revoked` (never trusted). `not_before` and `not_after` are UTC times such as `2030-01-01T00:00:00Z` or `null`; a key counts when `not_before <= now < not_after`. A list with a `key_id` that does not belong to its key, a repeated `key_id` or any unknown field is refused whole.

## Rotating the key

1. Add the new key as `next` with a `not_before` in the future, and ship the list to every consumer before that moment.
2. From `not_before` sign manifests with the new key (it now acts as `current`).
3. Move the old key to `retired` with a `not_after` that leaves time to install manifests published before the rotation.
4. After `not_after` the old key is refused (`key_expired`); remove it at the next list update.
5. After an incident mark the key `revoked`: it is refused at once, whatever its window.

## The switch `require_asymmetric_signature`

Off by default, so existing manifests keep working during the move.

| Manifest | Switch off | Switch on |
|---|---|---|
| Ed25519 signature that verifies | accepted (`ok`) | accepted (`ok`) |
| Ed25519 signature that does not verify, unknown, revoked, expired or not yet valid key | refused | refused |
| No signature (legacy) | accepted, labelled `legacy` | refused (`downgrade_refused`) |
| Algorithm or key named without a signature, wrong algorithm name, malformed signature | refused (`malformed`) | refused (`malformed`) |

A signature that is present is always checked, so turning the switch off never lets a forged signature through as if it were a legacy manifest. A damaged settings file counts as the switch on.
