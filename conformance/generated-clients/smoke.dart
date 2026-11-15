// Runs the generated Dart client against a transport that records the request, so the file is not only analysed
// but also called: the requests keep their shape, the answers are read into classes, and an example of every class of
// the contract goes through fromJson and toJson and must come back unchanged.
// Usage: dart run smoke.dart (next to hydra_server_client.dart and hydra_server_client_round_trip.dart)
import 'dart:io';

import 'hydra_server_client.dart';
import 'hydra_server_client_round_trip.dart';

Future<void> main() async {
  final seen = <HydraRequest>[];
  final client = HydraServerClient((request) async {
    seen.add(request);
    if (request.replyHeaders.isNotEmpty) {
      return const HydraReply<dynamic>(<String, dynamic>{'controllers': <dynamic>[<String, dynamic>{'id': 'c1'}]}, <String, String>{'ETag': 'w/1'});
    }
    switch (request.path) {
      case '/api/robot/7/command':
        return <String, dynamic>{'success': true, 'revision': 'r2', 'affectedCount': 1, 'operation_id': 'op-1'};
      case '/api/robot/9':
        return <String, dynamic>{'robot': <String, dynamic>{'id': 9}, 'revision': 'r1'};
      case '/api/hardware/canota/flash':
        return <String, dynamic>{'success': true, 'finalPhase': 'done'};
    }
    return <String, dynamic>{'lines': <dynamic>['a', 'b']};
  });

  final logs = await client.getAdminLogs(lines: '5');
  final command = await client.postRobotByIdCommand(id: 7, body: const HydraPostRobotByIdCommandBody(command: 'stop'));
  final robot = await client.getRobotById(id: 9);
  final flash = await client.postHardwareCanotaFlash(body: <int>[1, 2, 3]);
  final settings = await client.getSettingsWithHeaders();

  _expect(seen[0].method == 'GET' && seen[0].path == '/api/admin/logs' && seen[0].query['lines'] == '5', 'query');
  final sent = seen[1].body;
  _expect(seen[1].method == 'POST' && seen[1].path == '/api/robot/7/command' && sent is Map && sent.length == 1 && sent['command'] == 'stop', 'path and body: the class is sent as the plain JSON model');
  _expect(seen[2].query.isEmpty && seen[2].path == '/api/robot/9', 'no query');
  _expect(seen[3].contentType == 'application/octet-stream' && seen[3].body is List<int>, 'binary body');
  _expect(seen[4].replyHeaders.length == 1 && seen[4].replyHeaders[0] == 'ETag' && seen[4].path == '/api/settings' && settings.headers['ETag'] == 'w/1', 'reply with headers');
  _expect(logs.lines.length == 2 && logs.lines[1] == 'b', 'a list of text is read into the class');
  _expect(command.success && command.revision == 'r2' && command.affectedCount == 1 && command.operationId == 'op-1', 'the answer is read into its class with camelCase names');
  _expect(robot.revision == 'r1' && robot.robot['id'] == 9 && robot.cellId == null, 'an optional field that is absent reads as null');
  _expect(flash.finalPhase == 'done', 'the answer of the binary route');
  _expect(settings.body.controllers?.length == 1, 'the reply with headers keeps the typed body');
  final left = const HydraPostRobotByIdCommandBody(command: 'stop', seq: 3).toJson();
  _expect(left.length == 2 && left['seq'] == 3 && !left.containsKey('controllerId'), 'an optional field that is null is left out of toJson');
  var refusedField = false;
  try {
    HydraLogLines.fromJson(<String, dynamic>{});
  } catch (_) {
    refusedField = true;
  }
  _expect(refusedField, 'a missing required field must throw');
  _expect(fillPath('/a/{x}', {'x': 'a b/c'}) == '/a/a%20b%2Fc', 'escape');

  try {
    fillPath('/a/{x}', {});
    _expect(false, 'a missing path value must throw');
  } on ArgumentError {
    // expected
  }
  _expect(hydraClientOperations.contains('getAdminLogs'), 'operation list');

  final failures = roundTripAll();
  for (final failure in failures) {
    stderr.writeln('DART_CLIENT_SMOKE=FAIL round trip $failure');
  }
  _expect(failures.isEmpty, 'every class reads and writes its example unchanged');
  _expect(roundTripClasses > 40, 'the round trip covers the classes of the contract');
  stdout.writeln('DART_CLIENT_SMOKE=PASS ${hydraClientOperations.length} operations, $roundTripClasses classes round-tripped');
}

void _expect(bool condition, String what) {
  if (!condition) {
    stderr.writeln('DART_CLIENT_SMOKE=FAIL $what');
    exit(1);
  }
}
