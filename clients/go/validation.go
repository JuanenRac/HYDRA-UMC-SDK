// =============================================================================
// HYDRA-UMC-SDK - Go reference client: real JSON Schema runtime validation
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

package hydraumc

import (
	"bytes"
	"crypto/sha256"
	"embed"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"sort"

	"github.com/santhosh-tekuri/jsonschema/v5"
)

// schemas embeds this client's own vendored copy of the published v1 JSON
// Schema files (schemas/*.json), so a built binary needs no access to the
// monorepo's contracts/ directory at runtime. TestVendoredSchemasMatchCanonical
// (schema_drift_test.go) proves these copies stay byte-identical to
// contracts/json-schema/v1/, the normative source.
//
//go:embed schemas/*.json
var schemas embed.FS

// contractFiles maps each contract name this client validates to its
// vendored schema file - the same 7 names the Python reference validator's
// REQUIRED table documents in docs/PYTHON_CLIENT.md.
var contractFiles = map[string]string{
	"DeviceDescriptor": "device-descriptor.schema.json",
	"EventEnvelope":    "event-envelope.schema.json",
	"HealthReport":     "health-report.schema.json",
	"ProjectManifest":  "project-manifest.schema.json",
	"SafetyState":      "safety-state.schema.json",
	"ServerDiscovery":  "server-discovery.schema.json",
	"UpdateManifest":   "update-manifest.schema.json",
}

// ContractValidationError is returned by Validate when payload fails real
// JSON Schema validation, or when contract is not one of contractFiles.
type ContractValidationError struct {
	Contract string
	Err      error
}

func (e *ContractValidationError) Error() string {
	return fmt.Sprintf("%s: %s", e.Contract, e.Err)
}

func (e *ContractValidationError) Unwrap() error { return e.Err }

var compiledSchemas = map[string]*jsonschema.Schema{}

func compiledSchema(contract string) (*jsonschema.Schema, error) {
	if schema, ok := compiledSchemas[contract]; ok {
		return schema, nil
	}
	file, ok := contractFiles[contract]
	if !ok {
		return nil, fmt.Errorf("unknown contract: %s", contract)
	}
	raw, err := schemas.ReadFile("schemas/" + file)
	if err != nil {
		return nil, fmt.Errorf("embedded schema missing for %s: %w", contract, err)
	}
	compiler := jsonschema.NewCompiler()
	compiler.AssertFormat = true // real format checks (e.g. date-time), not just parsed-and-ignored
	url := "mem://" + file
	if err := compiler.AddResource(url, bytes.NewReader(raw)); err != nil {
		return nil, fmt.Errorf("cannot load schema for %s: %w", contract, err)
	}
	schema, err := compiler.Compile(url)
	if err != nil {
		return nil, fmt.Errorf("cannot compile schema for %s: %w", contract, err)
	}
	compiledSchemas[contract] = schema
	return schema, nil
}

// Validate checks payload (already-decoded JSON, e.g. from
// json.Unmarshal(data, &map[string]interface{}{}) or any struct) against
// the real, published v1 JSON Schema for contract. It returns nil on a
// valid payload and a *ContractValidationError on the first schema
// violation reported by the underlying validator, or on an unknown
// contract name. The JSON Schema files under contracts/json-schema/v1/
// remain the normative source; this function enforces them directly
// (compiled from this client's vendored copy), not a hand-reimplemented
// subset.
func Validate(contract string, payload interface{}) error {
	schema, err := compiledSchema(contract)
	if err != nil {
		return &ContractValidationError{Contract: contract, Err: err}
	}
	if err := schema.Validate(payload); err != nil {
		return &ContractValidationError{Contract: contract, Err: err}
	}
	return nil
}

// ValidateJSON is Validate for a raw JSON document, decoding it first with
// json.Number preserved (so integer fields like EventEnvelope.sequence are
// never silently treated as JSON booleans or floats during validation).
func ValidateJSON(contract string, data []byte) error {
	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.UseNumber()
	var payload interface{}
	if err := decoder.Decode(&payload); err != nil {
		return &ContractValidationError{Contract: contract, Err: fmt.Errorf("invalid JSON: %w", err)}
	}
	return Validate(contract, payload)
}

// KnownContracts returns the sorted contract names Validate accepts.
func KnownContracts() []string {
	names := make([]string, 0, len(contractFiles))
	for name := range contractFiles {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}

// utf8BOM is the 3-byte UTF-8 byte order mark. The real, canonical
// contracts/json-schema/v1/manifest.json (unlike the *.schema.json files)
// is saved with a leading BOM; encoding/json does not skip it, so it is
// stripped explicitly here rather than "fixed" by editing the normative
// file this client only vendors a copy of.
var utf8BOM = []byte{0xEF, 0xBB, 0xBF}

// LoadContractManifest decodes this client's vendored manifest.json - the
// generated integrity manifest listing every published v1 schema file and
// its sha256 digest.
func LoadContractManifest() (*ContractManifest, error) {
	raw, err := schemas.ReadFile("schemas/manifest.json")
	if err != nil {
		return nil, fmt.Errorf("embedded manifest.json missing: %w", err)
	}
	raw = bytes.TrimPrefix(raw, utf8BOM)
	var manifest ContractManifest
	if err := json.Unmarshal(raw, &manifest); err != nil {
		return nil, fmt.Errorf("cannot decode manifest.json: %w", err)
	}
	return &manifest, nil
}

// VerifyContractManifest recomputes the sha256 digest of every schema file
// this client embeds and compares it against manifest.json's own claim for
// that file, returning an error naming the first file whose vendored bytes
// do not match the digest manifest.json declares for it (a real integrity
// check, not just a structural one).
func VerifyContractManifest() error {
	manifest, err := LoadContractManifest()
	if err != nil {
		return err
	}
	for _, entry := range manifest.Contracts {
		raw, err := schemas.ReadFile("schemas/" + entry.File)
		if err != nil {
			return fmt.Errorf("manifest.json names %s but it is not embedded: %w", entry.File, err)
		}
		sum := sha256.Sum256(raw)
		actual := hex.EncodeToString(sum[:])
		if actual != entry.SHA256 {
			return fmt.Errorf("%s: manifest.json sha256 %s does not match embedded file's actual sha256 %s", entry.File, entry.SHA256, actual)
		}
	}
	return nil
}
