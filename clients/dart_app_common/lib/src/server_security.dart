// =============================================================================
// HYDRA-UMC app common (Dart) - src/server_security.dart
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
//
// The access options of the server an administrator can change: nine switches
// of GET/PUT /api/admin/server-config - the health route without a sign-in, the
// announcement of the global stop, the address kept in the history of
// connections, the camera pictures without a ticket, a token in the WebSocket
// address, the blanking of secrets in the log, the signature of a spoken
// confirmation, the password of an IP camera handed over through the
// environment of its process and TLS switched on by a new installation. The
// reading is tolerant: a server that predates an option answers without it and
// the screen does not show that switch. A value fixed by the environment of the
// server cannot be changed from here, and every change that lowers the
// protection is asked about first.
//
// Shared by the Flutter apps; the screen texts stay in each app.
// =============================================================================

import 'dart:convert';

/// Where the value of an option comes from. An [env] value is fixed by the environment of the server.
enum OptionSource { env, config, defaultValue }

/// One switch as the server reports it.
class ServerOption {
  final bool value;
  final OptionSource source;
  const ServerOption(this.value, this.source);

  bool get locked => source == OptionSource.env;

  @override
  bool operator ==(Object other) => other is ServerOption && other.value == value && other.source == source;

  @override
  int get hashCode => Object.hash(value, source);
}

/// What the switches of the screen say.
class ServerSecurityValues {
  final bool healthOpen;
  final bool publishGlobalStop;
  final bool recordAddress;
  final bool cameraOpen;
  final bool wsQueryToken;
  final bool logRedaction;
  final bool voiceSignature;
  final bool cameraCredentialsViaEnv;
  final bool newInstallTls;

  const ServerSecurityValues({
    required this.healthOpen,
    required this.publishGlobalStop,
    required this.recordAddress,
    required this.cameraOpen,
    required this.wsQueryToken,
    required this.logRedaction,
    required this.voiceSignature,
    this.cameraCredentialsViaEnv = true,
    this.newInstallTls = true,
  });

  ServerSecurityValues copyWith({
    bool? healthOpen,
    bool? publishGlobalStop,
    bool? recordAddress,
    bool? cameraOpen,
    bool? wsQueryToken,
    bool? logRedaction,
    bool? voiceSignature,
    bool? cameraCredentialsViaEnv,
    bool? newInstallTls,
  }) =>
      ServerSecurityValues(
        healthOpen: healthOpen ?? this.healthOpen,
        publishGlobalStop: publishGlobalStop ?? this.publishGlobalStop,
        recordAddress: recordAddress ?? this.recordAddress,
        cameraOpen: cameraOpen ?? this.cameraOpen,
        wsQueryToken: wsQueryToken ?? this.wsQueryToken,
        logRedaction: logRedaction ?? this.logRedaction,
        voiceSignature: voiceSignature ?? this.voiceSignature,
        cameraCredentialsViaEnv: cameraCredentialsViaEnv ?? this.cameraCredentialsViaEnv,
        newInstallTls: newInstallTls ?? this.newInstallTls,
      );
}

/// The switches this app offers; each is null when the server does not report it.
class ServerSecurityOptions {
  final ServerOption? healthOpen;
  final ServerOption? publishGlobalStop;
  final ServerOption? recordAddress;
  final ServerOption? cameraOpen;
  final ServerOption? wsQueryToken;
  final ServerOption? logRedaction;
  final ServerOption? voiceSignature;
  final ServerOption? cameraCredentialsViaEnv;
  final ServerOption? newInstallTls;

  const ServerSecurityOptions({
    this.healthOpen,
    this.publishGlobalStop,
    this.recordAddress,
    this.cameraOpen,
    this.wsQueryToken,
    this.logRedaction,
    this.voiceSignature,
    this.cameraCredentialsViaEnv,
    this.newInstallTls,
  });

  List<ServerOption?> get _all => [
        healthOpen,
        publishGlobalStop,
        recordAddress,
        cameraOpen,
        wsQueryToken,
        logRedaction,
        voiceSignature,
        cameraCredentialsViaEnv,
        newInstallTls,
      ];

  /// True when the server reports none of them (a server that predates all of these options).
  bool get isEmpty => _all.every((o) => o == null);

  /// [ServerSecurity.parse], for callers that read the options through their own type.
  static ServerSecurityOptions? parse(String body) => ServerSecurity.parse(body);

  /// The body of the change from these options to [next] (same as [ServerSecurity.patch]).
  Map<String, dynamic>? patch(ServerSecurityValues next) => ServerSecurity.patch(this, next);

  /// The changes to [next] that lower the protection (same as [ServerSecurity.lowerings]).
  List<ProtectionLowering> lowerings(ServerSecurityValues next) => ServerSecurity.lowerings(this, next);

  /// The values as the screen starts with them; an option the server does not report keeps its safe value.
  ServerSecurityValues toValues() => ServerSecurityValues(
        healthOpen: healthOpen?.value ?? false,
        publishGlobalStop: publishGlobalStop?.value ?? false,
        recordAddress: recordAddress?.value ?? false,
        cameraOpen: cameraOpen?.value ?? false,
        wsQueryToken: wsQueryToken?.value ?? false,
        logRedaction: logRedaction?.value ?? true,
        voiceSignature: voiceSignature?.value ?? false,
        cameraCredentialsViaEnv: cameraCredentialsViaEnv?.value ?? true,
        newInstallTls: newInstallTls?.value ?? true,
      );
}

