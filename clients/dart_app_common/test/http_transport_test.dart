// =============================================================================
// HYDRA-UMC app common (Dart) - test/http_transport_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// What the seam under the shared API client carries: the response headers (the
// ETag of the settings, the cursor of a paged list), a binary body in either
// direction and a text answer, and that all of it survives the client and the
// renewal of an expired session. A transport written before these fields
// existed (it builds the answer with a status and a body only) keeps working.
// =============================================================================

import 'dart:convert';

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

class _Scripted implements HttpTransport {
  _Scripted(this.answers);
  final List<HttpResponseData> answers;
  final List<HttpRequestData> seen = [];

  @override
  Future<HttpResponseData> send(HttpRequestData request) async {
    seen.add(request);
    return answers.removeAt(0);
  }

  @override
  void close() {}
}

HydraApiCore _clientOver(HttpTransport t) => HydraApiCore(
      baseUrl: 'http://hydra:3000',
      transport: t,
      clientHeader: 'test/1',
      controllerIdOf: () => 'ctl-1',
    );

void main() {
  group('HttpResponseData', () {
    test('an answer built the old way has no headers and no bytes', () {
      const answer = HttpResponseData(200, 'ok');
      expect(answer.headers, isEmpty);
      expect(answer.bodyBytes, isNull);
      expect(answer.path, '');
      expect(answer.header('ETag'), isNull);
    });

    test('a header is read whatever the case it came in', () {
      const answer = HttpResponseData(200, '{}', headers: {'etag': '"7"', 'X-Next-Cursor': 'abc'});
      expect(answer.header('ETag'), '"7"');
      expect(answer.header('ETAG'), '"7"');
      expect(answer.header('x-next-cursor'), 'abc');
      expect(answer.header('Missing'), isNull);
    });

    test('headersNamed lists the declared names and leaves out what is absent', () {
      const answer = HttpResponseData(200, '{}', headers: {'etag': '"7"'});
      expect(answer.headersNamed(const ['ETag', 'X-Next-Cursor']), {'ETag': '"7"'});
      expect(answer.headersNamed(const []), isEmpty);
    });

    test('copyWith changes what it is given and keeps the headers and the bytes', () {
      const answer = HttpResponseData(200, '', headers: {'etag': '"7"'}, bodyBytes: [1, 2, 3]);
      final named = answer.copyWith(path: '/api/x');
      expect(named.path, '/api/x');
      expect(named.statusCode, 200);
      expect(named.headers, {'etag': '"7"'});
      expect(named.bodyBytes, [1, 2, 3]);
      expect(answer.copyWith(statusCode: 204).statusCode, 204);
    });
  });

  group('HttpRequestData', () {
    test('withHeader keeps the binary body and the binary answer flag', () {
      const request = HttpRequestData('POST', 'http://h/api/x', bodyBytes: [9, 8], binaryResponse: true);
      final signed = request.withHeader('Authorization', 'Bearer t');
      expect(signed.headers, {'Authorization': 'Bearer t'});
      expect(signed.bodyBytes, [9, 8]);
      expect(signed.binaryResponse, isTrue);
      expect(signed.body, isNull);
    });

    test('a request built the old way is text and wants a text answer', () {
      const request = HttpRequestData('GET', 'http://h/api/x');
      expect(request.bodyBytes, isNull);
      expect(request.binaryResponse, isFalse);
    });
  });

  group('HydraApiCore.call', () {
    test('hands back the headers of the answer and fills in the path', () async {
      final transport = _Scripted([const HttpResponseData(200, '{}', headers: {'etag': '"12"'})]);
      final answer = await _clientOver(transport).call('GET', 'http://hydra:3000/api/robot/1', timeout: const Duration(seconds: 2));
      expect(answer.path, '/api/robot/1');
      expect(answer.header('ETag'), '"12"');
    });

    test('keeps the bytes of a binary answer and sends the bytes of an upload', () async {
      final transport = _Scripted([const HttpResponseData(200, '', bodyBytes: [0, 255, 7])]);
      final answer = await _clientOver(transport).call(
        'POST',
        'http://hydra:3000/api/hardware/canota/flash',
        headers: const {'Content-Type': 'application/octet-stream'},
        bodyBytes: const [1, 2, 3],
        binaryResponse: true,
        timeout: const Duration(seconds: 2),
      );
      expect(answer.bodyBytes, [0, 255, 7]);
      expect(transport.seen.single.bodyBytes, [1, 2, 3]);
      expect(transport.seen.single.body, isNull);
      expect(transport.seen.single.binaryResponse, isTrue);
    });

    test('a text answer stays text, line by line, untouched', () async {
      const lines = '{"seq":1}\n{"seq":2}\n';
      final transport = _Scripted([const HttpResponseData(200, lines, headers: {'content-type': 'application/x-ndjson'})]);
      final answer = await _clientOver(transport).call('GET', 'http://hydra:3000/api/audit?format=jsonl', timeout: const Duration(seconds: 2));
      expect(answer.body, lines);
      expect(const LineSplitter().convert(answer.body).length, 2);
      expect(answer.header('Content-Type'), 'application/x-ndjson');
    });
  });

  group('RenewingTransport', () {
    test('repeats the request with the new token and keeps the binary body, the flag and the headers of the new answer', () async {
      final inner = _Scripted([
        const HttpResponseData(401, ''),
        const HttpResponseData(200, '', headers: {'etag': '"3"'}, bodyBytes: [5, 6]),
      ]);
      final renewing = RenewingTransport(inner, () => () async => 'fresh');
      final answer = await renewing.send(const HttpRequestData(
        'POST',
        'http://h/api/x',
        headers: {'Authorization': 'Bearer old'},
        bodyBytes: [1, 2],
        binaryResponse: true,
      ));
      expect(answer.bodyBytes, [5, 6]);
      expect(answer.header('ETag'), '"3"');
      expect(inner.seen, hasLength(2));
      expect(inner.seen[1].headers['Authorization'], 'Bearer fresh');
      expect(inner.seen[1].bodyBytes, [1, 2]);
      expect(inner.seen[1].binaryResponse, isTrue);
    });
  });

  group('the answer of a refused write', () {
    test('is built with the old constructor and carries no headers', () {
      final answer = ListenOnlyGate.refusal('/api/robot/1/command');
      expect(answer.statusCode, 423);
      expect(answer.headers, isEmpty);
      expect(jsonDecode(answer.body)['code'], 'listen-only');
    });
  });
}
