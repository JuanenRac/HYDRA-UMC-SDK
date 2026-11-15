# =============================================================================
# HYDRA-UMC-SDK - Tests of the typed client generated from the server contract
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""generated/hydra-server-client.ts is the output of tools/generate_clients.py and has one method per route."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("generate_clients", ROOT / "tools" / "generate_clients.py")
gc = importlib.util.module_from_spec(_spec)
sys.modules["generate_clients"] = gc
_spec.loader.exec_module(gc)

FULL = json.loads((ROOT / "contracts" / "openapi" / "v1" / "server.full.openapi.json").read_text(encoding="utf-8"))
OPS = gc.operations(FULL)
SOURCE = (ROOT / "generated" / gc.TS_NAME).read_text(encoding="utf-8")


class GeneratedClientTests(unittest.TestCase):
    def test_the_committed_file_is_the_generator_output(self):
        committed = (ROOT / "generated" / gc.TS_NAME).read_bytes().replace(b"\r\n", b"\n")
        self.assertEqual(committed, gc.outputs()[gc.TS_NAME].encode("utf-8"))

    def test_every_route_has_one_method_and_the_names_are_unique(self):
        routes = {(m.upper(), p) for p, item in FULL["paths"].items() for m in item if m in gc.METHODS}
        self.assertEqual({(o["method"], o["path"]) for o in OPS}, routes)
        self.assertEqual(len({o["name"] for o in OPS}), len(OPS))
        for op in OPS:
            self.assertIn(f"  {op['name']}(", SOURCE)

    def test_every_named_schema_is_an_exported_type(self):
        for name in FULL["components"]["schemas"]:
            self.assertRegex(SOURCE, rf"export (interface|type) {name}\b")

    def test_a_route_with_path_parameters_asks_for_them_all(self):
        for op in OPS:
            names = re.findall(r"\{([^}]+)\}", op["path"])
            self.assertEqual([p["name"] for p in op["path_parameters"]], names)
            signature, required = gc.arguments(op)
            if names:
                self.assertTrue(required)
            for name in names:
                self.assertIn(name, signature)

    def test_the_method_name_is_made_from_the_verb_and_the_path(self):
        self.assertEqual(gc.operation_name("get", "/api/robot/{id}/state"), "getRobotByIdState")
        self.assertEqual(gc.operation_name("post", "/api/bridges/{name}/cmd/{verb}"), "postBridgesByNameCmdByVerb")
        self.assertEqual(gc.operation_name("get", "/.well-known/jwks.json"), "getWellKnownJwksJson")

    def test_the_schema_subset_maps_to_typescript(self):
        self.assertEqual(gc.type_of({"type": "integer"}), "number")
        self.assertEqual(gc.type_of({"type": "string", "nullable": True}), "string | null")
        self.assertEqual(gc.type_of({"enum": ["a", "b"]}), '"a" | "b"')
        self.assertEqual(gc.type_of({"type": "array", "items": {"$ref": "#/components/schemas/Thing"}}), "Thing[]")
        self.assertEqual(gc.type_of({"type": "array", "items": {"enum": ["a", "b"]}}), '("a" | "b")[]')
        self.assertEqual(gc.type_of({"type": "object"}), "Record<string, unknown>")
        self.assertEqual(gc.type_of({"type": "object", "required": ["x"], "properties": {"x": {"type": "string"}, "y-z": {"type": "boolean"}}}),
                         '{ x: string; "y-z"?: boolean }')
        self.assertEqual(gc.type_of(None), "unknown")

    def test_a_clash_of_method_names_stops_the_generator(self):
        document = {"paths": {"/a/{x}": {"get": {}}, "/a/ByX": {"get": {}}}, "components": {"schemas": {}}}
        with self.assertRaises(SystemExit):
            gc.operations(document)

    def test_the_transport_helpers_refuse_a_missing_path_value(self):
        self.assertIn("missing path parameter", SOURCE)
        self.assertIn("encodeURIComponent", SOURCE)

    def test_the_operation_list_matches_the_methods(self):
        listed = re.findall(r'^  "([A-Za-z0-9]+)",$', SOURCE, flags=re.M)
        self.assertEqual(listed, [o["name"] for o in OPS])


