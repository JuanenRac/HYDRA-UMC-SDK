// Generated from the server contract by tools/generate_clients.py. Do not edit.

@file:Suppress("UNCHECKED_CAST", "unused")

package hydra.umc.client

// The transport hands back the decoded JSON model: Map, List, String, Long, Double, Boolean or null.

/** Fields: success, devices */
typealias HydraBluetoothScan = Map<String, Any?>

/** Fields: accepted, result */
typealias HydraBridgeCommandAccepted = Map<String, Any?>

/** Fields: connected, bridges */
typealias HydraBridgeList = Map<String, Any?>

/** Fields: name, available, state, health, updatedAt */
typealias HydraBridgeState = Map<String, Any?>

/** Fields: success, cameraId, filename, capturedAt?, sizeBytes?, startedAt?, stoppedAt? */
typealias HydraCameraCapture = Map<String, Any?>

/** Fields: items */
typealias HydraCameraMediaList = Map<String, Any?>

typealias HydraCameraProcessStatus = Map<String, Map<String, Any?>>

/** Fields: success, finalPhase */
typealias HydraCanotaFlash = Map<String, Any?>

/** Fields: clients */
typealias HydraClients = Map<String, Any?>

/** Fields: schema_version, id, kind, user?, app_version?, origin?, two_factor?, first_seen_utc, last_seen_utc, last_failure_utc?, active_sessions, logins_ok, logins_failed, ip?, agent? */
typealias HydraConnectionClient = Map<String, Any?>

/** Fields: clients */
typealias HydraConnectionClientList = Map<String, Any?>

/** Fields: schema_version, id, at_utc, action, client_kind, client_id, user?, origin?, two_factor?, app_version?, ip?, agent? */
typealias HydraConnectionEvent = Map<String, Any?>

/** Fields: events */
typealias HydraConnectionEventList = Map<String, Any?>

/** Fields: id, name, username, createdAt, expiresAt, revokedAt, lastUsedAt, state, token */
typealias HydraDeviceTokenIssued = Map<String, Any?>

/** Fields: items */
typealias HydraDeviceTokenList = Map<String, Any?>

/** Fields: revoked, sessionsEnded */
typealias HydraDeviceTokenRevoked = Map<String, Any?>

/** Fields: id, name, username, createdAt, expiresAt, revokedAt, lastUsedAt, state */
typealias HydraDeviceTokenView = Map<String, Any?>

/** Fields: schema_version, generated_at_utc, available, summary, services, certificate, warnings */
typealias HydraEcosystemHealth = Map<String, Any?>

/** Fields: available, scannedAt, projects */
typealias HydraEcosystemStatus = Map<String, Any?>

/** Fields: error */
typealias HydraError = Map<String, Any?>

/** Fields: schema, id, mode, state, startedAt, updatedAt, error, stoppedAt, requireSignedTags, disk, services */
typealias HydraFleetUpdateReport = Map<String, Any?>

/** Fields: name, kind, repo, installed, latest, action, reason, state, step, substep?, substeps?, detail, error, order, elapsedS?, freeMb?, needMb?, unitRestored?, log */
typealias HydraFleetUpdateRow = Map<String, Any?>

/** Fields: applyEnabled, busy, report */
typealias HydraFleetUpdateStatus = Map<String, Any?>

/** Fields: success, announced */
typealias HydraGlobalStopReleased = Map<String, Any?>

/** Fields: schema_version, state, timestamp_utc, checks, service? */
typealias HydraHealthReport = Map<String, Any?>

/** Fields: schema_version, product, remoteApiVersion, appVersion, hostname, controllerCount, robotCount, uptimeSeconds, addresses? */
typealias HydraHydraInfo = Map<String, Any?>

/** Fields: ticket, expiresInSeconds */
typealias HydraInfoTicket = Map<String, Any?>

/** Fields: keys */
typealias HydraJwksDocument = Map<String, Any?>

/** Fields: success, kid, algorithm, keys, jwksPath */
typealias HydraJwtKeyRotated = Map<String, Any?>

/** Fields: algorithm, keys, jwksPath */
typealias HydraJwtKeys = Map<String, Any?>

/** Fields: registered */
typealias HydraLiveActivityRegistered = Map<String, Any?>

/** Fields: removed */
typealias HydraLiveActivityRemoved = Map<String, Any?>

/** Fields: lines */
typealias HydraLogLines = Map<String, Any?>

/** Fields: success, token, refreshToken, role */
typealias HydraLoginResult = Map<String, Any?>

/** Fields: ok, action, exitCode, timedOut, result, message */
typealias HydraMaintenanceOutcome = Map<String, Any?>

/** Fields: models */
typealias HydraModelList = Map<String, Any?>

/** Fields: success, slug */
typealias HydraModelSubmitted = Map<String, Any?>

/** Fields: online, slot, heard, ageMs?, sequence?, flags?, flagNames?, txErrors?, rxErrors?, stalls?, uptimeS?, source */
typealias HydraNodeHealth = Map<String, Any?>

/** Fields: state, lastSequence, secondsSinceBeat, action, timeoutSeconds, degradedRobots */
typealias HydraOperatorPresence = Map<String, Any?>

/** Fields: accepted, duplicate, stale, state, sequence, action, timeoutSeconds */
typealias HydraOperatorPresenceAck = Map<String, Any?>

typealias HydraPassthrough = Map<String, Any?>

/** Fields: ok */
typealias HydraPtzResult = Map<String, Any?>

/** Fields: registered */
typealias HydraPushDeviceRegistered = Map<String, Any?>

/** Fields: removed */
typealias HydraPushDeviceRemoved = Map<String, Any?>

/** Fields: enabled, configured, problem, devices, sandbox, events, liveActivity? */
typealias HydraPushStatus = Map<String, Any?>

/** Fields: reachable */
typealias HydraReachable = Map<String, Any?>

/** Fields: success, reservation?, reservationHistory */
typealias HydraReservation = Map<String, Any?>

/** Fields: schema_version, stale_after_s, robots */
typealias HydraRobotLiveness = Map<String, Any?>

/** Fields: enabled, maxPoints, timeoutMs */
typealias HydraRulConfig = Map<String, Any?>

/** Fields: id, repo, installed, previous, latest, state, signedPackage */
typealias HydraSelfUpdateItem = Map<String, Any?>

/** Fields: id, action, component, state, fromVersion, targetVersion, startedAt, updatedAt, error, detail, packageName?, log, by */
typealias HydraSelfUpdateJob = Map<String, Any?>

/** Fields: checkedAt, owner, rateLimited, items, applyEnabled, job */
typealias HydraSelfUpdateStatus = Map<String, Any?>

/** Fields: port, pendingPort */
typealias HydraServerConfig = Map<String, Any?>

/** Fields: success, appliesOnRestart */
typealias HydraServerConfigSaved = Map<String, Any?>

/** Fields: enabled, source, locked, key, state, services, order */
typealias HydraServiceIdentityStatus = Map<String, Any?>

/** Fields: controllers? */
typealias HydraSettings = Map<String, Any?>

/** Fields: success, stoppedCount, failedCount, persisted, announced?, robots */
typealias HydraStopAllResult = Map<String, Any?>

/** Fields: success */
typealias HydraSuccess = Map<String, Any?>

typealias HydraSupervisorSnapshot = Map<String, Any?>

/** Fields: cpu_load, memory_usage, temp, temp_is_real, rp1_temp, uptime, network */
typealias HydraSystemMetrics = Map<String, Any?>

