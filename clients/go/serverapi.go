// =============================================================================
// HYDRA-UMC-SDK - Go client of the claim, jog arming and safety-limit routes
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

package hydraumc

// Typed access to the routes of HYDRA-UMC-SERVER that decide who controls a
// robot and how far a jog may go: claim, release, jog-arm, GET /api/claims,
// GET /api/safety-limits and PUT /api/admin/safety-limits, plus the optional
// controllerId of command. The second block of the contract is here too (see
// serverapi_v2.go): GET /api/robot/:id with its revision, If-Match, the atomic
// table command, GET /api/audit and the claims message of the WebSocket.
// Request builders and response parsers never touch
// the network; ServerClient carries them over net/http (or any Doer).
// Everything is additive: a request without a controller id is the v1
// request, unknown response fields are ignored and an unknown error code
// stays a plain *APIError. The server decides; nothing here checks a limit,
// a claim or an arming on its own.

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"regexp"
	"strings"
)

// ControllerIDHeader is the header that names the controller of a request.
const ControllerIDHeader = "X-Controller-Id"

// Stable refusal codes of the server.
const (
	CodeOtherAccount         = "other-account"
	CodeOtherController      = "other-controller"
	CodeControllerIDRequired = "controller-id-required"
	CodeInvalidControllerID  = "invalid-controller-id"
	CodeJogNotArmed          = "jog-not-armed"
	CodeRevisionMismatch     = "revision-mismatch"
	CodeTableInvalid         = "table-invalid"
	CodeTableOutOfLimit      = "table-out-of-limit"
	CodeTableMissing         = "table-missing"
)

var controllerIDPattern = regexp.MustCompile(`^[A-Za-z0-9._:-]{1,64}$`)

// IsValidControllerID reports whether value is 1 to 64 characters of letters,
// digits and ". _ : -".
func IsValidControllerID(value string) bool { return controllerIDPattern.MatchString(value) }

// ServerRequestError is a request the client refuses to build; nothing was sent.
type ServerRequestError struct{ Message string }

func (e *ServerRequestError) Error() string { return e.Message }

// APIError is an error answer: HTTP status, readable text, the stable code
// when the server sent one and the decoded body.
type APIError struct {
	Status  int
	Message string
	Code    string // empty when the server sent none
	Body    json.RawMessage
}

func (e *APIError) Error() string {
	if e.Code != "" {
		return fmt.Sprintf("%d %s: %s", e.Status, e.Code, e.Message)
	}
	return fmt.Sprintf("%d %s", e.Status, e.Message)
}

// ClaimConflictError: the robot is claimed by someone else. Code is
// other-account or other-controller (empty on a server that predates the
// codes) and Reservation is the claim that blocks the caller.
type ClaimConflictError struct {
	APIError
	Reservation *Reservation
}

// ControllerIDRequiredError: the claim has a controller (409) or the server
// demands one to claim (400); send a controllerId.
type ControllerIDRequiredError struct{ ClaimConflictError }

// InvalidControllerIDError: the server refused the shape of the controllerId (400).
type InvalidControllerIDError struct{ APIError }

// JogNotArmedError: a jog was refused because the robot is not armed (403).
type JogNotArmedError struct{ APIError }

// Unwrap lets errors.As see every typed error as an *APIError too.
func (e *ClaimConflictError) Unwrap() error        { return &e.APIError }
func (e *ControllerIDRequiredError) Unwrap() error { return &e.ClaimConflictError }
func (e *InvalidControllerIDError) Unwrap() error  { return &e.APIError }
func (e *JogNotArmedError) Unwrap() error          { return &e.APIError }

// Reservation is a claim on a robot.
type Reservation struct {
	OwnerID       json.RawMessage `json:"ownerId"`
	OwnerUsername string          `json:"ownerUsername"`
	ClaimedAt     float64         `json:"claimedAt"`
	ExpiresAt     float64         `json:"expiresAt"`
	ControllerID  *string         `json:"controllerId,omitempty"`
}

// ClaimResult is the answer of claim and of release (Reservation is nil after a release).
type ClaimResult struct {
	Reservation *Reservation     `json:"reservation"`
	History     []map[string]any `json:"reservationHistory"`
	// Revision is the new revision of the robot, empty when the server sent none.
	Revision string `json:"revision,omitempty"`
}

// JogArmResult is the answer of jog-arm.
type JogArmResult struct {
	Armed     bool     `json:"armed"`
	ExpiresAt *float64 `json:"expiresAt,omitempty"`
	TTLMs     *float64 `json:"ttlMs,omitempty"`
}

