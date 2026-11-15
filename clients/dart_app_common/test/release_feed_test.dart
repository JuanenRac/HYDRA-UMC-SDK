// =============================================================================
// HYDRA-UMC app common (Dart) - test/release_feed_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The trust decisions on the release feed before an app tells the person about a newer version: the same as the
// Android app's.
// =============================================================================

import 'dart:convert';

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

const String _asset = 'HYDRA-UMC-IOS-CONTROL-release.ipa';
const String _hex = 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad';

String _feed({
  String tag = 'v1.2.0',
  bool draft = false,
  bool prerelease = false,
  Object? assets,
  Object? name = 'Release 1.2.0',
}) =>
    jsonEncode({
      'tag_name': tag,
      'name': name,
      'body': '  Notes here.  ',
      'html_url': 'https://example.test/releases/tag/$tag',
      'draft': draft,
      'prerelease': prerelease,
      'assets': assets ??
          [
            {'name': _asset, 'browser_download_url': 'https://example.test/$_asset', 'digest': 'sha256:$_hex'},
            {'name': '$_asset.sig', 'browser_download_url': 'https://example.test/$_asset.sig'},
          ],
    });

void main() {
  group('FeedVersion', () {
    test('reads three and four numeric parts, with or without v', () {
      expect(FeedVersion.parseStable('v1.2.3').toString(), '1.2.3');
      expect(FeedVersion.parseStable('0.8.0.1').toString(), '0.8.0.1');
      expect(FeedVersion.parseStable(' V10.0.0 ').toString(), '10.0.0');
    });

    test('anything else is not stable', () {
      for (final raw in <String?>[null, '', '1', '1.2', '1.2.3.4.5', '1.2.3-rc1', '1.x.3', '-1.2.3', '1..3', '1.2.3+b']) {
        expect(FeedVersion.parseStable(raw), isNull, reason: '$raw');
      }
    });

    test('compares part by part and a missing fourth part is zero', () {
      FeedVersion v(String s) => FeedVersion.parseStable(s)!;
      expect(v('1.2.4').compareTo(v('1.2.3')), 1);
      expect(v('1.2.3').compareTo(v('1.10.0')), -1);
      expect(v('1.2.3'), v('1.2.3.0'));
      expect(v('1.2.3.1').compareTo(v('1.2.3')), 1);
      expect(v('1.2.3').hashCode, v('1.2.3.0').hashCode);
    });
  });

  group('evaluateReleaseFeed', () {
    test('a newer stable release with the named asset is available', () {
      final result = evaluateReleaseFeed(_feed(), '1.1.9', _asset);
      expect(result, isA<ReleaseAvailable>());
      final r = (result as ReleaseAvailable).release;
      expect(r.version.toString(), '1.2.0');
      expect(r.name, 'Release 1.2.0');
      expect(r.notes, 'Notes here.');
      expect(r.pageUrl, 'https://example.test/releases/tag/v1.2.0');
      expect(r.assetUrl, 'https://example.test/$_asset');
      expect(r.signatureUrl, 'https://example.test/$_asset.sig');
      expect(r.digest, _hex);
    });

    test('the same or an older version is up to date', () {
      expect(evaluateReleaseFeed(_feed(), '1.2.0', _asset), isA<ReleaseUpToDate>());
      expect(evaluateReleaseFeed(_feed(), '2.0.0', _asset), isA<ReleaseUpToDate>());
    });

    test('drafts and pre-releases are never offered', () {
      expect(evaluateReleaseFeed(_feed(draft: true), '1.0.0', _asset), isA<ReleaseUpToDate>());
      expect(evaluateReleaseFeed(_feed(prerelease: true), '1.0.0', _asset), isA<ReleaseUpToDate>());
    });

    ReleaseFeedProblem problem(ReleaseFeedResult r) => (r as ReleaseFeedFailed).reason;

    test('the reasons the app can name are all different', () {
      expect(ReleaseFeedProblem.values.toSet().length, 6);
      expect(const ReleaseFeedFailed(ReleaseFeedProblem.unreachable).reason, ReleaseFeedProblem.unreachable);
    });

    test('a bad payload, tag or installed version fails with its reason', () {
      expect(problem(evaluateReleaseFeed('nope', '1.0.0', _asset)), ReleaseFeedProblem.notJson);
      expect(problem(evaluateReleaseFeed('[1]', '1.0.0', _asset)), ReleaseFeedProblem.notJson);
      expect(problem(evaluateReleaseFeed(_feed(tag: 'nightly'), '1.0.0', _asset)), ReleaseFeedProblem.badTag);
      expect(problem(evaluateReleaseFeed(_feed(), 'dev', _asset)), ReleaseFeedProblem.badInstalled);
    });

    test('a newer release needs the exact asset over HTTPS', () {
      expect(problem(evaluateReleaseFeed(_feed(assets: []), '1.0.0', _asset)), ReleaseFeedProblem.noAsset);
      expect(problem(evaluateReleaseFeed(_feed(assets: [
        {'name': 'other.ipa', 'browser_download_url': 'https://example.test/other.ipa'}
      ]), '1.0.0', _asset)), ReleaseFeedProblem.noAsset);
      expect(problem(evaluateReleaseFeed(_feed(assets: [
        {'name': _asset, 'browser_download_url': 'http://example.test/$_asset'}
      ]), '1.0.0', _asset)), ReleaseFeedProblem.notHttps);
      expect(problem(evaluateReleaseFeed(_feed(assets: [
        {'name': _asset, 'browser_download_url': 'https://example.test/$_asset'},
        {'name': '$_asset.sig', 'browser_download_url': 'http://example.test/$_asset.sig'},
      ]), '1.0.0', _asset)), ReleaseFeedProblem.notHttps);
    });

    test('no signature and no digest are reported as missing, not invented', () {
      final result = evaluateReleaseFeed(_feed(assets: [
        {'name': _asset, 'browser_download_url': 'https://example.test/$_asset', 'digest': 'md5:abc'}
      ]), '1.0.0', _asset) as ReleaseAvailable;
      expect(result.release.signatureUrl, isNull);
      expect(result.release.digest, isNull);
    });

    test('a release without a name is called by its version', () {
      final result = evaluateReleaseFeed(_feed(name: null), '1.0.0', _asset) as ReleaseAvailable;
      expect(result.release.name, 'v1.2.0');
    });

    test('an app that asks for no asset gets a notice with the page of the release', () {
      final result = evaluateReleaseFeed(_feed(assets: []), '1.0.0', null) as ReleaseAvailable;
      expect(result.release.assetName, isNull);
      expect(result.release.assetUrl, isNull);
      expect(result.release.signatureUrl, isNull);
      expect(result.release.digest, isNull);
      expect(result.release.pageUrl, 'https://example.test/releases/tag/v1.2.0');
      expect(evaluateReleaseFeed(_feed(assets: []), '1.2.0', null), isA<ReleaseUpToDate>());
      expect(evaluateReleaseFeed(_feed(draft: true), '1.0.0', null), isA<ReleaseUpToDate>());
    });

    test('a page that is not HTTPS is not offered', () {
      final text = _feed(assets: []).replaceFirst('https://example.test/releases', 'http://example.test/releases');
      final result = evaluateReleaseFeed(text, '1.0.0', null) as ReleaseAvailable;
      expect(result.release.pageUrl, isNull);
    });

    test('odd shapes in the assets list are skipped', () {
      final result = evaluateReleaseFeed(_feed(assets: [
        7,
        {'name': 5},
        {'name': _asset, 'browser_download_url': 'https://example.test/$_asset'},
      ]), '1.0.0', _asset);
      expect(result, isA<ReleaseAvailable>());
    });
  });
}
