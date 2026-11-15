// The rules of the generated classes that the contract of the server does not use: an open object keeps the keys it
// does not list, a closed one drops them, a reserved word is renamed, a schema may refer to itself and a map stays a map.
// Built by .github/workflows/generated-clients.yml from synthetic/openapi.json, next to the files the generator wrote.
package hydra.umc.synthetic

import kotlin.coroutines.Continuation
import kotlin.coroutines.EmptyCoroutineContext
import kotlin.coroutines.startCoroutine
import kotlin.system.exitProcess

private fun expect(condition: Boolean, what: String) {
    if (!condition) {
        System.err.println("KOTLIN_SYNTHETIC_SMOKE=FAIL $what")
        exitProcess(1)
    }
}

fun main() {
    val open = HydraOpen.fromJson(mapOf("name" to "n", "note" to null, "class" to "c", "in" to 4L, "unlisted" to listOf<Any?>(1L, "two"),
                                        "scores" to mapOf("a" to 2L), "nested" to mapOf("points" to listOf<Any?>(mapOf("x" to 1.5)))))
    expect(open.classValue == "c" && open.inValue == 4L && open.note == null, "reserved words are renamed and a null reads as null")
    expect(open.additionalProperties["unlisted"] == listOf<Any?>(1L, "two"), "an open object keeps the keys it does not list")
    expect(open.scores?.get("a") == 2L && open.nested?.points?.get(0)?.x == 1.5, "typed maps and nested inline classes")
    val written = open.toJson()
    expect(written["unlisted"] == listOf<Any?>(1L, "two") && written["class"] == "c" && written.containsKey("note") && written["note"] == null, "toJson writes the wire names, the kept keys and the required null")
    expect(!written.containsKey("mode"), "an optional field that is null is left out")

    val typed = HydraOpenTyped.fromJson(mapOf("id" to "a", "x" to 2L))
    expect(typed.additionalProperties["x"] == 2.0 && typed.toJson()["x"] == 2.0, "the keys of an open object follow the schema of additionalProperties")

    val closed = HydraClosed.fromJson(mapOf("id" to "a", "extra" to 1L))
    expect(closed.toJson() == mapOf("id" to "a"), "a closed object drops the keys it does not list")

    val tree = HydraTree.fromJson(mapOf("label" to "root", "children" to listOf<Any?>(mapOf("label" to "leaf", "parent" to mapOf("label" to "root")))))
    expect(tree.children?.get(0)?.label == "leaf" && tree.children?.get(0)?.parent?.label == "root", "a schema that refers to itself")
    expect(HydraTree.fromJson(tree.toJson()) == tree, "a self-referential class reads back what it wrote")

    var failure: Throwable? = null
    var bag: Map<String, List<String>>? = null
    var closedBack: HydraClosed? = null
    var seen: HydraRequest? = null
    val client = HydraServerClient { request ->
        seen = request
        if (request.path == "/api/bag") mapOf("k" to listOf<Any?>("v")) else mapOf("id" to "z", "extra" to true)
    }
    val work: suspend () -> Unit = {
        bag = client.getBag()
        closedBack = client.putClosed(HydraClosed("q"))
    }
    work.startCoroutine(Continuation(EmptyCoroutineContext) { failure = it.exceptionOrNull() })
    failure?.let { throw it }
    expect(bag == mapOf("k" to listOf("v")), "a named map stays a map")
    expect(closedBack?.id == "z" && seen?.body == mapOf("id" to "q"), "the body of a request is the plain JSON model")

    val failures = roundTripAll()
    failures.forEach { System.err.println("KOTLIN_SYNTHETIC_SMOKE=FAIL round trip $it") }
    expect(failures.isEmpty() && ROUND_TRIP_CLASSES == 4, "the round trip of the synthetic classes")
    println("KOTLIN_SYNTHETIC_SMOKE=PASS")
}
