// =============================================================================
// HYDRA-UMC-SDK - Go client of blocks 2 to 5 of the second server contract
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

package hydraumc

// GET /api/robot/:id with its revision, If-Match on command, claim and release (and the 412 it can
// answer), the atomic table command, GET /api/audit and the claims message of the WebSocket. Purely
// additive: a request without these options is the request of the first block.

import (
	"encoding/json"
	"fmt"
	"math"
	"regexp"
	"strings"
)

// TableModes are the modes of the table command.
var TableModes = []string{"absolute", "relative"}

// RevisionMismatchError: If-Match did not agree with the robot (412), it changed since it was read.
// Revision is the current one; read the robot again and retry.
type RevisionMismatchError struct {
	APIError
	Revision string
}

// TableMoveError: a table move was refused as a whole and nothing changed (400); Code is
// table-invalid, table-out-of-limit or table-missing.
type TableMoveError struct{ APIError }

// Unwrap lets errors.As see the typed errors as an *APIError too.
func (e *RevisionMismatchError) Unwrap() error { return &e.APIError }
func (e *TableMoveError) Unwrap() error        { return &e.APIError }

// RobotView is GET /api/robot/:id: the robot as the server holds it (the credentials of the cameras are
// left out unless the caller is an administrator), its revision (the ETag) and its cell.
type RobotView struct {
	Robot    map[string]any  `json:"robot"`
	Revision string          `json:"revision"`
	CellID   json.RawMessage `json:"cellId"`
}

// TableApplied is the position a table move ended in.
type TableApplied struct {
	RobotID int      `json:"robotId"`
	X       float64  `json:"x"`
	Y       float64  `json:"y"`
	RZ      *float64 `json:"rz,omitempty"`
}

// CommandResult is the answer of command: Revision is the robot's new one, Applied is set after a table move.
type CommandResult struct {
	Success       bool             `json:"success"`
	AffectedCount *int             `json:"affectedCount,omitempty"`
	Revision      string           `json:"revision,omitempty"`
	Applied       *TableApplied    `json:"applied,omitempty"`
	Warnings      []map[string]any `json:"warnings,omitempty"`
}

// AuditEntry is one line of the audit record.
type AuditEntry struct {
	Seq          int            `json:"seq"`
	TS           string         `json:"ts"`
	Type         string         `json:"type"`
	Outcome      string         `json:"outcome"`
	Prev         string         `json:"prev"`
	Hash         string         `json:"hash"`
	Username     *string        `json:"username,omitempty"`
	ControllerID *string        `json:"controllerId,omitempty"`
	IP           *string        `json:"ip,omitempty"`
	RobotID      *int           `json:"robotId,omitempty"`
	Detail       map[string]any `json:"detail,omitempty"`
}

// AuditView is GET /api/audit.
type AuditView struct {
	Enabled      bool           `json:"enabled"`
	LockedOff    bool           `json:"lockedOff"`
	Entries      []AuditEntry   `json:"entries"`
	Verification map[string]any `json:"verification,omitempty"`
}

// ReleaseOptions are the optional fields of release.
type ReleaseOptions struct {
	Reason       *string
	ControllerID string // empty: none
	IfMatch      string // empty: unconditional
}

// CommandOptions are the optional fields of command.
type CommandOptions struct {
	ControllerID string // empty: none
	IfMatch      string // empty: unconditional
}

// TableOptions are the optional fields of the table command.
type TableOptions struct {
	RZ           *float64
	Mode         string // "", "absolute" or "relative"; empty means absolute
	ControllerID string
	IfMatch      string
}

// AuditQuery are the filters of GET /api/audit; nil and empty values are not sent.
type AuditQuery struct {
	Limit    *int
	AfterSeq *int
	Type     string
	RobotID  *int
	Verify   bool
}

var auditTypePattern = regexp.MustCompile(`^[A-Za-z0-9._-]{1,40}$`)

