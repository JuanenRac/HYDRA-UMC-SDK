// Calls the generated Kotlin client through a transport that records the request, so the file is not only compiled
// but also run. Built by .github/workflows/generated-clients.yml together with generated/HydraServerClient.kt.
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
        if (request.replyHeaders.isNotEmpty()) HydraReply<Any?>(mapOf("ok" to true), mapOf("ETag" to "w/1")) else mapOf("lines" to listOf<Any?>())
    }
    var failure: Throwable? = null
    val body: suspend () -> Unit = {
        client.getAdminLogs(lines = "5")
        client.postRobotByIdCommand(7L, mapOf("command" to "stop"))
        client.getRobotById(9L)
        client.postHardwareCanotaFlash(body = byteArrayOf(1, 2, 3))
        client.getSettingsWithHeaders()
    }
    body.startCoroutine(Continuation(EmptyCoroutineContext) { failure = it.exceptionOrNull() })
    failure?.let { throw it }

    expect(seen[0].method == "GET" && seen[0].path == "/api/admin/logs" && seen[0].query["lines"] == "5", "query")
    expect(seen[1].method == "POST" && seen[1].path == "/api/robot/7/command" && seen[1].body != null, "path and body")
    expect(seen[2].query.isEmpty() && seen[2].path == "/api/robot/9", "no query")
    expect(seen[3].contentType == "application/octet-stream" && seen[3].body is ByteArray, "binary body")
    expect(seen[4].replyHeaders == listOf("ETag") && seen[4].path == "/api/settings", "reply with headers")
    expect(fillPath("/a/{x}", mapOf("x" to "a b/c")) == "/a/a%20b%2Fc", "escape")
    val refused = runCatching { fillPath("/a/{x}", emptyMap()) }.isFailure
    expect(refused, "a missing path value must throw")
    expect("getAdminLogs" in HYDRA_CLIENT_OPERATIONS, "operation list")
    println("KOTLIN_CLIENT_SMOKE=PASS ${HYDRA_CLIENT_OPERATIONS.size} operations")
}