/** Fields: success, robot, toolId */
typealias HydraToolArmResetResult = Map<String, Any?>

/** Fields: schema_version, ttlSeconds, arms, armedCount, staleCount */
typealias HydraToolArmsReport = Map<String, Any?>

/** Fields: success, recoveryCodes */
typealias HydraTotpConfirmed = Map<String, Any?>

/** Fields: success, secret, uri */
typealias HydraTotpEnrolment = Map<String, Any?>

/** Fields: enabled, recoveryLeft */
typealias HydraTotpStatus = Map<String, Any?>

/** Fields: name, family, installed, latest, state */
typealias HydraUpdateItem = Map<String, Any?>

/** Fields: checkedAt, owner, rateLimited, items */
typealias HydraUpdateReport = Map<String, Any?>

/** Fields: devices */
typealias HydraUsbDevices = Map<String, Any?>

/** Fields: users */
typealias HydraUserList = Map<String, Any?>

/** Fields: type, requestId, text, level, speak, requiresConfirmation, visualState?, intent?, interpretation?, messageCode?, messageParams?, textLanguage?, confirmationToken?, confirmationValiditySeconds? */
typealias HydraVoiceReply = Map<String, Any?>

/** Fields: type, headline, detail, level, speak */
typealias HydraWatchStatus = Map<String, Any?>

class HydraRequest(val method: String, val path: String, val query: Map<String, String>, val body: Any?, val access: String, val headers: Map<String, String> = emptyMap())

/** Carries one request to the server and returns the decoded JSON of the answer (null when there is none). */
fun interface HydraTransport {
    suspend fun send(request: HydraRequest): Any?
}

fun fillPath(template: String, values: Map<String, Any>): String =
    Regex("\\{([^}]+)\\}").replace(template) { match ->
        val value = values[match.groupValues[1]]?.toString()
        require(!value.isNullOrEmpty()) { "missing path parameter ${match.groupValues[1]}" }
        java.net.URLEncoder.encode(value, "UTF-8").replace("+", "%20")
    }

fun queryOf(values: Map<String, Any?>): Map<String, String> =
    values.filterValues { it != null }.mapValues { it.value.toString() }

class HydraServerClient(private val transport: HydraTransport) {
    /** GET /.well-known/jwks.json (access: public) */
    suspend fun getWellKnownJwksJson(): HydraJwksDocument {
        return transport.send(HydraRequest("GET", "/.well-known/jwks.json", emptyMap(), null, "public")) as HydraJwksDocument
    }

    /** GET /api/adapters (access: user) */
    suspend fun getAdapters(): HydraPassthrough {
        return transport.send(HydraRequest("GET", "/api/adapters", emptyMap(), null, "user")) as HydraPassthrough
    }

    /** GET /api/adapters/{adapterId} (access: user) */
    suspend fun getAdaptersByAdapterId(adapterId: String): Unit {
        transport.send(HydraRequest("GET", fillPath("/api/adapters/{adapterId}", mapOf("adapterId" to adapterId)), emptyMap(), null, "user"))
        return Unit
    }

    /** GET /api/admin/clients (access: admin) */
    suspend fun getAdminClients(): HydraClients {
        return transport.send(HydraRequest("GET", "/api/admin/clients", emptyMap(), null, "admin")) as HydraClients
    }

    /** GET /api/admin/device-tokens (access: admin) */
    suspend fun getAdminDeviceTokens(): HydraDeviceTokenList {
        return transport.send(HydraRequest("GET", "/api/admin/device-tokens", emptyMap(), null, "admin")) as HydraDeviceTokenList
    }

    /** POST /api/admin/device-tokens (access: admin) */
    suspend fun postAdminDeviceTokens(body: Map<String, Any?>): HydraDeviceTokenIssued {
        return transport.send(HydraRequest("POST", "/api/admin/device-tokens", emptyMap(), body, "admin")) as HydraDeviceTokenIssued
    }

    /** DELETE /api/admin/device-tokens/{id} (access: admin) */
    suspend fun deleteAdminDeviceTokensById(id: String): HydraDeviceTokenRevoked {
        return transport.send(HydraRequest("DELETE", fillPath("/api/admin/device-tokens/{id}", mapOf("id" to id)), emptyMap(), null, "admin")) as HydraDeviceTokenRevoked
    }

    /** GET /api/admin/fleet-update (access: admin) */
    suspend fun getAdminFleetUpdate(): HydraFleetUpdateStatus {
        return transport.send(HydraRequest("GET", "/api/admin/fleet-update", emptyMap(), null, "admin")) as HydraFleetUpdateStatus
    }

    /** POST /api/admin/fleet-update/apply (access: admin) */
    suspend fun postAdminFleetUpdateApply(body: Map<String, Any?>): HydraFleetUpdateStatus {
        return transport.send(HydraRequest("POST", "/api/admin/fleet-update/apply", emptyMap(), body, "admin")) as HydraFleetUpdateStatus
    }

    /** POST /api/admin/fleet-update/plan (access: admin) */
    suspend fun postAdminFleetUpdatePlan(): HydraFleetUpdateStatus {
        return transport.send(HydraRequest("POST", "/api/admin/fleet-update/plan", emptyMap(), null, "admin")) as HydraFleetUpdateStatus
    }

    /** POST /api/admin/fleet-update/resume (access: admin) */
    suspend fun postAdminFleetUpdateResume(body: Map<String, Any?>): HydraFleetUpdateStatus {
        return transport.send(HydraRequest("POST", "/api/admin/fleet-update/resume", emptyMap(), body, "admin")) as HydraFleetUpdateStatus
    }

    /** GET /api/admin/jwt-keys (access: admin) */
    suspend fun getAdminJwtKeys(): HydraJwtKeys {
        return transport.send(HydraRequest("GET", "/api/admin/jwt-keys", emptyMap(), null, "admin")) as HydraJwtKeys
    }

    /** POST /api/admin/jwt-keys/rotate (access: admin) */
    suspend fun postAdminJwtKeysRotate(): HydraJwtKeyRotated {
        return transport.send(HydraRequest("POST", "/api/admin/jwt-keys/rotate", emptyMap(), null, "admin")) as HydraJwtKeyRotated
    }

    /** GET /api/admin/logs (access: admin) */
    suspend fun getAdminLogs(lines: String? = null): HydraLogLines {
        return transport.send(HydraRequest("GET", "/api/admin/logs", queryOf(mapOf("lines" to lines)), null, "admin")) as HydraLogLines
    }

    /** POST /api/admin/maintenance/install (access: admin) */
    suspend fun postAdminMaintenanceInstall(body: Map<String, Any?>): HydraMaintenanceOutcome {
        return transport.send(HydraRequest("POST", "/api/admin/maintenance/install", emptyMap(), body, "admin")) as HydraMaintenanceOutcome
    }

    /** POST /api/admin/maintenance/prune (access: admin) */
    suspend fun postAdminMaintenancePrune(body: Map<String, Any?>): HydraMaintenanceOutcome {
        return transport.send(HydraRequest("POST", "/api/admin/maintenance/prune", emptyMap(), body, "admin")) as HydraMaintenanceOutcome
    }

    /** POST /api/admin/maintenance/rollback (access: admin) */
    suspend fun postAdminMaintenanceRollback(body: Map<String, Any?>): HydraMaintenanceOutcome {
        return transport.send(HydraRequest("POST", "/api/admin/maintenance/rollback", emptyMap(), body, "admin")) as HydraMaintenanceOutcome
    }

