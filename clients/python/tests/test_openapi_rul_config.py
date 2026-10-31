# =============================================================================
# HYDRA-UMC-SDK - The remaining-useful-life setting route in the OpenAPI documents
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import json
import unittest
from pathlib import Path

OPENAPI = Path(__file__).resolve().parents[3] / "contracts" / "openapi" / "v1"
ROUTE = "/api/rul/config"
FIELDS = ["enabled", "maxPoints", "timeoutMs"]


def _load(name: str) -> dict:
    return json.loads((OPENAPI / name).read_text(encoding="utf-8"))


class OpenApiRulConfigTests(unittest.TestCase):
    def test_both_documents_list_one_read_for_any_signed_in_account(self):
        typed = _load("server.openapi.json")["paths"][ROUTE]
        full = _load("server.full.openapi.json")["paths"][ROUTE]
        self.assertEqual(list(typed), ["get"])
        self.assertEqual(list(full), ["get"])
        self.assertEqual(typed["get"]["security"], [{"bearerAuth": []}])
        self.assertEqual(full["get"]["x-access"], "user", "no role is asked, so a viewer may read it")

    def test_the_answer_is_exactly_the_three_fields_and_closed(self):
        typed = _load("server.openapi.json")["components"]["schemas"]["RulConfig"]
        self.assertIs(typed["additionalProperties"], False)
        self.assertEqual(sorted(typed["required"]), sorted(FIELDS))
        self.assertEqual(sorted(typed["properties"]), sorted(FIELDS))
        self.assertEqual([typed["properties"][name]["type"] for name in FIELDS], ["boolean", "integer", "integer"])
        reference = _load("server.openapi.json")["paths"][ROUTE]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        self.assertEqual(reference, "#/components/schemas/RulConfig")

    def test_the_typed_slice_and_the_full_copy_agree_on_the_shape_and_the_limits(self):
        typed = _load("server.openapi.json")["components"]["schemas"]["RulConfig"]["properties"]
        full = _load("server.full.openapi.json")["components"]["schemas"]["RulConfig"]["properties"]
        for name in FIELDS:
            with self.subTest(field=name):
                for key in ("type", "minimum", "maximum"):
                    self.assertEqual(typed[name].get(key), full[name].get(key))

    def test_only_a_missing_session_is_an_error_in_the_typed_slice(self):
        responses = _load("server.openapi.json")["paths"][ROUTE]["get"]["responses"]
        self.assertEqual(sorted(responses), ["200", "401"], "a damaged configuration is a closed 200, never an error")


if __name__ == "__main__":
    unittest.main()
