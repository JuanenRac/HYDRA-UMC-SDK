// =============================================================================
// HYDRA-UMC app common (Dart) - test/ed25519_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// SHA-512 and Ed25519 in plain Dart against the published vectors (FIPS 180-4
// sizes around the padding limits, RFC 8032 tests 1 to 3, vectors made by the Python
// reference of the firmware tools, checked against a second implementation) and against keys made here at run time.
// =============================================================================

import 'dart:typed_data';

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

List<int> hex(String s) => [for (var i = 0; i < s.length; i += 2) int.parse(s.substring(i, i + 2), radix: 16)];
String toHex(List<int> b) => b.map((x) => x.toRadixString(16).padLeft(2, '0')).join();
List<int> pattern(int n) => [for (var i = 0; i < n; i++) (i * 7 + 1) & 255];

void main() {
  group('SHA-512', () {
    final vectors = <int, String>{
      0: 'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e',
      3: 'e3e811b3993a662d9b9b625208626836ec682ab11e6b6691fec762b3a54aad3e08f3e7eaed4584327de1168621179af623bbe26acb907d3279c7ad14e1a4e97e',
      111: '3dfde1184fd99f233f98be4250f4edb9b535157909b668334370742204d97e047f1fd6a74bb5ba447f337286f421d9af957811f7ef62a458771457da126cb65e',
      112: 'acc96c509e6d01787330a4c6a241e2cda9dcc2529dbe4288dbbcc3812133233c4698831127cf6ed0b333632b22715a5ce53a0a1002a684367b71c98aa6d1d900',
      113: '4ede4e315b6ca9754af594de49c76f096a1ff4f52a1f26644c25fb45bce727e428ed971dbdde70738ba0b45eb58c2bc637083626b692e24c0a2396c2b354659c',
      128: '31f33a52b36dc2e70c83b604fa999a5cabf33bf70e4556fbed7bff10870c1b7b241dd3f15d1ade24599f068fc58ab51e0028b0f0c98895c23358e8dee032ce06',
      300: '233b3cf1f69d5cf44ea3ac1ab6c3dd2a08a791fcd6f75f7b773be0a9116ba830bf1df9aed0c2e36ba3dba8bf04ce24830e420e733297b0d0884385896a54a199',
    };
    vectors.forEach((n, digest) {
      test('$n bytes', () => expect(toHex(sha512(pattern(n))), digest));
    });
    test('abc', () {
      expect(
        toHex(sha512('abc'.codeUnits)),
        'ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f',
      );
    });
  });

  group('Ed25519', () {
    test('RFC 8032 test 1 (empty message): the public key, the signature and the check', () {
      final seed = hex('9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60');
      final pub = hex('d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a');
      final sig = hex(
        'e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b',
      );
      expect(ed25519PublicKey(seed), pub);
      expect(ed25519Sign(seed, const <int>[]), sig);
      expect(ed25519Verify(pub, const <int>[], sig), isTrue);
    });

    test('RFC 8032 tests 2 and 3 (one byte and two bytes)', () {
      final cases = [
        [
          '4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb',
          '3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c',
          '72',
          '92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00',
        ],
        [
          'c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7',
          'fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025',
          'af82',
          '6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a',
        ],
      ];
      for (final c in cases) {
        final seed = hex(c[0]);
        final message = hex(c[2]);
        expect(toHex(ed25519PublicKey(seed)), c[1]);
        expect(toHex(ed25519Sign(seed, message)), c[3]);
        expect(ed25519Verify(hex(c[1]), message, hex(c[3])), isTrue);
      }
    });

    test('a longer message made by the Python reference of the firmware tools (1000 bytes)', () {
      final seed = hex('176162fd64dca26e613ec9ff42b4f215c7d741dbac5f29ff3978c43d74b30549');
      final message = pattern(1000);
      final sig = hex(
        '5b082615b7afd1750749d5b0fa23f4e0c8e36f5d645bd084d045c7dfdca505858f70e941b5dd0d1e19fccb22ef60db840e7d3f977837b46ae154d21d5a68e005',
      );
      expect(ed25519Sign(seed, message), sig);
      expect(ed25519Verify(ed25519PublicKey(seed), message, sig), isTrue);
      expect(ed25519Verify(ed25519PublicKey(seed), [...message, 0], sig), isFalse);
    });

    test('a signature made by the Python reference of the firmware tools verifies', () {
      final pub = hex('d28981e878d1dccdd2ca4dde2c2cbf0ea6aad1e1bdd3a08a74e97ccb43b7ce49');
      final message = hex('48594452412d554d432072656c656173652061737365742062797465730001ff');
      final sig = hex('d950e20ca4434e5545f8990eb9b89cc28c891e2030101b7580234be73adb0727306ad98bbd484e8707b8f9ff3b17d9891036c05eb2327e8ba6950a1b443c8f0a');
      expect(ed25519Verify(pub, message, sig), isTrue);
      expect(ed25519PublicKey(hex('176162fd64dca26e613ec9ff42b4f215c7d741dbac5f29ff3978c43d74b30549')), pub);
      expect(ed25519Sign(hex('176162fd64dca26e613ec9ff42b4f215c7d741dbac5f29ff3978c43d74b30549'), message), sig);
    });

    test('keys made here: what is signed verifies and nothing else does', () {
      for (var n = 1; n <= 3; n++) {
        final seed = Uint8List.fromList(List<int>.generate(32, (i) => (i * 31 + n * 17) & 255));
        final pub = ed25519PublicKey(seed);
        final message = pattern(40 * n);
        final sig = ed25519Sign(seed, message);
        expect(ed25519Verify(pub, message, sig), isTrue);
        final other = List<int>.of(message)..[0] ^= 1;
        expect(ed25519Verify(pub, other, sig), isFalse);
        expect(ed25519Verify(pub, message, List<int>.of(sig)..[3] ^= 1), isFalse);
        expect(ed25519Verify(pub, message, List<int>.of(sig)..[40] ^= 1), isFalse);
        final anotherSeed = Uint8List.fromList(List<int>.generate(32, (i) => (i * 5 + n) & 255));
        expect(ed25519Verify(ed25519PublicKey(anotherSeed), message, sig), isFalse);
      }
    });

    test('malformed input is false, never an exception', () {
      final seed = Uint8List.fromList(List<int>.generate(32, (i) => i));
      final pub = ed25519PublicKey(seed);
      final sig = ed25519Sign(seed, const [1, 2, 3]);
      expect(ed25519Verify(pub.sublist(1), const [1, 2, 3], sig), isFalse);
      expect(ed25519Verify(pub, const [1, 2, 3], sig.sublist(1)), isFalse);
      expect(ed25519Verify(pub, const [1, 2, 3], [...sig, 0]), isFalse);
      expect(ed25519Verify(List<int>.filled(32, 0xff), const [1, 2, 3], sig), isFalse);
      // a scalar that is not below the group order
      expect(ed25519Verify(pub, const [1, 2, 3], [...sig.sublist(0, 32), ...List<int>.filled(32, 0xff)]), isFalse);
    });
  });
}
