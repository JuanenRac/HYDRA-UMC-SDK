# =============================================================================
# HYDRA-UMC-SDK - tests of tools/verify_openapi.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The verifier must accept a sound document and refuse each kind of damage."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[3] / "tools"
_spec = importlib.util.spec_from_file_location("verify_openapi", TOOLS / "verify_openapi.py")
VERIFY = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(VERIFY)

GOOD = {
    "openapi": "3.0.3",
    "info": {"title": "t", "version": "1"},
    "paths": {
        "/a": {"get": {"operationId": "getA", "responses": {"200": {"description": "ok", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/A~1B"}}}}}}},
        "/b": {"delete": {"operationId": "deleteB", "responses": {"204": {"description": "gone"}}}},
    },
    "components": {"schemas": {"A/B": {"type": "object"}}},
}


class VerifyOpenApiTests(unittest.TestCase):
    def check(self, document: dict) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.openapi.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            # verify_document reports paths relative to the repository root
            VERIFY.ROOT = Path(tmp)
            VERIFY.verify_document(path)

    def test_a_sound_document_passes_and_json_pointer_escapes_are_decoded(self) -> None:
        self.check(GOOD)
        self.assertTrue(VERIFY.resolve_pointer(GOOD, "#/components/schemas/A~1B"))
        self.assertFalse(VERIFY.resolve_pointer(GOOD, "#/components/schemas/A"))

    def test_a_repeated_operation_id_is_refused(self) -> None:
        bad = copy.deepcopy(GOOD)
        bad["paths"]["/b"]["delete"]["operationId"] = "getA"
        with self.assertRaises(SystemExit):
            self.check(bad)

    def test_a_2xx_response_with_content_but_no_schema_is_refused(self) -> None:
        bad = copy.deepcopy(GOOD)
        bad["paths"]["/a"]["get"]["responses"]["200"]["content"]["application/json"] = {}
        with self.assertRaises(SystemExit):
            self.check(bad)

    def test_a_broken_reference_is_refused(self) -> None:
        bad = copy.deepcopy(GOOD)
        bad["paths"]["/a"]["get"]["responses"]["200"]["content"]["application/json"]["schema"] = {"$ref": "#/components/schemas/Missing"}
        with self.assertRaises(SystemExit):
            self.check(bad)


if __name__ == "__main__":
    unittest.main()