// ClaimEntry is one line of GET /api/claims. ControllerID is nil for a claim
// made without one; CellID is the cell of the settings tree, not a client.
type ClaimEntry struct {
	RobotID       int             `json:"robotId"`
	RobotName     *string         `json:"robotName"`
	CellID        json.RawMessage `json:"cellId"`
	OwnerID       json.RawMessage `json:"ownerId"`
	OwnerUsername string          `json:"ownerUsername"`
	ControllerID  *string         `json:"controllerId"`
	ClaimedAt     float64         `json:"claimedAt"`
	ExpiresAt     float64         `json:"expiresAt"`
	// JogArmedUntil is when the arming of the jog of this robot ends, nil when it is not armed.
	JogArmedUntil *float64 `json:"jogArmedUntil"`
}

// RobotSafety is the part of the safety limits that applies to one robot.
type RobotSafety struct {
	ID            int            `json:"id"`
	Model         *string        `json:"model"`
	Jog           map[string]any `json:"jog"`
	Temperature   map[string]any `json:"temperature"`
	JogArmedUntil *float64       `json:"jogArmedUntil"`
}

// SafetyLimitsView is the answer of GET and PUT of the safety limits; the
// sections stay as the server sent them because the server owns their shape.
type SafetyLimitsView struct {
	Limits     map[string]any `json:"limits"`
	Defaults   map[string]any `json:"defaults"`
	HardLimits map[string]any `json:"hardLimits"`
	Robot      *RobotSafety   `json:"robot,omitempty"`
}

// ServerRequest is a request ready to send: Body is nil for a request without one.
type ServerRequest struct {
	Method string
	Path   string
	Body   map[string]any
	// Headers are the extra headers of the request (If-Match); nil when there are none.
	Headers map[string]string
}

func checkController(controllerID string) error {
	if controllerID != "" && !IsValidControllerID(controllerID) {
		return &ServerRequestError{"controllerId must be 1 to 64 characters: letters, digits, . _ : -"}
	}
	return nil
}

// ClaimOptions are the optional fields of claim; nil pointers are not sent.
type ClaimOptions struct {
	TTLMs        *float64
	Force        *bool
	Reason       *string
	ControllerID string // empty: none
	IfMatch      string // empty: unconditional
}

// ClaimRequest builds POST /api/robot/{id}/claim.
func ClaimRequest(robotID int, o ClaimOptions) (ServerRequest, error) {
	if err := checkController(o.ControllerID); err != nil {
		return ServerRequest{}, err
	}
	body := map[string]any{}
	if o.TTLMs != nil {
		body["ttlMs"] = *o.TTLMs
	}
	if o.Force != nil {
		body["force"] = *o.Force
	}
	if o.Reason != nil {
		body["reason"] = *o.Reason
	}
	if o.ControllerID != "" {
		body["controllerId"] = o.ControllerID
	}
	headers, err := ifMatchHeaders(o.IfMatch)
	if err != nil {
		return ServerRequest{}, err
	}
	return ServerRequest{Method: "POST", Path: fmt.Sprintf("/api/robot/%d/claim", robotID), Body: body, Headers: headers}, nil
}

// ReleaseRequest builds POST /api/robot/{id}/release.
func ReleaseRequest(robotID int, reason *string, controllerID string) (ServerRequest, error) {
	return ReleaseRequestWith(robotID, ReleaseOptions{Reason: reason, ControllerID: controllerID})
}

// JogArmRequest builds POST /api/robot/{id}/jog-arm.
func JogArmRequest(robotID int, armed bool, ttlMs *float64, controllerID string) (ServerRequest, error) {
	if err := checkController(controllerID); err != nil {
		return ServerRequest{}, err
	}
	body := map[string]any{"armed": armed}
	if ttlMs != nil {
		body["ttlMs"] = *ttlMs
	}
	if controllerID != "" {
		body["controllerId"] = controllerID
	}
	return ServerRequest{Method: "POST", Path: fmt.Sprintf("/api/robot/%d/jog-arm", robotID), Body: body}, nil
}

// ListClaimsRequest builds GET /api/claims.
func ListClaimsRequest() ServerRequest { return ServerRequest{Method: "GET", Path: "/api/claims"} }

// SafetyLimitsRequest builds GET /api/safety-limits, with ?robotId= when robotID is not nil.
func SafetyLimitsRequest(robotID *int) ServerRequest {
	path := "/api/safety-limits"
	if robotID != nil {
		path += fmt.Sprintf("?robotId=%d", *robotID)
	}
	return ServerRequest{Method: "GET", Path: path}
}

// UpdateSafetyLimitsRequest builds PUT /api/admin/safety-limits.
func UpdateSafetyLimitsRequest(patch map[string]any) (ServerRequest, error) {
	if patch == nil {
		return ServerRequest{}, &ServerRequestError{"patch must be an object"}
	}
	body := make(map[string]any, len(patch))
	for k, v := range patch {
		body[k] = v
	}
	return ServerRequest{Method: "PUT", Path: "/api/admin/safety-limits", Body: body}, nil
}

