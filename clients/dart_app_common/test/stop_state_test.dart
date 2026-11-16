// =============================================================================
// HYDRA-UMC app common (Dart) - test/stop_state_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The stop-state message: how it is read, and that the socket hands it on.
// =============================================================================

import 'dart:async' show StreamController;
import 'dart:convert';
import 'dart:io';

import 'package:test/test.dart';

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';

Map<String, dynamic> _msg(String software, [Map<String, dynamic> extra = const {}]) => {
      'type': 'stop-state',
      'schema': 2,
      'state': {'state': 'STOPPED', 'physical': 'unknown', 'software': software, ...extra},
    };

void main() {
  test('a stop restored after a restart raises the notice', () {
    expect(StopStateNotice.restoredAfterRestart(_msg('stopped', {'restoredAfterRestart': true})), isTrue);
  });

  test('a stop pressed in this run or a released one does not', () {
    expect(StopStateNotice.restoredAfterRestart(_msg('stopped')), isFalse);
    expect(StopStateNotice.restoredAfterRestart(_msg('ready', {'restoredAfterRestart': true})), isFalse);
  });

  test('anything that is not a complete stop-state message leaves the notice as it was', () {
    expect(StopStateNotice.restoredAfterRestart({'type': 'claims'}), isNull);
    expect(StopStateNotice.restoredAfterRestart({'type': 'stop-state'}), isNull);
    expect(StopStateNotice.restoredAfterRestart({'type': 'stop-state', 'state': {'software': 'odd'}}), isNull);
  });

  test('the socket hands a stop-state message to onStopState and no other callback', () async {
    final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    final sockets = StreamController<WebSocket>.broadcast();
    server.listen((request) async {
      sockets.add(await WebSocketTransformer.upgrade(request, protocolSelector: (p) => 'hydra.bearer'));
    });
    final got = <Map<String, dynamic>>[];
    var settings = 0;
    final ws = HydraWebSocket(
      host: '127.0.0.1',
      port: server.port,
      token: 'tok',
      onStatus: (_) {},
      onSettings: (_) => settings++,
      onError: (_) {},
      onStopState: got.add,
    );
    final first = sockets.stream.first;
    ws.connect();
    final socket = await first;
    socket.add(jsonEncode(_msg('stopped', {'restoredAfterRestart': true})));
    for (var i = 0; i < 50 && got.isEmpty; i++) {
      await Future<void>.delayed(const Duration(milliseconds: 20));
    }
    expect(got, hasLength(1));
    expect(StopStateNotice.restoredAfterRestart(got.single), isTrue);
    expect(settings, 0);
    ws.disconnect();
    await socket.close();
    await server.close(force: true);
  });
}
