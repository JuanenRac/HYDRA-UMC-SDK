# =============================================================================
# HYDRA-UMC-SDK - Tests of the generated types and of the contract lint
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The generated TypeScript, Kotlin and Dart types follow the schemas, and the topic registry only names real contracts."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[3]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SDK / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TYPES = _load("generate_types")
CHECK = _load("contract_check")


class GeneratedTypesTests(unittest.TestCase):
    def test_committed_files_are_current(self) -> None:
        for name, text in TYPES.outputs().items():
            committed = (SDK / "generated" / name).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(committed, text.encode("utf-8"), f"generated/{name} is out of date")

    def test_every_schema_with_properties_has_a_type_in_each_language(self) -> None:
        titles = [TYPES.pascal(path.name.split(".")[0]) for path in sorted(TYPES.SCHEMAS.glob("*.schema.json"))
                  if json.loads(path.read_text(encoding="utf-8")).get("properties")]
        self.assertGreaterEqual(len(titles), 20)
        outputs = TYPES.outputs()
        for title in titles:
            self.assertIn(f"interface {title} ", outputs["hydra-contracts.ts"], title)
            self.assertIn(f"data class {title}(", outputs["HydraContracts.kt"], title)
            self.assertIn(f"class {title} {{", outputs["hydra_contracts.dart"], title)

    def test_required_and_optional_fields_and_literals(self) -> None:
        ts = TYPES.outputs()["hydra-contracts.ts"]
        self.assertIn('schema_version: "1.0";', ts)
        self.assertIn('state: "READY" | "DEGRADED" | "INHIBITED" | "FAULT" | "SAFE_STOP";', ts)
        self.assertIn("status_reason?: string;", ts)

    def test_a_reserved_word_gets_a_safe_name(self) -> None:
        self.assertEqual(TYPES.kt_name("interface"), "`interface`")
        self.assertEqual(TYPES.dart_name("default"), "default_")
        self.assertEqual(TYPES.dart_name("a-b"), "a_b")

    def test_check_fails_when_a_file_is_out_of_date(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            original = TYPES.OUT
            TYPES.OUT = Path(folder)
            try:
                self.assertEqual(TYPES.main(["--check"]), 1)
                self.assertEqual(TYPES.main([]), 0)
                self.assertEqual(TYPES.main(["--check"]), 0)
                (Path(folder) / "hydra-contracts.ts").write_text("edited", encoding="utf-8")
                self.assertEqual(TYPES.main(["--check"]), 1)
            finally:
                TYPES.OUT = original


class TopicRegistryTests(unittest.TestCase):
    def test_the_registry_of_this_sdk_is_valid(self) -> None:
        self.assertEqual(CHECK.topics_problems(SDK), [])

    def test_the_table_lists_every_topic_with_its_prefix(self) -> None:
        table = CHECK.topics_table(SDK)
        self.assertIn("hydra/bridges/<name>/health", table)
        self.assertIn("hydra/swarm/safety/estop", table)
        self.assertNotIn("hydra/bridges/<name>/hydra/swarm", table)

    def test_a_contract_that_does_not_exist_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "contracts" / "json-schema" / "v1").mkdir(parents=True)
            (root / "contracts" / "topics.json").write_text(json.dumps({"topics": [
                {"topic": "x", "direction": "sideways", "retained": True, "qos": 1, "contract": "nothing.schema.json"},
                {"topic": "x", "direction": "in", "retained": "yes", "qos": 5},
            ]}), encoding="utf-8")
            problems = CHECK.topics_problems(root)
        joined = "\n".join(problems)
        self.assertIn("direction must be in or out", joined)
        self.assertIn("nothing.schema.json", joined)
        self.assertIn("repeated topic", joined)
        self.assertIn("qos 0-2", joined)

    def test_a_missing_registry_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(CHECK.topics_problems(Path(folder)), ["contracts/topics.json is missing"])


if __name__ == "__main__":
    unittest.main()
