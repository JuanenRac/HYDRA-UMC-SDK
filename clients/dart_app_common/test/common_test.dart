// =============================================================================
// HYDRA-UMC app common (Dart) - test/common_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The shared code keeps the behaviour both apps relied on.
// =============================================================================

import 'dart:convert';

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

void main() {
  group('sha256Hex', () {
    test('matches the FIPS 180-4 vectors', () {
      expect(sha256Hex(<int>[]), 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');
      expect(sha256Hex(utf8.encode('abc')), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
      expect(
        sha256Hex(utf8.encode('abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq')),
        '248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1',
      );
    });
  });

  group('StopAllResult', () {
    test('reads a clean answer', () {
      final r = StopAllResult.fromJson({
        'success': true,
        'stoppedCount': 1,
        'failedCount': 0,
        'robots': [
          {'robotId': 1, 'name': 'A', 'stopped': true, 'valvesOff': 2, 'pumpsOff': 1},
        ],
      });
      expect(r.success, isTrue);
      expect(r.persisted, isTrue);
      expect(r.needsAttention, isFalse);
      expect(r.robots.single.valvesOff, 2);
    });

    test('counts come from the robots when the server omits them, and infinity is not a count', () {
      final r = StopAllResult.fromJson({
        'success': false,
        'stoppedCount': double.infinity,
        'robots': [
          {'robotId': 1, 'stopped': true},
          {'robotId': 2, 'stopped': false, 'error': 'x'},
        ],
      });
      expect(r.stoppedCount, 1);
      expect(r.failedCount, 1);
      expect(r.needsAttention, isTrue);
    });

    test('the fallback built from per-robot stops flags itself', () {
      final r = StopAllResult.fromRobots(
        [const StopAllRobot(robotId: 1, name: 'A', stopped: true)],
        viaFallback: true,
      );
      expect(r.success, isTrue);
      expect(r.viaFallback, isTrue);
    });

    test('an unsaved stop needs attention', () {
      final r = StopAllResult.fromJson({'success': true, 'persisted': false, 'robots': []});
      expect(r.needsAttention, isTrue);
    });
  });

  group('play confirmation rules', () {
    test('asks only when enabled and the robot is not playing', () {
      expect(playNeedsConfirmation(askBeforePlay: true, robotIsPlaying: false), isTrue);
      expect(playNeedsConfirmation(askBeforePlay: true, robotIsPlaying: true), isFalse);
      expect(playNeedsConfirmation(askBeforePlay: false, robotIsPlaying: false), isFalse);
    });

    test('speed percent and point count tolerate damaged data', () {
      expect(playSpeedPercent(double.nan), 0);
      expect(playSpeedPercent(-3), 0);
      expect(playSpeedPercent(49.6), 50);
      expect(recordedPointsCount({'recordedPoints': [1, 2]}), 2);
      expect(recordedPointsCount({'recordedPoints': 'x'}), 0);
    });
  });
}
