// Generated from the server contract by tools/generate_clients.py. Do not edit.

@file:Suppress("UNCHECKED_CAST", "unused")

package hydra.umc.client

// The transport hands back the decoded JSON model: Map, List, String, Long, Double, Boolean or null. Every object of the
// contract is a data class with fromJson (reads that model) and toJson (writes it again); no JSON library is needed.

typealias HydraCameraProcessStatus = Map<String, HydraCameraProcessStatusValue>

typealias HydraPassthrough = Map<String, Any?>

typealias HydraSupervisorSnapshot = Map<String, Any?>

/** One line of the audit record: the hash chain (seq, prev, hash) around the event. The keys of an event the server adds later are kept. */
data class HydraAuditEntry(
    val seq: Long,
    val ts: String,
    val prev: String,
    val hash: String,
    /** Short stable name of the event: claim, release, force-claim, force-release, safety-limits, jog-arm, stop-all, table-move... */
    val type: String,
    val outcome: String,
    /** The id of the account (any JSON value). */
    val userId: Any? = null,
    val username: String? = null,
    val controllerId: String? = null,
    val ip: String? = null,
    val robotId: Long? = null,
    val detail: Map<String, Any?>? = null,
    /** The keys the contract does not list, kept as they came. */
    val additionalProperties: Map<String, Any?> = emptyMap(),
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut.putAll(additionalProperties)
        jsonOut["seq"] = seq
        jsonOut["ts"] = ts
        jsonOut["prev"] = prev
        jsonOut["hash"] = hash
        jsonOut["type"] = type
        jsonOut["outcome"] = outcome
        if (userId != null) jsonOut["userId"] = userId
        if (username != null) jsonOut["username"] = username
        if (controllerId != null) jsonOut["controllerId"] = controllerId
        if (ip != null) jsonOut["ip"] = ip
        if (robotId != null) jsonOut["robotId"] = robotId
        if (detail != null) jsonOut["detail"] = detail
        return jsonOut
    }

    companion object {
        private val knownKeys: Set<String> = setOf("seq", "ts", "prev", "hash", "type", "outcome", "userId", "username", "controllerId", "ip", "robotId", "detail")

        fun fromJson(json: Map<String, Any?>): HydraAuditEntry = HydraAuditEntry(
            seq = (json["seq"] as Number).toLong(),
            ts = json["ts"] as String,
            prev = json["prev"] as String,
            hash = json["hash"] as String,
            type = json["type"] as String,
            outcome = json["outcome"] as String,
            userId = json["userId"],
            username = json["username"]?.let { v0 -> v0 as String },
            controllerId = json["controllerId"]?.let { v0 -> v0 as String },
            ip = json["ip"]?.let { v0 -> v0 as String },
            robotId = json["robotId"]?.let { v0 -> (v0 as Number).toLong() },
            detail = json["detail"]?.let { v0 -> hydraMap(v0) },
            additionalProperties = hydraMap(json.filterKeys { it !in knownKeys }),
        )
    }
}

