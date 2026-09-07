// =============================================================================
// HYDRA-UMC-SDK - TypeScript reference client: contract manifest integrity check
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

import * as crypto from "node:crypto";
import * as fs from "node:fs";
import * as path from "node:path";

import type { ContractManifest } from "./types";

const SCHEMA_DIR = path.join(__dirname, "..", "schemas");

/**
 * The real, canonical contracts/json-schema/v1/manifest.json (unlike the
 * *.schema.json files it lists) is saved with a leading UTF-8 byte order
 * mark (U+FEFF). Node's JSON.parse does not skip it, so it is stripped
 * explicitly here rather than "fixed" by re-encoding the normative file
 * this package only vendors a copy of.
 */
function stripBom(text: string): string {
  return text.charCodeAt(0) === 0xfeff ? text.slice(1) : text;
}

/** Decodes this package's vendored schemas/manifest.json. */
export function loadContractManifest(): ContractManifest {
  const raw = fs.readFileSync(path.join(SCHEMA_DIR, "manifest.json"), "utf-8");
  return JSON.parse(stripBom(raw)) as ContractManifest;
}

/**
 * Recomputes the sha256 digest of every schema file this package vendors
 * and compares it against manifest.json's own claim for that file.
 * Returns the (empty, on success) list of file names whose vendored bytes
 * do not match the digest manifest.json declares for them - a real
 * integrity check, not just a structural one.
 */
export function verifyContractManifest(): string[] {
  const manifest = loadContractManifest();
  const mismatches: string[] = [];
  for (const entry of manifest.contracts) {
    const filePath = path.join(SCHEMA_DIR, entry.file);
    let bytes: Buffer;
    try {
      bytes = fs.readFileSync(filePath);
    } catch {
      mismatches.push(`${entry.file}: manifest.json names it but it is not vendored under schemas/`);
      continue;
    }
    const actual = crypto.createHash("sha256").update(bytes).digest("hex");
    if (actual !== entry.sha256) {
      mismatches.push(`${entry.file}: manifest.json sha256 ${entry.sha256} does not match vendored file's actual sha256 ${actual}`);
    }
  }
  return mismatches;
}
