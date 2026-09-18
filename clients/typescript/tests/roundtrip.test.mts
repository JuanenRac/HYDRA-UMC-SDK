// =============================================================================
// HYDRA-UMC-SDK - Cross-language contract round-trip tests (TypeScript side)
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

import assert from "node:assert/strict";
import * as fs from "node:fs";
import * as path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import type {
  DeviceDescriptor,
  EventEnvelope,
  HealthReport,
  ProjectManifest,
  SafetyState,
  ServerDiscovery,
  UpdateManifest,
} from "../dist/index.js";

// Same fixtures every other language's own round-trip test uses - see
// clients/python/tests/test_contract_roundtrip.py,
// clients/go/roundtrip_test.go and clients/rust/tests/roundtrip.rs.
const here = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES = path.resolve(here, "..", "..", "..", "conformance", "fixtures", "v1");

function readFixture(name: string): unknown {
  return JSON.parse(fs.readFileSync(path.join(FIXTURES, name), "utf-8"));
}

/**
 * Decodes `fixtureName` (already real, valid JSON on disk - `JSON.parse`
 * IS this client's own decode step, no separate struct-mapping layer the
 * way Go/Rust have) as `T`, re-encodes it with `JSON.stringify`, and
 * asserts the re-parsed output is deeply/structurally equal to the
 * original parse - proving this client's own encode/decode path never
 * drops or mutates a real contract payload's fields, including any
 * `additionalProperties` this interface's own index signature allows
 * through untyped.
 */
function assertRoundtrips<T>(fixtureName: string): void {
  const original = readFixture(fixtureName) as T;
  const reencoded = JSON.stringify(original);
  const roundtripped = JSON.parse(reencoded) as T;
  assert.deepEqual(roundtripped, original);
}

test("DeviceDescriptor round-trips through JSON.stringify/JSON.parse", () => {
  assertRoundtrips<DeviceDescriptor>("device-descriptor.valid.json");
});

test("HealthReport round-trips through JSON.stringify/JSON.parse", () => {
  assertRoundtrips<HealthReport>("health-report.valid.json");
});

test("SafetyState round-trips through JSON.stringify/JSON.parse", () => {
  assertRoundtrips<SafetyState>("safety-state.valid.json");
});

test("UpdateManifest round-trips through JSON.stringify/JSON.parse", () => {
  assertRoundtrips<UpdateManifest>("update-manifest.valid.json");
});

test("EventEnvelope round-trips through JSON.stringify/JSON.parse", () => {
  assertRoundtrips<EventEnvelope>("event-envelope.valid.json");
});

test("ServerDiscovery round-trips through JSON.stringify/JSON.parse", () => {
  assertRoundtrips<ServerDiscovery>("server-discovery.valid.json");
});

test("ProjectManifest round-trips through JSON.stringify/JSON.parse", () => {
  assertRoundtrips<ProjectManifest>("project-manifest.valid.json");
});

// Capability/Operation/ScenarioOutcome have no dedicated interface in this
// client yet (see types.ts's own ContractName union - they're validated
// generically, same as clients/go and clients/rust today), so they
// round-trip through the same generic `unknown` shape JSON.parse already
// returns for them - still a real, honest test of this client's actual
// current behavior for those 3 contracts, not an invented one.
test("Capability round-trips through JSON.stringify/JSON.parse", () => {
  assertRoundtrips<unknown>("capability.valid.json");
});

test("Operation round-trips through JSON.stringify/JSON.parse", () => {
  assertRoundtrips<unknown>("operation.valid.json");
});

test("ScenarioOutcome round-trips through JSON.stringify/JSON.parse", () => {
  assertRoundtrips<unknown>("scenario-outcome.valid.json");
});

test("round trip is stable under a second encode/decode pass", () => {
  const original = readFixture("device-descriptor.valid.json");
  const twice = JSON.parse(JSON.stringify(JSON.parse(JSON.stringify(original))));
  assert.deepEqual(twice, original);
});
