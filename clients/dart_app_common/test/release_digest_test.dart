// =============================================================================
// HYDRA-UMC app common (Dart) - test/release_digest_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The digest rule of the release asset, the same as the Android app's.
// =============================================================================

import 'dart:convert';

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

const String _abc = 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad';

void main() {
  group('parseAssetDigest', () {
    test('reads sha256:<hex> in any case and with spaces around it', () {
      expect(parseAssetDigest('sha256:$_abc'), _abc);
      expect(parseAssetDigest('  SHA256:${_abc.toUpperCase()}  '), _abc);
    });

    test('anything else is "not published"', () {
      for (final raw in <String?>[null, '', 'sha1:$_abc', 'sha256:', 'sha256:${_abc.substring(1)}', 'sha256:${_abc}0', 'sha256:${_abc.replaceFirst('b', 'z')}', _abc]) {
        expect(parseAssetDigest(raw), isNull, reason: '$raw');
      }
    });
  });

  group('digestMatches', () {
    test('with no expected digest nothing can be compared', () {
      expect(digestMatches(null, _abc), isTrue);
    });

    test('a published digest must be equal, ignoring the case', () {
      expect(digestMatches(_abc, _abc), isTrue);
      expect(digestMatches(_abc, _abc.toUpperCase()), isTrue);
      expect(digestMatches(_abc, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'), isFalse);
    });
  });

  group('downloadMatchesDigest', () {
    final bytes = utf8.encode('abc');

    test('accepts the bytes the release published', () {
      expect(downloadMatchesDigest(bytes, 'sha256:$_abc'), isTrue);
    });

    test('refuses bytes that are not those of the release', () {
      expect(downloadMatchesDigest(utf8.encode('abd'), 'sha256:$_abc'), isFalse);
      expect(downloadMatchesDigest(<int>[], 'sha256:$_abc'), isFalse);
    });

    test('a release without a digest is accepted, as in the Android app', () {
      expect(downloadMatchesDigest(bytes, null), isTrue);
      expect(downloadMatchesDigest(bytes, 'sha1:$_abc'), isTrue);
    });
  });
}
