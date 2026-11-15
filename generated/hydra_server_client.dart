// Generated from the server contract by tools/generate_clients.py. Do not edit.
// ignore_for_file: unused_element

// The transport hands back the decoded JSON model: Map, List, String, int, double, bool or null.

/// Fields: success, devices
typedef HydraBluetoothScan = Map<String, dynamic>;

/// Fields: accepted, result
typedef HydraBridgeCommandAccepted = Map<String, dynamic>;

/// Fields: connected, bridges
typedef HydraBridgeList = Map<String, dynamic>;

/// Fields: name, available, state, health, updatedAt
typedef HydraBridgeState = Map<String, dynamic>;

/// Fields: success, cameraId, filename, capturedAt?, sizeBytes?, startedAt?, stoppedAt?
typedef HydraCameraCapture = Map<String, dynamic>;

/// Fields: items
typedef HydraCameraMediaList = Map<String, dynamic>;

typedef HydraCameraProcessStatus = Map<String, dynamic>;

/// Fields: success, finalPhase
typedef HydraCanotaFlash = Map<String, dynamic>;

/// Fields: clients
typedef HydraClients = Map<String, dynamic>;

/// Fields: schema_version, id, kind, user?, app_version?, origin?, two_factor?, first_seen_utc, last_seen_utc, last_failure_utc?, active_sessions, logins_ok, logins_failed, ip?, agent?
typedef HydraConnectionClient = Map<String, dynamic>;

/// Fields: clients
typedef HydraConnectionClientList = Map<String, dynamic>;

/// Fields: schema_version, id, at_utc, action, client_kind, client_id, user?, origin?, two_factor?, app_version?, ip?, agent?
typedef HydraConnectionEvent = Map<String, dynamic>;

/// Fields: events
typedef HydraConnectionEventList = Map<String, dynamic>;

/// Fields: id, name, username, createdAt, expiresAt, revokedAt, lastUsedAt, state, token
typedef HydraDeviceTokenIssued = Map<String, dynamic>;

/// Fields: items
typedef HydraDeviceTokenList = Map<String, dynamic>;

/// Fields: revoked, sessionsEnded
typedef HydraDeviceTokenRevoked = Map<String, dynamic>;

/// Fields: id, name, username, createdAt, expiresAt, revokedAt, lastUsedAt, state
typedef HydraDeviceTokenView = Map<String, dynamic>;

/// Fields: schema_version, generated_at_utc, available, summary, services, certificate, warnings
typedef HydraEcosystemHealth = Map<String, dynamic>;

/// Fields: available, scannedAt, projects
typedef HydraEcosystemStatus = Map<String, dynamic>;

/// Fields: error
typedef HydraError = Map<String, dynamic>;

/// Fields: schema, id, mode, state, startedAt, updatedAt, error, stoppedAt, requireSignedTags, disk, services
typedef HydraFleetUpdateReport = Map<String, dynamic>;

/// Fields: name, kind, repo, installed, latest, action, reason, state, step, substep?, substeps?, detail, error, order, elapsedS?, freeMb?, needMb?, unitRestored?, log
typedef HydraFleetUpdateRow = Map<String, dynamic>;

/// Fields: applyEnabled, busy, report
typedef HydraFleetUpdateStatus = Map<String, dynamic>;

/// Fields: success, announced
typedef HydraGlobalStopReleased = Map<String, dynamic>;

/// Fields: schema_version, state, timestamp_utc, checks, service?
typedef HydraHealthReport = Map<String, dynamic>;

/// Fields: schema_version, product, remoteApiVersion, appVersion, hostname, controllerCount, robotCount, uptimeSeconds, addresses?
typedef HydraHydraInfo = Map<String, dynamic>;

/// Fields: ticket, expiresInSeconds
typedef HydraInfoTicket = Map<String, dynamic>;

/// Fields: keys
typedef HydraJwksDocument = Map<String, dynamic>;

/// Fields: success, kid, algorithm, keys, jwksPath
typedef HydraJwtKeyRotated = Map<String, dynamic>;

/// Fields: algorithm, keys, jwksPath
typedef HydraJwtKeys = Map<String, dynamic>;

/// Fields: registered
typedef HydraLiveActivityRegistered = Map<String, dynamic>;

/// Fields: removed
typedef HydraLiveActivityRemoved = Map<String, dynamic>;

/// Fields: lines
typedef HydraLogLines = Map<String, dynamic>;

/// Fields: success, token, refreshToken, role
typedef HydraLoginResult = Map<String, dynamic>;

/// Fields: ok, action, exitCode, timedOut, result, message
typedef HydraMaintenanceOutcome = Map<String, dynamic>;

/// Fields: models
typedef HydraModelList = Map<String, dynamic>;

/// Fields: success, slug
typedef HydraModelSubmitted = Map<String, dynamic>;

/// Fields: online, slot, heard, ageMs?, sequence?, flags?, flagNames?, txErrors?, rxErrors?, stalls?, uptimeS?, source
typedef HydraNodeHealth = Map<String, dynamic>;

/// Fields: state, lastSequence, secondsSinceBeat, action, timeoutSeconds, degradedRobots
typedef HydraOperatorPresence = Map<String, dynamic>;

/// Fields: accepted, duplicate, stale, state, sequence, action, timeoutSeconds
typedef HydraOperatorPresenceAck = Map<String, dynamic>;

typedef HydraPassthrough = Map<String, dynamic>;

/// Fields: ok
typedef HydraPtzResult = Map<String, dynamic>;

/// Fields: registered
typedef HydraPushDeviceRegistered = Map<String, dynamic>;

/// Fields: removed
typedef HydraPushDeviceRemoved = Map<String, dynamic>;

/// Fields: enabled, configured, problem, devices, sandbox, events, liveActivity?
typedef HydraPushStatus = Map<String, dynamic>;

/// Fields: reachable
typedef HydraReachable = Map<String, dynamic>;

/// Fields: success, reservation?, reservationHistory
typedef HydraReservation = Map<String, dynamic>;

/// Fields: schema_version, stale_after_s, robots
typedef HydraRobotLiveness = Map<String, dynamic>;

/// Fields: enabled, maxPoints, timeoutMs
typedef HydraRulConfig = Map<String, dynamic>;

/// Fields: id, repo, installed, previous, latest, state, signedPackage
typedef HydraSelfUpdateItem = Map<String, dynamic>;

/// Fields: id, action, component, state, fromVersion, targetVersion, startedAt, updatedAt, error, detail, packageName?, log, by
typedef HydraSelfUpdateJob = Map<String, dynamic>;

/// Fields: checkedAt, owner, rateLimited, items, applyEnabled, job
typedef HydraSelfUpdateStatus = Map<String, dynamic>;

/// Fields: port, pendingPort
typedef HydraServerConfig = Map<String, dynamic>;

/// Fields: success, appliesOnRestart
typedef HydraServerConfigSaved = Map<String, dynamic>;

/// Fields: enabled, source, locked, key, state, services, order
typedef HydraServiceIdentityStatus = Map<String, dynamic>;

/// Fields: controllers?
typedef HydraSettings = Map<String, dynamic>;

