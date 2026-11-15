// =============================================================================
// HYDRA-UMC app common (Dart) - src/release_feed.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// What an app asks of the release feed before it tells the person that a newer
// version exists or downloads anything: a stable release (not a draft, not a
// pre-release), a tag that is `vMAJOR.MINOR.PATCH` (four parts are accepted),
// newer than the installed version, the exact named asset and an HTTPS
// address. The same trust decisions as the Android app; the download itself is
// then checked with `verifyDownloadedRelease`. Pure Dart: no network here.
// =============================================================================

import 'dart:convert';

import 'release_digest.dart';

/// A stable version of two to four numeric parts; compares part by part.
class FeedVersion implements Comparable<FeedVersion> {
  const FeedVersion(this.parts);

  final List<int> parts;

  /// `1.2.3` or `v1.2.3.4`; anything else (suffixes, one part, five parts, signs) gives `null`.
  static FeedVersion? parseStable(String? raw) {
    var text = (raw ?? '').trim();
    if (text.startsWith('v') || text.startsWith('V')) text = text.substring(1);
    final pieces = text.split('.');
    if (pieces.length < 3 || pieces.length > 4) return null;
    final parts = <int>[];
    for (final piece in pieces) {
      if (!RegExp(r'^[0-9]{1,9}$').hasMatch(piece)) return null;
      parts.add(int.parse(piece));
    }
    return FeedVersion(parts);
  }

  @override
  int compareTo(FeedVersion other) {
    for (var i = 0; i < 4; i++) {
      final a = i < parts.length ? parts[i] : 0;
      final b = i < other.parts.length ? other.parts[i] : 0;
      if (a != b) return a < b ? -1 : 1;
    }
    return 0;
  }

  @override
  bool operator ==(Object other) => other is FeedVersion && compareTo(other) == 0;

  @override
  int get hashCode => Object.hash(parts.isNotEmpty ? parts[0] : 0, parts.length > 1 ? parts[1] : 0,
      parts.length > 2 ? parts[2] : 0, parts.length > 3 ? parts[3] : 0);

  @override
  String toString() => parts.join('.');
}

/// A newer stable release with the asset the app named.
class AvailableRelease {
  const AvailableRelease({
    required this.version,
    required this.name,
    required this.notes,
    required this.pageUrl,
    required this.assetName,
    required this.assetUrl,
    required this.signatureUrl,
    required this.digest,
  });

  final FeedVersion version;
  final String name;
  final String notes;

  /// The address of the release page (`html_url`) when it is HTTPS, otherwise `null`: where an app that cannot
  /// install by itself sends the person.
  final String? pageUrl;

  /// The asset the app asked for, or `null` when it asked for none (a notice only).
  final String? assetName;
  final String? assetUrl;

  /// The address of `<asset>.sig` when the release carries one, otherwise `null`.
  final String? signatureUrl;

  /// The SHA-256 (hex) the feed publishes for the asset, or `null` when it publishes none.
  final String? digest;
}

/// The three ways the feed can answer.
sealed class ReleaseFeedResult {
  const ReleaseFeedResult();
}

class ReleaseUpToDate extends ReleaseFeedResult {
  const ReleaseUpToDate();
}

class ReleaseAvailable extends ReleaseFeedResult {
  const ReleaseAvailable(this.release);
  final AvailableRelease release;
}

class ReleaseFeedFailed extends ReleaseFeedResult {
  const ReleaseFeedFailed(this.reason);
  final ReleaseFeedProblem reason;
}

/// Why a feed answer cannot be used.
enum ReleaseFeedProblem {
  /// The feed could not be reached or answered with an error status (set by the app that asked, not by the rules).
  unreachable,

  /// The text is not a JSON object.
  notJson,

  /// The tag is not a stable version.
  badTag,

  /// The installed version is not a stable version.
  badInstalled,

  /// The release is newer but has no asset with the name the app asked for.
  noAsset,

  /// The address of the asset (or of its signature) is not HTTPS.
  notHttps,
}

String _str(Object? value) => value is String ? value : '';

/// Applies the trust decisions to the JSON of `releases/latest`. [installed] is the version of the running app
/// and [assetName] the exact name of the file the app can install. An app that publishes no installable file
/// (it only tells the person that a newer version exists) passes `null`: the asset checks are then skipped.
ReleaseFeedResult evaluateReleaseFeed(String payload, String installed, String? assetName) {
  final Object? decoded;
  try {
    decoded = jsonDecode(payload);
  } catch (_) {
    return const ReleaseFeedFailed(ReleaseFeedProblem.notJson);
  }
  if (decoded is! Map) return const ReleaseFeedFailed(ReleaseFeedProblem.notJson);
  if (decoded['draft'] == true || decoded['prerelease'] == true) return const ReleaseUpToDate();
  final remote = FeedVersion.parseStable(_str(decoded['tag_name']));
  if (remote == null) return const ReleaseFeedFailed(ReleaseFeedProblem.badTag);
  final local = FeedVersion.parseStable(installed);
  if (local == null) return const ReleaseFeedFailed(ReleaseFeedProblem.badInstalled);
  if (remote.compareTo(local) <= 0) return const ReleaseUpToDate();

  String? assetUrl;
  String? sigUrl;
  String? digest;
  if (assetName != null) {
    final assets = decoded['assets'] is List ? decoded['assets'] as List : const [];
    Map? asset;
    Map? signature;
    for (final item in assets) {
      if (item is! Map) continue;
      if (_str(item['name']) == assetName) asset ??= item;
      if (_str(item['name']) == '$assetName.sig') signature ??= item;
    }
    if (asset == null) return const ReleaseFeedFailed(ReleaseFeedProblem.noAsset);
    assetUrl = _str(asset['browser_download_url']);
    if (!assetUrl.startsWith('https://')) return const ReleaseFeedFailed(ReleaseFeedProblem.notHttps);
    final sig = signature == null ? '' : _str(signature['browser_download_url']);
    if (sig.isNotEmpty && !sig.startsWith('https://')) {
      return const ReleaseFeedFailed(ReleaseFeedProblem.notHttps);
    }
    sigUrl = sig.isEmpty ? null : sig;
    digest = parseAssetDigest(_str(asset['digest']));
  }
  final page = _str(decoded['html_url']);
  final name = decoded['name'];
  return ReleaseAvailable(AvailableRelease(
    version: remote,
    name: name is String && name.isNotEmpty ? name : 'v$remote',
    notes: _str(decoded['body']).trim(),
    pageUrl: page.startsWith('https://') ? page : null,
    assetName: assetName,
    assetUrl: assetUrl,
    signatureUrl: sigUrl,
    digest: digest,
  ));
}
