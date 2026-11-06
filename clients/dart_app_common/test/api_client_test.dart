// =============================================================================
// HYDRA-UMC app common (Dart) - test/api_client_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The shared API client over a scripted transport: replays
// conformance/api-client/vectors.json (command numbering, which answers mean an
// expired session, how error answers are read, the renewal conversation) and
// checks the headers, bodies and timeouts of the calls every app makes.
// =============================================================================

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

class ScriptedTransport implements HttpTransport {
  ScriptedTransport(this.answers);
  final List<HttpResponseData> answers;
  final List<HttpRequestData> seen = [];
  bool closed = false;
  Object? failWith;
  Duration delay = Duration.zero;

  @override
  Future<HttpResponseData> send(HttpRequestData request) async {
    seen.add(request);
    if (delay > Duration.zero) await Future<void>.delayed(delay);
    if (failWith != null) throw failWith!;
    return answers.isEmpty ? const HttpResponseData(200, '{}') : answers.removeAt(0);
  }

  @override
  void close() => closed = true;
}

Map<String, dynamic> loadVectors() {
  var dir = Directory.current;
  for (var i = 0; i < 4; i++) {
    final f = File('${dir.path}/conformance/api-client/vectors.json');
    if (f.existsSync()) return jsonDecode(f.readAsStringSync()) as Map<String, dynamic>;
    dir = dir.parent;
  }
  throw StateError('conformance/api-client/vectors.json not found');
}

HydraApiCore clientOver(HttpTransport t, {String? token, CommandSequence? sequence}) => HydraApiCore(
      baseUrl: 'http://hydra:3000',
      transport: t,
      clientHeader: HydraApiCore.clientHeaderValue('test', '1.2.3'),
      controllerIdOf: () => 'ctl-1',
      sequence: sequence,
    )..authToken = token;

class _Probing extends HydraApiCore {
  _Probing(HttpTransport t) : super(baseUrl: 'http://h:1', transport: t, clientHeader: 'x', controllerIdOf: () => 'c');
  int resolved = 0;
  @override
  Future<void> resolveScheme() async => resolved++;
}

