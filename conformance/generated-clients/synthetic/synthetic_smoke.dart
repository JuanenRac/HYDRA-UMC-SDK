// The rules of the generated classes that the contract of the server does not use: an open object keeps the keys it
// does not list, a closed one drops them, a reserved word is renamed, a schema may refer to itself and a map stays a map.
// Run by .github/workflows/generated-clients.yml from synthetic/openapi.json, next to the files the generator wrote.
import 'dart:io';

import 'hydra_server_client.dart';
import 'hydra_server_client_round_trip.dart';

void _expect(bool condition, String what) {
  if (!condition) {
    stderr.writeln('DART_SYNTHETIC_SMOKE=FAIL $what');
    exit(1);
  }
}

Future<void> main() async {
  final open = HydraOpen.fromJson(<String, dynamic>{
    'name': 'n',
    'note': null,
    'class': 'c',
    'in': 4,
    'unlisted': <dynamic>[1, 'two'],
    'scores': <String, dynamic>{'a': 2},
    'nested': <String, dynamic>{
      'points': <dynamic>[
        <String, dynamic>{'x': 1.5},
      ],
    },
  });
  _expect(open.classValue == 'c' && open.inValue == 4 && open.note == null, 'reserved words are renamed and a null reads as null');
  _expect(open.additionalProperties['unlisted'].length == 2 && open.additionalProperties['unlisted'][1] == 'two', 'an open object keeps the keys it does not list');
  _expect(open.scores?['a'] == 2 && open.nested?.points?[0].x == 1.5, 'typed maps and nested inline classes');
  final written = open.toJson();
  _expect(written['unlisted'].length == 2 && written['class'] == 'c' && written.containsKey('note') && written['note'] == null, 'toJson writes the wire names, the kept keys and the required null');
  _expect(!written.containsKey('mode'), 'an optional field that is null is left out');

  final typed = HydraOpenTyped.fromJson(<String, dynamic>{'id': 'a', 'x': 2});
  _expect(typed.additionalProperties['x'] == 2 && typed.toJson()['x'] == 2, 'the keys of an open object follow the schema of additionalProperties');

  final closed = HydraClosed.fromJson(<String, dynamic>{'id': 'a', 'extra': 1});
  _expect(closed.toJson().length == 1 && closed.toJson()['id'] == 'a', 'a closed object drops the keys it does not list');

  final tree = HydraTree.fromJson(<String, dynamic>{
    'label': 'root',
    'children': <dynamic>[
      <String, dynamic>{
        'label': 'leaf',
        'parent': <String, dynamic>{'label': 'root'},
      },
    ],
  });
  _expect(tree.children?[0].label == 'leaf' && tree.children?[0].parent?.label == 'root', 'a schema that refers to itself');
  _expect(HydraTree.fromJson(tree.toJson()).children?[0].parent?.label == 'root', 'a self-referential class reads back what it wrote');

  HydraRequest? seen;
  final client = HydraServerClient((request) async {
    seen = request;
    if (request.path == '/api/bag') {
      return <String, dynamic>{
        'k': <dynamic>['v'],
      };
    }
    return <String, dynamic>{'id': 'z', 'extra': true};
  });
  final bag = await client.getBag();
  final closedBack = await client.putClosed(body: const HydraClosed(id: 'q'));
  _expect(bag['k']?[0] == 'v', 'a named map stays a map');
  final sent = seen?.body;
  _expect(closedBack.id == 'z' && sent is Map && sent['id'] == 'q', 'the body of a request is the plain JSON model');

  final failures = roundTripAll();
  for (final failure in failures) {
    stderr.writeln('DART_SYNTHETIC_SMOKE=FAIL round trip $failure');
  }
  _expect(failures.isEmpty && roundTripClasses == 4, 'the round trip of the synthetic classes');
  stdout.writeln('DART_SYNTHETIC_SMOKE=PASS');
}