if __name__ == "__main__":
    unittest.main()


KT = (ROOT / "generated" / gc.KT_NAME).read_text(encoding="utf-8")
DART = (ROOT / "generated" / gc.DART_NAME).read_text(encoding="utf-8")


class NativeClientTests(unittest.TestCase):
    def test_the_committed_kotlin_and_dart_files_are_the_generator_output(self):
        produced = gc.outputs()
        for name in (gc.KT_NAME, gc.DART_NAME, gc.KT_ROUND_TRIP_NAME, gc.DART_ROUND_TRIP_NAME):
            committed = gc.target(name).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(committed, produced[name].encode("utf-8"), name)

    def test_every_route_has_a_method_with_the_same_name_in_all_three_languages(self):
        for op in OPS:
            self.assertIn(f"    suspend fun {op['name']}(", KT)
            self.assertRegex(DART, rf"  Future<[^\n]*> {op['name']}\(")
        listed_kt = re.findall(r'^    "([A-Za-z0-9]+)",$', KT, flags=re.M)
        listed_dart = re.findall(r"^  '([A-Za-z0-9]+)',$", DART, flags=re.M)
        self.assertEqual(listed_kt, [o["name"] for o in OPS])
        self.assertEqual(listed_dart, listed_kt)

    def test_every_named_schema_is_a_class_or_an_alias(self):
        for name, schema in FULL["components"]["schemas"].items():
            if gc.is_class(schema):
                self.assertIn(f"data class Hydra{name}(", KT)
                self.assertIn(f"class Hydra{name} {{", DART)
            else:
                self.assertIn(f"typealias Hydra{name} = ", KT)
                self.assertIn(f"typedef Hydra{name} = ", DART)

    def test_the_scalar_and_collection_mapping(self):
        kotlin, dart = gc.Flavor("kotlin"), gc.Flavor("dart")
        none = frozenset()
        self.assertEqual(gc.native_type({"type": "integer"}, kotlin, none), "Long")
        self.assertEqual(gc.native_type({"type": "integer"}, dart, none), "int")
        self.assertEqual(gc.native_type({"type": "number"}, dart, none), "num")
        self.assertEqual(gc.native_type({"type": ["string", "null"]}, kotlin, none), "String?")
        self.assertEqual(gc.native_type({"type": "string", "nullable": True}, dart, none), "String?")
        self.assertEqual(gc.native_type({"type": "array", "items": {"type": "boolean"}}, kotlin, none), "List<Boolean>")
        self.assertEqual(gc.native_type({"type": "array", "items": {"type": "boolean"}}, dart, none), "List<dynamic>")
        self.assertEqual(gc.native_type({"type": "object", "additionalProperties": {"type": "string"}}, kotlin, none), "Map<String, String>")
        self.assertEqual(gc.native_type({"enum": ["a", "b"]}, kotlin, none), "String")
        self.assertEqual(gc.native_type({"$ref": "#/components/schemas/Thing"}, dart, none), "HydraThing")
        self.assertEqual(gc.native_type({"$ref": "#/components/schemas/Thing"}, dart, frozenset({"Thing"})), "dynamic")
        self.assertEqual(gc.native_type(None, kotlin, none), "Any?")
        self.assertEqual(gc.native_type({"type": ["null", "integer"]}, dart, none), "int?")

    def test_a_schema_that_refers_to_itself_is_not_an_alias_of_itself(self):
        schemas = {"Tree": {"type": "object", "properties": {"child": {"$ref": "#/components/schemas/Tree"}}},
                   "Leaf": {"type": "object", "properties": {"tree": {"$ref": "#/components/schemas/Tree"}}}}
        self.assertEqual(gc.cyclic_schemas(schemas), frozenset({"Tree"}))

    def test_identifiers_are_camel_case_never_reserved_and_never_repeated(self):
        kotlin, dart = gc.Flavor("kotlin"), gc.Flavor("dart")
        taken: set[str] = set()
        self.assertEqual(gc.identifier("fingerprint_kind", kotlin, taken), "fingerprintKind")
        self.assertEqual(gc.identifier("in", kotlin, taken), "inValue")
        self.assertEqual(gc.identifier("default", dart, set()), "defaultValue")
        self.assertEqual(gc.identifier("fingerprint-kind", kotlin, taken), "fingerprintKind2")
        self.assertEqual(gc.identifier("2fa", dart, set()), "p2fa")

    def test_no_parameter_of_any_route_is_a_reserved_word(self):
        for flavor in (gc.Flavor("kotlin"), gc.Flavor("dart")):
            builder = gc.Builder(FULL, flavor)
            for op in OPS:
                params, _ = gc.native_arguments(op, builder)
                names = [p[0] for p in params]
                self.assertEqual(len(names), len(set(names)), op["name"])
                self.assertFalse(set(names) & flavor.words, op["name"])

    def test_the_optional_arguments_come_last_and_may_be_omitted(self):
        for op in OPS:
            params, _ = gc.native_arguments(op, gc.Builder(FULL, gc.Flavor("kotlin")))
            flags = [p[4] for p in params]
            self.assertEqual(flags, sorted(flags, reverse=True), op["name"])
        self.assertIn("suspend fun getAdminLogs(lines: String? = null)", KT)
        self.assertIn("getAdminLogs({String? lines})", DART)

    def test_the_helpers_refuse_a_missing_path_value_and_escape_the_rest(self):
        self.assertIn("missing path parameter", KT)
        self.assertIn("missing path parameter", DART)
        self.assertIn("URLEncoder", KT)
        self.assertIn("Uri.encodeComponent", DART)

    def test_the_text_of_a_route_cannot_close_the_comment_or_the_string(self):
        self.assertEqual(gc.dart_string("a'b$c" + chr(92) + "d"), "'a" + chr(92) + "'b" + chr(92) + "$c" + chr(92) * 2 + "d'")
        self.assertEqual(gc.doc_note({"summary": "ends */ here", "method": "GET", "path": "/x", "access": "user"}),
                         "ends * / here (access: user)")

    def test_the_compile_workflow_names_both_files(self):
        workflow = (ROOT / ".github" / "workflows" / "generated-clients.yml").read_text(encoding="utf-8")
        self.assertIn("generated/HydraServerClient.kt", workflow)
        self.assertIn("generated/hydra_server_client.dart", workflow)
        self.assertIn("kotlinc", workflow)
        self.assertIn("dart analyze", workflow)
        self.assertTrue((ROOT / "conformance" / "generated-clients" / "Smoke.kt").is_file())
        self.assertTrue((ROOT / "conformance" / "generated-clients" / "smoke.dart").is_file())
        self.assertIn("HydraServerClientRoundTrip.kt", workflow)
        self.assertIn("hydra_server_client_round_trip.dart", workflow)
        self.assertIn("synthetic/openapi.json", workflow)
        self.assertIn("SyntheticSmokeKt", workflow)
        self.assertIn("dart run synthetic_smoke.dart", workflow)
        self.assertTrue((ROOT / "conformance" / "generated-clients" / "synthetic" / "SyntheticSmoke.kt").is_file())
        self.assertTrue((ROOT / "conformance" / "generated-clients" / "synthetic" / "synthetic_smoke.dart").is_file())