/** GET /api/audit as JSON: the newest entries (oldest first) and, with ?verify=1, the check of the hash chain. The same entries come as lines of JSON with ?format=jsonl. */
data class HydraAuditReport(
    val enabled: Boolean,
    val lockedOff: Boolean,
    val entries: List<HydraAuditEntry>,
    val verification: HydraAuditVerification? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["enabled"] = enabled
        jsonOut["lockedOff"] = lockedOff
        jsonOut["entries"] = entries.map { v0 -> v0.toJson() }
        if (verification != null) jsonOut["verification"] = verification.toJson()
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraAuditReport = HydraAuditReport(
            enabled = json["enabled"] as Boolean,
            lockedOff = json["lockedOff"] as Boolean,
            entries = hydraList(json["entries"]).map { v0 -> HydraAuditEntry.fromJson(hydraMap(v0)) },
            verification = json["verification"]?.let { v0 -> HydraAuditVerification.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraAuditVerification(
    val ok: Boolean,
    val entries: Long,
    val brokenAtSeq: Long? = null,
    val reason: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["ok"] = ok
        jsonOut["entries"] = entries
        if (brokenAtSeq != null) jsonOut["brokenAtSeq"] = brokenAtSeq
        if (reason != null) jsonOut["reason"] = reason
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraAuditVerification = HydraAuditVerification(
            ok = json["ok"] as Boolean,
            entries = (json["entries"] as Number).toLong(),
            brokenAtSeq = json["brokenAtSeq"]?.let { v0 -> (v0 as Number).toLong() },
            reason = json["reason"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraBluetoothScan(
    val success: Boolean,
    val devices: List<Map<String, Any?>>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["devices"] = devices
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraBluetoothScan = HydraBluetoothScan(
            success = json["success"] as Boolean,
            devices = hydraList(json["devices"]).map { v0 -> hydraMap(v0) },
        )
    }
}

/** The outcome of a command sent through the gateway: it was published, and the bridge answered (result holds its answer) or did not answer in time (result null). */
data class HydraBridgeCommandAccepted(
    val accepted: Boolean,
    /** The answer the bridge published on the result topic, as it published it; null when none arrived in time. */
    val result: Any?,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["accepted"] = accepted
        jsonOut["result"] = result
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraBridgeCommandAccepted = HydraBridgeCommandAccepted(
            accepted = json["accepted"] as Boolean,
            result = json["result"],
        )
    }
}

/** The bridges the gateway has seen on the broker. */
data class HydraBridgeList(
    /** Whether the gateway is connected to the broker now. */
    val connected: Boolean,
    val bridges: List<HydraBridgeState>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["connected"] = connected
        jsonOut["bridges"] = bridges.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraBridgeList = HydraBridgeList(
            connected = json["connected"] as Boolean,
            bridges = hydraList(json["bridges"]).map { v0 -> HydraBridgeState.fromJson(hydraMap(v0)) },
        )
    }
}

/** What the gateway knows of one machine bridge from its retained topics: whether it is available (null when it never said), its last state and health report as the bridge published them, and when the last of them arrived. */
data class HydraBridgeState(
    val name: String,
    /** True while the bridge is online (or its health report is not a FAULT), false when offline, null when it published neither. */
    val available: Boolean?,
    /** The last retained state of the bridge exactly as it published it (null when it published none). */
    val state: Any?,
    /** The last retained HealthReport of the bridge (null when it publishes none). */
    val health: Any?,
    val updatedAt: String?,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["name"] = name
        jsonOut["available"] = available
        jsonOut["state"] = state
        jsonOut["health"] = health
        jsonOut["updatedAt"] = updatedAt
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraBridgeState = HydraBridgeState(
            name = json["name"] as String,
            available = json["available"]?.let { v0 -> v0 as Boolean },
            state = json["state"],
            health = json["health"],
            updatedAt = json["updatedAt"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraCameraCapture(
    val success: Boolean,
    val cameraId: Long,
    val filename: String,
    val capturedAt: String? = null,
    val sizeBytes: Long? = null,
    val startedAt: String? = null,
    val stoppedAt: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["cameraId"] = cameraId
        jsonOut["filename"] = filename
        if (capturedAt != null) jsonOut["capturedAt"] = capturedAt
        if (sizeBytes != null) jsonOut["sizeBytes"] = sizeBytes
        if (startedAt != null) jsonOut["startedAt"] = startedAt
        if (stoppedAt != null) jsonOut["stoppedAt"] = stoppedAt
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraCameraCapture = HydraCameraCapture(
            success = json["success"] as Boolean,
            cameraId = (json["cameraId"] as Number).toLong(),
            filename = json["filename"] as String,
            capturedAt = json["capturedAt"]?.let { v0 -> v0 as String },
            sizeBytes = json["sizeBytes"]?.let { v0 -> (v0 as Number).toLong() },
            startedAt = json["startedAt"]?.let { v0 -> v0 as String },
            stoppedAt = json["stoppedAt"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraCameraMediaList(
    val items: List<HydraCameraMediaListItemsItem>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["items"] = items.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraCameraMediaList = HydraCameraMediaList(
            items = hydraList(json["items"]).map { v0 -> HydraCameraMediaListItemsItem.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraCameraMediaListItemsItem(
    val cameraId: Long,
    val kind: String,
    val filename: String,
    val sizeBytes: Long,
    val capturedAt: String,
    val recording: Boolean,
    val durationMs: Long? = null,
    val frameCount: Long? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["cameraId"] = cameraId
        jsonOut["kind"] = kind
        jsonOut["filename"] = filename
        jsonOut["sizeBytes"] = sizeBytes
        jsonOut["capturedAt"] = capturedAt
        jsonOut["recording"] = recording
        if (durationMs != null) jsonOut["durationMs"] = durationMs
        if (frameCount != null) jsonOut["frameCount"] = frameCount
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraCameraMediaListItemsItem = HydraCameraMediaListItemsItem(
            cameraId = (json["cameraId"] as Number).toLong(),
            kind = json["kind"] as String,
            filename = json["filename"] as String,
            sizeBytes = (json["sizeBytes"] as Number).toLong(),
            capturedAt = json["capturedAt"] as String,
            recording = json["recording"] as Boolean,
            durationMs = json["durationMs"]?.let { v0 -> (v0 as Number).toLong() },
            frameCount = json["frameCount"]?.let { v0 -> (v0 as Number).toLong() },
        )
    }
}

/** An object of the server contract. */
data class HydraCameraProcessStatusValue(
    val status: String,
    val lastError: String?,
    val port: Long,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["status"] = status
        jsonOut["lastError"] = lastError
        jsonOut["port"] = port
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraCameraProcessStatusValue = HydraCameraProcessStatusValue(
            status = json["status"] as String,
            lastError = json["lastError"]?.let { v0 -> v0 as String },
            port = (json["port"] as Number).toLong(),
        )
    }
}

/** An object of the server contract. */
data class HydraCanotaFlash(
    val success: Boolean,
    val finalPhase: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["finalPhase"] = finalPhase
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraCanotaFlash = HydraCanotaFlash(
            success = json["success"] as Boolean,
            finalPhase = json["finalPhase"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraClaimList(
    val claims: List<HydraClaimView>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["claims"] = claims.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraClaimList = HydraClaimList(
            claims = hydraList(json["claims"]).map { v0 -> HydraClaimView.fromJson(hydraMap(v0)) },
        )
    }
}

/** One robot that has an active claim: who holds it, from which controller, until when and until when its jog is armed. */
data class HydraClaimView(
    val robotId: Long,
    val robotName: String? = null,
    /** The id of the controller the robot belongs to (any JSON value; the server does not fix its type). */
    val cellId: Any? = null,
    /** The id of the account that holds the claim (any JSON value). */
    val ownerId: Any? = null,
    val ownerUsername: String,
    val controllerId: String? = null,
    /** Milliseconds since the epoch. */
    val claimedAt: Double,
    /** Milliseconds since the epoch. */
    val expiresAt: Double,
    /** Milliseconds since the epoch; null when the jog is not armed. */
    val jogArmedUntil: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["robotId"] = robotId
        if (robotName != null) jsonOut["robotName"] = robotName
        if (cellId != null) jsonOut["cellId"] = cellId
        if (ownerId != null) jsonOut["ownerId"] = ownerId
        jsonOut["ownerUsername"] = ownerUsername
        if (controllerId != null) jsonOut["controllerId"] = controllerId
        jsonOut["claimedAt"] = claimedAt
        jsonOut["expiresAt"] = expiresAt
        if (jogArmedUntil != null) jsonOut["jogArmedUntil"] = jogArmedUntil
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraClaimView = HydraClaimView(
            robotId = (json["robotId"] as Number).toLong(),
            robotName = json["robotName"]?.let { v0 -> v0 as String },
            cellId = json["cellId"],
            ownerId = json["ownerId"],
            ownerUsername = json["ownerUsername"] as String,
            controllerId = json["controllerId"]?.let { v0 -> v0 as String },
            claimedAt = (json["claimedAt"] as Number).toDouble(),
            expiresAt = (json["expiresAt"] as Number).toDouble(),
            jogArmedUntil = json["jogArmedUntil"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraClients(
    val clients: List<Map<String, Any?>>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["clients"] = clients
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraClients = HydraClients(
            clients = hydraList(json["clients"]).map { v0 -> hydraMap(v0) },
        )
    }
}

/** An object of the server contract. */
data class HydraConnectionClient(
    val schemaVersion: String,
    val id: String,
    val kind: String,
    val user: String? = null,
    val appVersion: String? = null,
    val origin: String? = null,
    val twoFactor: Boolean? = null,
    val firstSeenUtc: String,
    val lastSeenUtc: String,
    val lastFailureUtc: String? = null,
    val activeSessions: Long,
    val loginsOk: Long,
    val loginsFailed: Long,
    /** Administrators only, and only when connections.recordAddress is on. */
    val ip: String? = null,
    /** Administrators only, and only when connections.recordAddress is on. */
    val agent: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["schema_version"] = schemaVersion
        jsonOut["id"] = id
        jsonOut["kind"] = kind
        if (user != null) jsonOut["user"] = user
        if (appVersion != null) jsonOut["app_version"] = appVersion
        if (origin != null) jsonOut["origin"] = origin
        if (twoFactor != null) jsonOut["two_factor"] = twoFactor
        jsonOut["first_seen_utc"] = firstSeenUtc
        jsonOut["last_seen_utc"] = lastSeenUtc
        if (lastFailureUtc != null) jsonOut["last_failure_utc"] = lastFailureUtc
        jsonOut["active_sessions"] = activeSessions
        jsonOut["logins_ok"] = loginsOk
        jsonOut["logins_failed"] = loginsFailed
        if (ip != null) jsonOut["ip"] = ip
        if (agent != null) jsonOut["agent"] = agent
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraConnectionClient = HydraConnectionClient(
            schemaVersion = json["schema_version"] as String,
            id = json["id"] as String,
            kind = json["kind"] as String,
            user = json["user"]?.let { v0 -> v0 as String },
            appVersion = json["app_version"]?.let { v0 -> v0 as String },
            origin = json["origin"]?.let { v0 -> v0 as String },
            twoFactor = json["two_factor"]?.let { v0 -> v0 as Boolean },
            firstSeenUtc = json["first_seen_utc"] as String,
            lastSeenUtc = json["last_seen_utc"] as String,
            lastFailureUtc = json["last_failure_utc"]?.let { v0 -> v0 as String },
            activeSessions = (json["active_sessions"] as Number).toLong(),
            loginsOk = (json["logins_ok"] as Number).toLong(),
            loginsFailed = (json["logins_failed"] as Number).toLong(),
            ip = json["ip"]?.let { v0 -> v0 as String },
            agent = json["agent"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraConnectionClientList(
    val clients: List<HydraConnectionClient>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["clients"] = clients.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraConnectionClientList = HydraConnectionClientList(
            clients = hydraList(json["clients"]).map { v0 -> HydraConnectionClient.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraConnectionEvent(
    val schemaVersion: String,
    val id: Long,
    val atUtc: String,
    val action: String,
    val clientKind: String,
    val clientId: String,
    val user: String? = null,
    val origin: String? = null,
    val twoFactor: Boolean? = null,
    val appVersion: String? = null,
    /** Administrators only, and only when connections.recordAddress is on. */
    val ip: String? = null,
    /** Administrators only, and only when connections.recordAddress is on. */
    val agent: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["schema_version"] = schemaVersion
        jsonOut["id"] = id
        jsonOut["at_utc"] = atUtc
        jsonOut["action"] = action
        jsonOut["client_kind"] = clientKind
        jsonOut["client_id"] = clientId
        if (user != null) jsonOut["user"] = user
        if (origin != null) jsonOut["origin"] = origin
        if (twoFactor != null) jsonOut["two_factor"] = twoFactor
        if (appVersion != null) jsonOut["app_version"] = appVersion
        if (ip != null) jsonOut["ip"] = ip
        if (agent != null) jsonOut["agent"] = agent
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraConnectionEvent = HydraConnectionEvent(
            schemaVersion = json["schema_version"] as String,
            id = (json["id"] as Number).toLong(),
            atUtc = json["at_utc"] as String,
            action = json["action"] as String,
            clientKind = json["client_kind"] as String,
            clientId = json["client_id"] as String,
            user = json["user"]?.let { v0 -> v0 as String },
            origin = json["origin"]?.let { v0 -> v0 as String },
            twoFactor = json["two_factor"]?.let { v0 -> v0 as Boolean },
            appVersion = json["app_version"]?.let { v0 -> v0 as String },
            ip = json["ip"]?.let { v0 -> v0 as String },
            agent = json["agent"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraConnectionEventList(
    val events: List<HydraConnectionEvent>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["events"] = events.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraConnectionEventList = HydraConnectionEventList(
            events = hydraList(json["events"]).map { v0 -> HydraConnectionEvent.fromJson(hydraMap(v0)) },
        )
    }
}

/** A device token just issued. The token is in this answer and nowhere else: the server does not keep it. */
data class HydraDeviceTokenIssued(
    /** The id of the token (22 URL-safe characters); the token itself is never kept. */
    val id: String,
    /** What the administrator called the device. */
    val name: String,
    /** The account the device signs in as. */
    val username: String,
    val createdAt: String,
    val expiresAt: String,
    val revokedAt: String?,
    val lastUsedAt: String?,
    val state: String,
    /** Signed token of one device; the device presents it on POST /api/device/login. */
    val token: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["id"] = id
        jsonOut["name"] = name
        jsonOut["username"] = username
        jsonOut["createdAt"] = createdAt
        jsonOut["expiresAt"] = expiresAt
        jsonOut["revokedAt"] = revokedAt
        jsonOut["lastUsedAt"] = lastUsedAt
        jsonOut["state"] = state
        jsonOut["token"] = token
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraDeviceTokenIssued = HydraDeviceTokenIssued(
            id = json["id"] as String,
            name = json["name"] as String,
            username = json["username"] as String,
            createdAt = json["createdAt"] as String,
            expiresAt = json["expiresAt"] as String,
            revokedAt = json["revokedAt"]?.let { v0 -> v0 as String },
            lastUsedAt = json["lastUsedAt"]?.let { v0 -> v0 as String },
            state = json["state"] as String,
            token = json["token"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraDeviceTokenList(
    val items: List<HydraDeviceTokenView>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["items"] = items.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraDeviceTokenList = HydraDeviceTokenList(
            items = hydraList(json["items"]).map { v0 -> HydraDeviceTokenView.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraDeviceTokenRevoked(
    val revoked: Boolean,
    val sessionsEnded: Long,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["revoked"] = revoked
        jsonOut["sessionsEnded"] = sessionsEnded
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraDeviceTokenRevoked = HydraDeviceTokenRevoked(
            revoked = json["revoked"] as Boolean,
            sessionsEnded = (json["sessionsEnded"] as Number).toLong(),
        )
    }
}

/** A device token as the administrator sees it: who it is for and until when, never the token. */
data class HydraDeviceTokenView(
    /** The id of the token (22 URL-safe characters); the token itself is never kept. */
    val id: String,
    /** What the administrator called the device. */
    val name: String,
    /** The account the device signs in as. */
    val username: String,
    val createdAt: String,
    val expiresAt: String,
    val revokedAt: String?,
    val lastUsedAt: String?,
    val state: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["id"] = id
        jsonOut["name"] = name
        jsonOut["username"] = username
        jsonOut["createdAt"] = createdAt
        jsonOut["expiresAt"] = expiresAt
        jsonOut["revokedAt"] = revokedAt
        jsonOut["lastUsedAt"] = lastUsedAt
        jsonOut["state"] = state
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraDeviceTokenView = HydraDeviceTokenView(
            id = json["id"] as String,
            name = json["name"] as String,
            username = json["username"] as String,
            createdAt = json["createdAt"] as String,
            expiresAt = json["expiresAt"] as String,
            revokedAt = json["revokedAt"]?.let { v0 -> v0 as String },
            lastUsedAt = json["lastUsedAt"]?.let { v0 -> v0 as String },
            state = json["state"] as String,
        )
    }
}

/** The health of the services of the ecosystem. Only on a server where ecosystemHealth.enabled is on (404 otherwise); for an operator or an administrator. The port, health path, unit and active state of a service are only in the answer to an administrator. */
data class HydraEcosystemHealth(
    val schemaVersion: String,
    val generatedAtUtc: String,
    /** False when the sibling checkouts could not be scanned (no services then). */
    val available: Boolean,
    val summary: HydraEcosystemHealthSummary,
    val services: List<HydraEcosystemHealthServicesItem>,
    /** The TLS certificate of this server; null when it runs without TLS. state is ok, expiring (fewer days left than warn_days), expired or unreadable. */
    val certificate: HydraEcosystemHealthCertificate?,
    val warnings: List<HydraEcosystemHealthWarningsItem>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["schema_version"] = schemaVersion
        jsonOut["generated_at_utc"] = generatedAtUtc
        jsonOut["available"] = available
        jsonOut["summary"] = summary.toJson()
        jsonOut["services"] = services.map { v0 -> v0.toJson() }
        jsonOut["certificate"] = certificate?.toJson()
        jsonOut["warnings"] = warnings.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraEcosystemHealth = HydraEcosystemHealth(
            schemaVersion = json["schema_version"] as String,
            generatedAtUtc = json["generated_at_utc"] as String,
            available = json["available"] as Boolean,
            summary = HydraEcosystemHealthSummary.fromJson(hydraMap(json["summary"])),
            services = hydraList(json["services"]).map { v0 -> HydraEcosystemHealthServicesItem.fromJson(hydraMap(v0)) },
            certificate = json["certificate"]?.let { v0 -> HydraEcosystemHealthCertificate.fromJson(hydraMap(v0)) },
            warnings = hydraList(json["warnings"]).map { v0 -> HydraEcosystemHealthWarningsItem.fromJson(hydraMap(v0)) },
        )
    }
}

/** The TLS certificate of this server; null when it runs without TLS. state is ok, expiring (fewer days left than warn_days), expired or unreadable. */
data class HydraEcosystemHealthCertificate(
    val state: String? = null,
    val notAfterUtc: String? = null,
    val daysLeft: Long? = null,
    val warnDays: Long? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (state != null) jsonOut["state"] = state
        if (notAfterUtc != null) jsonOut["not_after_utc"] = notAfterUtc
        if (daysLeft != null) jsonOut["days_left"] = daysLeft
        if (warnDays != null) jsonOut["warn_days"] = warnDays
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraEcosystemHealthCertificate = HydraEcosystemHealthCertificate(
            state = json["state"]?.let { v0 -> v0 as String },
            notAfterUtc = json["not_after_utc"]?.let { v0 -> v0 as String },
            daysLeft = json["days_left"]?.let { v0 -> (v0 as Number).toLong() },
            warnDays = json["warn_days"]?.let { v0 -> (v0 as Number).toLong() },
        )
    }
}

/** state is ok, degraded, down or unknown; reason is a short code the clients translate. version_expected comes from the manifest, version_reported from the HealthReport of the service; drift is true only when both are known and differ. */
data class HydraEcosystemHealthServicesItem(
    val name: String,
    val family: String?,
    val role: String?,
    val state: String,
    val reason: String,
    val versionExpected: String?,
    val versionReported: String?,
    val drift: Boolean,
    val lastSeenUtc: String?,
    val latencyMs: Long?,
    /** Administrators only. */
    val port: Long? = null,
    /** Administrators only. */
    val healthPath: String? = null,
    /** Administrators only. */
    val systemdUnit: String? = null,
    /** Administrators only. */
    val activeState: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["name"] = name
        jsonOut["family"] = family
        jsonOut["role"] = role
        jsonOut["state"] = state
        jsonOut["reason"] = reason
        jsonOut["version_expected"] = versionExpected
        jsonOut["version_reported"] = versionReported
        jsonOut["drift"] = drift
        jsonOut["last_seen_utc"] = lastSeenUtc
        jsonOut["latency_ms"] = latencyMs
        if (port != null) jsonOut["port"] = port
        if (healthPath != null) jsonOut["health_path"] = healthPath
        if (systemdUnit != null) jsonOut["systemd_unit"] = systemdUnit
        if (activeState != null) jsonOut["active_state"] = activeState
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraEcosystemHealthServicesItem = HydraEcosystemHealthServicesItem(
            name = json["name"] as String,
            family = json["family"]?.let { v0 -> v0 as String },
            role = json["role"]?.let { v0 -> v0 as String },
            state = json["state"] as String,
            reason = json["reason"] as String,
            versionExpected = json["version_expected"]?.let { v0 -> v0 as String },
            versionReported = json["version_reported"]?.let { v0 -> v0 as String },
            drift = json["drift"] as Boolean,
            lastSeenUtc = json["last_seen_utc"]?.let { v0 -> v0 as String },
            latencyMs = json["latency_ms"]?.let { v0 -> (v0 as Number).toLong() },
            port = json["port"]?.let { v0 -> (v0 as Number).toLong() },
            healthPath = json["health_path"]?.let { v0 -> v0 as String },
            systemdUnit = json["systemd_unit"]?.let { v0 -> v0 as String },
            activeState = json["active_state"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraEcosystemHealthSummary(
    val total: Long,
    val ok: Long,
    val degraded: Long,
    val down: Long,
    val unknown: Long,
    val drift: Long,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["total"] = total
        jsonOut["ok"] = ok
        jsonOut["degraded"] = degraded
        jsonOut["down"] = down
        jsonOut["unknown"] = unknown
        jsonOut["drift"] = drift
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraEcosystemHealthSummary = HydraEcosystemHealthSummary(
            total = (json["total"] as Number).toLong(),
            ok = (json["ok"] as Number).toLong(),
            degraded = (json["degraded"] as Number).toLong(),
            down = (json["down"] as Number).toLong(),
            unknown = (json["unknown"] as Number).toLong(),
            drift = (json["drift"] as Number).toLong(),
        )
    }
}

/** An object of the server contract. */
data class HydraEcosystemHealthWarningsItem(
    val code: String,
    val service: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["code"] = code
        if (service != null) jsonOut["service"] = service
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraEcosystemHealthWarningsItem = HydraEcosystemHealthWarningsItem(
            code = json["code"] as String,
            service = json["service"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraEcosystemStatus(
    val available: Boolean,
    val scannedAt: String,
    val projects: List<HydraEcosystemStatusProjectsItem>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["available"] = available
        jsonOut["scannedAt"] = scannedAt
        jsonOut["projects"] = projects.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraEcosystemStatus = HydraEcosystemStatus(
            available = json["available"] as Boolean,
            scannedAt = json["scannedAt"] as String,
            projects = hydraList(json["projects"]).map { v0 -> HydraEcosystemStatusProjectsItem.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraEcosystemStatusProjectsItem(
    val name: String,
    val role: String? = null,
    val stack: String? = null,
    val maturity: String? = null,
    val family: String? = null,
    val version: String? = null,
    val deploymentTarget: String? = null,
    val servicePort: Long? = null,
    val serviceHealthPath: String? = null,
    val serviceHost: String? = null,
    val systemdUnit: String? = null,
    val pid: Long? = null,
    val activeState: String? = null,
    val subState: String? = null,
    val live: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["name"] = name
        if (role != null) jsonOut["role"] = role
        if (stack != null) jsonOut["stack"] = stack
        if (maturity != null) jsonOut["maturity"] = maturity
        if (family != null) jsonOut["family"] = family
        if (version != null) jsonOut["version"] = version
        if (deploymentTarget != null) jsonOut["deploymentTarget"] = deploymentTarget
        if (servicePort != null) jsonOut["servicePort"] = servicePort
        if (serviceHealthPath != null) jsonOut["serviceHealthPath"] = serviceHealthPath
        if (serviceHost != null) jsonOut["serviceHost"] = serviceHost
        if (systemdUnit != null) jsonOut["systemdUnit"] = systemdUnit
        if (pid != null) jsonOut["pid"] = pid
        if (activeState != null) jsonOut["activeState"] = activeState
        if (subState != null) jsonOut["subState"] = subState
        if (live != null) jsonOut["live"] = live
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraEcosystemStatusProjectsItem = HydraEcosystemStatusProjectsItem(
            name = json["name"] as String,
            role = json["role"]?.let { v0 -> v0 as String },
            stack = json["stack"]?.let { v0 -> v0 as String },
            maturity = json["maturity"]?.let { v0 -> v0 as String },
            family = json["family"]?.let { v0 -> v0 as String },
            version = json["version"]?.let { v0 -> v0 as String },
            deploymentTarget = json["deploymentTarget"]?.let { v0 -> v0 as String },
            servicePort = json["servicePort"]?.let { v0 -> (v0 as Number).toLong() },
            serviceHealthPath = json["serviceHealthPath"]?.let { v0 -> v0 as String },
            serviceHost = json["serviceHost"]?.let { v0 -> v0 as String },
            systemdUnit = json["systemdUnit"]?.let { v0 -> v0 as String },
            pid = json["pid"]?.let { v0 -> (v0 as Number).toLong() },
            activeState = json["activeState"]?.let { v0 -> v0 as String },
            subState = json["subState"]?.let { v0 -> v0 as String },
            live = json["live"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraError(
    val error: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["error"] = error
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraError = HydraError(
            error = json["error"] as String,
        )
    }
}

/** The progress file of tools/fleet_update.py (hydra-fleet-update/1). A run whose heartbeat stopped is reported as interrupted. */
data class HydraFleetUpdateReport(
    val schema: String,
    val id: String,
    val mode: String,
    val state: String,
    val startedAt: String,
    val updatedAt: String,
    val error: String,
    val stoppedAt: String,
    val requireSignedTags: Boolean,
    val disk: HydraFleetUpdateReportDisk,
    val services: List<HydraFleetUpdateRow>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["schema"] = schema
        jsonOut["id"] = id
        jsonOut["mode"] = mode
        jsonOut["state"] = state
        jsonOut["startedAt"] = startedAt
        jsonOut["updatedAt"] = updatedAt
        jsonOut["error"] = error
        jsonOut["stoppedAt"] = stoppedAt
        jsonOut["requireSignedTags"] = requireSignedTags
        jsonOut["disk"] = disk.toJson()
        jsonOut["services"] = services.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraFleetUpdateReport = HydraFleetUpdateReport(
            schema = json["schema"] as String,
            id = json["id"] as String,
            mode = json["mode"] as String,
            state = json["state"] as String,
            startedAt = json["startedAt"] as String,
            updatedAt = json["updatedAt"] as String,
            error = json["error"] as String,
            stoppedAt = json["stoppedAt"] as String,
            requireSignedTags = json["requireSignedTags"] as Boolean,
            disk = HydraFleetUpdateReportDisk.fromJson(hydraMap(json["disk"])),
            services = hydraList(json["services"]).map { v0 -> HydraFleetUpdateRow.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraFleetUpdateReportDisk(
    val rootFreeMb: Long?,
    val workspaceFreeMb: Long?,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["rootFreeMb"] = rootFreeMb
        jsonOut["workspaceFreeMb"] = workspaceFreeMb
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraFleetUpdateReportDisk = HydraFleetUpdateReportDisk(
            rootFreeMb = json["rootFreeMb"]?.let { v0 -> (v0 as Number).toLong() },
            workspaceFreeMb = json["workspaceFreeMb"]?.let { v0 -> (v0 as Number).toLong() },
        )
    }
}

/** One program of the device in the update of everything installed: its versions, what the plan does with it and where its steps are. */
data class HydraFleetUpdateRow(
    val name: String,
    val kind: String,
    val repo: String,
    val installed: String?,
    val latest: String?,
    val action: String,
    val reason: String,
    val state: String,
    val step: String,
    val substep: String? = null,
    val substeps: Long? = null,
    val detail: String,
    val error: String,
    val order: Long,
    val elapsedS: Long? = null,
    val freeMb: Long? = null,
    val needMb: Long? = null,
    val unitRestored: Boolean? = null,
    val log: List<HydraFleetUpdateRowLogItem>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["name"] = name
        jsonOut["kind"] = kind
        jsonOut["repo"] = repo
        jsonOut["installed"] = installed
        jsonOut["latest"] = latest
        jsonOut["action"] = action
        jsonOut["reason"] = reason
        jsonOut["state"] = state
        jsonOut["step"] = step
        if (substep != null) jsonOut["substep"] = substep
        if (substeps != null) jsonOut["substeps"] = substeps
        jsonOut["detail"] = detail
        jsonOut["error"] = error
        jsonOut["order"] = order
        if (elapsedS != null) jsonOut["elapsedS"] = elapsedS
        if (freeMb != null) jsonOut["freeMb"] = freeMb
        if (needMb != null) jsonOut["needMb"] = needMb
        if (unitRestored != null) jsonOut["unitRestored"] = unitRestored
        jsonOut["log"] = log.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraFleetUpdateRow = HydraFleetUpdateRow(
            name = json["name"] as String,
            kind = json["kind"] as String,
            repo = json["repo"] as String,
            installed = json["installed"]?.let { v0 -> v0 as String },
            latest = json["latest"]?.let { v0 -> v0 as String },
            action = json["action"] as String,
            reason = json["reason"] as String,
            state = json["state"] as String,
            step = json["step"] as String,
            substep = json["substep"]?.let { v0 -> v0 as String },
            substeps = json["substeps"]?.let { v0 -> (v0 as Number).toLong() },
            detail = json["detail"] as String,
            error = json["error"] as String,
            order = (json["order"] as Number).toLong(),
            elapsedS = json["elapsedS"]?.let { v0 -> (v0 as Number).toLong() },
            freeMb = json["freeMb"]?.let { v0 -> (v0 as Number).toLong() },
            needMb = json["needMb"]?.let { v0 -> (v0 as Number).toLong() },
            unitRestored = json["unitRestored"]?.let { v0 -> v0 as Boolean },
            log = hydraList(json["log"]).map { v0 -> HydraFleetUpdateRowLogItem.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraFleetUpdateRowLogItem(
    val at: String,
    val text: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["at"] = at
        jsonOut["text"] = text
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraFleetUpdateRowLogItem = HydraFleetUpdateRowLogItem(
            at = json["at"] as String,
            text = json["text"] as String,
        )
    }
}

/** Whether applying is switched on, whether a look or a run is going on, and the progress file (null before the first look). */
data class HydraFleetUpdateStatus(
    val applyEnabled: Boolean,
    val busy: Boolean,
    val report: HydraFleetUpdateReport?,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["applyEnabled"] = applyEnabled
        jsonOut["busy"] = busy
        jsonOut["report"] = report?.toJson()
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraFleetUpdateStatus = HydraFleetUpdateStatus(
            applyEnabled = json["applyEnabled"] as Boolean,
            busy = json["busy"] as Boolean,
            report = json["report"]?.let { v0 -> HydraFleetUpdateReport.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraGetAdminRobotIdsResult(
    /** False while at least one robot id is used by more than one robot. */
    val ok: Boolean,
    val ambiguousCount: Long,
    /** The routes by these ids answer 409 robot_id_ambiguous. Controller ids only. */
    val ambiguous: List<HydraGetAdminRobotIdsResultAmbiguousItem>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["ok"] = ok
        jsonOut["ambiguousCount"] = ambiguousCount
        jsonOut["ambiguous"] = ambiguous.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetAdminRobotIdsResult = HydraGetAdminRobotIdsResult(
            ok = json["ok"] as Boolean,
            ambiguousCount = (json["ambiguousCount"] as Number).toLong(),
            ambiguous = hydraList(json["ambiguous"]).map { v0 -> HydraGetAdminRobotIdsResultAmbiguousItem.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraGetAdminRobotIdsResultAmbiguousItem(
    val robotId: Long,
    val controllers: List<String>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["robotId"] = robotId
        jsonOut["controllers"] = controllers
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetAdminRobotIdsResultAmbiguousItem = HydraGetAdminRobotIdsResultAmbiguousItem(
            robotId = (json["robotId"] as Number).toLong(),
            controllers = hydraList(json["controllers"]).map { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraGetConnectorHubGateSettingsResult(
    val allowLoopbackNoIdentity: Boolean,
    val loopbackSwitchAllowed: Boolean? = null,
    val verifiesTokens: Boolean? = null,
    val persisted: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["allowLoopbackNoIdentity"] = allowLoopbackNoIdentity
        if (loopbackSwitchAllowed != null) jsonOut["loopbackSwitchAllowed"] = loopbackSwitchAllowed
        if (verifiesTokens != null) jsonOut["verifiesTokens"] = verifiesTokens
        if (persisted != null) jsonOut["persisted"] = persisted
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetConnectorHubGateSettingsResult = HydraGetConnectorHubGateSettingsResult(
            allowLoopbackNoIdentity = json["allowLoopbackNoIdentity"] as Boolean,
            loopbackSwitchAllowed = json["loopbackSwitchAllowed"]?.let { v0 -> v0 as Boolean },
            verifiesTokens = json["verifiesTokens"]?.let { v0 -> v0 as Boolean },
            persisted = json["persisted"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraGetDroidEstopSettingsResult(
    val enabled: Boolean,
    val running: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["enabled"] = enabled
        if (running != null) jsonOut["running"] = running
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetDroidEstopSettingsResult = HydraGetDroidEstopSettingsResult(
            enabled = json["enabled"] as Boolean,
            running = json["running"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraGetHilBridgeSettingsResult(
    val requireTwinPass: Boolean,
    val locked: Boolean? = null,
    val persisted: Boolean? = null,
    val ready: Boolean? = null,
    val canChange: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["requireTwinPass"] = requireTwinPass
        if (locked != null) jsonOut["locked"] = locked
        if (persisted != null) jsonOut["persisted"] = persisted
        if (ready != null) jsonOut["ready"] = ready
        if (canChange != null) jsonOut["canChange"] = canChange
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetHilBridgeSettingsResult = HydraGetHilBridgeSettingsResult(
            requireTwinPass = json["requireTwinPass"] as Boolean,
            locked = json["locked"]?.let { v0 -> v0 as Boolean },
            persisted = json["persisted"]?.let { v0 -> v0 as Boolean },
            ready = json["ready"]?.let { v0 -> v0 as Boolean },
            canChange = json["canChange"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraGetOpsAgentProposalsResult(
    val pending: List<Map<String, Any?>>,
    val decided: List<Map<String, Any?>>? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["pending"] = pending
        if (decided != null) jsonOut["decided"] = decided
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetOpsAgentProposalsResult = HydraGetOpsAgentProposalsResult(
            pending = hydraList(json["pending"]).map { v0 -> hydraMap(v0) },
            decided = json["decided"]?.let { v0 -> hydraList(v0).map { v1 -> hydraMap(v1) } },
        )
    }
}

/** An object of the server contract. */
data class HydraGetRobotByIdResult(
    val robot: Map<String, Any?>,
    val revision: String,
    /** The id of the controller the robot belongs to (null when it is in none). */
    val cellId: Any? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["robot"] = robot
        jsonOut["revision"] = revision
        if (cellId != null) jsonOut["cellId"] = cellId
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetRobotByIdResult = HydraGetRobotByIdResult(
            robot = hydraMap(json["robot"]),
            revision = json["revision"] as String,
            cellId = json["cellId"],
        )
    }
}

/** An object of the server contract. */
data class HydraGetRos2BridgeSettingsResult(
    val requireSros2: Boolean,
    val active: Boolean,
    val restartNeeded: Boolean,
    val canChange: Boolean,
    val environmentReady: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["requireSros2"] = requireSros2
        jsonOut["active"] = active
        jsonOut["restartNeeded"] = restartNeeded
        jsonOut["canChange"] = canChange
        jsonOut["environmentReady"] = environmentReady
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetRos2BridgeSettingsResult = HydraGetRos2BridgeSettingsResult(
            requireSros2 = json["requireSros2"] as Boolean,
            active = json["active"] as Boolean,
            restartNeeded = json["restartNeeded"] as Boolean,
            canChange = json["canChange"] as Boolean,
            environmentReady = json["environmentReady"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraGetSemanticPlannerSettingsResult(
    val requireIdentity: Boolean,
    val verifiesTokens: Boolean? = null,
    val persisted: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["requireIdentity"] = requireIdentity
        if (verifiesTokens != null) jsonOut["verifiesTokens"] = verifiesTokens
        if (persisted != null) jsonOut["persisted"] = persisted
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetSemanticPlannerSettingsResult = HydraGetSemanticPlannerSettingsResult(
            requireIdentity = json["requireIdentity"] as Boolean,
            verifiesTokens = json["verifiesTokens"]?.let { v0 -> v0 as Boolean },
            persisted = json["persisted"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraGetTelemetryAggregateResultItem(
    val bucketStart: Double,
    val value: Double,
    val count: Double,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["bucketStart"] = bucketStart
        jsonOut["value"] = value
        jsonOut["count"] = count
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetTelemetryAggregateResultItem = HydraGetTelemetryAggregateResultItem(
            bucketStart = (json["bucketStart"] as Number).toDouble(),
            value = (json["value"] as Number).toDouble(),
            count = (json["count"] as Number).toDouble(),
        )
    }
}

/** An object of the server contract. */
data class HydraGetTelemetryDownsamplePlanResult(
    val plan: HydraGetTelemetryDownsamplePlanResultPlan,
    val hash: String,
    val tiers: List<Map<String, Any?>>? = null,
    val knownKinds: List<String>? = null,
    val switches: HydraGetTelemetryDownsamplePlanResultSwitches? = null,
    val audit: List<Map<String, Any?>>? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["plan"] = plan.toJson()
        jsonOut["hash"] = hash
        if (tiers != null) jsonOut["tiers"] = tiers
        if (knownKinds != null) jsonOut["knownKinds"] = knownKinds
        if (switches != null) jsonOut["switches"] = switches.toJson()
        if (audit != null) jsonOut["audit"] = audit
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetTelemetryDownsamplePlanResult = HydraGetTelemetryDownsamplePlanResult(
            plan = HydraGetTelemetryDownsamplePlanResultPlan.fromJson(hydraMap(json["plan"])),
            hash = json["hash"] as String,
            tiers = json["tiers"]?.let { v0 -> hydraList(v0).map { v1 -> hydraMap(v1) } },
            knownKinds = json["knownKinds"]?.let { v0 -> hydraList(v0).map { v1 -> v1 as String } },
            switches = json["switches"]?.let { v0 -> HydraGetTelemetryDownsamplePlanResultSwitches.fromJson(hydraMap(v0)) },
            audit = json["audit"]?.let { v0 -> hydraList(v0).map { v1 -> hydraMap(v1) } },
        )
    }
}

/** An object of the server contract. */
data class HydraGetTelemetryDownsamplePlanResultPlan(
    val tiers: List<HydraGetTelemetryDownsamplePlanResultPlanTiersItem>,
    val delete: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["tiers"] = tiers.map { v0 -> v0.toJson() }
        jsonOut["delete"] = delete
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetTelemetryDownsamplePlanResultPlan = HydraGetTelemetryDownsamplePlanResultPlan(
            tiers = hydraList(json["tiers"]).map { v0 -> HydraGetTelemetryDownsamplePlanResultPlanTiersItem.fromJson(hydraMap(v0)) },
            delete = json["delete"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraGetTelemetryDownsamplePlanResultPlanTiersItem(
    val kind: String,
    val field: String,
    /** How long raw points are kept: milliseconds or text such as 30d. */
    val raw: Any? = null,
    /** Width of the rollup bucket. */
    val bucket: Any? = null,
    /** Width of the fine rollup bucket. */
    val fineBucket: Any? = null,
    /** How long rollups are kept. */
    val rollupRetention: Any? = null,
    /** How long fine rollups are kept. */
    val fineRetention: Any? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["kind"] = kind
        jsonOut["field"] = field
        if (raw != null) jsonOut["raw"] = raw
        if (bucket != null) jsonOut["bucket"] = bucket
        if (fineBucket != null) jsonOut["fineBucket"] = fineBucket
        if (rollupRetention != null) jsonOut["rollupRetention"] = rollupRetention
        if (fineRetention != null) jsonOut["fineRetention"] = fineRetention
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetTelemetryDownsamplePlanResultPlanTiersItem = HydraGetTelemetryDownsamplePlanResultPlanTiersItem(
            kind = json["kind"] as String,
            field = json["field"] as String,
            raw = json["raw"],
            bucket = json["bucket"],
            fineBucket = json["fineBucket"],
            rollupRetention = json["rollupRetention"],
            fineRetention = json["fineRetention"],
        )
    }
}

/** An object of the server contract. */
data class HydraGetTelemetryDownsamplePlanResultSwitches(
    val allowDelete: Boolean? = null,
    val deleteRequestedByPlan: Boolean? = null,
    val deleteOldSwitch: Boolean? = null,
    val effectiveMode: String? = null,
    val fineRollups: Boolean? = null,
    val autoIntervalSeconds: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (allowDelete != null) jsonOut["allowDelete"] = allowDelete
        if (deleteRequestedByPlan != null) jsonOut["deleteRequestedByPlan"] = deleteRequestedByPlan
        if (deleteOldSwitch != null) jsonOut["deleteOldSwitch"] = deleteOldSwitch
        if (effectiveMode != null) jsonOut["effectiveMode"] = effectiveMode
        if (fineRollups != null) jsonOut["fineRollups"] = fineRollups
        if (autoIntervalSeconds != null) jsonOut["autoIntervalSeconds"] = autoIntervalSeconds
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetTelemetryDownsamplePlanResultSwitches = HydraGetTelemetryDownsamplePlanResultSwitches(
            allowDelete = json["allowDelete"]?.let { v0 -> v0 as Boolean },
            deleteRequestedByPlan = json["deleteRequestedByPlan"]?.let { v0 -> v0 as Boolean },
            deleteOldSwitch = json["deleteOldSwitch"]?.let { v0 -> v0 as Boolean },
            effectiveMode = json["effectiveMode"]?.let { v0 -> v0 as String },
            fineRollups = json["fineRollups"]?.let { v0 -> v0 as Boolean },
            autoIntervalSeconds = json["autoIntervalSeconds"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraGetTelemetryQueryResultItem(
    val sourceId: String,
    val kind: String,
    val field: String,
    val timestamp: Double,
    val value: Double,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["sourceId"] = sourceId
        jsonOut["kind"] = kind
        jsonOut["field"] = field
        jsonOut["timestamp"] = timestamp
        jsonOut["value"] = value
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGetTelemetryQueryResultItem = HydraGetTelemetryQueryResultItem(
            sourceId = json["sourceId"] as String,
            kind = json["kind"] as String,
            field = json["field"] as String,
            timestamp = (json["timestamp"] as Number).toDouble(),
            value = (json["value"] as Number).toDouble(),
        )
    }
}

/** An object of the server contract. */
data class HydraGlobalStopReleased(
    val success: Boolean,
    /** Whether the retained READY went out on the MQTT bridge (false when announcing is not configured or the broker is not connected). */
    val announced: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["announced"] = announced
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraGlobalStopReleased = HydraGlobalStopReleased(
            success = json["success"] as Boolean,
            announced = json["announced"] as Boolean,
        )
    }
}

/** The HealthReport contract of the SDK. Nothing else about the host is in it. */
data class HydraHealthReport(
    val schemaVersion: String,
    val state: String,
    val timestampUtc: String,
    val checks: Map<String, Any?>,
    val service: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["schema_version"] = schemaVersion
        jsonOut["state"] = state
        jsonOut["timestamp_utc"] = timestampUtc
        jsonOut["checks"] = checks
        if (service != null) jsonOut["service"] = service
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraHealthReport = HydraHealthReport(
            schemaVersion = json["schema_version"] as String,
            state = json["state"] as String,
            timestampUtc = json["timestamp_utc"] as String,
            checks = hydraMap(json["checks"]),
            service = json["service"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraHydraInfo(
    val schemaVersion: String,
    val product: String,
    val remoteApiVersion: Long,
    val appVersion: String,
    val hostname: String,
    val controllerCount: Long,
    val robotCount: Long,
    val uptimeSeconds: Long,
    /** The addresses of this server on the local network. Present only while an administrator allowed it (discovery.advertiseAddress); a client must not rely on it. */
    val addresses: List<String>? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["schema_version"] = schemaVersion
        jsonOut["product"] = product
        jsonOut["remoteApiVersion"] = remoteApiVersion
        jsonOut["appVersion"] = appVersion
        jsonOut["hostname"] = hostname
        jsonOut["controllerCount"] = controllerCount
        jsonOut["robotCount"] = robotCount
        jsonOut["uptimeSeconds"] = uptimeSeconds
        if (addresses != null) jsonOut["addresses"] = addresses
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraHydraInfo = HydraHydraInfo(
            schemaVersion = json["schema_version"] as String,
            product = json["product"] as String,
            remoteApiVersion = (json["remoteApiVersion"] as Number).toLong(),
            appVersion = json["appVersion"] as String,
            hostname = json["hostname"] as String,
            controllerCount = (json["controllerCount"] as Number).toLong(),
            robotCount = (json["robotCount"] as Number).toLong(),
            uptimeSeconds = (json["uptimeSeconds"] as Number).toLong(),
            addresses = json["addresses"]?.let { v0 -> hydraList(v0).map { v1 -> v1 as String } },
        )
    }
}

/** An object of the server contract. */
data class HydraInfoTicket(
    /** Signed ticket for the read-only information routes; it goes in the address as ?ticket=. */
    val ticket: String,
    val expiresInSeconds: Long,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["ticket"] = ticket
        jsonOut["expiresInSeconds"] = expiresInSeconds
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraInfoTicket = HydraInfoTicket(
            ticket = json["ticket"] as String,
            expiresInSeconds = (json["expiresInSeconds"] as Number).toLong(),
        )
    }
}

/** A JSON Web Key Set (RFC 7517) with the public Ed25519 keys that verify the EdDSA sign-in tokens: the active one and, during the overlap of a rotation, the previous one. Public parameters only. */
data class HydraJwksDocument(
    val keys: List<HydraJwksDocumentKeysItem>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["keys"] = keys.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraJwksDocument = HydraJwksDocument(
            keys = hydraList(json["keys"]).map { v0 -> HydraJwksDocumentKeysItem.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraJwksDocumentKeysItem(
    val kty: String,
    val crv: String,
    /** The public key, base64url. */
    val x: String,
    /** The key id (the RFC 7638 thumbprint, shortened); the header of each token names it. */
    val kid: String,
    val use: String,
    val alg: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["kty"] = kty
        jsonOut["crv"] = crv
        jsonOut["x"] = x
        jsonOut["kid"] = kid
        jsonOut["use"] = use
        jsonOut["alg"] = alg
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraJwksDocumentKeysItem = HydraJwksDocumentKeysItem(
            kty = json["kty"] as String,
            crv = json["crv"] as String,
            x = json["x"] as String,
            kid = json["kid"] as String,
            use = json["use"] as String,
            alg = json["alg"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraJwtKeyRotated(
    val success: Boolean,
    /** The key id of the new active key. */
    val kid: String,
    val algorithm: String,
    val keys: List<HydraJwtKeyRotatedKeysItem>,
    val jwksPath: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["kid"] = kid
        jsonOut["algorithm"] = algorithm
        jsonOut["keys"] = keys.map { v0 -> v0.toJson() }
        jsonOut["jwksPath"] = jwksPath
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraJwtKeyRotated = HydraJwtKeyRotated(
            success = json["success"] as Boolean,
            kid = json["kid"] as String,
            algorithm = json["algorithm"] as String,
            keys = hydraList(json["keys"]).map { v0 -> HydraJwtKeyRotatedKeysItem.fromJson(hydraMap(v0)) },
            jwksPath = json["jwksPath"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraJwtKeyRotatedKeysItem(
    val kid: String,
    /** Unix seconds. */
    val createdAt: Long,
    /** Unix seconds; null for the active key. */
    val retiredAt: Long?,
    val active: Boolean,
    /** Unix seconds at which a retired key stops being accepted and published; null for the active key. */
    val acceptedUntil: Long?,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["kid"] = kid
        jsonOut["createdAt"] = createdAt
        jsonOut["retiredAt"] = retiredAt
        jsonOut["active"] = active
        jsonOut["acceptedUntil"] = acceptedUntil
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraJwtKeyRotatedKeysItem = HydraJwtKeyRotatedKeysItem(
            kid = json["kid"] as String,
            createdAt = (json["createdAt"] as Number).toLong(),
            retiredAt = json["retiredAt"]?.let { v0 -> (v0 as Number).toLong() },
            active = json["active"] as Boolean,
            acceptedUntil = json["acceptedUntil"]?.let { v0 -> (v0 as Number).toLong() },
        )
    }
}

/** The state of the token signing keys. Never any private part. */
data class HydraJwtKeys(
    val algorithm: String,
    val keys: List<HydraJwtKeysKeysItem>,
    val jwksPath: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["algorithm"] = algorithm
        jsonOut["keys"] = keys.map { v0 -> v0.toJson() }
        jsonOut["jwksPath"] = jwksPath
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraJwtKeys = HydraJwtKeys(
            algorithm = json["algorithm"] as String,
            keys = hydraList(json["keys"]).map { v0 -> HydraJwtKeysKeysItem.fromJson(hydraMap(v0)) },
            jwksPath = json["jwksPath"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraJwtKeysKeysItem(
    val kid: String,
    /** Unix seconds. */
    val createdAt: Long,
    /** Unix seconds; null for the active key. */
    val retiredAt: Long?,
    val active: Boolean,
    /** Unix seconds at which a retired key stops being accepted and published; null for the active key. */
    val acceptedUntil: Long?,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["kid"] = kid
        jsonOut["createdAt"] = createdAt
        jsonOut["retiredAt"] = retiredAt
        jsonOut["active"] = active
        jsonOut["acceptedUntil"] = acceptedUntil
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraJwtKeysKeysItem = HydraJwtKeysKeysItem(
            kid = json["kid"] as String,
            createdAt = (json["createdAt"] as Number).toLong(),
            retiredAt = json["retiredAt"]?.let { v0 -> (v0 as Number).toLong() },
            active = json["active"] as Boolean,
            acceptedUntil = json["acceptedUntil"]?.let { v0 -> (v0 as Number).toLong() },
        )
    }
}

/** An object of the server contract. */
data class HydraLiveActivityRegistered(
    val registered: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["registered"] = registered
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraLiveActivityRegistered = HydraLiveActivityRegistered(
            registered = json["registered"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraLiveActivityRemoved(
    val removed: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["removed"] = removed
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraLiveActivityRemoved = HydraLiveActivityRemoved(
            removed = json["removed"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraLogLines(
    val lines: List<String>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["lines"] = lines
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraLogLines = HydraLogLines(
            lines = hydraList(json["lines"]).map { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraLoginResult(
    val success: Boolean,
    val token: String,
    val refreshToken: String,
    val role: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["token"] = token
        jsonOut["refreshToken"] = refreshToken
        jsonOut["role"] = role
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraLoginResult = HydraLoginResult(
            success = json["success"] as Boolean,
            token = json["token"] as String,
            refreshToken = json["refreshToken"] as String,
            role = json["role"] as String,
        )
    }
}

/** What one run of the deploy tool of the operating system image did (status, install, rollback or prune). `result` is the JSON the tool printed on success (the state of the components, or the list of removed releases) and null otherwise; `message` is the last lines the tool printed on its error output, cut to a fixed size. */
data class HydraMaintenanceOutcome(
    val ok: Boolean,
    val action: String,
    val exitCode: Long,
    val timedOut: Boolean,
    val result: Any?,
    val message: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["ok"] = ok
        jsonOut["action"] = action
        jsonOut["exitCode"] = exitCode
        jsonOut["timedOut"] = timedOut
        jsonOut["result"] = result
        jsonOut["message"] = message
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraMaintenanceOutcome = HydraMaintenanceOutcome(
            ok = json["ok"] as Boolean,
            action = json["action"] as String,
            exitCode = (json["exitCode"] as Number).toLong(),
            timedOut = json["timedOut"] as Boolean,
            result = json["result"],
            message = json["message"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraModelList(
    val models: List<Map<String, Any?>>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["models"] = models
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraModelList = HydraModelList(
            models = hydraList(json["models"]).map { v0 -> hydraMap(v0) },
        )
    }
}

/** An object of the server contract. */
data class HydraModelSubmitted(
    val success: Boolean,
    val slug: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["slug"] = slug
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraModelSubmitted = HydraModelSubmitted(
            success = json["success"] as Boolean,
            slug = json["slug"] as String,
        )
    }
}

/** The last health frame that the kinematic brain heard from the controller board in a slot, read from the SPI bridge. Only on a server where nodeHealth.enabled is on (404 otherwise); for an operator or an administrator. Read only. */
data class HydraNodeHealth(
    /** False when the brain did not answer (its build has the health query off, or the link is down): then only slot and source carry anything. */
    val online: Boolean,
    val slot: Long,
    /** True when the brain has heard a health frame of the slot, false when it never has, null when it did not answer. */
    val heard: Boolean?,
    /** How long ago the brain heard it, in steps of 100 ms. */
    val ageMs: Long? = null,
    val sequence: Long? = null,
    val flags: Long? = null,
    val flagNames: List<String>? = null,
    val txErrors: Long? = null,
    val rxErrors: Long? = null,
    val stalls: Long? = null,
    /** Seconds since the board started, in steps of 16 (4080 means 4080 or more). */
    val uptimeS: Long? = null,
    val source: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["online"] = online
        jsonOut["slot"] = slot
        jsonOut["heard"] = heard
        if (ageMs != null) jsonOut["ageMs"] = ageMs
        if (sequence != null) jsonOut["sequence"] = sequence
        if (flags != null) jsonOut["flags"] = flags
        if (flagNames != null) jsonOut["flagNames"] = flagNames
        if (txErrors != null) jsonOut["txErrors"] = txErrors
        if (rxErrors != null) jsonOut["rxErrors"] = rxErrors
        if (stalls != null) jsonOut["stalls"] = stalls
        if (uptimeS != null) jsonOut["uptimeS"] = uptimeS
        jsonOut["source"] = source
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraNodeHealth = HydraNodeHealth(
            online = json["online"] as Boolean,
            slot = (json["slot"] as Number).toLong(),
            heard = json["heard"]?.let { v0 -> v0 as Boolean },
            ageMs = json["ageMs"]?.let { v0 -> (v0 as Number).toLong() },
            sequence = json["sequence"]?.let { v0 -> (v0 as Number).toLong() },
            flags = json["flags"]?.let { v0 -> (v0 as Number).toLong() },
            flagNames = json["flagNames"]?.let { v0 -> hydraList(v0).map { v1 -> v1 as String } },
            txErrors = json["txErrors"]?.let { v0 -> (v0 as Number).toLong() },
            rxErrors = json["rxErrors"]?.let { v0 -> (v0 as Number).toLong() },
            stalls = json["stalls"]?.let { v0 -> (v0 as Number).toLong() },
            uptimeS = json["uptimeS"]?.let { v0 -> (v0 as Number).toLong() },
            source = json["source"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraOperatorPresence(
    val state: String,
    val lastSequence: Long?,
    val secondsSinceBeat: Long?,
    val action: String,
    val timeoutSeconds: Double,
    val degradedRobots: List<Long>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["state"] = state
        jsonOut["lastSequence"] = lastSequence
        jsonOut["secondsSinceBeat"] = secondsSinceBeat
        jsonOut["action"] = action
        jsonOut["timeoutSeconds"] = timeoutSeconds
        jsonOut["degradedRobots"] = degradedRobots
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraOperatorPresence = HydraOperatorPresence(
            state = json["state"] as String,
            lastSequence = json["lastSequence"]?.let { v0 -> (v0 as Number).toLong() },
            secondsSinceBeat = json["secondsSinceBeat"]?.let { v0 -> (v0 as Number).toLong() },
            action = json["action"] as String,
            timeoutSeconds = (json["timeoutSeconds"] as Number).toDouble(),
            degradedRobots = hydraList(json["degradedRobots"]).map { v0 -> (v0 as Number).toLong() },
        )
    }
}

/** An object of the server contract. */
data class HydraOperatorPresenceAck(
    val accepted: Boolean,
    val duplicate: Boolean,
    val stale: Boolean,
    val state: String,
    val sequence: Long,
    val action: String,
    val timeoutSeconds: Double,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["accepted"] = accepted
        jsonOut["duplicate"] = duplicate
        jsonOut["stale"] = stale
        jsonOut["state"] = state
        jsonOut["sequence"] = sequence
        jsonOut["action"] = action
        jsonOut["timeoutSeconds"] = timeoutSeconds
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraOperatorPresenceAck = HydraOperatorPresenceAck(
            accepted = json["accepted"] as Boolean,
            duplicate = json["duplicate"] as Boolean,
            stale = json["stale"] as Boolean,
            state = json["state"] as String,
            sequence = (json["sequence"] as Number).toLong(),
            action = json["action"] as String,
            timeoutSeconds = (json["timeoutSeconds"] as Number).toDouble(),
        )
    }
}

/** An object of the server contract. */
data class HydraPostAdminDeviceTokensBody(
    val name: String,
    val username: String,
    val ttlDays: Double? = null,
    val confirm: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["name"] = name
        jsonOut["username"] = username
        if (ttlDays != null) jsonOut["ttlDays"] = ttlDays
        jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostAdminDeviceTokensBody = HydraPostAdminDeviceTokensBody(
            name = json["name"] as String,
            username = json["username"] as String,
            ttlDays = json["ttlDays"]?.let { v0 -> (v0 as Number).toDouble() },
            confirm = json["confirm"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPostAdminFleetUpdateApplyBody(
    val services: List<String>? = null,
    val confirm: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (services != null) jsonOut["services"] = services
        jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostAdminFleetUpdateApplyBody = HydraPostAdminFleetUpdateApplyBody(
            services = json["services"]?.let { v0 -> hydraList(v0).map { v1 -> v1 as String } },
            confirm = json["confirm"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPostAdminFleetUpdateResumeBody(
    val service: String,
    val confirm: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["service"] = service
        jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostAdminFleetUpdateResumeBody = HydraPostAdminFleetUpdateResumeBody(
            service = json["service"] as String,
            confirm = json["confirm"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPostAdminMaintenanceInstallBody(
    val packageValue: String,
    val allowDowngrade: Boolean? = null,
    val confirm: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["package"] = packageValue
        if (allowDowngrade != null) jsonOut["allowDowngrade"] = allowDowngrade
        jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostAdminMaintenanceInstallBody = HydraPostAdminMaintenanceInstallBody(
            packageValue = json["package"] as String,
            allowDowngrade = json["allowDowngrade"]?.let { v0 -> v0 as Boolean },
            confirm = json["confirm"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPostAdminMaintenancePruneBody(
    val component: String,
    val keep: Double? = null,
    val confirm: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["component"] = component
        if (keep != null) jsonOut["keep"] = keep
        jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostAdminMaintenancePruneBody = HydraPostAdminMaintenancePruneBody(
            component = json["component"] as String,
            keep = json["keep"]?.let { v0 -> (v0 as Number).toDouble() },
            confirm = json["confirm"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPostAdminMaintenanceRollbackBody(
    val component: String,
    val confirm: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["component"] = component
        jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostAdminMaintenanceRollbackBody = HydraPostAdminMaintenanceRollbackBody(
            component = json["component"] as String,
            confirm = json["confirm"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPostAdminSelfUpdateApplyBody(
    val component: String,
    val confirm: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["component"] = component
        jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostAdminSelfUpdateApplyBody = HydraPostAdminSelfUpdateApplyBody(
            component = json["component"] as String,
            confirm = json["confirm"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPostAdminSelfUpdateRollbackBody(
    val component: String,
    val confirm: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["component"] = component
        jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostAdminSelfUpdateRollbackBody = HydraPostAdminSelfUpdateRollbackBody(
            component = json["component"] as String,
            confirm = json["confirm"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPostCameraByIdPtzBody(
    val host: String,
    val port: Long? = null,
    val username: String? = null,
    val password: String? = null,
    val channel: Long? = null,
    val pan: Double? = null,
    val tilt: Double? = null,
    val zoom: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["host"] = host
        if (port != null) jsonOut["port"] = port
        if (username != null) jsonOut["username"] = username
        if (password != null) jsonOut["password"] = password
        if (channel != null) jsonOut["channel"] = channel
        if (pan != null) jsonOut["pan"] = pan
        if (tilt != null) jsonOut["tilt"] = tilt
        if (zoom != null) jsonOut["zoom"] = zoom
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostCameraByIdPtzBody = HydraPostCameraByIdPtzBody(
            host = json["host"] as String,
            port = json["port"]?.let { v0 -> (v0 as Number).toLong() },
            username = json["username"]?.let { v0 -> v0 as String },
            password = json["password"]?.let { v0 -> v0 as String },
            channel = json["channel"]?.let { v0 -> (v0 as Number).toLong() },
            pan = json["pan"]?.let { v0 -> (v0 as Number).toDouble() },
            tilt = json["tilt"]?.let { v0 -> (v0 as Number).toDouble() },
            zoom = json["zoom"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraPostCameraDiscoverRtspPathBody(
    val host: String,
    val port: Long? = null,
    val username: String? = null,
    val password: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["host"] = host
        if (port != null) jsonOut["port"] = port
        if (username != null) jsonOut["username"] = username
        if (password != null) jsonOut["password"] = password
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostCameraDiscoverRtspPathBody = HydraPostCameraDiscoverRtspPathBody(
            host = json["host"] as String,
            port = json["port"]?.let { v0 -> (v0 as Number).toLong() },
            username = json["username"]?.let { v0 -> v0 as String },
            password = json["password"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraPostConnectorHubGateSettingsBody(
    val allowLoopbackNoIdentity: Boolean,
    val confirm: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["allowLoopbackNoIdentity"] = allowLoopbackNoIdentity
        if (confirm != null) jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostConnectorHubGateSettingsBody = HydraPostConnectorHubGateSettingsBody(
            allowLoopbackNoIdentity = json["allowLoopbackNoIdentity"] as Boolean,
            confirm = json["confirm"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraPostConnectorHubGateSettingsResult(
    val allowLoopbackNoIdentity: Boolean,
    val loopbackSwitchAllowed: Boolean? = null,
    val verifiesTokens: Boolean? = null,
    val persisted: Boolean? = null,
    val changed: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["allowLoopbackNoIdentity"] = allowLoopbackNoIdentity
        if (loopbackSwitchAllowed != null) jsonOut["loopbackSwitchAllowed"] = loopbackSwitchAllowed
        if (verifiesTokens != null) jsonOut["verifiesTokens"] = verifiesTokens
        if (persisted != null) jsonOut["persisted"] = persisted
        if (changed != null) jsonOut["changed"] = changed
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostConnectorHubGateSettingsResult = HydraPostConnectorHubGateSettingsResult(
            allowLoopbackNoIdentity = json["allowLoopbackNoIdentity"] as Boolean,
            loopbackSwitchAllowed = json["loopbackSwitchAllowed"]?.let { v0 -> v0 as Boolean },
            verifiesTokens = json["verifiesTokens"]?.let { v0 -> v0 as Boolean },
            persisted = json["persisted"]?.let { v0 -> v0 as Boolean },
            changed = json["changed"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraPostDeviceLoginBody(
    val token: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["token"] = token
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostDeviceLoginBody = HydraPostDeviceLoginBody(
            token = json["token"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostDroidEstopSettingsBody(
    val enabled: Boolean,
    val confirm: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["enabled"] = enabled
        jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostDroidEstopSettingsBody = HydraPostDroidEstopSettingsBody(
            enabled = json["enabled"] as Boolean,
            confirm = json["confirm"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPostDroidEstopSettingsResult(
    val enabled: Boolean,
    val running: Boolean? = null,
    val changed: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["enabled"] = enabled
        if (running != null) jsonOut["running"] = running
        if (changed != null) jsonOut["changed"] = changed
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostDroidEstopSettingsResult = HydraPostDroidEstopSettingsResult(
            enabled = json["enabled"] as Boolean,
            running = json["running"]?.let { v0 -> v0 as Boolean },
            changed = json["changed"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraPostHardwareFramEraseBody(
    val confirm: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostHardwareFramEraseBody = HydraPostHardwareFramEraseBody(
            confirm = json["confirm"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostHilBridgeSettingsBody(
    val requireTwinPass: Boolean,
    val confirm: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["requireTwinPass"] = requireTwinPass
        jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostHilBridgeSettingsBody = HydraPostHilBridgeSettingsBody(
            requireTwinPass = json["requireTwinPass"] as Boolean,
            confirm = json["confirm"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPostHilBridgeSettingsResult(
    val requireTwinPass: Boolean,
    val locked: Boolean? = null,
    val persisted: Boolean? = null,
    val ready: Boolean? = null,
    val canChange: Boolean? = null,
    val changed: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["requireTwinPass"] = requireTwinPass
        if (locked != null) jsonOut["locked"] = locked
        if (persisted != null) jsonOut["persisted"] = persisted
        if (ready != null) jsonOut["ready"] = ready
        if (canChange != null) jsonOut["canChange"] = canChange
        if (changed != null) jsonOut["changed"] = changed
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostHilBridgeSettingsResult = HydraPostHilBridgeSettingsResult(
            requireTwinPass = json["requireTwinPass"] as Boolean,
            locked = json["locked"]?.let { v0 -> v0 as Boolean },
            persisted = json["persisted"]?.let { v0 -> v0 as Boolean },
            ready = json["ready"]?.let { v0 -> v0 as Boolean },
            canChange = json["canChange"]?.let { v0 -> v0 as Boolean },
            changed = json["changed"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraPostInfoTicketBody(
    val ttlSeconds: Any? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (ttlSeconds != null) jsonOut["ttlSeconds"] = ttlSeconds
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostInfoTicketBody = HydraPostInfoTicketBody(
            ttlSeconds = json["ttlSeconds"],
        )
    }
}

/** An object of the server contract. */
data class HydraPostIntegrationsTestConnectionBody(
    val host: String,
    val port: Long,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["host"] = host
        jsonOut["port"] = port
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostIntegrationsTestConnectionBody = HydraPostIntegrationsTestConnectionBody(
            host = json["host"] as String,
            port = (json["port"] as Number).toLong(),
        )
    }
}

/** An object of the server contract. */
data class HydraPostLoginBody(
    val username: String,
    val password: String,
    val totp: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["username"] = username
        jsonOut["password"] = password
        if (totp != null) jsonOut["totp"] = totp
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostLoginBody = HydraPostLoginBody(
            username = json["username"] as String,
            password = json["password"] as String,
            totp = json["totp"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraPostLogoutBody(
    val refreshToken: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (refreshToken != null) jsonOut["refreshToken"] = refreshToken
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostLogoutBody = HydraPostLogoutBody(
            refreshToken = json["refreshToken"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraPostModelsSubmitBody(
    val category: Any? = null,
    val meshFiles: Any? = null,
    val name: Any? = null,
    val overwrite: Any? = null,
    val urdfFilename: Any? = null,
    val urdfXml: Any? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (category != null) jsonOut["category"] = category
        if (meshFiles != null) jsonOut["meshFiles"] = meshFiles
        if (name != null) jsonOut["name"] = name
        if (overwrite != null) jsonOut["overwrite"] = overwrite
        if (urdfFilename != null) jsonOut["urdfFilename"] = urdfFilename
        if (urdfXml != null) jsonOut["urdfXml"] = urdfXml
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostModelsSubmitBody = HydraPostModelsSubmitBody(
            category = json["category"],
            meshFiles = json["meshFiles"],
            name = json["name"],
            overwrite = json["overwrite"],
            urdfFilename = json["urdfFilename"],
            urdfXml = json["urdfXml"],
        )
    }
}

/** An object of the server contract. */
data class HydraPostOperatorConfirmationsBody(
    val action: String,
    val jobId: String,
    val confirm: Boolean,
    val ttlSeconds: Long? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["action"] = action
        jsonOut["job_id"] = jobId
        jsonOut["confirm"] = confirm
        if (ttlSeconds != null) jsonOut["ttl_seconds"] = ttlSeconds
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostOperatorConfirmationsBody = HydraPostOperatorConfirmationsBody(
            action = json["action"] as String,
            jobId = json["job_id"] as String,
            confirm = json["confirm"] as Boolean,
            ttlSeconds = json["ttl_seconds"]?.let { v0 -> (v0 as Number).toLong() },
        )
    }
}

/** An object of the server contract. */
data class HydraPostOperatorConfirmationsResult(
    /** A JWT (HS256) valid once, for this action and this job only. Never stored or logged by the server. */
    val token: String,
    val action: String,
    val jobId: String,
    /** Unix seconds. */
    val expiresAt: Long,
    val ttlSeconds: Long,
    val singleUse: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["token"] = token
        jsonOut["action"] = action
        jsonOut["job_id"] = jobId
        jsonOut["expires_at"] = expiresAt
        jsonOut["ttl_seconds"] = ttlSeconds
        jsonOut["single_use"] = singleUse
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostOperatorConfirmationsResult = HydraPostOperatorConfirmationsResult(
            token = json["token"] as String,
            action = json["action"] as String,
            jobId = json["job_id"] as String,
            expiresAt = (json["expires_at"] as Number).toLong(),
            ttlSeconds = (json["ttl_seconds"] as Number).toLong(),
            singleUse = json["single_use"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPostOperatorPresenceBody(
    val type: String? = null,
    val protocolVersion: Long? = null,
    val sequence: Long,
    val intervalSeconds: Double,
    val state: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (type != null) jsonOut["type"] = type
        if (protocolVersion != null) jsonOut["protocolVersion"] = protocolVersion
        jsonOut["sequence"] = sequence
        jsonOut["intervalSeconds"] = intervalSeconds
        jsonOut["state"] = state
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostOperatorPresenceBody = HydraPostOperatorPresenceBody(
            type = json["type"]?.let { v0 -> v0 as String },
            protocolVersion = json["protocolVersion"]?.let { v0 -> (v0 as Number).toLong() },
            sequence = (json["sequence"] as Number).toLong(),
            intervalSeconds = (json["intervalSeconds"] as Number).toDouble(),
            state = json["state"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostOpsAgentProposalsDecideBody(
    val incidentId: String,
    val decision: String,
    val confirm: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["incidentId"] = incidentId
        jsonOut["decision"] = decision
        if (confirm != null) jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostOpsAgentProposalsDecideBody = HydraPostOpsAgentProposalsDecideBody(
            incidentId = json["incidentId"] as String,
            decision = json["decision"] as String,
            confirm = json["confirm"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraPostOpsAgentProposalsDecideResult(
    val decision: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (decision != null) jsonOut["decision"] = decision
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostOpsAgentProposalsDecideResult = HydraPostOpsAgentProposalsDecideResult(
            decision = json["decision"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraPostPushDevicesBody(
    val token: String,
    val platform: String,
    val locale: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["token"] = token
        jsonOut["platform"] = platform
        if (locale != null) jsonOut["locale"] = locale
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostPushDevicesBody = HydraPostPushDevicesBody(
            token = json["token"] as String,
            platform = json["platform"] as String,
            locale = json["locale"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraPostPushLiveActivitiesBody(
    val activityToken: String,
    val robotId: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["activityToken"] = activityToken
        jsonOut["robotId"] = robotId
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostPushLiveActivitiesBody = HydraPostPushLiveActivitiesBody(
            activityToken = json["activityToken"] as String,
            robotId = json["robotId"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostRefreshBody(
    val refreshToken: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["refreshToken"] = refreshToken
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostRefreshBody = HydraPostRefreshBody(
            refreshToken = json["refreshToken"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostRobotByIdClaimBody(
    val ttlMs: Double? = null,
    val force: Boolean? = null,
    val reason: String? = null,
    val controllerId: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (ttlMs != null) jsonOut["ttlMs"] = ttlMs
        if (force != null) jsonOut["force"] = force
        if (reason != null) jsonOut["reason"] = reason
        if (controllerId != null) jsonOut["controllerId"] = controllerId
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostRobotByIdClaimBody = HydraPostRobotByIdClaimBody(
            ttlMs = json["ttlMs"]?.let { v0 -> (v0 as Number).toDouble() },
            force = json["force"]?.let { v0 -> v0 as Boolean },
            reason = json["reason"]?.let { v0 -> v0 as String },
            controllerId = json["controllerId"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraPostRobotByIdClaimResult(
    val success: Boolean,
    val reservation: Map<String, Any?>,
    val reservationHistory: List<Map<String, Any?>>,
    val revision: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["reservation"] = reservation
        jsonOut["reservationHistory"] = reservationHistory
        jsonOut["revision"] = revision
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostRobotByIdClaimResult = HydraPostRobotByIdClaimResult(
            success = json["success"] as Boolean,
            reservation = hydraMap(json["reservation"]),
            reservationHistory = hydraList(json["reservationHistory"]).map { v0 -> hydraMap(v0) },
            revision = json["revision"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostRobotByIdCommandBody(
    /** One of the commands the server knows (an unknown one answers 400). */
    val command: String,
    val params: Map<String, Any?>? = null,
    val seq: Long? = null,
    val controllerId: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["command"] = command
        if (params != null) jsonOut["params"] = params
        if (seq != null) jsonOut["seq"] = seq
        if (controllerId != null) jsonOut["controllerId"] = controllerId
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostRobotByIdCommandBody = HydraPostRobotByIdCommandBody(
            command = json["command"] as String,
            params = json["params"]?.let { v0 -> hydraMap(v0) },
            seq = json["seq"]?.let { v0 -> (v0 as Number).toLong() },
            controllerId = json["controllerId"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraPostRobotByIdCommandResult(
    val success: Boolean,
    val affectedCount: Double? = null,
    val revision: String,
    val operationId: String? = null,
    val operation: Map<String, Any?>? = null,
    val lifecycle: Map<String, Any?>? = null,
    val applied: Map<String, Any?>? = null,
    val warnings: List<Any?>? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        if (affectedCount != null) jsonOut["affectedCount"] = affectedCount
        jsonOut["revision"] = revision
        if (operationId != null) jsonOut["operation_id"] = operationId
        if (operation != null) jsonOut["operation"] = operation
        if (lifecycle != null) jsonOut["lifecycle"] = lifecycle
        if (applied != null) jsonOut["applied"] = applied
        if (warnings != null) jsonOut["warnings"] = warnings
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostRobotByIdCommandResult = HydraPostRobotByIdCommandResult(
            success = json["success"] as Boolean,
            affectedCount = json["affectedCount"]?.let { v0 -> (v0 as Number).toDouble() },
            revision = json["revision"] as String,
            operationId = json["operation_id"]?.let { v0 -> v0 as String },
            operation = json["operation"]?.let { v0 -> hydraMap(v0) },
            lifecycle = json["lifecycle"]?.let { v0 -> hydraMap(v0) },
            applied = json["applied"]?.let { v0 -> hydraMap(v0) },
            warnings = json["warnings"]?.let { v0 -> hydraList(v0) },
        )
    }
}

/** An object of the server contract. */
data class HydraPostRobotByIdJogArmBody(
    val armed: Boolean,
    val ttlMs: Double? = null,
    val controllerId: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["armed"] = armed
        if (ttlMs != null) jsonOut["ttlMs"] = ttlMs
        if (controllerId != null) jsonOut["controllerId"] = controllerId
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostRobotByIdJogArmBody = HydraPostRobotByIdJogArmBody(
            armed = json["armed"] as Boolean,
            ttlMs = json["ttlMs"]?.let { v0 -> (v0 as Number).toDouble() },
            controllerId = json["controllerId"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraPostRobotByIdJogArmResult(
    val success: Boolean,
    val armed: Boolean,
    val expiresAt: Double? = null,
    val ttlMs: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["armed"] = armed
        if (expiresAt != null) jsonOut["expiresAt"] = expiresAt
        if (ttlMs != null) jsonOut["ttlMs"] = ttlMs
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostRobotByIdJogArmResult = HydraPostRobotByIdJogArmResult(
            success = json["success"] as Boolean,
            armed = json["armed"] as Boolean,
            expiresAt = json["expiresAt"]?.let { v0 -> (v0 as Number).toDouble() },
            ttlMs = json["ttlMs"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraPostRobotByIdReleaseBody(
    val reason: String? = null,
    val controllerId: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (reason != null) jsonOut["reason"] = reason
        if (controllerId != null) jsonOut["controllerId"] = controllerId
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostRobotByIdReleaseBody = HydraPostRobotByIdReleaseBody(
            reason = json["reason"]?.let { v0 -> v0 as String },
            controllerId = json["controllerId"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraPostRobotByIdReleaseResult(
    val success: Boolean,
    val reservationHistory: List<Map<String, Any?>>,
    val revision: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["reservationHistory"] = reservationHistory
        jsonOut["revision"] = revision
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostRobotByIdReleaseResult = HydraPostRobotByIdReleaseResult(
            success = json["success"] as Boolean,
            reservationHistory = hydraList(json["reservationHistory"]).map { v0 -> hydraMap(v0) },
            revision = json["revision"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostRos2BridgeSettingsBody(
    val requireSros2: Boolean,
    val confirm: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["requireSros2"] = requireSros2
        jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostRos2BridgeSettingsBody = HydraPostRos2BridgeSettingsBody(
            requireSros2 = json["requireSros2"] as Boolean,
            confirm = json["confirm"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPostRos2BridgeSettingsResult(
    val requireSros2: Boolean,
    val active: Boolean,
    val restartNeeded: Boolean,
    val canChange: Boolean,
    val environmentReady: Boolean,
    val changed: Boolean? = null,
    val appliesAfterRestart: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["requireSros2"] = requireSros2
        jsonOut["active"] = active
        jsonOut["restartNeeded"] = restartNeeded
        jsonOut["canChange"] = canChange
        jsonOut["environmentReady"] = environmentReady
        if (changed != null) jsonOut["changed"] = changed
        if (appliesAfterRestart != null) jsonOut["appliesAfterRestart"] = appliesAfterRestart
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostRos2BridgeSettingsResult = HydraPostRos2BridgeSettingsResult(
            requireSros2 = json["requireSros2"] as Boolean,
            active = json["active"] as Boolean,
            restartNeeded = json["restartNeeded"] as Boolean,
            canChange = json["canChange"] as Boolean,
            environmentReady = json["environmentReady"] as Boolean,
            changed = json["changed"]?.let { v0 -> v0 as Boolean },
            appliesAfterRestart = json["appliesAfterRestart"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraPostSemanticPlannerSettingsBody(
    val requireIdentity: Boolean,
    val confirm: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["requireIdentity"] = requireIdentity
        if (confirm != null) jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostSemanticPlannerSettingsBody = HydraPostSemanticPlannerSettingsBody(
            requireIdentity = json["requireIdentity"] as Boolean,
            confirm = json["confirm"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraPostSemanticPlannerSettingsResult(
    val requireIdentity: Boolean,
    val verifiesTokens: Boolean? = null,
    val persisted: Boolean? = null,
    val changed: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["requireIdentity"] = requireIdentity
        if (verifiesTokens != null) jsonOut["verifiesTokens"] = verifiesTokens
        if (persisted != null) jsonOut["persisted"] = persisted
        if (changed != null) jsonOut["changed"] = changed
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostSemanticPlannerSettingsResult = HydraPostSemanticPlannerSettingsResult(
            requireIdentity = json["requireIdentity"] as Boolean,
            verifiesTokens = json["verifiesTokens"]?.let { v0 -> v0 as Boolean },
            persisted = json["persisted"]?.let { v0 -> v0 as Boolean },
            changed = json["changed"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraPostSettingsResult(
    val success: Boolean,
    val revision: String,
    val warnings: List<Map<String, Any?>>? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["revision"] = revision
        if (warnings != null) jsonOut["warnings"] = warnings
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostSettingsResult = HydraPostSettingsResult(
            success = json["success"] as Boolean,
            revision = json["revision"] as String,
            warnings = json["warnings"]?.let { v0 -> hydraList(v0).map { v1 -> hydraMap(v1) } },
        )
    }
}

/** An object of the server contract. */
data class HydraPostSystemBluetoothPairBody(
    val mac: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["mac"] = mac
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostSystemBluetoothPairBody = HydraPostSystemBluetoothPairBody(
            mac = json["mac"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostSystemBluetoothPowerBody(
    val on: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["on"] = on
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostSystemBluetoothPowerBody = HydraPostSystemBluetoothPowerBody(
            on = json["on"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPostSystemBluetoothRemoveBody(
    val mac: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["mac"] = mac
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostSystemBluetoothRemoveBody = HydraPostSystemBluetoothRemoveBody(
            mac = json["mac"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostToolArmsResetBody(
    val robot: String,
    val toolId: Long,
    val confirm: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["robot"] = robot
        jsonOut["toolId"] = toolId
        jsonOut["confirm"] = confirm
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostToolArmsResetBody = HydraPostToolArmsResetBody(
            robot = json["robot"] as String,
            toolId = (json["toolId"] as Number).toLong(),
            confirm = json["confirm"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostTotpBeginBody(
    val password: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["password"] = password
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostTotpBeginBody = HydraPostTotpBeginBody(
            password = json["password"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostTotpConfirmBody(
    val code: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["code"] = code
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostTotpConfirmBody = HydraPostTotpConfirmBody(
            code = json["code"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostTotpDisableBody(
    val password: String,
    val code: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["password"] = password
        jsonOut["code"] = code
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostTotpDisableBody = HydraPostTotpDisableBody(
            password = json["password"] as String,
            code = json["code"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostTotpRecoveryCodesBody(
    val password: String,
    val code: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["password"] = password
        jsonOut["code"] = code
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostTotpRecoveryCodesBody = HydraPostTotpRecoveryCodesBody(
            password = json["password"] as String,
            code = json["code"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostUploadWorkBody(
    /** A folder inside the data folder of the server (no .. allowed). */
    val folderPath: String,
    /** The name of the file; only its last component is used. */
    val fileName: String,
    /** Any JSON value (the recorded points are an array); the server writes it pretty-printed as the file. */
    val content: Any?,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["folderPath"] = folderPath
        jsonOut["fileName"] = fileName
        jsonOut["content"] = content
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostUploadWorkBody = HydraPostUploadWorkBody(
            folderPath = json["folderPath"] as String,
            fileName = json["fileName"] as String,
            content = json["content"],
        )
    }
}

/** An object of the server contract. */
data class HydraPostUsersBody(
    val username: String,
    val password: String,
    val role: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["username"] = username
        jsonOut["password"] = password
        jsonOut["role"] = role
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostUsersBody = HydraPostUsersBody(
            username = json["username"] as String,
            password = json["password"] as String,
            role = json["role"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraPostVoiceConfirmBody(
    val confirmationToken: Any? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (confirmationToken != null) jsonOut["confirmationToken"] = confirmationToken
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostVoiceConfirmBody = HydraPostVoiceConfirmBody(
            confirmationToken = json["confirmationToken"],
        )
    }
}

/** An object of the server contract. */
data class HydraPostVoiceTurnBody(
    val locale: Any? = null,
    val requestId: Any? = null,
    val subject: Any? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (locale != null) jsonOut["locale"] = locale
        if (requestId != null) jsonOut["requestId"] = requestId
        if (subject != null) jsonOut["subject"] = subject
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPostVoiceTurnBody = HydraPostVoiceTurnBody(
            locale = json["locale"],
            requestId = json["requestId"],
            subject = json["subject"],
        )
    }
}

/** An object of the server contract. */
data class HydraPtzResult(
    val ok: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["ok"] = ok
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPtzResult = HydraPtzResult(
            ok = json["ok"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPushDeviceRegistered(
    val registered: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["registered"] = registered
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPushDeviceRegistered = HydraPushDeviceRegistered(
            registered = json["registered"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPushDeviceRemoved(
    val removed: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["removed"] = removed
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPushDeviceRemoved = HydraPushDeviceRemoved(
            removed = json["removed"] as Boolean,
        )
    }
}

/** The state of the push notifications of the server, for an administrator. It tells whether the credentials of the Apple push service are usable and why not, never the credentials or the device tokens. */
data class HydraPushStatus(
    val enabled: Boolean,
    val configured: Boolean,
    val problem: String?,
    val devices: Long,
    val sandbox: Boolean,
    val events: HydraPushStatusEvents,
    /** The Live Activity on the lock screen: whether it is sent (off by default), the most it may show (status, progress or full; status by default) and how many activities are registered. */
    val liveActivity: HydraPushStatusLiveActivity? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["enabled"] = enabled
        jsonOut["configured"] = configured
        jsonOut["problem"] = problem
        jsonOut["devices"] = devices
        jsonOut["sandbox"] = sandbox
        jsonOut["events"] = events.toJson()
        if (liveActivity != null) jsonOut["liveActivity"] = liveActivity.toJson()
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPushStatus = HydraPushStatus(
            enabled = json["enabled"] as Boolean,
            configured = json["configured"] as Boolean,
            problem = json["problem"]?.let { v0 -> v0 as String },
            devices = (json["devices"] as Number).toLong(),
            sandbox = json["sandbox"] as Boolean,
            events = HydraPushStatusEvents.fromJson(hydraMap(json["events"])),
            liveActivity = json["liveActivity"]?.let { v0 -> HydraPushStatusLiveActivity.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraPushStatusEvents(
    val jobFinished: Boolean,
    val globalStop: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["jobFinished"] = jobFinished
        jsonOut["globalStop"] = globalStop
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPushStatusEvents = HydraPushStatusEvents(
            jobFinished = json["jobFinished"] as Boolean,
            globalStop = json["globalStop"] as Boolean,
        )
    }
}

/** The Live Activity on the lock screen: whether it is sent (off by default), the most it may show (status, progress or full; status by default) and how many activities are registered. */
data class HydraPushStatusLiveActivity(
    val enabled: Boolean,
    val level: String,
    val activities: Long,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["enabled"] = enabled
        jsonOut["level"] = level
        jsonOut["activities"] = activities
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPushStatusLiveActivity = HydraPushStatusLiveActivity(
            enabled = json["enabled"] as Boolean,
            level = json["level"] as String,
            activities = (json["activities"] as Number).toLong(),
        )
    }
}

/** A patch of the safety limits: only the blocks and keys sent change, each inside the hard limits of the server. */
data class HydraPutAdminSafetyLimitsBody(
    val jog: HydraPutAdminSafetyLimitsBodyJog? = null,
    val temperature: HydraPutAdminSafetyLimitsBodyTemperature? = null,
    val claims: HydraPutAdminSafetyLimitsBodyClaims? = null,
    val audit: HydraPutAdminSafetyLimitsBodyAudit? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (jog != null) jsonOut["jog"] = jog.toJson()
        if (temperature != null) jsonOut["temperature"] = temperature.toJson()
        if (claims != null) jsonOut["claims"] = claims.toJson()
        if (audit != null) jsonOut["audit"] = audit.toJson()
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsBody = HydraPutAdminSafetyLimitsBody(
            jog = json["jog"]?.let { v0 -> HydraPutAdminSafetyLimitsBodyJog.fromJson(hydraMap(v0)) },
            temperature = json["temperature"]?.let { v0 -> HydraPutAdminSafetyLimitsBodyTemperature.fromJson(hydraMap(v0)) },
            claims = json["claims"]?.let { v0 -> HydraPutAdminSafetyLimitsBodyClaims.fromJson(hydraMap(v0)) },
            audit = json["audit"]?.let { v0 -> HydraPutAdminSafetyLimitsBodyAudit.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsBodyAudit(
    val enabled: Boolean? = null,
    val motionIntervalSeconds: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (enabled != null) jsonOut["enabled"] = enabled
        if (motionIntervalSeconds != null) jsonOut["motionIntervalSeconds"] = motionIntervalSeconds
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsBodyAudit = HydraPutAdminSafetyLimitsBodyAudit(
            enabled = json["enabled"]?.let { v0 -> v0 as Boolean },
            motionIntervalSeconds = json["motionIntervalSeconds"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsBodyClaims(
    val requireControllerId: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (requireControllerId != null) jsonOut["requireControllerId"] = requireControllerId
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsBodyClaims = HydraPutAdminSafetyLimitsBodyClaims(
            requireControllerId = json["requireControllerId"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsBodyJog(
    val armRequired: Boolean? = null,
    val armTtlMs: Double? = null,
    val default: HydraPutAdminSafetyLimitsBodyJogDefault? = null,
    val models: Map<String, Any?>? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (armRequired != null) jsonOut["armRequired"] = armRequired
        if (armTtlMs != null) jsonOut["armTtlMs"] = armTtlMs
        if (default != null) jsonOut["default"] = default.toJson()
        if (models != null) jsonOut["models"] = models
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsBodyJog = HydraPutAdminSafetyLimitsBodyJog(
            armRequired = json["armRequired"]?.let { v0 -> v0 as Boolean },
            armTtlMs = json["armTtlMs"]?.let { v0 -> (v0 as Number).toDouble() },
            default = json["default"]?.let { v0 -> HydraPutAdminSafetyLimitsBodyJogDefault.fromJson(hydraMap(v0)) },
            models = json["models"]?.let { v0 -> hydraMap(v0) },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsBodyJogDefault(
    val maxAmount: Double? = null,
    val maxAbsolute: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (maxAmount != null) jsonOut["maxAmount"] = maxAmount
        if (maxAbsolute != null) jsonOut["maxAbsolute"] = maxAbsolute
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsBodyJogDefault = HydraPutAdminSafetyLimitsBodyJogDefault(
            maxAmount = json["maxAmount"]?.let { v0 -> (v0 as Number).toDouble() },
            maxAbsolute = json["maxAbsolute"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsBodyTemperature(
    val default: HydraPutAdminSafetyLimitsBodyTemperatureDefault? = null,
    val models: Map<String, Any?>? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (default != null) jsonOut["default"] = default.toJson()
        if (models != null) jsonOut["models"] = models
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsBodyTemperature = HydraPutAdminSafetyLimitsBodyTemperature(
            default = json["default"]?.let { v0 -> HydraPutAdminSafetyLimitsBodyTemperatureDefault.fromJson(hydraMap(v0)) },
            models = json["models"]?.let { v0 -> hydraMap(v0) },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsBodyTemperatureDefault(
    val bedMaxC: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (bedMaxC != null) jsonOut["bedMaxC"] = bedMaxC
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsBodyTemperatureDefault = HydraPutAdminSafetyLimitsBodyTemperatureDefault(
            bedMaxC = json["bedMaxC"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsResult(
    val limits: HydraPutAdminSafetyLimitsResultLimits,
    val defaults: Map<String, Any?>? = null,
    val hardLimits: Map<String, Any?>? = null,
    val success: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["limits"] = limits.toJson()
        if (defaults != null) jsonOut["defaults"] = defaults
        if (hardLimits != null) jsonOut["hardLimits"] = hardLimits
        jsonOut["success"] = success
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsResult = HydraPutAdminSafetyLimitsResult(
            limits = HydraPutAdminSafetyLimitsResultLimits.fromJson(hydraMap(json["limits"])),
            defaults = json["defaults"]?.let { v0 -> hydraMap(v0) },
            hardLimits = json["hardLimits"]?.let { v0 -> hydraMap(v0) },
            success = json["success"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsResultLimits(
    val jog: HydraPutAdminSafetyLimitsResultLimitsJog? = null,
    val temperature: HydraPutAdminSafetyLimitsResultLimitsTemperature? = null,
    val claims: HydraPutAdminSafetyLimitsResultLimitsClaims? = null,
    val audit: HydraPutAdminSafetyLimitsResultLimitsAudit? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (jog != null) jsonOut["jog"] = jog.toJson()
        if (temperature != null) jsonOut["temperature"] = temperature.toJson()
        if (claims != null) jsonOut["claims"] = claims.toJson()
        if (audit != null) jsonOut["audit"] = audit.toJson()
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsResultLimits = HydraPutAdminSafetyLimitsResultLimits(
            jog = json["jog"]?.let { v0 -> HydraPutAdminSafetyLimitsResultLimitsJog.fromJson(hydraMap(v0)) },
            temperature = json["temperature"]?.let { v0 -> HydraPutAdminSafetyLimitsResultLimitsTemperature.fromJson(hydraMap(v0)) },
            claims = json["claims"]?.let { v0 -> HydraPutAdminSafetyLimitsResultLimitsClaims.fromJson(hydraMap(v0)) },
            audit = json["audit"]?.let { v0 -> HydraPutAdminSafetyLimitsResultLimitsAudit.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsResultLimitsAudit(
    val enabled: Boolean? = null,
    val motionIntervalSeconds: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (enabled != null) jsonOut["enabled"] = enabled
        if (motionIntervalSeconds != null) jsonOut["motionIntervalSeconds"] = motionIntervalSeconds
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsResultLimitsAudit = HydraPutAdminSafetyLimitsResultLimitsAudit(
            enabled = json["enabled"]?.let { v0 -> v0 as Boolean },
            motionIntervalSeconds = json["motionIntervalSeconds"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsResultLimitsClaims(
    val requireControllerId: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (requireControllerId != null) jsonOut["requireControllerId"] = requireControllerId
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsResultLimitsClaims = HydraPutAdminSafetyLimitsResultLimitsClaims(
            requireControllerId = json["requireControllerId"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsResultLimitsJog(
    val armRequired: Boolean? = null,
    val armTtlMs: Double? = null,
    val default: HydraPutAdminSafetyLimitsResultLimitsJogDefault? = null,
    val models: Map<String, Any?>? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (armRequired != null) jsonOut["armRequired"] = armRequired
        if (armTtlMs != null) jsonOut["armTtlMs"] = armTtlMs
        if (default != null) jsonOut["default"] = default.toJson()
        if (models != null) jsonOut["models"] = models
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsResultLimitsJog = HydraPutAdminSafetyLimitsResultLimitsJog(
            armRequired = json["armRequired"]?.let { v0 -> v0 as Boolean },
            armTtlMs = json["armTtlMs"]?.let { v0 -> (v0 as Number).toDouble() },
            default = json["default"]?.let { v0 -> HydraPutAdminSafetyLimitsResultLimitsJogDefault.fromJson(hydraMap(v0)) },
            models = json["models"]?.let { v0 -> hydraMap(v0) },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsResultLimitsJogDefault(
    val maxAmount: Double? = null,
    val maxAbsolute: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (maxAmount != null) jsonOut["maxAmount"] = maxAmount
        if (maxAbsolute != null) jsonOut["maxAbsolute"] = maxAbsolute
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsResultLimitsJogDefault = HydraPutAdminSafetyLimitsResultLimitsJogDefault(
            maxAmount = json["maxAmount"]?.let { v0 -> (v0 as Number).toDouble() },
            maxAbsolute = json["maxAbsolute"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsResultLimitsTemperature(
    val default: HydraPutAdminSafetyLimitsResultLimitsTemperatureDefault? = null,
    val models: Map<String, Any?>? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (default != null) jsonOut["default"] = default.toJson()
        if (models != null) jsonOut["models"] = models
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsResultLimitsTemperature = HydraPutAdminSafetyLimitsResultLimitsTemperature(
            default = json["default"]?.let { v0 -> HydraPutAdminSafetyLimitsResultLimitsTemperatureDefault.fromJson(hydraMap(v0)) },
            models = json["models"]?.let { v0 -> hydraMap(v0) },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminSafetyLimitsResultLimitsTemperatureDefault(
    val bedMaxC: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (bedMaxC != null) jsonOut["bedMaxC"] = bedMaxC
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminSafetyLimitsResultLimitsTemperatureDefault = HydraPutAdminSafetyLimitsResultLimitsTemperatureDefault(
            bedMaxC = json["bedMaxC"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** Every key is optional: port and any of the blocks of the security configuration. A key that is not one of them is ignored. */
data class HydraPutAdminServerConfigBody(
    /** The listen port, 1 to 65535; it applies when the server restarts. */
    val port: Long? = null,
    /** The options of the aiAccess block of the security configuration that the body changes; only the keys sent are changed. */
    val aiAccess: Map<String, Any?>? = null,
    /** The options of the infoAuth block of the security configuration that the body changes; only the keys sent are changed. */
    val infoAuth: Map<String, Any?>? = null,
    /** The options of the tls block of the security configuration that the body changes; only the keys sent are changed. */
    val tls: Map<String, Any?>? = null,
    /** The options of the ble block of the security configuration that the body changes; only the keys sent are changed. */
    val ble: Map<String, Any?>? = null,
    /** The options of the mqtt block of the security configuration that the body changes; only the keys sent are changed. */
    val mqtt: Map<String, Any?>? = null,
    /** The options of the voice block of the security configuration that the body changes; only the keys sent are changed. */
    val voice: Map<String, Any?>? = null,
    /** The options of the mavlink block of the security configuration that the body changes; only the keys sent are changed. */
    val mavlink: Map<String, Any?>? = null,
    /** The options of the robots block of the security configuration that the body changes; only the keys sent are changed. */
    val robots: Map<String, Any?>? = null,
    /** The options of the connections block of the security configuration that the body changes; only the keys sent are changed. */
    val connections: Map<String, Any?>? = null,
    /** The options of the health block of the security configuration that the body changes; only the keys sent are changed. */
    val health: Map<String, Any?>? = null,
    /** The options of the ecosystemHealth block of the security configuration that the body changes; only the keys sent are changed. */
    val ecosystemHealth: Map<String, Any?>? = null,
    /** The options of the nodeHealth block of the security configuration that the body changes; only the keys sent are changed. */
    val nodeHealth: Map<String, Any?>? = null,
    /** The options of the twinRelay block of the security configuration that the body changes; only the keys sent are changed. */
    val twinRelay: Map<String, Any?>? = null,
    /** The options of the infoTickets block of the security configuration that the body changes; only the keys sent are changed. */
    val infoTickets: Map<String, Any?>? = null,
    /** The options of the deviceTokens block of the security configuration that the body changes; only the keys sent are changed. */
    val deviceTokens: Map<String, Any?>? = null,
    /** The options of the updateCheck block of the security configuration that the body changes; only the keys sent are changed. */
    val updateCheck: Map<String, Any?>? = null,
    /** The options of the discovery block of the security configuration that the body changes; only the keys sent are changed. */
    val discovery: Map<String, Any?>? = null,
    /** The options of the maintenance block of the security configuration that the body changes; only the keys sent are changed. */
    val maintenance: Map<String, Any?>? = null,
    /** The options of the atc block of the security configuration that the body changes; only the keys sent are changed. */
    val atc: Map<String, Any?>? = null,
    /** The options of the detectionHef block of the security configuration that the body changes; only the keys sent are changed. */
    val detectionHef: Map<String, Any?>? = null,
    /** The options of the auth block of the security configuration that the body changes; only the keys sent are changed. */
    val auth: Map<String, Any?>? = null,
    /** The options of the presence block of the security configuration that the body changes; only the keys sent are changed. */
    val presence: Map<String, Any?>? = null,
    /** The options of the push block of the security configuration that the body changes; only the keys sent are changed. */
    val push: Map<String, Any?>? = null,
    /** The options of the trustedNetworks block of the security configuration that the body changes; only the keys sent are changed. */
    val trustedNetworks: Map<String, Any?>? = null,
    /** The options of the rul block of the security configuration that the body changes; only the keys sent are changed. */
    val rul: Map<String, Any?>? = null,
    /** The options of the safety block of the security configuration that the body changes; only the keys sent are changed. */
    val safety: Map<String, Any?>? = null,
    /** The options of the camera block of the security configuration that the body changes; only the keys sent are changed. */
    val camera: Map<String, Any?>? = null,
    /** The options of the install block of the security configuration that the body changes; only the keys sent are changed. */
    val install: Map<String, Any?>? = null,
    /** The options of the websocket block of the security configuration that the body changes; only the keys sent are changed. */
    val websocket: Map<String, Any?>? = null,
    /** The options of the logging block of the security configuration that the body changes; only the keys sent are changed. */
    val logging: Map<String, Any?>? = null,
    /** The options of the rateLimits block of the security configuration that the body changes; only the keys sent are changed. */
    val rateLimits: Map<String, Any?>? = null,
    /** The options of the bridges block of the security configuration that the body changes; only the keys sent are changed. */
    val bridges: Map<String, Any?>? = null,
    /** The options of the jobDispatcher block of the security configuration that the body changes; only the keys sent are changed. */
    val jobDispatcher: Map<String, Any?>? = null,
    /** The ingest switches (each true or false) and the file of the public keys of the operators that sign trajectory proposals; only the keys sent are changed, and an environment variable still locks its switch. */
    val ingest: HydraPutAdminServerConfigBodyIngest? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (port != null) jsonOut["port"] = port
        if (aiAccess != null) jsonOut["aiAccess"] = aiAccess
        if (infoAuth != null) jsonOut["infoAuth"] = infoAuth
        if (tls != null) jsonOut["tls"] = tls
        if (ble != null) jsonOut["ble"] = ble
        if (mqtt != null) jsonOut["mqtt"] = mqtt
        if (voice != null) jsonOut["voice"] = voice
        if (mavlink != null) jsonOut["mavlink"] = mavlink
        if (robots != null) jsonOut["robots"] = robots
        if (connections != null) jsonOut["connections"] = connections
        if (health != null) jsonOut["health"] = health
        if (ecosystemHealth != null) jsonOut["ecosystemHealth"] = ecosystemHealth
        if (nodeHealth != null) jsonOut["nodeHealth"] = nodeHealth
        if (twinRelay != null) jsonOut["twinRelay"] = twinRelay
        if (infoTickets != null) jsonOut["infoTickets"] = infoTickets
        if (deviceTokens != null) jsonOut["deviceTokens"] = deviceTokens
        if (updateCheck != null) jsonOut["updateCheck"] = updateCheck
        if (discovery != null) jsonOut["discovery"] = discovery
        if (maintenance != null) jsonOut["maintenance"] = maintenance
        if (atc != null) jsonOut["atc"] = atc
        if (detectionHef != null) jsonOut["detectionHef"] = detectionHef
        if (auth != null) jsonOut["auth"] = auth
        if (presence != null) jsonOut["presence"] = presence
        if (push != null) jsonOut["push"] = push
        if (trustedNetworks != null) jsonOut["trustedNetworks"] = trustedNetworks
        if (rul != null) jsonOut["rul"] = rul
        if (safety != null) jsonOut["safety"] = safety
        if (camera != null) jsonOut["camera"] = camera
        if (install != null) jsonOut["install"] = install
        if (websocket != null) jsonOut["websocket"] = websocket
        if (logging != null) jsonOut["logging"] = logging
        if (rateLimits != null) jsonOut["rateLimits"] = rateLimits
        if (bridges != null) jsonOut["bridges"] = bridges
        if (jobDispatcher != null) jsonOut["jobDispatcher"] = jobDispatcher
        if (ingest != null) jsonOut["ingest"] = ingest.toJson()
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminServerConfigBody = HydraPutAdminServerConfigBody(
            port = json["port"]?.let { v0 -> (v0 as Number).toLong() },
            aiAccess = json["aiAccess"]?.let { v0 -> hydraMap(v0) },
            infoAuth = json["infoAuth"]?.let { v0 -> hydraMap(v0) },
            tls = json["tls"]?.let { v0 -> hydraMap(v0) },
            ble = json["ble"]?.let { v0 -> hydraMap(v0) },
            mqtt = json["mqtt"]?.let { v0 -> hydraMap(v0) },
            voice = json["voice"]?.let { v0 -> hydraMap(v0) },
            mavlink = json["mavlink"]?.let { v0 -> hydraMap(v0) },
            robots = json["robots"]?.let { v0 -> hydraMap(v0) },
            connections = json["connections"]?.let { v0 -> hydraMap(v0) },
            health = json["health"]?.let { v0 -> hydraMap(v0) },
            ecosystemHealth = json["ecosystemHealth"]?.let { v0 -> hydraMap(v0) },
            nodeHealth = json["nodeHealth"]?.let { v0 -> hydraMap(v0) },
            twinRelay = json["twinRelay"]?.let { v0 -> hydraMap(v0) },
            infoTickets = json["infoTickets"]?.let { v0 -> hydraMap(v0) },
            deviceTokens = json["deviceTokens"]?.let { v0 -> hydraMap(v0) },
            updateCheck = json["updateCheck"]?.let { v0 -> hydraMap(v0) },
            discovery = json["discovery"]?.let { v0 -> hydraMap(v0) },
            maintenance = json["maintenance"]?.let { v0 -> hydraMap(v0) },
            atc = json["atc"]?.let { v0 -> hydraMap(v0) },
            detectionHef = json["detectionHef"]?.let { v0 -> hydraMap(v0) },
            auth = json["auth"]?.let { v0 -> hydraMap(v0) },
            presence = json["presence"]?.let { v0 -> hydraMap(v0) },
            push = json["push"]?.let { v0 -> hydraMap(v0) },
            trustedNetworks = json["trustedNetworks"]?.let { v0 -> hydraMap(v0) },
            rul = json["rul"]?.let { v0 -> hydraMap(v0) },
            safety = json["safety"]?.let { v0 -> hydraMap(v0) },
            camera = json["camera"]?.let { v0 -> hydraMap(v0) },
            install = json["install"]?.let { v0 -> hydraMap(v0) },
            websocket = json["websocket"]?.let { v0 -> hydraMap(v0) },
            logging = json["logging"]?.let { v0 -> hydraMap(v0) },
            rateLimits = json["rateLimits"]?.let { v0 -> hydraMap(v0) },
            bridges = json["bridges"]?.let { v0 -> hydraMap(v0) },
            jobDispatcher = json["jobDispatcher"]?.let { v0 -> hydraMap(v0) },
            ingest = json["ingest"]?.let { v0 -> HydraPutAdminServerConfigBodyIngest.fromJson(hydraMap(v0)) },
        )
    }
}

/** The ingest switches (each true or false) and the file of the public keys of the operators that sign trajectory proposals; only the keys sent are changed, and an environment variable still locks its switch. */
data class HydraPutAdminServerConfigBodyIngest(
    val faultFeed: Boolean? = null,
    val scenario: Boolean? = null,
    val developerNode: Boolean? = null,
    val anomalyFeed: Boolean? = null,
    val anomalyVoiceRelay: Boolean? = null,
    val voiceChain: Boolean? = null,
    val proposalVerify: Boolean? = null,
    val proposalKeysFile: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (faultFeed != null) jsonOut["faultFeed"] = faultFeed
        if (scenario != null) jsonOut["scenario"] = scenario
        if (developerNode != null) jsonOut["developerNode"] = developerNode
        if (anomalyFeed != null) jsonOut["anomalyFeed"] = anomalyFeed
        if (anomalyVoiceRelay != null) jsonOut["anomalyVoiceRelay"] = anomalyVoiceRelay
        if (voiceChain != null) jsonOut["voiceChain"] = voiceChain
        if (proposalVerify != null) jsonOut["proposalVerify"] = proposalVerify
        if (proposalKeysFile != null) jsonOut["proposalKeysFile"] = proposalKeysFile
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutAdminServerConfigBodyIngest = HydraPutAdminServerConfigBodyIngest(
            faultFeed = json["faultFeed"]?.let { v0 -> v0 as Boolean },
            scenario = json["scenario"]?.let { v0 -> v0 as Boolean },
            developerNode = json["developerNode"]?.let { v0 -> v0 as Boolean },
            anomalyFeed = json["anomalyFeed"]?.let { v0 -> v0 as Boolean },
            anomalyVoiceRelay = json["anomalyVoiceRelay"]?.let { v0 -> v0 as Boolean },
            voiceChain = json["voiceChain"]?.let { v0 -> v0 as Boolean },
            proposalVerify = json["proposalVerify"]?.let { v0 -> v0 as Boolean },
            proposalKeysFile = json["proposalKeysFile"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraPutAdminServerConfigResult(
    val success: Boolean,
    val appliesOnRestart: Boolean,
    val warnings: List<String>,
    /** The keys the contract does not list, kept as they came. */
    val additionalProperties: Map<String, Any?> = emptyMap(),
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut.putAll(additionalProperties)
        jsonOut["success"] = success
        jsonOut["appliesOnRestart"] = appliesOnRestart
        jsonOut["warnings"] = warnings
        return jsonOut
    }

    companion object {
        private val knownKeys: Set<String> = setOf("success", "appliesOnRestart", "warnings")

        fun fromJson(json: Map<String, Any?>): HydraPutAdminServerConfigResult = HydraPutAdminServerConfigResult(
            success = json["success"] as Boolean,
            appliesOnRestart = json["appliesOnRestart"] as Boolean,
            warnings = hydraList(json["warnings"]).map { v0 -> v0 as String },
            additionalProperties = hydraMap(json.filterKeys { it !in knownKeys }),
        )
    }
}

/** An object of the server contract. */
data class HydraPutSettingsResult(
    val success: Boolean,
    val revision: String,
    val warnings: List<Map<String, Any?>>? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["revision"] = revision
        if (warnings != null) jsonOut["warnings"] = warnings
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutSettingsResult = HydraPutSettingsResult(
            success = json["success"] as Boolean,
            revision = json["revision"] as String,
            warnings = json["warnings"]?.let { v0 -> hydraList(v0).map { v1 -> hydraMap(v1) } },
        )
    }
}

/** plan is the whole plan; expectedHash is the hash read last (the data lake refuses a plan that changed meanwhile); confirmDelete is needed to switch real deletion on; preview only asks what saving would do. */
data class HydraPutTelemetryDownsamplePlanBody(
    val plan: HydraPutTelemetryDownsamplePlanBodyPlan,
    val expectedHash: String? = null,
    val confirmDelete: Boolean? = null,
    val preview: Boolean? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["plan"] = plan.toJson()
        if (expectedHash != null) jsonOut["expectedHash"] = expectedHash
        if (confirmDelete != null) jsonOut["confirmDelete"] = confirmDelete
        if (preview != null) jsonOut["preview"] = preview
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutTelemetryDownsamplePlanBody = HydraPutTelemetryDownsamplePlanBody(
            plan = HydraPutTelemetryDownsamplePlanBodyPlan.fromJson(hydraMap(json["plan"])),
            expectedHash = json["expectedHash"]?.let { v0 -> v0 as String },
            confirmDelete = json["confirmDelete"]?.let { v0 -> v0 as Boolean },
            preview = json["preview"]?.let { v0 -> v0 as Boolean },
        )
    }
}

/** An object of the server contract. */
data class HydraPutTelemetryDownsamplePlanBodyPlan(
    val tiers: List<HydraPutTelemetryDownsamplePlanBodyPlanTiersItem>,
    val delete: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["tiers"] = tiers.map { v0 -> v0.toJson() }
        jsonOut["delete"] = delete
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutTelemetryDownsamplePlanBodyPlan = HydraPutTelemetryDownsamplePlanBodyPlan(
            tiers = hydraList(json["tiers"]).map { v0 -> HydraPutTelemetryDownsamplePlanBodyPlanTiersItem.fromJson(hydraMap(v0)) },
            delete = json["delete"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraPutTelemetryDownsamplePlanBodyPlanTiersItem(
    val kind: String,
    val field: String,
    /** How long raw points are kept: milliseconds or text such as 30d. */
    val raw: Any? = null,
    /** Width of the rollup bucket. */
    val bucket: Any? = null,
    /** Width of the fine rollup bucket. */
    val fineBucket: Any? = null,
    /** How long rollups are kept. */
    val rollupRetention: Any? = null,
    /** How long fine rollups are kept. */
    val fineRetention: Any? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["kind"] = kind
        jsonOut["field"] = field
        if (raw != null) jsonOut["raw"] = raw
        if (bucket != null) jsonOut["bucket"] = bucket
        if (fineBucket != null) jsonOut["fineBucket"] = fineBucket
        if (rollupRetention != null) jsonOut["rollupRetention"] = rollupRetention
        if (fineRetention != null) jsonOut["fineRetention"] = fineRetention
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutTelemetryDownsamplePlanBodyPlanTiersItem = HydraPutTelemetryDownsamplePlanBodyPlanTiersItem(
            kind = json["kind"] as String,
            field = json["field"] as String,
            raw = json["raw"],
            bucket = json["bucket"],
            fineBucket = json["fineBucket"],
            rollupRetention = json["rollupRetention"],
            fineRetention = json["fineRetention"],
        )
    }
}

/** An object of the server contract. */
data class HydraPutTelemetryDownsamplePlanResult(
    val saved: Boolean,
    val preview: Boolean? = null,
    val unchanged: Boolean? = null,
    val hash: String,
    val previousHash: String? = null,
    val tiers: List<Map<String, Any?>>? = null,
    val mode: String? = null,
    val changes: List<Map<String, Any?>>? = null,
    val warnings: List<String>? = null,
    val effects: HydraPutTelemetryDownsamplePlanResultEffects? = null,
    val currentEffects: HydraPutTelemetryDownsamplePlanResultCurrentEffects? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["saved"] = saved
        if (preview != null) jsonOut["preview"] = preview
        if (unchanged != null) jsonOut["unchanged"] = unchanged
        jsonOut["hash"] = hash
        if (previousHash != null) jsonOut["previousHash"] = previousHash
        if (tiers != null) jsonOut["tiers"] = tiers
        if (mode != null) jsonOut["mode"] = mode
        if (changes != null) jsonOut["changes"] = changes
        if (warnings != null) jsonOut["warnings"] = warnings
        if (effects != null) jsonOut["effects"] = effects.toJson()
        if (currentEffects != null) jsonOut["currentEffects"] = currentEffects.toJson()
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutTelemetryDownsamplePlanResult = HydraPutTelemetryDownsamplePlanResult(
            saved = json["saved"] as Boolean,
            preview = json["preview"]?.let { v0 -> v0 as Boolean },
            unchanged = json["unchanged"]?.let { v0 -> v0 as Boolean },
            hash = json["hash"] as String,
            previousHash = json["previousHash"]?.let { v0 -> v0 as String },
            tiers = json["tiers"]?.let { v0 -> hydraList(v0).map { v1 -> hydraMap(v1) } },
            mode = json["mode"]?.let { v0 -> v0 as String },
            changes = json["changes"]?.let { v0 -> hydraList(v0).map { v1 -> hydraMap(v1) } },
            warnings = json["warnings"]?.let { v0 -> hydraList(v0).map { v1 -> v1 as String } },
            effects = json["effects"]?.let { v0 -> HydraPutTelemetryDownsamplePlanResultEffects.fromJson(hydraMap(v0)) },
            currentEffects = json["currentEffects"]?.let { v0 -> HydraPutTelemetryDownsamplePlanResultCurrentEffects.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraPutTelemetryDownsamplePlanResultCurrentEffects(
    val totals: HydraPutTelemetryDownsamplePlanResultCurrentEffectsTotals? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (totals != null) jsonOut["totals"] = totals.toJson()
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutTelemetryDownsamplePlanResultCurrentEffects = HydraPutTelemetryDownsamplePlanResultCurrentEffects(
            totals = json["totals"]?.let { v0 -> HydraPutTelemetryDownsamplePlanResultCurrentEffectsTotals.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraPutTelemetryDownsamplePlanResultCurrentEffectsTotals(
    val rawPointsToRollUp: Double? = null,
    val rollupsToExpire: Double? = null,
    val fineRollupsToExpire: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (rawPointsToRollUp != null) jsonOut["rawPointsToRollUp"] = rawPointsToRollUp
        if (rollupsToExpire != null) jsonOut["rollupsToExpire"] = rollupsToExpire
        if (fineRollupsToExpire != null) jsonOut["fineRollupsToExpire"] = fineRollupsToExpire
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutTelemetryDownsamplePlanResultCurrentEffectsTotals = HydraPutTelemetryDownsamplePlanResultCurrentEffectsTotals(
            rawPointsToRollUp = json["rawPointsToRollUp"]?.let { v0 -> (v0 as Number).toDouble() },
            rollupsToExpire = json["rollupsToExpire"]?.let { v0 -> (v0 as Number).toDouble() },
            fineRollupsToExpire = json["fineRollupsToExpire"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraPutTelemetryDownsamplePlanResultEffects(
    val totals: HydraPutTelemetryDownsamplePlanResultEffectsTotals? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (totals != null) jsonOut["totals"] = totals.toJson()
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutTelemetryDownsamplePlanResultEffects = HydraPutTelemetryDownsamplePlanResultEffects(
            totals = json["totals"]?.let { v0 -> HydraPutTelemetryDownsamplePlanResultEffectsTotals.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraPutTelemetryDownsamplePlanResultEffectsTotals(
    val rawPointsToRollUp: Double? = null,
    val rollupsToExpire: Double? = null,
    val fineRollupsToExpire: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (rawPointsToRollUp != null) jsonOut["rawPointsToRollUp"] = rawPointsToRollUp
        if (rollupsToExpire != null) jsonOut["rollupsToExpire"] = rollupsToExpire
        if (fineRollupsToExpire != null) jsonOut["fineRollupsToExpire"] = fineRollupsToExpire
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutTelemetryDownsamplePlanResultEffectsTotals = HydraPutTelemetryDownsamplePlanResultEffectsTotals(
            rawPointsToRollUp = json["rawPointsToRollUp"]?.let { v0 -> (v0 as Number).toDouble() },
            rollupsToExpire = json["rollupsToExpire"]?.let { v0 -> (v0 as Number).toDouble() },
            fineRollupsToExpire = json["fineRollupsToExpire"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraPutUsersByUsernameBody(
    val newUsername: String? = null,
    val password: String? = null,
    val role: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (newUsername != null) jsonOut["newUsername"] = newUsername
        if (password != null) jsonOut["password"] = password
        if (role != null) jsonOut["role"] = role
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraPutUsersByUsernameBody = HydraPutUsersByUsernameBody(
            newUsername = json["newUsername"]?.let { v0 -> v0 as String },
            password = json["password"]?.let { v0 -> v0 as String },
            role = json["role"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraReachable(
    val reachable: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["reachable"] = reachable
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraReachable = HydraReachable(
            reachable = json["reachable"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraRobotLiveness(
    val schemaVersion: String,
    val staleAfterS: Long,
    val robots: List<HydraRobotLivenessRobotsItem>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["schema_version"] = schemaVersion
        jsonOut["stale_after_s"] = staleAfterS
        jsonOut["robots"] = robots.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraRobotLiveness = HydraRobotLiveness(
            schemaVersion = json["schema_version"] as String,
            staleAfterS = (json["stale_after_s"] as Number).toLong(),
            robots = hydraList(json["robots"]).map { v0 -> HydraRobotLivenessRobotsItem.fromJson(hydraMap(v0)) },
        )
    }
}

/** state is live (news within stale_after_s), stale (older news) or unknown (none since the server started). The flag online of the roster is not read. */
data class HydraRobotLivenessRobotsItem(
    val controllerId: String,
    val robotId: Long,
    val state: String,
    val lastUpdateUtc: String? = null,
    val ageS: Long? = null,
    /** state (a command or a change of its state) or heartbeat. */
    val source: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["controller_id"] = controllerId
        jsonOut["robot_id"] = robotId
        jsonOut["state"] = state
        if (lastUpdateUtc != null) jsonOut["last_update_utc"] = lastUpdateUtc
        if (ageS != null) jsonOut["age_s"] = ageS
        if (source != null) jsonOut["source"] = source
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraRobotLivenessRobotsItem = HydraRobotLivenessRobotsItem(
            controllerId = json["controller_id"] as String,
            robotId = (json["robot_id"] as Number).toLong(),
            state = json["state"] as String,
            lastUpdateUtc = json["last_update_utc"]?.let { v0 -> v0 as String },
            ageS = json["age_s"]?.let { v0 -> (v0 as Number).toLong() },
            source = json["source"]?.let { v0 -> v0 as String },
        )
    }
}

/** What a signed-in client may read of the remaining-useful-life relay: whether an operator may use it and the two limits that size a request. Nothing else; closed (enabled false, 5000 points, 8000 ms) when the configuration is missing or damaged. */
data class HydraRulConfig(
    /** True only when the relay is open to operators (rul.enabled, or HYDRA_UMC_RUL=1). */
    val enabled: Boolean,
    /** Largest number of points the relay accepts in one request. */
    val maxPoints: Long,
    /** How long the relay waits for the detector, in milliseconds. */
    val timeoutMs: Long,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["enabled"] = enabled
        jsonOut["maxPoints"] = maxPoints
        jsonOut["timeoutMs"] = timeoutMs
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraRulConfig = HydraRulConfig(
            enabled = json["enabled"] as Boolean,
            maxPoints = (json["maxPoints"] as Number).toLong(),
            timeoutMs = (json["timeoutMs"] as Number).toLong(),
        )
    }
}

/** The limits every client is held to (data/safety-limits.json), as saved by PUT /api/admin/safety-limits. */
data class HydraSafetyLimitsConfig(
    val jog: HydraSafetyLimitsConfigJog,
    val temperature: HydraSafetyLimitsConfigTemperature,
    val claims: HydraSafetyLimitsConfigClaims,
    val audit: HydraSafetyLimitsConfigAudit,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["jog"] = jog.toJson()
        jsonOut["temperature"] = temperature.toJson()
        jsonOut["claims"] = claims.toJson()
        jsonOut["audit"] = audit.toJson()
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSafetyLimitsConfig = HydraSafetyLimitsConfig(
            jog = HydraSafetyLimitsConfigJog.fromJson(hydraMap(json["jog"])),
            temperature = HydraSafetyLimitsConfigTemperature.fromJson(hydraMap(json["temperature"])),
            claims = HydraSafetyLimitsConfigClaims.fromJson(hydraMap(json["claims"])),
            audit = HydraSafetyLimitsConfigAudit.fromJson(hydraMap(json["audit"])),
        )
    }
}

/** An object of the server contract. */
data class HydraSafetyLimitsConfigAudit(
    val enabled: Boolean,
    val motionIntervalSeconds: Double,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["enabled"] = enabled
        jsonOut["motionIntervalSeconds"] = motionIntervalSeconds
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSafetyLimitsConfigAudit = HydraSafetyLimitsConfigAudit(
            enabled = json["enabled"] as Boolean,
            motionIntervalSeconds = (json["motionIntervalSeconds"] as Number).toDouble(),
        )
    }
}

/** An object of the server contract. */
data class HydraSafetyLimitsConfigClaims(
    val requireControllerId: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["requireControllerId"] = requireControllerId
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSafetyLimitsConfigClaims = HydraSafetyLimitsConfigClaims(
            requireControllerId = json["requireControllerId"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraSafetyLimitsConfigJog(
    val armRequired: Boolean,
    val armTtlMs: Double,
    val default: HydraSafetyLimitsConfigJogDefault,
    /** Per model (lower-case name before the parenthesis), the entries that differ from the default. */
    val models: Map<String, HydraSafetyLimitsConfigJogModelsValue>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["armRequired"] = armRequired
        jsonOut["armTtlMs"] = armTtlMs
        jsonOut["default"] = default.toJson()
        jsonOut["models"] = models.mapValues { (_, v0) -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSafetyLimitsConfigJog = HydraSafetyLimitsConfigJog(
            armRequired = json["armRequired"] as Boolean,
            armTtlMs = (json["armTtlMs"] as Number).toDouble(),
            default = HydraSafetyLimitsConfigJogDefault.fromJson(hydraMap(json["default"])),
            models = hydraMap(json["models"]).mapValues { (_, v0) -> HydraSafetyLimitsConfigJogModelsValue.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraSafetyLimitsConfigJogDefault(
    val maxAmount: Double,
    val maxAbsolute: Double,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["maxAmount"] = maxAmount
        jsonOut["maxAbsolute"] = maxAbsolute
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSafetyLimitsConfigJogDefault = HydraSafetyLimitsConfigJogDefault(
            maxAmount = (json["maxAmount"] as Number).toDouble(),
            maxAbsolute = (json["maxAbsolute"] as Number).toDouble(),
        )
    }
}

/** The limits of a relative and an absolute jog; a model entry names only what it changes. */
data class HydraSafetyLimitsConfigJogModelsValue(
    val maxAmount: Double? = null,
    val maxAbsolute: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (maxAmount != null) jsonOut["maxAmount"] = maxAmount
        if (maxAbsolute != null) jsonOut["maxAbsolute"] = maxAbsolute
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSafetyLimitsConfigJogModelsValue = HydraSafetyLimitsConfigJogModelsValue(
            maxAmount = json["maxAmount"]?.let { v0 -> (v0 as Number).toDouble() },
            maxAbsolute = json["maxAbsolute"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraSafetyLimitsConfigTemperature(
    val default: HydraSafetyLimitsConfigTemperatureDefault,
    val models: Map<String, HydraSafetyLimitsConfigTemperatureModelsValue>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["default"] = default.toJson()
        jsonOut["models"] = models.mapValues { (_, v0) -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSafetyLimitsConfigTemperature = HydraSafetyLimitsConfigTemperature(
            default = HydraSafetyLimitsConfigTemperatureDefault.fromJson(hydraMap(json["default"])),
            models = hydraMap(json["models"]).mapValues { (_, v0) -> HydraSafetyLimitsConfigTemperatureModelsValue.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraSafetyLimitsConfigTemperatureDefault(
    val bedMaxC: Double,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["bedMaxC"] = bedMaxC
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSafetyLimitsConfigTemperatureDefault = HydraSafetyLimitsConfigTemperatureDefault(
            bedMaxC = (json["bedMaxC"] as Number).toDouble(),
        )
    }
}

/** An object of the server contract. */
data class HydraSafetyLimitsConfigTemperatureModelsValue(
    val bedMaxC: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (bedMaxC != null) jsonOut["bedMaxC"] = bedMaxC
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSafetyLimitsConfigTemperatureModelsValue = HydraSafetyLimitsConfigTemperatureModelsValue(
            bedMaxC = json["bedMaxC"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** GET /api/safety-limits: the limits in force, the defaults, the ceilings no value can pass and, when ?robotId= names a robot, the limits that apply to it. */
data class HydraSafetyLimitsView(
    val limits: HydraSafetyLimitsConfig,
    val defaults: HydraSafetyLimitsConfig,
    /** The fixed ceilings (jogMaxAmount, jogMaxAbsolute, armTtlMs {min,max}, bedMaxC, auditMotionIntervalSeconds {min,max}); the set grows with the server. */
    val hardLimits: Map<String, Any?>,
    val robot: HydraSafetyLimitsViewRobot? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["limits"] = limits.toJson()
        jsonOut["defaults"] = defaults.toJson()
        jsonOut["hardLimits"] = hardLimits
        if (robot != null) jsonOut["robot"] = robot.toJson()
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSafetyLimitsView = HydraSafetyLimitsView(
            limits = HydraSafetyLimitsConfig.fromJson(hydraMap(json["limits"])),
            defaults = HydraSafetyLimitsConfig.fromJson(hydraMap(json["defaults"])),
            hardLimits = hydraMap(json["hardLimits"]),
            robot = json["robot"]?.let { v0 -> HydraSafetyLimitsViewRobot.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraSafetyLimitsViewRobot(
    val id: Long,
    val model: String? = null,
    val jog: HydraSafetyLimitsViewRobotJog,
    val temperature: HydraSafetyLimitsViewRobotTemperature,
    /** Milliseconds since the epoch; null when the jog is not armed. */
    val jogArmedUntil: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["id"] = id
        if (model != null) jsonOut["model"] = model
        jsonOut["jog"] = jog.toJson()
        jsonOut["temperature"] = temperature.toJson()
        if (jogArmedUntil != null) jsonOut["jogArmedUntil"] = jogArmedUntil
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSafetyLimitsViewRobot = HydraSafetyLimitsViewRobot(
            id = (json["id"] as Number).toLong(),
            model = json["model"]?.let { v0 -> v0 as String },
            jog = HydraSafetyLimitsViewRobotJog.fromJson(hydraMap(json["jog"])),
            temperature = HydraSafetyLimitsViewRobotTemperature.fromJson(hydraMap(json["temperature"])),
            jogArmedUntil = json["jogArmedUntil"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraSafetyLimitsViewRobotJog(
    val maxAmount: Double? = null,
    val maxAbsolute: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (maxAmount != null) jsonOut["maxAmount"] = maxAmount
        if (maxAbsolute != null) jsonOut["maxAbsolute"] = maxAbsolute
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSafetyLimitsViewRobotJog = HydraSafetyLimitsViewRobotJog(
            maxAmount = json["maxAmount"]?.let { v0 -> (v0 as Number).toDouble() },
            maxAbsolute = json["maxAbsolute"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraSafetyLimitsViewRobotTemperature(
    val bedMaxC: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (bedMaxC != null) jsonOut["bedMaxC"] = bedMaxC
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSafetyLimitsViewRobotTemperature = HydraSafetyLimitsViewRobotTemperature(
            bedMaxC = json["bedMaxC"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraSelfUpdateItem(
    val id: String,
    val repo: String,
    val installed: String?,
    val previous: String?,
    val latest: String?,
    val state: String,
    /** Whether the newest release carries the package, its hash and its signature. */
    val signedPackage: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["id"] = id
        jsonOut["repo"] = repo
        jsonOut["installed"] = installed
        jsonOut["previous"] = previous
        jsonOut["latest"] = latest
        jsonOut["state"] = state
        jsonOut["signedPackage"] = signedPackage
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSelfUpdateItem = HydraSelfUpdateItem(
            id = json["id"] as String,
            repo = json["repo"] as String,
            installed = json["installed"]?.let { v0 -> v0 as String },
            previous = json["previous"]?.let { v0 -> v0 as String },
            latest = json["latest"]?.let { v0 -> v0 as String },
            state = json["state"] as String,
            signedPackage = json["signedPackage"] as Boolean,
        )
    }
}

/** One update (or way back) of a program of this machine, step by step. It lives in a file, so it can be read again after the server restarts. */
data class HydraSelfUpdateJob(
    val id: String,
    val action: String,
    val component: String,
    val state: String,
    val fromVersion: String?,
    val targetVersion: String?,
    val startedAt: String,
    val updatedAt: String,
    val error: String?,
    val detail: String,
    val packageName: String? = null,
    val log: List<HydraSelfUpdateJobLogItem>,
    val by: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["id"] = id
        jsonOut["action"] = action
        jsonOut["component"] = component
        jsonOut["state"] = state
        jsonOut["fromVersion"] = fromVersion
        jsonOut["targetVersion"] = targetVersion
        jsonOut["startedAt"] = startedAt
        jsonOut["updatedAt"] = updatedAt
        jsonOut["error"] = error
        jsonOut["detail"] = detail
        if (packageName != null) jsonOut["packageName"] = packageName
        jsonOut["log"] = log.map { v0 -> v0.toJson() }
        jsonOut["by"] = by
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSelfUpdateJob = HydraSelfUpdateJob(
            id = json["id"] as String,
            action = json["action"] as String,
            component = json["component"] as String,
            state = json["state"] as String,
            fromVersion = json["fromVersion"]?.let { v0 -> v0 as String },
            targetVersion = json["targetVersion"]?.let { v0 -> v0 as String },
            startedAt = json["startedAt"] as String,
            updatedAt = json["updatedAt"] as String,
            error = json["error"]?.let { v0 -> v0 as String },
            detail = json["detail"] as String,
            packageName = json["packageName"]?.let { v0 -> v0 as String },
            log = hydraList(json["log"]).map { v0 -> HydraSelfUpdateJobLogItem.fromJson(hydraMap(v0)) },
            by = json["by"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraSelfUpdateJobLogItem(
    val at: String,
    val step: String,
    val text: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["at"] = at
        jsonOut["step"] = step
        jsonOut["text"] = text
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSelfUpdateJobLogItem = HydraSelfUpdateJobLogItem(
            at = json["at"] as String,
            step = json["step"] as String,
            text = json["text"] as String,
        )
    }
}

/** The programs of this machine set against the newest signed release of each, whether applying is switched on, and the job that is going on or the last one. */
data class HydraSelfUpdateStatus(
    val checkedAt: String?,
    val owner: String,
    val rateLimited: Boolean,
    val items: List<HydraSelfUpdateItem>,
    val applyEnabled: Boolean,
    val job: HydraSelfUpdateJob?,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["checkedAt"] = checkedAt
        jsonOut["owner"] = owner
        jsonOut["rateLimited"] = rateLimited
        jsonOut["items"] = items.map { v0 -> v0.toJson() }
        jsonOut["applyEnabled"] = applyEnabled
        jsonOut["job"] = job?.toJson()
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSelfUpdateStatus = HydraSelfUpdateStatus(
            checkedAt = json["checkedAt"]?.let { v0 -> v0 as String },
            owner = json["owner"] as String,
            rateLimited = json["rateLimited"] as Boolean,
            items = hydraList(json["items"]).map { v0 -> HydraSelfUpdateItem.fromJson(hydraMap(v0)) },
            applyEnabled = json["applyEnabled"] as Boolean,
            job = json["job"]?.let { v0 -> HydraSelfUpdateJob.fromJson(hydraMap(v0)) },
        )
    }
}

/** The listen port and, besides it, the security options of the server (the groups of PUT /api/admin/server-config: tls, ble, mqtt, voice, auth, ingest...). The groups grow with the server, so a key this list does not name is kept, not dropped. */
data class HydraServerConfig(
    val port: Long,
    val pendingPort: Long?,
    /** The keys the contract does not list, kept as they came. */
    val additionalProperties: Map<String, Any?> = emptyMap(),
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut.putAll(additionalProperties)
        jsonOut["port"] = port
        jsonOut["pendingPort"] = pendingPort
        return jsonOut
    }

    companion object {
        private val knownKeys: Set<String> = setOf("port", "pendingPort")

        fun fromJson(json: Map<String, Any?>): HydraServerConfig = HydraServerConfig(
            port = (json["port"] as Number).toLong(),
            pendingPort = json["pendingPort"]?.let { v0 -> (v0 as Number).toLong() },
            additionalProperties = hydraMap(json.filterKeys { it !in knownKeys }),
        )
    }
}

/** The identity this server presents to the services it calls: the switch (auth.serviceIdentity.enabled), whether JWT_SECRET can sign, and which services take the identity. Read-only; the switch is changed with PUT /api/admin/server-config. */
data class HydraServiceIdentityStatus(
    val enabled: Boolean,
    val source: String,
    /** True when the switch comes from the environment (HYDRA_UMC_SERVICE_IDENTITY) and cannot be changed here. */
    val locked: Boolean,
    /** Whether JWT_SECRET can sign: unset, an example value or too short is unusable. */
    val key: String,
    val state: String,
    val services: List<HydraServiceIdentityStatusServicesItem>,
    /** The safe order of the steps, as codes the screens translate. */
    val order: List<String>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["enabled"] = enabled
        jsonOut["source"] = source
        jsonOut["locked"] = locked
        jsonOut["key"] = key
        jsonOut["state"] = state
        jsonOut["services"] = services.map { v0 -> v0.toJson() }
        jsonOut["order"] = order
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraServiceIdentityStatus = HydraServiceIdentityStatus(
            enabled = json["enabled"] as Boolean,
            source = json["source"] as String,
            locked = json["locked"] as Boolean,
            key = json["key"] as String,
            state = json["state"] as String,
            services = hydraList(json["services"]).map { v0 -> HydraServiceIdentityStatusServicesItem.fromJson(hydraMap(v0)) },
            order = hydraList(json["order"]).map { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraServiceIdentityStatusServicesItem(
    /** The short name of the service (the repository name without its prefix). */
    val name: String,
    val support: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["name"] = name
        jsonOut["support"] = support
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraServiceIdentityStatusServicesItem = HydraServiceIdentityStatusServicesItem(
            name = json["name"] as String,
            support = json["support"] as String,
        )
    }
}

/** The full settings document. Controllers and their robots are listed under controllers[].robots. */
data class HydraSettings(
    val controllers: List<Map<String, Any?>>? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        if (controllers != null) jsonOut["controllers"] = controllers
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSettings = HydraSettings(
            controllers = json["controllers"]?.let { v0 -> hydraList(v0).map { v1 -> hydraMap(v1) } },
        )
    }
}

/** An object of the server contract. */
data class HydraStopAllResult(
    val success: Boolean,
    val stoppedCount: Long,
    val failedCount: Long,
    val persisted: Boolean,
    /** Present only when announcing a global stop is configured (safety.publishGlobalStop): whether the retained SAFE_STOP went out on the MQTT bridge. */
    val announced: Boolean? = null,
    val robots: List<HydraStopAllResultRobotsItem>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["stoppedCount"] = stoppedCount
        jsonOut["failedCount"] = failedCount
        jsonOut["persisted"] = persisted
        if (announced != null) jsonOut["announced"] = announced
        jsonOut["robots"] = robots.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraStopAllResult = HydraStopAllResult(
            success = json["success"] as Boolean,
            stoppedCount = (json["stoppedCount"] as Number).toLong(),
            failedCount = (json["failedCount"] as Number).toLong(),
            persisted = json["persisted"] as Boolean,
            announced = json["announced"]?.let { v0 -> v0 as Boolean },
            robots = hydraList(json["robots"]).map { v0 -> HydraStopAllResultRobotsItem.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraStopAllResultRobotsItem(
    val robotId: Long,
    val controllerId: String,
    val name: String,
    val stopped: Boolean,
    val valvesOff: Long,
    val pumpsOff: Long,
    val reservedBy: String? = null,
    val error: String? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["robotId"] = robotId
        jsonOut["controllerId"] = controllerId
        jsonOut["name"] = name
        jsonOut["stopped"] = stopped
        jsonOut["valvesOff"] = valvesOff
        jsonOut["pumpsOff"] = pumpsOff
        if (reservedBy != null) jsonOut["reservedBy"] = reservedBy
        if (error != null) jsonOut["error"] = error
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraStopAllResultRobotsItem = HydraStopAllResultRobotsItem(
            robotId = (json["robotId"] as Number).toLong(),
            controllerId = json["controllerId"] as String,
            name = json["name"] as String,
            stopped = json["stopped"] as Boolean,
            valvesOff = (json["valvesOff"] as Number).toLong(),
            pumpsOff = (json["pumpsOff"] as Number).toLong(),
            reservedBy = json["reservedBy"]?.let { v0 -> v0 as String },
            error = json["error"]?.let { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraSuccess(
    val success: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSuccess = HydraSuccess(
            success = json["success"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraSystemMetrics(
    val cpuLoad: Double,
    val memoryUsage: Double,
    val temp: Double?,
    val tempIsReal: Boolean,
    val rp1Temp: Double?,
    val uptime: Double,
    val network: Map<String, Any?>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["cpu_load"] = cpuLoad
        jsonOut["memory_usage"] = memoryUsage
        jsonOut["temp"] = temp
        jsonOut["temp_is_real"] = tempIsReal
        jsonOut["rp1_temp"] = rp1Temp
        jsonOut["uptime"] = uptime
        jsonOut["network"] = network
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraSystemMetrics = HydraSystemMetrics(
            cpuLoad = (json["cpu_load"] as Number).toDouble(),
            memoryUsage = (json["memory_usage"] as Number).toDouble(),
            temp = json["temp"]?.let { v0 -> (v0 as Number).toDouble() },
            tempIsReal = json["temp_is_real"] as Boolean,
            rp1Temp = json["rp1_temp"]?.let { v0 -> (v0 as Number).toDouble() },
            uptime = (json["uptime"] as Number).toDouble(),
            network = hydraMap(json["network"]),
        )
    }
}

/** The answer of a reset of the arm state of one URTC tool changer: the robot and the tool that were reset. The reset moves nothing mechanical; it puts the tool changer back to the disarmed state it reports. */
data class HydraToolArmResetResult(
    val success: Boolean,
    val robot: String,
    val toolId: Long,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["robot"] = robot
        jsonOut["toolId"] = toolId
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraToolArmResetResult = HydraToolArmResetResult(
            success = json["success"] as Boolean,
            robot = json["robot"] as String,
            toolId = (json["toolId"] as Number).toLong(),
        )
    }
}

/** The arm state of the URTC tools as the safety zones service lists it, carried by the server unchanged (the schema tool-arms.schema.json is the contract of the service). The last report of each pair of robot and tool, how old it is, and whether it is stale; a stale report is not counted in armedCount, and a panel shows a stale armed tool as a warning and a stale disarmed tool as unknown. A restart of the service forgets the reports, which a panel sees as an empty list. */
data class HydraToolArmsReport(
    val schemaVersion: String,
    val ttlSeconds: Double,
    val arms: List<HydraToolArmsReportArmsItem>,
    val armedCount: Long,
    val staleCount: Long,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["schema_version"] = schemaVersion
        jsonOut["ttlSeconds"] = ttlSeconds
        jsonOut["arms"] = arms.map { v0 -> v0.toJson() }
        jsonOut["armedCount"] = armedCount
        jsonOut["staleCount"] = staleCount
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraToolArmsReport = HydraToolArmsReport(
            schemaVersion = json["schema_version"] as String,
            ttlSeconds = (json["ttlSeconds"] as Number).toDouble(),
            arms = hydraList(json["arms"]).map { v0 -> HydraToolArmsReportArmsItem.fromJson(hydraMap(v0)) },
            armedCount = (json["armedCount"] as Number).toLong(),
            staleCount = (json["staleCount"] as Number).toLong(),
        )
    }
}

/** An object of the server contract. */
data class HydraToolArmsReportArmsItem(
    val robot: String,
    val toolId: Long,
    val armed: Boolean,
    val by: String? = null,
    val seq: Long,
    val ageSeconds: Double,
    val stale: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["robot"] = robot
        jsonOut["toolId"] = toolId
        jsonOut["armed"] = armed
        if (by != null) jsonOut["by"] = by
        jsonOut["seq"] = seq
        jsonOut["ageSeconds"] = ageSeconds
        jsonOut["stale"] = stale
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraToolArmsReportArmsItem = HydraToolArmsReportArmsItem(
            robot = json["robot"] as String,
            toolId = (json["toolId"] as Number).toLong(),
            armed = json["armed"] as Boolean,
            by = json["by"]?.let { v0 -> v0 as String },
            seq = (json["seq"] as Number).toLong(),
            ageSeconds = (json["ageSeconds"] as Number).toDouble(),
            stale = json["stale"] as Boolean,
        )
    }
}

/** An object of the server contract. */
data class HydraTotpConfirmed(
    val success: Boolean,
    val recoveryCodes: List<String>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["recoveryCodes"] = recoveryCodes
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraTotpConfirmed = HydraTotpConfirmed(
            success = json["success"] as Boolean,
            recoveryCodes = hydraList(json["recoveryCodes"]).map { v0 -> v0 as String },
        )
    }
}

/** An object of the server contract. */
data class HydraTotpEnrolment(
    val success: Boolean,
    val secret: String,
    val uri: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["success"] = success
        jsonOut["secret"] = secret
        jsonOut["uri"] = uri
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraTotpEnrolment = HydraTotpEnrolment(
            success = json["success"] as Boolean,
            secret = json["secret"] as String,
            uri = json["uri"] as String,
        )
    }
}

/** An object of the server contract. */
data class HydraTotpStatus(
    val enabled: Boolean,
    val recoveryLeft: Long,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["enabled"] = enabled
        jsonOut["recoveryLeft"] = recoveryLeft
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraTotpStatus = HydraTotpStatus(
            enabled = json["enabled"] as Boolean,
            recoveryLeft = (json["recoveryLeft"] as Number).toLong(),
        )
    }
}

/** An object of the server contract. */
data class HydraUpdateItem(
    val name: String,
    val family: String?,
    val installed: String?,
    /** The newest published release, or null when it could not be looked up. */
    val latest: String?,
    val state: String,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["name"] = name
        jsonOut["family"] = family
        jsonOut["installed"] = installed
        jsonOut["latest"] = latest
        jsonOut["state"] = state
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraUpdateItem = HydraUpdateItem(
            name = json["name"] as String,
            family = json["family"]?.let { v0 -> v0 as String },
            installed = json["installed"]?.let { v0 -> v0 as String },
            latest = json["latest"]?.let { v0 -> v0 as String },
            state = json["state"] as String,
        )
    }
}

/** The installed version of each program set against its newest published release. It reports; it never installs anything. */
data class HydraUpdateReport(
    val checkedAt: String?,
    val owner: String,
    /** True when GitHub refused for quota during the look; the programs it did not reach have no newest version. */
    val rateLimited: Boolean,
    val items: List<HydraUpdateItem>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["checkedAt"] = checkedAt
        jsonOut["owner"] = owner
        jsonOut["rateLimited"] = rateLimited
        jsonOut["items"] = items.map { v0 -> v0.toJson() }
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraUpdateReport = HydraUpdateReport(
            checkedAt = json["checkedAt"]?.let { v0 -> v0 as String },
            owner = json["owner"] as String,
            rateLimited = json["rateLimited"] as Boolean,
            items = hydraList(json["items"]).map { v0 -> HydraUpdateItem.fromJson(hydraMap(v0)) },
        )
    }
}

/** An object of the server contract. */
data class HydraUsbDevices(
    val devices: List<Map<String, Any?>>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["devices"] = devices
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraUsbDevices = HydraUsbDevices(
            devices = hydraList(json["devices"]).map { v0 -> hydraMap(v0) },
        )
    }
}

/** An object of the server contract. */
data class HydraUserList(
    val users: List<Map<String, Any?>>,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["users"] = users
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraUserList = HydraUserList(
            users = hydraList(json["users"]).map { v0 -> hydraMap(v0) },
        )
    }
}

/** The answer of POST /api/voice/confirm: the confirmation result of the voice interface and whether the server verified its signature. Keys the interface adds are kept. */
data class HydraVoiceConfirmResult(
    val type: String,
    val status: String,
    val requestId: String? = null,
    val intent: Map<String, Any?>? = null,
    val subject: String? = null,
    val verified: Boolean,
    /** The keys the contract does not list, kept as they came. */
    val additionalProperties: Map<String, Any?> = emptyMap(),
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut.putAll(additionalProperties)
        jsonOut["type"] = type
        jsonOut["status"] = status
        if (requestId != null) jsonOut["requestId"] = requestId
        if (intent != null) jsonOut["intent"] = intent
        if (subject != null) jsonOut["subject"] = subject
        jsonOut["verified"] = verified
        return jsonOut
    }

    companion object {
        private val knownKeys: Set<String> = setOf("type", "status", "requestId", "intent", "subject", "verified")

        fun fromJson(json: Map<String, Any?>): HydraVoiceConfirmResult = HydraVoiceConfirmResult(
            type = json["type"] as String,
            status = json["status"] as String,
            requestId = json["requestId"]?.let { v0 -> v0 as String },
            intent = json["intent"]?.let { v0 -> hydraMap(v0) },
            subject = json["subject"]?.let { v0 -> v0 as String },
            verified = json["verified"] as Boolean,
            additionalProperties = hydraMap(json.filterKeys { it !in knownKeys }),
        )
    }
}

/** An object of the server contract. */
data class HydraVoiceReply(
    val type: String,
    val requestId: String,
    val text: String,
    val level: String,
    val speak: Boolean,
    val requiresConfirmation: Boolean,
    val visualState: String? = null,
    val intent: Map<String, Any?>? = null,
    val interpretation: Map<String, Any?>? = null,
    val messageCode: String? = null,
    val messageParams: Map<String, Any?>? = null,
    val textLanguage: String? = null,
    val confirmationToken: String? = null,
    val confirmationValiditySeconds: Double? = null,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["type"] = type
        jsonOut["requestId"] = requestId
        jsonOut["text"] = text
        jsonOut["level"] = level
        jsonOut["speak"] = speak
        jsonOut["requiresConfirmation"] = requiresConfirmation
        if (visualState != null) jsonOut["visualState"] = visualState
        if (intent != null) jsonOut["intent"] = intent
        if (interpretation != null) jsonOut["interpretation"] = interpretation
        if (messageCode != null) jsonOut["messageCode"] = messageCode
        if (messageParams != null) jsonOut["messageParams"] = messageParams
        if (textLanguage != null) jsonOut["textLanguage"] = textLanguage
        if (confirmationToken != null) jsonOut["confirmationToken"] = confirmationToken
        if (confirmationValiditySeconds != null) jsonOut["confirmationValiditySeconds"] = confirmationValiditySeconds
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraVoiceReply = HydraVoiceReply(
            type = json["type"] as String,
            requestId = json["requestId"] as String,
            text = json["text"] as String,
            level = json["level"] as String,
            speak = json["speak"] as Boolean,
            requiresConfirmation = json["requiresConfirmation"] as Boolean,
            visualState = json["visualState"]?.let { v0 -> v0 as String },
            intent = json["intent"]?.let { v0 -> hydraMap(v0) },
            interpretation = json["interpretation"]?.let { v0 -> hydraMap(v0) },
            messageCode = json["messageCode"]?.let { v0 -> v0 as String },
            messageParams = json["messageParams"]?.let { v0 -> hydraMap(v0) },
            textLanguage = json["textLanguage"]?.let { v0 -> v0 as String },
            confirmationToken = json["confirmationToken"]?.let { v0 -> v0 as String },
            confirmationValiditySeconds = json["confirmationValiditySeconds"]?.let { v0 -> (v0 as Number).toDouble() },
        )
    }
}

/** An object of the server contract. */
data class HydraWatchStatus(
    val type: String,
    val headline: String,
    val detail: String,
    val level: String,
    val speak: Boolean,
) {
    fun toJson(): Map<String, Any?> {
        val jsonOut = LinkedHashMap<String, Any?>()
        jsonOut["type"] = type
        jsonOut["headline"] = headline
        jsonOut["detail"] = detail
        jsonOut["level"] = level
        jsonOut["speak"] = speak
        return jsonOut
    }

    companion object {
        fun fromJson(json: Map<String, Any?>): HydraWatchStatus = HydraWatchStatus(
            type = json["type"] as String,
            headline = json["headline"] as String,
            detail = json["detail"] as String,
            level = json["level"] as String,
            speak = json["speak"] as Boolean,
        )
    }
}

private fun hydraMap(value: Any?): Map<String, Any?> =
    (value as Map<*, *>).entries.associate { (key, item) -> (key as String) to item }

private fun hydraList(value: Any?): List<Any?> = value as List<*>

/** contentType is the media type of a body that is not JSON; responseType is text or binary when the answer is not JSON; replyHeaders names the response headers to hand back in a HydraReply. */
class HydraRequest(val method: String, val path: String, val query: Map<String, String>, val body: Any?, val access: String, val headers: Map<String, String> = emptyMap(),
                   val contentType: String? = null, val responseType: String? = null, val replyHeaders: List<String> = emptyList())

/** The answer of a route that declares response headers: the decoded body and the headers under their declared names (ETag, X-Next-Cursor). */
class HydraReply<T>(val body: T, val headers: Map<String, String>)

/** Carries one request to the server and returns the decoded answer (null when there is none); a request with replyHeaders gets a HydraReply. */
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
        val raw = transport.send(HydraRequest("GET", "/.well-known/jwks.json", emptyMap(), null, "public"))
        return HydraJwksDocument.fromJson(hydraMap(raw))
    }

    /** GET /api/adapters (access: user) */
    suspend fun getAdapters(): Map<String, Any?> {
        val raw = transport.send(HydraRequest("GET", "/api/adapters", emptyMap(), null, "user"))
        return hydraMap(raw)
    }

    /** GET /api/adapters/{adapterId} (access: user) */
    suspend fun getAdaptersByAdapterId(adapterId: String): Unit {
        transport.send(HydraRequest("GET", fillPath("/api/adapters/{adapterId}", mapOf("adapterId" to adapterId)), emptyMap(), null, "user"))
        return Unit
    }

    /** GET /api/admin/clients (access: admin) */
    suspend fun getAdminClients(): HydraClients {
        val raw = transport.send(HydraRequest("GET", "/api/admin/clients", emptyMap(), null, "admin"))
        return HydraClients.fromJson(hydraMap(raw))
    }

    /** GET /api/admin/device-tokens (access: admin) */
    suspend fun getAdminDeviceTokens(): HydraDeviceTokenList {
        val raw = transport.send(HydraRequest("GET", "/api/admin/device-tokens", emptyMap(), null, "admin"))
        return HydraDeviceTokenList.fromJson(hydraMap(raw))
    }

    /** POST /api/admin/device-tokens (access: admin) */
    suspend fun postAdminDeviceTokens(body: HydraPostAdminDeviceTokensBody): HydraDeviceTokenIssued {
        val raw = transport.send(HydraRequest("POST", "/api/admin/device-tokens", emptyMap(), body.toJson(), "admin"))
        return HydraDeviceTokenIssued.fromJson(hydraMap(raw))
    }

    /** DELETE /api/admin/device-tokens/{id} (access: admin) */
    suspend fun deleteAdminDeviceTokensById(id: String): HydraDeviceTokenRevoked {
        val raw = transport.send(HydraRequest("DELETE", fillPath("/api/admin/device-tokens/{id}", mapOf("id" to id)), emptyMap(), null, "admin"))
        return HydraDeviceTokenRevoked.fromJson(hydraMap(raw))
    }

    /** GET /api/admin/fleet-update (access: admin) */
    suspend fun getAdminFleetUpdate(): HydraFleetUpdateStatus {
        val raw = transport.send(HydraRequest("GET", "/api/admin/fleet-update", emptyMap(), null, "admin"))
        return HydraFleetUpdateStatus.fromJson(hydraMap(raw))
    }

    /** POST /api/admin/fleet-update/apply (access: admin) */
    suspend fun postAdminFleetUpdateApply(body: HydraPostAdminFleetUpdateApplyBody): HydraFleetUpdateStatus {
        val raw = transport.send(HydraRequest("POST", "/api/admin/fleet-update/apply", emptyMap(), body.toJson(), "admin"))
        return HydraFleetUpdateStatus.fromJson(hydraMap(raw))
    }

    /** POST /api/admin/fleet-update/plan (access: admin) */
    suspend fun postAdminFleetUpdatePlan(): HydraFleetUpdateStatus {
        val raw = transport.send(HydraRequest("POST", "/api/admin/fleet-update/plan", emptyMap(), null, "admin"))
        return HydraFleetUpdateStatus.fromJson(hydraMap(raw))
    }

    /** POST /api/admin/fleet-update/resume (access: admin) */
    suspend fun postAdminFleetUpdateResume(body: HydraPostAdminFleetUpdateResumeBody): HydraFleetUpdateStatus {
        val raw = transport.send(HydraRequest("POST", "/api/admin/fleet-update/resume", emptyMap(), body.toJson(), "admin"))
        return HydraFleetUpdateStatus.fromJson(hydraMap(raw))
    }

    /** GET /api/admin/jwt-keys (access: admin) */
    suspend fun getAdminJwtKeys(): HydraJwtKeys {
        val raw = transport.send(HydraRequest("GET", "/api/admin/jwt-keys", emptyMap(), null, "admin"))
        return HydraJwtKeys.fromJson(hydraMap(raw))
    }

    /** POST /api/admin/jwt-keys/rotate (access: admin) */
    suspend fun postAdminJwtKeysRotate(): HydraJwtKeyRotated {
        val raw = transport.send(HydraRequest("POST", "/api/admin/jwt-keys/rotate", emptyMap(), null, "admin"))
        return HydraJwtKeyRotated.fromJson(hydraMap(raw))
    }

    /** GET /api/admin/logs (access: admin) */
    suspend fun getAdminLogs(lines: String? = null): HydraLogLines {
        val raw = transport.send(HydraRequest("GET", "/api/admin/logs", queryOf(mapOf("lines" to lines)), null, "admin"))
        return HydraLogLines.fromJson(hydraMap(raw))
    }

    /** POST /api/admin/maintenance/install (access: admin) */
    suspend fun postAdminMaintenanceInstall(body: HydraPostAdminMaintenanceInstallBody): HydraMaintenanceOutcome {
        val raw = transport.send(HydraRequest("POST", "/api/admin/maintenance/install", emptyMap(), body.toJson(), "admin"))
        return HydraMaintenanceOutcome.fromJson(hydraMap(raw))
    }

    /** POST /api/admin/maintenance/prune (access: admin) */
    suspend fun postAdminMaintenancePrune(body: HydraPostAdminMaintenancePruneBody): HydraMaintenanceOutcome {
        val raw = transport.send(HydraRequest("POST", "/api/admin/maintenance/prune", emptyMap(), body.toJson(), "admin"))
        return HydraMaintenanceOutcome.fromJson(hydraMap(raw))
    }

    /** POST /api/admin/maintenance/rollback (access: admin) */
    suspend fun postAdminMaintenanceRollback(body: HydraPostAdminMaintenanceRollbackBody): HydraMaintenanceOutcome {
        val raw = transport.send(HydraRequest("POST", "/api/admin/maintenance/rollback", emptyMap(), body.toJson(), "admin"))
        return HydraMaintenanceOutcome.fromJson(hydraMap(raw))
    }

    /** GET /api/admin/maintenance/status (access: admin) */
    suspend fun getAdminMaintenanceStatus(component: String? = null): HydraMaintenanceOutcome {
        val raw = transport.send(HydraRequest("GET", "/api/admin/maintenance/status", queryOf(mapOf("component" to component)), null, "admin"))
        return HydraMaintenanceOutcome.fromJson(hydraMap(raw))
    }

    /** GET /api/admin/push (access: admin) */
    suspend fun getAdminPush(): HydraPushStatus {
        val raw = transport.send(HydraRequest("GET", "/api/admin/push", emptyMap(), null, "admin"))
        return HydraPushStatus.fromJson(hydraMap(raw))
    }

    /** POST /api/admin/restart (access: admin) */
    suspend fun postAdminRestart(): HydraSuccess {
        val raw = transport.send(HydraRequest("POST", "/api/admin/restart", emptyMap(), null, "admin"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** GET /api/admin/robot-ids (access: admin) */
    suspend fun getAdminRobotIds(): HydraGetAdminRobotIdsResult {
        val raw = transport.send(HydraRequest("GET", "/api/admin/robot-ids", emptyMap(), null, "admin"))
        return HydraGetAdminRobotIdsResult.fromJson(hydraMap(raw))
    }

    /** PUT /api/admin/safety-limits (access: admin) */
    suspend fun putAdminSafetyLimits(body: HydraPutAdminSafetyLimitsBody): HydraPutAdminSafetyLimitsResult {
        val raw = transport.send(HydraRequest("PUT", "/api/admin/safety-limits", emptyMap(), body.toJson(), "admin"))
        return HydraPutAdminSafetyLimitsResult.fromJson(hydraMap(raw))
    }

    /** GET /api/admin/self-update (access: admin) */
    suspend fun getAdminSelfUpdate(refresh: String? = null): HydraSelfUpdateStatus {
        val raw = transport.send(HydraRequest("GET", "/api/admin/self-update", queryOf(mapOf("refresh" to refresh)), null, "admin"))
        return HydraSelfUpdateStatus.fromJson(hydraMap(raw))
    }

    /** POST /api/admin/self-update/apply (access: admin) */
    suspend fun postAdminSelfUpdateApply(body: HydraPostAdminSelfUpdateApplyBody): HydraSelfUpdateJob {
        val raw = transport.send(HydraRequest("POST", "/api/admin/self-update/apply", emptyMap(), body.toJson(), "admin"))
        return HydraSelfUpdateJob.fromJson(hydraMap(raw))
    }

    /** GET /api/admin/self-update/jobs/{id} (access: admin) */
    suspend fun getAdminSelfUpdateJobsById(id: String): HydraSelfUpdateJob {
        val raw = transport.send(HydraRequest("GET", fillPath("/api/admin/self-update/jobs/{id}", mapOf("id" to id)), emptyMap(), null, "admin"))
        return HydraSelfUpdateJob.fromJson(hydraMap(raw))
    }

    /** POST /api/admin/self-update/rollback (access: admin) */
    suspend fun postAdminSelfUpdateRollback(body: HydraPostAdminSelfUpdateRollbackBody): HydraSelfUpdateJob {
        val raw = transport.send(HydraRequest("POST", "/api/admin/self-update/rollback", emptyMap(), body.toJson(), "admin"))
        return HydraSelfUpdateJob.fromJson(hydraMap(raw))
    }

    /** GET /api/admin/server-config (access: admin) */
    suspend fun getAdminServerConfig(): HydraServerConfig {
        val raw = transport.send(HydraRequest("GET", "/api/admin/server-config", emptyMap(), null, "admin"))
        return HydraServerConfig.fromJson(hydraMap(raw))
    }

    /** PUT /api/admin/server-config (access: admin) */
    suspend fun putAdminServerConfig(body: HydraPutAdminServerConfigBody? = null): HydraPutAdminServerConfigResult {
        val raw = transport.send(HydraRequest("PUT", "/api/admin/server-config", emptyMap(), body?.toJson(), "admin"))
        return HydraPutAdminServerConfigResult.fromJson(hydraMap(raw))
    }

    /** GET /api/admin/service-identity (access: admin) */
    suspend fun getAdminServiceIdentity(): HydraServiceIdentityStatus {
        val raw = transport.send(HydraRequest("GET", "/api/admin/service-identity", emptyMap(), null, "admin"))
        return HydraServiceIdentityStatus.fromJson(hydraMap(raw))
    }

    /** GET /api/admin/updates (access: admin) */
    suspend fun getAdminUpdates(refresh: String? = null): HydraUpdateReport {
        val raw = transport.send(HydraRequest("GET", "/api/admin/updates", queryOf(mapOf("refresh" to refresh)), null, "admin"))
        return HydraUpdateReport.fromJson(hydraMap(raw))
    }

    /** GET /api/anomaly/verdicts (access: user) */
    suspend fun getAnomalyVerdicts(verdict: String? = null, verify: String? = null): Unit {
        transport.send(HydraRequest("GET", "/api/anomaly/verdicts", queryOf(mapOf("verdict" to verdict, "verify" to verify)), null, "user"))
        return Unit
    }

    /** GET /api/audit (access: admin) */
    suspend fun getAudit(afterSeq: String? = null, format: String? = null, limit: String? = null, robotId: String? = null, type: String? = null, verify: String? = null): HydraAuditReport {
        val raw = transport.send(HydraRequest("GET", "/api/audit", queryOf(mapOf("afterSeq" to afterSeq, "format" to format, "limit" to limit, "robotId" to robotId, "type" to type, "verify" to verify)), null, "admin"))
        return HydraAuditReport.fromJson(hydraMap(raw))
    }

    /** GET /api/audit (access: admin); the answer as text, the way the route offers it besides JSON. */
    suspend fun getAuditAsText(afterSeq: String? = null, format: String? = null, limit: String? = null, robotId: String? = null, type: String? = null, verify: String? = null): String {
        return transport.send(HydraRequest("GET", "/api/audit", queryOf(mapOf("afterSeq" to afterSeq, "format" to format, "limit" to limit, "robotId" to robotId, "type" to type, "verify" to verify)), null, "admin", responseType = "text")) as String
    }

    /** GET /api/bridges (access: user) */
    suspend fun getBridges(): HydraBridgeList {
        val raw = transport.send(HydraRequest("GET", "/api/bridges", emptyMap(), null, "user"))
        return HydraBridgeList.fromJson(hydraMap(raw))
    }

    /** POST /api/bridges/{name}/cmd/{verb} (access: user) */
    suspend fun postBridgesByNameCmdByVerb(name: String, verb: String, body: Map<String, Any?>? = null): HydraBridgeCommandAccepted {
        val raw = transport.send(HydraRequest("POST", fillPath("/api/bridges/{name}/cmd/{verb}", mapOf("name" to name, "verb" to verb)), emptyMap(), body, "user"))
        return HydraBridgeCommandAccepted.fromJson(hydraMap(raw))
    }

    /** GET /api/bridges/{name}/state (access: user) */
    suspend fun getBridgesByNameState(name: String): HydraBridgeState {
        val raw = transport.send(HydraRequest("GET", fillPath("/api/bridges/{name}/state", mapOf("name" to name)), emptyMap(), null, "user"))
        return HydraBridgeState.fromJson(hydraMap(raw))
    }

    /** POST /api/camera/discover-rtsp-path (access: admin) */
    suspend fun postCameraDiscoverRtspPath(body: HydraPostCameraDiscoverRtspPathBody): Unit {
        transport.send(HydraRequest("POST", "/api/camera/discover-rtsp-path", emptyMap(), body.toJson(), "admin"))
        return Unit
    }

    /** GET /api/camera/discover-usb-devices (access: user) */
    suspend fun getCameraDiscoverUsbDevices(): HydraUsbDevices {
        val raw = transport.send(HydraRequest("GET", "/api/camera/discover-usb-devices", emptyMap(), null, "user"))
        return HydraUsbDevices.fromJson(hydraMap(raw))
    }

    /** GET /api/camera/media (access: user) */
    suspend fun getCameraMedia(): HydraCameraMediaList {
        val raw = transport.send(HydraRequest("GET", "/api/camera/media", emptyMap(), null, "user"))
        return HydraCameraMediaList.fromJson(hydraMap(raw))
    }

    /** GET /api/camera/media/{cameraId}/{kind}/{filename} (access: public) */
    suspend fun getCameraMediaByCameraIdByKindByFilename(cameraId: Long, kind: String, filename: String): Unit {
        transport.send(HydraRequest("GET", fillPath("/api/camera/media/{cameraId}/{kind}/{filename}", mapOf("cameraId" to cameraId, "kind" to kind, "filename" to filename)), emptyMap(), null, "public"))
        return Unit
    }

    /** DELETE /api/camera/media/{cameraId}/{kind}/{filename} (access: user) */
    suspend fun deleteCameraMediaByCameraIdByKindByFilename(cameraId: Long, kind: String, filename: String): HydraCameraCapture {
        val raw = transport.send(HydraRequest("DELETE", fillPath("/api/camera/media/{cameraId}/{kind}/{filename}", mapOf("cameraId" to cameraId, "kind" to kind, "filename" to filename)), emptyMap(), null, "user"))
        return HydraCameraCapture.fromJson(hydraMap(raw))
    }

    /** POST /api/camera/ticket (access: user) */
    suspend fun postCameraTicket(): Unit {
        transport.send(HydraRequest("POST", "/api/camera/ticket", emptyMap(), null, "user"))
        return Unit
    }

    /** POST /api/camera/{id}/ptz (access: admin) */
    suspend fun postCameraByIdPtz(id: Long, body: HydraPostCameraByIdPtzBody): HydraPtzResult {
        val raw = transport.send(HydraRequest("POST", fillPath("/api/camera/{id}/ptz", mapOf("id" to id)), emptyMap(), body.toJson(), "admin"))
        return HydraPtzResult.fromJson(hydraMap(raw))
    }

    /** POST /api/camera/{id}/recording/start (access: user) */
    suspend fun postCameraByIdRecordingStart(id: Long): HydraCameraCapture {
        val raw = transport.send(HydraRequest("POST", fillPath("/api/camera/{id}/recording/start", mapOf("id" to id)), emptyMap(), null, "user"))
        return HydraCameraCapture.fromJson(hydraMap(raw))
    }

    /** POST /api/camera/{id}/recording/stop (access: user) */
    suspend fun postCameraByIdRecordingStop(id: Long): HydraCameraCapture {
        val raw = transport.send(HydraRequest("POST", fillPath("/api/camera/{id}/recording/stop", mapOf("id" to id)), emptyMap(), null, "user"))
        return HydraCameraCapture.fromJson(hydraMap(raw))
    }

    /** POST /api/camera/{id}/snapshot (access: user) */
    suspend fun postCameraByIdSnapshot(id: Long): HydraCameraCapture {
        val raw = transport.send(HydraRequest("POST", fillPath("/api/camera/{id}/snapshot", mapOf("id" to id)), emptyMap(), null, "user"))
        return HydraCameraCapture.fromJson(hydraMap(raw))
    }

    /** GET /api/camera/{id}/stream (access: public) */
    suspend fun getCameraByIdStream(id: Long): Unit {
        transport.send(HydraRequest("GET", fillPath("/api/camera/{id}/stream", mapOf("id" to id)), emptyMap(), null, "public"))
        return Unit
    }

    /** GET /api/cameras/status (access: user) */
    suspend fun getCamerasStatus(): Map<String, HydraCameraProcessStatusValue> {
        val raw = transport.send(HydraRequest("GET", "/api/cameras/status", emptyMap(), null, "user"))
        return hydraMap(raw).mapValues { (_, v0) -> HydraCameraProcessStatusValue.fromJson(hydraMap(v0)) }
    }

    /** GET /api/claims (access: user) */
    suspend fun getClaims(): HydraClaimList {
        val raw = transport.send(HydraRequest("GET", "/api/claims", emptyMap(), null, "user"))
        return HydraClaimList.fromJson(hydraMap(raw))
    }

    /** List the clients the server has seen (access: user) */
    suspend fun getConnectionsClients(kind: String? = null, user: String? = null, active: String? = null): HydraConnectionClientList {
        val raw = transport.send(HydraRequest("GET", "/api/connections/clients", queryOf(mapOf("kind" to kind, "user" to user, "active" to active)), null, "user"))
        return HydraConnectionClientList.fromJson(hydraMap(raw))
    }

    /** List the history of the sign-ins of the clients (access: user) */
    suspend fun getConnectionsEvents(kind: String? = null, action: String? = null, user: String? = null, before: String? = null, limit: String? = null): HydraConnectionEventList {
        val raw = transport.send(HydraRequest("GET", "/api/connections/events", queryOf(mapOf("kind" to kind, "action" to action, "user" to user, "before" to before, "limit" to limit)), null, "user"))
        return HydraConnectionEventList.fromJson(hydraMap(raw))
    }

    /** GET /api/connector-hub/gate/audit (access: user) */
    suspend fun getConnectorHubGateAudit(): Map<String, Any?> {
        val raw = transport.send(HydraRequest("GET", "/api/connector-hub/gate/audit", emptyMap(), null, "user"))
        return hydraMap(raw)
    }

    /** POST /api/connector-hub/gate/evaluate (access: user) */
    suspend fun postConnectorHubGateEvaluate(): Map<String, Any?> {
        val raw = transport.send(HydraRequest("POST", "/api/connector-hub/gate/evaluate", emptyMap(), null, "user"))
        return hydraMap(raw)
    }

    /** GET /api/connector-hub/gate/settings (access: user) */
    suspend fun getConnectorHubGateSettings(): HydraGetConnectorHubGateSettingsResult {
        val raw = transport.send(HydraRequest("GET", "/api/connector-hub/gate/settings", emptyMap(), null, "user"))
        return HydraGetConnectorHubGateSettingsResult.fromJson(hydraMap(raw))
    }

    /** POST /api/connector-hub/gate/settings (access: admin) */
    suspend fun postConnectorHubGateSettings(body: HydraPostConnectorHubGateSettingsBody): HydraPostConnectorHubGateSettingsResult {
        val raw = transport.send(HydraRequest("POST", "/api/connector-hub/gate/settings", emptyMap(), body.toJson(), "admin"))
        return HydraPostConnectorHubGateSettingsResult.fromJson(hydraMap(raw))
    }

    /** GET /api/dev-server/status (access: user) */
    suspend fun getDevServerStatus(verify: String? = null): Unit {
        transport.send(HydraRequest("GET", "/api/dev-server/status", queryOf(mapOf("verify" to verify)), null, "user"))
        return Unit
    }

    /** POST /api/device/login (access: public) */
    suspend fun postDeviceLogin(body: HydraPostDeviceLoginBody): HydraLoginResult {
        val raw = transport.send(HydraRequest("POST", "/api/device/login", emptyMap(), body.toJson(), "public"))
        return HydraLoginResult.fromJson(hydraMap(raw))
    }

    /** GET /api/droid-estop/settings (access: user) */
    suspend fun getDroidEstopSettings(): HydraGetDroidEstopSettingsResult {
        val raw = transport.send(HydraRequest("GET", "/api/droid-estop/settings", emptyMap(), null, "user"))
        return HydraGetDroidEstopSettingsResult.fromJson(hydraMap(raw))
    }

    /** POST /api/droid-estop/settings (access: admin) */
    suspend fun postDroidEstopSettings(body: HydraPostDroidEstopSettingsBody): HydraPostDroidEstopSettingsResult {
        val raw = transport.send(HydraRequest("POST", "/api/droid-estop/settings", emptyMap(), body.toJson(), "admin"))
        return HydraPostDroidEstopSettingsResult.fromJson(hydraMap(raw))
    }

    /** GET /api/ecosystem/health (access: user) */
    suspend fun getEcosystemHealth(): HydraEcosystemHealth {
        val raw = transport.send(HydraRequest("GET", "/api/ecosystem/health", emptyMap(), null, "user"))
        return HydraEcosystemHealth.fromJson(hydraMap(raw))
    }

    /** GET /api/ecosystem/node-health (access: user) */
    suspend fun getEcosystemNodeHealth(slot: String? = null): HydraNodeHealth {
        val raw = transport.send(HydraRequest("GET", "/api/ecosystem/node-health", queryOf(mapOf("slot" to slot)), null, "user"))
        return HydraNodeHealth.fromJson(hydraMap(raw))
    }

    /** POST /api/ecosystem/service/{unit}/{action} (access: admin) */
    suspend fun postEcosystemServiceByUnitByAction(unit: String, action: String): HydraSuccess {
        val raw = transport.send(HydraRequest("POST", fillPath("/api/ecosystem/service/{unit}/{action}", mapOf("unit" to unit, "action" to action)), emptyMap(), null, "admin"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** GET /api/ecosystem/status (access: public) */
    suspend fun getEcosystemStatus(): HydraEcosystemStatus {
        val raw = transport.send(HydraRequest("GET", "/api/ecosystem/status", emptyMap(), null, "public"))
        return HydraEcosystemStatus.fromJson(hydraMap(raw))
    }

    /** GET /api/faults (access: user) */
    suspend fun getFaults(active: String? = null, limit: String? = null, verify: String? = null): Unit {
        transport.send(HydraRequest("GET", "/api/faults", queryOf(mapOf("active" to active, "limit" to limit, "verify" to verify)), null, "user"))
        return Unit
    }

    /** POST /api/hardware/canota/flash (access: admin) */
    suspend fun postHardwareCanotaFlash(body: ByteArray, tier: String? = null, slot: String? = null, relay: String? = null, hardwareId: String? = null, versionMajor: String? = null, versionMinor: String? = null, versionPatch: String? = null, signature: String? = null, downgradeFrom: String? = null, target: String? = null, minBootloader: String? = null): HydraCanotaFlash {
        val raw = transport.send(HydraRequest("POST", "/api/hardware/canota/flash", queryOf(mapOf("tier" to tier, "slot" to slot, "relay" to relay, "hardware_id" to hardwareId, "version_major" to versionMajor, "version_minor" to versionMinor, "version_patch" to versionPatch, "signature" to signature, "downgrade_from" to downgradeFrom, "target" to target, "min_bootloader" to minBootloader)), body, "admin", contentType = "application/octet-stream"))
        return HydraCanotaFlash.fromJson(hydraMap(raw))
    }

    /** GET /api/hardware/canota/version (access: user) */
    suspend fun getHardwareCanotaVersion(relay: String? = null, slot: String? = null, tier: String? = null): Map<String, Any?> {
        val raw = transport.send(HydraRequest("GET", "/api/hardware/canota/version", queryOf(mapOf("relay" to relay, "slot" to slot, "tier" to tier)), null, "user"))
        return hydraMap(raw)
    }

    /** POST /api/hardware/fram/erase (access: admin) */
    suspend fun postHardwareFramErase(body: HydraPostHardwareFramEraseBody): Map<String, Any?> {
        val raw = transport.send(HydraRequest("POST", "/api/hardware/fram/erase", emptyMap(), body.toJson(), "admin"))
        return hydraMap(raw)
    }

    /** POST /api/hardware/fram/selftest (access: admin) */
    suspend fun postHardwareFramSelftest(): Map<String, Any?> {
        val raw = transport.send(HydraRequest("POST", "/api/hardware/fram/selftest", emptyMap(), null, "admin"))
        return hydraMap(raw)
    }

    /** GET /api/hil-bridge/settings (access: user) */
    suspend fun getHilBridgeSettings(): HydraGetHilBridgeSettingsResult {
        val raw = transport.send(HydraRequest("GET", "/api/hil-bridge/settings", emptyMap(), null, "user"))
        return HydraGetHilBridgeSettingsResult.fromJson(hydraMap(raw))
    }

    /** POST /api/hil-bridge/settings (access: admin) */
    suspend fun postHilBridgeSettings(body: HydraPostHilBridgeSettingsBody): HydraPostHilBridgeSettingsResult {
        val raw = transport.send(HydraRequest("POST", "/api/hil-bridge/settings", emptyMap(), body.toJson(), "admin"))
        return HydraPostHilBridgeSettingsResult.fromJson(hydraMap(raw))
    }

    /** GET /api/hydra-info (access: public) */
    suspend fun getHydraInfo(): HydraHydraInfo {
        val raw = transport.send(HydraRequest("GET", "/api/hydra-info", emptyMap(), null, "public"))
        return HydraHydraInfo.fromJson(hydraMap(raw))
    }

    /** POST /api/info/ticket (access: user) */
    suspend fun postInfoTicket(body: HydraPostInfoTicketBody? = null): HydraInfoTicket {
        val raw = transport.send(HydraRequest("POST", "/api/info/ticket", emptyMap(), body?.toJson(), "user"))
        return HydraInfoTicket.fromJson(hydraMap(raw))
    }

    /** POST /api/ingest/dev-server/status (access: public) */
    suspend fun postIngestDevServerStatus(): Unit {
        transport.send(HydraRequest("POST", "/api/ingest/dev-server/status", emptyMap(), null, "public"))
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
    suspend fun postIntegrationsTestConnection(body: HydraPostIntegrationsTestConnectionBody): HydraReachable {
        val raw = transport.send(HydraRequest("POST", "/api/integrations/test-connection", emptyMap(), body.toJson(), "user"))
        return HydraReachable.fromJson(hydraMap(raw))
    }

    /** POST /api/login (access: public) */
    suspend fun postLogin(body: HydraPostLoginBody): HydraLoginResult {
        val raw = transport.send(HydraRequest("POST", "/api/login", emptyMap(), body.toJson(), "public"))
        return HydraLoginResult.fromJson(hydraMap(raw))
    }

    /** POST /api/logout (access: public) */
    suspend fun postLogout(body: HydraPostLogoutBody? = null): HydraSuccess {
        val raw = transport.send(HydraRequest("POST", "/api/logout", emptyMap(), body?.toJson(), "public"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** GET /api/models (access: public) */
    suspend fun getModels(): HydraModelList {
        val raw = transport.send(HydraRequest("GET", "/api/models", emptyMap(), null, "public"))
        return HydraModelList.fromJson(hydraMap(raw))
    }

    /** POST /api/models/submit (access: admin) */
    suspend fun postModelsSubmit(body: HydraPostModelsSubmitBody? = null): HydraModelSubmitted {
        val raw = transport.send(HydraRequest("POST", "/api/models/submit", emptyMap(), body?.toJson(), "admin"))
        return HydraModelSubmitted.fromJson(hydraMap(raw))
    }

    /** GET /api/models/{category}/{slug}/download (access: public) */
    suspend fun getModelsByCategoryBySlugDownload(category: String, slug: String): Unit {
        transport.send(HydraRequest("GET", fillPath("/api/models/{category}/{slug}/download", mapOf("category" to category, "slug" to slug)), emptyMap(), null, "public"))
        return Unit
    }

    /** POST /api/operator/confirmations (access: user) */
    suspend fun postOperatorConfirmations(body: HydraPostOperatorConfirmationsBody): HydraPostOperatorConfirmationsResult {
        val raw = transport.send(HydraRequest("POST", "/api/operator/confirmations", emptyMap(), body.toJson(), "user"))
        return HydraPostOperatorConfirmationsResult.fromJson(hydraMap(raw))
    }

    /** GET /api/operator/presence (access: user) */
    suspend fun getOperatorPresence(): HydraOperatorPresence {
        val raw = transport.send(HydraRequest("GET", "/api/operator/presence", emptyMap(), null, "user"))
        return HydraOperatorPresence.fromJson(hydraMap(raw))
    }

    /** POST /api/operator/presence (access: user) */
    suspend fun postOperatorPresence(body: HydraPostOperatorPresenceBody): HydraOperatorPresenceAck {
        val raw = transport.send(HydraRequest("POST", "/api/operator/presence", emptyMap(), body.toJson(), "user"))
        return HydraOperatorPresenceAck.fromJson(hydraMap(raw))
    }

    /** GET /api/ops-agent/proposals (access: admin) */
    suspend fun getOpsAgentProposals(): HydraGetOpsAgentProposalsResult {
        val raw = transport.send(HydraRequest("GET", "/api/ops-agent/proposals", emptyMap(), null, "admin"))
        return HydraGetOpsAgentProposalsResult.fromJson(hydraMap(raw))
    }

    /** POST /api/ops-agent/proposals/decide (access: admin) */
    suspend fun postOpsAgentProposalsDecide(body: HydraPostOpsAgentProposalsDecideBody): HydraPostOpsAgentProposalsDecideResult {
        val raw = transport.send(HydraRequest("POST", "/api/ops-agent/proposals/decide", emptyMap(), body.toJson(), "admin"))
        return HydraPostOpsAgentProposalsDecideResult.fromJson(hydraMap(raw))
    }

    /** POST /api/push/devices (access: user) */
    suspend fun postPushDevices(body: HydraPostPushDevicesBody): HydraPushDeviceRegistered {
        val raw = transport.send(HydraRequest("POST", "/api/push/devices", emptyMap(), body.toJson(), "user"))
        return HydraPushDeviceRegistered.fromJson(hydraMap(raw))
    }

    /** DELETE /api/push/devices/{token} (access: user) */
    suspend fun deletePushDevicesByToken(token: String): HydraPushDeviceRemoved {
        val raw = transport.send(HydraRequest("DELETE", fillPath("/api/push/devices/{token}", mapOf("token" to token)), emptyMap(), null, "user"))
        return HydraPushDeviceRemoved.fromJson(hydraMap(raw))
    }

    /** POST /api/push/live-activities (access: user) */
    suspend fun postPushLiveActivities(body: HydraPostPushLiveActivitiesBody): HydraLiveActivityRegistered {
        val raw = transport.send(HydraRequest("POST", "/api/push/live-activities", emptyMap(), body.toJson(), "user"))
        return HydraLiveActivityRegistered.fromJson(hydraMap(raw))
    }

    /** DELETE /api/push/live-activities/{token} (access: user) */
    suspend fun deletePushLiveActivitiesByToken(token: String): HydraLiveActivityRemoved {
        val raw = transport.send(HydraRequest("DELETE", fillPath("/api/push/live-activities/{token}", mapOf("token" to token)), emptyMap(), null, "user"))
        return HydraLiveActivityRemoved.fromJson(hydraMap(raw))
    }

    /** POST /api/refresh (access: public) */
    suspend fun postRefresh(body: HydraPostRefreshBody): HydraLoginResult {
        val raw = transport.send(HydraRequest("POST", "/api/refresh", emptyMap(), body.toJson(), "public"))
        return HydraLoginResult.fromJson(hydraMap(raw))
    }

    /** GET /api/robot/{id} (access: user) */
    suspend fun getRobotById(id: Long): HydraGetRobotByIdResult {
        val raw = transport.send(HydraRequest("GET", fillPath("/api/robot/{id}", mapOf("id" to id)), emptyMap(), null, "user"))
        return HydraGetRobotByIdResult.fromJson(hydraMap(raw))
    }

    /** GET /api/robot/{id} (access: user); the reply also holds the response headers ETag. */
    suspend fun getRobotByIdWithHeaders(id: Long): HydraReply<HydraGetRobotByIdResult> {
        val reply = transport.send(HydraRequest("GET", fillPath("/api/robot/{id}", mapOf("id" to id)), emptyMap(), null, "user", replyHeaders = listOf("ETag"))) as HydraReply<Any?>
        return HydraReply<HydraGetRobotByIdResult>(HydraGetRobotByIdResult.fromJson(hydraMap(reply.body)), reply.headers)
    }

    /** POST /api/robot/{id}/claim (access: user) */
    suspend fun postRobotByIdClaim(id: Long, headerIfMatch: String? = null, headerXControllerId: String? = null, body: HydraPostRobotByIdClaimBody? = null): HydraPostRobotByIdClaimResult {
        val raw = transport.send(HydraRequest("POST", fillPath("/api/robot/{id}/claim", mapOf("id" to id)), emptyMap(), body?.toJson(), "user", headers = queryOf(mapOf("If-Match" to headerIfMatch, "X-Controller-Id" to headerXControllerId))))
        return HydraPostRobotByIdClaimResult.fromJson(hydraMap(raw))
    }

    /** POST /api/robot/{id}/claim (access: user); the reply also holds the response headers ETag. */
    suspend fun postRobotByIdClaimWithHeaders(id: Long, headerIfMatch: String? = null, headerXControllerId: String? = null, body: HydraPostRobotByIdClaimBody? = null): HydraReply<HydraPostRobotByIdClaimResult> {
        val reply = transport.send(HydraRequest("POST", fillPath("/api/robot/{id}/claim", mapOf("id" to id)), emptyMap(), body?.toJson(), "user", headers = queryOf(mapOf("If-Match" to headerIfMatch, "X-Controller-Id" to headerXControllerId)), replyHeaders = listOf("ETag"))) as HydraReply<Any?>
        return HydraReply<HydraPostRobotByIdClaimResult>(HydraPostRobotByIdClaimResult.fromJson(hydraMap(reply.body)), reply.headers)
    }

    /** POST /api/robot/{id}/command (access: user) */
    suspend fun postRobotByIdCommand(id: Long, body: HydraPostRobotByIdCommandBody, headerIfMatch: String? = null, headerXControllerId: String? = null, headerXCorrelationId: String? = null): HydraPostRobotByIdCommandResult {
        val raw = transport.send(HydraRequest("POST", fillPath("/api/robot/{id}/command", mapOf("id" to id)), emptyMap(), body.toJson(), "user", headers = queryOf(mapOf("If-Match" to headerIfMatch, "X-Controller-Id" to headerXControllerId, "X-Correlation-Id" to headerXCorrelationId))))
        return HydraPostRobotByIdCommandResult.fromJson(hydraMap(raw))
    }

    /** POST /api/robot/{id}/heartbeat (access: user) */
    suspend fun postRobotByIdHeartbeat(id: Long): HydraSuccess {
        val raw = transport.send(HydraRequest("POST", fillPath("/api/robot/{id}/heartbeat", mapOf("id" to id)), emptyMap(), null, "user"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** POST /api/robot/{id}/jog-arm (access: user) */
    suspend fun postRobotByIdJogArm(id: Long, body: HydraPostRobotByIdJogArmBody, headerXControllerId: String? = null): HydraPostRobotByIdJogArmResult {
        val raw = transport.send(HydraRequest("POST", fillPath("/api/robot/{id}/jog-arm", mapOf("id" to id)), emptyMap(), body.toJson(), "user", headers = queryOf(mapOf("X-Controller-Id" to headerXControllerId))))
        return HydraPostRobotByIdJogArmResult.fromJson(hydraMap(raw))
    }

    /** POST /api/robot/{id}/release (access: user) */
    suspend fun postRobotByIdRelease(id: Long, headerIfMatch: String? = null, headerXControllerId: String? = null, body: HydraPostRobotByIdReleaseBody? = null): HydraPostRobotByIdReleaseResult {
        val raw = transport.send(HydraRequest("POST", fillPath("/api/robot/{id}/release", mapOf("id" to id)), emptyMap(), body?.toJson(), "user", headers = queryOf(mapOf("If-Match" to headerIfMatch, "X-Controller-Id" to headerXControllerId))))
        return HydraPostRobotByIdReleaseResult.fromJson(hydraMap(raw))
    }

    /** POST /api/robot/{id}/release (access: user); the reply also holds the response headers ETag. */
    suspend fun postRobotByIdReleaseWithHeaders(id: Long, headerIfMatch: String? = null, headerXControllerId: String? = null, body: HydraPostRobotByIdReleaseBody? = null): HydraReply<HydraPostRobotByIdReleaseResult> {
        val reply = transport.send(HydraRequest("POST", fillPath("/api/robot/{id}/release", mapOf("id" to id)), emptyMap(), body?.toJson(), "user", headers = queryOf(mapOf("If-Match" to headerIfMatch, "X-Controller-Id" to headerXControllerId)), replyHeaders = listOf("ETag"))) as HydraReply<Any?>
        return HydraReply<HydraPostRobotByIdReleaseResult>(HydraPostRobotByIdReleaseResult.fromJson(hydraMap(reply.body)), reply.headers)
    }

    /** GET /api/robots/liveness (access: user) */
    suspend fun getRobotsLiveness(): HydraRobotLiveness {
        val raw = transport.send(HydraRequest("GET", "/api/robots/liveness", emptyMap(), null, "user"))
        return HydraRobotLiveness.fromJson(hydraMap(raw))
    }

    /** GET /api/ros2-bridge/settings (access: user) */
    suspend fun getRos2BridgeSettings(): HydraGetRos2BridgeSettingsResult {
        val raw = transport.send(HydraRequest("GET", "/api/ros2-bridge/settings", emptyMap(), null, "user"))
        return HydraGetRos2BridgeSettingsResult.fromJson(hydraMap(raw))
    }

    /** POST /api/ros2-bridge/settings (access: admin) */
    suspend fun postRos2BridgeSettings(body: HydraPostRos2BridgeSettingsBody): HydraPostRos2BridgeSettingsResult {
        val raw = transport.send(HydraRequest("POST", "/api/ros2-bridge/settings", emptyMap(), body.toJson(), "admin"))
        return HydraPostRos2BridgeSettingsResult.fromJson(hydraMap(raw))
    }

    /** GET /api/rul/config (access: user) */
    suspend fun getRulConfig(): HydraRulConfig {
        val raw = transport.send(HydraRequest("GET", "/api/rul/config", emptyMap(), null, "user"))
        return HydraRulConfig.fromJson(hydraMap(raw))
    }

    /** GET /api/safety-limits (access: user) */
    suspend fun getSafetyLimits(robotId: String? = null): HydraSafetyLimitsView {
        val raw = transport.send(HydraRequest("GET", "/api/safety-limits", queryOf(mapOf("robotId" to robotId)), null, "user"))
        return HydraSafetyLimitsView.fromJson(hydraMap(raw))
    }

    /** GET /api/semantic-planner/settings (access: user) */
    suspend fun getSemanticPlannerSettings(): HydraGetSemanticPlannerSettingsResult {
        val raw = transport.send(HydraRequest("GET", "/api/semantic-planner/settings", emptyMap(), null, "user"))
        return HydraGetSemanticPlannerSettingsResult.fromJson(hydraMap(raw))
    }

    /** POST /api/semantic-planner/settings (access: admin) */
    suspend fun postSemanticPlannerSettings(body: HydraPostSemanticPlannerSettingsBody): HydraPostSemanticPlannerSettingsResult {
        val raw = transport.send(HydraRequest("POST", "/api/semantic-planner/settings", emptyMap(), body.toJson(), "admin"))
        return HydraPostSemanticPlannerSettingsResult.fromJson(hydraMap(raw))
    }

    /** GET /api/settings (access: user) */
    suspend fun getSettings(): HydraSettings {
        val raw = transport.send(HydraRequest("GET", "/api/settings", emptyMap(), null, "user"))
        return HydraSettings.fromJson(hydraMap(raw))
    }

    /** GET /api/settings (access: user); the reply also holds the response headers ETag. */
    suspend fun getSettingsWithHeaders(): HydraReply<HydraSettings> {
        val reply = transport.send(HydraRequest("GET", "/api/settings", emptyMap(), null, "user", replyHeaders = listOf("ETag"))) as HydraReply<Any?>
        return HydraReply<HydraSettings>(HydraSettings.fromJson(hydraMap(reply.body)), reply.headers)
    }

    /** PUT /api/settings (access: admin) */
    suspend fun putSettings(headerIfMatch: String, body: HydraSettings): HydraPutSettingsResult {
        val raw = transport.send(HydraRequest("PUT", "/api/settings", emptyMap(), body.toJson(), "admin", headers = queryOf(mapOf("If-Match" to headerIfMatch))))
        return HydraPutSettingsResult.fromJson(hydraMap(raw))
    }

    /** PUT /api/settings (access: admin); the reply also holds the response headers ETag. */
    suspend fun putSettingsWithHeaders(headerIfMatch: String, body: HydraSettings): HydraReply<HydraPutSettingsResult> {
        val reply = transport.send(HydraRequest("PUT", "/api/settings", emptyMap(), body.toJson(), "admin", headers = queryOf(mapOf("If-Match" to headerIfMatch)), replyHeaders = listOf("ETag"))) as HydraReply<Any?>
        return HydraReply<HydraPutSettingsResult>(HydraPutSettingsResult.fromJson(hydraMap(reply.body)), reply.headers)
    }

    /** POST /api/settings (access: admin) */
    suspend fun postSettings(body: HydraSettings, headerIfMatch: String? = null): HydraPostSettingsResult {
        val raw = transport.send(HydraRequest("POST", "/api/settings", emptyMap(), body.toJson(), "admin", headers = queryOf(mapOf("If-Match" to headerIfMatch))))
        return HydraPostSettingsResult.fromJson(hydraMap(raw))
    }

    /** POST /api/settings (access: admin); the reply also holds the response headers ETag. */
    suspend fun postSettingsWithHeaders(body: HydraSettings, headerIfMatch: String? = null): HydraReply<HydraPostSettingsResult> {
        val reply = transport.send(HydraRequest("POST", "/api/settings", emptyMap(), body.toJson(), "admin", headers = queryOf(mapOf("If-Match" to headerIfMatch)), replyHeaders = listOf("ETag"))) as HydraReply<Any?>
        return HydraReply<HydraPostSettingsResult>(HydraPostSettingsResult.fromJson(hydraMap(reply.body)), reply.headers)
    }

    /** POST /api/stop-all (access: user) */
    suspend fun postStopAll(): HydraStopAllResult {
        val raw = transport.send(HydraRequest("POST", "/api/stop-all", emptyMap(), null, "user"))
        return HydraStopAllResult.fromJson(hydraMap(raw))
    }

    /** POST /api/stop-all/release (access: admin) */
    suspend fun postStopAllRelease(): HydraGlobalStopReleased {
        val raw = transport.send(HydraRequest("POST", "/api/stop-all/release", emptyMap(), null, "admin"))
        return HydraGlobalStopReleased.fromJson(hydraMap(raw))
    }

    /** POST /api/system/bluetooth/pair (access: admin) */
    suspend fun postSystemBluetoothPair(body: HydraPostSystemBluetoothPairBody): Unit {
        transport.send(HydraRequest("POST", "/api/system/bluetooth/pair", emptyMap(), body.toJson(), "admin"))
        return Unit
    }

    /** POST /api/system/bluetooth/power (access: admin) */
    suspend fun postSystemBluetoothPower(body: HydraPostSystemBluetoothPowerBody): HydraSuccess {
        val raw = transport.send(HydraRequest("POST", "/api/system/bluetooth/power", emptyMap(), body.toJson(), "admin"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** POST /api/system/bluetooth/remove (access: admin) */
    suspend fun postSystemBluetoothRemove(body: HydraPostSystemBluetoothRemoveBody): HydraSuccess {
        val raw = transport.send(HydraRequest("POST", "/api/system/bluetooth/remove", emptyMap(), body.toJson(), "admin"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** POST /api/system/bluetooth/scan (access: admin) */
    suspend fun postSystemBluetoothScan(): HydraBluetoothScan {
        val raw = transport.send(HydraRequest("POST", "/api/system/bluetooth/scan", emptyMap(), null, "admin"))
        return HydraBluetoothScan.fromJson(hydraMap(raw))
    }

    /** GET /api/system/bluetooth/status (access: admin) */
    suspend fun getSystemBluetoothStatus(): Unit {
        transport.send(HydraRequest("GET", "/api/system/bluetooth/status", emptyMap(), null, "admin"))
        return Unit
    }

    /** GET /api/system/metrics (access: public) */
    suspend fun getSystemMetrics(): HydraSystemMetrics {
        val raw = transport.send(HydraRequest("GET", "/api/system/metrics", emptyMap(), null, "public"))
        return HydraSystemMetrics.fromJson(hydraMap(raw))
    }

    /** POST /api/system/reboot (access: public) */
    suspend fun postSystemReboot(): HydraSuccess {
        val raw = transport.send(HydraRequest("POST", "/api/system/reboot", emptyMap(), null, "public"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** POST /api/system/shutdown (access: public) */
    suspend fun postSystemShutdown(): HydraSuccess {
        val raw = transport.send(HydraRequest("POST", "/api/system/shutdown", emptyMap(), null, "public"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** GET /api/system/supervisor (access: public) */
    suspend fun getSystemSupervisor(): Map<String, Any?> {
        val raw = transport.send(HydraRequest("GET", "/api/system/supervisor", emptyMap(), null, "public"))
        return hydraMap(raw)
    }

    /** GET /api/telemetry/aggregate (access: user) */
    suspend fun getTelemetryAggregate(sourceId: String? = null, kind: String? = null, field: String? = null, bucketMs: String? = null, start: String? = null, end: String? = null, before: String? = null, agg: String? = null): List<HydraGetTelemetryAggregateResultItem> {
        val raw = transport.send(HydraRequest("GET", "/api/telemetry/aggregate", queryOf(mapOf("sourceId" to sourceId, "kind" to kind, "field" to field, "bucketMs" to bucketMs, "start" to start, "end" to end, "before" to before, "agg" to agg)), null, "user"))
        return hydraList(raw).map { v0 -> HydraGetTelemetryAggregateResultItem.fromJson(hydraMap(v0)) }
    }

    /** GET /api/telemetry/downsample-plan (access: admin) */
    suspend fun getTelemetryDownsamplePlan(): HydraGetTelemetryDownsamplePlanResult {
        val raw = transport.send(HydraRequest("GET", "/api/telemetry/downsample-plan", emptyMap(), null, "admin"))
        return HydraGetTelemetryDownsamplePlanResult.fromJson(hydraMap(raw))
    }

    /** PUT /api/telemetry/downsample-plan (access: admin) */
    suspend fun putTelemetryDownsamplePlan(body: HydraPutTelemetryDownsamplePlanBody, preview: String? = null): HydraPutTelemetryDownsamplePlanResult {
        val raw = transport.send(HydraRequest("PUT", "/api/telemetry/downsample-plan", queryOf(mapOf("preview" to preview)), body.toJson(), "admin"))
        return HydraPutTelemetryDownsamplePlanResult.fromJson(hydraMap(raw))
    }

    /** GET /api/telemetry/query (access: user) */
    suspend fun getTelemetryQuery(sourceId: String? = null, kind: String? = null, field: String? = null, start: String? = null, end: String? = null, before: String? = null, limit: String? = null, cursor: String? = null): List<HydraGetTelemetryQueryResultItem> {
        val raw = transport.send(HydraRequest("GET", "/api/telemetry/query", queryOf(mapOf("sourceId" to sourceId, "kind" to kind, "field" to field, "start" to start, "end" to end, "before" to before, "limit" to limit, "cursor" to cursor)), null, "user"))
        return hydraList(raw).map { v0 -> HydraGetTelemetryQueryResultItem.fromJson(hydraMap(v0)) }
    }

    /** GET /api/telemetry/query (access: user); the reply also holds the response headers X-Next-Cursor. */
    suspend fun getTelemetryQueryWithHeaders(sourceId: String? = null, kind: String? = null, field: String? = null, start: String? = null, end: String? = null, before: String? = null, limit: String? = null, cursor: String? = null): HydraReply<List<HydraGetTelemetryQueryResultItem>> {
        val reply = transport.send(HydraRequest("GET", "/api/telemetry/query", queryOf(mapOf("sourceId" to sourceId, "kind" to kind, "field" to field, "start" to start, "end" to end, "before" to before, "limit" to limit, "cursor" to cursor)), null, "user", replyHeaders = listOf("X-Next-Cursor"))) as HydraReply<Any?>
        return HydraReply<List<HydraGetTelemetryQueryResultItem>>(hydraList(reply.body).map { v0 -> HydraGetTelemetryQueryResultItem.fromJson(hydraMap(v0)) }, reply.headers)
    }

    /** GET /api/tool-arms (access: user) */
    suspend fun getToolArms(): HydraToolArmsReport {
        val raw = transport.send(HydraRequest("GET", "/api/tool-arms", emptyMap(), null, "user"))
        return HydraToolArmsReport.fromJson(hydraMap(raw))
    }

    /** POST /api/tool-arms/reset (access: admin) */
    suspend fun postToolArmsReset(body: HydraPostToolArmsResetBody): HydraToolArmResetResult {
        val raw = transport.send(HydraRequest("POST", "/api/tool-arms/reset", emptyMap(), body.toJson(), "admin"))
        return HydraToolArmResetResult.fromJson(hydraMap(raw))
    }

    /** POST /api/totp/begin (access: user) */
    suspend fun postTotpBegin(body: HydraPostTotpBeginBody): HydraTotpEnrolment {
        val raw = transport.send(HydraRequest("POST", "/api/totp/begin", emptyMap(), body.toJson(), "user"))
        return HydraTotpEnrolment.fromJson(hydraMap(raw))
    }

    /** POST /api/totp/confirm (access: user) */
    suspend fun postTotpConfirm(body: HydraPostTotpConfirmBody): HydraTotpConfirmed {
        val raw = transport.send(HydraRequest("POST", "/api/totp/confirm", emptyMap(), body.toJson(), "user"))
        return HydraTotpConfirmed.fromJson(hydraMap(raw))
    }

    /** POST /api/totp/disable (access: user) */
    suspend fun postTotpDisable(body: HydraPostTotpDisableBody): HydraSuccess {
        val raw = transport.send(HydraRequest("POST", "/api/totp/disable", emptyMap(), body.toJson(), "user"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** POST /api/totp/recovery-codes (access: user) */
    suspend fun postTotpRecoveryCodes(body: HydraPostTotpRecoveryCodesBody): HydraTotpConfirmed {
        val raw = transport.send(HydraRequest("POST", "/api/totp/recovery-codes", emptyMap(), body.toJson(), "user"))
        return HydraTotpConfirmed.fromJson(hydraMap(raw))
    }

    /** GET /api/totp/status (access: user) */
    suspend fun getTotpStatus(): HydraTotpStatus {
        val raw = transport.send(HydraRequest("GET", "/api/totp/status", emptyMap(), null, "user"))
        return HydraTotpStatus.fromJson(hydraMap(raw))
    }

    /** POST /api/trajectory/proposals/verify (access: user) */
    suspend fun postTrajectoryProposalsVerify(): Unit {
        transport.send(HydraRequest("POST", "/api/trajectory/proposals/verify", emptyMap(), null, "user"))
        return Unit
    }

    /** POST /api/upload-work (access: user) */
    suspend fun postUploadWork(body: HydraPostUploadWorkBody): HydraSuccess {
        val raw = transport.send(HydraRequest("POST", "/api/upload-work", emptyMap(), body.toJson(), "user"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** GET /api/users (access: admin) */
    suspend fun getUsers(): HydraUserList {
        val raw = transport.send(HydraRequest("GET", "/api/users", emptyMap(), null, "admin"))
        return HydraUserList.fromJson(hydraMap(raw))
    }

    /** POST /api/users (access: admin) */
    suspend fun postUsers(body: HydraPostUsersBody): HydraSuccess {
        val raw = transport.send(HydraRequest("POST", "/api/users", emptyMap(), body.toJson(), "admin"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** PUT /api/users/{username} (access: admin) */
    suspend fun putUsersByUsername(username: String, body: HydraPutUsersByUsernameBody? = null): HydraSuccess {
        val raw = transport.send(HydraRequest("PUT", fillPath("/api/users/{username}", mapOf("username" to username)), emptyMap(), body?.toJson(), "admin"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** DELETE /api/users/{username} (access: admin) */
    suspend fun deleteUsersByUsername(username: String): HydraSuccess {
        val raw = transport.send(HydraRequest("DELETE", fillPath("/api/users/{username}", mapOf("username" to username)), emptyMap(), null, "admin"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** DELETE /api/users/{username}/totp (access: admin) */
    suspend fun deleteUsersByUsernameTotp(username: String): HydraSuccess {
        val raw = transport.send(HydraRequest("DELETE", fillPath("/api/users/{username}/totp", mapOf("username" to username)), emptyMap(), null, "admin"))
        return HydraSuccess.fromJson(hydraMap(raw))
    }

    /** GET /api/voice/chain (access: admin) */
    suspend fun getVoiceChain(limit: String? = null, verify: String? = null): Unit {
        transport.send(HydraRequest("GET", "/api/voice/chain", queryOf(mapOf("limit" to limit, "verify" to verify)), null, "admin"))
        return Unit
    }

    /** POST /api/voice/confirm (access: user) */
    suspend fun postVoiceConfirm(body: HydraPostVoiceConfirmBody? = null): HydraVoiceConfirmResult {
        val raw = transport.send(HydraRequest("POST", "/api/voice/confirm", emptyMap(), body?.toJson(), "user"))
        return HydraVoiceConfirmResult.fromJson(hydraMap(raw))
    }

    /** POST /api/voice/turn (access: user) */
    suspend fun postVoiceTurn(body: HydraPostVoiceTurnBody? = null): HydraVoiceReply {
        val raw = transport.send(HydraRequest("POST", "/api/voice/turn", emptyMap(), body?.toJson(), "user"))
        return HydraVoiceReply.fromJson(hydraMap(raw))
    }

    /** GET /api/watch/system-status (access: user) */
    suspend fun getWatchSystemStatus(): Unit {
        transport.send(HydraRequest("GET", "/api/watch/system-status", emptyMap(), null, "user"))
        return Unit
    }

    /** GET /health (access: public) */
    suspend fun getHealth(): HydraHealthReport {
        val raw = transport.send(HydraRequest("GET", "/health", emptyMap(), null, "public"))
        return HydraHealthReport.fromJson(hydraMap(raw))
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
    "postTotpRecoveryCodes",
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
