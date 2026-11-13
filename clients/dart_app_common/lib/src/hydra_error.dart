// =============================================================================
// HYDRA-UMC app common (Dart) - src/hydra_error.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The error an app's view model reports: a typed kind and the raw parameters,
// never a formatted text. Each app turns it into its own localized sentence
// (HydraError.localize in the app, over its own l10n), so the type is shared
// and the wording is not. A kind an app never produces is simply never built
// there; an app gives such a kind a neutral text.
// =============================================================================

/// What went wrong, in terms every app understands.
enum HydraErrorKind {
  loginFailed,
  loginError,
  fetchFailed,
  robotNotFound,
  notConnected,
  txError,
  unknownCommand,
  wsConnectionLost,
  wsConnectFailed,
  wsAuthRejected,
  voiceAssistantFailed,
  serverMessage,
  robotReserved,
  permissionDenied,
  commandRejected,
  commandNotApplied,
  stopNotConfirmed,
  claimOtherController,
  staleSequence,
  homeRejected,
  jogOutOfReach,
  claimControllerRequired,
  jogNotArmed,
  jogOverLimit,
  savedDataBlocked,
  revisionChanged,
  tlsFailed,
  robotDisabled,
  enableNotAllowed,
  adminRequired,
  homeResetBlocked,
  deadManBlocked,
  deadManEnded,
  deadManStopNotConfirmed,
  pairingOff,
  pairingProblem,
  workBlocked,
  workLoadFailed,
  workInvalidFile,
  systemActionFailed,
  serverReadOnly,
}

/// A kind and its parameters (`error`, `command`, `owner`, `reason`, `limit`, `detail`, ...).
class HydraError {
  final HydraErrorKind kind;
  final Map<String, String> params;
  const HydraError(this.kind, [this.params = const {}]);

  @override
  String toString() => 'HydraError($kind, $params)';
}