// CommandRequest builds POST /api/robot/{id}/command with the optional controller id.
func CommandRequest(robotID int, command string, params map[string]any, controllerID string) (ServerRequest, error) {
	return CommandRequestWith(robotID, command, params, CommandOptions{ControllerID: controllerID})
}

// ParseClaimResult decodes the answer of claim and release.
func ParseClaimResult(body []byte) (ClaimResult, error) {
	var result ClaimResult
	if err := json.Unmarshal(body, &result); err != nil {
		return ClaimResult{}, &ServerRequestError{"claim answer is not a JSON object"}
	}
	return result, nil
}

// ParseJogArmResult decodes the answer of jog-arm; the answer must carry a boolean "armed".
func ParseJogArmResult(body []byte) (JogArmResult, error) {
	var raw map[string]json.RawMessage
	if err := json.Unmarshal(body, &raw); err != nil {
		return JogArmResult{}, &ServerRequestError{"jog-arm answer is not a JSON object"}
	}
	if _, ok := raw["armed"]; !ok {
		return JogArmResult{}, &ServerRequestError{"jog-arm answer has no boolean 'armed'"}
	}
	var result JogArmResult
	if err := json.Unmarshal(body, &result); err != nil {
		return JogArmResult{}, &ServerRequestError{"jog-arm answer has no boolean 'armed'"}
	}
	return result, nil
}

// ParseClaims decodes GET /api/claims.
func ParseClaims(body []byte) ([]ClaimEntry, error) {
	var wrapper struct {
		Claims *[]ClaimEntry `json:"claims"`
	}
	if err := json.Unmarshal(body, &wrapper); err != nil || wrapper.Claims == nil {
		return nil, &ServerRequestError{"claims answer has no 'claims' list"}
	}
	return *wrapper.Claims, nil
}

// ParseSafetyLimits decodes GET and PUT of the safety limits.
func ParseSafetyLimits(body []byte) (SafetyLimitsView, error) {
	var view SafetyLimitsView
	if err := json.Unmarshal(body, &view); err != nil {
		return SafetyLimitsView{}, &ServerRequestError{"safety-limits answer is not a JSON object"}
	}
	return view, nil
}

// ParseAPIError turns an error answer into the most specific typed error.
// body may be empty or not JSON.
func ParseAPIError(status int, body []byte) error {
	var data struct {
		Error       string          `json:"error"`
		Code        string          `json:"code"`
		Reservation json.RawMessage `json:"reservation"`
		Revision    string          `json:"revision"`
	}
	_ = json.Unmarshal(body, &data) // a body that is not a JSON object leaves the zero values
	message := data.Error
	if message == "" {
		message = fmt.Sprintf("HTTP %d", status)
	}
	base := APIError{Status: status, Message: message, Code: data.Code, Body: json.RawMessage(body)}
	var reservation *Reservation
	if len(data.Reservation) > 0 && string(data.Reservation) != "null" {
		var parsed Reservation
		if json.Unmarshal(data.Reservation, &parsed) == nil {
			reservation = &parsed
		}
	}
	switch {
	case data.Code == CodeControllerIDRequired:
		return &ControllerIDRequiredError{ClaimConflictError{base, reservation}}
	case data.Code == CodeOtherAccount || data.Code == CodeOtherController:
		return &ClaimConflictError{base, reservation}
	case data.Code == CodeInvalidControllerID:
		return &InvalidControllerIDError{base}
	case data.Code == CodeJogNotArmed:
		return &JogNotArmedError{base}
	case data.Code == CodeRevisionMismatch || status == http.StatusPreconditionFailed:
		return &RevisionMismatchError{APIError: base, Revision: data.Revision}
	case data.Code == CodeTableInvalid || data.Code == CodeTableOutOfLimit || data.Code == CodeTableMissing:
		return &TableMoveError{base}
	case status == http.StatusConflict && reservation != nil:
		return &ClaimConflictError{base, reservation}
	}
	return &base
}

// Doer is the part of *http.Client that ServerClient needs.
type Doer interface {
	Do(*http.Request) (*http.Response, error)
}

// ServerClient calls the routes above. ControllerID is the identity this
// client picked for its session; it is sent with every request that accepts
// one unless the call passes its own.
type ServerClient struct {
	BaseURL      string
	Token        string
	ControllerID string
	HTTP         Doer
}

// NewServerClient checks the default controller id and uses http.DefaultClient.
func NewServerClient(baseURL, token, controllerID string) (*ServerClient, error) {
	if err := checkController(controllerID); err != nil {
		return nil, err
	}
	return &ServerClient{BaseURL: strings.TrimRight(baseURL, "/"), Token: token, ControllerID: controllerID, HTTP: http.DefaultClient}, nil
}