/// Fields: success, stoppedCount, failedCount, persisted, announced?, robots
typedef HydraStopAllResult = Map<String, dynamic>;

/// Fields: success
typedef HydraSuccess = Map<String, dynamic>;

typedef HydraSupervisorSnapshot = Map<String, dynamic>;

/// Fields: cpu_load, memory_usage, temp, temp_is_real, rp1_temp, uptime, network
typedef HydraSystemMetrics = Map<String, dynamic>;

/// Fields: success, robot, toolId
typedef HydraToolArmResetResult = Map<String, dynamic>;

/// Fields: schema_version, ttlSeconds, arms, armedCount, staleCount
typedef HydraToolArmsReport = Map<String, dynamic>;

/// Fields: success, recoveryCodes
typedef HydraTotpConfirmed = Map<String, dynamic>;

/// Fields: success, secret, uri
typedef HydraTotpEnrolment = Map<String, dynamic>;

/// Fields: enabled, recoveryLeft
typedef HydraTotpStatus = Map<String, dynamic>;

/// Fields: name, family, installed, latest, state
typedef HydraUpdateItem = Map<String, dynamic>;

/// Fields: checkedAt, owner, rateLimited, items
typedef HydraUpdateReport = Map<String, dynamic>;

/// Fields: devices
typedef HydraUsbDevices = Map<String, dynamic>;

/// Fields: users
typedef HydraUserList = Map<String, dynamic>;

/// Fields: type, requestId, text, level, speak, requiresConfirmation, visualState?, intent?, interpretation?, messageCode?, messageParams?, textLanguage?, confirmationToken?, confirmationValiditySeconds?
typedef HydraVoiceReply = Map<String, dynamic>;

/// Fields: type, headline, detail, level, speak
typedef HydraWatchStatus = Map<String, dynamic>;

class HydraRequest {
  const HydraRequest(this.method, this.path, this.query, this.body, this.access, {this.headers = const <String, String>{}});
  final String method;
  final String path;
  final Map<String, String> query;
  final Object? body;
  final String access;
  final Map<String, String> headers;
}

/// Carries one request to the server and returns the decoded JSON of the answer (null when there is none).
typedef HydraTransport = Future<dynamic> Function(HydraRequest request);

String fillPath(String template, Map<String, Object> values) {
  return template.replaceAllMapped(RegExp(r'\{([^}]+)\}'), (match) {
    final value = values[match.group(1)]?.toString();
    if (value == null || value.isEmpty) {
      throw ArgumentError('missing path parameter ${match.group(1)}');
    }
    return Uri.encodeComponent(value);
  });
}

Map<String, String> queryOf(Map<String, Object?> values) {
  return {
    for (final entry in values.entries)
      if (entry.value != null) entry.key: entry.value.toString(),
  };
}

class HydraServerClient {
  HydraServerClient(this._transport);

  final HydraTransport _transport;

  /// GET /.well-known/jwks.json (access: public)
  Future<HydraJwksDocument> getWellKnownJwksJson() async {
    return (await _transport(HydraRequest('GET', '/.well-known/jwks.json', const <String, String>{}, null, 'public'))) as HydraJwksDocument;
  }

  /// GET /api/adapters (access: user)
  Future<HydraPassthrough> getAdapters() async {
    return (await _transport(HydraRequest('GET', '/api/adapters', const <String, String>{}, null, 'user'))) as HydraPassthrough;
  }

  /// GET /api/adapters/{adapterId} (access: user)
  Future<void> getAdaptersByAdapterId({required String adapterId}) async {
    await _transport(HydraRequest('GET', fillPath('/api/adapters/{adapterId}', {'adapterId': adapterId}), const <String, String>{}, null, 'user'));
  }

  /// GET /api/admin/clients (access: admin)
  Future<HydraClients> getAdminClients() async {
    return (await _transport(HydraRequest('GET', '/api/admin/clients', const <String, String>{}, null, 'admin'))) as HydraClients;
  }

  /// GET /api/admin/device-tokens (access: admin)
  Future<HydraDeviceTokenList> getAdminDeviceTokens() async {
    return (await _transport(HydraRequest('GET', '/api/admin/device-tokens', const <String, String>{}, null, 'admin'))) as HydraDeviceTokenList;
  }

