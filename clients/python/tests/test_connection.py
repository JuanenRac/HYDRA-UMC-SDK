# =============================================================================
# HYDRA-UMC-SDK - ConnectionEvent and ConnectionClient contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import json
import unittest
from pathlib import Path

from hydra_umc_sdk import CLIENT_KINDS, CONNECTION_ACTIONS, ContractValidationError, validate

FIXTURES = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1"


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ConnectionEventTests(unittest.TestCase):
    def test_the_fixtures_are_judged_as_their_names_say(self):
        validate("ConnectionEvent", _fixture("connection-event.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("ConnectionEvent", _fixture("connection-event.invalid.json"))

    def test_every_action_and_every_kind_is_accepted(self):
        for action in CONNECTION_ACTIONS:
            for kind in CLIENT_KINDS:
                with self.subTest(action=action, kind=kind):
                    validate("ConnectionEvent", dict(_fixture("connection-event.valid.json"), action=action, client_kind=kind))

    def test_a_secret_cannot_be_added(self):
        for field in ("password", "token", "cookie", "pin", "recovery_code"):
            with self.subTest(field=field), self.assertRaises(ContractValidationError):
                validate("ConnectionEvent", dict(_fixture("connection-event.valid.json"), **{field: "x"}))

    def test_the_date_must_be_an_rfc_3339_date_time(self):
        for bad in ("yesterday", "2026-01-01", "2026-13-45T00:00:00Z", 5):
            with self.subTest(bad=bad), self.assertRaises(ContractValidationError):
                validate("ConnectionEvent", dict(_fixture("connection-event.valid.json"), at_utc=bad))

    def test_the_address_and_the_agent_are_optional_and_limited(self):
        base = _fixture("connection-event.valid.json")
        validate("ConnectionEvent", dict(base, ip="192.168.0.20", agent="Mozilla/5.0"))
        for field, size in (("ip", 65), ("agent", 121), ("user", 61)):
            with self.subTest(field=field), self.assertRaises(ContractValidationError):
                validate("ConnectionEvent", dict(base, **{field: "x" * size}))


class ConnectionClientTests(unittest.TestCase):
    def test_the_fixtures_are_judged_as_their_names_say(self):
        validate("ConnectionClient", _fixture("connection-client.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("ConnectionClient", _fixture("connection-client.invalid.json"))

    def test_the_counters_are_integers_from_zero(self):
        base = _fixture("connection-client.valid.json")
        for field in ("active_sessions", "logins_ok", "logins_failed"):
            for bad in (-1, "1", 1.5, True):
                with self.subTest(field=field, bad=bad), self.assertRaises(ContractValidationError):
                    validate("ConnectionClient", dict(base, **{field: bad}))

    def test_a_client_without_user_or_failure_is_valid(self):
        base = _fixture("connection-client.valid.json")
        base.pop("user")
        base.pop("last_failure_utc")
        validate("ConnectionClient", base)


if __name__ == "__main__":
    unittest.main()
