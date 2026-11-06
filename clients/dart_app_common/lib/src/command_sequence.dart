// =============================================================================
// HYDRA-UMC app common (Dart) - src/command_sequence.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The number an app puts on its motion commands (`seq`). The server refuses a
// jog whose number is not above the highest one it has seen from the same
// account and controller, and a stop raises that mark, so a jog sent before a
// stop can never move the robot after it. The number grows by at least one
// with every command and follows the clock, so a restarted app starts above
// everything an earlier run sent.
// =============================================================================

/// A counter of command numbers. The apps keep one per process; tests make
/// their own with a fake clock.
class CommandSequence {
  CommandSequence({Set<String>? numbered, int Function()? clock})
      : numberedCommands = numbered ?? defaultNumbered,
        _clock = clock ?? _systemClock;

  /// The commands the server orders by number: the motion commands, the stop
  /// that must overtake them and the joints move.
  static const Set<String> defaultNumbered = {'stop', 'jog', 'jogStart', 'jogStop', 'table', 'reset', 'joints'};

  final Set<String> numberedCommands;
  final int Function() _clock;
  int _last = 0;

  static int _systemClock() => DateTime.now().millisecondsSinceEpoch;

  bool isNumbered(Object? command) => command is String && numberedCommands.contains(command);

  /// The next number: above the previous one and not below the clock.
  int next() {
    final now = _clock();
    _last = _last + 1 > now ? _last + 1 : now;
    return _last;
  }

  /// Starts over (tests only).
  void reset() => _last = 0;

  /// [payload] with the next `seq` when it is a numbered command; any other
  /// command goes out as it is.
  Map<String, dynamic> numbered(Map<String, dynamic> payload) =>
      isNumbered(payload['command']) ? {...payload, 'seq': next()} : payload;
}
