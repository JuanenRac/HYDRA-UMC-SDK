// =============================================================================
// HYDRA-UMC app common (Dart) - src/stop_state_notice.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The `stop-state` message of the server (sent to a connection that asked for
// remoteApiVersion=2): this reads the part the apps show, whether the server
// is stopped only because it restarted while stopped (`restoredAfterRestart`),
// which an administrator has to release.
// =============================================================================

class StopStateNotice {
  StopStateNotice._();

  /// True when [message] is a complete `stop-state` message that says the global stop is on and was restored after a
  /// restart; false for a complete one that says anything else; null for a message that is not a complete `stop-state`
  /// one (so the notice stays as it was).
  static bool? restoredAfterRestart(Map<String, dynamic> message) {
    if (message['type'] != 'stop-state') return null;
    final state = message['state'];
    if (state is! Map) return null;
    final software = state['software'];
    if (software != 'stopped' && software != 'ready') return null;
    return software == 'stopped' && state['restoredAfterRestart'] == true;
  }
}
