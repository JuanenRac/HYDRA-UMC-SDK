// Calls the generated Kotlin client through a transport that records the request, so the file is not only compiled
// but also run: the requests keep their shape, the answers are read into data classes, and an example of every class
// of the contract goes through fromJson and toJson and must come back unchanged.
// Built by .github/workflows/generated-clients.yml together with generated/HydraServerClient.kt and the round trip file.
package hydra.umc.client

import kotlin.coroutines.Continuation
import kotlin.coroutines.EmptyCoroutineContext
import kotlin.coroutines.startCoroutine
import kotlin.system.exitProcess

private fun expect(condition: Boolean, what: String) {
    if (!condition) {
        System.err.println("KOTLIN_CLIENT_SMOKE=FAIL $what")
        exitProcess(1)
    }
}

fun main() {
    val seen = mutableListOf<HydraRequest>()
    val client = HydraServerClient { request ->
        seen.add(request)
        when {
            request.replyHeaders.isNotEmpty() -> HydraReply<Any?>(mapOf("controllers" to listOf<Any?>(mapOf("id" to "c1"))), mapOf("ETag" to "w/1"))
            request.path == "/api/robot/7/command" -> mapOf("success" to true, "revision" to "r2", "affectedCount" to 1L, "operation_id" to "op-1")
            request.path == "/api/robot/9" -> mapOf("robot" to mapOf("id" to 9L), "revision" to "r1")
            request.path == "/api/hardware/canota/flash" -> mapOf("success" to true, "finalPhase" to "done")
            else -> mapOf("lines" to listOf<Any?>("a", "b"))
        }
    }
    var failure: Throwable? = null
    var logs: HydraLogLines? = null
    var command: HydraPostRobotByIdCommandResult? = null
    var robot: HydraGetRobotByIdResult? = null
    var flash: HydraCanotaFlash? = null
    var settings: HydraReply<HydraSettings>? = null
    val body: suspend () -> Unit = {
        logs = client.getAdminLogs(lines = "5")
        command = client.postRobotByIdCommand(7L, HydraPostRobotByIdCommandBody(command = "stop"))
        robot = client.getRobotById(9L)
        flash = client.postHardwareCanotaFlash(body = byteArrayOf(1, 2, 3))
        settings = client.getSettingsWithHeaders()
    }
    body.startCoroutine(Continuation(EmptyCoroutineContext) { failure = it.exceptionOrNull() })
    failure?.let { throw it }

    expect(seen[0].method == "GET" && seen[0].path == "/api/admin/logs" && seen[0].query["lines"] == "5", "query")
    expect(seen[1].method == "POST" && seen[1].path == "/api/robot/7/command" && seen[1].body == mapOf("command" to "stop"), "path and body: the class is sent as the plain JSON model")
    expect(seen[2].query.isEmpty() && seen[2].path == "/api/robot/9", "no query")
    expect(seen[3].contentType == "application/octet-stream" && seen[3].body is ByteArray, "binary body")
    expect(seen[4].replyHeaders == listOf("ETag") && seen[4].path == "/api/settings", "reply with headers")
    expect(logs?.lines == listOf("a", "b"), "a list of text is read into the class")
    expect(command?.success == true && command?.revision == "r2" && command?.affectedCount == 1.0 && command?.operationId == "op-1", "the answer is read into its class with camelCase names")
    expect(robot?.revision == "r1" && robot?.robot?.get("id") == 9L && robot?.cellId == null, "an optional field that is absent reads as null")
    expect(flash?.finalPhase == "done", "the answer of the binary route")
    expect(settings?.headers?.get("ETag") == "w/1" && settings?.body?.controllers?.size == 1, "the reply with headers keeps the headers and the typed body")
    expect(HydraPostRobotByIdCommandBody(command = "stop", seq = 3L).toJson() == mapOf("command" to "stop", "seq" to 3L), "an optional field that is null is left out of toJson")
    val refusedField = runCatching { HydraLogLines.fromJson(emptyMap()) }.isFailure
    expect(refusedField, "a missing required field must throw")
    expect(fillPath("/a/{x}", mapOf("x" to "a b/c")) == "/a/a%20b%2Fc", "escape")
    val refused = runCatching { fillPath("/a/{x}", emptyMap()) }.isFailure
    expect(refused, "a missing path value must throw")
    expect("getAdminLogs" in HYDRA_CLIENT_OPERATIONS, "operation list")

    val failures = roundTripAll()
    failures.forEach { System.err.println("KOTLIN_CLIENT_SMOKE=FAIL round trip $it") }
    expect(failures.isEmpty(), "every class reads and writes its example unchanged")
    expect(ROUND_TRIP_CLASSES > 40, "the round trip covers the classes of the contract")
    println("KOTLIN_CLIENT_SMOKE=PASS ${HYDRA_CLIENT_OPERATIONS.size} operations, $ROUND_TRIP_CLASSES classes round-tripped")
}
