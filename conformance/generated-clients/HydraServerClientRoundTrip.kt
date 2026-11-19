// Generated from the server contract by tools/generate_clients.py. Do not edit.

package hydra.umc.client

// Reads an example of every class with fromJson and writes it with toJson: the result must equal the example.
private val failures = mutableListOf<String>()

private fun <T> roundTrip(label: String, example: Map<String, Any?>, read: (Map<String, Any?>) -> T, write: (T) -> Map<String, Any?>) {
    val again = try { write(read(example)) } catch (error: Exception) { failures.add("$label threw $error"); return }
    if (again != example) failures.add("$label changed: $again instead of $example")
}

private fun roundTripHydraAuditEntry() {
    roundTrip("HydraAuditEntry full", mapOf<String, Any?>("seq" to 7L, "ts" to "text", "prev" to "text", "hash" to "text", "type" to "text", "outcome" to "ok", "userId" to "sample", "username" to "text", "controllerId" to "text", "ip" to "text", "robotId" to 7L, "detail" to mapOf<String, Any?>("extraKey" to "extra"), "extraKey" to "extra"), { HydraAuditEntry.fromJson(it) }, { it.toJson() })
    roundTrip("HydraAuditEntry required only", mapOf<String, Any?>("seq" to 7L, "ts" to "text", "prev" to "text", "hash" to "text", "type" to "text", "outcome" to "ok"), { HydraAuditEntry.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraAuditReport() {
    roundTrip("HydraAuditReport full", mapOf<String, Any?>("enabled" to true, "lockedOff" to true, "entries" to listOf<Any?>(mapOf<String, Any?>("seq" to 7L, "ts" to "text", "prev" to "text", "hash" to "text", "type" to "text", "outcome" to "ok", "userId" to "sample", "username" to "text", "controllerId" to "text", "ip" to "text", "robotId" to 7L, "detail" to mapOf<String, Any?>("extraKey" to "extra"), "extraKey" to "extra")), "verification" to mapOf<String, Any?>("ok" to true, "entries" to 7L, "brokenAtSeq" to 7L, "reason" to "text")), { HydraAuditReport.fromJson(it) }, { it.toJson() })
    roundTrip("HydraAuditReport required only", mapOf<String, Any?>("enabled" to true, "lockedOff" to true, "entries" to listOf<Any?>(mapOf<String, Any?>("seq" to 7L, "ts" to "text", "prev" to "text", "hash" to "text", "type" to "text", "outcome" to "ok"))), { HydraAuditReport.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraAuditVerification() {
    roundTrip("HydraAuditVerification full", mapOf<String, Any?>("ok" to true, "entries" to 7L, "brokenAtSeq" to 7L, "reason" to "text"), { HydraAuditVerification.fromJson(it) }, { it.toJson() })
    roundTrip("HydraAuditVerification required only", mapOf<String, Any?>("ok" to true, "entries" to 7L), { HydraAuditVerification.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraBluetoothScan() {
    roundTrip("HydraBluetoothScan full", mapOf<String, Any?>("success" to true, "devices" to listOf<Any?>(mapOf<String, Any?>("key" to "value"))), { HydraBluetoothScan.fromJson(it) }, { it.toJson() })
    roundTrip("HydraBluetoothScan required only", mapOf<String, Any?>("success" to true, "devices" to listOf<Any?>(mapOf<String, Any?>("key" to "value"))), { HydraBluetoothScan.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraBridgeCommandAccepted() {
    roundTrip("HydraBridgeCommandAccepted full", mapOf<String, Any?>("accepted" to true, "result" to "sample"), { HydraBridgeCommandAccepted.fromJson(it) }, { it.toJson() })
    roundTrip("HydraBridgeCommandAccepted required only", mapOf<String, Any?>("accepted" to true, "result" to "sample"), { HydraBridgeCommandAccepted.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraBridgeList() {
    roundTrip("HydraBridgeList full", mapOf<String, Any?>("connected" to true, "bridges" to listOf<Any?>(mapOf<String, Any?>("name" to "text", "available" to true, "state" to "sample", "health" to "sample", "updatedAt" to "text"))), { HydraBridgeList.fromJson(it) }, { it.toJson() })
    roundTrip("HydraBridgeList required only", mapOf<String, Any?>("connected" to true, "bridges" to listOf<Any?>(mapOf<String, Any?>("name" to "text", "available" to true, "state" to "sample", "health" to "sample", "updatedAt" to "text"))), { HydraBridgeList.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraBridgeState() {
    roundTrip("HydraBridgeState full", mapOf<String, Any?>("name" to "text", "available" to true, "state" to "sample", "health" to "sample", "updatedAt" to "text"), { HydraBridgeState.fromJson(it) }, { it.toJson() })
    roundTrip("HydraBridgeState required only", mapOf<String, Any?>("name" to "text", "available" to true, "state" to "sample", "health" to "sample", "updatedAt" to "text"), { HydraBridgeState.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraCameraCapture() {
    roundTrip("HydraCameraCapture full", mapOf<String, Any?>("success" to true, "cameraId" to 7L, "filename" to "text", "capturedAt" to "text", "sizeBytes" to 7L, "startedAt" to "text", "stoppedAt" to "text"), { HydraCameraCapture.fromJson(it) }, { it.toJson() })
    roundTrip("HydraCameraCapture required only", mapOf<String, Any?>("success" to true, "cameraId" to 7L, "filename" to "text"), { HydraCameraCapture.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraCameraMediaList() {
    roundTrip("HydraCameraMediaList full", mapOf<String, Any?>("items" to listOf<Any?>(mapOf<String, Any?>("cameraId" to 7L, "kind" to "snapshots", "filename" to "text", "sizeBytes" to 7L, "capturedAt" to "text", "recording" to true, "durationMs" to 7L, "frameCount" to 7L))), { HydraCameraMediaList.fromJson(it) }, { it.toJson() })
    roundTrip("HydraCameraMediaList required only", mapOf<String, Any?>("items" to listOf<Any?>(mapOf<String, Any?>("cameraId" to 7L, "kind" to "snapshots", "filename" to "text", "sizeBytes" to 7L, "capturedAt" to "text", "recording" to true))), { HydraCameraMediaList.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraCanotaFlash() {
    roundTrip("HydraCanotaFlash full", mapOf<String, Any?>("success" to true, "finalPhase" to "text"), { HydraCanotaFlash.fromJson(it) }, { it.toJson() })
    roundTrip("HydraCanotaFlash required only", mapOf<String, Any?>("success" to true, "finalPhase" to "text"), { HydraCanotaFlash.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraClaimList() {
    roundTrip("HydraClaimList full", mapOf<String, Any?>("claims" to listOf<Any?>(mapOf<String, Any?>("robotId" to 7L, "robotName" to "text", "cellId" to "sample", "ownerId" to "sample", "ownerUsername" to "text", "controllerId" to "text", "claimedAt" to 1.5, "expiresAt" to 1.5, "jogArmedUntil" to 1.5))), { HydraClaimList.fromJson(it) }, { it.toJson() })
    roundTrip("HydraClaimList required only", mapOf<String, Any?>("claims" to listOf<Any?>(mapOf<String, Any?>("robotId" to 7L, "ownerUsername" to "text", "claimedAt" to 1.5, "expiresAt" to 1.5))), { HydraClaimList.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraClaimView() {
    roundTrip("HydraClaimView full", mapOf<String, Any?>("robotId" to 7L, "robotName" to "text", "cellId" to "sample", "ownerId" to "sample", "ownerUsername" to "text", "controllerId" to "text", "claimedAt" to 1.5, "expiresAt" to 1.5, "jogArmedUntil" to 1.5), { HydraClaimView.fromJson(it) }, { it.toJson() })
    roundTrip("HydraClaimView required only", mapOf<String, Any?>("robotId" to 7L, "ownerUsername" to "text", "claimedAt" to 1.5, "expiresAt" to 1.5), { HydraClaimView.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraClients() {
    roundTrip("HydraClients full", mapOf<String, Any?>("clients" to listOf<Any?>(mapOf<String, Any?>("key" to "value"))), { HydraClients.fromJson(it) }, { it.toJson() })
    roundTrip("HydraClients required only", mapOf<String, Any?>("clients" to listOf<Any?>(mapOf<String, Any?>("key" to "value"))), { HydraClients.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraConnectionClient() {
    roundTrip("HydraConnectionClient full", mapOf<String, Any?>("schema_version" to "1.0", "id" to "text", "kind" to "studio", "user" to "text", "app_version" to "text", "origin" to "local", "two_factor" to true, "first_seen_utc" to "text", "last_seen_utc" to "text", "last_failure_utc" to "text", "active_sessions" to 7L, "logins_ok" to 7L, "logins_failed" to 7L, "ip" to "text", "agent" to "text"), { HydraConnectionClient.fromJson(it) }, { it.toJson() })
    roundTrip("HydraConnectionClient required only", mapOf<String, Any?>("schema_version" to "1.0", "id" to "text", "kind" to "studio", "first_seen_utc" to "text", "last_seen_utc" to "text", "active_sessions" to 7L, "logins_ok" to 7L, "logins_failed" to 7L), { HydraConnectionClient.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraConnectionClientList() {
    roundTrip("HydraConnectionClientList full", mapOf<String, Any?>("clients" to listOf<Any?>(mapOf<String, Any?>("schema_version" to "1.0", "id" to "text", "kind" to "studio", "user" to "text", "app_version" to "text", "origin" to "local", "two_factor" to true, "first_seen_utc" to "text", "last_seen_utc" to "text", "last_failure_utc" to "text", "active_sessions" to 7L, "logins_ok" to 7L, "logins_failed" to 7L, "ip" to "text", "agent" to "text"))), { HydraConnectionClientList.fromJson(it) }, { it.toJson() })
    roundTrip("HydraConnectionClientList required only", mapOf<String, Any?>("clients" to listOf<Any?>(mapOf<String, Any?>("schema_version" to "1.0", "id" to "text", "kind" to "studio", "first_seen_utc" to "text", "last_seen_utc" to "text", "active_sessions" to 7L, "logins_ok" to 7L, "logins_failed" to 7L))), { HydraConnectionClientList.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraConnectionEvent() {
    roundTrip("HydraConnectionEvent full", mapOf<String, Any?>("schema_version" to "1.0", "id" to 7L, "at_utc" to "text", "action" to "first_seen", "client_kind" to "studio", "client_id" to "text", "user" to "text", "origin" to "local", "two_factor" to true, "app_version" to "text", "ip" to "text", "agent" to "text"), { HydraConnectionEvent.fromJson(it) }, { it.toJson() })
    roundTrip("HydraConnectionEvent required only", mapOf<String, Any?>("schema_version" to "1.0", "id" to 7L, "at_utc" to "text", "action" to "first_seen", "client_kind" to "studio", "client_id" to "text"), { HydraConnectionEvent.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraConnectionEventList() {
    roundTrip("HydraConnectionEventList full", mapOf<String, Any?>("events" to listOf<Any?>(mapOf<String, Any?>("schema_version" to "1.0", "id" to 7L, "at_utc" to "text", "action" to "first_seen", "client_kind" to "studio", "client_id" to "text", "user" to "text", "origin" to "local", "two_factor" to true, "app_version" to "text", "ip" to "text", "agent" to "text"))), { HydraConnectionEventList.fromJson(it) }, { it.toJson() })
    roundTrip("HydraConnectionEventList required only", mapOf<String, Any?>("events" to listOf<Any?>(mapOf<String, Any?>("schema_version" to "1.0", "id" to 7L, "at_utc" to "text", "action" to "first_seen", "client_kind" to "studio", "client_id" to "text"))), { HydraConnectionEventList.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraDeviceTokenIssued() {
    roundTrip("HydraDeviceTokenIssued full", mapOf<String, Any?>("id" to "text", "name" to "text", "username" to "text", "createdAt" to "text", "expiresAt" to "text", "revokedAt" to "text", "lastUsedAt" to "text", "state" to "active", "token" to "text"), { HydraDeviceTokenIssued.fromJson(it) }, { it.toJson() })
    roundTrip("HydraDeviceTokenIssued required only", mapOf<String, Any?>("id" to "text", "name" to "text", "username" to "text", "createdAt" to "text", "expiresAt" to "text", "revokedAt" to "text", "lastUsedAt" to "text", "state" to "active", "token" to "text"), { HydraDeviceTokenIssued.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraDeviceTokenList() {
    roundTrip("HydraDeviceTokenList full", mapOf<String, Any?>("items" to listOf<Any?>(mapOf<String, Any?>("id" to "text", "name" to "text", "username" to "text", "createdAt" to "text", "expiresAt" to "text", "revokedAt" to "text", "lastUsedAt" to "text", "state" to "active"))), { HydraDeviceTokenList.fromJson(it) }, { it.toJson() })
    roundTrip("HydraDeviceTokenList required only", mapOf<String, Any?>("items" to listOf<Any?>(mapOf<String, Any?>("id" to "text", "name" to "text", "username" to "text", "createdAt" to "text", "expiresAt" to "text", "revokedAt" to "text", "lastUsedAt" to "text", "state" to "active"))), { HydraDeviceTokenList.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraDeviceTokenRevoked() {
    roundTrip("HydraDeviceTokenRevoked full", mapOf<String, Any?>("revoked" to true, "sessionsEnded" to 7L), { HydraDeviceTokenRevoked.fromJson(it) }, { it.toJson() })
    roundTrip("HydraDeviceTokenRevoked required only", mapOf<String, Any?>("revoked" to true, "sessionsEnded" to 7L), { HydraDeviceTokenRevoked.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraDeviceTokenView() {
    roundTrip("HydraDeviceTokenView full", mapOf<String, Any?>("id" to "text", "name" to "text", "username" to "text", "createdAt" to "text", "expiresAt" to "text", "revokedAt" to "text", "lastUsedAt" to "text", "state" to "active"), { HydraDeviceTokenView.fromJson(it) }, { it.toJson() })
    roundTrip("HydraDeviceTokenView required only", mapOf<String, Any?>("id" to "text", "name" to "text", "username" to "text", "createdAt" to "text", "expiresAt" to "text", "revokedAt" to "text", "lastUsedAt" to "text", "state" to "active"), { HydraDeviceTokenView.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraEcosystemHealth() {
    roundTrip("HydraEcosystemHealth full", mapOf<String, Any?>("schema_version" to "text", "generated_at_utc" to "text", "available" to true, "summary" to mapOf<String, Any?>("total" to 7L, "ok" to 7L, "degraded" to 7L, "down" to 7L, "unknown" to 7L, "drift" to 7L), "services" to listOf<Any?>(mapOf<String, Any?>("name" to "text", "family" to "text", "role" to "text", "state" to "text", "reason" to "text", "version_expected" to "text", "version_reported" to "text", "drift" to true, "last_seen_utc" to "text", "latency_ms" to 7L, "port" to 7L, "health_path" to "text", "systemd_unit" to "text", "active_state" to "text")), "certificate" to mapOf<String, Any?>("state" to "text", "not_after_utc" to "text", "days_left" to 7L, "warn_days" to 7L), "warnings" to listOf<Any?>(mapOf<String, Any?>("code" to "text", "service" to "text"))), { HydraEcosystemHealth.fromJson(it) }, { it.toJson() })
    roundTrip("HydraEcosystemHealth required only", mapOf<String, Any?>("schema_version" to "text", "generated_at_utc" to "text", "available" to true, "summary" to mapOf<String, Any?>("total" to 7L, "ok" to 7L, "degraded" to 7L, "down" to 7L, "unknown" to 7L, "drift" to 7L), "services" to listOf<Any?>(mapOf<String, Any?>("name" to "text", "family" to "text", "role" to "text", "state" to "text", "reason" to "text", "version_expected" to "text", "version_reported" to "text", "drift" to true, "last_seen_utc" to "text", "latency_ms" to 7L)), "certificate" to mapOf<String, Any?>(), "warnings" to listOf<Any?>(mapOf<String, Any?>("code" to "text"))), { HydraEcosystemHealth.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraEcosystemStatus() {
    roundTrip("HydraEcosystemStatus full", mapOf<String, Any?>("available" to true, "scannedAt" to "text", "projects" to listOf<Any?>(mapOf<String, Any?>("name" to "text", "role" to "text", "stack" to "text", "maturity" to "text", "family" to "text", "version" to "text", "deploymentTarget" to "text", "servicePort" to 7L, "serviceHealthPath" to "text", "serviceHost" to "text", "systemdUnit" to "text", "pid" to 7L, "activeState" to "text", "subState" to "text", "live" to true))), { HydraEcosystemStatus.fromJson(it) }, { it.toJson() })
    roundTrip("HydraEcosystemStatus required only", mapOf<String, Any?>("available" to true, "scannedAt" to "text", "projects" to listOf<Any?>(mapOf<String, Any?>("name" to "text"))), { HydraEcosystemStatus.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraError() {
    roundTrip("HydraError full", mapOf<String, Any?>("error" to "text"), { HydraError.fromJson(it) }, { it.toJson() })
    roundTrip("HydraError required only", mapOf<String, Any?>("error" to "text"), { HydraError.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraFleetUpdateReport() {
    roundTrip("HydraFleetUpdateReport full", mapOf<String, Any?>("schema" to "hydra-fleet-update/1", "id" to "text", "mode" to "plan", "state" to "planned", "startedAt" to "text", "updatedAt" to "text", "error" to "text", "stoppedAt" to "text", "requireSignedTags" to true, "disk" to mapOf<String, Any?>("rootFreeMb" to 7L, "workspaceFreeMb" to 7L), "services" to listOf<Any?>(mapOf<String, Any?>("name" to "text", "kind" to "repo", "repo" to "text", "installed" to "text", "latest" to "text", "action" to "update", "reason" to "text", "state" to "waiting", "step" to "", "substep" to "text", "substeps" to 7L, "detail" to "text", "error" to "text", "order" to 7L, "elapsedS" to 7L, "freeMb" to 7L, "needMb" to 7L, "unitRestored" to true, "log" to listOf<Any?>(mapOf<String, Any?>("at" to "text", "text" to "text"))))), { HydraFleetUpdateReport.fromJson(it) }, { it.toJson() })
    roundTrip("HydraFleetUpdateReport required only", mapOf<String, Any?>("schema" to "hydra-fleet-update/1", "id" to "text", "mode" to "plan", "state" to "planned", "startedAt" to "text", "updatedAt" to "text", "error" to "text", "stoppedAt" to "text", "requireSignedTags" to true, "disk" to mapOf<String, Any?>("rootFreeMb" to 7L, "workspaceFreeMb" to 7L), "services" to listOf<Any?>(mapOf<String, Any?>("name" to "text", "kind" to "repo", "repo" to "text", "installed" to "text", "latest" to "text", "action" to "update", "reason" to "text", "state" to "waiting", "step" to "", "detail" to "text", "error" to "text", "order" to 7L, "log" to listOf<Any?>(mapOf<String, Any?>("at" to "text", "text" to "text"))))), { HydraFleetUpdateReport.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraFleetUpdateRow() {
    roundTrip("HydraFleetUpdateRow full", mapOf<String, Any?>("name" to "text", "kind" to "repo", "repo" to "text", "installed" to "text", "latest" to "text", "action" to "update", "reason" to "text", "state" to "waiting", "step" to "", "substep" to "text", "substeps" to 7L, "detail" to "text", "error" to "text", "order" to 7L, "elapsedS" to 7L, "freeMb" to 7L, "needMb" to 7L, "unitRestored" to true, "log" to listOf<Any?>(mapOf<String, Any?>("at" to "text", "text" to "text"))), { HydraFleetUpdateRow.fromJson(it) }, { it.toJson() })
    roundTrip("HydraFleetUpdateRow required only", mapOf<String, Any?>("name" to "text", "kind" to "repo", "repo" to "text", "installed" to "text", "latest" to "text", "action" to "update", "reason" to "text", "state" to "waiting", "step" to "", "detail" to "text", "error" to "text", "order" to 7L, "log" to listOf<Any?>(mapOf<String, Any?>("at" to "text", "text" to "text"))), { HydraFleetUpdateRow.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraFleetUpdateStatus() {
    roundTrip("HydraFleetUpdateStatus full", mapOf<String, Any?>("applyEnabled" to true, "busy" to true, "report" to mapOf<String, Any?>("schema" to "hydra-fleet-update/1", "id" to "text", "mode" to "plan", "state" to "planned", "startedAt" to "text", "updatedAt" to "text", "error" to "text", "stoppedAt" to "text", "requireSignedTags" to true, "disk" to mapOf<String, Any?>("rootFreeMb" to 7L, "workspaceFreeMb" to 7L), "services" to listOf<Any?>(mapOf<String, Any?>("name" to "text", "kind" to "repo", "repo" to "text", "installed" to "text", "latest" to "text", "action" to "update", "reason" to "text", "state" to "waiting", "step" to "", "substep" to "text", "substeps" to 7L, "detail" to "text", "error" to "text", "order" to 7L, "elapsedS" to 7L, "freeMb" to 7L, "needMb" to 7L, "unitRestored" to true, "log" to listOf<Any?>(mapOf<String, Any?>("at" to "text", "text" to "text")))))), { HydraFleetUpdateStatus.fromJson(it) }, { it.toJson() })
    roundTrip("HydraFleetUpdateStatus required only", mapOf<String, Any?>("applyEnabled" to true, "busy" to true, "report" to mapOf<String, Any?>("schema" to "hydra-fleet-update/1", "id" to "text", "mode" to "plan", "state" to "planned", "startedAt" to "text", "updatedAt" to "text", "error" to "text", "stoppedAt" to "text", "requireSignedTags" to true, "disk" to mapOf<String, Any?>("rootFreeMb" to 7L, "workspaceFreeMb" to 7L), "services" to listOf<Any?>(mapOf<String, Any?>("name" to "text", "kind" to "repo", "repo" to "text", "installed" to "text", "latest" to "text", "action" to "update", "reason" to "text", "state" to "waiting", "step" to "", "detail" to "text", "error" to "text", "order" to 7L, "log" to listOf<Any?>(mapOf<String, Any?>("at" to "text", "text" to "text")))))), { HydraFleetUpdateStatus.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraGlobalStopReleased() {
    roundTrip("HydraGlobalStopReleased full", mapOf<String, Any?>("success" to true, "announced" to true), { HydraGlobalStopReleased.fromJson(it) }, { it.toJson() })
    roundTrip("HydraGlobalStopReleased required only", mapOf<String, Any?>("success" to true, "announced" to true), { HydraGlobalStopReleased.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraHealthReport() {
    roundTrip("HydraHealthReport full", mapOf<String, Any?>("schema_version" to "text", "state" to "text", "timestamp_utc" to "text", "checks" to mapOf<String, Any?>("key" to "value"), "service" to "text"), { HydraHealthReport.fromJson(it) }, { it.toJson() })
    roundTrip("HydraHealthReport required only", mapOf<String, Any?>("schema_version" to "text", "state" to "text", "timestamp_utc" to "text", "checks" to mapOf<String, Any?>("key" to "value")), { HydraHealthReport.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraHydraInfo() {
    roundTrip("HydraHydraInfo full", mapOf<String, Any?>("schema_version" to "text", "product" to "text", "remoteApiVersion" to 7L, "appVersion" to "text", "hostname" to "text", "controllerCount" to 7L, "robotCount" to 7L, "uptimeSeconds" to 7L, "addresses" to listOf<Any?>("text")), { HydraHydraInfo.fromJson(it) }, { it.toJson() })
    roundTrip("HydraHydraInfo required only", mapOf<String, Any?>("schema_version" to "text", "product" to "text", "remoteApiVersion" to 7L, "appVersion" to "text", "hostname" to "text", "controllerCount" to 7L, "robotCount" to 7L, "uptimeSeconds" to 7L), { HydraHydraInfo.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraInfoTicket() {
    roundTrip("HydraInfoTicket full", mapOf<String, Any?>("ticket" to "text", "expiresInSeconds" to 7L), { HydraInfoTicket.fromJson(it) }, { it.toJson() })
    roundTrip("HydraInfoTicket required only", mapOf<String, Any?>("ticket" to "text", "expiresInSeconds" to 7L), { HydraInfoTicket.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraJwksDocument() {
    roundTrip("HydraJwksDocument full", mapOf<String, Any?>("keys" to listOf<Any?>(mapOf<String, Any?>("kty" to "OKP", "crv" to "Ed25519", "x" to "text", "kid" to "text", "use" to "sig", "alg" to "EdDSA"))), { HydraJwksDocument.fromJson(it) }, { it.toJson() })
    roundTrip("HydraJwksDocument required only", mapOf<String, Any?>("keys" to listOf<Any?>(mapOf<String, Any?>("kty" to "OKP", "crv" to "Ed25519", "x" to "text", "kid" to "text", "use" to "sig", "alg" to "EdDSA"))), { HydraJwksDocument.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraJwtKeyRotated() {
    roundTrip("HydraJwtKeyRotated full", mapOf<String, Any?>("success" to true, "kid" to "text", "algorithm" to "HS256", "keys" to listOf<Any?>(mapOf<String, Any?>("kid" to "text", "createdAt" to 7L, "retiredAt" to 7L, "active" to true, "acceptedUntil" to 7L)), "jwksPath" to "text"), { HydraJwtKeyRotated.fromJson(it) }, { it.toJson() })
    roundTrip("HydraJwtKeyRotated required only", mapOf<String, Any?>("success" to true, "kid" to "text", "algorithm" to "HS256", "keys" to listOf<Any?>(mapOf<String, Any?>("kid" to "text", "createdAt" to 7L, "retiredAt" to 7L, "active" to true, "acceptedUntil" to 7L)), "jwksPath" to "text"), { HydraJwtKeyRotated.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraJwtKeys() {
    roundTrip("HydraJwtKeys full", mapOf<String, Any?>("algorithm" to "HS256", "keys" to listOf<Any?>(mapOf<String, Any?>("kid" to "text", "createdAt" to 7L, "retiredAt" to 7L, "active" to true, "acceptedUntil" to 7L)), "jwksPath" to "text"), { HydraJwtKeys.fromJson(it) }, { it.toJson() })
    roundTrip("HydraJwtKeys required only", mapOf<String, Any?>("algorithm" to "HS256", "keys" to listOf<Any?>(mapOf<String, Any?>("kid" to "text", "createdAt" to 7L, "retiredAt" to 7L, "active" to true, "acceptedUntil" to 7L)), "jwksPath" to "text"), { HydraJwtKeys.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraLiveActivityRegistered() {
    roundTrip("HydraLiveActivityRegistered full", mapOf<String, Any?>("registered" to true), { HydraLiveActivityRegistered.fromJson(it) }, { it.toJson() })
    roundTrip("HydraLiveActivityRegistered required only", mapOf<String, Any?>("registered" to true), { HydraLiveActivityRegistered.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraLiveActivityRemoved() {
    roundTrip("HydraLiveActivityRemoved full", mapOf<String, Any?>("removed" to true), { HydraLiveActivityRemoved.fromJson(it) }, { it.toJson() })
    roundTrip("HydraLiveActivityRemoved required only", mapOf<String, Any?>("removed" to true), { HydraLiveActivityRemoved.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraLogLines() {
    roundTrip("HydraLogLines full", mapOf<String, Any?>("lines" to listOf<Any?>("text")), { HydraLogLines.fromJson(it) }, { it.toJson() })
    roundTrip("HydraLogLines required only", mapOf<String, Any?>("lines" to listOf<Any?>("text")), { HydraLogLines.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraLoginResult() {
    roundTrip("HydraLoginResult full", mapOf<String, Any?>("success" to true, "token" to "text", "refreshToken" to "text", "role" to "text"), { HydraLoginResult.fromJson(it) }, { it.toJson() })
    roundTrip("HydraLoginResult required only", mapOf<String, Any?>("success" to true, "token" to "text", "refreshToken" to "text", "role" to "text"), { HydraLoginResult.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraMaintenanceOutcome() {
    roundTrip("HydraMaintenanceOutcome full", mapOf<String, Any?>("ok" to true, "action" to "status", "exitCode" to 7L, "timedOut" to true, "result" to "sample", "message" to "text"), { HydraMaintenanceOutcome.fromJson(it) }, { it.toJson() })
    roundTrip("HydraMaintenanceOutcome required only", mapOf<String, Any?>("ok" to true, "action" to "status", "exitCode" to 7L, "timedOut" to true, "result" to "sample", "message" to "text"), { HydraMaintenanceOutcome.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraModelList() {
    roundTrip("HydraModelList full", mapOf<String, Any?>("models" to listOf<Any?>(mapOf<String, Any?>("key" to "value"))), { HydraModelList.fromJson(it) }, { it.toJson() })
    roundTrip("HydraModelList required only", mapOf<String, Any?>("models" to listOf<Any?>(mapOf<String, Any?>("key" to "value"))), { HydraModelList.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraModelSubmitted() {
    roundTrip("HydraModelSubmitted full", mapOf<String, Any?>("success" to true, "slug" to "text"), { HydraModelSubmitted.fromJson(it) }, { it.toJson() })
    roundTrip("HydraModelSubmitted required only", mapOf<String, Any?>("success" to true, "slug" to "text"), { HydraModelSubmitted.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraNodeHealth() {
    roundTrip("HydraNodeHealth full", mapOf<String, Any?>("online" to true, "slot" to 7L, "heard" to true, "ageMs" to 7L, "sequence" to 7L, "flags" to 7L, "flagNames" to listOf<Any?>("text"), "txErrors" to 7L, "rxErrors" to 7L, "stalls" to 7L, "uptimeS" to 7L, "source" to "brain-health"), { HydraNodeHealth.fromJson(it) }, { it.toJson() })
    roundTrip("HydraNodeHealth required only", mapOf<String, Any?>("online" to true, "slot" to 7L, "heard" to true, "source" to "brain-health"), { HydraNodeHealth.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraOperatorPresence() {
    roundTrip("HydraOperatorPresence full", mapOf<String, Any?>("state" to "unknown", "lastSequence" to 7L, "secondsSinceBeat" to 7L, "action" to "slow", "timeoutSeconds" to 1.5, "degradedRobots" to listOf<Any?>(7L)), { HydraOperatorPresence.fromJson(it) }, { it.toJson() })
    roundTrip("HydraOperatorPresence required only", mapOf<String, Any?>("state" to "unknown", "lastSequence" to 7L, "secondsSinceBeat" to 7L, "action" to "slow", "timeoutSeconds" to 1.5, "degradedRobots" to listOf<Any?>(7L)), { HydraOperatorPresence.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraOperatorPresenceAck() {
    roundTrip("HydraOperatorPresenceAck full", mapOf<String, Any?>("accepted" to true, "duplicate" to true, "stale" to true, "state" to "present", "sequence" to 7L, "action" to "slow", "timeoutSeconds" to 1.5), { HydraOperatorPresenceAck.fromJson(it) }, { it.toJson() })
    roundTrip("HydraOperatorPresenceAck required only", mapOf<String, Any?>("accepted" to true, "duplicate" to true, "stale" to true, "state" to "present", "sequence" to 7L, "action" to "slow", "timeoutSeconds" to 1.5), { HydraOperatorPresenceAck.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraPtzResult() {
    roundTrip("HydraPtzResult full", mapOf<String, Any?>("ok" to true), { HydraPtzResult.fromJson(it) }, { it.toJson() })
    roundTrip("HydraPtzResult required only", mapOf<String, Any?>("ok" to true), { HydraPtzResult.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraPushDeviceRegistered() {
    roundTrip("HydraPushDeviceRegistered full", mapOf<String, Any?>("registered" to true), { HydraPushDeviceRegistered.fromJson(it) }, { it.toJson() })
    roundTrip("HydraPushDeviceRegistered required only", mapOf<String, Any?>("registered" to true), { HydraPushDeviceRegistered.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraPushDeviceRemoved() {
    roundTrip("HydraPushDeviceRemoved full", mapOf<String, Any?>("removed" to true), { HydraPushDeviceRemoved.fromJson(it) }, { it.toJson() })
    roundTrip("HydraPushDeviceRemoved required only", mapOf<String, Any?>("removed" to true), { HydraPushDeviceRemoved.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraPushStatus() {
    roundTrip("HydraPushStatus full", mapOf<String, Any?>("enabled" to true, "configured" to true, "problem" to "missing", "devices" to 7L, "sandbox" to true, "events" to mapOf<String, Any?>("jobFinished" to true, "globalStop" to true), "liveActivity" to mapOf<String, Any?>("enabled" to true, "level" to "status", "activities" to 7L)), { HydraPushStatus.fromJson(it) }, { it.toJson() })
    roundTrip("HydraPushStatus required only", mapOf<String, Any?>("enabled" to true, "configured" to true, "problem" to "missing", "devices" to 7L, "sandbox" to true, "events" to mapOf<String, Any?>("jobFinished" to true, "globalStop" to true)), { HydraPushStatus.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraReachable() {
    roundTrip("HydraReachable full", mapOf<String, Any?>("reachable" to true), { HydraReachable.fromJson(it) }, { it.toJson() })
    roundTrip("HydraReachable required only", mapOf<String, Any?>("reachable" to true), { HydraReachable.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraRobotLiveness() {
    roundTrip("HydraRobotLiveness full", mapOf<String, Any?>("schema_version" to "text", "stale_after_s" to 7L, "robots" to listOf<Any?>(mapOf<String, Any?>("controller_id" to "text", "robot_id" to 7L, "state" to "text", "last_update_utc" to "text", "age_s" to 7L, "source" to "text"))), { HydraRobotLiveness.fromJson(it) }, { it.toJson() })
    roundTrip("HydraRobotLiveness required only", mapOf<String, Any?>("schema_version" to "text", "stale_after_s" to 7L, "robots" to listOf<Any?>(mapOf<String, Any?>("controller_id" to "text", "robot_id" to 7L, "state" to "text"))), { HydraRobotLiveness.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraRulConfig() {
    roundTrip("HydraRulConfig full", mapOf<String, Any?>("enabled" to true, "maxPoints" to 7L, "timeoutMs" to 7L), { HydraRulConfig.fromJson(it) }, { it.toJson() })
    roundTrip("HydraRulConfig required only", mapOf<String, Any?>("enabled" to true, "maxPoints" to 7L, "timeoutMs" to 7L), { HydraRulConfig.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraSafetyLimitsConfig() {
    roundTrip("HydraSafetyLimitsConfig full", mapOf<String, Any?>("jog" to mapOf<String, Any?>("armRequired" to true, "armTtlMs" to 1.5, "default" to mapOf<String, Any?>("maxAmount" to 1.5, "maxAbsolute" to 1.5), "models" to mapOf<String, Any?>("extraKey" to mapOf<String, Any?>("maxAmount" to 1.5, "maxAbsolute" to 1.5))), "temperature" to mapOf<String, Any?>("default" to mapOf<String, Any?>("bedMaxC" to 1.5), "models" to mapOf<String, Any?>("extraKey" to mapOf<String, Any?>("bedMaxC" to 1.5))), "claims" to mapOf<String, Any?>("requireControllerId" to true), "audit" to mapOf<String, Any?>("enabled" to true, "motionIntervalSeconds" to 1.5)), { HydraSafetyLimitsConfig.fromJson(it) }, { it.toJson() })
    roundTrip("HydraSafetyLimitsConfig required only", mapOf<String, Any?>("jog" to mapOf<String, Any?>("armRequired" to true, "armTtlMs" to 1.5, "default" to mapOf<String, Any?>("maxAmount" to 1.5, "maxAbsolute" to 1.5), "models" to mapOf<String, Any?>()), "temperature" to mapOf<String, Any?>("default" to mapOf<String, Any?>("bedMaxC" to 1.5), "models" to mapOf<String, Any?>()), "claims" to mapOf<String, Any?>("requireControllerId" to true), "audit" to mapOf<String, Any?>("enabled" to true, "motionIntervalSeconds" to 1.5)), { HydraSafetyLimitsConfig.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraSafetyLimitsView() {
    roundTrip("HydraSafetyLimitsView full", mapOf<String, Any?>("limits" to mapOf<String, Any?>("jog" to mapOf<String, Any?>("armRequired" to true, "armTtlMs" to 1.5, "default" to mapOf<String, Any?>("maxAmount" to 1.5, "maxAbsolute" to 1.5), "models" to mapOf<String, Any?>("extraKey" to mapOf<String, Any?>("maxAmount" to 1.5, "maxAbsolute" to 1.5))), "temperature" to mapOf<String, Any?>("default" to mapOf<String, Any?>("bedMaxC" to 1.5), "models" to mapOf<String, Any?>("extraKey" to mapOf<String, Any?>("bedMaxC" to 1.5))), "claims" to mapOf<String, Any?>("requireControllerId" to true), "audit" to mapOf<String, Any?>("enabled" to true, "motionIntervalSeconds" to 1.5)), "defaults" to mapOf<String, Any?>("jog" to mapOf<String, Any?>("armRequired" to true, "armTtlMs" to 1.5, "default" to mapOf<String, Any?>("maxAmount" to 1.5, "maxAbsolute" to 1.5), "models" to mapOf<String, Any?>("extraKey" to mapOf<String, Any?>("maxAmount" to 1.5, "maxAbsolute" to 1.5))), "temperature" to mapOf<String, Any?>("default" to mapOf<String, Any?>("bedMaxC" to 1.5), "models" to mapOf<String, Any?>("extraKey" to mapOf<String, Any?>("bedMaxC" to 1.5))), "claims" to mapOf<String, Any?>("requireControllerId" to true), "audit" to mapOf<String, Any?>("enabled" to true, "motionIntervalSeconds" to 1.5)), "hardLimits" to mapOf<String, Any?>("extraKey" to "extra"), "robot" to mapOf<String, Any?>("id" to 7L, "model" to "text", "jog" to mapOf<String, Any?>("maxAmount" to 1.5, "maxAbsolute" to 1.5), "temperature" to mapOf<String, Any?>("bedMaxC" to 1.5), "jogArmedUntil" to 1.5)), { HydraSafetyLimitsView.fromJson(it) }, { it.toJson() })
    roundTrip("HydraSafetyLimitsView required only", mapOf<String, Any?>("limits" to mapOf<String, Any?>("jog" to mapOf<String, Any?>("armRequired" to true, "armTtlMs" to 1.5, "default" to mapOf<String, Any?>("maxAmount" to 1.5, "maxAbsolute" to 1.5), "models" to mapOf<String, Any?>()), "temperature" to mapOf<String, Any?>("default" to mapOf<String, Any?>("bedMaxC" to 1.5), "models" to mapOf<String, Any?>()), "claims" to mapOf<String, Any?>("requireControllerId" to true), "audit" to mapOf<String, Any?>("enabled" to true, "motionIntervalSeconds" to 1.5)), "defaults" to mapOf<String, Any?>("jog" to mapOf<String, Any?>("armRequired" to true, "armTtlMs" to 1.5, "default" to mapOf<String, Any?>("maxAmount" to 1.5, "maxAbsolute" to 1.5), "models" to mapOf<String, Any?>()), "temperature" to mapOf<String, Any?>("default" to mapOf<String, Any?>("bedMaxC" to 1.5), "models" to mapOf<String, Any?>()), "claims" to mapOf<String, Any?>("requireControllerId" to true), "audit" to mapOf<String, Any?>("enabled" to true, "motionIntervalSeconds" to 1.5)), "hardLimits" to mapOf<String, Any?>()), { HydraSafetyLimitsView.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraSelfUpdateItem() {
    roundTrip("HydraSelfUpdateItem full", mapOf<String, Any?>("id" to "server", "repo" to "text", "installed" to "text", "previous" to "text", "latest" to "text", "state" to "current", "signedPackage" to true), { HydraSelfUpdateItem.fromJson(it) }, { it.toJson() })
    roundTrip("HydraSelfUpdateItem required only", mapOf<String, Any?>("id" to "server", "repo" to "text", "installed" to "text", "previous" to "text", "latest" to "text", "state" to "current", "signedPackage" to true), { HydraSelfUpdateItem.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraSelfUpdateJob() {
    roundTrip("HydraSelfUpdateJob full", mapOf<String, Any?>("id" to "text", "action" to "apply", "component" to "server", "state" to "checking", "fromVersion" to "text", "targetVersion" to "text", "startedAt" to "text", "updatedAt" to "text", "error" to "no_release", "detail" to "text", "packageName" to "text", "log" to listOf<Any?>(mapOf<String, Any?>("at" to "text", "step" to "checking", "text" to "text")), "by" to "text"), { HydraSelfUpdateJob.fromJson(it) }, { it.toJson() })
    roundTrip("HydraSelfUpdateJob required only", mapOf<String, Any?>("id" to "text", "action" to "apply", "component" to "server", "state" to "checking", "fromVersion" to "text", "targetVersion" to "text", "startedAt" to "text", "updatedAt" to "text", "error" to "no_release", "detail" to "text", "log" to listOf<Any?>(mapOf<String, Any?>("at" to "text", "step" to "checking", "text" to "text")), "by" to "text"), { HydraSelfUpdateJob.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraSelfUpdateStatus() {
    roundTrip("HydraSelfUpdateStatus full", mapOf<String, Any?>("checkedAt" to "text", "owner" to "text", "rateLimited" to true, "items" to listOf<Any?>(mapOf<String, Any?>("id" to "server", "repo" to "text", "installed" to "text", "previous" to "text", "latest" to "text", "state" to "current", "signedPackage" to true)), "applyEnabled" to true, "job" to mapOf<String, Any?>("id" to "text", "action" to "apply", "component" to "server", "state" to "checking", "fromVersion" to "text", "targetVersion" to "text", "startedAt" to "text", "updatedAt" to "text", "error" to "no_release", "detail" to "text", "packageName" to "text", "log" to listOf<Any?>(mapOf<String, Any?>("at" to "text", "step" to "checking", "text" to "text")), "by" to "text")), { HydraSelfUpdateStatus.fromJson(it) }, { it.toJson() })
    roundTrip("HydraSelfUpdateStatus required only", mapOf<String, Any?>("checkedAt" to "text", "owner" to "text", "rateLimited" to true, "items" to listOf<Any?>(mapOf<String, Any?>("id" to "server", "repo" to "text", "installed" to "text", "previous" to "text", "latest" to "text", "state" to "current", "signedPackage" to true)), "applyEnabled" to true, "job" to mapOf<String, Any?>("id" to "text", "action" to "apply", "component" to "server", "state" to "checking", "fromVersion" to "text", "targetVersion" to "text", "startedAt" to "text", "updatedAt" to "text", "error" to "no_release", "detail" to "text", "log" to listOf<Any?>(mapOf<String, Any?>("at" to "text", "step" to "checking", "text" to "text")), "by" to "text")), { HydraSelfUpdateStatus.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraServerConfig() {
    roundTrip("HydraServerConfig full", mapOf<String, Any?>("port" to 7L, "pendingPort" to 7L, "extraKey" to "extra"), { HydraServerConfig.fromJson(it) }, { it.toJson() })
    roundTrip("HydraServerConfig required only", mapOf<String, Any?>("port" to 7L, "pendingPort" to 7L), { HydraServerConfig.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraServiceIdentityStatus() {
    roundTrip("HydraServiceIdentityStatus full", mapOf<String, Any?>("enabled" to true, "source" to "env", "locked" to true, "key" to "usable", "state" to "presenting", "services" to listOf<Any?>(mapOf<String, Any?>("name" to "text", "support" to "accepts")), "order" to listOf<Any?>("server_first")), { HydraServiceIdentityStatus.fromJson(it) }, { it.toJson() })
    roundTrip("HydraServiceIdentityStatus required only", mapOf<String, Any?>("enabled" to true, "source" to "env", "locked" to true, "key" to "usable", "state" to "presenting", "services" to listOf<Any?>(mapOf<String, Any?>("name" to "text", "support" to "accepts")), "order" to listOf<Any?>("server_first")), { HydraServiceIdentityStatus.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraSettings() {
    roundTrip("HydraSettings full", mapOf<String, Any?>("controllers" to listOf<Any?>(mapOf<String, Any?>("key" to "value"))), { HydraSettings.fromJson(it) }, { it.toJson() })
    roundTrip("HydraSettings required only", mapOf<String, Any?>(), { HydraSettings.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraStopAllResult() {
    roundTrip("HydraStopAllResult full", mapOf<String, Any?>("success" to true, "stoppedCount" to 7L, "failedCount" to 7L, "persisted" to true, "announced" to true, "robots" to listOf<Any?>(mapOf<String, Any?>("robotId" to 7L, "controllerId" to "text", "name" to "text", "stopped" to true, "valvesOff" to 7L, "pumpsOff" to 7L, "reservedBy" to "text", "error" to "text"))), { HydraStopAllResult.fromJson(it) }, { it.toJson() })
    roundTrip("HydraStopAllResult required only", mapOf<String, Any?>("success" to true, "stoppedCount" to 7L, "failedCount" to 7L, "persisted" to true, "robots" to listOf<Any?>(mapOf<String, Any?>("robotId" to 7L, "controllerId" to "text", "name" to "text", "stopped" to true, "valvesOff" to 7L, "pumpsOff" to 7L))), { HydraStopAllResult.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraSuccess() {
    roundTrip("HydraSuccess full", mapOf<String, Any?>("success" to true), { HydraSuccess.fromJson(it) }, { it.toJson() })
    roundTrip("HydraSuccess required only", mapOf<String, Any?>("success" to true), { HydraSuccess.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraSystemMetrics() {
    roundTrip("HydraSystemMetrics full", mapOf<String, Any?>("cpu_load" to 1.5, "memory_usage" to 1.5, "temp" to 1.5, "temp_is_real" to true, "rp1_temp" to 1.5, "uptime" to 1.5, "network" to mapOf<String, Any?>("key" to "value")), { HydraSystemMetrics.fromJson(it) }, { it.toJson() })
    roundTrip("HydraSystemMetrics required only", mapOf<String, Any?>("cpu_load" to 1.5, "memory_usage" to 1.5, "temp" to 1.5, "temp_is_real" to true, "rp1_temp" to 1.5, "uptime" to 1.5, "network" to mapOf<String, Any?>("key" to "value")), { HydraSystemMetrics.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraToolArmResetResult() {
    roundTrip("HydraToolArmResetResult full", mapOf<String, Any?>("success" to true, "robot" to "text", "toolId" to 7L), { HydraToolArmResetResult.fromJson(it) }, { it.toJson() })
    roundTrip("HydraToolArmResetResult required only", mapOf<String, Any?>("success" to true, "robot" to "text", "toolId" to 7L), { HydraToolArmResetResult.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraToolArmsReport() {
    roundTrip("HydraToolArmsReport full", mapOf<String, Any?>("schema_version" to "text", "ttlSeconds" to 1.5, "arms" to listOf<Any?>(mapOf<String, Any?>("robot" to "text", "toolId" to 7L, "armed" to true, "by" to "text", "seq" to 7L, "ageSeconds" to 1.5, "stale" to true)), "armedCount" to 7L, "staleCount" to 7L), { HydraToolArmsReport.fromJson(it) }, { it.toJson() })
    roundTrip("HydraToolArmsReport required only", mapOf<String, Any?>("schema_version" to "text", "ttlSeconds" to 1.5, "arms" to listOf<Any?>(mapOf<String, Any?>("robot" to "text", "toolId" to 7L, "armed" to true, "seq" to 7L, "ageSeconds" to 1.5, "stale" to true)), "armedCount" to 7L, "staleCount" to 7L), { HydraToolArmsReport.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraTotpConfirmed() {
    roundTrip("HydraTotpConfirmed full", mapOf<String, Any?>("success" to true, "recoveryCodes" to listOf<Any?>("text")), { HydraTotpConfirmed.fromJson(it) }, { it.toJson() })
    roundTrip("HydraTotpConfirmed required only", mapOf<String, Any?>("success" to true, "recoveryCodes" to listOf<Any?>("text")), { HydraTotpConfirmed.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraTotpEnrolment() {
    roundTrip("HydraTotpEnrolment full", mapOf<String, Any?>("success" to true, "secret" to "text", "uri" to "text"), { HydraTotpEnrolment.fromJson(it) }, { it.toJson() })
    roundTrip("HydraTotpEnrolment required only", mapOf<String, Any?>("success" to true, "secret" to "text", "uri" to "text"), { HydraTotpEnrolment.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraTotpStatus() {
    roundTrip("HydraTotpStatus full", mapOf<String, Any?>("enabled" to true, "recoveryLeft" to 7L), { HydraTotpStatus.fromJson(it) }, { it.toJson() })
    roundTrip("HydraTotpStatus required only", mapOf<String, Any?>("enabled" to true, "recoveryLeft" to 7L), { HydraTotpStatus.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraUpdateItem() {
    roundTrip("HydraUpdateItem full", mapOf<String, Any?>("name" to "text", "family" to "text", "installed" to "text", "latest" to "text", "state" to "current"), { HydraUpdateItem.fromJson(it) }, { it.toJson() })
    roundTrip("HydraUpdateItem required only", mapOf<String, Any?>("name" to "text", "family" to "text", "installed" to "text", "latest" to "text", "state" to "current"), { HydraUpdateItem.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraUpdateManifestVerdict() {
    roundTrip("HydraUpdateManifestVerdict full", mapOf<String, Any?>("accepted" to true, "code" to "ok", "key_id" to "text", "require_asymmetric_signature" to true), { HydraUpdateManifestVerdict.fromJson(it) }, { it.toJson() })
    roundTrip("HydraUpdateManifestVerdict required only", mapOf<String, Any?>("accepted" to true, "code" to "ok", "key_id" to "text", "require_asymmetric_signature" to true), { HydraUpdateManifestVerdict.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraUpdateReport() {
    roundTrip("HydraUpdateReport full", mapOf<String, Any?>("checkedAt" to "text", "owner" to "text", "rateLimited" to true, "items" to listOf<Any?>(mapOf<String, Any?>("name" to "text", "family" to "text", "installed" to "text", "latest" to "text", "state" to "current"))), { HydraUpdateReport.fromJson(it) }, { it.toJson() })
    roundTrip("HydraUpdateReport required only", mapOf<String, Any?>("checkedAt" to "text", "owner" to "text", "rateLimited" to true, "items" to listOf<Any?>(mapOf<String, Any?>("name" to "text", "family" to "text", "installed" to "text", "latest" to "text", "state" to "current"))), { HydraUpdateReport.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraUsbDevices() {
    roundTrip("HydraUsbDevices full", mapOf<String, Any?>("devices" to listOf<Any?>(mapOf<String, Any?>("key" to "value"))), { HydraUsbDevices.fromJson(it) }, { it.toJson() })
    roundTrip("HydraUsbDevices required only", mapOf<String, Any?>("devices" to listOf<Any?>(mapOf<String, Any?>("key" to "value"))), { HydraUsbDevices.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraUserList() {
    roundTrip("HydraUserList full", mapOf<String, Any?>("users" to listOf<Any?>(mapOf<String, Any?>("key" to "value"))), { HydraUserList.fromJson(it) }, { it.toJson() })
    roundTrip("HydraUserList required only", mapOf<String, Any?>("users" to listOf<Any?>(mapOf<String, Any?>("key" to "value"))), { HydraUserList.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraVoiceConfirmResult() {
    roundTrip("HydraVoiceConfirmResult full", mapOf<String, Any?>("type" to "confirmation_result", "status" to "confirmed", "requestId" to "text", "intent" to mapOf<String, Any?>("key" to "value"), "subject" to "text", "verified" to true, "extraKey" to "extra"), { HydraVoiceConfirmResult.fromJson(it) }, { it.toJson() })
    roundTrip("HydraVoiceConfirmResult required only", mapOf<String, Any?>("type" to "confirmation_result", "status" to "confirmed", "verified" to true), { HydraVoiceConfirmResult.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraVoiceReply() {
    roundTrip("HydraVoiceReply full", mapOf<String, Any?>("type" to "assistant_reply", "requestId" to "text", "text" to "text", "level" to "text", "speak" to true, "requiresConfirmation" to true, "visualState" to "text", "intent" to mapOf<String, Any?>("key" to "value"), "interpretation" to mapOf<String, Any?>("key" to "value"), "messageCode" to "text", "messageParams" to mapOf<String, Any?>("key" to "value"), "textLanguage" to "text", "confirmationToken" to "text", "confirmationValiditySeconds" to 1.5), { HydraVoiceReply.fromJson(it) }, { it.toJson() })
    roundTrip("HydraVoiceReply required only", mapOf<String, Any?>("type" to "assistant_reply", "requestId" to "text", "text" to "text", "level" to "text", "speak" to true, "requiresConfirmation" to true), { HydraVoiceReply.fromJson(it) }, { it.toJson() })
}

private fun roundTripHydraWatchStatus() {
    roundTrip("HydraWatchStatus full", mapOf<String, Any?>("type" to "system_status", "headline" to "text", "detail" to "text", "level" to "NOMINAL", "speak" to true), { HydraWatchStatus.fromJson(it) }, { it.toJson() })
    roundTrip("HydraWatchStatus required only", mapOf<String, Any?>("type" to "system_status", "headline" to "text", "detail" to "text", "level" to "NOMINAL", "speak" to true), { HydraWatchStatus.fromJson(it) }, { it.toJson() })
}

/** Runs every round trip and returns the failures (empty when all pass). */
fun roundTripAll(): List<String> {
    failures.clear()
    roundTripHydraAuditEntry()
    roundTripHydraAuditReport()
    roundTripHydraAuditVerification()
    roundTripHydraBluetoothScan()
    roundTripHydraBridgeCommandAccepted()
    roundTripHydraBridgeList()
    roundTripHydraBridgeState()
    roundTripHydraCameraCapture()
    roundTripHydraCameraMediaList()
    roundTripHydraCanotaFlash()
    roundTripHydraClaimList()
    roundTripHydraClaimView()
    roundTripHydraClients()
    roundTripHydraConnectionClient()
    roundTripHydraConnectionClientList()
    roundTripHydraConnectionEvent()
    roundTripHydraConnectionEventList()
    roundTripHydraDeviceTokenIssued()
    roundTripHydraDeviceTokenList()
    roundTripHydraDeviceTokenRevoked()
    roundTripHydraDeviceTokenView()
    roundTripHydraEcosystemHealth()
    roundTripHydraEcosystemStatus()
    roundTripHydraError()
    roundTripHydraFleetUpdateReport()
    roundTripHydraFleetUpdateRow()
    roundTripHydraFleetUpdateStatus()
    roundTripHydraGlobalStopReleased()
    roundTripHydraHealthReport()
    roundTripHydraHydraInfo()
    roundTripHydraInfoTicket()
    roundTripHydraJwksDocument()
    roundTripHydraJwtKeyRotated()
    roundTripHydraJwtKeys()
    roundTripHydraLiveActivityRegistered()
    roundTripHydraLiveActivityRemoved()
    roundTripHydraLogLines()
    roundTripHydraLoginResult()
    roundTripHydraMaintenanceOutcome()
    roundTripHydraModelList()
    roundTripHydraModelSubmitted()
    roundTripHydraNodeHealth()
    roundTripHydraOperatorPresence()
    roundTripHydraOperatorPresenceAck()
    roundTripHydraPtzResult()
    roundTripHydraPushDeviceRegistered()
    roundTripHydraPushDeviceRemoved()
    roundTripHydraPushStatus()
    roundTripHydraReachable()
    roundTripHydraRobotLiveness()
    roundTripHydraRulConfig()
    roundTripHydraSafetyLimitsConfig()
    roundTripHydraSafetyLimitsView()
    roundTripHydraSelfUpdateItem()
    roundTripHydraSelfUpdateJob()
    roundTripHydraSelfUpdateStatus()
    roundTripHydraServerConfig()
    roundTripHydraServiceIdentityStatus()
    roundTripHydraSettings()
    roundTripHydraStopAllResult()
    roundTripHydraSuccess()
    roundTripHydraSystemMetrics()
    roundTripHydraToolArmResetResult()
    roundTripHydraToolArmsReport()
    roundTripHydraTotpConfirmed()
    roundTripHydraTotpEnrolment()
    roundTripHydraTotpStatus()
    roundTripHydraUpdateItem()
    roundTripHydraUpdateManifestVerdict()
    roundTripHydraUpdateReport()
    roundTripHydraUsbDevices()
    roundTripHydraUserList()
    roundTripHydraVoiceConfirmResult()
    roundTripHydraVoiceReply()
    roundTripHydraWatchStatus()
    return failures.toList()
}
const val ROUND_TRIP_CLASSES: Int = 75