class BinaryTextAndHeaderTests(unittest.TestCase):
    """A binary body, an answer in text and the response headers reach all three clients."""

    def test_the_typescript_constructor_has_no_parameter_property(self):
        self.assertIn("  private readonly transport: HydraTransport;\n  constructor(transport: HydraTransport) {\n    this.transport = transport;\n  }", SOURCE)
        self.assertNotIn("constructor(private", SOURCE)

    def test_the_binary_flash_body_is_sent_as_octet_stream(self):
        flash = next(o for o in OPS if o["path"] == "/api/hardware/canota/flash")
        self.assertEqual(flash["body"], "Uint8Array")
        self.assertEqual(flash["body_media"], "application/octet-stream")
        self.assertIn('body: args?.body, access: "admin", contentType: "application/octet-stream"', SOURCE)
        self.assertIn("suspend fun postHardwareCanotaFlash(", KT)
        self.assertRegex(KT, r'postHardwareCanotaFlash\([^)]*body: ByteArray')
        self.assertRegex(DART, r"postHardwareCanotaFlash\(\{[^}]*required List<int> body")
        self.assertIn('contentType = "application/octet-stream"', KT)
        self.assertIn("contentType: 'application/octet-stream'", DART)

    def test_a_text_or_binary_answer_is_typed_and_flagged(self):
        text = {"responses": {"200": {"description": "ok", "content": {"application/x-ndjson": {"schema": {"type": "string"}}}}}}
        binary = {"responses": {"200": {"description": "ok", "content": {"application/octet-stream": {}}}}}
        self.assertEqual(gc.success_response(text)[0], "text")
        self.assertEqual(gc.success_type(text), "string")
        self.assertEqual(gc.success_response(binary)[0], "binary")
        self.assertEqual(gc.success_type(binary), "Uint8Array")
        self.assertEqual(gc.success_response({"responses": {"204": {"description": "none"}}})[0], "none")
        self.assertEqual(gc.success_type({"responses": {"204": {"description": "none"}}}), "void")
        self.assertEqual(gc.native_type(gc.success_schema(binary), gc.Flavor("kotlin"), frozenset()), "ByteArray")
        self.assertEqual(gc.native_type(gc.success_schema(binary), gc.Flavor("dart"), frozenset()), "List<int>")
        op = {"body": None, "body_media": None, "answer": "text", "reply_headers": ["ETag"]}
        self.assertEqual(gc.request_extras(op, False), [("responseType", "text")])
        self.assertEqual(gc.request_extras({**op, "answer": "json"}, True), [("replyHeaders", ["ETag"])])

    def test_a_route_that_declares_response_headers_has_a_with_headers_method_in_all_languages(self):
        declared = {(o["method"], o["path"]): o["reply_headers"] for o in OPS if o["reply_headers"]}
        self.assertEqual(declared[("GET", "/api/settings")], ["ETag"])
        self.assertEqual(declared[("GET", "/api/telemetry/query")], ["X-Next-Cursor"])
        for op in OPS:
            if not op["reply_headers"]:
                self.assertNotIn(f"{op['name']}WithHeaders", SOURCE)
                continue
            self.assertIn(f"  {op['name']}WithHeaders(", SOURCE)
            self.assertIn(f"    suspend fun {op['name']}WithHeaders(", KT)
            self.assertRegex(DART, rf"Future<HydraReply<[^\n]*> {op['name']}WithHeaders\(")
        self.assertIn("export interface HydraReply<T>", SOURCE)
        self.assertIn("class HydraReply<T>(val body: T, val headers: Map<String, String>)", KT)
        self.assertIn("class HydraReply<T> {", DART)
        self.assertIn('replyHeaders: ["ETag"]', SOURCE)
        self.assertIn('replyHeaders = listOf("ETag")', KT)
        self.assertIn("replyHeaders: const <String>['ETag']", DART)

    def test_a_method_name_that_would_collide_with_the_reply_variant_stops_the_generator(self):
        document = {"paths": {"/a/withHeaders": {"get": {}}}, "components": {"schemas": {}}}
        with self.assertRaises(SystemExit):
            gc.operations(document)


