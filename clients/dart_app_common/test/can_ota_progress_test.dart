// =============================================================================
// HYDRA-UMC app common (Dart) - test/can_ota_progress_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The reading of the `canota_progress` message, and its delivery through the WebSocket against a real local dart:io server.
// =============================================================================

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:test/test.dart';

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';

Map<String, dynamic> _message(Map<String, Object?> payload) => {'type': 'canota_progress', 'payload': payload};

void main() {
  group('CanOtaProgress.fromMessage', () {
    test('a transfer message gives the phase, the pages and the percent', () {
      final p = CanOtaProgress.fromMessage(_message({'phase': 'transferring', 'pages_sent': 10, 'pages_total': 40, 'percent': 25, 'error': null}))!;
      expect(p.phase, CanOtaPhase.transferring);
      expect([p.pagesSent, p.pagesTotal, p.percent, p.error], [10, 40, 25, null]);
      expect(p.finished, isFalse);
    });

    test('every phase the server writes is known and only done and error end the cycle', () {
      const names = ['connecting', 'entering_bootloader', 'erasing_fram', 'transferring', 'verifying', 'rebooting', 'done', 'error'];
      expect(CanOtaPhase.values.map((p) => p.wire), names);
      for (final name in names) {
        expect(CanOtaProgress.fromMessage(_message({'phase': name}))!.finished, name == 'done' || name == 'error');
      }
    });

    test('an error carries its reason; a long one is cut and a blank one is dropped', () {
      final long = CanOtaProgress.fromMessage(_message({'phase': 'error', 'error': 'x' * 500}))!;
      expect(long.error!.length, CanOtaProgress.maxReasonChars);
      expect(CanOtaProgress.fromMessage(_message({'phase': 'error', 'error': '  '}))!.error, isNull);
    });

    test('a missing or wrong number stays null and the percent stays inside 0 to 100', () {
      final none = CanOtaProgress.fromMessage(_message({'phase': 'verifying'}))!;
      expect([none.percent, none.pagesSent, none.pagesTotal], [null, null, null]);
      final wrong = CanOtaProgress.fromMessage(_message({'phase': 'transferring', 'pages_sent': -1, 'pages_total': 2.5, 'percent': 'half'}))!;
      expect([wrong.percent, wrong.pagesSent, wrong.pagesTotal], [null, null, null]);
      expect(CanOtaProgress.fromMessage(_message({'phase': 'done', 'percent': 140}))!.percent, 100);
      expect(CanOtaProgress.fromMessage(_message({'phase': 'connecting', 'percent': -5}))!.percent, 0);
      expect(CanOtaProgress.fromMessage(_message({'phase': 'transferring', 'percent': 33.6}))!.percent, 34);
    });

    test('a message with no payload or an unknown phase is not a progress', () {
      expect(CanOtaProgress.fromMessage({'type': 'canota_progress'}), isNull);
      expect(CanOtaProgress.fromMessage(_message({'phase': 'dancing'})), isNull);
      expect(CanOtaProgress.fromMessage(_message({'percent': 10})), isNull);
    });
  });

  group('the WebSocket', () {
    Future<HttpServer> serve(List<String> frames) async {
      final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
      server.listen((request) async {
        final socket = await WebSocketTransformer.upgrade(
          request,
          protocolSelector: (p) => p.contains('hydra.bearer') ? 'hydra.bearer' : null,
        );
        for (final frame in frames) {
          socket.add(frame);
        }
      });
      return server;
    }

    test('a progress message goes to its own callback and not to the settings one', () async {
      final server = await serve([jsonEncode(_message({'phase': 'transferring', 'pages_sent': 5, 'pages_total': 20, 'percent': 25}))]);
      addTearDown(() => server.close(force: true));
      final progress = Completer<Map<String, dynamic>>();
      final settings = <Map<String, dynamic>>[];
      final ws = HydraWebSocket(
        host: '127.0.0.1',
        port: server.port,
        token: 'tok',
        onStatus: (_) {},
        onSettings: settings.add,
        onError: (_) {},
        onCanOtaProgress: (m) {
          if (!progress.isCompleted) progress.complete(m);
        },
      )..connect();
      addTearDown(ws.disconnect);
      final read = CanOtaProgress.fromMessage(await progress.future.timeout(const Duration(seconds: 5)))!;
      expect(read.phase, CanOtaPhase.transferring);
      expect(read.percent, 25);
      expect(settings, isEmpty);
    });

    test('a client that does not listen for progress ignores the message and still gets the settings', () async {
      final server = await serve([
        jsonEncode(_message({'phase': 'done'})),
        jsonEncode({'type': 'settings', 'payload': {'controllers': []}}),
      ]);
      addTearDown(() => server.close(force: true));
      final settings = Completer<Map<String, dynamic>>();
      final ws = HydraWebSocket(
        host: '127.0.0.1',
        port: server.port,
        token: 'tok',
        onStatus: (_) {},
        onSettings: (m) {
          if (!settings.isCompleted) settings.complete(m);
        },
        onError: (_) {},
      )..connect();
      addTearDown(ws.disconnect);
      final first = await settings.future.timeout(const Duration(seconds: 5));
      expect(first.containsKey('controllers'), isTrue);
    });
  });
}
