// =============================================================================
// HYDRA-UMC app common (Dart) - src/hydra_api_core.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The HTTP client of the HYDRA-UMC server that the Flutter apps share: headers
// (client tag, bearer token, controller id, If-Match), the numbering of motion
// commands, the renewal of an expired session, the reading of the server's
// error answers and the endpoints every app calls. It speaks through an
// injected [HttpTransport]; it knows nothing about package:http, TLS policy or
// the app's own models. An app extends it (adding its typed endpoints and the
// choice between http and https) and keeps its public API.
// =============================================================================

import 'dart:async';
import 'dart:convert';

import 'command_sequence.dart';
import 'contract_v2.dart' show revisionOf;
import 'http_transport.dart';

/// A refused or malformed answer from the server.
class HydraApiException implements Exception {
  final String message;
  final int? statusCode;
  final String? code;
  final String? serverMessage;
  final String? revision;
  HydraApiException(this.message, {this.statusCode, this.code, this.serverMessage, this.revision});

  /// 412, or the code `revision-mismatch`: the settings changed since they were read.
  bool get isRevisionMismatch => statusCode == 412 || code == 'revision-mismatch';

  /// The session is over or the token is not valid (not a role problem).
  bool get isSessionProblem =>
      statusCode == 401 || (statusCode == 403 && (code == 'TOKEN_EXPIRED' || code == 'TOKEN_INVALID'));

  bool get isPermissionDenied =>
      statusCode == 403 && !isSessionProblem && !isJogNotArmed && !isEnableNotAllowed && !isAdminRequired;

  bool get isReservedByAnother => statusCode == 409;
  bool get isOtherAccount => statusCode == 409 && code == 'other-account';
  bool get isStaleSequence => statusCode == 409 && code == 'stale-sequence';
  bool get isOtherController => statusCode == 409 && code == 'other-controller';
  bool get isControllerIdRequired => code == 'controller-id-required';
  bool get isJogNotArmed => statusCode == 403 && code == 'jog-not-armed';
  bool get isHomeRejected =>
      (statusCode == 400 && code == 'home-pose-mismatch') || (statusCode == 422 && code == 'home-out-of-limits');
  bool get isRobotDisabled => statusCode == 423 || code == 'robot-disabled';
  bool get isEnableNotAllowed => statusCode == 403 && code == 'enable-not-allowed';
  bool get isAdminRequired => statusCode == 403 && code == 'admin-required';
  bool get isRejectedCommand => statusCode == 400;
  bool get isRateLimited => statusCode == 429;
  bool get isNotFound => statusCode == 404;

  @override
  String toString() => message;
}

class HydraApiCore {
  HydraApiCore({
    required this.baseUrl,
    required HttpTransport transport,
    required String clientHeader,
    required this.controllerIdOf,
    CommandSequence? sequence,
  })  : sequence = sequence ?? CommandSequence(),
        _clientHeaders = {'X-Hydra-Client': clientHeader} {
    _transport = RenewingTransport(transport, () => tokenRenewer);
  }

  /// `scheme://host:port`, no trailing slash.
  String baseUrl;

  /// The bearer token of the session, if any.
  String? authToken;

  /// Asked for a new token when a request is answered with an expired
  /// session; null when the app cannot renew it.
  TokenRenewer? tokenRenewer;

  /// The counter that numbers the motion commands.
  final CommandSequence sequence;

  /// Reads the id of this controller (the apps keep one per process).
  final String Function() controllerIdOf;
  final Map<String, String> _clientHeaders;
  late final HttpTransport _transport;

  String get controllerId => controllerIdOf();

  bool get usesTls => baseUrl.startsWith('https://');

  /// `X-Hydra-Client` value: `<tag>/<version>` when the version is a plain
  /// token of at most 24 characters, else just the tag.
  static String clientHeaderValue(String tag, String version) =>
      RegExp(r'^[0-9A-Za-z._-]{1,24}$').hasMatch(version) ? '$tag/$version' : tag;

  Map<String, String> get clientHeaders => _clientHeaders;
  Map<String, String> get authHeaders => authToken != null ? {'Authorization': 'Bearer $authToken'} : const {};
  Map<String, String> get controllerHeaders => {'X-Controller-Id': controllerId};

  /// Headers for media the app fetches on its own (images, streams).
  Map<String, String> get mediaHeaders => {..._clientHeaders, ...authHeaders};

  static const Map<String, String> _json = {'Content-Type': 'application/json'};

  /// Hook: the app may learn here whether the server speaks https or http
  /// before the first call that needs it (login, settings).
  Future<void> resolveScheme() async {}

  // -------------------------------------------------------------------------
  // The one place a request leaves.
  // -------------------------------------------------------------------------

  /// Sends one request through the (renewing) transport, within [timeout].
  Future<HttpResponseData> call(
    String method,
    String url, {
    Map<String, String> headers = const {},
    String? body,
    required Duration timeout,
  }) async {
    final req = HttpRequestData(method, url, headers: headers, body: body);
    final resp = await _transport.send(req).timeout(timeout);
    return resp.path.isEmpty ? HttpResponseData(resp.statusCode, resp.body, path: req.path) : resp;
  }

  /// GET [path] with the client and auth headers.
  Future<HttpResponseData> get(String path, Duration timeout) =>
      call('GET', '$baseUrl$path', headers: {..._clientHeaders, ...authHeaders}, timeout: timeout);

  /// POST [path] with a JSON body (null: no body) and the client and auth headers.
  Future<HttpResponseData> post(String path, Duration timeout, [Object? body]) => call('POST', '$baseUrl$path',
      headers: {if (body != null) ..._json, ..._clientHeaders, ...authHeaders},
      body: body == null ? null : jsonEncode(body),
      timeout: timeout);

