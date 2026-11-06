// =============================================================================
// HYDRA-UMC app common (Dart) - src/http_transport.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The seam under the shared API client. The package does not import
// package:http or any Flutter plugin: each app injects an [HttpTransport]
// (its own adapter over package:http, dart:io or a test double) and the client
// does the rest. [RenewingTransport] is the one place that renews an expired
// session and repeats the request once.
// =============================================================================

import 'dart:convert';

/// One request, already built: the URL is absolute and the body is text.
class HttpRequestData {
  const HttpRequestData(this.method, this.url, {this.headers = const {}, this.body});

  final String method;
  final String url;
  final Map<String, String> headers;
  final String? body;

  HttpRequestData withHeader(String name, String value) =>
      HttpRequestData(method, url, headers: {...headers, name: value}, body: body);

  /// The path of the URL (what an error message names).
  String get path => Uri.parse(url).path;
}

/// What came back: the status, the body as text and the path that was asked.
class HttpResponseData {
  const HttpResponseData(this.statusCode, this.body, {this.path = ''});

  final int statusCode;
  final String body;
  final String path;
}

/// The platform side of the client. Timeouts are applied by the client, so an
/// implementation only has to send and answer (or throw its own error).
abstract class HttpTransport {
  Future<HttpResponseData> send(HttpRequestData request);

  /// Releases whatever the implementation holds.
  void close();
}

/// Returns the new bearer token, or null when the session could not be renewed.
typedef TokenRenewer = Future<String?> Function();

/// True for the answers a new token can cure: 401, or 403 with the code
/// TOKEN_EXPIRED / TOKEN_INVALID. Any other 403 is a role problem and a new
/// token would not change it.
bool isSessionAnswer(int status, String body) {
  if (status == 401) return true;
  if (status != 403) return false;
  try {
    final decoded = jsonDecode(body);
    final code = decoded is Map ? decoded['code'] : null;
    return code == 'TOKEN_EXPIRED' || code == 'TOKEN_INVALID';
  } catch (_) {
    return false;
  }
}

/// A transport that, when a request carried a bearer token and was answered
/// with an expired or invalid session, asks the owner of the session for a new
/// token and sends the request once more with it. Any other answer, a request
/// without a bearer token (login, refresh) and a failed renewal reach the
/// caller untouched.
class RenewingTransport implements HttpTransport {
  RenewingTransport(this._inner, this._renewer);

  final HttpTransport _inner;

  /// Read at every request, so the owner can set it after the client exists
  /// (and clear it when the session ends).
  final TokenRenewer? Function() _renewer;

  @override
  Future<HttpResponseData> send(HttpRequestData request) async {
    final renewer = _renewer();
    final hadBearer = (request.headers['Authorization'] ?? '').startsWith('Bearer ');
    if (renewer == null || !hadBearer) return _inner.send(request);

    final first = await _inner.send(request);
    if (!isSessionAnswer(first.statusCode, first.body)) return first;

    String? token;
    try {
      token = await renewer();
    } catch (_) {
      token = null;
    }
    if (token == null || token.isEmpty) return first;
    return _inner.send(request.withHeader('Authorization', 'Bearer $token'));
  }

  @override
  void close() => _inner.close();
}
