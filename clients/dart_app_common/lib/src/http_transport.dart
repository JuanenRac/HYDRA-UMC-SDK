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

/// One request, already built: the URL is absolute and the body is text (or, for an upload that is not text, [bodyBytes]).
class HttpRequestData {
  const HttpRequestData(
    this.method,
    this.url, {
    this.headers = const {},
    this.body,
    this.bodyBytes,
    this.binaryResponse = false,
  });

  final String method;
  final String url;
  final Map<String, String> headers;
  final String? body;

  /// The raw body of an upload that is not text (a firmware image). When set, [body] is null and the transport sends these bytes as they are.
  final List<int>? bodyBytes;

  /// True when the answer is not text (a binary download): the transport hands the bytes back in [HttpResponseData.bodyBytes] and
  /// does not decode them, because decoding a binary body as text corrupts it.
  final bool binaryResponse;

  HttpRequestData withHeader(String name, String value) => HttpRequestData(
        method,
        url,
        headers: {...headers, name: value},
        body: body,
        bodyBytes: bodyBytes,
        binaryResponse: binaryResponse,
      );

  /// The path of the URL (what an error message names).
  String get path => Uri.parse(url).path;
}

/// What came back: the status, the body as text, the path that was asked, the response headers and, for a binary answer, the bytes.
///
/// [headers] and [bodyBytes] are optional and empty by default, so a transport written before they existed keeps working: it simply
/// hands back no headers (a caller that needs one, like the ETag of the settings, then finds it missing and says so).
class HttpResponseData {
  const HttpResponseData(
    this.statusCode,
    this.body, {
    this.path = '',
    this.headers = const {},
    this.bodyBytes,
  });

  final int statusCode;

  /// The body as text. For a binary answer ([bodyBytes] set) it is empty.
  final String body;
  final String path;

  /// The response headers. A transport should hand them over with lower-case names (HTTP names are case-insensitive); [header] reads one
  /// whatever the case.
  final Map<String, String> headers;

  /// The raw bytes of a binary answer (the request had [HttpRequestData.binaryResponse]); null for a text answer.
  final List<int>? bodyBytes;

  /// One response header by name, whatever the case it came in; null when the answer did not carry it.
  String? header(String name) {
    final wanted = name.toLowerCase();
    for (final entry in headers.entries) {
      if (entry.key.toLowerCase() == wanted) return entry.value;
    }
    return null;
  }

  /// The response headers a route declares (`ETag`, `X-Next-Cursor`), found whatever the case they came in and listed under the
  /// declared name; a header the answer did not carry is left out. This is what a [HydraReply] of the generated client holds.
  Map<String, String> headersNamed(Iterable<String> names) {
    final found = <String, String>{};
    for (final name in names) {
      final value = header(name);
      if (value != null) found[name] = value;
    }
    return found;
  }

  /// The same answer with the path (and optionally other parts) replaced; everything else, headers and bytes included, is kept.
  HttpResponseData copyWith({int? statusCode, String? body, String? path, Map<String, String>? headers, List<int>? bodyBytes}) =>
      HttpResponseData(
        statusCode ?? this.statusCode,
        body ?? this.body,
        path: path ?? this.path,
        headers: headers ?? this.headers,
        bodyBytes: bodyBytes ?? this.bodyBytes,
      );
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
