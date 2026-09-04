// =============================================================================
// HYDRA-UMC-SDK - TypeScript reference client: anti-drift check for vendored schemas
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

import assert from "node:assert/strict";
import * as fs from "node:fs";
import * as path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const CANONICAL_DIR = path.resolve(here, "..", "..", "..", "contracts", "json-schema", "v1");
const VENDORED_DIR = path.resolve(here, "..", "schemas");

test("vendored schemas/*.json stays byte-identical to contracts/json-schema/v1", () => {
  if (!fs.existsSync(CANONICAL_DIR)) {
    // Not inside a HYDRA-UMC-SDK checkout (e.g. a standalone package
    // install) - Validate/validate() never depend on this directory, only
    // on schemas/, so skip rather than fail.
    return;
  }
  const canonicalFiles = fs.readdirSync(CANONICAL_DIR).filter((name) => name.endsWith(".json"));
  const vendoredFiles = fs.readdirSync(VENDORED_DIR).filter((name) => name.endsWith(".json"));

  assert.deepEqual(
    [...canonicalFiles].sort(),
    [...vendoredFiles].sort(),
    "clients/typescript/schemas/ must vendor exactly the files published under contracts/json-schema/v1/"
  );

  for (const name of canonicalFiles) {
    const canonical = fs.readFileSync(path.join(CANONICAL_DIR, name));
    const vendored = fs.readFileSync(path.join(VENDORED_DIR, name));
    assert.ok(canonical.equals(vendored), `clients/typescript/schemas/${name} has drifted from contracts/json-schema/v1/${name}`);
  }
});
