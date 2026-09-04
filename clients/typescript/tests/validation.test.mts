// =============================================================================
// HYDRA-UMC-SDK - TypeScript reference client tests: real schema validation
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

import assert from "node:assert/strict";
import * as fs from "node:fs";
import * as path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { ContractValidationError, type ContractName, isValid, knownContracts, validate, verifyContractManifest } from "../dist/index.js";

// This test file is .mts (real ESM) purely so it can use `import` while the
// package itself stays "type": "commonjs" for its published dist/ output -
// import.meta.url replaces CommonJS's __dirname here.
const here = path.dirname(fileURLToPath(import.meta.url));

// Two directories up from clients/typescript is the repository root - the
// same layout clients/python/tests/test_validation.py relies on for the
// exact same fixtures.
const FIXTURES = path.resolve(here, "..", "..", "..", "conformance", "fixtures", "v1");

const CONTRACT_FIXTURE_STEM: Record<ContractName, string> = {
  DeviceDescriptor: "device-descriptor",
  EventEnvelope: "event-envelope",
  HealthReport: "health-report",
  ProjectManifest: "project-manifest",
  SafetyState: "safety-state",
  ServerDiscovery: "server-discovery",
  UpdateManifest: "update-manifest",
};

function readFixture(name: string): unknown {
  return JSON.parse(fs.readFileSync(path.join(FIXTURES, name), "utf-8"));
}

test("knownContracts lists all 7 real contracts", () => {
  assert.deepEqual(knownContracts(), [
    "DeviceDescriptor",
    "EventEnvelope",
    "HealthReport",
    "ProjectManifest",
    "SafetyState",
    "ServerDiscovery",
    "UpdateManifest",
  ]);
});

for (const [contract, stem] of Object.entries(CONTRACT_FIXTURE_STEM) as [ContractName, string][]) {
  test(`accepts the real ${contract} valid fixture`, () => {
    const payload = readFixture(`${stem}.valid.json`);
    assert.doesNotThrow(() => validate(contract, payload));
    assert.equal(isValid(contract, payload), true);
  });

  test(`rejects the real ${contract} invalid fixture`, () => {
    const payload = readFixture(`${stem}.invalid.json`);
    assert.throws(() => validate(contract, payload), ContractValidationError);
    assert.equal(isValid(contract, payload), false);
  });
}

test("rejects an unknown contract name", () => {
  assert.throws(() => validate("NotARealContract" as ContractName, {}), ContractValidationError);
});

test("rejects a boolean where EventEnvelope.sequence requires an integer", () => {
  // bool is not a JSON Schema "integer" - mirrors
  // clients/python/tests/test_validation.py's
  // test_rejects_boolean_event_sequence and clients/go's
  // TestValidateRejectsBooleanForIntegerSequence.
  const payload = {
    schema_version: "1.0",
    event_id: "e",
    type: "x",
    source: "os",
    timestamp_utc: "2026-08-26T12:00:00Z",
    sequence: true,
  };
  assert.throws(() => validate("EventEnvelope", payload), ContractValidationError);
});

test("rejects an invalid RFC 3339 date-time via ajv-formats", () => {
  const payload = {
    schema_version: "1.0",
    state: "READY",
    timestamp_utc: "2026-02-30T12:00:00Z", // no such calendar day
    checks: {},
  };
  assert.throws(() => validate("HealthReport", payload), ContractValidationError);
});

test("accepts a minimal schema-valid HealthReport", () => {
  const payload = {
    schema_version: "1.0",
    state: "READY",
    timestamp_utc: "2026-01-01T00:00:00Z",
    checks: { storage: { state: "PASS" } },
  };
  assert.doesNotThrow(() => validate("HealthReport", payload));
});

test("rejects an unknown property on ProjectManifest (additionalProperties: false)", () => {
  const payload = readFixture("project-manifest.valid.json") as Record<string, unknown>;
  const withExtra = { ...payload, unexpected_field: "nope" };
  assert.throws(() => validate("ProjectManifest", withExtra), ContractValidationError);
});

test("verifyContractManifest finds no mismatches", () => {
  assert.deepEqual(verifyContractManifest(), []);
});