// ifMatchHeaders is the If-Match header for a revision (quoted or not) or for "*"; none for "".
func ifMatchHeaders(value string) (map[string]string, error) {
	if value == "" {
		return nil, nil
	}
	text := strings.TrimSpace(value)
	if text == "" || strings.ContainsAny(value, "\r\n") {
		return nil, &ServerRequestError{"ifMatch must be a revision string"}
	}
	if text != "*" && !strings.HasPrefix(text, "\"") && !strings.HasPrefix(text, "W/") {
		text = "\"" + text + "\""
	}
	return map[string]string{"If-Match": text}, nil
}

// ReleaseRequestWith builds POST /api/robot/{id}/release.
func ReleaseRequestWith(robotID int, o ReleaseOptions) (ServerRequest, error) {
	if err := checkController(o.ControllerID); err != nil {
		return ServerRequest{}, err
	}
	headers, err := ifMatchHeaders(o.IfMatch)
	if err != nil {
		return ServerRequest{}, err
	}
	body := map[string]any{}
	if o.Reason != nil {
		body["reason"] = *o.Reason
	}
	if o.ControllerID != "" {
		body["controllerId"] = o.ControllerID
	}
	return ServerRequest{Method: "POST", Path: fmt.Sprintf("/api/robot/%d/release", robotID), Body: body, Headers: headers}, nil
}

// CommandRequestWith builds POST /api/robot/{id}/command with the optional controller id and revision.
func CommandRequestWith(robotID int, command string, params map[string]any, o CommandOptions) (ServerRequest, error) {
	if command == "" {
		return ServerRequest{}, &ServerRequestError{"command must be a non-empty string"}
	}
	if err := checkController(o.ControllerID); err != nil {
		return ServerRequest{}, err
	}
	headers, err := ifMatchHeaders(o.IfMatch)
	if err != nil {
		return ServerRequest{}, err
	}
	body := map[string]any{"command": command}
	if params != nil {
		body["params"] = params
	}
	if o.ControllerID != "" {
		body["controllerId"] = o.ControllerID
	}
	return ServerRequest{Method: "POST", Path: fmt.Sprintf("/api/robot/%d/command", robotID), Body: body, Headers: headers}, nil
}

func finiteNumber(value float64, name string) error {
	if math.IsNaN(value) || math.IsInf(value, 0) {
		return &ServerRequestError{name + " must be a number"}
	}
	return nil
}

// TableCommandRequest builds one move of the XY table in one request. The server checks it as a whole
// against the limits of the robot's model and applies all of it or none.
func TableCommandRequest(robotID int, x, y float64, o TableOptions) (ServerRequest, error) {
	mode := o.Mode
	if mode == "" {
		mode = "absolute"
	}
	if mode != "absolute" && mode != "relative" {
		return ServerRequest{}, &ServerRequestError{"mode must be \"absolute\" or \"relative\""}
	}
	for name, value := range map[string]float64{"x": x, "y": y} {
		if err := finiteNumber(value, name); err != nil {
			return ServerRequest{}, err
		}
	}
	params := map[string]any{"x": x, "y": y, "mode": mode}
	if o.RZ != nil {
		if err := finiteNumber(*o.RZ, "rz"); err != nil {
			return ServerRequest{}, err
		}
		params["rz"] = *o.RZ
	}
	return CommandRequestWith(robotID, "table", params, CommandOptions{ControllerID: o.ControllerID, IfMatch: o.IfMatch})
}

// GetRobotRequest builds GET /api/robot/{id}.
func GetRobotRequest(robotID int) ServerRequest {
	return ServerRequest{Method: "GET", Path: fmt.Sprintf("/api/robot/%d", robotID)}
}

