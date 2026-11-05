// =============================================================================
// HYDRA-UMC-IOS-CONTROL - WebSocket endpoint encoding test
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

import 'package:test/test.dart';
import 'package:hydra_umc_app_common/hydra_umc_app_common.dart';

void main() {
  test('never puts the bearer token, whatever characters it holds, into the WebSocket address', () {
    final uri = HydraWebSocket.buildConnectionUri(
      host: '192.168.1.20',
      port: 3000,
      token: 'token+with/characters?and=value',
    );

    expect(uri.scheme, 'ws');
    expect(uri.path, '/ws');
    expect(uri.queryParameters.containsKey('token'), isFalse);
    expect(uri.toString(), isNot(contains('characters')));
    expect(uri.queryParameters['remoteApiVersion'], '2');
  });
}
