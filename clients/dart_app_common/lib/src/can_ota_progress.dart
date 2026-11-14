// =============================================================================
// HYDRA-UMC app common (Dart) - lib/src/can_ota_progress.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The `canota_progress` message of the server: while a real flash cycle of a board runs, every connected administrator receives
// {"type":"canota_progress","payload":{"phase","pages_sent","pages_total","percent","error"}}. This is the one reading of it for
// the Dart apps. Nothing is guessed: a missing or wrong number stays null.
// =============================================================================

/// The phases of a flash cycle, named as the server writes them.
enum CanOtaPhase {
  connecting('connecting'),
  enteringBootloader('entering_bootloader'),
  erasingFram('erasing_fram'),
  transferring('transferring'),
  verifying('verifying'),
  rebooting('rebooting'),
  done('done'),
  error('error');

  final String wire;
  const CanOtaPhase(this.wire);

  /// The phase written [wire], or null for a name this package does not know.
  static CanOtaPhase? fromWire(Object? wire) {
    for (final phase in values) {
      if (phase.wire == wire) return phase;
    }
    return null;
  }
}

/// One report of the progress of a flash cycle.
class CanOtaProgress {
  /// The longest reason kept, in characters.
  static const int maxReasonChars = 300;

  final CanOtaPhase phase;

  /// 0 to 100, or null when the server sent no usable number.
  final int? percent;
  final int? pagesSent;
  final int? pagesTotal;

  /// The reason the bootloader client reports (at most [maxReasonChars] characters), or null.
  final String? error;

  const CanOtaProgress({required this.phase, this.percent, this.pagesSent, this.pagesTotal, this.error});

  /// True once the cycle ended, well or badly.
  bool get finished => phase == CanOtaPhase.done || phase == CanOtaPhase.error;

  static int? _count(Object? value) {
    if (value is! num || !value.isFinite || value < 0 || value != value.floorToDouble() || value > 2147483647) return null;
    return value.toInt();
  }

  /// The progress in a `canota_progress` [message], or null when it carries no phase this package knows.
  static CanOtaProgress? fromMessage(Map<String, dynamic> message) {
    final payload = message['payload'];
    if (payload is! Map) return null;
    final phase = CanOtaPhase.fromWire(payload['phase']);
    if (phase == null) return null;
    final rawPercent = payload['percent'];
    final percent = rawPercent is num && rawPercent.isFinite ? rawPercent.round().clamp(0, 100).toInt() : null;
    final rawReason = payload['error'];
    final reason = rawReason is String && rawReason.trim().isNotEmpty
        ? (rawReason.length > maxReasonChars ? rawReason.substring(0, maxReasonChars) : rawReason)
        : null;
    return CanOtaProgress(
      phase: phase,
      percent: percent,
      pagesSent: _count(payload['pages_sent']),
      pagesTotal: _count(payload['pages_total']),
      error: reason,
    );
  }
}
