// =============================================================================
// HYDRA-UMC app common (Dart) - test/connection_history_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The reading of the list of clients and of the history of sign-ins that the server gives.
// =============================================================================

import 'package:test/test.dart';

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';

void main() {
  dateViews();
  const client = '{"schema_version":"1.0","id":"0123456789abcdef","kind":"ios","user":"ana","app_version":"0.2.9","origin":"local",'
      '"two_factor":true,"first_seen_utc":"2026-01-01T00:00:00.000Z","last_seen_utc":"2026-01-02T00:00:00.000Z",'
      '"active_sessions":2,"logins_ok":5,"logins_failed":1}';

  test('a date is read as the server writes it', () {
    expect(ConnectionHistory.millis('2026-01-01T00:00:00.000Z'), 1767225600000);
    expect(ConnectionHistory.millis('2026-01-01T00:00:00.123Z'), 1767225600123);
    expect(ConnectionHistory.millis('2026-01-01T00:00:01Z'), 1767225601000);
    expect(ConnectionHistory.millis('yesterday'), isNull);
    expect(ConnectionHistory.millis('2026-13-01T00:00:00.000Z'), isNull);
    expect(ConnectionHistory.millis(null), isNull);
  });

  test('a client is read field by field', () {
    final list = ConnectionHistory.parseClients('{"clients":[$client]}');
    expect(list, hasLength(1));
    final c = list[0];
    expect(c.kind, 'ios');
    expect(c.user, 'ana');
    expect(c.appVersion, '0.2.9');
    expect(c.origin, 'local');
    expect(c.twoFactor, isTrue);
    expect(c.activeSessions, 2);
    expect(c.loginsOk, 5);
    expect(c.loginsFailed, 1);
    expect(c.ip, isNull);
  });

  test('a kind it does not know is other and an entry with a bad identifier or date is left out', () {
    final odd = client.replaceAll('"kind":"ios"', '"kind":"toaster"');
    expect(ConnectionHistory.parseClients('{"clients":[$odd]}')[0].kind, 'other');
    expect(ConnectionHistory.parseClients('{"clients":[${client.replaceAll("0123456789abcdef", "nope")}]}'), isEmpty);
    expect(ConnectionHistory.parseClients('{"clients":[${client.replaceAll("2026-01-02T00:00:00.000Z", "later")}]}'), isEmpty);
    expect(ConnectionHistory.parseClients('{"clients":[5,null,{}]}'), isEmpty);
    expect(ConnectionHistory.parseClients('{}'), isEmpty);
    expect(ConnectionHistory.parseClients('[]'), isEmpty);
  });

  test('the most recently seen client comes first and an address is kept only when it is sent', () {
    final older = client
        .replaceAll('0123456789abcdef', 'fedcba9876543210')
        .replaceAll('2026-01-02T00:00:00.000Z', '2026-01-01T12:00:00.000Z')
        .replaceAll('"active_sessions":2', '"active_sessions":0,"ip":"192.168.0.9"');
    final list = ConnectionHistory.parseClients('{"clients":[$older,$client]}');
    expect(list.map((c) => c.id), ['0123456789abcdef', 'fedcba9876543210']);
    expect(list[1].ip, '192.168.0.9');
    expect(list[0].ip, isNull);
  });

  test('events are read newest first and only the actions the server writes', () {
    const events = '{"events":['
        '{"schema_version":"1.0","id":1,"at_utc":"2026-01-01T00:00:00.000Z","action":"login","client_kind":"studio","client_id":"0123456789abcdef","user":"ana"},'
        '{"schema_version":"1.0","id":3,"at_utc":"2026-01-03T00:00:00.000Z","action":"login_failed","client_kind":"ios","client_id":"0123456789abcdef","user":"ana","app_version":"0.2.9"},'
        '{"schema_version":"1.0","id":2,"at_utc":"2026-01-02T00:00:00.000Z","action":"format_disk","client_kind":"studio","client_id":"0123456789abcdef"},'
        '{"schema_version":"1.0","id":0,"at_utc":"2026-01-02T00:00:00.000Z","action":"login","client_kind":"studio","client_id":"0123456789abcdef"}]}';
    final list = ConnectionHistory.parseEvents(events);
    expect(list.map((e) => e.id), [3, 1]);
    expect(list[0].isFailure, isTrue);
    expect(list[1].isFailure, isFalse);
    expect(list[0].appVersion, '0.2.9');
    expect(list[1].appVersion, isNull);
  });

  test('how long ago is short', () {
    const now = 10000000000;
    expect(ConnectionHistory.ago(now - 30000, now), (30, 's'));
    expect(ConnectionHistory.ago(now - 12 * 60000, now), (12, 'min'));
    expect(ConnectionHistory.ago(now - 3 * 3600000, now), (3, 'h'));
    expect(ConnectionHistory.ago(now - 3 * 86400000, now), (3, 'd'));
    expect(ConnectionHistory.ago(now + 5000, now), (0, 's'));
  });
}

void dateViews() {
  group('dates and hostile counts', () {
    test('the DateTime views are the same instants in UTC', () {
      final c = ConnectionHistory.parseClient({
        'id': '0123456789abcdef',
        'kind': 'ios',
        'first_seen_utc': '2026-01-01T00:00:00.000Z',
        'last_seen_utc': '2026-01-01T00:00:01.500Z',
        'active_sessions': double.infinity,
        'logins_ok': -4,
        'logins_failed': 3.9,
      })!;
      expect(c.firstSeen, DateTime.utc(2026, 1, 1));
      expect(c.lastSeen, DateTime.utc(2026, 1, 1, 0, 0, 1, 500));
      expect(c.activeSessions, 0);
      expect(c.loginsOk, 0);
      expect(c.loginsFailed, 3);
      expect(ConnectionHistory.parseDate('2026-01-01T00:00:00Z'), DateTime.utc(2026));
      expect(ConnectionHistory.parseDate(5), isNull);
      expect(ConnectionHistory.agoDates(DateTime.utc(2026), DateTime.utc(2026, 1, 1, 0, 12)), (12, 'min'));
    });
  });
}
