// Runs the generated Dart client against a transport that records the request, so the file is not only analysed
// but also called. Usage: dart run smoke.dart <path of generated/hydra_server_client.dart>
import 'dart:io';

import 'hydra_server_client.dart';

Future<void> main() async {
  final seen = <HydraRequest>[];
  final client = HydraServerClient((request) async {
    seen.add(request);
    return <String, dynamic>{'lines': <dynamic>[]};
  });

  await client.getAdminLogs(lines: '5');
  await client.postRobotByIdCommand(id: 7, body: <String, dynamic>{'command': 'stop'});
  await client.getRobotById(id: 9);

  _expect(seen[0].method == 'GET' && seen[0].path == '/api/admin/logs' && seen[0].query['lines'] == '5', 'query');
  _expect(seen[1].method == 'POST' && seen[1].path == '/api/robot/7/command' && seen[1].body != null, 'path and body');
  _expect(seen[2].query.isEmpty && seen[2].path == '/api/robot/9', 'no query');
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
