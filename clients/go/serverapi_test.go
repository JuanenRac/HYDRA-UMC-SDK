// =============================================================================
// HYDRA-UMC-SDK - Go tests: claim, jog arming and safety-limit client
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

type serverCases struct {
	Requests []struct {
		Name   string         `json:"name"`
		Call   string         `json:"call"`
		Args   map[string]any `json:"args"`
		Expect struct {
			Method string         `json:"method"`
			Path   string         `json:"path"`
			Body   map[string]any `json:"body"`
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
			Kind           string  `json:"kind"`
			Code           *string `json:"code"`
			HasReservation bool    `json:"hasReservation"`
		} `json:"expect"`
	} `json:"errors"`
	Responses map[string]json.RawMessage `json:"responses"`
}

func loadServerCases(t *testing.T) serverCases {
	t.Helper()
	raw, err := os.ReadFile(filepath.Join("..", "..", "conformance", "server-routes", "cases.json"))
	if err != nil {
		t.Fatalf("cannot read the server route cases: %v", err)
	}
	var cases serverCases
	if err := json.Unmarshal(raw, &cases); err != nil {
		t.Fatalf("cannot decode the server route cases: %v", err)
	}
	return cases
}

func argString(args map[string]any, key string) string {
	if v, ok := args[key].(string); ok {
		return v
	}
	return ""
}

func argStringPtr(args map[string]any, key string) *string {
	if v, ok := args[key].(string); ok {
		return &v
	}
	return nil
}

func argFloatPtr(args map[string]any, key string) *float64 {
	if v, ok := args[key].(float64); ok {
		return &v
	}
	return nil
}

func argInt(args map[string]any, key string) int {
	v, _ := args[key].(float64)
	return int(v)
}

func buildServerRequest(call string, args map[string]any) (ServerRequest, error) {
	controller := argString(args, "controllerId")
	robot := argInt(args, "robotId")
	switch call {
	case "claim":
		options := ClaimOptions{TTLMs: argFloatPtr(args, "ttlMs"), Reason: argStringPtr(args, "reason"), ControllerID: controller}
		if v, ok := args["force"].(bool); ok {
			options.Force = &v
		}
		return ClaimRequest(robot, options)
	case "release":
		return ReleaseRequest(robot, argStringPtr(args, "reason"), controller)
	case "jogArm":
		armed, _ := args["armed"].(bool)
		return JogArmRequest(robot, armed, argFloatPtr(args, "ttlMs"), controller)
	case "listClaims":
		return ListClaimsRequest(), nil
	case "getSafetyLimits":
		if _, ok := args["robotId"]; ok {
			return SafetyLimitsRequest(&robot), nil
		}
		return SafetyLimitsRequest(nil), nil
	case "updateSafetyLimits":
		patch, _ := args["patch"].(map[string]any)
		return UpdateSafetyLimitsRequest(patch)
	case "command":
		params, _ := args["params"].(map[string]any)
		return CommandRequest(robot, argString(args, "command"), params, controller)
	}
	panic("unknown call " + call)
}

func TestServerRequestCases(t *testing.T) {
	for _, c := range loadServerCases(t).Requests {
		t.Run(c.Name, func(t *testing.T) {
			request, err := buildServerRequest(c.Call, c.Args)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if request.Method != c.Expect.Method || request.Path != c.Expect.Path {
				t.Fatalf("got %s %s, want %s %s", request.Method, request.Path, c.Expect.Method, c.Expect.Path)
			}
			if !reflect.DeepEqual(normalize(request.Body), normalize(c.Expect.Body)) {
				t.Fatalf("got body %v, want %v", request.Body, c.Expect.Body)
			}
		})
	}
}

// normalize round-trips through JSON so int and float64 numbers compare equal.
func normalize(value map[string]any) any {
	if value == nil {
		return nil
	}
	raw, _ := json.Marshal(value)
	var out any
	_ = json.Unmarshal(raw, &out)
	return out
}

func TestServerInvalidRequestsAreRefusedBeforeSending(t *testing.T) {
	for _, c := range loadServerCases(t).InvalidRequests {
		t.Run(c.Name, func(t *testing.T) {
			if id, present := c.Args["controllerId"].(string); present && id == "" {
				t.Skip("in Go the empty controller id is the zero value and means: not sent")
			}
			_, err := buildServerRequest(c.Call, c.Args)
			var refused *ServerRequestError
			if !errors.As(err, &refused) {
				t.Fatalf("expected a ServerRequestError, got %v", err)
			}
		})
	}
}

