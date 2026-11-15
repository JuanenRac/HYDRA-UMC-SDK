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
        for name in (gc.KT_NAME, gc.DART_NAME):
            committed = (ROOT / "generated" / name).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(committed, produced[name].encode("utf-8"), name)

    def test_every_route_has_a_method_with_the_same_name_in_all_three_languages(self):
        for op in OPS:
            self.assertIn(f"    suspend fun {op['name']}(", KT)
            self.assertRegex(DART, rf"  Future<[^\n]*> {op['name']}\(")
        listed_kt = re.findall(r'^    "([A-Za-z0-9]+)",$', KT, flags=re.M)
        listed_dart = re.findall(r"^  '([A-Za-z0-9]+)',$", DART, flags=re.M)
        self.assertEqual(listed_kt, [o["name"] for o in OPS])
        self.assertEqual(listed_dart, listed_kt)

    def test_every_named_schema_is_an_alias(self):
        for name in FULL["components"]["schemas"]:
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
            for op in OPS:
                params, _ = gc.native_arguments(op, flavor, frozenset())
                names = [p[0] for p in params]
                self.assertEqual(len(names), len(set(names)), op["name"])
                self.assertFalse(set(names) & flavor.words, op["name"])

    def test_the_optional_arguments_come_last_and_may_be_omitted(self):
        for op in OPS:
            params, _ = gc.native_arguments(op, gc.Flavor("kotlin"), frozenset())
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