    /** GET /api/admin/maintenance/status (access: admin) */
    suspend fun getAdminMaintenanceStatus(component: String? = null): HydraMaintenanceOutcome {
        return transport.send(HydraRequest("GET", "/api/admin/maintenance/status", queryOf(mapOf("component" to component)), null, "admin")) as HydraMaintenanceOutcome
    }

    /** GET /api/admin/push (access: admin) */
    suspend fun getAdminPush(): HydraPushStatus {
        return transport.send(HydraRequest("GET", "/api/admin/push", emptyMap(), null, "admin")) as HydraPushStatus
    }

    /** POST /api/admin/restart (access: admin) */
    suspend fun postAdminRestart(): HydraSuccess {
        return transport.send(HydraRequest("POST", "/api/admin/restart", emptyMap(), null, "admin")) as HydraSuccess
    }

    /** GET /api/admin/robot-ids (access: admin) */
    suspend fun getAdminRobotIds(): Map<String, Any?> {
        return transport.send(HydraRequest("GET", "/api/admin/robot-ids", emptyMap(), null, "admin")) as Map<String, Any?>
    }

    /** PUT /api/admin/safety-limits (access: admin) */
    suspend fun putAdminSafetyLimits(body: Map<String, Any?>): Map<String, Any?> {
        return transport.send(HydraRequest("PUT", "/api/admin/safety-limits", emptyMap(), body, "admin")) as Map<String, Any?>
    }

    /** GET /api/admin/self-update (access: admin) */
    suspend fun getAdminSelfUpdate(refresh: String? = null): HydraSelfUpdateStatus {
        return transport.send(HydraRequest("GET", "/api/admin/self-update", queryOf(mapOf("refresh" to refresh)), null, "admin")) as HydraSelfUpdateStatus
    }

    /** POST /api/admin/self-update/apply (access: admin) */
    suspend fun postAdminSelfUpdateApply(body: Map<String, Any?>): HydraSelfUpdateJob {
        return transport.send(HydraRequest("POST", "/api/admin/self-update/apply", emptyMap(), body, "admin")) as HydraSelfUpdateJob
    }

    /** GET /api/admin/self-update/jobs/{id} (access: admin) */
    suspend fun getAdminSelfUpdateJobsById(id: String): HydraSelfUpdateJob {
        return transport.send(HydraRequest("GET", fillPath("/api/admin/self-update/jobs/{id}", mapOf("id" to id)), emptyMap(), null, "admin")) as HydraSelfUpdateJob
    }

    /** POST /api/admin/self-update/rollback (access: admin) */
    suspend fun postAdminSelfUpdateRollback(body: Map<String, Any?>): HydraSelfUpdateJob {
        return transport.send(HydraRequest("POST", "/api/admin/self-update/rollback", emptyMap(), body, "admin")) as HydraSelfUpdateJob
    }

    /** GET /api/admin/server-config (access: admin) */
    suspend fun getAdminServerConfig(): HydraServerConfig {
        return transport.send(HydraRequest("GET", "/api/admin/server-config", emptyMap(), null, "admin")) as HydraServerConfig
    }

    /** PUT /api/admin/server-config (access: admin) */
    suspend fun putAdminServerConfig(body: Map<String, Any?>? = null): Map<String, Any?> {
        return transport.send(HydraRequest("PUT", "/api/admin/server-config", emptyMap(), body, "admin")) as Map<String, Any?>
    }

    /** GET /api/admin/service-identity (access: admin) */
    suspend fun getAdminServiceIdentity(): HydraServiceIdentityStatus {
        return transport.send(HydraRequest("GET", "/api/admin/service-identity", emptyMap(), null, "admin")) as HydraServiceIdentityStatus
    }

    /** GET /api/admin/updates (access: admin) */
    suspend fun getAdminUpdates(refresh: String? = null): HydraUpdateReport {
        return transport.send(HydraRequest("GET", "/api/admin/updates", queryOf(mapOf("refresh" to refresh)), null, "admin")) as HydraUpdateReport
    }

    /** GET /api/anomaly/verdicts (access: user) */
    suspend fun getAnomalyVerdicts(verdict: String? = null, verify: String? = null): Unit {
        transport.send(HydraRequest("GET", "/api/anomaly/verdicts", queryOf(mapOf("verdict" to verdict, "verify" to verify)), null, "user"))
        return Unit
    }

    /** GET /api/audit (access: admin) */
    suspend fun getAudit(afterSeq: String? = null, format: String? = null, limit: String? = null, robotId: String? = null, type: String? = null, verify: String? = null): Unit {
        transport.send(HydraRequest("GET", "/api/audit", queryOf(mapOf("afterSeq" to afterSeq, "format" to format, "limit" to limit, "robotId" to robotId, "type" to type, "verify" to verify)), null, "admin"))
        return Unit
    }

    /** GET /api/bridges (access: user) */
    suspend fun getBridges(): HydraBridgeList {
        return transport.send(HydraRequest("GET", "/api/bridges", emptyMap(), null, "user")) as HydraBridgeList
    }

    /** POST /api/bridges/{name}/cmd/{verb} (access: user) */
    suspend fun postBridgesByNameCmdByVerb(name: String, verb: String, body: Map<String, Any?>? = null): HydraBridgeCommandAccepted {
        return transport.send(HydraRequest("POST", fillPath("/api/bridges/{name}/cmd/{verb}", mapOf("name" to name, "verb" to verb)), emptyMap(), body, "user")) as HydraBridgeCommandAccepted
    }

    /** GET /api/bridges/{name}/state (access: user) */
    suspend fun getBridgesByNameState(name: String): HydraBridgeState {
        return transport.send(HydraRequest("GET", fillPath("/api/bridges/{name}/state", mapOf("name" to name)), emptyMap(), null, "user")) as HydraBridgeState
    }

    /** POST /api/camera/discover-rtsp-path (access: admin) */
    suspend fun postCameraDiscoverRtspPath(body: Map<String, Any?>): Unit {
        transport.send(HydraRequest("POST", "/api/camera/discover-rtsp-path", emptyMap(), body, "admin"))
        return Unit
    }

    /** GET /api/camera/discover-usb-devices (access: user) */
    suspend fun getCameraDiscoverUsbDevices(): HydraUsbDevices {
        return transport.send(HydraRequest("GET", "/api/camera/discover-usb-devices", emptyMap(), null, "user")) as HydraUsbDevices
    }

    /** GET /api/camera/media (access: user) */
    suspend fun getCameraMedia(): HydraCameraMediaList {
        return transport.send(HydraRequest("GET", "/api/camera/media", emptyMap(), null, "user")) as HydraCameraMediaList
    }

    /** GET /api/camera/media/{cameraId}/{kind}/{filename} (access: public) */
    suspend fun getCameraMediaByCameraIdByKindByFilename(cameraId: Long, kind: String, filename: String): Unit {
        transport.send(HydraRequest("GET", fillPath("/api/camera/media/{cameraId}/{kind}/{filename}", mapOf("cameraId" to cameraId, "kind" to kind, "filename" to filename)), emptyMap(), null, "public"))
        return Unit
    }

