// =============================================================================
// HYDRA-UMC-SDK - TypeScript reference client: real JSON Schema runtime validation
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

import * as fs from "node:fs";
import * as path from "node:path";
import Ajv2020, { type ErrorObject, type ValidateFunction } from "ajv/dist/2020";
import addFormats from "ajv-formats";

import type { ContractName } from "./types";

/**
 * Raised by `validate()` on the first schema violation Ajv reports, or on
 * an unknown contract name. A `ValueError`-shaped subclass, matching the
 * Python reference client's own `ContractValidationError`
 * (`clients/python/src/hydra_umc_sdk/validation.py`).
 */
export class ContractValidationError extends Error {
  readonly contract: string;
  readonly errors: ErrorObject[] | null | undefined;

  constructor(contract: string, message: string, errors?: ErrorObject[] | null) {
    super(`${contract}: ${message}`);
    this.name = "ContractValidationError";
    this.contract = contract;
    this.errors = errors;
  }
}

/**
 * Vendored schema file for each of the 7 real payload contracts this
 * client validates - the same 7 names documented in
 * docs/PYTHON_CLIENT.md's REQUIRED table for the Python reference client.
 */
const CONTRACT_FILES: Record<ContractName, string> = {
  DeviceDescriptor: "device-descriptor.schema.json",
  HealthReport: "health-report.schema.json",
  SafetyState: "safety-state.schema.json",
  UpdateManifest: "update-manifest.schema.json",
  EventEnvelope: "event-envelope.schema.json",
  ServerDiscovery: "server-discovery.schema.json",
  ProjectManifest: "project-manifest.schema.json",
};

/**
 * This package's own vendored schema copies (schemas/*.json, shipped
 * alongside dist/ via package.json's "files"). __dirname resolves relative
 * to the *compiled* file, so this stays correct whether run from src/
 * (ts-node/native TS) or dist/ (tsc output) - both sit directly under
 * clients/typescript/, one level above schemas/.
 */
const SCHEMA_DIR = path.join(__dirname, "..", "schemas");

const ajv = new Ajv2020({ allErrors: true, strict: true });
addFormats(ajv);

const compiled = new Map<ContractName, ValidateFunction>();

function compiledValidator(contract: ContractName): ValidateFunction {
  const cached = compiled.get(contract);
  if (cached) {
    return cached;
  }
  const file = CONTRACT_FILES[contract];
  if (!file) {
    throw new ContractValidationError(contract, "unknown contract");
  }
  const schemaPath = path.join(SCHEMA_DIR, file);
  let schema: unknown;
  try {
    schema = JSON.parse(fs.readFileSync(schemaPath, "utf-8"));
  } catch (error) {
    throw new ContractValidationError(contract, `cannot load schema ${schemaPath}: ${(error as Error).message}`);
  }
  const validator = ajv.compile(schema as Record<string, unknown>);
  compiled.set(contract, validator);
  return validator;
}

/**
 * Validate `payload` against the real, published v1 JSON Schema for
 * `contract`. Throws `ContractValidationError` on the first violation Ajv
 * reports (all errors are still collected on `.errors`); returns nothing
 * on a valid payload. This enforces the full schema (via Ajv, a real
 * draft 2020-12 JSON Schema validator with `ajv-formats` enabled for
 * `format: "date-time"`), not a hand-reimplemented subset.
 */
export function validate(contract: ContractName, payload: unknown): void {
  const validator = compiledValidator(contract);
  const ok = validator(payload);
  if (!ok) {
    const message = ajv.errorsText(validator.errors, { separator: "; " });
    throw new ContractValidationError(contract, message, validator.errors);
  }
}

/** `validate()` as a boolean predicate instead of a throw/no-throw call. */
export function isValid(contract: ContractName, payload: unknown): boolean {
  try {
    validate(contract, payload);
    return true;
  } catch {
    return false;
  }
}

/** The contract names `validate()`/`isValid()` accept, sorted. */
export function knownContracts(): ContractName[] {
  return (Object.keys(CONTRACT_FILES) as ContractName[]).sort();
}
