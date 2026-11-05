// =============================================================================
// HYDRA-UMC app common (Dart) - test/home_reset_rules_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The rules of HOME/RESET without a screen: the first reason not to send it, in the order a
// person can fix them, and the confirmation in steps within a time window.
// =============================================================================

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

HomeResetSituation _ok({
  bool switchedOn = true,
  bool connected = true,
  bool robotOnline = true,
  bool robotEnabled = true,
  bool robotPlaying = false,
  bool jogInFlight = false,
  bool stopInProgress = false,
  bool needsArming = false,
  String? role = 'operator',
  bool hasPose = true,
  bool serverSupports = true,
}) =>
    HomeResetSituation(
      switchedOn: switchedOn,
      connected: connected,
      robotOnline: robotOnline,
      robotEnabled: robotEnabled,
      robotPlaying: robotPlaying,
      jogInFlight: jogInFlight,
      stopInProgress: stopInProgress,
      needsArming: needsArming,
      role: role,
      hasPose: hasPose,
      serverSupports: serverSupports,
    );

void main() {
  group('homeResetBlockOf', () {
    test('nothing blocks a robot that is ready', () {
      expect(homeResetBlockOf(_ok()), HomeResetBlock.none);
    });

    test('each reason is reported on its own', () {
      expect(homeResetBlockOf(_ok(switchedOn: false)), HomeResetBlock.off);
      expect(homeResetBlockOf(_ok(connected: false)), HomeResetBlock.notConnected);
      expect(homeResetBlockOf(_ok(serverSupports: false)), HomeResetBlock.notSupported);
      expect(homeResetBlockOf(_ok(role: 'viewer')), HomeResetBlock.role);
      expect(homeResetBlockOf(_ok(robotOnline: false)), HomeResetBlock.offline);
      expect(homeResetBlockOf(_ok(robotEnabled: false)), HomeResetBlock.safeMode);
      expect(homeResetBlockOf(_ok(stopInProgress: true)), HomeResetBlock.stopPending);
      expect(homeResetBlockOf(_ok(robotPlaying: true)), HomeResetBlock.moving);
      expect(homeResetBlockOf(_ok(jogInFlight: true)), HomeResetBlock.jogBusy);
      expect(homeResetBlockOf(_ok(needsArming: true)), HomeResetBlock.notArmed);
      expect(homeResetBlockOf(_ok(hasPose: false)), HomeResetBlock.noPose);
    });

    test('the first reason a person can fix wins', () {
      expect(homeResetBlockOf(_ok(switchedOn: false, connected: false)), HomeResetBlock.off);
      expect(homeResetBlockOf(_ok(robotOnline: false, robotPlaying: true)), HomeResetBlock.offline);
    });

    test('a role that cannot be read is left to the server, and an administrator may', () {
      expect(homeResetRoleAllowed(null), isTrue);
      expect(homeResetRoleAllowed('admin'), isTrue);
      expect(homeResetRoleAllowed('guest'), isFalse);
    });
  });

  group('HomeResetConfirmation', () {
    test('needs every step in order and then reports done', () {
      var now = DateTime(2030);
      final c = HomeResetConfirmation(steps: 2, window: const Duration(seconds: 10), clock: () => now);
      expect(c.current, 1);
      expect(c.advance(), const HomeResetProgress.waiting(2));
      now = now.add(const Duration(seconds: 3));
      expect(c.current, 2);
      expect(c.advance().isDone, isTrue);
      expect(c.current, 1);
    });

    test('a step after the window starts over, and so does cancel', () {
      var now = DateTime(2030);
      final c = HomeResetConfirmation(steps: 2, window: const Duration(seconds: 10), clock: () => now);
      c.advance();
      now = now.add(const Duration(seconds: 11));
      expect(c.current, 1);
      expect(c.advance(), const HomeResetProgress.waiting(2));
      c.cancel();
      expect(c.current, 1);
    });

    test('fewer than one step counts as one', () {
      final c = HomeResetConfirmation(steps: 0, window: const Duration(seconds: 1));
      expect(c.advance().isDone, isTrue);
    });
  });
}
