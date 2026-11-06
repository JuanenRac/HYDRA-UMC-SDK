// =============================================================================
// HYDRA-UMC app common (Dart) - src/connection_history.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// Who connects to the server: the two answers of the server
// (GET /api/connections/clients and /events) in the closed shape of the
// ConnectionClient and ConnectionEvent contracts of the SDK. No password,
// token or cookie is in either. The address and the user agent come only for
// an administrator and only when the server was told to keep them; this app
// shows them when they come and never asks.
//
// Times are milliseconds since the epoch (UTC); the DateTime getters convert.
// =============================================================================

import 'dart:convert';

/// The kinds of client the server tells apart.
const List<String> connectionKinds = ['studio', 'suite', 'android', 'ios', 'dsi', 'watch', 'voice', 'other'];

/// The things the history writes down.
const List<String> connectionActions = [
  'first_seen',
  'login',
  'login_failed',
  'second_factor_failed',
  'logout',
  'session_ended',
  'session_expired',
];

/// One application the server has seen.
class ConnectionClient {
  final String id;
  final String kind;
  final String? user;
  final String? appVersion;

  /// "local" or "remote", or null when the server did not say.
  final String? origin;
  final bool? twoFactor;
  final int firstSeenMs;
  final int lastSeenMs;

  /// The same instants as UTC dates.
  DateTime get firstSeen => DateTime.fromMillisecondsSinceEpoch(firstSeenMs, isUtc: true);
  DateTime get lastSeen => DateTime.fromMillisecondsSinceEpoch(lastSeenMs, isUtc: true);
  final int activeSessions;
  final int loginsOk;
  final int loginsFailed;
  final String? ip;

  const ConnectionClient({
    required this.id,
    required this.kind,
    this.user,
    this.appVersion,
    this.origin,
    this.twoFactor,
    required this.firstSeenMs,
    required this.lastSeenMs,
    required this.activeSessions,
    required this.loginsOk,
    required this.loginsFailed,
    this.ip,
  });
}

/// One line of the history.
class ConnectionEvent {
  final int id;
  final int atMs;

  /// The same instant as a UTC date.
  DateTime get at => DateTime.fromMillisecondsSinceEpoch(atMs, isUtc: true);
  final String action;
  final String kind;
  final String? user;
  final String? appVersion;

  const ConnectionEvent({
    required this.id,
    required this.atMs,
    required this.action,
    required this.kind,
    this.user,
    this.appVersion,
  });

  /// A refused sign-in or a wrong code of the second step: painted as a warning.
  bool get isFailure => action == 'login_failed' || action == 'second_factor_failed';
}

/// Why the history could not be read, for the sentence the screen shows.
enum ConnectionsFailure { unavailable, session, network, other }

class ConnectionHistory {
  ConnectionHistory._();

