// =============================================================================
// HYDRA-UMC-SDK - Go reference client: Operation, Capability and
// ScenarioOutcome contract types
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

package hydraumc

import "encoding/json"

// These three schemas set additionalProperties: true, so every struct below
// keeps the fields it does not name in Extra and writes them back when it is
// encoded: a payload from a newer producer survives a decode/encode pass
// instead of being silently trimmed.

// decodeWithExtra decodes data into target (an alias type without the
// custom methods) and fills extra with every key not listed in known.
func decodeWithExtra(data []byte, target any, known []string, extra *map[string]json.RawMessage) error {
	if err := json.Unmarshal(data, target); err != nil {
		return err
	}
	all := map[string]json.RawMessage{}
	if err := json.Unmarshal(data, &all); err != nil {
		return err
	}
	for _, key := range known {
		delete(all, key)
	}
	if len(all) == 0 {
		*extra = nil
		return nil
	}
	*extra = all
	return nil
}

// encodeWithExtra encodes value (an alias type) and adds the extra keys that
// do not collide with a field the struct names.
func encodeWithExtra(value any, extra map[string]json.RawMessage) ([]byte, error) {
	raw, err := json.Marshal(value)
	if err != nil {
		return nil, err
	}
	if len(extra) == 0 {
		return raw, nil
	}
	merged := map[string]json.RawMessage{}
	if err := json.Unmarshal(raw, &merged); err != nil {
		return nil, err
	}
	for key, val := range extra {
		if _, taken := merged[key]; !taken {
			merged[key] = val
		}
	}
	return json.Marshal(merged)
}

// Target mirrors the "target" object of operation.schema.json and
// capability.schema.json.
type Target struct {
	Kind  string                     `json:"kind"`
	ID    string                     `json:"id"`
	Extra map[string]json.RawMessage `json:"-"`
}

type targetAlias Target

// UnmarshalJSON keeps unknown fields in Extra.
func (t *Target) UnmarshalJSON(data []byte) error {
	return decodeWithExtra(data, (*targetAlias)(t), []string{"kind", "id"}, &t.Extra)
}

// MarshalJSON writes the known fields and Extra.
func (t Target) MarshalJSON() ([]byte, error) {
	return encodeWithExtra(targetAlias(t), t.Extra)
}

// OperationStatus is the operation.schema.json "status" enum.
type OperationStatus string

const (
	OperationReceived   OperationStatus = "received"
	OperationAuthorized OperationStatus = "authorized"
	OperationQueued     OperationStatus = "queued"
	OperationSent       OperationStatus = "sent"
	OperationConfirmed  OperationStatus = "confirmed"
	OperationTerminated OperationStatus = "terminated"
	OperationRejected   OperationStatus = "rejected"
)

// OperationError mirrors the "error" object of operation.schema.json.
type OperationError struct {
	Code    string                     `json:"code"`
	Message string                     `json:"message"`
	Extra   map[string]json.RawMessage `json:"-"`
}

type operationErrorAlias OperationError

// UnmarshalJSON keeps unknown fields in Extra.
func (e *OperationError) UnmarshalJSON(data []byte) error {
	return decodeWithExtra(data, (*operationErrorAlias)(e), []string{"code", "message"}, &e.Extra)
}

// MarshalJSON writes the known fields and Extra.
func (e OperationError) MarshalJSON() ([]byte, error) {
	return encodeWithExtra(operationErrorAlias(e), e.Extra)
}

// OperationOrigin is the operation.schema.json "result.origin" enum.
type OperationOrigin string

const (
	OriginReal      OperationOrigin = "real"
	OriginSimulated OperationOrigin = "simulated"
)

// OperationOutcome is the operation.schema.json "result.outcome" enum.
type OperationOutcome string

const (
	OutcomeSuccess OperationOutcome = "success"
	OutcomeFailure OperationOutcome = "failure"
	OutcomeUnknown OperationOutcome = "unknown"
)

