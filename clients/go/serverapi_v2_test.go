// =============================================================================
// HYDRA-UMC-SDK - Go tests: blocks 2 to 5 of the second server contract
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

package hydraumc

import (
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

type serverCasesV2 struct {
	Requests []struct {
		Name   string         `json:"name"`
		Call   string         `json:"call"`
		Args   map[string]any `json:"args"`
		Expect struct {
			Method  string            `json:"method"`
			Path    string            `json:"path"`
			Body    map[string]any    `json:"body"`
			Headers map[string]string `json:"headers"`
		} `json:"expect"`
	} `json:"requests"`
	InvalidRequests []struct {
		Name string         `json:"name"`
		Call string         `json:"call"`
		Args map[string]any `json:"args"`
	} `json:"invalidRequests"`
	Errors []struct {
		Name   string          `json:"name"`
		Status int             `json:"status"`
		Body   json.RawMessage `json:"body"`
		Expect struct {
			Kind     string  `json:"kind"`
			Code     *string `json:"code"`
			Revision *string `json:"revision"`
		} `json:"expect"`
	} `json:"errors"`
	Responses map[string]json.RawMessage `json:"responses"`
}

func loadServerCasesV2(t *testing.T) serverCasesV2 {
	t.Helper()
	raw, err := os.ReadFile(filepath.Join("..", "..", "conformance", "server-routes", "cases_v2.json"))
	if err != nil {
		t.Fatalf("cannot read the v2 server route cases: %v", err)
	}
	var cases serverCasesV2
	if err := json.Unmarshal(raw, &cases); err != nil {
		t.Fatalf("cannot decode the v2 server route cases: %v", err)
	}
	return cases
}

func buildV2(call string, args map[string]any) (ServerRequest, error) {
	controller := argString(args, "controllerId")
	ifMatch := argString(args, "ifMatch")
	robot := argInt(args, "robotId")
	if v, present := args["robotId"]; present {
		if _, isNumber := v.(float64); !isNumber {
			return ServerRequest{}, &ServerRequestError{"robot_id must be an integer"}
		}
	}
	switch call {
	case "getRobot":
		return GetRobotRequest(robot), nil
	case "claim":
		return ClaimRequest(robot, ClaimOptions{ControllerID: controller, IfMatch: ifMatch})
	case "release":
		return ReleaseRequestWith(robot, ReleaseOptions{ControllerID: controller, IfMatch: ifMatch})
	case "command":
		params, _ := args["params"].(map[string]any)
		return CommandRequestWith(robot, argString(args, "command"), params, CommandOptions{ControllerID: controller, IfMatch: ifMatch})
	case "table":
		x, _ := args["x"].(float64)
		y, _ := args["y"].(float64)
		if _, ok := args["x"].(float64); !ok {
			return ServerRequest{}, &ServerRequestError{"x must be a number"}
		}
		return TableCommandRequest(robot, x, y, TableOptions{RZ: argFloatPtr(args, "rz"), Mode: argString(args, "mode"), ControllerID: controller, IfMatch: ifMatch})
	case "audit":
		q := AuditQuery{Type: argString(args, "type")}
		if v, ok := args["limit"].(float64); ok {
			n := int(v)
			q.Limit = &n
		}
		if v, ok := args["afterSeq"].(float64); ok {
			n := int(v)
			q.AfterSeq = &n
		}
		if _, ok := args["robotId"]; ok {
			q.RobotID = &robot
		}
		q.Verify, _ = args["verify"].(bool)
		return AuditRequest(q)
	}
	panic("unknown call " + call)
}

func TestServerV2RequestCases(t *testing.T) {
	for _, c := range loadServerCasesV2(t).Requests {
		t.Run(c.Name, func(t *testing.T) {
			request, err := buildV2(c.Call, c.Args)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if request.Method != c.Expect.Method || request.Path != c.Expect.Path {
				t.Fatalf("got %s %s, want %s %s", request.Method, request.Path, c.Expect.Method, c.Expect.Path)
			}
			if !reflect.DeepEqual(normalize(request.Body), normalize(c.Expect.Body)) {
				t.Fatalf("got body %v, want %v", request.Body, c.Expect.Body)
			}
			got := request.Headers
			if got == nil {
				got = map[string]string{}
			}
			if !reflect.DeepEqual(got, c.Expect.Headers) {
				t.Fatalf("got headers %v, want %v", got, c.Expect.Headers)
			}
		})
	}
}

func TestServerV2InvalidRequestsAreRefusedBeforeSending(t *testing.T) {
	for _, c := range loadServerCasesV2(t).InvalidRequests {
		t.Run(c.Name, func(t *testing.T) {
			_, err := buildV2(c.Call, c.Args)
			var refused *ServerRequestError
			if !errors.As(err, &refused) {
				t.Fatalf("expected a ServerRequestError, got %v", err)
			}
		})
	}
}

func TestServerV2ErrorCases(t *testing.T) {
	for _, c := range loadServerCasesV2(t).Errors {
		t.Run(c.Name, func(t *testing.T) {
			err := ParseAPIError(c.Status, []byte(c.Body))
			var kind, revision string
			switch typed := err.(type) {
			case *RevisionMismatchError:
				kind, revision = "revision-mismatch", typed.Revision
			case *TableMoveError:
				kind = "table-move"
			default:
				t.Fatalf("unexpected type %T", err)
			}
			if kind != c.Expect.Kind {
				t.Fatalf("kind %s, want %s", kind, c.Expect.Kind)
			}
			wantRevision := ""
			if c.Expect.Revision != nil {
				wantRevision = *c.Expect.Revision
			}
			if revision != wantRevision {
				t.Fatalf("revision %q, want %q", revision, wantRevision)
			}
			apiError, ok := AsAPIError(err)
			if !ok || apiError.Status != c.Status {
				t.Fatalf("every typed error must unwrap to an APIError with the status")
			}
			wantCode := ""
			if c.Expect.Code != nil {
				wantCode = *c.Expect.Code
			}
			if apiError.Code != wantCode {
				t.Fatalf("code %q, want %q", apiError.Code, wantCode)
			}
		})
	}
}

func TestServerV2Responses(t *testing.T) {
	cases := loadServerCasesV2(t)
	robot, err := ParseRobot(cases.Responses["robot"])
	if err != nil || robot.Revision != "0123456789abcdef" || robot.Robot["name"] != "B" || string(robot.CellID) != `"c1"` {
		t.Fatalf("robot: %+v %v", robot, err)
	}
	if _, err := ParseRobot([]byte(`{"robot":{}}`)); err == nil {
		t.Fatal("a robot answer without a revision must be refused")
	}
	plain, err := ParseCommandResult(cases.Responses["commandPlain"])
	if err != nil || !plain.Success || plain.Revision != "fedcba9876543210" || plain.Applied != nil {
		t.Fatalf("plain: %+v %v", plain, err)
	}
	table, err := ParseCommandResult(cases.Responses["commandTable"])
	if err != nil || table.Applied == nil || table.Applied.X != 40 || table.Applied.Y != 65 || table.Applied.RZ == nil || *table.Applied.RZ != 15 {
		t.Fatalf("table: %+v %v", table, err)
	}
	claim, err := ParseClaimResult(cases.Responses["claimWithRevision"])
	if err != nil || claim.Revision != "0123456789abcdef" {
		t.Fatalf("claim: %+v %v", claim, err)
	}
	audit, err := ParseAudit(cases.Responses["audit"])
	if err != nil || !audit.Enabled || audit.LockedOff || len(audit.Entries) != 2 {
		t.Fatalf("audit: %+v %v", audit, err)
	}
	if audit.Entries[0].ControllerID == nil || *audit.Entries[0].ControllerID != "tab-1" || audit.Entries[0].Detail["action"] != "claimed" || audit.Entries[1].Username != nil {
		t.Fatalf("audit entries: %+v", audit.Entries)
	}
	if audit.Verification["entries"] != float64(2) {
		t.Fatalf("verification: %v", audit.Verification)
	}
	claims, ok, err := ParseClaimsEvent(cases.Responses["claimsEvent"])
	if err != nil || !ok || len(claims) != 2 || claims[0].JogArmedUntil == nil || *claims[0].JogArmedUntil != 31000 || claims[1].JogArmedUntil != nil {
		t.Fatalf("claims event: %+v %v %v", claims, ok, err)
	}
	if _, ok, _ := ParseClaimsEvent(cases.Responses["otherMessage"]); ok {
		t.Fatal("another message is not a claims event")
	}
	if _, ok, _ := ParseClaimsEvent([]byte("not a message")); ok {
		t.Fatal("garbage is not a claims event")
	}
}

func TestServerV2ClientSendsTheRevisionBack(t *testing.T) {
	cases := loadServerCasesV2(t)
	var seenHeader, seenPath, seenBody string
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/api/robot/3" {
			_, _ = w.Write(cases.Responses["robot"])
			return
		}
		seenHeader, seenPath = r.Header.Get("If-Match"), r.URL.Path
		raw, _ := io.ReadAll(r.Body)
		seenBody = string(raw)
		_, _ = w.Write(cases.Responses["commandTable"])
	}))
	defer server.Close()
	client, err := NewServerClient(server.URL, "tok", "tab-1")
	if err != nil {
		t.Fatal(err)
	}
	view, err := client.Robot(3)
	if err != nil {
		t.Fatal(err)
	}
	rz := 15.0
	result, err := client.MoveTable(3, 40, 65, TableOptions{RZ: &rz, IfMatch: view.Revision})
	if err != nil || result.Applied == nil || result.Applied.RobotID != 1 {
		t.Fatalf("move: %+v %v", result, err)
	}
	if seenHeader != `"0123456789abcdef"` || seenPath != "/api/robot/3/command" {
		t.Fatalf("header %q path %q", seenHeader, seenPath)
	}
	var body struct {
		Params       map[string]any `json:"params"`
		ControllerID string         `json:"controllerId"`
	}
	if err := json.Unmarshal([]byte(seenBody), &body); err != nil || body.ControllerID != "tab-1" || body.Params["mode"] != "absolute" || body.Params["rz"] != float64(15) {
		t.Fatalf("body %s %v", seenBody, err)
	}
}

func TestServerV2StaleRevisionAndRefusedTableMove(t *testing.T) {
	cases := loadServerCasesV2(t)
	status := 412
	body := []byte(nil)
	for _, c := range cases.Errors {
		if c.Name == "revision-mismatch" {
			status, body = c.Status, []byte(c.Body)
		}
	}
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(status)
		_, _ = w.Write(body)
	}))
	defer server.Close()
	client, _ := NewServerClient(server.URL, "tok", "")
	_, err := client.CommandWith(1, "jog", map[string]any{"axis": "x", "amount": 1}, CommandOptions{IfMatch: "old"})
	var stale *RevisionMismatchError
	if !errors.As(err, &stale) || stale.Revision != "0123456789abcdef" {
		t.Fatalf("expected a RevisionMismatchError with the current revision, got %v", err)
	}
	if _, err := client.ReleaseWith(1, ReleaseOptions{IfMatch: "old"}); !errors.As(err, &stale) {
		t.Fatalf("release must report a stale revision too: %v", err)
	}
}