    /** DELETE /api/camera/media/{cameraId}/{kind}/{filename} (access: user) */
    suspend fun deleteCameraMediaByCameraIdByKindByFilename(cameraId: Long, kind: String, filename: String): HydraCameraCapture {
        return transport.send(HydraRequest("DELETE", fillPath("/api/camera/media/{cameraId}/{kind}/{filename}", mapOf("cameraId" to cameraId, "kind" to kind, "filename" to filename)), emptyMap(), null, "user")) as HydraCameraCapture
    }

    /** POST /api/camera/ticket (access: user) */
    suspend fun postCameraTicket(): Unit {
        transport.send(HydraRequest("POST", "/api/camera/ticket", emptyMap(), null, "user"))
        return Unit
    }

    /** POST /api/camera/{id}/ptz (access: admin) */
    suspend fun postCameraByIdPtz(id: Long, body: Map<String, Any?>): HydraPtzResult {
        return transport.send(HydraRequest("POST", fillPath("/api/camera/{id}/ptz", mapOf("id" to id)), emptyMap(), body, "admin")) as HydraPtzResult
    }

    /** POST /api/camera/{id}/recording/start (access: user) */
    suspend fun postCameraByIdRecordingStart(id: Long): HydraCameraCapture {
        return transport.send(HydraRequest("POST", fillPath("/api/camera/{id}/recording/start", mapOf("id" to id)), emptyMap(), null, "user")) as HydraCameraCapture
    }

    /** POST /api/camera/{id}/recording/stop (access: user) */
    suspend fun postCameraByIdRecordingStop(id: Long): HydraCameraCapture {
        return transport.send(HydraRequest("POST", fillPath("/api/camera/{id}/recording/stop", mapOf("id" to id)), emptyMap(), null, "user")) as HydraCameraCapture
    }

    /** POST /api/camera/{id}/snapshot (access: user) */
    suspend fun postCameraByIdSnapshot(id: Long): HydraCameraCapture {
        return transport.send(HydraRequest("POST", fillPath("/api/camera/{id}/snapshot", mapOf("id" to id)), emptyMap(), null, "user")) as HydraCameraCapture
    }

    /** GET /api/camera/{id}/stream (access: public) */
    suspend fun getCameraByIdStream(id: Long): Unit {
        transport.send(HydraRequest("GET", fillPath("/api/camera/{id}/stream", mapOf("id" to id)), emptyMap(), null, "public"))
        return Unit
    }

    /** GET /api/cameras/status (access: user) */
    suspend fun getCamerasStatus(): HydraCameraProcessStatus {
        return transport.send(HydraRequest("GET", "/api/cameras/status", emptyMap(), null, "user")) as HydraCameraProcessStatus
    }

    /** GET /api/claims (access: user) */
    suspend fun getClaims(): Unit {
        transport.send(HydraRequest("GET", "/api/claims", emptyMap(), null, "user"))
        return Unit
    }

    /** List the clients the server has seen (access: user) */
    suspend fun getConnectionsClients(kind: String? = null, user: String? = null, active: String? = null): HydraConnectionClientList {
        return transport.send(HydraRequest("GET", "/api/connections/clients", queryOf(mapOf("kind" to kind, "user" to user, "active" to active)), null, "user")) as HydraConnectionClientList
    }

    /** List the history of the sign-ins of the clients (access: user) */
    suspend fun getConnectionsEvents(kind: String? = null, action: String? = null, user: String? = null, before: String? = null, limit: String? = null): HydraConnectionEventList {
        return transport.send(HydraRequest("GET", "/api/connections/events", queryOf(mapOf("kind" to kind, "action" to action, "user" to user, "before" to before, "limit" to limit)), null, "user")) as HydraConnectionEventList
    }

    /** GET /api/connector-hub/gate/audit (access: user) */
    suspend fun getConnectorHubGateAudit(): HydraPassthrough {
        return transport.send(HydraRequest("GET", "/api/connector-hub/gate/audit", emptyMap(), null, "user")) as HydraPassthrough
    }

    /** POST /api/connector-hub/gate/evaluate (access: user) */
    suspend fun postConnectorHubGateEvaluate(): HydraPassthrough {
        return transport.send(HydraRequest("POST", "/api/connector-hub/gate/evaluate", emptyMap(), null, "user")) as HydraPassthrough
    }

    /** GET /api/connector-hub/gate/settings (access: user) */
    suspend fun getConnectorHubGateSettings(): Map<String, Any?> {
        return transport.send(HydraRequest("GET", "/api/connector-hub/gate/settings", emptyMap(), null, "user")) as Map<String, Any?>
    }

    /** POST /api/connector-hub/gate/settings (access: admin) */
    suspend fun postConnectorHubGateSettings(body: Map<String, Any?>): Map<String, Any?> {
        return transport.send(HydraRequest("POST", "/api/connector-hub/gate/settings", emptyMap(), body, "admin")) as Map<String, Any?>
    }

    /** GET /api/dev-server/status (access: user) */
    suspend fun getDevServerStatus(verify: String? = null): Unit {
        transport.send(HydraRequest("GET", "/api/dev-server/status", queryOf(mapOf("verify" to verify)), null, "user"))
        return Unit
    }

    /** GET /api/developer-node/status (access: user) */
    suspend fun getDeveloperNodeStatus(verify: String? = null): Unit {
        transport.send(HydraRequest("GET", "/api/developer-node/status", queryOf(mapOf("verify" to verify)), null, "user"))
        return Unit
    }

    /** POST /api/device/login (access: public) */
    suspend fun postDeviceLogin(body: Map<String, Any?>): HydraLoginResult {
        return transport.send(HydraRequest("POST", "/api/device/login", emptyMap(), body, "public")) as HydraLoginResult
    }

    /** GET /api/droid-estop/settings (access: user) */
    suspend fun getDroidEstopSettings(): Map<String, Any?> {
        return transport.send(HydraRequest("GET", "/api/droid-estop/settings", emptyMap(), null, "user")) as Map<String, Any?>
    }

    /** POST /api/droid-estop/settings (access: admin) */
    suspend fun postDroidEstopSettings(body: Map<String, Any?>): Map<String, Any?> {
        return transport.send(HydraRequest("POST", "/api/droid-estop/settings", emptyMap(), body, "admin")) as Map<String, Any?>
    }

    /** GET /api/ecosystem/health (access: user) */
    suspend fun getEcosystemHealth(): HydraEcosystemHealth {
        return transport.send(HydraRequest("GET", "/api/ecosystem/health", emptyMap(), null, "user")) as HydraEcosystemHealth
    }

    /** GET /api/ecosystem/node-health (access: user) */
    suspend fun getEcosystemNodeHealth(slot: String? = null): HydraNodeHealth {
        return transport.send(HydraRequest("GET", "/api/ecosystem/node-health", queryOf(mapOf("slot" to slot)), null, "user")) as HydraNodeHealth
    }

    /** POST /api/ecosystem/service/{unit}/{action} (access: admin) */
    suspend fun postEcosystemServiceByUnitByAction(unit: String, action: String): HydraSuccess {
        return transport.send(HydraRequest("POST", fillPath("/api/ecosystem/service/{unit}/{action}", mapOf("unit" to unit, "action" to action)), emptyMap(), null, "admin")) as HydraSuccess
    }

    /** GET /api/ecosystem/status (access: public) */
    suspend fun getEcosystemStatus(): HydraEcosystemStatus {
        return transport.send(HydraRequest("GET", "/api/ecosystem/status", emptyMap(), null, "public")) as HydraEcosystemStatus
    }