// OperationResult mirrors the "result" object of operation.schema.json: the
// evidence that an operation really was confirmed. OutcomeReason is required
// by the schema unless the outcome is "success".
type OperationResult struct {
	RunID            string                     `json:"run_id"`
	Revision         *string                    `json:"revision,omitempty"`
	Origin           OperationOrigin            `json:"origin"`
	ObserversEnabled bool                       `json:"observers_enabled"`
	AcceptedAtUTC    *string                    `json:"accepted_at_utc,omitempty"`
	ExecutedAtUTC    *string                    `json:"executed_at_utc,omitempty"`
	ObservedAtUTC    *string                    `json:"observed_at_utc,omitempty"`
	Outcome          OperationOutcome           `json:"outcome"`
	OutcomeReason    *string                    `json:"outcome_reason,omitempty"`
	Extra            map[string]json.RawMessage `json:"-"`
}

type operationResultAlias OperationResult

var operationResultKnown = []string{
	"run_id", "revision", "origin", "observers_enabled", "accepted_at_utc",
	"executed_at_utc", "observed_at_utc", "outcome", "outcome_reason",
}

// UnmarshalJSON keeps unknown fields in Extra.
func (r *OperationResult) UnmarshalJSON(data []byte) error {
	return decodeWithExtra(data, (*operationResultAlias)(r), operationResultKnown, &r.Extra)
}

// MarshalJSON writes the known fields and Extra.
func (r OperationResult) MarshalJSON() ([]byte, error) {
	return encodeWithExtra(operationResultAlias(r), r.Extra)
}

// Operation mirrors operation.schema.json.
type Operation struct {
	SchemaVersion  string                     `json:"schema_version"`
	OperationID    string                     `json:"operation_id"`
	CorrelationID  string                     `json:"correlation_id"`
	Kind           string                     `json:"kind"`
	Target         Target                     `json:"target"`
	Status         OperationStatus            `json:"status"`
	StatusReason   *string                    `json:"status_reason,omitempty"`
	RequestedAtUTC string                     `json:"requested_at_utc"`
	UpdatedAtUTC   string                     `json:"updated_at_utc"`
	Params         map[string]interface{}     `json:"params"`
	Error          *OperationError            `json:"error,omitempty"`
	Result         *OperationResult           `json:"result,omitempty"`
	Extra          map[string]json.RawMessage `json:"-"`
}

type operationAlias Operation

var operationKnown = []string{
	"schema_version", "operation_id", "correlation_id", "kind", "target", "status",
	"status_reason", "requested_at_utc", "updated_at_utc", "params", "error", "result",
}

// UnmarshalJSON keeps unknown fields in Extra.
func (o *Operation) UnmarshalJSON(data []byte) error {
	return decodeWithExtra(data, (*operationAlias)(o), operationKnown, &o.Extra)
}

// MarshalJSON writes the known fields and Extra.
func (o Operation) MarshalJSON() ([]byte, error) {
	return encodeWithExtra(operationAlias(o), o.Extra)
}

// CapabilityCheckOutcome is the capability.schema.json "last_check_outcome"
// enum.
type CapabilityCheckOutcome string

const (
	CheckVerified CapabilityCheckOutcome = "verified"
	CheckFailed   CapabilityCheckOutcome = "failed"
	CheckUnknown  CapabilityCheckOutcome = "unknown"
)

// Capability mirrors capability.schema.json.
type Capability struct {
	SchemaVersion        string                     `json:"schema_version"`
	Target               Target                     `json:"target"`
	Kind                 string                     `json:"kind"`
	Declared             bool                       `json:"declared"`
	LastCheckedAtUTC     *string                    `json:"last_checked_at_utc,omitempty"`
	CheckedConfiguration *string                    `json:"checked_configuration,omitempty"`
	MaxAgeSeconds        *float64                   `json:"max_age_seconds,omitempty"`
	LastCheckOutcome     *CapabilityCheckOutcome    `json:"last_check_outcome,omitempty"`
	LastCheckReason      *string                    `json:"last_check_reason,omitempty"`
	Extra                map[string]json.RawMessage `json:"-"`
}

