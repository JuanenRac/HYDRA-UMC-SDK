// Runs the generated Dart client against a transport that records the request, so the file is not only analysed
// but also called. Usage: dart run smoke.dart <path of generated/hydra_server_client.dart>
import 'dart:io';

import 'hydra_server_client.dart';

Future<void> main() async {
  final seen = <HydraRequest>[];
  final client = HydraServerClient((request) async {
    seen.add(request);
    if (request.replyHeaders.isNotEmpty) {
      return const HydraReply<dynamic>(<String, dynamic>{'ok': true}, <String, String>{'ETag': 'w/1'});
    }
    return <String, dynamic>{'lines': <dynamic>[]};
  });

  await client.getAdminLogs(lines: '5');
  await client.postRobotByIdCommand(id: 7, body: <String, dynamic>{'command': 'stop'});
  await client.getRobotById(id: 9);
  await client.postHardwareCanotaFlash(body: <int>[1, 2, 3]);
  final settings = await client.getSettingsWithHeaders();

  _expect(seen[0].method == 'GET' && seen[0].path == '/api/admin/logs' && seen[0].query['lines'] == '5', 'query');
  _expect(seen[1].method == 'POST' && seen[1].path == '/api/robot/7/command' && seen[1].body != null, 'path and body');
  _expect(seen[2].query.isEmpty && seen[2].path == '/api/robot/9', 'no query');
  _expect(seen[3].contentType == 'application/octet-stream' && seen[3].body is List<int>, 'binary body');
  _expect(seen[4].replyHeaders.length == 1 && seen[4].replyHeaders[0] == 'ETag' && seen[4].path == '/api/settings' && settings.headers['ETag'] == 'w/1', 'reply with headers');
  _expect(fillPath('/a/{x}', {'x': 'a b/c'}) == '/a/a%20b%2Fc', 'escape');

  try {
    fillPath('/a/{x}', {});
    _expect(false, 'a missing path value must throw');
  } on ArgumentError {
    // expected
  }
  _expect(hydraClientOperations.contains('getAdminLogs'), 'operation list');
  stdout.writeln('DART_CLIENT_SMOKE=PASS ${hydraClientOperations.length} operations');
}

void _expect(bool condition, String what) {
  if (!condition) {
    stderr.writeln('DART_CLIENT_SMOKE=FAIL $what');
    exit(1);
  }
}