    /** GET /api/faults (access: user) */
    suspend fun getFaults(active: String? = null, limit: String? = null, verify: String? = null): Unit {
        transport.send(HydraRequest("GET", "/api/faults", queryOf(mapOf("active" to active, "limit" to limit, "verify" to verify)), null, "user"))
        return Unit
    }

    /** POST /api/hardware/canota/flash (access: admin) */
    suspend fun postHardwareCanotaFlash(tier: String? = null, slot: String? = null, relay: String? = null, hardwareId: String? = null, versionMajor: String? = null, versionMinor: String? = null, versionPatch: String? = null, signature: String? = null, downgradeFrom: String? = null, target: String? = null, minBootloader: String? = null): HydraCanotaFlash {
        return transport.send(HydraRequest("POST", "/api/hardware/canota/flash", queryOf(mapOf("tier" to tier, "slot" to slot, "relay" to relay, "hardware_id" to hardwareId, "version_major" to versionMajor, "version_minor" to versionMinor, "version_patch" to versionPatch, "signature" to signature, "downgrade_from" to downgradeFrom, "target" to target, "min_bootloader" to minBootloader)), null, "admin")) as HydraCanotaFlash
    }

    /** GET /api/hardware/canota/version (access: user) */
    suspend fun getHardwareCanotaVersion(relay: String? = null, slot: String? = null, tier: String? = null): HydraPassthrough {
        return transport.send(HydraRequest("GET", "/api/hardware/canota/version", queryOf(mapOf("relay" to relay, "slot" to slot, "tier" to tier)), null, "user")) as HydraPassthrough
    }

    /** POST /api/hardware/fram/erase (access: admin) */
    suspend fun postHardwareFramErase(body: Map<String, Any?>): HydraPassthrough {
        return transport.send(HydraRequest("POST", "/api/hardware/fram/erase", emptyMap(), body, "admin")) as HydraPassthrough
    }

    /** POST /api/hardware/fram/selftest (access: admin) */
    suspend fun postHardwareFramSelftest(): HydraPassthrough {
        return transport.send(HydraRequest("POST", "/api/hardware/fram/selftest", emptyMap(), null, "admin")) as HydraPassthrough
    }

    /** GET /api/hil-bridge/settings (access: user) */
    suspend fun getHilBridgeSettings(): Map<String, Any?> {
        return transport.send(HydraRequest("GET", "/api/hil-bridge/settings", emptyMap(), null, "user")) as Map<String, Any?>
    }

    /** POST /api/hil-bridge/settings (access: admin) */
    suspend fun postHilBridgeSettings(body: Map<String, Any?>): Map<String, Any?> {
        return transport.send(HydraRequest("POST", "/api/hil-bridge/settings", emptyMap(), body, "admin")) as Map<String, Any?>
    }

    /** GET /api/hydra-info (access: public) */
    suspend fun getHydraInfo(): HydraHydraInfo {
        return transport.send(HydraRequest("GET", "/api/hydra-info", emptyMap(), null, "public")) as HydraHydraInfo
    }

    /** POST /api/info/ticket (access: user) */
    suspend fun postInfoTicket(body: Map<String, Any?>? = null): HydraInfoTicket {
        return transport.send(HydraRequest("POST", "/api/info/ticket", emptyMap(), body, "user")) as HydraInfoTicket
    }

    /** POST /api/ingest/dev-server/status (access: public) */
    suspend fun postIngestDevServerStatus(): Unit {
        transport.send(HydraRequest("POST", "/api/ingest/dev-server/status", emptyMap(), null, "public"))
        return Unit
    }

    /** POST /api/ingest/developer-node/status (access: public) */
    suspend fun postIngestDeveloperNodeStatus(): Unit {
        transport.send(HydraRequest("POST", "/api/ingest/developer-node/status", emptyMap(), null, "public"))
        return Unit
    }

    /** POST /api/ingest/scenario-outcome (access: user) */
    suspend fun postIngestScenarioOutcome(): Unit {
        transport.send(HydraRequest("POST", "/api/ingest/scenario-outcome", emptyMap(), null, "user"))
        return Unit
    }

    /** GET /api/ingest/scenario-outcomes (access: user) */
    suspend fun getIngestScenarioOutcomes(fingerprintKind: String? = null, limit: String? = null, scenarioId: String? = null, verify: String? = null): Unit {
        transport.send(HydraRequest("GET", "/api/ingest/scenario-outcomes", queryOf(mapOf("fingerprint_kind" to fingerprintKind, "limit" to limit, "scenario_id" to scenarioId, "verify" to verify)), null, "user"))
        return Unit
    }

    /** POST /api/integrations/test-connection (access: user) */
    suspend fun postIntegrationsTestConnection(body: Map<String, Any?>): HydraReachable {
        return transport.send(HydraRequest("POST", "/api/integrations/test-connection", emptyMap(), body, "user")) as HydraReachable
    }

    /** POST /api/login (access: public) */
    suspend fun postLogin(body: Map<String, Any?>): HydraLoginResult {
        return transport.send(HydraRequest("POST", "/api/login", emptyMap(), body, "public")) as HydraLoginResult
    }

    /** POST /api/logout (access: public) */
    suspend fun postLogout(body: Map<String, Any?>? = null): HydraSuccess {
        return transport.send(HydraRequest("POST", "/api/logout", emptyMap(), body, "public")) as HydraSuccess
    }

    /** GET /api/models (access: public) */
    suspend fun getModels(): HydraModelList {
        return transport.send(HydraRequest("GET", "/api/models", emptyMap(), null, "public")) as HydraModelList
    }

    /** POST /api/models/submit (access: admin) */
    suspend fun postModelsSubmit(body: Map<String, Any?>? = null): HydraModelSubmitted {
        return transport.send(HydraRequest("POST", "/api/models/submit", emptyMap(), body, "admin")) as HydraModelSubmitted
    }

    /** GET /api/models/{category}/{slug}/download (access: public) */
    suspend fun getModelsByCategoryBySlugDownload(category: String, slug: String): Unit {
        transport.send(HydraRequest("GET", fillPath("/api/models/{category}/{slug}/download", mapOf("category" to category, "slug" to slug)), emptyMap(), null, "public"))
        return Unit
    }

    /** POST /api/operator/confirmations (access: user) */
    suspend fun postOperatorConfirmations(body: Map<String, Any?>): Map<String, Any?> {
        return transport.send(HydraRequest("POST", "/api/operator/confirmations", emptyMap(), body, "user")) as Map<String, Any?>
    }

    /** GET /api/operator/presence (access: user) */
    suspend fun getOperatorPresence(): HydraOperatorPresence {
        return transport.send(HydraRequest("GET", "/api/operator/presence", emptyMap(), null, "user")) as HydraOperatorPresence
    }

    /** POST /api/operator/presence (access: user) */
    suspend fun postOperatorPresence(body: Map<String, Any?>): HydraOperatorPresenceAck {
        return transport.send(HydraRequest("POST", "/api/operator/presence", emptyMap(), body, "user")) as HydraOperatorPresenceAck
    }

    /** GET /api/ops-agent/proposals (access: admin) */
    suspend fun getOpsAgentProposals(): Map<String, Any?> {
        return transport.send(HydraRequest("GET", "/api/ops-agent/proposals", emptyMap(), null, "admin")) as Map<String, Any?>
    }

    /** POST /api/ops-agent/proposals/decide (access: admin) */
    suspend fun postOpsAgentProposalsDecide(body: Map<String, Any?>): Map<String, Any?> {
        return transport.send(HydraRequest("POST", "/api/ops-agent/proposals/decide", emptyMap(), body, "admin")) as Map<String, Any?>
    }

