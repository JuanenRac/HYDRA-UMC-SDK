// =============================================================================
// HYDRA-UMC app common (Dart) - src/listen_only_gate.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// Listen-only mode at the door of the network: the view model already drops
// every command but STOP and the safe-mode disable; this gate also refuses,
// before anything leaves the device, every other write to the server
// (settings, push and presence registration, files, ...). A write is any
// request that is not GET or HEAD. Let through: STOP (the global one and a
// robot command that is stop or disable) and the sign-in, the renewal and the
// end of the session. Pure Dart, so the apps share one rule.
// =============================================================================

import 'dart:convert';

import 'http_transport.dart';

class ListenOnlyGate {
  ListenOnlyGate._();

  /// Opacity of the controls that the mode disables; full opacity when it is off.
  static const double dimmedOpacity = 0.4;
  static double controlOpacity(bool on) => on ? dimmedOpacity : 1.0;

  /// Set by the view model with the switch of the settings; off until the person turns it on.
  static bool enabled = false;

  /// The most servers kept read-only by their own switch.
  static const int maxServers = 50;

  /// How a server is named in the list: its host and port.
  static String serverKey(String host, int port) => '$host:$port';

  /// Whether the mode holds for the server [serverKey]: the general switch, or that server in the list
  /// (no server known: only the general switch).
  static bool effective(bool general, Set<String> servers, String? serverKey) =>
      general || (serverKey != null && servers.contains(serverKey));

  /// The names kept from a stored list: not empty, no longer than 200 characters, no spaces at the ends,
  /// at most [maxServers].
  static Set<String> cleanServers(Iterable<String> raw) =>
      raw.where((s) => s.isNotEmpty && s.length <= 200 && s.trim() == s).take(maxServers).toSet();

  static const Set<String> _allowedCommands = {'stop', 'jogStop', 'disable'};
  static const Set<String> _sessionNames = {'login', 'refresh', 'logout'};

  /// Whether a request may leave the app while the mode is on. Pure. The path is read by its segments.
  static bool allows(String method, String path, String? body) {
    final m = method.toUpperCase();
    if (m == 'GET' || m == 'HEAD') return true;
    final parts = path.split('/').where((p) => p.isNotEmpty).toList();
    if (parts.isEmpty || parts.first != 'api') return false;
    final rest = parts.sublist(1);
    if (rest.length == 1 && (_sessionNames.contains(rest[0]) || rest[0] == 'stop-all')) return true;
    if (rest.length == 2 && rest[0] == 'device' && rest[1] == 'login') return true;
    if (rest.length == 3 && rest[0] == 'robot' && rest[2] == 'command' && body != null) {
      try {
        final decoded = jsonDecode(body);
        return decoded is Map && _allowedCommands.contains(decoded['command']);
      } catch (_) {
        return false;
      }
    }
    return false;
  }

  /// The answer of a refused write: 423, as if the server had locked the route, and nothing was sent.
  /// [device] names what the person holds in the sentence ("app" on a phone, "panel" on the display).
  static HttpResponseData refusal(String path, {String device = 'app'}) => HttpResponseData(
        423,
        jsonEncode({
          'error': 'Listen only is on: nothing is written from this $device except STOP.',
          'code': 'listen-only',
        }),
        path: path,
      );
}