  static final RegExp _id = RegExp(r'^[0-9a-f]{16}$');
  static final RegExp _utcDate = RegExp(r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,9}))?Z$');

  /// An ISO date in UTC as the server writes it (`2026-01-02T03:04:05.678Z`) in milliseconds; null for anything else.
  /// [millis] as a UTC date (null when the text is not one of the server's dates).
  static DateTime? parseDate(Object? text) {
    final ms = text is String ? millis(text) : null;
    return ms == null ? null : DateTime.fromMillisecondsSinceEpoch(ms, isUtc: true);
  }

  static int? millis(String? text) {
    if (text == null) return null;
    final m = _utcDate.firstMatch(text);
    if (m == null) return null;
    final y = int.parse(m.group(1)!);
    final mo = int.parse(m.group(2)!);
    final d = int.parse(m.group(3)!);
    final h = int.parse(m.group(4)!);
    final mi = int.parse(m.group(5)!);
    final se = int.parse(m.group(6)!);
    if (mo < 1 || mo > 12 || d < 1 || d > 31 || h > 23 || mi > 59 || se > 59) return null;
    final ms = int.parse((m.group(7) ?? '').padRight(3, '0').substring(0, 3));
    return DateTime.utc(y, mo, d, h, mi, se, ms).millisecondsSinceEpoch;
  }

  /// A string field, or null when it is absent, null or empty.
  static String? _text(Map<String, dynamic> json, String name) {
    final value = json[name];
    return value is String && value.isNotEmpty ? value : null;
  }

  static int _count(Object? value) => value is num && value.isFinite ? value.toInt().clamp(0, 1 << 31) : 0;

  static String _kindOf(String? text) => text != null && connectionKinds.contains(text) ? text : 'other';

  /// Reads one client; null when it is not a well-formed entry (a bad identifier or date).
  static ConnectionClient? parseClient(Object? json) {
    if (json is! Map<String, dynamic>) return null;
    final id = _text(json, 'id');
    if (id == null || !_id.hasMatch(id)) return null;
    final first = millis(_text(json, 'first_seen_utc'));
    final last = millis(_text(json, 'last_seen_utc'));
    if (first == null || last == null) return null;
    final origin = _text(json, 'origin');
    return ConnectionClient(
      id: id,
      kind: _kindOf(_text(json, 'kind')),
      user: _text(json, 'user'),
      appVersion: _text(json, 'app_version'),
      origin: origin == 'local' || origin == 'remote' ? origin : null,
      twoFactor: json['two_factor'] is bool ? json['two_factor'] as bool : null,
      firstSeenMs: first,
      lastSeenMs: last,
      activeSessions: _count(json['active_sessions']),
      loginsOk: _count(json['logins_ok']),
      loginsFailed: _count(json['logins_failed']),
      ip: _text(json, 'ip'),
    );
  }

  /// Reads one event; null when it is not a well-formed entry or its action is not one the server writes.
  static ConnectionEvent? parseEvent(Object? json) {
    if (json is! Map<String, dynamic>) return null;
    final action = _text(json, 'action');
    if (action == null || !connectionActions.contains(action)) return null;
    final at = millis(_text(json, 'at_utc'));
    if (at == null) return null;
    final id = json['id'];
    if (id is! num || id < 1) return null;
    return ConnectionEvent(
      id: id.toInt(),
      atMs: at,
      action: action,
      kind: _kindOf(_text(json, 'client_kind')),
      user: _text(json, 'user'),
      appVersion: _text(json, 'app_version'),
    );
  }

  static List<dynamic> _list(String body, String name) {
    final root = jsonDecode(body);
    if (root is! Map<String, dynamic>) return const [];
    final list = root[name];
    return list is List ? list : const [];
  }

  /// The clients of an answer `{ "clients": [...] }`, the most recently seen first; what cannot be read is left out.
  static List<ConnectionClient> parseClients(String body) {
    final out = _list(body, 'clients').map(parseClient).whereType<ConnectionClient>().toList();
    out.sort((a, b) => b.lastSeenMs.compareTo(a.lastSeenMs));
    return out;
  }

  /// The events of an answer `{ "events": [...] }`, newest first.
  static List<ConnectionEvent> parseEvents(String body) {
    final out = _list(body, 'events').map(parseEvent).whereType<ConnectionEvent>().toList();
    out.sort((a, b) => b.id.compareTo(a.id));
    return out;
  }

  /// How long ago, short enough for a line: the amount and its unit ("s", "min", "h" or "d").
  /// [ago] over two dates.
  static (int, String) agoDates(DateTime then, DateTime now) => ago(then.millisecondsSinceEpoch, now.millisecondsSinceEpoch);

  static (int, String) ago(int thenMs, int nowMs) {
    final seconds = ((nowMs - thenMs) ~/ 1000).clamp(0, 1 << 40);
    if (seconds < 60) return (seconds, 's');
    if (seconds < 3600) return (seconds ~/ 60, 'min');
    if (seconds < 48 * 3600) return (seconds ~/ 3600, 'h');
    return (seconds ~/ 86400, 'd');
  }
}