/// The changes that lower the protection of the server; the screen has a sentence for each.
enum ProtectionLowering {
  healthOpen,
  recordAddress,
  cameraOpen,
  wsQueryToken,
  logRedactionOff,
  voiceSignatureOff,
  cameraCredentialsInArguments,
  newInstallTlsOff,
}

/// Why the options could not be read or saved, for the sentence the screen shows.
enum ServerOptionsFailure { unavailable, session, forbidden, network, other }

class ServerSecurity {
  ServerSecurity._();

  static ServerOption? _option(Object? json) {
    if (json is! Map<String, dynamic>) return null;
    final value = json['value'];
    if (value is! bool) return null;
    final source = switch (json['source']) {
      'env' => OptionSource.env,
      'config' => OptionSource.config,
      'default' => OptionSource.defaultValue,
      _ => null,
    };
    return source == null ? null : ServerOption(value, source);
  }

  static Object? _at(Map<String, dynamic> root, String group, String name) {
    final node = root[group];
    return node is Map<String, dynamic> ? node[name] : null;
  }

  /// Reads the answer of GET /api/admin/server-config; null when the text is not a JSON object.
  static ServerSecurityOptions? parse(String body) {
    final Object? root;
    try {
      root = jsonDecode(body);
    } catch (_) {
      return null;
    }
    if (root is! Map<String, dynamic>) return null;
    return ServerSecurityOptions(
      healthOpen: _option(_at(root, 'health', 'open')),
      publishGlobalStop: _option(_at(root, 'safety', 'publishGlobalStop')),
      recordAddress: _option(_at(root, 'connections', 'recordAddress')),
      cameraOpen: _option(_at(root, 'camera', 'open')),
      wsQueryToken: _option(_at(root, 'websocket', 'allowQueryToken')),
      logRedaction: _option(_at(root, 'logging', 'redactSecrets')),
      voiceSignature: _option(_at(root, 'voice', 'requireSignature')),
      cameraCredentialsViaEnv: _option(_at(root, 'camera', 'credentialsViaEnv')),
      newInstallTls: _option(_at(root, 'install', 'newInstallTls')),
    );
  }

  /// The request body: only what changed, and never an option the server fixes from its environment or does not
  /// report. Null when nothing would be sent.
  static Map<String, dynamic>? patch(ServerSecurityOptions current, ServerSecurityValues next) {
    final body = <String, dynamic>{};
    void put(String group, String name, ServerOption? option, bool wanted) {
      if (option == null || option.locked || option.value == wanted) return;
      (body.putIfAbsent(group, () => <String, dynamic>{}) as Map<String, dynamic>)[name] = wanted;
    }

    put('health', 'open', current.healthOpen, next.healthOpen);
    put('safety', 'publishGlobalStop', current.publishGlobalStop, next.publishGlobalStop);
    put('connections', 'recordAddress', current.recordAddress, next.recordAddress);
    put('camera', 'open', current.cameraOpen, next.cameraOpen);
    put('websocket', 'allowQueryToken', current.wsQueryToken, next.wsQueryToken);
    put('logging', 'redactSecrets', current.logRedaction, next.logRedaction);
    put('voice', 'requireSignature', current.voiceSignature, next.voiceSignature);
    put('camera', 'credentialsViaEnv', current.cameraCredentialsViaEnv, next.cameraCredentialsViaEnv);
    put('install', 'newInstallTls', current.newInstallTls, next.newInstallTls);
    return body.isEmpty ? null : body;
  }

  /// The changes in [next] that lower the protection, in a fixed order. Turning a switch to its safe side never
  /// asks, and neither does the announcement of the global stop (announcing a stop is the safe direction). An option
  /// the server fixes is not a change.
  static List<ProtectionLowering> lowerings(ServerSecurityOptions current, ServerSecurityValues next) {
    bool rises(ServerOption? o, bool wanted) => o != null && !o.locked && !o.value && wanted;
    bool falls(ServerOption? o, bool wanted) => o != null && !o.locked && o.value && !wanted;
    return [
      if (rises(current.healthOpen, next.healthOpen)) ProtectionLowering.healthOpen,
      if (rises(current.recordAddress, next.recordAddress)) ProtectionLowering.recordAddress,
      if (rises(current.cameraOpen, next.cameraOpen)) ProtectionLowering.cameraOpen,
      if (rises(current.wsQueryToken, next.wsQueryToken)) ProtectionLowering.wsQueryToken,
      if (falls(current.logRedaction, next.logRedaction)) ProtectionLowering.logRedactionOff,
      if (falls(current.voiceSignature, next.voiceSignature)) ProtectionLowering.voiceSignatureOff,
      if (falls(current.cameraCredentialsViaEnv, next.cameraCredentialsViaEnv)) ProtectionLowering.cameraCredentialsInArguments,
      if (falls(current.newInstallTls, next.newInstallTls)) ProtectionLowering.newInstallTlsOff,
    ];
  }
}