    /** POST /api/push/devices (access: user) */
    suspend fun postPushDevices(body: Map<String, Any?>): HydraPushDeviceRegistered {
        return transport.send(HydraRequest("POST", "/api/push/devices", emptyMap(), body, "user")) as HydraPushDeviceRegistered
    }

    /** DELETE /api/push/devices/{token} (access: user) */
    suspend fun deletePushDevicesByToken(token: String): HydraPushDeviceRemoved {
        return transport.send(HydraRequest("DELETE", fillPath("/api/push/devices/{token}", mapOf("token" to token)), emptyMap(), null, "user")) as HydraPushDeviceRemoved
    }

    /** POST /api/push/live-activities (access: user) */
    suspend fun postPushLiveActivities(body: Map<String, Any?>): HydraLiveActivityRegistered {
        return transport.send(HydraRequest("POST", "/api/push/live-activities", emptyMap(), body, "user")) as HydraLiveActivityRegistered
    }

    /** DELETE /api/push/live-activities/{token} (access: user) */
    suspend fun deletePushLiveActivitiesByToken(token: String): HydraLiveActivityRemoved {
        return transport.send(HydraRequest("DELETE", fillPath("/api/push/live-activities/{token}", mapOf("token" to token)), emptyMap(), null, "user")) as HydraLiveActivityRemoved
    }

    /** POST /api/refresh (access: public) */
    suspend fun postRefresh(body: Map<String, Any?>): HydraLoginResult {
        return transport.send(HydraRequest("POST", "/api/refresh", emptyMap(), body, "public")) as HydraLoginResult
    }

    /** GET /api/robot/{id} (access: user) */
    suspend fun getRobotById(id: Long): Map<String, Any?> {
        return transport.send(HydraRequest("GET", fillPath("/api/robot/{id}", mapOf("id" to id)), emptyMap(), null, "user")) as Map<String, Any?>
    }

    /** POST /api/robot/{id}/claim (access: user) */
    suspend fun postRobotByIdClaim(id: Long, headerIfMatch: String? = null, headerXControllerId: String? = null, body: Map<String, Any?>? = null): Map<String, Any?> {
        return transport.send(HydraRequest("POST", fillPath("/api/robot/{id}/claim", mapOf("id" to id)), emptyMap(), body, "user", headers = queryOf(mapOf("If-Match" to headerIfMatch, "X-Controller-Id" to headerXControllerId)))) as Map<String, Any?>
    }

    /** POST /api/robot/{id}/command (access: user) */
    suspend fun postRobotByIdCommand(id: Long, body: Map<String, Any?>, headerIfMatch: String? = null, headerXControllerId: String? = null, headerXCorrelationId: String? = null): Map<String, Any?> {
        return transport.send(HydraRequest("POST", fillPath("/api/robot/{id}/command", mapOf("id" to id)), emptyMap(), body, "user", headers = queryOf(mapOf("If-Match" to headerIfMatch, "X-Controller-Id" to headerXControllerId, "X-Correlation-Id" to headerXCorrelationId)))) as Map<String, Any?>
    }

    /** POST /api/robot/{id}/heartbeat (access: user) */
    suspend fun postRobotByIdHeartbeat(id: Long): HydraSuccess {
        return transport.send(HydraRequest("POST", fillPath("/api/robot/{id}/heartbeat", mapOf("id" to id)), emptyMap(), null, "user")) as HydraSuccess
    }

    /** POST /api/robot/{id}/jog-arm (access: user) */
    suspend fun postRobotByIdJogArm(id: Long, body: Map<String, Any?>, headerXControllerId: String? = null): Map<String, Any?> {
        return transport.send(HydraRequest("POST", fillPath("/api/robot/{id}/jog-arm", mapOf("id" to id)), emptyMap(), body, "user", headers = queryOf(mapOf("X-Controller-Id" to headerXControllerId)))) as Map<String, Any?>
    }

    /** POST /api/robot/{id}/release (access: user) */
    suspend fun postRobotByIdRelease(id: Long, headerIfMatch: String? = null, headerXControllerId: String? = null, body: Map<String, Any?>? = null): Map<String, Any?> {
        return transport.send(HydraRequest("POST", fillPath("/api/robot/{id}/release", mapOf("id" to id)), emptyMap(), body, "user", headers = queryOf(mapOf("If-Match" to headerIfMatch, "X-Controller-Id" to headerXControllerId)))) as Map<String, Any?>
    }

    /** GET /api/robots/liveness (access: user) */
    suspend fun getRobotsLiveness(): HydraRobotLiveness {
        return transport.send(HydraRequest("GET", "/api/robots/liveness", emptyMap(), null, "user")) as HydraRobotLiveness
    }

    /** GET /api/ros2-bridge/settings (access: user) */
    suspend fun getRos2BridgeSettings(): Map<String, Any?> {
        return transport.send(HydraRequest("GET", "/api/ros2-bridge/settings", emptyMap(), null, "user")) as Map<String, Any?>
    }

    /** POST /api/ros2-bridge/settings (access: admin) */
    suspend fun postRos2BridgeSettings(body: Map<String, Any?>): Map<String, Any?> {
        return transport.send(HydraRequest("POST", "/api/ros2-bridge/settings", emptyMap(), body, "admin")) as Map<String, Any?>
    }

    /** GET /api/rul/config (access: user) */
    suspend fun getRulConfig(): HydraRulConfig {
        return transport.send(HydraRequest("GET", "/api/rul/config", emptyMap(), null, "user")) as HydraRulConfig
    }

    /** GET /api/safety-limits (access: user) */
    suspend fun getSafetyLimits(robotId: String? = null): Unit {
        transport.send(HydraRequest("GET", "/api/safety-limits", queryOf(mapOf("robotId" to robotId)), null, "user"))
        return Unit
    }

    /** GET /api/semantic-planner/settings (access: user) */
    suspend fun getSemanticPlannerSettings(): Map<String, Any?> {
        return transport.send(HydraRequest("GET", "/api/semantic-planner/settings", emptyMap(), null, "user")) as Map<String, Any?>
    }

    /** POST /api/semantic-planner/settings (access: admin) */
    suspend fun postSemanticPlannerSettings(body: Map<String, Any?>): Map<String, Any?> {
        return transport.send(HydraRequest("POST", "/api/semantic-planner/settings", emptyMap(), body, "admin")) as Map<String, Any?>
    }

    /** GET /api/settings (access: user) */
    suspend fun getSettings(): HydraSettings {
        return transport.send(HydraRequest("GET", "/api/settings", emptyMap(), null, "user")) as HydraSettings
    }

    /** PUT /api/settings (access: admin) */
    suspend fun putSettings(headerIfMatch: String, body: HydraSettings): Map<String, Any?> {
        return transport.send(HydraRequest("PUT", "/api/settings", emptyMap(), body, "admin", headers = queryOf(mapOf("If-Match" to headerIfMatch)))) as Map<String, Any?>
    }

    /** POST /api/settings (access: admin) */
    suspend fun postSettings(body: HydraSettings, headerIfMatch: String? = null): Map<String, Any?> {
        return transport.send(HydraRequest("POST", "/api/settings", emptyMap(), body, "admin", headers = queryOf(mapOf("If-Match" to headerIfMatch)))) as Map<String, Any?>
    }