  /// POST /api/admin/device-tokens (access: admin)
  Future<HydraDeviceTokenIssued> postAdminDeviceTokens({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/admin/device-tokens', const <String, String>{}, body, 'admin'))) as HydraDeviceTokenIssued;
  }

  /// DELETE /api/admin/device-tokens/{id} (access: admin)
  Future<HydraDeviceTokenRevoked> deleteAdminDeviceTokensById({required String id}) async {
    return (await _transport(HydraRequest('DELETE', fillPath('/api/admin/device-tokens/{id}', {'id': id}), const <String, String>{}, null, 'admin'))) as HydraDeviceTokenRevoked;
  }

  /// GET /api/admin/fleet-update (access: admin)
  Future<HydraFleetUpdateStatus> getAdminFleetUpdate() async {
    return (await _transport(HydraRequest('GET', '/api/admin/fleet-update', const <String, String>{}, null, 'admin'))) as HydraFleetUpdateStatus;
  }

  /// POST /api/admin/fleet-update/apply (access: admin)
  Future<HydraFleetUpdateStatus> postAdminFleetUpdateApply({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/admin/fleet-update/apply', const <String, String>{}, body, 'admin'))) as HydraFleetUpdateStatus;
  }

  /// POST /api/admin/fleet-update/plan (access: admin)
  Future<HydraFleetUpdateStatus> postAdminFleetUpdatePlan() async {
    return (await _transport(HydraRequest('POST', '/api/admin/fleet-update/plan', const <String, String>{}, null, 'admin'))) as HydraFleetUpdateStatus;
  }

  /// POST /api/admin/fleet-update/resume (access: admin)
  Future<HydraFleetUpdateStatus> postAdminFleetUpdateResume({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/admin/fleet-update/resume', const <String, String>{}, body, 'admin'))) as HydraFleetUpdateStatus;
  }

  /// GET /api/admin/jwt-keys (access: admin)
  Future<HydraJwtKeys> getAdminJwtKeys() async {
    return (await _transport(HydraRequest('GET', '/api/admin/jwt-keys', const <String, String>{}, null, 'admin'))) as HydraJwtKeys;
  }

  /// POST /api/admin/jwt-keys/rotate (access: admin)
  Future<HydraJwtKeyRotated> postAdminJwtKeysRotate() async {
    return (await _transport(HydraRequest('POST', '/api/admin/jwt-keys/rotate', const <String, String>{}, null, 'admin'))) as HydraJwtKeyRotated;
  }

  /// GET /api/admin/logs (access: admin)
  Future<HydraLogLines> getAdminLogs({String? lines}) async {
    return (await _transport(HydraRequest('GET', '/api/admin/logs', queryOf({'lines': lines}), null, 'admin'))) as HydraLogLines;
  }

  /// POST /api/admin/maintenance/install (access: admin)
  Future<HydraMaintenanceOutcome> postAdminMaintenanceInstall({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/admin/maintenance/install', const <String, String>{}, body, 'admin'))) as HydraMaintenanceOutcome;
  }

  /// POST /api/admin/maintenance/prune (access: admin)
  Future<HydraMaintenanceOutcome> postAdminMaintenancePrune({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/admin/maintenance/prune', const <String, String>{}, body, 'admin'))) as HydraMaintenanceOutcome;
  }

  /// POST /api/admin/maintenance/rollback (access: admin)
  Future<HydraMaintenanceOutcome> postAdminMaintenanceRollback({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/admin/maintenance/rollback', const <String, String>{}, body, 'admin'))) as HydraMaintenanceOutcome;
  }

  /// GET /api/admin/maintenance/status (access: admin)
  Future<HydraMaintenanceOutcome> getAdminMaintenanceStatus({String? component}) async {
    return (await _transport(HydraRequest('GET', '/api/admin/maintenance/status', queryOf({'component': component}), null, 'admin'))) as HydraMaintenanceOutcome;
  }

  /// GET /api/admin/push (access: admin)
  Future<HydraPushStatus> getAdminPush() async {
    return (await _transport(HydraRequest('GET', '/api/admin/push', const <String, String>{}, null, 'admin'))) as HydraPushStatus;
  }

  /// POST /api/admin/restart (access: admin)
  Future<HydraSuccess> postAdminRestart() async {
    return (await _transport(HydraRequest('POST', '/api/admin/restart', const <String, String>{}, null, 'admin'))) as HydraSuccess;
  }

  /// GET /api/admin/robot-ids (access: admin)
  Future<Map<String, dynamic>> getAdminRobotIds() async {
    return (await _transport(HydraRequest('GET', '/api/admin/robot-ids', const <String, String>{}, null, 'admin'))) as Map<String, dynamic>;
  }

  /// PUT /api/admin/safety-limits (access: admin)
  Future<Map<String, dynamic>> putAdminSafetyLimits({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('PUT', '/api/admin/safety-limits', const <String, String>{}, body, 'admin'))) as Map<String, dynamic>;
  }

  /// GET /api/admin/self-update (access: admin)
  Future<HydraSelfUpdateStatus> getAdminSelfUpdate({String? refresh}) async {
    return (await _transport(HydraRequest('GET', '/api/admin/self-update', queryOf({'refresh': refresh}), null, 'admin'))) as HydraSelfUpdateStatus;
  }

  /// POST /api/admin/self-update/apply (access: admin)
  Future<HydraSelfUpdateJob> postAdminSelfUpdateApply({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/admin/self-update/apply', const <String, String>{}, body, 'admin'))) as HydraSelfUpdateJob;
  }

  /// GET /api/admin/self-update/jobs/{id} (access: admin)
  Future<HydraSelfUpdateJob> getAdminSelfUpdateJobsById({required String id}) async {
    return (await _transport(HydraRequest('GET', fillPath('/api/admin/self-update/jobs/{id}', {'id': id}), const <String, String>{}, null, 'admin'))) as HydraSelfUpdateJob;
  }

  /// POST /api/admin/self-update/rollback (access: admin)
  Future<HydraSelfUpdateJob> postAdminSelfUpdateRollback({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/admin/self-update/rollback', const <String, String>{}, body, 'admin'))) as HydraSelfUpdateJob;
  }

  /// GET /api/admin/server-config (access: admin)
  Future<HydraServerConfig> getAdminServerConfig() async {
    return (await _transport(HydraRequest('GET', '/api/admin/server-config', const <String, String>{}, null, 'admin'))) as HydraServerConfig;
  }

  /// PUT /api/admin/server-config (access: admin)
  Future<Map<String, dynamic>> putAdminServerConfig({Map<String, dynamic>? body}) async {
    return (await _transport(HydraRequest('PUT', '/api/admin/server-config', const <String, String>{}, body, 'admin'))) as Map<String, dynamic>;
  }

  /// GET /api/admin/service-identity (access: admin)
  Future<HydraServiceIdentityStatus> getAdminServiceIdentity() async {
    return (await _transport(HydraRequest('GET', '/api/admin/service-identity', const <String, String>{}, null, 'admin'))) as HydraServiceIdentityStatus;
  }

  /// GET /api/admin/updates (access: admin)
  Future<HydraUpdateReport> getAdminUpdates({String? refresh}) async {
    return (await _transport(HydraRequest('GET', '/api/admin/updates', queryOf({'refresh': refresh}), null, 'admin'))) as HydraUpdateReport;
  }

  /// GET /api/anomaly/verdicts (access: user)
  Future<void> getAnomalyVerdicts({String? verdict, String? verify}) async {
    await _transport(HydraRequest('GET', '/api/anomaly/verdicts', queryOf({'verdict': verdict, 'verify': verify}), null, 'user'));
  }

  /// GET /api/audit (access: admin)
  Future<void> getAudit({String? afterSeq, String? format, String? limit, String? robotId, String? type, String? verify}) async {
    await _transport(HydraRequest('GET', '/api/audit', queryOf({'afterSeq': afterSeq, 'format': format, 'limit': limit, 'robotId': robotId, 'type': type, 'verify': verify}), null, 'admin'));
  }

  /// GET /api/bridges (access: user)
  Future<HydraBridgeList> getBridges() async {
    return (await _transport(HydraRequest('GET', '/api/bridges', const <String, String>{}, null, 'user'))) as HydraBridgeList;
  }

  /// POST /api/bridges/{name}/cmd/{verb} (access: user)
  Future<HydraBridgeCommandAccepted> postBridgesByNameCmdByVerb({required String name, required String verb, Map<String, dynamic>? body}) async {
    return (await _transport(HydraRequest('POST', fillPath('/api/bridges/{name}/cmd/{verb}', {'name': name, 'verb': verb}), const <String, String>{}, body, 'user'))) as HydraBridgeCommandAccepted;
  }

  /// GET /api/bridges/{name}/state (access: user)
  Future<HydraBridgeState> getBridgesByNameState({required String name}) async {
    return (await _transport(HydraRequest('GET', fillPath('/api/bridges/{name}/state', {'name': name}), const <String, String>{}, null, 'user'))) as HydraBridgeState;
  }

  /// POST /api/camera/discover-rtsp-path (access: admin)
  Future<void> postCameraDiscoverRtspPath({required Map<String, dynamic> body}) async {
    await _transport(HydraRequest('POST', '/api/camera/discover-rtsp-path', const <String, String>{}, body, 'admin'));
  }

  /// GET /api/camera/discover-usb-devices (access: user)
  Future<HydraUsbDevices> getCameraDiscoverUsbDevices() async {
    return (await _transport(HydraRequest('GET', '/api/camera/discover-usb-devices', const <String, String>{}, null, 'user'))) as HydraUsbDevices;
  }

  /// GET /api/camera/media (access: user)
  Future<HydraCameraMediaList> getCameraMedia() async {
    return (await _transport(HydraRequest('GET', '/api/camera/media', const <String, String>{}, null, 'user'))) as HydraCameraMediaList;
  }

  /// GET /api/camera/media/{cameraId}/{kind}/{filename} (access: public)
  Future<void> getCameraMediaByCameraIdByKindByFilename({required int cameraId, required String kind, required String filename}) async {
    await _transport(HydraRequest('GET', fillPath('/api/camera/media/{cameraId}/{kind}/{filename}', {'cameraId': cameraId, 'kind': kind, 'filename': filename}), const <String, String>{}, null, 'public'));
  }

  /// DELETE /api/camera/media/{cameraId}/{kind}/{filename} (access: user)
  Future<HydraCameraCapture> deleteCameraMediaByCameraIdByKindByFilename({required int cameraId, required String kind, required String filename}) async {
    return (await _transport(HydraRequest('DELETE', fillPath('/api/camera/media/{cameraId}/{kind}/{filename}', {'cameraId': cameraId, 'kind': kind, 'filename': filename}), const <String, String>{}, null, 'user'))) as HydraCameraCapture;
  }

  /// POST /api/camera/ticket (access: user)
  Future<void> postCameraTicket() async {
    await _transport(HydraRequest('POST', '/api/camera/ticket', const <String, String>{}, null, 'user'));
  }

  /// POST /api/camera/{id}/ptz (access: admin)
  Future<HydraPtzResult> postCameraByIdPtz({required int id, required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', fillPath('/api/camera/{id}/ptz', {'id': id}), const <String, String>{}, body, 'admin'))) as HydraPtzResult;
  }

  /// POST /api/camera/{id}/recording/start (access: user)
  Future<HydraCameraCapture> postCameraByIdRecordingStart({required int id}) async {
    return (await _transport(HydraRequest('POST', fillPath('/api/camera/{id}/recording/start', {'id': id}), const <String, String>{}, null, 'user'))) as HydraCameraCapture;
  }

  /// POST /api/camera/{id}/recording/stop (access: user)
  Future<HydraCameraCapture> postCameraByIdRecordingStop({required int id}) async {
    return (await _transport(HydraRequest('POST', fillPath('/api/camera/{id}/recording/stop', {'id': id}), const <String, String>{}, null, 'user'))) as HydraCameraCapture;
  }

  /// POST /api/camera/{id}/snapshot (access: user)
  Future<HydraCameraCapture> postCameraByIdSnapshot({required int id}) async {
    return (await _transport(HydraRequest('POST', fillPath('/api/camera/{id}/snapshot', {'id': id}), const <String, String>{}, null, 'user'))) as HydraCameraCapture;
  }

  /// GET /api/camera/{id}/stream (access: public)
  Future<void> getCameraByIdStream({required int id}) async {
    await _transport(HydraRequest('GET', fillPath('/api/camera/{id}/stream', {'id': id}), const <String, String>{}, null, 'public'));
  }

  /// GET /api/cameras/status (access: user)
  Future<HydraCameraProcessStatus> getCamerasStatus() async {
    return (await _transport(HydraRequest('GET', '/api/cameras/status', const <String, String>{}, null, 'user'))) as HydraCameraProcessStatus;
  }

  /// GET /api/claims (access: user)
  Future<void> getClaims() async {
    await _transport(HydraRequest('GET', '/api/claims', const <String, String>{}, null, 'user'));
  }

  /// List the clients the server has seen (access: user)
  Future<HydraConnectionClientList> getConnectionsClients({String? kind, String? user, String? active}) async {
    return (await _transport(HydraRequest('GET', '/api/connections/clients', queryOf({'kind': kind, 'user': user, 'active': active}), null, 'user'))) as HydraConnectionClientList;
  }

  /// List the history of the sign-ins of the clients (access: user)
  Future<HydraConnectionEventList> getConnectionsEvents({String? kind, String? action, String? user, String? before, String? limit}) async {
    return (await _transport(HydraRequest('GET', '/api/connections/events', queryOf({'kind': kind, 'action': action, 'user': user, 'before': before, 'limit': limit}), null, 'user'))) as HydraConnectionEventList;
  }

  /// GET /api/connector-hub/gate/audit (access: user)
  Future<HydraPassthrough> getConnectorHubGateAudit() async {
    return (await _transport(HydraRequest('GET', '/api/connector-hub/gate/audit', const <String, String>{}, null, 'user'))) as HydraPassthrough;
  }

  /// POST /api/connector-hub/gate/evaluate (access: user)
  Future<HydraPassthrough> postConnectorHubGateEvaluate() async {
    return (await _transport(HydraRequest('POST', '/api/connector-hub/gate/evaluate', const <String, String>{}, null, 'user'))) as HydraPassthrough;
  }

  /// GET /api/connector-hub/gate/settings (access: user)
  Future<Map<String, dynamic>> getConnectorHubGateSettings() async {
    return (await _transport(HydraRequest('GET', '/api/connector-hub/gate/settings', const <String, String>{}, null, 'user'))) as Map<String, dynamic>;
  }

  /// POST /api/connector-hub/gate/settings (access: admin)
  Future<Map<String, dynamic>> postConnectorHubGateSettings({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/connector-hub/gate/settings', const <String, String>{}, body, 'admin'))) as Map<String, dynamic>;
  }

  /// GET /api/dev-server/status (access: user)
  Future<void> getDevServerStatus({String? verify}) async {
    await _transport(HydraRequest('GET', '/api/dev-server/status', queryOf({'verify': verify}), null, 'user'));
  }

  /// GET /api/developer-node/status (access: user)
  Future<void> getDeveloperNodeStatus({String? verify}) async {
    await _transport(HydraRequest('GET', '/api/developer-node/status', queryOf({'verify': verify}), null, 'user'));
  }

  /// POST /api/device/login (access: public)
  Future<HydraLoginResult> postDeviceLogin({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/device/login', const <String, String>{}, body, 'public'))) as HydraLoginResult;
  }

  /// GET /api/droid-estop/settings (access: user)
  Future<Map<String, dynamic>> getDroidEstopSettings() async {
    return (await _transport(HydraRequest('GET', '/api/droid-estop/settings', const <String, String>{}, null, 'user'))) as Map<String, dynamic>;
  }

  /// POST /api/droid-estop/settings (access: admin)
  Future<Map<String, dynamic>> postDroidEstopSettings({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/droid-estop/settings', const <String, String>{}, body, 'admin'))) as Map<String, dynamic>;
  }

  /// GET /api/ecosystem/health (access: user)
  Future<HydraEcosystemHealth> getEcosystemHealth() async {
    return (await _transport(HydraRequest('GET', '/api/ecosystem/health', const <String, String>{}, null, 'user'))) as HydraEcosystemHealth;
  }

  /// GET /api/ecosystem/node-health (access: user)
  Future<HydraNodeHealth> getEcosystemNodeHealth({String? slot}) async {
    return (await _transport(HydraRequest('GET', '/api/ecosystem/node-health', queryOf({'slot': slot}), null, 'user'))) as HydraNodeHealth;
  }

  /// POST /api/ecosystem/service/{unit}/{action} (access: admin)
  Future<HydraSuccess> postEcosystemServiceByUnitByAction({required String unit, required String action}) async {
    return (await _transport(HydraRequest('POST', fillPath('/api/ecosystem/service/{unit}/{action}', {'unit': unit, 'action': action}), const <String, String>{}, null, 'admin'))) as HydraSuccess;
  }

  /// GET /api/ecosystem/status (access: public)
  Future<HydraEcosystemStatus> getEcosystemStatus() async {
    return (await _transport(HydraRequest('GET', '/api/ecosystem/status', const <String, String>{}, null, 'public'))) as HydraEcosystemStatus;
  }

  /// GET /api/faults (access: user)
  Future<void> getFaults({String? active, String? limit, String? verify}) async {
    await _transport(HydraRequest('GET', '/api/faults', queryOf({'active': active, 'limit': limit, 'verify': verify}), null, 'user'));
  }

  /// POST /api/hardware/canota/flash (access: admin)
  Future<HydraCanotaFlash> postHardwareCanotaFlash({String? tier, String? slot, String? relay, String? hardwareId, String? versionMajor, String? versionMinor, String? versionPatch, String? signature, String? downgradeFrom, String? target, String? minBootloader}) async {
    return (await _transport(HydraRequest('POST', '/api/hardware/canota/flash', queryOf({'tier': tier, 'slot': slot, 'relay': relay, 'hardware_id': hardwareId, 'version_major': versionMajor, 'version_minor': versionMinor, 'version_patch': versionPatch, 'signature': signature, 'downgrade_from': downgradeFrom, 'target': target, 'min_bootloader': minBootloader}), null, 'admin'))) as HydraCanotaFlash;
  }

  /// GET /api/hardware/canota/version (access: user)
  Future<HydraPassthrough> getHardwareCanotaVersion({String? relay, String? slot, String? tier}) async {
    return (await _transport(HydraRequest('GET', '/api/hardware/canota/version', queryOf({'relay': relay, 'slot': slot, 'tier': tier}), null, 'user'))) as HydraPassthrough;
  }

  /// POST /api/hardware/fram/erase (access: admin)
  Future<HydraPassthrough> postHardwareFramErase({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/hardware/fram/erase', const <String, String>{}, body, 'admin'))) as HydraPassthrough;
  }

  /// POST /api/hardware/fram/selftest (access: admin)
  Future<HydraPassthrough> postHardwareFramSelftest() async {
    return (await _transport(HydraRequest('POST', '/api/hardware/fram/selftest', const <String, String>{}, null, 'admin'))) as HydraPassthrough;
  }

  /// GET /api/hil-bridge/settings (access: user)
  Future<Map<String, dynamic>> getHilBridgeSettings() async {
    return (await _transport(HydraRequest('GET', '/api/hil-bridge/settings', const <String, String>{}, null, 'user'))) as Map<String, dynamic>;
  }

  /// POST /api/hil-bridge/settings (access: admin)
  Future<Map<String, dynamic>> postHilBridgeSettings({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/hil-bridge/settings', const <String, String>{}, body, 'admin'))) as Map<String, dynamic>;
  }

  /// GET /api/hydra-info (access: public)
  Future<HydraHydraInfo> getHydraInfo() async {
    return (await _transport(HydraRequest('GET', '/api/hydra-info', const <String, String>{}, null, 'public'))) as HydraHydraInfo;
  }

  /// POST /api/info/ticket (access: user)
  Future<HydraInfoTicket> postInfoTicket({Map<String, dynamic>? body}) async {
    return (await _transport(HydraRequest('POST', '/api/info/ticket', const <String, String>{}, body, 'user'))) as HydraInfoTicket;
  }

  /// POST /api/ingest/dev-server/status (access: public)
  Future<void> postIngestDevServerStatus() async {
    await _transport(HydraRequest('POST', '/api/ingest/dev-server/status', const <String, String>{}, null, 'public'));
  }

  /// POST /api/ingest/developer-node/status (access: public)
  Future<void> postIngestDeveloperNodeStatus() async {
    await _transport(HydraRequest('POST', '/api/ingest/developer-node/status', const <String, String>{}, null, 'public'));
  }

  /// POST /api/ingest/scenario-outcome (access: user)
  Future<void> postIngestScenarioOutcome() async {
    await _transport(HydraRequest('POST', '/api/ingest/scenario-outcome', const <String, String>{}, null, 'user'));
  }

  /// GET /api/ingest/scenario-outcomes (access: user)
  Future<void> getIngestScenarioOutcomes({String? fingerprintKind, String? limit, String? scenarioId, String? verify}) async {
    await _transport(HydraRequest('GET', '/api/ingest/scenario-outcomes', queryOf({'fingerprint_kind': fingerprintKind, 'limit': limit, 'scenario_id': scenarioId, 'verify': verify}), null, 'user'));
  }

  /// POST /api/integrations/test-connection (access: user)
  Future<HydraReachable> postIntegrationsTestConnection({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/integrations/test-connection', const <String, String>{}, body, 'user'))) as HydraReachable;
  }

  /// POST /api/login (access: public)
  Future<HydraLoginResult> postLogin({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/login', const <String, String>{}, body, 'public'))) as HydraLoginResult;
  }

  /// POST /api/logout (access: public)
  Future<HydraSuccess> postLogout({Map<String, dynamic>? body}) async {
    return (await _transport(HydraRequest('POST', '/api/logout', const <String, String>{}, body, 'public'))) as HydraSuccess;
  }

  /// GET /api/models (access: public)
  Future<HydraModelList> getModels() async {
    return (await _transport(HydraRequest('GET', '/api/models', const <String, String>{}, null, 'public'))) as HydraModelList;
  }

  /// POST /api/models/submit (access: admin)
  Future<HydraModelSubmitted> postModelsSubmit({Map<String, dynamic>? body}) async {
    return (await _transport(HydraRequest('POST', '/api/models/submit', const <String, String>{}, body, 'admin'))) as HydraModelSubmitted;
  }

  /// GET /api/models/{category}/{slug}/download (access: public)
  Future<void> getModelsByCategoryBySlugDownload({required String category, required String slug}) async {
    await _transport(HydraRequest('GET', fillPath('/api/models/{category}/{slug}/download', {'category': category, 'slug': slug}), const <String, String>{}, null, 'public'));
  }

  /// POST /api/operator/confirmations (access: user)
  Future<Map<String, dynamic>> postOperatorConfirmations({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/operator/confirmations', const <String, String>{}, body, 'user'))) as Map<String, dynamic>;
  }

  /// GET /api/operator/presence (access: user)
  Future<HydraOperatorPresence> getOperatorPresence() async {
    return (await _transport(HydraRequest('GET', '/api/operator/presence', const <String, String>{}, null, 'user'))) as HydraOperatorPresence;
  }

  /// POST /api/operator/presence (access: user)
  Future<HydraOperatorPresenceAck> postOperatorPresence({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/operator/presence', const <String, String>{}, body, 'user'))) as HydraOperatorPresenceAck;
  }

  /// GET /api/ops-agent/proposals (access: admin)
  Future<Map<String, dynamic>> getOpsAgentProposals() async {
    return (await _transport(HydraRequest('GET', '/api/ops-agent/proposals', const <String, String>{}, null, 'admin'))) as Map<String, dynamic>;
  }

  /// POST /api/ops-agent/proposals/decide (access: admin)
  Future<Map<String, dynamic>> postOpsAgentProposalsDecide({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/ops-agent/proposals/decide', const <String, String>{}, body, 'admin'))) as Map<String, dynamic>;
  }

  /// POST /api/push/devices (access: user)
  Future<HydraPushDeviceRegistered> postPushDevices({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/push/devices', const <String, String>{}, body, 'user'))) as HydraPushDeviceRegistered;
  }

  /// DELETE /api/push/devices/{token} (access: user)
  Future<HydraPushDeviceRemoved> deletePushDevicesByToken({required String token}) async {
    return (await _transport(HydraRequest('DELETE', fillPath('/api/push/devices/{token}', {'token': token}), const <String, String>{}, null, 'user'))) as HydraPushDeviceRemoved;
  }

  /// POST /api/push/live-activities (access: user)
  Future<HydraLiveActivityRegistered> postPushLiveActivities({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/push/live-activities', const <String, String>{}, body, 'user'))) as HydraLiveActivityRegistered;
  }

  /// DELETE /api/push/live-activities/{token} (access: user)
  Future<HydraLiveActivityRemoved> deletePushLiveActivitiesByToken({required String token}) async {
    return (await _transport(HydraRequest('DELETE', fillPath('/api/push/live-activities/{token}', {'token': token}), const <String, String>{}, null, 'user'))) as HydraLiveActivityRemoved;
  }

  /// POST /api/refresh (access: public)
  Future<HydraLoginResult> postRefresh({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/refresh', const <String, String>{}, body, 'public'))) as HydraLoginResult;
  }

  /// GET /api/robot/{id} (access: user)
  Future<Map<String, dynamic>> getRobotById({required int id}) async {
    return (await _transport(HydraRequest('GET', fillPath('/api/robot/{id}', {'id': id}), const <String, String>{}, null, 'user'))) as Map<String, dynamic>;
  }

  /// POST /api/robot/{id}/claim (access: user)
  Future<Map<String, dynamic>> postRobotByIdClaim({required int id, String? headerIfMatch, String? headerXControllerId, Map<String, dynamic>? body}) async {
    return (await _transport(HydraRequest('POST', fillPath('/api/robot/{id}/claim', {'id': id}), const <String, String>{}, body, 'user', headers: queryOf({'If-Match': headerIfMatch, 'X-Controller-Id': headerXControllerId})))) as Map<String, dynamic>;
  }

  /// POST /api/robot/{id}/command (access: user)
  Future<Map<String, dynamic>> postRobotByIdCommand({required int id, required Map<String, dynamic> body, String? headerIfMatch, String? headerXControllerId, String? headerXCorrelationId}) async {
    return (await _transport(HydraRequest('POST', fillPath('/api/robot/{id}/command', {'id': id}), const <String, String>{}, body, 'user', headers: queryOf({'If-Match': headerIfMatch, 'X-Controller-Id': headerXControllerId, 'X-Correlation-Id': headerXCorrelationId})))) as Map<String, dynamic>;
  }

  /// POST /api/robot/{id}/heartbeat (access: user)
  Future<HydraSuccess> postRobotByIdHeartbeat({required int id}) async {
    return (await _transport(HydraRequest('POST', fillPath('/api/robot/{id}/heartbeat', {'id': id}), const <String, String>{}, null, 'user'))) as HydraSuccess;
  }

  /// POST /api/robot/{id}/jog-arm (access: user)
  Future<Map<String, dynamic>> postRobotByIdJogArm({required int id, required Map<String, dynamic> body, String? headerXControllerId}) async {
    return (await _transport(HydraRequest('POST', fillPath('/api/robot/{id}/jog-arm', {'id': id}), const <String, String>{}, body, 'user', headers: queryOf({'X-Controller-Id': headerXControllerId})))) as Map<String, dynamic>;
  }

  /// POST /api/robot/{id}/release (access: user)
  Future<Map<String, dynamic>> postRobotByIdRelease({required int id, String? headerIfMatch, String? headerXControllerId, Map<String, dynamic>? body}) async {
    return (await _transport(HydraRequest('POST', fillPath('/api/robot/{id}/release', {'id': id}), const <String, String>{}, body, 'user', headers: queryOf({'If-Match': headerIfMatch, 'X-Controller-Id': headerXControllerId})))) as Map<String, dynamic>;
  }

  /// GET /api/robots/liveness (access: user)
  Future<HydraRobotLiveness> getRobotsLiveness() async {
    return (await _transport(HydraRequest('GET', '/api/robots/liveness', const <String, String>{}, null, 'user'))) as HydraRobotLiveness;
  }

  /// GET /api/ros2-bridge/settings (access: user)
  Future<Map<String, dynamic>> getRos2BridgeSettings() async {
    return (await _transport(HydraRequest('GET', '/api/ros2-bridge/settings', const <String, String>{}, null, 'user'))) as Map<String, dynamic>;
  }

  /// POST /api/ros2-bridge/settings (access: admin)
  Future<Map<String, dynamic>> postRos2BridgeSettings({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/ros2-bridge/settings', const <String, String>{}, body, 'admin'))) as Map<String, dynamic>;
  }

  /// GET /api/rul/config (access: user)
  Future<HydraRulConfig> getRulConfig() async {
    return (await _transport(HydraRequest('GET', '/api/rul/config', const <String, String>{}, null, 'user'))) as HydraRulConfig;
  }

  /// GET /api/safety-limits (access: user)
  Future<void> getSafetyLimits({String? robotId}) async {
    await _transport(HydraRequest('GET', '/api/safety-limits', queryOf({'robotId': robotId}), null, 'user'));
  }

  /// GET /api/semantic-planner/settings (access: user)
  Future<Map<String, dynamic>> getSemanticPlannerSettings() async {
    return (await _transport(HydraRequest('GET', '/api/semantic-planner/settings', const <String, String>{}, null, 'user'))) as Map<String, dynamic>;
  }

  /// POST /api/semantic-planner/settings (access: admin)
  Future<Map<String, dynamic>> postSemanticPlannerSettings({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/semantic-planner/settings', const <String, String>{}, body, 'admin'))) as Map<String, dynamic>;
  }

  /// GET /api/settings (access: user)
  Future<HydraSettings> getSettings() async {
    return (await _transport(HydraRequest('GET', '/api/settings', const <String, String>{}, null, 'user'))) as HydraSettings;
  }

  /// PUT /api/settings (access: admin)
  Future<Map<String, dynamic>> putSettings({required String headerIfMatch, required HydraSettings body}) async {
    return (await _transport(HydraRequest('PUT', '/api/settings', const <String, String>{}, body, 'admin', headers: queryOf({'If-Match': headerIfMatch})))) as Map<String, dynamic>;
  }

  /// POST /api/settings (access: admin)
  Future<Map<String, dynamic>> postSettings({required HydraSettings body, String? headerIfMatch}) async {
    return (await _transport(HydraRequest('POST', '/api/settings', const <String, String>{}, body, 'admin', headers: queryOf({'If-Match': headerIfMatch})))) as Map<String, dynamic>;
  }

  /// POST /api/stop-all (access: user)
  Future<HydraStopAllResult> postStopAll() async {
    return (await _transport(HydraRequest('POST', '/api/stop-all', const <String, String>{}, null, 'user'))) as HydraStopAllResult;
  }

  /// POST /api/stop-all/release (access: admin)
  Future<HydraGlobalStopReleased> postStopAllRelease() async {
    return (await _transport(HydraRequest('POST', '/api/stop-all/release', const <String, String>{}, null, 'admin'))) as HydraGlobalStopReleased;
  }

  /// POST /api/system/bluetooth/pair (access: admin)
  Future<void> postSystemBluetoothPair({required Map<String, dynamic> body}) async {
    await _transport(HydraRequest('POST', '/api/system/bluetooth/pair', const <String, String>{}, body, 'admin'));
  }

  /// POST /api/system/bluetooth/power (access: admin)
  Future<HydraSuccess> postSystemBluetoothPower({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/system/bluetooth/power', const <String, String>{}, body, 'admin'))) as HydraSuccess;
  }

  /// POST /api/system/bluetooth/remove (access: admin)
  Future<HydraSuccess> postSystemBluetoothRemove({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/system/bluetooth/remove', const <String, String>{}, body, 'admin'))) as HydraSuccess;
  }

  /// POST /api/system/bluetooth/scan (access: admin)
  Future<HydraBluetoothScan> postSystemBluetoothScan() async {
    return (await _transport(HydraRequest('POST', '/api/system/bluetooth/scan', const <String, String>{}, null, 'admin'))) as HydraBluetoothScan;
  }

  /// GET /api/system/bluetooth/status (access: admin)
  Future<void> getSystemBluetoothStatus() async {
    await _transport(HydraRequest('GET', '/api/system/bluetooth/status', const <String, String>{}, null, 'admin'));
  }

  /// GET /api/system/metrics (access: public)
  Future<HydraSystemMetrics> getSystemMetrics() async {
    return (await _transport(HydraRequest('GET', '/api/system/metrics', const <String, String>{}, null, 'public'))) as HydraSystemMetrics;
  }

  /// POST /api/system/reboot (access: public)
  Future<HydraSuccess> postSystemReboot() async {
    return (await _transport(HydraRequest('POST', '/api/system/reboot', const <String, String>{}, null, 'public'))) as HydraSuccess;
  }

  /// POST /api/system/shutdown (access: public)
  Future<HydraSuccess> postSystemShutdown() async {
    return (await _transport(HydraRequest('POST', '/api/system/shutdown', const <String, String>{}, null, 'public'))) as HydraSuccess;
  }

  /// GET /api/system/supervisor (access: public)
  Future<HydraSupervisorSnapshot> getSystemSupervisor() async {
    return (await _transport(HydraRequest('GET', '/api/system/supervisor', const <String, String>{}, null, 'public'))) as HydraSupervisorSnapshot;
  }

  /// GET /api/telemetry/aggregate (access: user)
  Future<List<dynamic>> getTelemetryAggregate({String? sourceId, String? kind, String? field, String? bucketMs, String? start, String? end, String? before, String? agg}) async {
    return (await _transport(HydraRequest('GET', '/api/telemetry/aggregate', queryOf({'sourceId': sourceId, 'kind': kind, 'field': field, 'bucketMs': bucketMs, 'start': start, 'end': end, 'before': before, 'agg': agg}), null, 'user'))) as List<dynamic>;
  }

  /// GET /api/telemetry/downsample-plan (access: admin)
  Future<Map<String, dynamic>> getTelemetryDownsamplePlan() async {
    return (await _transport(HydraRequest('GET', '/api/telemetry/downsample-plan', const <String, String>{}, null, 'admin'))) as Map<String, dynamic>;
  }

  /// PUT /api/telemetry/downsample-plan (access: admin)
  Future<Map<String, dynamic>> putTelemetryDownsamplePlan({required Map<String, dynamic> body, String? preview}) async {
    return (await _transport(HydraRequest('PUT', '/api/telemetry/downsample-plan', queryOf({'preview': preview}), body, 'admin'))) as Map<String, dynamic>;
  }

  /// GET /api/telemetry/query (access: user)
  Future<List<dynamic>> getTelemetryQuery({String? sourceId, String? kind, String? field, String? start, String? end, String? before, String? limit, String? cursor}) async {
    return (await _transport(HydraRequest('GET', '/api/telemetry/query', queryOf({'sourceId': sourceId, 'kind': kind, 'field': field, 'start': start, 'end': end, 'before': before, 'limit': limit, 'cursor': cursor}), null, 'user'))) as List<dynamic>;
  }

  /// GET /api/tool-arms (access: user)
  Future<HydraToolArmsReport> getToolArms() async {
    return (await _transport(HydraRequest('GET', '/api/tool-arms', const <String, String>{}, null, 'user'))) as HydraToolArmsReport;
  }

  /// POST /api/tool-arms/reset (access: admin)
  Future<HydraToolArmResetResult> postToolArmsReset({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/tool-arms/reset', const <String, String>{}, body, 'admin'))) as HydraToolArmResetResult;
  }

  /// POST /api/totp/begin (access: user)
  Future<HydraTotpEnrolment> postTotpBegin({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/totp/begin', const <String, String>{}, body, 'user'))) as HydraTotpEnrolment;
  }

  /// POST /api/totp/confirm (access: user)
  Future<HydraTotpConfirmed> postTotpConfirm({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/totp/confirm', const <String, String>{}, body, 'user'))) as HydraTotpConfirmed;
  }

  /// POST /api/totp/disable (access: user)
  Future<HydraSuccess> postTotpDisable({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/totp/disable', const <String, String>{}, body, 'user'))) as HydraSuccess;
  }

  /// GET /api/totp/status (access: user)
  Future<HydraTotpStatus> getTotpStatus() async {
    return (await _transport(HydraRequest('GET', '/api/totp/status', const <String, String>{}, null, 'user'))) as HydraTotpStatus;
  }

  /// POST /api/trajectory/proposals/verify (access: user)
  Future<void> postTrajectoryProposalsVerify() async {
    await _transport(HydraRequest('POST', '/api/trajectory/proposals/verify', const <String, String>{}, null, 'user'));
  }

  /// POST /api/upload-work (access: user)
  Future<HydraSuccess> postUploadWork({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/upload-work', const <String, String>{}, body, 'user'))) as HydraSuccess;
  }

  /// GET /api/users (access: admin)
  Future<HydraUserList> getUsers() async {
    return (await _transport(HydraRequest('GET', '/api/users', const <String, String>{}, null, 'admin'))) as HydraUserList;
  }

  /// POST /api/users (access: admin)
  Future<HydraSuccess> postUsers({required Map<String, dynamic> body}) async {
    return (await _transport(HydraRequest('POST', '/api/users', const <String, String>{}, body, 'admin'))) as HydraSuccess;
  }

  /// PUT /api/users/{username} (access: admin)
  Future<HydraSuccess> putUsersByUsername({required String username, Map<String, dynamic>? body}) async {
    return (await _transport(HydraRequest('PUT', fillPath('/api/users/{username}', {'username': username}), const <String, String>{}, body, 'admin'))) as HydraSuccess;
  }

  /// DELETE /api/users/{username} (access: admin)
  Future<HydraSuccess> deleteUsersByUsername({required String username}) async {
    return (await _transport(HydraRequest('DELETE', fillPath('/api/users/{username}', {'username': username}), const <String, String>{}, null, 'admin'))) as HydraSuccess;
  }

  /// DELETE /api/users/{username}/totp (access: admin)
  Future<HydraSuccess> deleteUsersByUsernameTotp({required String username}) async {
    return (await _transport(HydraRequest('DELETE', fillPath('/api/users/{username}/totp', {'username': username}), const <String, String>{}, null, 'admin'))) as HydraSuccess;
  }

  /// GET /api/voice/chain (access: admin)
  Future<void> getVoiceChain({String? limit, String? verify}) async {
    await _transport(HydraRequest('GET', '/api/voice/chain', queryOf({'limit': limit, 'verify': verify}), null, 'admin'));
  }

  /// POST /api/voice/confirm (access: user)
  Future<void> postVoiceConfirm({Map<String, dynamic>? body}) async {
    await _transport(HydraRequest('POST', '/api/voice/confirm', const <String, String>{}, body, 'user'));
  }

  /// POST /api/voice/turn (access: user)
  Future<void> postVoiceTurn({Map<String, dynamic>? body}) async {
    await _transport(HydraRequest('POST', '/api/voice/turn', const <String, String>{}, body, 'user'));
  }

  /// GET /api/watch/system-status (access: user)
  Future<void> getWatchSystemStatus() async {
    await _transport(HydraRequest('GET', '/api/watch/system-status', const <String, String>{}, null, 'user'));
  }

  /// GET /health (access: public)
  Future<HydraHealthReport> getHealth() async {
    return (await _transport(HydraRequest('GET', '/health', const <String, String>{}, null, 'public'))) as HydraHealthReport;
  }

  /// GET /metrics (access: public)
  Future<void> getMetrics() async {
    await _transport(HydraRequest('GET', '/metrics', const <String, String>{}, null, 'public'));
  }

}

const List<String> hydraClientOperations = [
  'getWellKnownJwksJson',
  'getAdapters',
  'getAdaptersByAdapterId',
  'getAdminClients',
  'getAdminDeviceTokens',
  'postAdminDeviceTokens',
  'deleteAdminDeviceTokensById',
  'getAdminFleetUpdate',
  'postAdminFleetUpdateApply',
  'postAdminFleetUpdatePlan',
  'postAdminFleetUpdateResume',
  'getAdminJwtKeys',
  'postAdminJwtKeysRotate',
  'getAdminLogs',
  'postAdminMaintenanceInstall',
  'postAdminMaintenancePrune',
  'postAdminMaintenanceRollback',
  'getAdminMaintenanceStatus',
  'getAdminPush',
  'postAdminRestart',
  'getAdminRobotIds',
  'putAdminSafetyLimits',
  'getAdminSelfUpdate',
  'postAdminSelfUpdateApply',
  'getAdminSelfUpdateJobsById',
  'postAdminSelfUpdateRollback',
  'getAdminServerConfig',
  'putAdminServerConfig',
  'getAdminServiceIdentity',
  'getAdminUpdates',
  'getAnomalyVerdicts',
  'getAudit',
  'getBridges',
  'postBridgesByNameCmdByVerb',
  'getBridgesByNameState',
  'postCameraDiscoverRtspPath',
  'getCameraDiscoverUsbDevices',
  'getCameraMedia',
  'getCameraMediaByCameraIdByKindByFilename',
  'deleteCameraMediaByCameraIdByKindByFilename',
  'postCameraTicket',
  'postCameraByIdPtz',
  'postCameraByIdRecordingStart',
  'postCameraByIdRecordingStop',
  'postCameraByIdSnapshot',
  'getCameraByIdStream',
  'getCamerasStatus',
  'getClaims',
  'getConnectionsClients',
  'getConnectionsEvents',
  'getConnectorHubGateAudit',
  'postConnectorHubGateEvaluate',
  'getConnectorHubGateSettings',
  'postConnectorHubGateSettings',
  'getDevServerStatus',
  'getDeveloperNodeStatus',
  'postDeviceLogin',
  'getDroidEstopSettings',
  'postDroidEstopSettings',
  'getEcosystemHealth',
  'getEcosystemNodeHealth',
  'postEcosystemServiceByUnitByAction',
  'getEcosystemStatus',
  'getFaults',
  'postHardwareCanotaFlash',
  'getHardwareCanotaVersion',
  'postHardwareFramErase',
  'postHardwareFramSelftest',
  'getHilBridgeSettings',
  'postHilBridgeSettings',
  'getHydraInfo',
  'postInfoTicket',
  'postIngestDevServerStatus',
  'postIngestDeveloperNodeStatus',
  'postIngestScenarioOutcome',
  'getIngestScenarioOutcomes',
  'postIntegrationsTestConnection',
  'postLogin',
  'postLogout',
  'getModels',
  'postModelsSubmit',
  'getModelsByCategoryBySlugDownload',
  'postOperatorConfirmations',
  'getOperatorPresence',
  'postOperatorPresence',
  'getOpsAgentProposals',
  'postOpsAgentProposalsDecide',
  'postPushDevices',
  'deletePushDevicesByToken',
  'postPushLiveActivities',
  'deletePushLiveActivitiesByToken',
  'postRefresh',
  'getRobotById',
  'postRobotByIdClaim',
  'postRobotByIdCommand',
  'postRobotByIdHeartbeat',
  'postRobotByIdJogArm',
  'postRobotByIdRelease',
  'getRobotsLiveness',
  'getRos2BridgeSettings',
  'postRos2BridgeSettings',
  'getRulConfig',
  'getSafetyLimits',
  'getSemanticPlannerSettings',
  'postSemanticPlannerSettings',
  'getSettings',
  'putSettings',
  'postSettings',
  'postStopAll',
  'postStopAllRelease',
  'postSystemBluetoothPair',
  'postSystemBluetoothPower',
  'postSystemBluetoothRemove',
  'postSystemBluetoothScan',
  'getSystemBluetoothStatus',
  'getSystemMetrics',
  'postSystemReboot',
  'postSystemShutdown',
  'getSystemSupervisor',
  'getTelemetryAggregate',
  'getTelemetryDownsamplePlan',
  'putTelemetryDownsamplePlan',
  'getTelemetryQuery',
  'getToolArms',
  'postToolArmsReset',
  'postTotpBegin',
  'postTotpConfirm',
  'postTotpDisable',
  'getTotpStatus',
  'postTrajectoryProposalsVerify',
  'postUploadWork',
  'getUsers',
  'postUsers',
  'putUsersByUsername',
  'deleteUsersByUsername',
  'deleteUsersByUsernameTotp',
  'getVoiceChain',
  'postVoiceConfirm',
  'postVoiceTurn',
  'getWatchSystemStatus',
  'getHealth',
  'getMetrics',
];
