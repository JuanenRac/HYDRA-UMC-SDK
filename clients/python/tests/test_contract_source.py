# =============================================================================
# HYDRA-UMC-SDK - Tests of the contract source of the connection routes
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Pins the contract of the connection routes as the server offers it today (characterization) and proves that the
drift check of tools/contract_source.py fails when the generated document, a schema copy, the server or a client drifts."""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location("contract_source", ROOT / "tools" / "contract_source.py")
cs = importlib.util.module_from_spec(_spec)
sys.modules["contract_source"] = cs
_spec.loader.exec_module(cs)

SOURCE = cs.load_sources()["connections"]
GENERATED = cs.build_document(SOURCE)
KINDS = ["studio", "suite", "android", "ios", "dsi", "watch", "voice", "other"]
ACTIONS = ["first_seen", "login", "login_failed", "second_factor_failed", "logout", "session_ended", "session_expired"]


def server_view(document: dict) -> dict:
    """What the server's generated inventory looks like for the same routes: every query parameter a plain string, the
    status codes the handler produces, the 401 a shared middleware adds, and the schemas written by hand in its types."""
    view = copy.deepcopy(document)
    for item in view["paths"].values():
        for operation in item.values():
            for parameter in operation["parameters"]:
                parameter["schema"] = {"type": "string"}
            operation["responses"]["401"] = {"description": "Not signed in"}
    return view


class CharacterizationTests(unittest.TestCase):
    """The routes and the shapes the server offers today."""

    def test_the_routes_and_their_access(self):
        routes = {(method, path): operation for path, item in GENERATED["paths"].items() for method, operation in item.items()}
        self.assertEqual(sorted(routes), [("get", "/api/connections/clients"), ("get", "/api/connections/events")])
        for operation in routes.values():
            self.assertEqual(operation["x-access"], "user")
            self.assertEqual(operation["security"], [{"bearerAuth": []}])
            self.assertEqual(sorted(operation["responses"]), ["200", "400"])

    def test_the_query_parameters(self):
        def parameters(path):
            return {p["name"]: p["schema"] for p in GENERATED["paths"][path]["get"]["parameters"]}

        clients = parameters("/api/connections/clients")
        self.assertEqual(sorted(clients), ["active", "kind", "user"])
        self.assertEqual(clients["kind"]["enum"], KINDS)
        self.assertEqual(clients["active"]["enum"], ["1", "true"])
        events = parameters("/api/connections/events")
        self.assertEqual(sorted(events), ["action", "before", "kind", "limit", "user"])
        self.assertEqual(events["action"]["enum"], ACTIONS)
        self.assertEqual(events["limit"]["pattern"], "^\\d{1,9}$")
        self.assertEqual(events["before"]["pattern"], "^\\d{1,9}$")

    def test_the_answers_are_lists_of_the_closed_schemas(self):
        schemas = GENERATED["components"]["schemas"]
        self.assertEqual(schemas["ConnectionClientList"]["properties"]["clients"]["items"], {"$ref": "#/components/schemas/ConnectionClient"})
        self.assertEqual(schemas["ConnectionEventList"]["properties"]["events"]["items"], {"$ref": "#/components/schemas/ConnectionEvent"})
        for name in ("ConnectionClient", "ConnectionEvent"):
            self.assertIs(schemas[name]["additionalProperties"], False, name)
            forbidden = {"password", "token", "cookie", "secret", "code", "totp"}
            self.assertFalse(forbidden & set(schemas[name]["properties"]), name)

    def test_the_closed_schemas_are_the_ones_of_the_sdk(self):
        self.assertEqual(sorted(SOURCE["schemas"]), ["ConnectionClient", "ConnectionEvent"])
        client = cs.schema_of("ConnectionClient", SOURCE)
        self.assertEqual(client["required"], ["schema_version", "id", "kind", "first_seen_utc", "last_seen_utc", "active_sessions", "logins_ok", "logins_failed"])
        self.assertEqual(cs.enum_of("ConnectionEvent.action", SOURCE), ACTIONS)
        self.assertEqual(cs.enum_of("ConnectionClient.kind", SOURCE), KINDS)


class RepositoryStateTests(unittest.TestCase):
    def test_the_generated_document_is_what_the_source_produces(self):
        self.assertEqual(cs.check_generated("connections", SOURCE), [])

    def test_every_schema_copy_is_identical_and_listed_with_its_hash(self):
        self.assertEqual(cs.check_schema_copies(SOURCE), [])

    def test_the_command_line_check_passes(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cs.main(["--check"])
        self.assertEqual(code, 0, err.getvalue())
        self.assertIn("CONTRACT_SOURCE=PASS", out.getvalue())

    def test_without_any_checkout_the_check_skips_and_with_the_requirement_it_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(cs.run_check(Path(tmp), None, []), 0)
            self.assertIn("CONTRACT_SOURCE=SKIP", out.getvalue())
            import os
            os.environ["HYDRA_UMC_REQUIRE_WORKSPACE"] = "1"
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(cs.run_check(Path(tmp), None, []), 1)
            finally:
                del os.environ["HYDRA_UMC_REQUIRE_WORKSPACE"]


class ServerDriftTests(unittest.TestCase):
    def setUp(self):
        self.server = server_view(GENERATED)

    def test_a_server_that_offers_the_source_has_no_differences(self):
        self.assertEqual(cs.compare_with_server_document(SOURCE, self.server), [])

    def test_a_route_the_server_does_not_register(self):
        del self.server["paths"]["/api/connections/events"]
        self.assertIn("does not register", "\n".join(cs.compare_with_server_document(SOURCE, self.server)))

    def test_a_different_access(self):
        del self.server["paths"]["/api/connections/clients"]["get"]["security"]
        self.assertIn("access differs", "\n".join(cs.compare_with_server_document(SOURCE, self.server)))

    def test_a_status_the_handler_stopped_producing_or_started_producing(self):
        del self.server["paths"]["/api/connections/events"]["get"]["responses"]["400"]
        self.assertIn("never produces it", "\n".join(cs.compare_with_server_document(SOURCE, self.server)))
        self.server = server_view(GENERATED)
        self.server["paths"]["/api/connections/events"]["get"]["responses"]["404"] = {"description": "x"}
        self.assertIn("does not list it", "\n".join(cs.compare_with_server_document(SOURCE, self.server)))

    def test_a_middleware_status_is_not_a_difference(self):
        self.server["paths"]["/api/connections/events"]["get"]["responses"]["429"] = {"description": "x"}
        self.assertEqual(cs.compare_with_server_document(SOURCE, self.server), [])

    def test_a_query_parameter_added_or_removed(self):
        parameters = self.server["paths"]["/api/connections/events"]["get"]["parameters"]
        parameters.append({"name": "order", "in": "query", "schema": {"type": "string"}})
        self.assertIn("reads the query parameter 'order'", "\n".join(cs.compare_with_server_document(SOURCE, self.server)))
        parameters.pop()
        parameters.pop(0)
        self.assertIn("never reads it", "\n".join(cs.compare_with_server_document(SOURCE, self.server)))

    def test_a_schema_that_drifts(self):
        schemas = self.server["components"]["schemas"]
        schemas["ConnectionEvent"]["required"].remove("client_id")
        self.assertIn("schema ConnectionEvent", "\n".join(cs.compare_with_server_document(SOURCE, self.server)))
        self.server = server_view(GENERATED)
        self.server["components"]["schemas"]["ConnectionClient"]["properties"]["kind"]["enum"].append("kiosk")
        self.assertIn("schema ConnectionClient", "\n".join(cs.compare_with_server_document(SOURCE, self.server)))
        self.server = server_view(GENERATED)
        del self.server["components"]["schemas"]["ConnectionClient"]["properties"]["app_version"]["pattern"]
        self.assertIn("schema ConnectionClient", "\n".join(cs.compare_with_server_document(SOURCE, self.server)))
        self.server = server_view(GENERATED)
        self.server["components"]["schemas"]["ConnectionEvent"]["additionalProperties"] = True
        self.assertIn("schema ConnectionEvent", "\n".join(cs.compare_with_server_document(SOURCE, self.server)))
        self.server = server_view(GENERATED)
        del self.server["components"]["schemas"]["ConnectionEvent"]
        self.assertIn("does not carry it", "\n".join(cs.compare_with_server_document(SOURCE, self.server)))

    def test_the_enums_of_the_server_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            kinds = ", ".join(f'"{k}"' for k in KINDS)
            actions = ", ".join(f'"{a}"' for a in ACTIONS)
            text = f"export const CLIENT_KINDS = [{kinds}] as const;\nexport const CONNECTION_ACTIONS = [{actions}] as const;\n"
            (root / "src" / "connections.ts").write_text(text, encoding="utf-8")
            self.assertEqual(cs.compare_server_enums(SOURCE, root), [])
            (root / "src" / "connections.ts").write_text(text.replace('"voice", ', ""), encoding="utf-8")
            self.assertIn("CLIENT_KINDS differs", "\n".join(cs.compare_server_enums(SOURCE, root)))
            (root / "src" / "connections.ts").write_text("nothing", encoding="utf-8")
            self.assertIn("not found", "\n".join(cs.compare_server_enums(SOURCE, root)))


class SchemaCopyDriftTests(unittest.TestCase):
    def make_copy(self, tmp: str) -> Path:
        clients = Path(tmp) / "clients"
        directory = clients / "go" / "schemas"
        directory.mkdir(parents=True)
        for path in cs.SCHEMAS.iterdir():
            if path.is_file():
                shutil.copy(path, directory / path.name)
        return clients

    def test_a_copy_that_differs_or_is_missing_or_unlisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            clients = self.make_copy(tmp)
            directory = clients / "go" / "schemas"
            # The temporary copy is outside the repository, so the labels are absolute; the check must still pass.
            self.assertEqual(cs.check_schema_copies(SOURCE, clients), [])
            (directory / "connection-event.schema.json").write_text("{}\n", encoding="utf-8")
            self.assertIn("differs", "\n".join(cs.check_schema_copies(SOURCE, clients)))
            (directory / "connection-event.schema.json").write_bytes((cs.SCHEMAS / "connection-event.schema.json").read_bytes())
            manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
            for entry in manifest["contracts"]:
                if entry["file"] == "connection-event.schema.json":
                    entry["sha256"] = "0" * 64
            (directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertIn("another hash", "\n".join(cs.check_schema_copies(SOURCE, clients)))
            (directory / "connection-client.schema.json").unlink()
            self.assertIn("is missing", "\n".join(cs.check_schema_copies(SOURCE, clients)))

    def test_a_manifest_that_cannot_be_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            clients = self.make_copy(tmp)
            (clients / "go" / "schemas" / "manifest.json").write_text("not json", encoding="utf-8")
            self.assertIn("cannot be read", "\n".join(cs.check_schema_copies(SOURCE, clients)))


class ConsumerDriftTests(unittest.TestCase):
    def scan(self, text: str, suffix: str = ".ts") -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "client"
            (root / "src").mkdir(parents=True)
            (root / "src" / f"api{suffix}").write_text(text, encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "skipped.ts").write_text('"/api/connections/unknown"', encoding="utf-8")
            return cs.scan_consumer(SOURCE, root)

    def test_declared_routes_and_parameters_pass(self):
        self.assertEqual(self.scan('get("/api/connections/clients?kind=studio&active=1")'), [])
        self.assertEqual(self.scan("`/api/connections/events?limit=${n}&before=${id}`"), [])
        self.assertEqual(self.scan('url = "/api/connections/clients/"'), [])
        self.assertEqual(self.scan('"/api/login"'), [])

    def test_an_unknown_route_is_reported(self):
        self.assertIn("/api/connections/purge", "\n".join(self.scan('post("/api/connections/purge")')))

    def test_an_undeclared_query_parameter_is_reported(self):
        self.assertIn("'sort'", "\n".join(self.scan('get("/api/connections/events?sort=asc")')))
        self.assertIn("'limit'", "\n".join(self.scan('"/api/connections/clients?user=x&limit=3"')))

    def test_a_python_client_is_scanned_too(self):
        self.assertIn("'zone'", "\n".join(self.scan('requests.get(BASE + "/api/connections/clients?zone=1")', ".py")))


class SourceErrorTests(unittest.TestCase):
    def test_a_source_that_names_a_missing_property(self):
        with self.assertRaises(cs.SourceError):
            cs.enum_of("ConnectionClient.nothing", SOURCE)
        with self.assertRaises(cs.SourceError):
            cs.enum_of("ConnectionClient.id", SOURCE)
        with self.assertRaises(cs.SourceError):
            cs.schema_of("Nothing", SOURCE)

    def test_two_sources_cannot_claim_the_same_route(self):
        self.assertEqual(cs.duplicate_routes({"connections": SOURCE}), [])
        problems = cs.duplicate_routes({"one": SOURCE, "two": SOURCE})
        self.assertEqual(len(problems), 2)
        self.assertIn("declared by both one and two", problems[0])

    def test_a_folder_without_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(cs.SourceError):
                cs.load_sources(Path(tmp))

    def test_the_generator_writes_the_same_bytes_that_are_committed(self):
        self.assertEqual(cs.output_path(SOURCE).read_text(encoding="utf-8").replace("\r\n", "\n"), cs.render(GENERATED))
        json.loads(cs.render(GENERATED))


if __name__ == "__main__":
    unittest.main()