class TextVariantAndTypedAnswerTests(unittest.TestCase):
    """A JSON route that also offers text has an AsText method, and the routes that used to answer void are typed."""

    def test_a_json_route_that_also_offers_text_has_a_text_variant_in_all_languages(self):
        both = {"responses": {"200": {"description": "ok", "content": {"application/json": {"schema": {"type": "object"}}, "application/x-ndjson": {"schema": {"type": "string"}}}}}}
        self.assertTrue(gc.has_text_variant(both))
        self.assertFalse(gc.has_text_variant({"responses": {"200": {"description": "ok", "content": {"application/json": {"schema": {"type": "object"}}}}}}))
        self.assertFalse(gc.has_text_variant({"responses": {"200": {"description": "ok", "content": {"application/x-ndjson": {"schema": {"type": "string"}}}}}}))
        self.assertFalse(gc.has_text_variant({"responses": {"204": {"description": "none"}}}))
        wanted = {o["name"] for o in OPS if o["text_variant"]}
        self.assertEqual(wanted, {"getAudit"})
        for name in wanted:
            self.assertIn(f"  {name}AsText(", SOURCE)
            self.assertIn(f"    suspend fun {name}AsText(", KT)
            self.assertIn(f"  Future<String> {name}AsText(", DART)
        self.assertIn('query: queryOf(args?.query), headers: {}, body: undefined, access: "admin", responseType: "text" }) as Promise<string>;', SOURCE)
        self.assertIn('responseType = "text")) as String', KT)
        self.assertIn("responseType: 'text'))) as String;", DART)

    def test_a_text_variant_is_not_a_second_operation_and_a_clashing_name_stops_the_generator(self):
        self.assertNotIn("getAuditAsText", [o["name"] for o in OPS])
        document = {"paths": {"/a/asText": {"get": {}}}, "components": {"schemas": {}}}
        with self.assertRaises(SystemExit):
            gc.operations(document)

    def test_the_audit_route_offers_json_and_lines_and_the_other_routes_are_typed(self):
        audit = FULL["paths"]["/api/audit"]["get"]["responses"]["200"]["content"]
        self.assertEqual(set(audit), {"application/json", "application/x-ndjson"})
        self.assertEqual(audit["application/json"]["schema"], {"$ref": "#/components/schemas/AuditReport"})
        typed = {
            ("get", "/api/claims"): "ClaimList",
            ("get", "/api/safety-limits"): "SafetyLimitsView",
            ("post", "/api/voice/turn"): "VoiceReply",
            ("post", "/api/voice/confirm"): "VoiceConfirmResult",
        }
        for (method, path), shape in typed.items():
            schema = FULL["paths"][path][method]["responses"]["200"]["content"]["application/json"]["schema"]
            self.assertEqual(schema, {"$ref": f"#/components/schemas/{shape}"}, f"{method} {path}")
        for name in ("getClaims", "getSafetyLimits", "postVoiceTurn", "postVoiceConfirm", "getAudit"):
            self.assertNotIn(f"Future<void> {name}(", DART)
            self.assertNotIn(f"suspend fun {name}(): Unit", KT)

    def test_the_server_configuration_keeps_the_keys_it_does_not_list(self):
        self.assertIs(FULL["components"]["schemas"]["ServerConfig"].get("additionalProperties"), True)
        self.assertIn("val additionalProperties: Map<String, Any?>", KT)
        self.assertIn("final Map<String, dynamic> additionalProperties;", DART.split("class HydraServerConfig {", 1)[1].split("class HydraServerConfigSaved", 1)[0])

    def test_the_new_shapes_follow_the_handlers_of_the_server(self):
        schemas = FULL["components"]["schemas"]
        self.assertEqual(schemas["ClaimView"]["required"], ["robotId", "ownerUsername", "claimedAt", "expiresAt"])
        self.assertEqual(set(schemas["ClaimView"]["properties"]), {"robotId", "robotName", "cellId", "ownerId", "ownerUsername", "controllerId", "claimedAt", "expiresAt", "jogArmedUntil"})
        self.assertEqual(set(schemas["SafetyLimitsView"]["properties"]), {"limits", "defaults", "hardLimits", "robot"})
        self.assertEqual(set(schemas["SafetyLimitsConfig"]["properties"]), {"jog", "temperature", "claims", "audit"})
        self.assertEqual(schemas["AuditEntry"]["properties"]["outcome"]["enum"], ["ok", "refused", "failed"])
        self.assertEqual(set(schemas["AuditReport"]["properties"]), {"enabled", "lockedOff", "entries", "verification"})
        self.assertEqual(schemas["VoiceConfirmResult"]["properties"]["status"]["enum"], ["confirmed", "expired", "invalid"])


