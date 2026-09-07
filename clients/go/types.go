// =============================================================================
// HYDRA-UMC-SDK - Go reference client: hand-written contract types
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

// Package hydraumc is the Go reference client for the HYDRA-UMC-SDK v1
// contracts: hand-written struct types mirroring the published JSON Schema
// files under contracts/json-schema/v1/, plus real schema-based runtime
// validation (see validation.go). The JSON Schema files remain the
// normative source, exactly as documented in docs/CONTRACTS.md for the
// Python reference client; these types and the embedded schema copies are
// checked against that source by TestVendoredSchemasMatchCanonical so they
// cannot silently drift.
package hydraumc

// SchemaVersion is the only schema_version value every v1 contract accepts.
const SchemaVersion = "1.0"

// DeviceDescriptor mirrors device-descriptor.schema.json.
type DeviceDescriptor struct {
	SchemaVersion   string   `json:"schema_version"`
	NodeID          string   `json:"node_id"`
	Profile         string   `json:"profile"`
	Hostname        string   `json:"hostname"`
	Machine         string   `json:"machine"`
	OperatingSystem string   `json:"operating_system"`
	Kernel          string   `json:"kernel"`
	Interfaces      []string `json:"interfaces"`
}

// HealthState is the health-report.schema.json "state" enum.
type HealthState string

const (
	HealthReady     HealthState = "READY"
	HealthDegraded  HealthState = "DEGRADED"
	HealthInhibited HealthState = "INHIBITED"
	HealthFault     HealthState = "FAULT"
	HealthSafeStop  HealthState = "SAFE_STOP"
)

// HealthReport mirrors health-report.schema.json.
type HealthReport struct {
	SchemaVersion string                 `json:"schema_version"`
	State         HealthState            `json:"state"`
	TimestampUTC  string                 `json:"timestamp_utc"`
	Checks        map[string]interface{} `json:"checks"`
}

// SafetyStateValue is the safety-state.schema.json "state" enum - narrower
// than HealthState (no DEGRADED), matching the real schema and the Python
// reference validator's own documented distinction.
type SafetyStateValue string

const (
	SafetyReady     SafetyStateValue = "READY"
	SafetyInhibited SafetyStateValue = "INHIBITED"
	SafetyFault     SafetyStateValue = "FAULT"
	SafetySafeStop  SafetyStateValue = "SAFE_STOP"
)

// SafetyState mirrors safety-state.schema.json.
type SafetyState struct {
	SchemaVersion string           `json:"schema_version"`
	State         SafetyStateValue `json:"state"`
	Source        string           `json:"source"`
	TimestampUTC  string           `json:"timestamp_utc"`
}

// UpdateManifest mirrors update-manifest.schema.json.
type UpdateManifest struct {
	SchemaVersion string `json:"schema_version"`
	Project       string `json:"project"`
	Version       string `json:"version"`
	ArtifactURL   string `json:"artifact_url"`
	SHA256        string `json:"sha256"`
}

// EventEnvelope mirrors event-envelope.schema.json. CorrelationID is
// optional in the schema, so it is a pointer to distinguish "absent" from
// an empty string when round-tripping through encoding/json.
type EventEnvelope struct {
	SchemaVersion string  `json:"schema_version"`
	EventID       string  `json:"event_id"`
	Type          string  `json:"type"`
	Source        string  `json:"source"`
	TimestampUTC  string  `json:"timestamp_utc"`
	Sequence      int64   `json:"sequence"`
	CorrelationID *string `json:"correlation_id,omitempty"`
}

// ServerDiscovery mirrors server-discovery.schema.json, including its
// deliberately camelCase field names (the real GET /api/hydra-info wire
// shape - see docs/CONTRACTS.md).
type ServerDiscovery struct {
	SchemaVersion    string `json:"schema_version"`
	Product          string `json:"product"`
	RemoteAPIVersion int64  `json:"remoteApiVersion"`
	AppVersion       string `json:"appVersion"`
	Hostname         string `json:"hostname"`
	ControllerCount  int64  `json:"controllerCount"`
	RobotCount       int64  `json:"robotCount"`
	UptimeSeconds    int64  `json:"uptimeSeconds"`
}

