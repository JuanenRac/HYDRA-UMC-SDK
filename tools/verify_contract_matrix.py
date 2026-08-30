#!/usr/bin/env python3
# =============================================================================
# HYDRA-UMC-SDK - Automatic contract/validator compatibility matrix
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Real, automatic compatibility matrix between the published v1 JSON
Schema contracts and this SDK's own Python reference validator.

The Python validator (`clients/python/src/hydra_umc_sdk/validation.py`)
hand-implements the required-v1 subset of each real schema rather than
interpreting the schema files directly - real, but a real drift risk:
this script is the automatic check that a published schema file was
never added (or renamed) without a matching validator entry, and that
every real conformance fixture is judged the way its own filename
claims it should be. It found and this session fixed one real,
concrete instance of that drift: `project-manifest.schema.json` (the
real `hydra-umc.project.json` contract every repository in this
ecosystem publishes) had no `ProjectManifest` entry in the validator at
all - it could never actually be validated.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "contracts" / "json-schema" / "v1"
FIXTURES_DIR = ROOT / "conformance" / "fixtures" / "v1"
CLIENT_SRC = ROOT / "clients" / "python" / "src"
sys.path.insert(0, str(CLIENT_SRC))

from hydra_umc_sdk.validation import REQUIRED, ContractValidationError, validate  # noqa: E402


def fail(message: str) -> None:
    print(f"CONTRACT_MATRIX=FAIL {message}", file=sys.stderr)
    raise SystemExit(1)


def schema_file_to_contract_name(schema_path: Path) -> str:
    """Real, deterministic kebab-case -> PascalCase mapping - the same
    convention every real schema file in this repository already uses
    (device-descriptor.schema.json -> DeviceDescriptor, and so on)."""
    stem = schema_path.name.removesuffix(".schema.json")
    return "".join(part.capitalize() for part in stem.split("-"))


def discover_schema_contracts() -> dict[str, Path]:
    schema_files = sorted(SCHEMA_DIR.glob("*.schema.json"))
    if not schema_files:
        fail(f"no *.schema.json files found under {SCHEMA_DIR}")
    return {schema_file_to_contract_name(path): path for path in schema_files}


def check_matrix_coverage(schema_contracts: dict[str, Path]) -> None:
    """Every real published schema must have a validator entry, and
    every validator entry must correspond to a real published schema -
    drift in either direction is a real, reportable failure."""
    schema_names = set(schema_contracts)
    validator_names = set(REQUIRED)

    missing_in_validator = sorted(schema_names - validator_names)
    if missing_in_validator:
        fail(
            "published schema(s) with no validator entry (real drift): "
            + ", ".join(missing_in_validator)
        )

    stale_in_validator = sorted(validator_names - schema_names)
    if stale_in_validator:
        fail(
            "validator entry/entries with no published schema file (real drift): "
            + ", ".join(stale_in_validator)
        )

    print(f"CONTRACT_MATRIX_COVERAGE=PASS contracts={len(schema_names)}")


def check_fixture_matrix() -> int:
    """Every real conformance fixture is judged the way its own
    filename claims - `<contract>.valid.json` must validate cleanly,
    `<contract>.invalid.json` must be rejected. Contract name is derived
    from the fixture's own filename via the same kebab-case ->
    PascalCase mapping used for schema files, so a fixture for a
    contract that doesn't exist is itself a real, caught failure."""
    fixture_files = sorted(FIXTURES_DIR.glob("*.json"))
    checked = 0
    for fixture_path in fixture_files:
        name = fixture_path.stem
        if name.endswith(".valid"):
            contract = schema_file_to_contract_name(Path(name[: -len(".valid")] + ".schema.json"))
            expect_valid = True
        elif name.endswith(".invalid"):
            contract = schema_file_to_contract_name(Path(name[: -len(".invalid")] + ".schema.json"))
            expect_valid = False
        else:
            continue  # not a top-level valid/invalid fixture (e.g. producers/ subtree - covered by unit tests)

        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        try:
            validate(contract, payload)
            passed = True
        except ContractValidationError:
            passed = False

        if passed != expect_valid:
            fail(
                f"{fixture_path.relative_to(ROOT)}: expected "
                f"{'PASS' if expect_valid else 'REJECT'} for contract {contract}, got "
                f"{'PASS' if passed else 'REJECT'}"
            )
        print(f"CONTRACT_MATRIX_FIXTURE=PASS {fixture_path.name} contract={contract} expected={'valid' if expect_valid else 'invalid'}")
        checked += 1
    return checked


def check_unknown_and_incompatible_cases(schema_contracts: dict[str, Path]) -> None:
    """Real, explicit proof of the two negative cases this matrix is
    specifically meant to guard: a contract name that was never
    published at all, and a real payload declaring a schema_version
    this validator does not (yet) support."""
    try:
        validate("NotARealPublishedContract", {})
    except ContractValidationError:
        pass
    else:
        fail("an unknown contract name must be rejected, not silently accepted")
    print("CONTRACT_MATRIX_UNKNOWN_SCHEMA=PASS")

    any_contract = next(iter(schema_contracts))
    incompatible_payload = {field: "x" for field in REQUIRED[any_contract]}
    incompatible_payload["schema_version"] = "2.0"
    try:
        validate(any_contract, incompatible_payload)
    except ContractValidationError:
        pass
    else:
        fail("an incompatible schema_version must be rejected, not silently accepted")
    print("CONTRACT_MATRIX_INCOMPATIBLE_VERSION=PASS")

    malformed_update = {
        "schema_version": "1.0",
        "project": "HYDRA-UMC-EXAMPLE",
        "version": "latest",
        "artifact_url": "https://example.invalid/example.tar.gz",
        "sha256": "0" * 64,
    }
    try:
        validate("UpdateManifest", malformed_update)
    except ContractValidationError:
        pass
    else:
        fail("an update manifest with a non-semver version must be rejected")
    print("CONTRACT_MATRIX_UPDATE_VERSION=PASS")


def main() -> int:
    schema_contracts = discover_schema_contracts()
    check_matrix_coverage(schema_contracts)
    checked = check_fixture_matrix()
    check_unknown_and_incompatible_cases(schema_contracts)
    print(f"CONTRACT_MATRIX=PASS contracts={len(schema_contracts)} fixtures={checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
