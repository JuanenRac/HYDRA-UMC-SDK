// =============================================================================
// HYDRA-UMC app common (Dart) - test/hydra_error_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The typed error is shared; the wording is each app's.
// =============================================================================

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

void main() {
  test('a kind carries its raw parameters and no text', () {
    const e = HydraError(HydraErrorKind.txError, {'command': 'jog', 'error': 'boom'});
    expect(e.kind, HydraErrorKind.txError);
    expect(e.params['command'], 'jog');
    expect(const HydraError(HydraErrorKind.notConnected).params, isEmpty);
  });

  test('the kinds of both apps are in the shared enum', () {
    for (final name in ['systemActionFailed', 'deadManBlocked', 'workInvalidFile', 'pairingProblem', 'voiceAssistantFailed']) {
      expect(HydraErrorKind.values.asNameMap().containsKey(name), isTrue, reason: name);
    }
  });

  test('a read-only server is told apart from a robot in safe mode', () {
    final readOnly = HydraApiException('x', statusCode: 423, code: 'server-read-only');
    expect(readOnly.isServerReadOnly, isTrue);
    expect(readOnly.isRobotDisabled, isFalse);
    final disabled = HydraApiException('x', statusCode: 423, code: 'robot-disabled');
    expect(disabled.isRobotDisabled, isTrue);
    expect(disabled.isServerReadOnly, isFalse);
    expect(HydraApiException('x', statusCode: 423).isRobotDisabled, isTrue);
    expect(HydraApiException('x', statusCode: 403, code: 'server-read-only').isRobotDisabled, isFalse);
    expect(const HydraError(HydraErrorKind.serverReadOnly).params, isEmpty);
  });
}