void main() {
  final vectors = loadVectors();

  group('command numbering vectors', () {
    final seq = vectors['sequence'] as Map<String, dynamic>;
    test('numbered set is the one in the vectors', () {
      expect(CommandSequence.defaultNumbered, (seq['numbered'] as List).cast<String>().toSet());
    });
    test('steps', () {
      var clock = 0;
      final s = CommandSequence(clock: () => clock);
      for (final step in seq['steps'] as List) {
        clock = step['clock'] as int;
        final out = s.numbered({'command': step['command']});
        expect(out['seq'], step['seq'], reason: '${step['command']} at $clock');
      }
    });
  });

  group('session answer vectors', () {
    for (final v in vectors['session_answers'] as List) {
      test('${v['status']} ${v['body']}', () {
        expect(isSessionAnswer(v['status'] as int, v['body'] as String), v['expired']);
      });
    }
  });

  group('error vectors', () {
    for (final v in vectors['errors'] as List) {
      test('${v['status']} ${v['body']}', () async {
        final c = clientOver(ScriptedTransport([HttpResponseData(v['status'] as int, v['body'] as String)]));
        try {
          await c.getSettings();
          fail('should throw');
        } on HydraApiException catch (e) {
          expect(e.statusCode, v['status']);
          expect(e.code, v['code']);
          expect(e.revision, v['revision']);
          expect(e.serverMessage, v['serverMessage']);
          expect(e.message, 'HTTP ${v['status']} from /api/settings');
          final flags = <String, bool>{
            'isRevisionMismatch': e.isRevisionMismatch,
            'isSessionProblem': e.isSessionProblem,
            'isPermissionDenied': e.isPermissionDenied,
            'isReservedByAnother': e.isReservedByAnother,
            'isOtherAccount': e.isOtherAccount,
            'isStaleSequence': e.isStaleSequence,
            'isOtherController': e.isOtherController,
            'isControllerIdRequired': e.isControllerIdRequired,
            'isJogNotArmed': e.isJogNotArmed,
            'isHomeRejected': e.isHomeRejected,
            'isRobotDisabled': e.isRobotDisabled,
            'isEnableNotAllowed': e.isEnableNotAllowed,
            'isAdminRequired': e.isAdminRequired,
            'isRejectedCommand': e.isRejectedCommand,
            'isRateLimited': e.isRateLimited,
            'isNotFound': e.isNotFound,
          };
          final expected = (v['flags'] as List).cast<String>().toSet();
          expect({for (final f in flags.entries) if (f.value) f.key}, expected);
        }
      });
    }
  });

  group('renewal vectors', () {
    for (final v in vectors['renewal'] as List) {
      test(v['name'] as String, () async {
        final answers = [for (final a in v['answers'] as List) HttpResponseData(a[0] as int, a[1] as String)];
        final t = ScriptedTransport(answers);
        final c = clientOver(t, token: v['bearer'] as String?);
        var renewals = 0;
        c.tokenRenewer = () async {
          renewals++;
          return v['renew'] as String?;
        };
        final last = await c.get('/api/x', const Duration(seconds: 1));
        final bearers = [for (final r in t.seen) r.headers['Authorization']?.replaceFirst('Bearer ', '')];
        expect(bearers, v['sent_bearers']);
        expect(renewals, v['renewals']);
        expect([last.statusCode, last.body], v['final']);
      });
    }

    test('a renewer that throws leaves the original answer', () async {
      final t = ScriptedTransport([const HttpResponseData(401, '')]);
      final c = clientOver(t, token: 'old')..tokenRenewer = () async => throw StateError('boom');
      expect((await c.get('/api/x', const Duration(seconds: 1))).statusCode, 401);
      expect(t.seen.length, 1);
    });

    test('the renewer can be set after the client exists and cleared again', () async {
      final t = ScriptedTransport([const HttpResponseData(401, ''), const HttpResponseData(200, 'ok')]);
      final c = clientOver(t, token: 'old');
      c.tokenRenewer = () async => 'new';
      expect((await c.get('/api/x', const Duration(seconds: 1))).body, 'ok');
      c.tokenRenewer = null;
      t.answers.add(const HttpResponseData(401, ''));
      expect((await c.get('/api/x', const Duration(seconds: 1))).statusCode, 401);
      expect(t.seen.length, 3);
    });
  });

  group('requests', () {
    test('robot command: numbered, controller headers, If-Match, body', () async {
      final t = ScriptedTransport([const HttpResponseData(200, '{"ok":true}')]);
      final c = clientOver(t, token: 'tok', sequence: CommandSequence(clock: () => 77));
      await c.postRobotCommand(3, {'command': 'jog', 'axis': 'x'}, ifMatch: 'r1');
      final r = t.seen.single;
      expect(r.method, 'POST');
      expect(r.url, 'http://hydra:3000/api/robot/3/command');
      expect(r.headers['X-Hydra-Client'], 'test/1.2.3');
      expect(r.headers['Authorization'], 'Bearer tok');
      expect(r.headers['X-Controller-Id'], 'ctl-1');
      expect(r.headers['If-Match'], 'r1');
      expect(r.headers['Content-Type'], 'application/json');
      expect(jsonDecode(r.body!), {'command': 'jog', 'axis': 'x', 'seq': 77, 'controllerId': 'ctl-1'});
    });

    test('a command that is not numbered carries no seq, and no value means no If-Match', () async {
      final t = ScriptedTransport([const HttpResponseData(200, '{}')]);
      final c = clientOver(t, token: 'tok');
      await c.postRobotCommand(1, {'command': 'speed', 'value': 50});
      expect((jsonDecode(t.seen.single.body!) as Map).containsKey('seq'), false);
      expect(t.seen.single.headers.containsKey('If-Match'), false);
    });

    test('login, refresh and logout carry no bearer token', () async {
      final t = ScriptedTransport([]);
      final c = clientOver(t, token: 'tok');
      await c.login('u', 'p');
      await c.refresh('rt');
      await c.logoutRemote('rt');
      expect(t.seen.map((r) => r.url.split('/api/').last), ['login', 'refresh', 'logout']);
      expect(t.seen.every((r) => !r.headers.containsKey('Authorization')), true);
      expect(jsonDecode(t.seen[0].body!), {'username': 'u', 'password': 'p'});
    });

    test('logoutRemote swallows a failure', () async {
      final t = ScriptedTransport([])..failWith = const SocketException('down');
      await clientOver(t).logoutRemote('rt');
    });

    test('stop-all posts without body or content type; claim and release', () async {
      final t = ScriptedTransport([]);
      final c = clientOver(t, token: 'tok');
      await c.postStopAll();
      expect(t.seen.last.body, isNull);
      expect(t.seen.last.headers.containsKey('Content-Type'), false);
      await c.postClaim(2, ttlMs: 5000, force: true);
      expect(jsonDecode(t.seen.last.body!), {'ttlMs': 5000, 'force': true, 'controllerId': 'ctl-1'});
      await c.postRelease(2);
      expect(t.seen.last.url, endsWith('/api/robot/2/release'));
    });

    test('a call that outlasts its timeout throws TimeoutException', () async {
      final t = ScriptedTransport([])..delay = const Duration(milliseconds: 200);
      await expectLater(clientOver(t).getText('/api/audit', const Duration(milliseconds: 20)), throwsA(isA<TimeoutException>()));
    });

    test('invalid JSON and non-object answers are refused with a message', () async {
      final c = clientOver(ScriptedTransport([const HttpResponseData(200, 'nope'), const HttpResponseData(200, '[1]')]));
      await expectLater(
          c.getSettings(), throwsA(predicate((e) => e is HydraApiException && e.message.startsWith('Response is not valid JSON'))));
      await expectLater(
          c.getSettings(), throwsA(predicate((e) => e is HydraApiException && e.message == 'Response is not a JSON object')));
    });

    test('the scheme hook runs before login and settings, close reaches the transport', () async {
      final t = ScriptedTransport([]);
      final c = _Probing(t);
      await c.login('u', 'p');
      await c.getSettings();
      expect(c.resolved, 2);
      c.close();
      expect(t.closed, true);
    });

    test('the client header value keeps a plain version and drops an odd one', () {
      expect(HydraApiCore.clientHeaderValue('dsi', '0.4.1'), 'dsi/0.4.1');
      expect(HydraApiCore.clientHeaderValue('dsi', 'has space'), 'dsi');
      expect(HydraApiCore.clientHeaderValue('dsi', ''), 'dsi');
    });
  });
}
