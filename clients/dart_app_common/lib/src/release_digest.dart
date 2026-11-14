// =============================================================================
// HYDRA-UMC app common (Dart) - src/release_digest.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The check of a downloaded release asset against the digest that GitHub
// publishes for it, the same rule the Android app applies: a release that
// publishes no digest cannot be checked; one that publishes a digest must
// match it exactly. Pure Dart, so the apps and the tests share one rule.
// =============================================================================

import 'sha256.dart';

final RegExp _sha256Hex = RegExp(r'^[0-9a-f]{64}$');

/// The SHA-256 of an asset from the `digest` field of a GitHub release asset
/// (`sha256:<64 hex digits>`), in lower case. Anything else (empty, another
/// algorithm, a wrong length, non-hex characters) counts as "not published"
/// and gives `null`.
String? parseAssetDigest(String? raw) {
  final value = (raw ?? '').trim().toLowerCase();
  if (!value.startsWith('sha256:')) return null;
  final hex = value.substring('sha256:'.length);
  return _sha256Hex.hasMatch(hex) ? hex : null;
}

/// Whether [actual] (the SHA-256 of what was downloaded, in hex) is acceptable
/// for [expected] (from [parseAssetDigest]). With no expected digest nothing
/// can be compared and the answer is `true`, as it is in the Android app;
/// with one, it must be equal, ignoring the case.
bool digestMatches(String? expected, String actual) =>
    expected == null || expected.toLowerCase() == actual.trim().toLowerCase();

/// Checks the [bytes] of a download against the raw `digest` of its asset.
/// `true` when the release published no digest or the digest matches; `false`
/// when it published one and the bytes are not those of the release.
bool downloadMatchesDigest(List<int> bytes, String? rawDigest) =>
    digestMatches(parseAssetDigest(rawDigest), sha256Hex(bytes));
