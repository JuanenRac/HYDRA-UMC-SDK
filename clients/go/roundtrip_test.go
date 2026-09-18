// =============================================================================
// HYDRA-UMC-SDK - Cross-language contract round-trip tests (Go side)
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

package hydraumc

import (
	"encoding/json"
	"reflect"
	"testing"
)

// roundtripFixture is the same 10-contract set every other language's own
// round-trip test uses (see clients/python/tests/test_contract_roundtrip.py
// and clients/rust/tests/roundtrip.rs), each paired with a `new() any`
// factory for the concrete Go type this client actually decodes that
// contract into today. 7 of the 10 real v1 contracts already have a
// hand-written struct in types.go; the 3 newer ones (Capability,
// Operation, ScenarioOutcome) are validated generically (see
// validation.go) and have no dedicated struct yet, so they round-trip
// through the same generic map[string]interface{} representation
// Validate() itself uses - still a real, honest round trip of THIS
// client's actual current representation, not an invented one.
var roundtripFixtures = map[string]struct {
	file    string
	newType func() any
}{
	"DeviceDescriptor": {"device-descriptor.valid.json", func() any { return &DeviceDescriptor{} }},
	"HealthReport":     {"health-report.valid.json", func() any { return &HealthReport{} }},
	"SafetyState":      {"safety-state.valid.json", func() any { return &SafetyState{} }},
	"UpdateManifest":   {"update-manifest.valid.json", func() any { return &UpdateManifest{} }},
	"EventEnvelope":    {"event-envelope.valid.json", func() any { return &EventEnvelope{} }},
	"ServerDiscovery":  {"server-discovery.valid.json", func() any { return &ServerDiscovery{} }},
	"ProjectManifest":  {"project-manifest.valid.json", func() any { return &ProjectManifest{} }},
	"Capability":       {"capability.valid.json", func() any { return &map[string]interface{}{} }},
	"Operation":        {"operation.valid.json", func() any { return &map[string]interface{}{} }},
	"ScenarioOutcome":  {"scenario-outcome.valid.json", func() any { return &map[string]interface{}{} }},
}

// TestContractRoundtripPreservesEveryField decodes each real fixture into
// this client's own native representation for that contract (a
// hand-written struct where one exists, a generic map otherwise),
// re-encodes it, and asserts the re-encoded JSON is structurally
// equivalent to the original fixture (compared as generic
// map[string]interface{}, so key order/whitespace differences don't count
// as a real mismatch - only actual data loss or mutation does).
func TestContractRoundtripPreservesEveryField(t *testing.T) {
	dir := fixturesDir(t)
	for contract, spec := range roundtripFixtures {
		contract, spec := contract, spec
		t.Run(contract, func(t *testing.T) {
			raw := readFixture(t, dir, spec.file)

			var original map[string]interface{}
			if err := json.Unmarshal(raw, &original); err != nil {
				t.Fatalf("%s: fixture is not valid JSON: %v", contract, err)
			}

			decoded := spec.newType()
			if err := json.Unmarshal(raw, decoded); err != nil {
				t.Fatalf("%s: failed to decode into %T: %v", contract, decoded, err)
			}

			reencoded, err := json.Marshal(decoded)
			if err != nil {
				t.Fatalf("%s: failed to re-encode %T: %v", contract, decoded, err)
			}

			var roundtripped map[string]interface{}
			if err := json.Unmarshal(reencoded, &roundtripped); err != nil {
				t.Fatalf("%s: re-encoded output is not valid JSON: %v", contract, err)
			}

			if !reflect.DeepEqual(original, roundtripped) {
				t.Fatalf("%s: round trip through %T did not structurally match the original fixture\noriginal:  %s\nroundtrip: %s", contract, decoded, original, roundtripped)
			}
		})
	}
}
