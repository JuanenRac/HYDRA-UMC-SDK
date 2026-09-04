// =============================================================================
// HYDRA-UMC-SDK - Go reference client tests: real schema validation
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

package hydraumc

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

// fixturesDir locates conformance/fixtures/v1 relative to this monorepo
// checkout. This client is developed and tested inside the HYDRA-UMC-SDK
// repository (see clients/python's own tests for the same pattern against
// the same fixtures) - a copy of this package built or vendored outside
// the monorepo would not have these fixtures on disk, which is why
// Validate/ValidateJSON themselves depend only on the embedded schemas/,
// never on this directory.
func fixturesDir(t *testing.T) string {
	t.Helper()
	dir, err := filepath.Abs(filepath.Join("..", "..", "conformance", "fixtures", "v1"))
	if err != nil {
		t.Fatalf("cannot resolve conformance fixtures directory: %v", err)
	}
	if info, err := os.Stat(dir); err != nil || !info.IsDir() {
		t.Skipf("conformance fixtures not found at %s (expected inside a HYDRA-UMC-SDK checkout)", dir)
	}
	return dir
}

func readFixture(t *testing.T, dir, name string) []byte {
	t.Helper()
	data, err := os.ReadFile(filepath.Join(dir, name))
	if err != nil {
		t.Fatalf("cannot read fixture %s: %v", name, err)
	}
	return data
}

// contractFixtureFile is the same fixture-naming convention
// tools/verify_contract_matrix.py enforces: <kebab-case-contract>.valid.json
// / .invalid.json.
var contractFixtureFile = map[string]string{
	"DeviceDescriptor": "device-descriptor",
	"EventEnvelope":    "event-envelope",
	"HealthReport":     "health-report",
	"ProjectManifest":  "project-manifest",
	"SafetyState":      "safety-state",
	"ServerDiscovery":  "server-discovery",
	"UpdateManifest":   "update-manifest",
}

func TestAcceptsEveryValidFixture(t *testing.T) {
	dir := fixturesDir(t)
	for contract, stem := range contractFixtureFile {
		contract, stem := contract, stem
		t.Run(contract, func(t *testing.T) {
			data := readFixture(t, dir, stem+".valid.json")
			if err := ValidateJSON(contract, data); err != nil {
				t.Errorf("expected %s valid fixture to pass, got: %v", contract, err)
			}
		})
	}
}

func TestRejectsEveryInvalidFixture(t *testing.T) {
	dir := fixturesDir(t)
	for contract, stem := range contractFixtureFile {
		contract, stem := contract, stem
		t.Run(contract, func(t *testing.T) {
			data := readFixture(t, dir, stem+".invalid.json")
			if err := ValidateJSON(contract, data); err == nil {
				t.Errorf("expected %s invalid fixture to be rejected, got nil error", contract)
			}
		})
	}
}

func TestUnknownContractIsRejected(t *testing.T) {
	err := Validate("NotARealContract", map[string]interface{}{})
	if err == nil {
		t.Fatal("expected an error for an unknown contract name")
	}
	if _, ok := err.(*ContractValidationError); !ok {
		t.Fatalf("expected a *ContractValidationError, got %T: %v", err, err)
	}
}

func TestKnownContractsListsAllSeven(t *testing.T) {
	names := KnownContracts()
	if len(names) != 7 {
		t.Fatalf("expected 7 known contracts, got %d: %v", len(names), names)
	}
}

func TestValidateRejectsBooleanForIntegerSequence(t *testing.T) {
	// bool must never satisfy an "integer" schema - mirrors
	// clients/python/tests/test_validation.py's
	// test_rejects_boolean_event_sequence, ported to Go's own JSON decoding.
	payload := map[string]interface{}{
		"schema_version": "1.0",
		"event_id":       "e",
		"type":           "x",
		"source":         "os",
		"timestamp_utc":  "2026-08-26T12:00:00Z",
		"sequence":       true,
	}
	if err := Validate("EventEnvelope", payload); err == nil {
		t.Fatal("expected a boolean sequence to be rejected")
	}
}

func TestValidateRejectsInvalidDateTime(t *testing.T) {
	payload := map[string]interface{}{
		"schema_version": "1.0",
		"state":          "READY",
		"timestamp_utc":  "2026-02-30T12:00:00Z", // no such calendar day
		"checks":         map[string]interface{}{},
	}
	if err := Validate("HealthReport", payload); err == nil {
		t.Fatal("expected an invalid RFC 3339 date-time to be rejected")
	}
}

func TestValidateAcceptsAMinimalHealthReport(t *testing.T) {
	payload := map[string]interface{}{
		"schema_version": "1.0",
		"state":          "READY",
		"timestamp_utc":  "2026-01-01T00:00:00Z",
		"checks":         map[string]interface{}{"storage": map[string]interface{}{"state": "PASS"}},
	}
	if err := Validate("HealthReport", payload); err != nil {
		t.Fatalf("expected a schema-valid HealthReport to pass, got: %v", err)
	}
}

func TestVerifyContractManifestPasses(t *testing.T) {
	if err := VerifyContractManifest(); err != nil {
		t.Fatalf("expected every embedded schema to match manifest.json's own sha256 digest, got: %v", err)
	}
}

func TestNativeVersionPatternRoundTripsStringForm(t *testing.T) {
	manifest := ProjectManifest{NativeVersion: NativeVersion{
		File:    "CHANGELOG.md",
		Pattern: NativeVersionPattern{Pattern: `(\d+)\.(\d+)\.(\d+)`},
	}}
	encoded, err := json.Marshal(manifest)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	var decoded ProjectManifest
	if err := json.Unmarshal(encoded, &decoded); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if decoded.NativeVersion.Pattern.Pattern != manifest.NativeVersion.Pattern.Pattern {
		t.Fatalf("string pattern did not round-trip: got %q", decoded.NativeVersion.Pattern.Pattern)
	}
	if decoded.NativeVersion.Pattern.Components != nil {
		t.Fatalf("string pattern must not decode Components")
	}
}

func TestNativeVersionPatternRoundTripsComponentForm(t *testing.T) {
	manifest := ProjectManifest{NativeVersion: NativeVersion{
		File: "version.go",
		Pattern: NativeVersionPattern{Components: &NativeVersionPatternComponents{
			Major: "MAJOR", Minor: "MINOR", Patch: "PATCH",
		}},
	}}
	encoded, err := json.Marshal(manifest)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}
	var decoded ProjectManifest
	if err := json.Unmarshal(encoded, &decoded); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if decoded.NativeVersion.Pattern.Components == nil || *decoded.NativeVersion.Pattern.Components != *manifest.NativeVersion.Pattern.Components {
		t.Fatalf("component pattern did not round-trip: got %+v", decoded.NativeVersion.Pattern.Components)
	}
}
