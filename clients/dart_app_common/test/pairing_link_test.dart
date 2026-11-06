// =============================================================================
// HYDRA-UMC app common (Dart) - test/pairing_link_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// Reading the text of a pairing link (the QR code of the admin page of the server): what is accepted, and every way a link
// can be refused.
// =============================================================================

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

void main() {
  final fp = 'ab' * 32;

  PairingOffer ok(String text) {
    final result = PairingLink.parse(text);
    expect(result.isOk, isTrue, reason: '${result.problem}');
    return result.offer!;
  }

  PairingProblem? problem(String? text) => PairingLink.parse(text).problem;

  test('a complete link is read', () {
    final offer = ok('hydra-umc://pair?host=192.168.0.180&port=3000&fp=$fp&name=Workshop%20CM5');
    expect(offer.host, '192.168.0.180');
    expect(offer.port, 3000);
    expect(offer.fingerprint, fp);
    expect(offer.name, 'Workshop CM5');
    expect(offer.usesPinning, isTrue);
  });

  test('the fingerprint may carry colons and capitals', () {
    final spelled = [for (var i = 0; i < 32; i++) 'AB'].join(':');
    expect(ok('hydra-umc://pair?host=hydra.local&port=443&fp=$spelled').fingerprint, fp);
  });

  test('a link without name uses the host as name', () {
    final offer = ok('hydra-umc://pair?host=hydra.local&port=3000&fp=$fp');
    expect(offer.name, 'hydra.local');
  });

  test('a link without fingerprint is always refused', () {
    expect(problem('hydra-umc://pair?host=hydra.local&port=3000'), PairingProblem.missingFingerprint);
    expect(problem('hydra-umc://pair?host=hydra.local&port=3000&fp='), PairingProblem.missingFingerprint);
    expect(problem('hydra-umc://pair?host=hydra.local&port=3000&fp=%20%20'), PairingProblem.missingFingerprint);
    expect(problem('hydra-umc://pair?host=hydra.local&port=3000&name=Cell'), PairingProblem.missingFingerprint);
  });

  test('the scheme and the host are not case sensitive and spaces around are ignored', () {
    expect(ok('  HYDRA-UMC://PAIR?HOST=10.0.0.5&PORT=3000&FP=$fp  ').port, 3000);
  });

  test('an IPv6 address in brackets is read', () {
    expect(ok('hydra-umc://pair?host=%5Bfe80::1%5D&port=3000&fp=$fp').host, 'fe80::1');
  });

  test('other text is not a pairing link', () {
    expect(problem(null), PairingProblem.empty);
    expect(problem('   '), PairingProblem.empty);
    expect(problem('https://example.com/?host=a&port=1'), PairingProblem.notAPairingLink);
    expect(problem('hydra-umc://other?host=a&port=1'), PairingProblem.notAPairingLink);
    expect(PairingLink.looksLikePairing('WIFI:S:x;T:WPA;P:y;;'), isFalse);
    expect(PairingLink.looksLikePairing('hydra-umc://pair?host=a&port=1'), isTrue);
  });

  test('a host that is not a host is refused', () {
    expect(problem('hydra-umc://pair?port=3000'), PairingProblem.missingHost);
    expect(problem('hydra-umc://pair?host=300.1.1.1&port=3000'), PairingProblem.badHost);
    expect(problem('hydra-umc://pair?host=a%2Fb&port=3000'), PairingProblem.badHost);
    expect(problem('hydra-umc://pair?host=user%40evil.com&port=3000'), PairingProblem.badHost);
    expect(problem('hydra-umc://pair?host=-bad.local&port=3000'), PairingProblem.badHost);
  });

  test('a port outside the range is refused', () {
    expect(problem('hydra-umc://pair?host=a.local'), PairingProblem.badPort);
    expect(problem('hydra-umc://pair?host=a.local&port=0'), PairingProblem.badPort);
    expect(problem('hydra-umc://pair?host=a.local&port=65536'), PairingProblem.badPort);
    expect(problem('hydra-umc://pair?host=a.local&port=-1'), PairingProblem.badPort);
    expect(problem('hydra-umc://pair?host=a.local&port=80x'), PairingProblem.badPort);
    expect(ok('hydra-umc://pair?host=a.local&port=65535&fp=$fp').port, 65535);
  });

  test('a fingerprint that is not a SHA-256 is refused', () {
    expect(problem('hydra-umc://pair?host=a.local&port=1&fp=abcd'), PairingProblem.badFingerprint);
    expect(problem('hydra-umc://pair?host=a.local&port=1&fp=${'zz' * 32}'), PairingProblem.badFingerprint);
  });

  test('a repeated field is refused so a link cannot say two things', () {
    expect(problem('hydra-umc://pair?host=a.local&host=b.local&port=1'), PairingProblem.repeatedField);
  });

  test('unknown fields are ignored and never kept', () {
    final offer = ok('hydra-umc://pair?host=a.local&port=1&fp=$fp&token=secret&password=x');
    expect(offer.host, 'a.local');
    expect(offer.toString().contains('secret'), isFalse);
  });

  test('the name is bounded and has no control characters', () {
    expect(problem('hydra-umc://pair?host=a.local&port=1&fp=$fp&name=${'n' * (PairingLimits.standard.nameMax + 1)}'), PairingProblem.badName);
    expect(problem('hydra-umc://pair?host=a.local&port=1&fp=$fp&name=a%0Ab'), PairingProblem.badName);
    expect(ok('hydra-umc://pair?host=a.local&port=1&fp=$fp&name=${'n' * PairingLimits.standard.nameMax}').name.length, PairingLimits.standard.nameMax);
  });

  test('a broken percent encoding and a too long text are refused', () {
    expect(problem('hydra-umc://pair?host=a%zz&port=1'), PairingProblem.badEncoding);
    expect(problem('hydra-umc://pair?host=a.local&port=1&fp=$fp&name=${'x' * PairingLimits.standard.maxPayloadChars}'), PairingProblem.tooLong);
  });

  test('the fingerprint spelling is normalised the same way on its own', () {
    expect(normalizeFingerprint(fp.toUpperCase()), fp);
    expect(normalizeFingerprint('${'ab:' * 31}ab'), fp);
    expect(normalizeFingerprint('abcd'), isNull);
  });

  test('other limits can be given and are used', () {
    const tight = PairingLimits(nameMax: 3, portMax: 9000);
    expect(PairingLink.parse('hydra-umc://pair?host=a.local&port=9001&fp=$fp', limits: tight).problem, PairingProblem.badPort);
    expect(PairingLink.parse('hydra-umc://pair?host=a.local&port=9000&fp=$fp&name=abcd', limits: tight).problem, PairingProblem.badName);
    expect(PairingLink.parse('hydra-umc://pair?host=a.local&port=9000&fp=$fp&name=abc', limits: tight).isOk, isTrue);
  });
}