// AuditRequest builds GET /api/audit (administrators).
func AuditRequest(q AuditQuery) (ServerRequest, error) {
	var parts []string
	if q.Limit != nil {
		parts = append(parts, fmt.Sprintf("limit=%d", *q.Limit))
	}
	if q.AfterSeq != nil {
		parts = append(parts, fmt.Sprintf("afterSeq=%d", *q.AfterSeq))
	}
	if q.Type != "" {
		if !auditTypePattern.MatchString(q.Type) {
			return ServerRequest{}, &ServerRequestError{"type must be a short plain name"}
		}
		parts = append(parts, "type="+q.Type)
	}
	if q.RobotID != nil {
		parts = append(parts, fmt.Sprintf("robotId=%d", *q.RobotID))
	}
	if q.Verify {
		parts = append(parts, "verify=1")
	}
	path := "/api/audit"
	if len(parts) > 0 {
		path += "?" + strings.Join(parts, "&")
	}
	return ServerRequest{Method: "GET", Path: path}, nil
}

// ParseRobot decodes GET /api/robot/{id}; the answer must carry a revision.
func ParseRobot(body []byte) (RobotView, error) {
	var view RobotView
	if err := json.Unmarshal(body, &view); err != nil {
		return RobotView{}, &ServerRequestError{"robot answer is not a JSON object"}
	}
	if view.Revision == "" {
		return RobotView{}, &ServerRequestError{"robot answer has no 'revision'"}
	}
	if view.Robot == nil {
		return RobotView{}, &ServerRequestError{"robot must be a JSON object"}
	}
	return view, nil
}

// ParseCommandResult decodes the answer of command.
func ParseCommandResult(body []byte) (CommandResult, error) {
	var result CommandResult
	if err := json.Unmarshal(body, &result); err != nil {
		return CommandResult{}, &ServerRequestError{"command answer is not a JSON object"}
	}
	return result, nil
}

// ParseAudit decodes GET /api/audit.
func ParseAudit(body []byte) (AuditView, error) {
	var view AuditView
	if err := json.Unmarshal(body, &view); err != nil {
		return AuditView{}, &ServerRequestError{"audit answer is not a JSON object"}
	}
	return view, nil
}

// ParseClaimsEvent decodes the `claims` message of the WebSocket (sent to the clients that opened /ws
// with ?remoteApiVersion=2): the same list as GET /api/claims. ok is false for any other message.
func ParseClaimsEvent(message []byte) (claims []ClaimEntry, ok bool, err error) {
	var head struct {
		Type string `json:"type"`
	}
	if json.Unmarshal(message, &head) != nil || head.Type != "claims" {
		return nil, false, nil
	}
	claims, err = ParseClaims(message)
	return claims, err == nil, err
}

// Robot calls GET /api/robot/{id}: the robot with its revision, to send back as IfMatch.
func (c *ServerClient) Robot(robotID int) (RobotView, error) {
	raw, err := c.send(GetRobotRequest(robotID))
	if err != nil {
		return RobotView{}, err
	}
	return ParseRobot(raw)
}

// CommandWith calls POST /api/robot/{id}/command and returns the raw answer.
func (c *ServerClient) CommandWith(robotID int, command string, params map[string]any, o CommandOptions) ([]byte, error) {
	o.ControllerID = c.controllerFor(o.ControllerID)
	request, err := CommandRequestWith(robotID, command, params, o)
	if err != nil {
		return nil, err
	}
	return c.send(request)
}

// MoveTable moves the XY table of a robot in one request.
func (c *ServerClient) MoveTable(robotID int, x, y float64, o TableOptions) (CommandResult, error) {
	o.ControllerID = c.controllerFor(o.ControllerID)
	request, err := TableCommandRequest(robotID, x, y, o)
	if err != nil {
		return CommandResult{}, err
	}
	raw, err := c.send(request)
	if err != nil {
		return CommandResult{}, err
	}
	return ParseCommandResult(raw)
}

// Audit calls GET /api/audit (administrators).
func (c *ServerClient) Audit(q AuditQuery) (AuditView, error) {
	request, err := AuditRequest(q)
	if err != nil {
		return AuditView{}, err
	}
	raw, err := c.send(request)
	if err != nil {
		return AuditView{}, err
	}
	return ParseAudit(raw)
}