func TestServerErrorCases(t *testing.T) {
	for _, c := range loadServerCases(t).Errors {
		t.Run(c.Name, func(t *testing.T) {
			body := []byte(c.Body)
			if string(body) == "null" {
				body = nil
			}
			err := ParseAPIError(c.Status, body)
			var kind string
			var reservation *Reservation
			switch typed := err.(type) {
			case *ControllerIDRequiredError:
				kind, reservation = "controller-id-required", typed.Reservation
			case *ClaimConflictError:
				kind, reservation = "claim-conflict", typed.Reservation
			case *InvalidControllerIDError:
				kind = "invalid-controller-id"
			case *JogNotArmedError:
				kind = "jog-not-armed"
			case *APIError:
				kind = "api-error"
			default:
				t.Fatalf("unexpected type %T", err)
			}
			if kind != c.Expect.Kind {
				t.Fatalf("kind %s, want %s", kind, c.Expect.Kind)
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
			if (reservation != nil) != c.Expect.HasReservation {
				t.Fatalf("reservation present = %v, want %v", reservation != nil, c.Expect.HasReservation)
			}
		})
	}
}

func TestControllerRequiredIsAlsoAClaimConflict(t *testing.T) {
	err := ParseAPIError(409, []byte(`{"error":"x","code":"controller-id-required"}`))
	var conflict *ClaimConflictError
	if !errors.As(err, &conflict) {
		t.Fatal("a controller-required error must also be a claim conflict")
	}
}

func TestServerResponses(t *testing.T) {
	cases := loadServerCases(t)
	claim, err := ParseClaimResult(cases.Responses["claim"])
	if err != nil || claim.Reservation == nil || *claim.Reservation.ControllerID != "tab-1" || claim.History[0]["action"] != "claimed" {
		t.Fatalf("claim result: %+v %v", claim, err)
	}
	released, _ := ParseClaimResult([]byte(`{"success":true,"reservation":null}`))
	if released.Reservation != nil {
		t.Fatal("a release has no reservation")
	}
	on, err := ParseJogArmResult(cases.Responses["jogArmOn"])
	if err != nil || !on.Armed || on.TTLMs == nil || *on.TTLMs != 30000 {
		t.Fatalf("jog arm on: %+v %v", on, err)
	}
	off, _ := ParseJogArmResult(cases.Responses["jogArmOff"])
	if off.Armed || off.ExpiresAt != nil {
		t.Fatalf("jog arm off: %+v", off)
	}
	if _, err := ParseJogArmResult([]byte(`{"success":true}`)); err == nil {
		t.Fatal("an answer without armed must be refused")
	}
	claims, err := ParseClaims(cases.Responses["claims"])
	if err != nil || len(claims) != 2 || claims[0].RobotID != 1 || claims[1].ControllerID != nil || claims[1].RobotName != nil {
		t.Fatalf("claims: %+v %v", claims, err)
	}
	view, err := ParseSafetyLimits(cases.Responses["safetyLimits"])
	if err != nil || view.Robot == nil || *view.Robot.JogArmedUntil != 31000 || *view.Robot.Model != "Parol6 (6-DOF)" {
		t.Fatalf("safety limits: %+v %v", view, err)
	}
}

func TestServerClientOverHTTP(t *testing.T) {
	cases := loadServerCases(t)
	var seen struct {
		path, auth, method string
		body               map[string]any
	}
	status := 200
	answer := []byte(cases.Responses["claim"])
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		seen.path, seen.auth, seen.method = r.URL.RequestURI(), r.Header.Get("Authorization"), r.Method
		raw, _ := io.ReadAll(r.Body)
		seen.body = nil
		_ = json.Unmarshal(raw, &seen.body)
		w.WriteHeader(status)
		_, _ = w.Write(answer)
	}))
	defer server.Close()

	client, err := NewServerClient(server.URL+"/", "tok", "tab-1")
	if err != nil {
		t.Fatal(err)
	}
	ttl := 1000.0
	result, err := client.Claim(1, ClaimOptions{TTLMs: &ttl})
	if err != nil || result.Reservation.OwnerUsername != "alice" {
		t.Fatalf("claim: %+v %v", result, err)
	}
	if seen.path != "/api/robot/1/claim" || seen.auth != "Bearer tok" || seen.body["controllerId"] != "tab-1" || seen.body["ttlMs"] != 1000.0 {
		t.Fatalf("request seen by the server: %+v", seen)
	}

	if _, err := client.Release(1, nil, "tab-2"); err != nil || seen.body["controllerId"] != "tab-2" {
		t.Fatalf("the controller id of a call must win: %+v %v", seen, err)
	}

	status, answer = 409, []byte(`{"error":"robot is already claimed by alice","code":"other-controller","reservation":{"ownerUsername":"alice"}}`)
	_, err = client.Claim(1, ClaimOptions{})
	var conflict *ClaimConflictError
	if !errors.As(err, &conflict) || conflict.Code != CodeOtherController || conflict.Reservation == nil {
		t.Fatalf("expected a claim conflict, got %v", err)
	}

	status, answer = 403, []byte(`{"error":"not armed","code":"jog-not-armed"}`)
	_, err = client.Command(1, "jog", map[string]any{"axis": "x", "amount": 1.0}, "")
	var unarmed *JogNotArmedError
	if !errors.As(err, &unarmed) {
		t.Fatalf("expected JogNotArmedError, got %v", err)
	}

	status, answer = 502, []byte("bad gateway")
	if _, err = client.ListClaims(); err == nil {
		t.Fatal("a 502 must be an error")
	} else if apiError, ok := AsAPIError(err); !ok || apiError.Status != 502 {
		t.Fatalf("expected an APIError with status 502, got %v", err)
	}
}

func TestNewServerClientRefusesABadControllerID(t *testing.T) {
	if _, err := NewServerClient("http://x", "", "no good"); err == nil {
		t.Fatal("a malformed default controller id must be refused")
	}
}
