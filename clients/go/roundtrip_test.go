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

// roundtripFixtures is the same 10-contract set every other language's own
// round-trip test uses (see clients/python/tests/test_contract_roundtrip.py
// and clients/rust/tests/roundtrip.rs), each paired with a `new() any`
// factory for the concrete Go type this client decodes that contract into.
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
	"Capability":       {"capability.valid.json", func() any { return &Capability{} }},
	"Operation":        {"operation.valid.json", func() any { return &Operation{} }},
	"ScenarioOutcome":  {"scenario-outcome.valid.json", func() any { return &ScenarioOutcome{} }},
}

// TestContractRoundtripPreservesEveryField decodes each real fixture into
// this client's own native representation for that contract (a
// hand-written struct),
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

// TestNewerContractsKeepUnknownFields checks that the structs of the three
// contracts that allow additional properties write back what they do not
// name.
func TestNewerContractsKeepUnknownFields(t *testing.T) {
	cases := map[string]struct {
		raw string
		out any
	}{
		"Operation":       {`{"schema_version":"1.0","operation_id":"o","correlation_id":"c","kind":"k","target":{"kind":"robot","id":"r","x":1},"status":"queued","requested_at_utc":"2024-01-01T00:00:00Z","updated_at_utc":"2024-01-01T00:00:00Z","params":{},"future":{"a":1}}`, &Operation{}},
		"Capability":      {`{"schema_version":"1.0","target":{"kind":"robot","id":"r"},"kind":"k","declared":false,"future":[1,2]}`, &Capability{}},
		"ScenarioOutcome": {`{"schema_version":"1.0","scenario_id":"s","run_id":"r","base_fingerprint":"f","phase":"before","repro_case":"c","observed":{"outcome":"reproduced","more":true},"timestamp_utc":"2024-01-01T00:00:00Z","future":1}`, &ScenarioOutcome{}},
	}
	for name, tc := range cases {
		name, tc := name, tc
		t.Run(name, func(t *testing.T) {
			if err := json.Unmarshal([]byte(tc.raw), tc.out); err != nil {
				t.Fatalf("decode: %v", err)
			}
			out, err := json.Marshal(tc.out)
			if err != nil {
				t.Fatalf("encode: %v", err)
			}
			var want, got map[string]interface{}
			_ = json.Unmarshal([]byte(tc.raw), &want)
			_ = json.Unmarshal(out, &got)
			if !reflect.DeepEqual(want, got) {
				t.Fatalf("unknown fields were lost\nwant: %s\ngot:  %s", want, got)
			}
		})
	}
}

// TestOperationTypedAccess reads the real Operation fixture through the
// typed fields.
func TestOperationTypedAccess(t *testing.T) {
	raw := readFixture(t, fixturesDir(t), "operation.valid.json")
	var op Operation
	if err := json.Unmarshal(raw, &op); err != nil {
		t.Fatal(err)
	}
	if op.Status != OperationTerminated || op.Result == nil || op.Result.Origin != OriginReal || op.Result.Outcome != OutcomeSuccess {
		t.Fatalf("unexpected typed view: %+v", op)
	}
	if op.Target.ID != "controller-1:robot-3" {
		t.Fatalf("target id %q", op.Target.ID)
	}
}
