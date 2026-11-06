// =============================================================================
// HYDRA-UMC app common (Dart) - test/server_info_state_test.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The server entry and the views over the settings tree behave as the apps
// relied on when each kept its own copy.
// =============================================================================

import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';
import 'package:test/test.dart';

void main() {
  group('ServerInfo', () {
    test('reads a hydra-info answer and ignores values of the wrong type', () {
      final info = ServerInfo.fromHydraInfo('10.0.0.5', 3000, {
        'product': 'HYDRA-UMC',
        'remoteApiVersion': 4,
        'appVersion': '1.2.3',
        'hostname': 'cm5',
        'controllerCount': 2,
        'robotCount': 'many',
        'uptimeSeconds': double.nan,
      });
      expect(info.product, 'HYDRA-UMC');
      expect(info.remoteApiVersion, 4);
      expect(info.controllerCount, 2);
      expect(info.robotCount, 0);
      expect(info.uptimeSeconds, 0);
      expect(info.baseUrl, 'http://10.0.0.5:3000');
      expect(info.connectionId, '10.0.0.5:3000');
      expect(info.displayName, 'cm5');
    });

    test('a TLS-only server builds https addresses and copyWith keeps the rest', () {
      final info = ServerInfo.fromHydraInfo('h', 443, const {}, useTls: true);
      expect(info.baseUrl, 'https://h:443');
      final named = info.copyWith(nickname: 'bench', username: 'op');
      expect(named.displayName, 'bench');
      expect(named.username, 'op');
      expect(named.useTls, isTrue);
      expect(named.host, 'h');
      expect(named.copyWith(useTls: false).baseUrl, 'http://h:443');
    });

    test('the name falls back from nickname to hostname to host', () {
      expect(const ServerInfo(host: 'a').displayName, 'a');
      expect(const ServerInfo(host: 'a', hostname: 'b').displayName, 'b');
      expect(const ServerInfo(host: 'a', hostname: 'b', nickname: 'c').displayName, 'c');
    });
  });

  group('HydraState', () {
    final tree = <String, dynamic>{
      'activeControllerId': 7,
      'controllers': [
        {
          'id': 7,
          'name': 'Bench',
          'robots': [
            {'id': 1, 'online': true, 'enabled': false, 'jogStep': 1.0, 'model': 'xArm 6'},
            {'id': 2},
            'not a robot',
          ],
        },
      ],
    };

    test('exposes controllers and robots over the raw tree', () {
      final state = HydraState(tree);
      expect(state.activeControllerId, '7');
      final robots = state.activeController!.robots;
      expect(robots.length, 2);
      expect(robots[0].online, isTrue);
      expect(robots[0].isEnabled, isFalse);
      expect(robots[0].manufacturer, 'UFACTORY');
      expect(robots[1].name, 'Robot 2');
      expect(robots[1].isEnabled, isTrue);
    });

    test('writes go through to the raw map and unknown fields stay', () {
      final raw = <String, dynamic>{'id': 3, 'extra': 'kept'};
      final robot = RobotView(raw);
      robot.setOnline(true);
      robot.setEnabled(false);
      robot.setPlaying(true);
      expect(raw['online'], isTrue);
      expect(raw['enabled'], isFalse);
      expect(robot.isPlaying, isTrue);
      robot.setPaused(true);
      expect(robot.isPaused, isTrue);
      robot.stop();
      expect(robot.isPlaying, isFalse);
      expect((raw['playbackState'] as Map)['activeStep'], -1);
      expect(raw['extra'], 'kept');
    });

    test('the jog step picks the nearest offered step and falls back without one', () {
      expect(RobotView({'jogStep': 0.9}).jogStepOr(5, [0.1, 1, 10]), 1);
      expect(RobotView({}).jogStepOr(5, [0.1, 1, 10]), 5);
      expect(RobotView({'jogStep': -1}).jogStep, isNull);
    });

    test('a camera is only reported when vision is really on', () {
      expect(RobotView({'cameraView': {}}).hasCamera, isFalse);
    });
  });
}