func (c *ServerClient) controllerFor(own string) string {
	if own != "" {
		return own
	}
	return c.ControllerID
}

func (c *ServerClient) send(request ServerRequest) ([]byte, error) {
	var reader io.Reader
	if request.Body != nil {
		encoded, err := json.Marshal(request.Body)
		if err != nil {
			return nil, err
		}
		reader = bytes.NewReader(encoded)
	}
	httpRequest, err := http.NewRequest(request.Method, strings.TrimRight(c.BaseURL, "/")+request.Path, reader)
	if err != nil {
		return nil, err
	}
	httpRequest.Header.Set("Accept", "application/json")
	for name, value := range request.Headers {
		httpRequest.Header.Set(name, value)
	}
	if c.Token != "" {
		httpRequest.Header.Set("Authorization", "Bearer "+c.Token)
	}
	if request.Body != nil {
		httpRequest.Header.Set("Content-Type", "application/json")
	}
	doer := c.HTTP
	if doer == nil {
		doer = http.DefaultClient
	}
	response, err := doer.Do(httpRequest)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()
	raw, err := io.ReadAll(response.Body)
	if err != nil {
		return nil, err
	}
	if response.StatusCode >= 400 {
		return nil, ParseAPIError(response.StatusCode, raw)
	}
	return raw, nil
}

// Claim calls POST /api/robot/{id}/claim.
func (c *ServerClient) Claim(robotID int, o ClaimOptions) (ClaimResult, error) {
	o.ControllerID = c.controllerFor(o.ControllerID)
	request, err := ClaimRequest(robotID, o)
	if err != nil {
		return ClaimResult{}, err
	}
	raw, err := c.send(request)
	if err != nil {
		return ClaimResult{}, err
	}
	return ParseClaimResult(raw)
}

// Release calls POST /api/robot/{id}/release.
func (c *ServerClient) Release(robotID int, reason *string, controllerID string) (ClaimResult, error) {
	return c.ReleaseWith(robotID, ReleaseOptions{Reason: reason, ControllerID: controllerID})
}

// ReleaseWith calls POST /api/robot/{id}/release with the options (the revision for If-Match among them).
func (c *ServerClient) ReleaseWith(robotID int, o ReleaseOptions) (ClaimResult, error) {
	o.ControllerID = c.controllerFor(o.ControllerID)
	request, err := ReleaseRequestWith(robotID, o)
	if err != nil {
		return ClaimResult{}, err
	}
	raw, err := c.send(request)
	if err != nil {
		return ClaimResult{}, err
	}
	return ParseClaimResult(raw)
}

// JogArm calls POST /api/robot/{id}/jog-arm.
func (c *ServerClient) JogArm(robotID int, armed bool, ttlMs *float64, controllerID string) (JogArmResult, error) {
	request, err := JogArmRequest(robotID, armed, ttlMs, c.controllerFor(controllerID))
	if err != nil {
		return JogArmResult{}, err
	}
	raw, err := c.send(request)
	if err != nil {
		return JogArmResult{}, err
	}
	return ParseJogArmResult(raw)
}

// ListClaims calls GET /api/claims.
func (c *ServerClient) ListClaims() ([]ClaimEntry, error) {
	raw, err := c.send(ListClaimsRequest())
	if err != nil {
		return nil, err
	}
	return ParseClaims(raw)
}

// SafetyLimits calls GET /api/safety-limits.
func (c *ServerClient) SafetyLimits(robotID *int) (SafetyLimitsView, error) {
	raw, err := c.send(SafetyLimitsRequest(robotID))
	if err != nil {
		return SafetyLimitsView{}, err
	}
	return ParseSafetyLimits(raw)
}

// UpdateSafetyLimits calls PUT /api/admin/safety-limits.
func (c *ServerClient) UpdateSafetyLimits(patch map[string]any) (SafetyLimitsView, error) {
	request, err := UpdateSafetyLimitsRequest(patch)
	if err != nil {
		return SafetyLimitsView{}, err
	}
	raw, err := c.send(request)
	if err != nil {
		return SafetyLimitsView{}, err
	}
	return ParseSafetyLimits(raw)
}

// Command calls POST /api/robot/{id}/command and returns the raw answer.
func (c *ServerClient) Command(robotID int, command string, params map[string]any, controllerID string) ([]byte, error) {
	return c.CommandWith(robotID, command, params, CommandOptions{ControllerID: controllerID})
}

// AsAPIError returns the *APIError inside err (every typed error contains one).
func AsAPIError(err error) (*APIError, bool) {
	var apiError *APIError
	ok := errors.As(err, &apiError)
	return apiError, ok
}