type capabilityAlias Capability

var capabilityKnown = []string{
	"schema_version", "target", "kind", "declared", "last_checked_at_utc",
	"checked_configuration", "max_age_seconds", "last_check_outcome", "last_check_reason",
}

// UnmarshalJSON keeps unknown fields in Extra.
func (c *Capability) UnmarshalJSON(data []byte) error {
	return decodeWithExtra(data, (*capabilityAlias)(c), capabilityKnown, &c.Extra)
}

// MarshalJSON writes the known fields and Extra.
func (c Capability) MarshalJSON() ([]byte, error) {
	return encodeWithExtra(capabilityAlias(c), c.Extra)
}

// ScenarioPhase is the scenario-outcome.schema.json "phase" enum.
type ScenarioPhase string

const (
	PhaseBefore ScenarioPhase = "before"
	PhaseAfter  ScenarioPhase = "after"
)

// ScenarioObservedOutcome is the scenario-outcome.schema.json
// "observed.outcome" enum.
type ScenarioObservedOutcome string

const (
	ScenarioReproduced    ScenarioObservedOutcome = "reproduced"
	ScenarioNotReproduced ScenarioObservedOutcome = "not-reproduced"
	ScenarioError         ScenarioObservedOutcome = "error"
)

// ScenarioObserved mirrors the "observed" object of scenario-outcome.schema.json.
type ScenarioObserved struct {
	Outcome  ScenarioObservedOutcome    `json:"outcome"`
	ExitCode *int64                     `json:"exit_code,omitempty"`
	Evidence *string                    `json:"evidence,omitempty"`
	Extra    map[string]json.RawMessage `json:"-"`
}

type scenarioObservedAlias ScenarioObserved

// UnmarshalJSON keeps unknown fields in Extra.
func (s *ScenarioObserved) UnmarshalJSON(data []byte) error {
	return decodeWithExtra(data, (*scenarioObservedAlias)(s), []string{"outcome", "exit_code", "evidence"}, &s.Extra)
}

// MarshalJSON writes the known fields and Extra.
func (s ScenarioObserved) MarshalJSON() ([]byte, error) {
	return encodeWithExtra(scenarioObservedAlias(s), s.Extra)
}

// ScenarioOutcome mirrors scenario-outcome.schema.json.
type ScenarioOutcome struct {
	SchemaVersion   string                     `json:"schema_version"`
	ScenarioID      string                     `json:"scenario_id"`
	RunID           string                     `json:"run_id"`
	BaseFingerprint string                     `json:"base_fingerprint"`
	Phase           ScenarioPhase              `json:"phase"`
	ReproCase       string                     `json:"repro_case"`
	Observed        ScenarioObserved           `json:"observed"`
	TimestampUTC    string                     `json:"timestamp_utc"`
	Extra           map[string]json.RawMessage `json:"-"`
}

type scenarioOutcomeAlias ScenarioOutcome

var scenarioOutcomeKnown = []string{
	"schema_version", "scenario_id", "run_id", "base_fingerprint", "phase",
	"repro_case", "observed", "timestamp_utc",
}

// UnmarshalJSON keeps unknown fields in Extra.
func (s *ScenarioOutcome) UnmarshalJSON(data []byte) error {
	return decodeWithExtra(data, (*scenarioOutcomeAlias)(s), scenarioOutcomeKnown, &s.Extra)
}

// MarshalJSON writes the known fields and Extra.
func (s ScenarioOutcome) MarshalJSON() ([]byte, error) {
	return encodeWithExtra(scenarioOutcomeAlias(s), s.Extra)
}