  /// GET [path] and decode a JSON object.
  Future<Map<String, dynamic>> getJson(String path, Duration timeout) async => expectJson(await get(path, timeout));

  /// GET [path] and return the body text of a 2xx answer.
  Future<String> getText(String path, Duration timeout) async {
    final resp = await get(path, timeout);
    throwForStatus(resp);
    return resp.body;
  }

  /// POST [path] and decode a JSON object.
  Future<Map<String, dynamic>> postJson(String path, Duration timeout, [Object? body]) async =>
      expectJson(await post(path, timeout, body));

  // -------------------------------------------------------------------------
  // Session
  // -------------------------------------------------------------------------

  Future<Map<String, dynamic>> login(String username, String password) async {
    await resolveScheme();
    final resp = await call('POST', '$baseUrl/api/login',
        headers: {..._json, ..._clientHeaders},
        body: jsonEncode({'username': username, 'password': password}),
        timeout: const Duration(seconds: 15));
    return expectJson(resp);
  }

  Future<Map<String, dynamic>> refresh(String refreshToken) async {
    final resp = await call('POST', '$baseUrl/api/refresh',
        headers: {..._json, ..._clientHeaders},
        body: jsonEncode({'refreshToken': refreshToken}),
        timeout: const Duration(seconds: 5));
    return expectJson(resp);
  }

  /// Best effort: a failure is ignored (the local session ends anyway).
  Future<void> logoutRemote(String refreshToken) async {
    try {
      await call('POST', '$baseUrl/api/logout',
          headers: {..._json, ..._clientHeaders},
          body: jsonEncode({'refreshToken': refreshToken}),
          timeout: const Duration(seconds: 5));
    } catch (_) {
      // Nothing to do: the token expires by itself.
    }
  }

  Future<Map<String, dynamic>> getSettings() async {
    await resolveScheme(); // a restored session never ran login()
    return getJson('/api/settings', const Duration(seconds: 5));
  }

  // -------------------------------------------------------------------------
  // Commands
  // -------------------------------------------------------------------------

  Future<Map<String, dynamic>> postRobotCommand(
    dynamic robotId,
    Map<String, dynamic> payload, {
    Duration timeout = const Duration(seconds: 5),
    String? ifMatch,
  }) =>
      _control('/api/robot/$robotId/command', sequence.numbered(payload), timeout, ifMatch);

  /// POST with the controller id in header and body (claims, jog arming...).
  Future<Map<String, dynamic>> postControl(String path, Map<String, dynamic> body, {String? ifMatch}) =>
      _control(path, body, const Duration(seconds: 5), ifMatch);

  Future<Map<String, dynamic>> _control(String path, Map<String, dynamic> body, Duration timeout, String? ifMatch) async {
    final resp = await call('POST', '$baseUrl$path',
        headers: {
          ..._json,
          ..._clientHeaders,
          ...controllerHeaders,
          ...authHeaders,
          'If-Match': ?ifMatch,
        },
        body: jsonEncode({...body, 'controllerId': controllerId}),
        timeout: timeout);
    return expectJson(resp);
  }

  Future<Map<String, dynamic>> postClaim(dynamic robotId, {int? ttlMs, bool force = false, String? ifMatch}) =>
      postControl('/api/robot/$robotId/claim', {'ttlMs': ?ttlMs, if (force) 'force': true},
          ifMatch: ifMatch);

  Future<Map<String, dynamic>> postRelease(dynamic robotId, {String? ifMatch}) =>
      postControl('/api/robot/$robotId/release', {}, ifMatch: ifMatch);

  Future<Map<String, dynamic>> postJogArm(dynamic robotId, bool armed) =>
      postControl('/api/robot/$robotId/jog-arm', {'armed': armed});

  /// Global STOP of every robot.
  Future<Map<String, dynamic>> postStopAll({Duration timeout = const Duration(seconds: 2)}) =>
      postJson('/api/stop-all', timeout);

  Future<Map<String, dynamic>> getSystemMetrics() => getJson('/api/system/metrics', const Duration(seconds: 5));

  // -------------------------------------------------------------------------
  // Reading the answers
  // -------------------------------------------------------------------------

  /// The JSON object of a 2xx answer; anything else is a [HydraApiException].
  Map<String, dynamic> expectJson(HttpResponseData resp) {
    throwForStatus(resp);
    final Object? decoded;
    try {
      decoded = jsonDecode(resp.body);
    } on FormatException catch (e) {
      throw HydraApiException('Response is not valid JSON: ${e.message}');
    }
    if (decoded is! Map<String, dynamic>) {
      throw HydraApiException('Response is not a JSON object');
    }
    return decoded;
  }

  /// Throws a [HydraApiException] carrying the server's code, message and
  /// revision when the status is not 2xx.
  void throwForStatus(HttpResponseData resp) {
    if (resp.statusCode >= 200 && resp.statusCode < 300) return;
    String? code;
    String? serverMessage;
    String? revision;
    try {
      final body = jsonDecode(resp.body);
      if (body is Map) {
        if (body['code'] is String) code = body['code'] as String;
        if (body['error'] is String) serverMessage = body['error'] as String;
        revision = revisionOf(body);
      }
    } catch (_) {
      // The error body is not JSON: the status alone says what happened.
    }
    throw HydraApiException(
      'HTTP ${resp.statusCode} from ${resp.path}',
      statusCode: resp.statusCode,
      code: code,
      serverMessage: serverMessage,
      revision: revision,
    );
  }

  void close() => _transport.close();
}