    /** POST /api/stop-all (access: user) */
    suspend fun postStopAll(): HydraStopAllResult {
        return transport.send(HydraRequest("POST", "/api/stop-all", emptyMap(), null, "user")) as HydraStopAllResult
    }

    /** POST /api/stop-all/release (access: admin) */
    suspend fun postStopAllRelease(): HydraGlobalStopReleased {
        return transport.send(HydraRequest("POST", "/api/stop-all/release", emptyMap(), null, "admin")) as HydraGlobalStopReleased
    }

    /** POST /api/system/bluetooth/pair (access: admin) */
    suspend fun postSystemBluetoothPair(body: Map<String, Any?>): Unit {
        transport.send(HydraRequest("POST", "/api/system/bluetooth/pair", emptyMap(), body, "admin"))
        return Unit
    }

    /** POST /api/system/bluetooth/power (access: admin) */
    suspend fun postSystemBluetoothPower(body: Map<String, Any?>): HydraSuccess {
        return transport.send(HydraRequest("POST", "/api/system/bluetooth/power", emptyMap(), body, "admin")) as HydraSuccess
    }

    /** POST /api/system/bluetooth/remove (access: admin) */
    suspend fun postSystemBluetoothRemove(body: Map<String, Any?>): HydraSuccess {
        return transport.send(HydraRequest("POST", "/api/system/bluetooth/remove", emptyMap(), body, "admin")) as HydraSuccess
    }

    /** POST /api/system/bluetooth/scan (access: admin) */
    suspend fun postSystemBluetoothScan(): HydraBluetoothScan {
        return transport.send(HydraRequest("POST", "/api/system/bluetooth/scan", emptyMap(), null, "admin")) as HydraBluetoothScan
    }

    /** GET /api/system/bluetooth/status (access: admin) */
    suspend fun getSystemBluetoothStatus(): Unit {
        transport.send(HydraRequest("GET", "/api/system/bluetooth/status", emptyMap(), null, "admin"))
        return Unit
    }

    /** GET /api/system/metrics (access: public) */
    suspend fun getSystemMetrics(): HydraSystemMetrics {
        return transport.send(HydraRequest("GET", "/api/system/metrics", emptyMap(), null, "public")) as HydraSystemMetrics
    }

    /** POST /api/system/reboot (access: public) */
    suspend fun postSystemReboot(): HydraSuccess {
        return transport.send(HydraRequest("POST", "/api/system/reboot", emptyMap(), null, "public")) as HydraSuccess
    }

    /** POST /api/system/shutdown (access: public) */
    suspend fun postSystemShutdown(): HydraSuccess {
        return transport.send(HydraRequest("POST", "/api/system/shutdown", emptyMap(), null, "public")) as HydraSuccess
    }

    /** GET /api/system/supervisor (access: public) */
    suspend fun getSystemSupervisor(): HydraSupervisorSnapshot {
        return transport.send(HydraRequest("GET", "/api/system/supervisor", emptyMap(), null, "public")) as HydraSupervisorSnapshot
    }

    /** GET /api/telemetry/aggregate (access: user) */
    suspend fun getTelemetryAggregate(sourceId: String? = null, kind: String? = null, field: String? = null, bucketMs: String? = null, start: String? = null, end: String? = null, before: String? = null, agg: String? = null): List<Map<String, Any?>> {
        return transport.send(HydraRequest("GET", "/api/telemetry/aggregate", queryOf(mapOf("sourceId" to sourceId, "kind" to kind, "field" to field, "bucketMs" to bucketMs, "start" to start, "end" to end, "before" to before, "agg" to agg)), null, "user")) as List<Map<String, Any?>>
    }

    /** GET /api/telemetry/downsample-plan (access: admin) */
    suspend fun getTelemetryDownsamplePlan(): Map<String, Any?> {
        return transport.send(HydraRequest("GET", "/api/telemetry/downsample-plan", emptyMap(), null, "admin")) as Map<String, Any?>
    }

    /** PUT /api/telemetry/downsample-plan (access: admin) */
    suspend fun putTelemetryDownsamplePlan(body: Map<String, Any?>, preview: String? = null): Map<String, Any?> {
        return transport.send(HydraRequest("PUT", "/api/telemetry/downsample-plan", queryOf(mapOf("preview" to preview)), body, "admin")) as Map<String, Any?>
    }

    /** GET /api/telemetry/query (access: user) */
    suspend fun getTelemetryQuery(sourceId: String? = null, kind: String? = null, field: String? = null, start: String? = null, end: String? = null, before: String? = null, limit: String? = null, cursor: String? = null): List<Map<String, Any?>> {
        return transport.send(HydraRequest("GET", "/api/telemetry/query", queryOf(mapOf("sourceId" to sourceId, "kind" to kind, "field" to field, "start" to start, "end" to end, "before" to before, "limit" to limit, "cursor" to cursor)), null, "user")) as List<Map<String, Any?>>
    }

    /** GET /api/tool-arms (access: user) */
    suspend fun getToolArms(): HydraToolArmsReport {
        return transport.send(HydraRequest("GET", "/api/tool-arms", emptyMap(), null, "user")) as HydraToolArmsReport
    }

    /** POST /api/tool-arms/reset (access: admin) */
    suspend fun postToolArmsReset(body: Map<String, Any?>): HydraToolArmResetResult {
        return transport.send(HydraRequest("POST", "/api/tool-arms/reset", emptyMap(), body, "admin")) as HydraToolArmResetResult
    }

    /** POST /api/totp/begin (access: user) */
    suspend fun postTotpBegin(body: Map<String, Any?>): HydraTotpEnrolment {
        return transport.send(HydraRequest("POST", "/api/totp/begin", emptyMap(), body, "user")) as HydraTotpEnrolment
    }

    /** POST /api/totp/confirm (access: user) */
    suspend fun postTotpConfirm(body: Map<String, Any?>): HydraTotpConfirmed {
        return transport.send(HydraRequest("POST", "/api/totp/confirm", emptyMap(), body, "user")) as HydraTotpConfirmed
    }

    /** POST /api/totp/disable (access: user) */
    suspend fun postTotpDisable(body: Map<String, Any?>): HydraSuccess {
        return transport.send(HydraRequest("POST", "/api/totp/disable", emptyMap(), body, "user")) as HydraSuccess
    }

    /** GET /api/totp/status (access: user) */
    suspend fun getTotpStatus(): HydraTotpStatus {
        return transport.send(HydraRequest("GET", "/api/totp/status", emptyMap(), null, "user")) as HydraTotpStatus
    }

    /** POST /api/trajectory/proposals/verify (access: user) */
    suspend fun postTrajectoryProposalsVerify(): Unit {
        transport.send(HydraRequest("POST", "/api/trajectory/proposals/verify", emptyMap(), null, "user"))
        return Unit
    }

    /** POST /api/upload-work (access: user) */
    suspend fun postUploadWork(body: Map<String, Any?>): HydraSuccess {
        return transport.send(HydraRequest("POST", "/api/upload-work", emptyMap(), body, "user")) as HydraSuccess
    }

    /** GET /api/users (access: admin) */
    suspend fun getUsers(): HydraUserList {
        return transport.send(HydraRequest("GET", "/api/users", emptyMap(), null, "admin")) as HydraUserList
    }

    /** POST /api/users (access: admin) */
    suspend fun postUsers(body: Map<String, Any?>): HydraSuccess {
        return transport.send(HydraRequest("POST", "/api/users", emptyMap(), body, "admin")) as HydraSuccess
    }

