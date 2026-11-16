// =============================================================================
// HYDRA-UMC app common (Dart) - test/listen_only_gate_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// Listen-only mode at the door of the network: every write is refused with a 423, except STOP, the sign-in and the
// renewal and end of the session; reads go through. The rule is shared by the iOS app and the display app.
// =============================================================================

import 'dart:convert';

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

String _cmd(String command) => jsonEncode({'command': command});

void main() {
  tearDown(() => ListenOnlyGate.enabled = false);

  test('it is off until a switch turns it on', () {
    expect(ListenOnlyGate.enabled, isFalse);
  });

  test('reads, STOP and the session are allowed', () {
    expect(ListenOnlyGate.allows('GET', '/api/settings', null), isTrue);
    expect(ListenOnlyGate.allows('head', '/api/settings', null), isTrue);
    expect(ListenOnlyGate.allows('POST', '/api/stop-all', null), isTrue);
    for (final c in ['stop', 'jogStop', 'disable']) {
      expect(ListenOnlyGate.allows('POST', '/api/robot/3/command', _cmd(c)), isTrue, reason: c);
    }
    for (final p in ['/api/login', '/api/refresh', '/api/logout', '/api/device/login']) {
      expect(ListenOnlyGate.allows('POST', p, '{}'), isTrue, reason: p);
    }
  });

  test('every other robot command and every write of the administration is refused', () {
    for (final c in ['jog', 'jogStart', 'play', 'pause', 'reset', 'enable', 'tool', 'valve', 'pump', 'speed', 'vision']) {
      expect(ListenOnlyGate.allows('POST', '/api/robot/3/command', _cmd(c)), isFalse, reason: c);
    }
    expect(ListenOnlyGate.allows('POST', '/api/robot/3/command', 'not json'), isFalse);
    expect(ListenOnlyGate.allows('POST', '/api/robot/3/command', jsonEncode([1])), isFalse);
    expect(ListenOnlyGate.allows('POST', '/api/robot/3/command', null), isFalse);
    for (final w in [
      ['POST', '/api/settings'], ['PUT', '/api/settings'], ['POST', '/api/system/reboot'], ['DELETE', '/api/users/bob'],
      ['POST', '/api/push/device'], ['POST', '/api/presence'], ['POST', '/api/claims'], ['PUT', '/api/server/config'],
      ['POST', '/'], ['POST', ''], ['POST', '/other/login'], ['POST', '/api/robot/3/other'], ['POST', '/api/login/extra'],
    ]) {
      expect(ListenOnlyGate.allows(w[0], w[1], '{}'), isFalse, reason: '${w[0]} ${w[1]}');
    }
  });

  test('the refusal is a 423 with the listen-only code, in the words of the device', () {
    final app = ListenOnlyGate.refusal('/api/settings');
    expect(app.statusCode, 423);
    expect(app.path, '/api/settings');
    expect(jsonDecode(app.body)['code'], 'listen-only');
    expect(jsonDecode(app.body)['error'], contains('from this app'));
    final panel = ListenOnlyGate.refusal('/api/settings', device: 'panel');
    expect(jsonDecode(panel.body)['error'], contains('from this panel'));
  });

  test('the controls are dimmed only while the mode is on', () {
    expect(ListenOnlyGate.controlOpacity(false), 1.0);
    expect(ListenOnlyGate.controlOpacity(true), ListenOnlyGate.dimmedOpacity);
    expect(ListenOnlyGate.dimmedOpacity, inInclusiveRange(0.2, 0.6));
  });

  test('the mode holds for a server by the general switch or by the list', () {
    final key = ListenOnlyGate.serverKey('10.0.0.5', 18080);
    expect(key, '10.0.0.5:18080');
    expect(ListenOnlyGate.effective(false, {}, key), isFalse);
    expect(ListenOnlyGate.effective(false, {key}, key), isTrue);
    expect(ListenOnlyGate.effective(false, {key}, null), isFalse);
    expect(ListenOnlyGate.effective(true, {}, null), isTrue);
  });

  test('the stored list is cleaned and bounded', () {
    expect(ListenOnlyGate.cleanServers(['a:1', '', ' b:2', 'c:3 ', 'x' * 201, 'd:4']), {'a:1', 'd:4'});
    final many = List.generate(ListenOnlyGate.maxServers + 20, (i) => 'h$i:1');
    expect(ListenOnlyGate.cleanServers(many).length, ListenOnlyGate.maxServers);
  });
}