SYNTHETIC = json.loads((ROOT / "conformance" / "generated-clients" / "synthetic" / "openapi.json").read_text(encoding="utf-8"))


def build(flavor_name, document=SYNTHETIC):
    builder = gc.Builder(document, gc.Flavor(flavor_name))
    for name in sorted(builder.schemas):
        builder.reference(name)
    return builder


class ClassModelTests(unittest.TestCase):
    """The objects of the contract are classes with fields, fromJson and toJson in Kotlin and Dart."""

    def test_a_schema_with_properties_is_a_class_and_a_map_stays_an_alias(self):
        self.assertTrue(gc.is_class(SYNTHETIC["components"]["schemas"]["Open"]))
        self.assertFalse(gc.is_class(SYNTHETIC["components"]["schemas"]["Bag"]))
        self.assertFalse(gc.is_class({"type": "array", "items": {"type": "string"}}))
        kotlin = gc.as_kotlin(SYNTHETIC, "hydra.umc.synthetic")
        dart = gc.as_dart(SYNTHETIC)
        self.assertIn("package hydra.umc.synthetic", kotlin)
        self.assertIn("typealias HydraBag = Map<String, List<String>>", kotlin)
        self.assertIn("typedef HydraBag = Map<String, List<String>>;", dart)
        self.assertIn("data class HydraClosed(", kotlin)
        self.assertIn("class HydraClosed {", dart)

    def test_every_class_has_from_json_and_to_json_in_both_languages(self):
        for name, schema in FULL["components"]["schemas"].items():
            if not gc.is_class(schema):
                continue
            self.assertIn(f"fun fromJson(json: Map<String, Any?>): Hydra{name} = Hydra{name}(", KT)
            self.assertIn(f"factory Hydra{name}.fromJson(Map<String, dynamic> json) => Hydra{name}(", DART)
        self.assertEqual(KT.count("    fun toJson(): Map<String, Any?> {"), KT.count("fun fromJson(json: Map<String, Any?>)"))
        self.assertEqual(DART.count("  Map<String, dynamic> toJson() {"), DART.count("factory Hydra"))

    def test_the_fields_follow_the_contract(self):
        kotlin = build("kotlin")
        fields = {f["wire"]: f for f in kotlin.defs["HydraOpen"]["fields"]}
        self.assertTrue(fields["name"]["required"])
        self.assertEqual(fields["name"]["native"].type, "String")
        self.assertEqual(fields["note"]["native"].type, "String?")
        self.assertTrue(fields["note"]["required"])
        self.assertEqual(fields["mode"]["native"].type, "String?")
        self.assertEqual(fields["in"]["name"], "inValue")
        self.assertEqual(fields["class"]["name"], "classValue")
        self.assertEqual(fields["scores"]["native"].type, "Map<String, Long>?")
        self.assertEqual(fields["tags"]["native"].type, "List<String>?")
        dart = build("dart")
        self.assertEqual({f["wire"]: f["native"].type for f in dart.defs["HydraOpen"]["fields"]}["scores"], "Map<String, int>?")

    def test_field_names_are_camel_case_and_never_a_member_of_the_class(self):
        for flavor_name in ("kotlin", "dart"):
            builder = build(flavor_name, FULL)
            members = gc.KOTLIN_MEMBERS if flavor_name == "kotlin" else gc.DART_MEMBERS
            for name, definition in builder.defs.items():
                names = [f["name"] for f in definition["fields"]]
                self.assertEqual(len(names), len(set(names)), name)
                self.assertFalse(set(names) & members, name)
                self.assertFalse(set(names) & builder.flavor.words, name)
                for ident in names:
                    self.assertRegex(ident, r"^[a-z][A-Za-z0-9]*$", name)

    def test_additional_properties_open_keeps_the_keys_and_closed_drops_them(self):
        kotlin = build("kotlin")
        self.assertIsNotNone(kotlin.defs["HydraOpen"]["open"])
        self.assertEqual(kotlin.defs["HydraOpen"]["open"]["native"].type, "Map<String, Any?>")
        self.assertEqual(kotlin.defs["HydraOpenTyped"]["open"]["native"].type, "Map<String, Double>")
        self.assertIsNone(kotlin.defs["HydraClosed"]["open"])
        self.assertIsNone(kotlin.defs["HydraTree"]["open"])
        text = gc.as_kotlin(SYNTHETIC)
        self.assertIn('private val knownKeys: Set<String> = setOf("name", "note", "class", "in", "mode", "tags", "scores", "nested")', text)
        self.assertIn("jsonOut.putAll(additionalProperties)", text)
        self.assertIn("static const Set<String> _knownKeys", gc.as_dart(SYNTHETIC))

    def test_a_schema_that_refers_to_itself_is_an_ordinary_class(self):
        kotlin = gc.as_kotlin(SYNTHETIC)
        self.assertIn("val children: List<HydraTree>? = null", kotlin)
        self.assertIn("val parent: HydraTree? = null", kotlin)
        self.assertIn("HydraTree.fromJson(hydraMap(v1))", kotlin)
        dart = gc.as_dart(SYNTHETIC)
        self.assertIn("final List<HydraTree>? children;", dart)
        self.assertIn("final HydraTree? parent;", dart)

    def test_inline_objects_get_a_class_named_after_where_they_are(self):
        builder = build("kotlin")
        text = gc.as_kotlin(SYNTHETIC)
        self.assertIn("HydraOpenNested", builder.defs)
        self.assertIn("HydraOpenNestedPointsItem", builder.defs)
        self.assertIn("val points: List<HydraOpenNestedPointsItem>? = null", text)
        command = next(o for o in OPS if o["name"] == "postRobotByIdCommand")
        self.assertIn("HydraPostRobotByIdCommandBody", KT)
        self.assertIn("HydraPostRobotByIdCommandResult", KT)
        self.assertEqual(command["body_schema"].get("type"), "object")
        self.assertNotIn("HydraPostRobotByIdCommandBody2", KT)

    def test_a_request_body_is_sent_as_the_plain_json_model_and_the_answer_is_read_into_its_class(self):
        self.assertIn("body.toJson()", KT)
        self.assertIn("body.toJson()", DART)
        self.assertIn("return HydraLogLines.fromJson(hydraMap(raw))", KT)
        self.assertIn("return HydraLogLines.fromJson(_hydraMap(raw));", DART)
        self.assertIn("HydraReply<HydraSettings>(HydraSettings.fromJson(hydraMap(reply.body)), reply.headers)", KT)
        self.assertIn("HydraReply<HydraSettings>(HydraSettings.fromJson(_hydraMap(reply.body)), reply.headers)", DART)
        self.assertIn("body?.toJson()", gc.as_kotlin(SYNTHETIC))

    def test_the_requests_keep_their_shape(self):
        self.assertIn('transport.send(HydraRequest("GET", "/api/admin/logs", queryOf(mapOf("lines" to lines)), null, "admin"))', KT)
        self.assertIn("_transport(HydraRequest('GET', '/api/admin/logs', queryOf({'lines': lines}), null, 'admin'))", DART)
        self.assertIn('contentType = "application/octet-stream"', KT)
        self.assertIn("contentType: 'application/octet-stream'", DART)
        self.assertIn('replyHeaders = listOf("ETag")', KT)

    def test_the_helpers_are_private_and_need_no_library(self):
        self.assertIn("private fun hydraMap(value: Any?)", KT)
        self.assertIn("private fun hydraList(value: Any?)", KT)
        self.assertIn("Map<String, dynamic> _hydraMap(Object? value)", DART)
        for text in (KT, DART):
            self.assertNotRegex(text, r"(?m)^import (org\.json|kotlinx|com\.google)")
            self.assertNotIn("dart:convert", text)

    def test_the_typescript_client_keeps_real_interfaces_with_fields(self):
        self.assertRegex(SOURCE, r"export interface ConnectionClient \{\n  schema_version:")
        self.assertIn("export interface ConnectionClient {", SOURCE)
        closed = re.search(r"export interface ConnectionClient \{.*?\n\}", SOURCE, flags=re.S).group(0)
        self.assertNotIn("[other: string]", closed)

    def test_an_example_is_built_from_the_schema(self):
        schemas = SYNTHETIC["components"]["schemas"]
        full = gc.example_of(schemas["Open"], schemas, True, ("Open",))
        self.assertEqual(full["name"], "text")
        self.assertEqual(full["extraKey"], "extra")
        self.assertEqual(full["mode"], "fast")
        self.assertEqual(full["nested"]["points"][0]["x"], 1.5)
        minimal = gc.example_of(schemas["Open"], schemas, False, ("Open",))
        self.assertEqual(set(minimal), {"name", "note"})
        tree = gc.example_of(schemas["Tree"], schemas, True, ("Tree",))
        self.assertEqual(tree["children"], [])
        self.assertNotIn("parent", tree)

    def test_the_round_trip_files_cover_every_class_of_the_contract(self):
        classes = [n for n, s in FULL["components"]["schemas"].items() if gc.is_class(s)]
        kotlin = (gc.target(gc.KT_ROUND_TRIP_NAME)).read_text(encoding="utf-8")
        dart = (gc.target(gc.DART_ROUND_TRIP_NAME)).read_text(encoding="utf-8")
        for name in classes:
            self.assertIn(f"private fun roundTripHydra{name}()", kotlin)
            self.assertIn(f"_roundTrip<Hydra{name}>(failures, 'Hydra{name} full'", dart)
        self.assertIn(f"const val ROUND_TRIP_CLASSES: Int = {len(classes)}", kotlin)
        self.assertGreater(len(classes), 40)

    def test_the_generator_writes_a_second_document_into_a_folder(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            code = gc.main(["--spec", str(ROOT / "conformance" / "generated-clients" / "synthetic" / "openapi.json"), "--out", folder,
                            "--kotlin-package", "hydra.umc.synthetic"])
            self.assertEqual(code, 0)
            names = sorted(p.name for p in Path(folder).iterdir())
            self.assertEqual(names, sorted([gc.TS_NAME, gc.KT_NAME, gc.DART_NAME, gc.KT_ROUND_TRIP_NAME, gc.DART_ROUND_TRIP_NAME]))
            self.assertIn("package hydra.umc.synthetic", (Path(folder) / gc.KT_NAME).read_text(encoding="utf-8"))
        with self.assertRaises(SystemExit):
            gc.main(["--spec", "x.json"])

    def test_nullable_and_union_schemas(self):
        builder = gc.Builder({"components": {"schemas": {}}}, gc.Flavor("kotlin"))
        self.assertEqual(builder.native({"anyOf": [{"type": "string"}, {"type": "null"}]}, "X").type, "String?")
        self.assertEqual(builder.native({"anyOf": [{"type": "string"}, {"type": "integer"}]}, "X").type, "Any?")
        self.assertEqual(builder.native({"const": "system_status"}, "X").type, "String")
        self.assertEqual(builder.native({"type": "string", "format": "binary"}, "X").type, "ByteArray")
        self.assertEqual(builder.native({"type": ["object", "null"]}, "X").type, "Map<String, Any?>?")
        self.assertEqual(builder.native({}, "X").type, "Any?")
        dart = gc.Builder({"components": {"schemas": {}}}, gc.Flavor("dart"))
        self.assertEqual(dart.native({"type": "array", "items": {"type": ["integer", "null"]}}, "X").type, "List<int?>")
        self.assertEqual(dart.native({"type": "number"}, "X").decode("v", 0), "v as num")
        self.assertEqual(builder.native({"type": "integer"}, "X").decode("v", 0), "(v as Number).toLong()")

    def test_a_dollar_sign_in_a_kotlin_name_is_escaped(self):
        self.assertEqual(gc.kt_string("a$b"), '"a\\$b"')
        self.assertEqual(gc.dart_string("a$b"), "'a\\$b'")