    /** PUT /api/users/{username} (access: admin) */
    suspend fun putUsersByUsername(username: String, body: Map<String, Any?>? = null): HydraSuccess {
        return transport.send(HydraRequest("PUT", fillPath("/api/users/{username}", mapOf("username" to username)), emptyMap(), body, "admin")) as HydraSuccess
    }

    /** DELETE /api/users/{username} (access: admin) */
    suspend fun deleteUsersByUsername(username: String): HydraSuccess {
        return transport.send(HydraRequest("DELETE", fillPath("/api/users/{username}", mapOf("username" to username)), emptyMap(), null, "admin")) as HydraSuccess
    }

    /** DELETE /api/users/{username}/totp (access: admin) */
    suspend fun deleteUsersByUsernameTotp(username: String): HydraSuccess {
        return transport.send(HydraRequest("DELETE", fillPath("/api/users/{username}/totp", mapOf("username" to username)), emptyMap(), null, "admin")) as HydraSuccess
    }

    /** GET /api/voice/chain (access: admin) */
    suspend fun getVoiceChain(limit: String? = null, verify: String? = null): Unit {
        transport.send(HydraRequest("GET", "/api/voice/chain", queryOf(mapOf("limit" to limit, "verify" to verify)), null, "admin"))
        return Unit
    }

    /** POST /api/voice/confirm (access: user) */
    suspend fun postVoiceConfirm(body: Map<String, Any?>? = null): Unit {
        transport.send(HydraRequest("POST", "/api/voice/confirm", emptyMap(), body, "user"))
        return Unit
    }

    /** POST /api/voice/turn (access: user) */
    suspend fun postVoiceTurn(body: Map<String, Any?>? = null): Unit {
        transport.send(HydraRequest("POST", "/api/voice/turn", emptyMap(), body, "user"))
        return Unit
    }

    /** GET /api/watch/system-status (access: user) */
    suspend fun getWatchSystemStatus(): Unit {
        transport.send(HydraRequest("GET", "/api/watch/system-status", emptyMap(), null, "user"))
        return Unit
    }

    /** GET /health (access: public) */
    suspend fun getHealth(): HydraHealthReport {
        return transport.send(HydraRequest("GET", "/health", emptyMap(), null, "public")) as HydraHealthReport
    }

    /** GET /metrics (access: public) */
    suspend fun getMetrics(): Unit {
        transport.send(HydraRequest("GET", "/metrics", emptyMap(), null, "public"))
        return Unit
    }

}

val HYDRA_CLIENT_OPERATIONS: List<String> = listOf(
    "getWellKnownJwksJson",
    "getAdapters",
    "getAdaptersByAdapterId",
    "getAdminClients",
    "getAdminDeviceTokens",
    "postAdminDeviceTokens",
    "deleteAdminDeviceTokensById",
    "getAdminFleetUpdate",
    "postAdminFleetUpdateApply",
    "postAdminFleetUpdatePlan",
    "postAdminFleetUpdateResume",
    "getAdminJwtKeys",
    "postAdminJwtKeysRotate",
    "getAdminLogs",
    "postAdminMaintenanceInstall",
    "postAdminMaintenancePrune",
    "postAdminMaintenanceRollback",
    "getAdminMaintenanceStatus",
    "getAdminPush",
    "postAdminRestart",
    "getAdminRobotIds",
    "putAdminSafetyLimits",
    "getAdminSelfUpdate",
    "postAdminSelfUpdateApply",
    "getAdminSelfUpdateJobsById",
    "postAdminSelfUpdateRollback",
    "getAdminServerConfig",
    "putAdminServerConfig",
    "getAdminServiceIdentity",
    "getAdminUpdates",
    "getAnomalyVerdicts",
    "getAudit",
    "getBridges",
    "postBridgesByNameCmdByVerb",
    "getBridgesByNameState",
    "postCameraDiscoverRtspPath",
    "getCameraDiscoverUsbDevices",
    "getCameraMedia",
    "getCameraMediaByCameraIdByKindByFilename",
    "deleteCameraMediaByCameraIdByKindByFilename",
    "postCameraTicket",
    "postCameraByIdPtz",
    "postCameraByIdRecordingStart",
    "postCameraByIdRecordingStop",
    "postCameraByIdSnapshot",
    "getCameraByIdStream",
    "getCamerasStatus",
    "getClaims",
    "getConnectionsClients",
    "getConnectionsEvents",
    "getConnectorHubGateAudit",
    "postConnectorHubGateEvaluate",
    "getConnectorHubGateSettings",
    "postConnectorHubGateSettings",
    "getDevServerStatus",
    "getDeveloperNodeStatus",
    "postDeviceLogin",
    "getDroidEstopSettings",
    "postDroidEstopSettings",
    "getEcosystemHealth",
    "getEcosystemNodeHealth",
    "postEcosystemServiceByUnitByAction",
    "getEcosystemStatus",
    "getFaults",
    "postHardwareCanotaFlash",
    "getHardwareCanotaVersion",
    "postHardwareFramErase",
    "postHardwareFramSelftest",
    "getHilBridgeSettings",
    "postHilBridgeSettings",
    "getHydraInfo",
    "postInfoTicket",
    "postIngestDevServerStatus",
    "postIngestDeveloperNodeStatus",
    "postIngestScenarioOutcome",
    "getIngestScenarioOutcomes",
    "postIntegrationsTestConnection",
    "postLogin",
    "postLogout",
    "getModels",
    "postModelsSubmit",
    "getModelsByCategoryBySlugDownload",
    "postOperatorConfirmations",
    "getOperatorPresence",
    "postOperatorPresence",
    "getOpsAgentProposals",
    "postOpsAgentProposalsDecide",
    "postPushDevices",
    "deletePushDevicesByToken",
    "postPushLiveActivities",
    "deletePushLiveActivitiesByToken",
    "postRefresh",
    "getRobotById",
    "postRobotByIdClaim",
    "postRobotByIdCommand",
    "postRobotByIdHeartbeat",
    "postRobotByIdJogArm",
    "postRobotByIdRelease",
    "getRobotsLiveness",
    "getRos2BridgeSettings",
    "postRos2BridgeSettings",
    "getRulConfig",
    "getSafetyLimits",
    "getSemanticPlannerSettings",
    "postSemanticPlannerSettings",
    "getSettings",
    "putSettings",
    "postSettings",
    "postStopAll",
    "postStopAllRelease",
    "postSystemBluetoothPair",
    "postSystemBluetoothPower",
    "postSystemBluetoothRemove",
    "postSystemBluetoothScan",
    "getSystemBluetoothStatus",
    "getSystemMetrics",
    "postSystemReboot",
    "postSystemShutdown",
    "getSystemSupervisor",
    "getTelemetryAggregate",
    "getTelemetryDownsamplePlan",
    "putTelemetryDownsamplePlan",
    "getTelemetryQuery",
    "getToolArms",
    "postToolArmsReset",
    "postTotpBegin",
    "postTotpConfirm",
    "postTotpDisable",
    "getTotpStatus",
    "postTrajectoryProposalsVerify",
    "postUploadWork",
    "getUsers",
    "postUsers",
    "putUsersByUsername",
    "deleteUsersByUsername",
    "deleteUsersByUsernameTotp",
    "getVoiceChain",
    "postVoiceConfirm",
    "postVoiceTurn",
    "getWatchSystemStatus",
    "getHealth",
    "getMetrics",
)
