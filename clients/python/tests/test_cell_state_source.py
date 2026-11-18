# =============================================================================
# HYDRA-UMC-SDK - Cell state source tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The three sources of the state of a cell, and what the reader does with a verdict it cannot trust."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from hydra_umc_sdk.cell_state_source import (
    ALGORITHM_ED25519,
    CellStateSource,
    CellStateSourceConfig,
    CellStateSourceError,
    _message,
    config_from_environment,
    fresh_text,
)

KEY = "k" * 40
NOW_MS = 1_800_000_000_000


def stamp(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def verdict(state: str = "READY", *, counter: int = 10, at_ms: int = NOW_MS, key: str = KEY, key_id: str = "default", extra: dict | None = None) -> dict:
    sdk_state = {"schema_version": "1.0", "state": state, "source": "safety-zones", "timestamp_utc": stamp(at_ms)}
    sig = hmac.new(key.encode(), _message(sdk_state, counter, key_id), hashlib.sha256).hexdigest()
    payload = {"sdkSafetyState": sdk_state, "reason": None, "sdkSafetyStateSignature": {"alg": "HMAC-SHA256", "key_id": key_id, "counter": counter, "sig": sig}}
    payload.update(extra or {})
    return payload


class WithFiles(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.dir = Path(self._dir.name)
        self.key_file = self.dir / "key.txt"
        self.key_file.write_text(KEY, encoding="utf-8")

    def write(self, name: str, text: str, mtime: float | None = None) -> str:
        path = self.dir / name
        path.write_text(text, encoding="utf-8")
        if mtime is not None:
            os.utime(path, (mtime, mtime))
        return str(path)

    def zones(self, payload: dict | str, **changes: object) -> CellStateSource:
        path = self.write("state.json", payload if isinstance(payload, str) else json.dumps(payload))
        config = CellStateSourceConfig(source="safety_zones", path=path, key_file=str(self.key_file), **changes)  # type: ignore[arg-type]
        return CellStateSource(config, wall_clock_ms=lambda: NOW_MS)


class TheFixedSource(unittest.TestCase):
    def test_it_answers_the_configured_word(self):
        self.assertEqual(CellStateSource(CellStateSourceConfig(source="fixed", value="INHIBITED"))(), "INHIBITED")
        described = CellStateSource(CellStateSourceConfig()).describe()
        self.assertEqual((described["cell_source"], described["state"]), ("fixed", "READY"))

    def test_a_configuration_that_cannot_work_is_refused_when_it_is_built(self):
        for changes in (
            {"source": "gpio"},
            {"value": "ready"},
            {"max_age_seconds": 0},
            {"max_age_seconds": True},
            {"algorithm": "RSA"},
            {"source": "file"},
            {"source": "safety_zones", "key_file": "k"},
            {"source": "safety_zones", "path": "p", "url": "http://x/", "key_file": "k"},
            {"source": "safety_zones", "path": "p"},
            {"source": "safety_zones", "url": "ftp://x/", "key_file": "k"},
            {"source": "safety_zones", "path": "p", "algorithm": ALGORITHM_ED25519},
        ):
            with self.assertRaises(CellStateSourceError, msg=str(changes)):
                CellStateSourceConfig(**changes)  # type: ignore[arg-type]


class TheFileSource(WithFiles):
    def reader(self, path: str, now: float) -> CellStateSource:
        return CellStateSource(CellStateSourceConfig(source="file", path=path, max_age_seconds=5), clock=lambda: now)

    def test_a_fresh_word_is_read_and_everything_else_is_a_safe_stop(self):
        path = self.write("cell.txt", "READY extra words\n", mtime=1000.0)
        self.assertEqual(self.reader(path, 1002.0)(), "READY")
        self.assertEqual(self.reader(path, 1010.0)(), "SAFE_STOP")
        self.assertEqual(self.reader(path, 990.0)(), "SAFE_STOP")
        self.assertEqual(self.reader(str(self.dir / "missing"), 1000.0)(), "SAFE_STOP")
        self.assertEqual(self.reader(self.write("empty.txt", "  \n", mtime=1000.0), 1000.0)(), "SAFE_STOP")
        self.assertEqual(self.reader(self.write("odd.txt", "GO\n", mtime=1000.0), 1000.0)(), "SAFE_STOP")
        self.assertEqual(self.reader(self.write("lower.txt", "ready\n", mtime=1000.0), 1000.0)(), "SAFE_STOP")

    def test_the_text_of_a_file_is_found_by_the_helper(self):
        path = self.write("cell.txt", "FAULT\n", mtime=500.0)
        self.assertEqual(fresh_text(path, 5, lambda: 501.0), "FAULT")
        self.assertIsNone(fresh_text(path, 5, lambda: 600.0))

    def test_the_answer_says_where_it_came_from_and_why(self):
        source = self.reader(str(self.dir / "missing"), 1000.0)
        described = source.describe()
        self.assertEqual((described["cell_source"], described["state"]), ("file", "SAFE_STOP"))
        self.assertIn("missing", described["reason"])


class TheSafetyZonesSource(WithFiles):
    def test_a_signed_fresh_verdict_is_acted_on(self):
        for state in ("READY", "INHIBITED", "FAULT", "SAFE_STOP"):
            self.assertEqual(self.zones(verdict(state))(), state)
        self.assertEqual(self.zones(verdict()).describe()["reason"], "signed verdict")

    def test_an_unsigned_forged_or_other_keyed_verdict_is_a_safe_stop(self):
        unsigned = verdict()
        del unsigned["sdkSafetyStateSignature"]
        self.assertEqual(self.zones(unsigned)(), "SAFE_STOP")
        self.assertIn("not signed", self.zones(unsigned).describe()["reason"])
        self.assertEqual(self.zones(verdict(key="x" * 40))(), "SAFE_STOP")
        forged = verdict("SAFE_STOP")
        forged["sdkSafetyState"]["state"] = "READY"
        self.assertEqual(self.zones(forged)(), "SAFE_STOP")
        self.assertEqual(self.zones(verdict(key_id="other"), key_id="default")(), "SAFE_STOP")
        self.assertEqual(self.zones(verdict(key_id="other"), key_id="other")(), "READY")

    def test_an_old_or_future_verdict_is_a_safe_stop(self):
        self.assertEqual(self.zones(verdict(at_ms=NOW_MS - 4000))(), "READY")
        self.assertEqual(self.zones(verdict(at_ms=NOW_MS - 6000))(), "SAFE_STOP")
        self.assertEqual(self.zones(verdict(at_ms=NOW_MS + 6000))(), "SAFE_STOP")

    def test_the_counter_never_goes_back_but_the_same_verdict_can_be_read_again(self):
        path = Path(self.write("state.json", json.dumps(verdict(counter=20))))
        source = CellStateSource(CellStateSourceConfig(source="safety_zones", path=str(path), key_file=str(self.key_file)), wall_clock_ms=lambda: NOW_MS)
        self.assertEqual(source(), "READY")
        self.assertEqual(source(), "READY")
        path.write_text(json.dumps(verdict("READY", counter=19)), encoding="utf-8")
        self.assertEqual(source(), "SAFE_STOP")
        self.assertIn("replay", source.describe()["reason"])
        path.write_text(json.dumps(verdict("FAULT", counter=21)), encoding="utf-8")
        self.assertEqual(source(), "FAULT")

    def test_a_message_that_is_not_the_contract_is_a_safe_stop(self):
        for text in ("not json", "[]", "{}", json.dumps(verdict(extra={"surprise": 1}))):
            self.assertEqual(self.zones(text)(), "SAFE_STOP", text)
        self.assertEqual(self.zones(verdict(), max_age_seconds=5)(), "READY")
        large = self.zones(" " * 70000)
        self.assertEqual(large(), "SAFE_STOP")
        self.assertIn("too large", large.describe()["reason"])

    def test_a_missing_file_is_a_safe_stop(self):
        config = CellStateSourceConfig(source="safety_zones", path=str(self.dir / "none.json"), key_file=str(self.key_file))
        self.assertEqual(CellStateSource(config)(), "SAFE_STOP")

    def test_the_verdict_can_come_from_an_http_address(self):
        calls: list[str] = []

        def fetch(url: str) -> bytes:
            calls.append(url)
            return json.dumps(verdict()).encode()

        config = CellStateSourceConfig(source="safety_zones", url="http://127.0.0.1:1/state", key_file=str(self.key_file))
        self.assertEqual(CellStateSource(config, wall_clock_ms=lambda: NOW_MS, fetch=fetch)(), "READY")
        self.assertEqual(calls, ["http://127.0.0.1:1/state"])

        def down(url: str) -> bytes:
            raise OSError("down")

        self.assertEqual(CellStateSource(config, wall_clock_ms=lambda: NOW_MS, fetch=down)(), "SAFE_STOP")

    def test_a_reader_that_fails_unexpectedly_still_answers_a_safe_stop(self):
        source = self.zones(verdict())
        with mock.patch.object(CellStateSource, "_read", side_effect=RuntimeError("boom")):
            self.assertEqual(source(), "SAFE_STOP")
        with mock.patch.object(CellStateSource, "_read", return_value=("GO", "x")):
            self.assertEqual(source(), "SAFE_STOP")

    def test_a_short_or_missing_key_is_refused_and_never_printed(self):
        short = self.dir / "short.txt"
        short.write_text("tiny", encoding="utf-8")
        for key_file in (str(short), str(self.dir / "absent.txt")):
            config = CellStateSourceConfig(source="safety_zones", path="p", key_file=key_file)
            with self.assertRaises(CellStateSourceError) as caught:
                CellStateSource(config)
            self.assertNotIn("tiny", str(caught.exception))


class TheEd25519Verdict(WithFiles):
    def test_only_the_public_key_is_needed_and_a_hmac_verdict_is_refused(self):
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import ed25519
        except ImportError:
            self.skipTest("the cryptography package is not installed")
        private = ed25519.Ed25519PrivateKey.generate()
        public_file = self.dir / "public.pem"
        public_file.write_bytes(private.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
        sdk_state = {"schema_version": "1.0", "state": "READY", "source": "safety-zones", "timestamp_utc": stamp(NOW_MS)}
        sig = private.sign(_message(sdk_state, 7, "default")).hex()
        payload = {"sdkSafetyState": sdk_state, "reason": None, "sdkSafetyStateSignature": {"alg": "Ed25519", "key_id": "default", "counter": 7, "sig": sig}}
        path = self.write("state.json", json.dumps(payload))
        config = CellStateSourceConfig(source="safety_zones", path=path, algorithm="Ed25519", public_key_file=str(public_file))
        self.assertEqual(CellStateSource(config, wall_clock_ms=lambda: NOW_MS)(), "READY")
        payload["sdkSafetyStateSignature"]["sig"] = "0" * 128
        self.write("state.json", json.dumps(payload))
        self.assertEqual(CellStateSource(config, wall_clock_ms=lambda: NOW_MS)(), "SAFE_STOP")
        self.write("state.json", json.dumps(verdict()))
        self.assertEqual(CellStateSource(config, wall_clock_ms=lambda: NOW_MS)(), "SAFE_STOP")
        with self.assertRaises(CellStateSourceError):
            CellStateSource(CellStateSourceConfig(source="safety_zones", path=path, algorithm="Ed25519", public_key_file=str(self.key_file)))


class TheEnvironment(unittest.TestCase):
    def test_nothing_set_means_the_bridge_keeps_its_own_behaviour(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(config_from_environment("CNC"))

    def test_the_settings_are_read_from_the_environment(self):
        env = {
            "HYDRA_UMC_UAV_CELL_STATE_SOURCE": "Safety_Zones",
            "HYDRA_UMC_UAV_CELL_STATE_URL": "https://zones.local/state",
            "HYDRA_UMC_UAV_CELL_STATE_KEY_FILE": "/keys/zones",
            "HYDRA_UMC_UAV_CELL_STATE_MAX_AGE": "3.5",
            "HYDRA_UMC_UAV_CELL_STATE_KEY_ID": "uav",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            config = config_from_environment("UAV")
        assert config is not None
        self.assertEqual((config.source, config.url, config.max_age_seconds, config.key_id), ("safety_zones", "https://zones.local/state", 3.5, "uav"))
        with mock.patch.dict(os.environ, {"HYDRA_UMC_UAV_CELL_STATE_SOURCE": "fixed", "HYDRA_UMC_UAV_CELL_STATE_MAX_AGE": "soon"}, clear=True):
            with self.assertRaises(CellStateSourceError):
                config_from_environment("UAV")
        with mock.patch.dict(os.environ, {"HYDRA_UMC_UAV_CELL_STATE_SOURCE": "fixed", "HYDRA_UMC_UAV_CELL_STATE_VALUE": "fault"}, clear=True):
            config = config_from_environment("UAV")
        assert config is not None
        self.assertEqual(config.value, "FAULT")


if __name__ == "__main__":
    unittest.main()