// ProjectManifestRole is the project-manifest.schema.json "role" enum.
type ProjectManifestRole string

const (
	RoleAPI      ProjectManifestRole = "api"
	RoleUI       ProjectManifestRole = "ui"
	RoleCLI      ProjectManifestRole = "cli"
	RoleFirmware ProjectManifestRole = "firmware"
	RoleLibrary  ProjectManifestRole = "library"
	RoleService  ProjectManifestRole = "service"
	RoleTool     ProjectManifestRole = "tool"
)

// ProjectManifestDeploymentTarget is the project-manifest.schema.json
// "deployment_target" enum.
type ProjectManifestDeploymentTarget string

const (
	DeploymentCM5      ProjectManifestDeploymentTarget = "cm5"
	DeploymentUserPC   ProjectManifestDeploymentTarget = "user-pc"
	DeploymentMobile   ProjectManifestDeploymentTarget = "mobile"
	DeploymentWearable ProjectManifestDeploymentTarget = "wearable"
)

// ProjectManifestMaturity is the project-manifest.schema.json "maturity"
// enum.
type ProjectManifestMaturity string

const (
	MaturityScaffolding ProjectManifestMaturity = "scaffolding"
	MaturityFunctional  ProjectManifestMaturity = "functional"
	MaturityEstablished ProjectManifestMaturity = "established"
	MaturityProduction  ProjectManifestMaturity = "production"
)

// NativeVersionPattern is native_version.pattern's "oneOf": either a single
// regular expression capturing major.minor.patch, or a mapping of one
// regular expression per component. Exactly one of Pattern or Components
// is set for a valid payload; MarshalJSON/UnmarshalJSON round-trip either
// shape without inventing a field the schema does not have.
type NativeVersionPattern struct {
	Pattern    string
	Components *NativeVersionPatternComponents
}

// NativeVersionPatternComponents is native_version.pattern's object form.
type NativeVersionPatternComponents struct {
	Major string `json:"major"`
	Minor string `json:"minor"`
	Patch string `json:"patch"`
}

// NativeVersion mirrors project-manifest.schema.json's native_version.
type NativeVersion struct {
	File    string               `json:"file"`
	Pattern NativeVersionPattern `json:"pattern"`
}

// ProjectManifest mirrors project-manifest.schema.json - the
// hydra-umc.project.json contract every repository in this ecosystem
// publishes.
type ProjectManifest struct {
	SchemaVersion    string                          `json:"schema_version"`
	Ecosystem        string                          `json:"ecosystem"`
	Name             string                          `json:"name"`
	Version          string                          `json:"version"`
	Role             ProjectManifestRole             `json:"role"`
	Stack            string                          `json:"stack"`
	Technologies     []string                        `json:"technologies"`
	DeploymentTarget ProjectManifestDeploymentTarget `json:"deployment_target"`
	Maturity         ProjectManifestMaturity         `json:"maturity"`
	Family           string                          `json:"family"`
	Parent           *string                         `json:"parent"`
	NativeVersion    NativeVersion                   `json:"native_version"`
	Build            string                          `json:"build"`
	Notes            string                          `json:"notes"`
}

// ContractManifestEntry is one entry of manifest.json's "contracts" array:
// a published schema file's name and its sha256 digest.
type ContractManifestEntry struct {
	File   string `json:"file"`
	SHA256 string `json:"sha256"`
}

// ContractManifest mirrors contracts/json-schema/v1/manifest.json - the
// generated integrity manifest listing every published v1 schema file and
// its sha256 digest (see contracts/generate_manifest.py). It is data, not
// itself a JSON Schema, so it has no schema-based Validate() entry point;
// VerifyContractManifest (validation.go) instead recomputes each listed
// file's digest and compares it for real.
type ContractManifest struct {
	SchemaVersion string                  `json:"schema_version"`
	Contracts     []ContractManifestEntry `json:"contracts"`
}
