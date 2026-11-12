// =============================================================================
// HYDRA-UMC-SDK - Go tests: edges of the server client (every call, every refusal, every cut)
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

package hydraumc

import (
	"encoding/json"
	"errors"
	"io"
	"math"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

type edgeSeen struct {
	method, path, auth, ifMatch string
	body                        map[string]any
}

// edgeServer answers every request with the status and body in *answer and records the last request.
func edgeServer(t *testing.T, status *int, answer *string) (*ServerClient, *edgeSeen) {
	t.Helper()
	seen := &edgeSeen{}
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		seen.method, seen.path, seen.auth, seen.ifMatch = r.Method, r.URL.RequestURI(), r.Header.Get("Authorization"), r.Header.Get("If-Match")
		raw, _ := io.ReadAll(r.Body)
		seen.body = nil
		_ = json.Unmarshal(raw, &seen.body)
		w.WriteHeader(*status)
		_, _ = w.Write([]byte(*answer))
	}))
	t.Cleanup(server.Close)
	client, err := NewServerClient(server.URL, "tok", "edge-1")
	if err != nil {
		t.Fatal(err)
	}
	return client, seen
}

type brokenDoer struct{ err error }

func (b brokenDoer) Do(*http.Request) (*http.Response, error) { return nil, b.err }

type brokenBody struct{}

func (brokenBody) Read([]byte) (int, error) { return 0, errors.New("cut in the middle") }
func (brokenBody) Close() error             { return nil }

type cutBodyDoer struct{}

func (cutBodyDoer) Do(*http.Request) (*http.Response, error) {
	return &http.Response{StatusCode: 200, Body: brokenBody{}, Header: http.Header{}}, nil
}

func TestErrorTextsCarryTheStatusAndTheCode(t *testing.T) {
	plain := ParseAPIError(500, []byte(`not json`))
	if got := plain.Error(); got != "500 HTTP 500" {
		t.Fatalf("plain error text: %q", got)
	}
	coded := ParseAPIError(409, []byte(`{"error":"busy","code":"other-account"}`))
	if got := coded.Error(); !strings.Contains(got, "409 other-account: busy") {
		t.Fatalf("coded error text: %q", got)
	}
	if got := (&ServerRequestError{"nope"}).Error(); got != "nope" {
		t.Fatalf("request error text: %q", got)
	}
	api, ok := AsAPIError(plain)
	if !ok || api.Status != 500 || string(api.Body) != "not json" {
		t.Fatalf("AsAPIError: %v %v", api, ok)
	}
	if _, ok := AsAPIError(errors.New("other")); ok {
		t.Fatal("a foreign error must not be an APIError")
	}
}

func TestEveryCallOfTheClientReachesItsRoute(t *testing.T) {
	status, answer := 200, ""
	client, seen := edgeServer(t, &status, &answer)
	two := 2
	cases := []struct {
		name, answer, method, path string
		call                       func() error
	}{
		{"jog-arm", `{"armed":true,"ttlMs":500}`, "POST", "/api/robot/3/jog-arm", func() error {
			result, err := client.JogArm(3, true, nil, "")
			if err == nil && !result.Armed {
				t.Error("armed must be true")
			}
			return err
		}},
		{"list claims", `{"claims":[]}`, "GET", "/api/claims", func() error { _, err := client.ListClaims(); return err }},
		{"safety limits", `{"limits":{},"defaults":{},"hardLimits":{}}`, "GET", "/api/safety-limits?robotId=2", func() error {
			_, err := client.SafetyLimits(&two)
			return err
		}},
		{"safety limits for all", `{"limits":{},"defaults":{},"hardLimits":{}}`, "GET", "/api/safety-limits", func() error {
			_, err := client.SafetyLimits(nil)
			return err
		}},
		{"update safety limits", `{"limits":{"a":1},"defaults":{},"hardLimits":{}}`, "PUT", "/api/admin/safety-limits", func() error {
			view, err := client.UpdateSafetyLimits(map[string]any{"a": 1})
			if err == nil && view.Limits["a"] == nil {
				t.Error("the limits must come back")
			}
			return err
		}},
		{"robot", `{"robot":{"id":1},"revision":"r1","cellId":null}`, "GET", "/api/robot/1", func() error { _, err := client.Robot(1); return err }},
		{"audit", `{"enabled":true,"lockedOff":false,"entries":[]}`, "GET", "/api/audit?limit=5&type=login", func() error {
			limit := 5
			_, err := client.Audit(AuditQuery{Limit: &limit, Type: "login"})
			return err
		}},
		{"move table", `{"success":true,"revision":"r2"}`, "POST", "/api/robot/4/command", func() error {
			result, err := client.MoveTable(4, 1.5, -2, TableOptions{})
			if err == nil && result.Revision != "r2" {
				t.Error("the new revision must come back")
			}
			return err
		}},
		{"command", `{"success":true}`, "POST", "/api/robot/4/command", func() error {
			_, err := client.Command(4, "stop", nil, "")
			return err
		}},
	}
	for _, c := range cases {
		status, answer = 200, c.answer
		if err := c.call(); err != nil {
			t.Fatalf("%s: %v", c.name, err)
		}
		if seen.method != c.method || seen.path != c.path || seen.auth != "Bearer tok" {
			t.Fatalf("%s: went to %s %s (auth %q)", c.name, seen.method, seen.path, seen.auth)
		}
	}
	// the controller id of the session rides along when the call names none
	status, answer = 200, `{"armed":false}`
	if _, err := client.JogArm(3, false, nil, ""); err != nil || seen.body["controllerId"] != "edge-1" {
		t.Fatalf("the session controller id must be sent: %v %v", err, seen.body)
	}
	if _, err := client.JogArm(3, false, nil, "mine"); err != nil || seen.body["controllerId"] != "mine" {
		t.Fatalf("the controller id of the call wins: %v %v", err, seen.body)
	}
}

func TestEveryCallRefusesWhatItCannotBuildAndSendsNothing(t *testing.T) {
	status, answer := 200, `{}`
	client, seen := edgeServer(t, &status, &answer)
	nan, inf := math.NaN(), math.Inf(1)
	cases := map[string]func() error{
		"update with a nil patch": func() error { _, err := client.UpdateSafetyLimits(nil); return err },
		"jog-arm with a bad id":   func() error { _, err := client.JogArm(1, true, nil, "bad id!"); return err },
		"claim with a bad id":     func() error { _, err := client.Claim(1, ClaimOptions{ControllerID: "bad id!"}); return err },
		"release with a bad revision": func() error {
			_, err := client.ReleaseWith(1, ReleaseOptions{IfMatch: "not\nvalid"})
			return err
		},
		"command with no name":  func() error { _, err := client.Command(1, "", nil, ""); return err },
		"table with NaN":        func() error { _, err := client.MoveTable(1, nan, 0, TableOptions{}); return err },
		"table with infinity":   func() error { _, err := client.MoveTable(1, 0, inf, TableOptions{}); return err },
		"table with a bad mode": func() error { _, err := client.MoveTable(1, 0, 0, TableOptions{Mode: "diagonal"}); return err },
		"table with a bad rz":   func() error { _, err := client.MoveTable(1, 0, 0, TableOptions{RZ: &nan}); return err },
		"audit with a bad type": func() error { _, err := client.Audit(AuditQuery{Type: "a b;c"}); return err },
	}
	for name, call := range cases {
		seen.method = ""
		err := call()
		var refused *ServerRequestError
		if !errors.As(err, &refused) {
			t.Fatalf("%s: want a ServerRequestError, got %v", name, err)
		}
		if seen.method != "" {
			t.Fatalf("%s: a refused request must send nothing", name)
		}
	}
}

func TestTheParsersRefuseWhatIsNotTheirShape(t *testing.T) {
	bad := []byte(`[1,2`)
	if _, err := ParseClaimResult(bad); err == nil {
		t.Error("claim result")
	}
	if _, err := ParseJogArmResult(bad); err == nil {
		t.Error("jog-arm not JSON")
	}
	if _, err := ParseJogArmResult([]byte(`{"armed":"yes"}`)); err == nil {
		t.Error("jog-arm with a text armed")
	}
	if _, err := ParseJogArmResult([]byte(`{}`)); err == nil {
		t.Error("jog-arm without armed")
	}
	if _, err := ParseClaims(bad); err == nil {
		t.Error("claims not JSON")
	}
	if _, err := ParseClaims([]byte(`{"claims":null}`)); err == nil {
		t.Error("claims null")
	}
	if _, err := ParseSafetyLimits(bad); err == nil {
		t.Error("safety limits")
	}
	if _, err := ParseRobot(bad); err == nil {
		t.Error("robot not JSON")
	}
	if _, err := ParseRobot([]byte(`{"robot":{}}`)); err == nil {
		t.Error("robot without revision")
	}
	if _, err := ParseRobot([]byte(`{"revision":"r"}`)); err == nil {
		t.Error("robot without robot")
	}
	if _, err := ParseCommandResult(bad); err == nil {
		t.Error("command result")
	}
	if _, err := ParseAudit(bad); err == nil {
		t.Error("audit")
	}
	if claims, ok, err := ParseClaimsEvent([]byte(`{"type":"other"}`)); ok || err != nil || claims != nil {
		t.Error("another message is not a claims event")
	}
	if _, ok, err := ParseClaimsEvent([]byte(`{"type":"claims"}`)); ok || err == nil {
		t.Error("a claims event without the list is an error")
	}
	if _, ok, err := ParseClaimsEvent([]byte(`nonsense`)); ok || err != nil {
		t.Error("a message that is not JSON is simply not a claims event")
	}
}

func TestTheClientSurvivesTheNetworkAndTheServerFailing(t *testing.T) {
	status, answer := 503, `{"error":"down"}`
	client, _ := edgeServer(t, &status, &answer)
	if _, err := client.ListClaims(); err == nil {
		t.Fatal("a 503 must be an error")
	} else if api, ok := AsAPIError(err); !ok || api.Status != 503 {
		t.Fatalf("a 503 must be an APIError: %v", err)
	}
	// every call turns the error of the server into its own error
	calls := map[string]func() error{
		"claim":   func() error { _, err := client.Claim(1, ClaimOptions{}); return err },
		"release": func() error { _, err := client.Release(1, nil, ""); return err },
		"jog-arm": func() error { _, err := client.JogArm(1, true, nil, ""); return err },
		"limits":  func() error { _, err := client.SafetyLimits(nil); return err },
		"update":  func() error { _, err := client.UpdateSafetyLimits(map[string]any{}); return err },
		"robot":   func() error { _, err := client.Robot(1); return err },
		"command": func() error { _, err := client.CommandWith(1, "x", nil, CommandOptions{}); return err },
		"table":   func() error { _, err := client.MoveTable(1, 0, 0, TableOptions{}); return err },
		"audit":   func() error { _, err := client.Audit(AuditQuery{}); return err },
	}
	for name, call := range calls {
		if err := call(); err == nil {
			t.Fatalf("%s: a 503 must be an error", name)
		}
	}
	// a cut connection and a body that breaks while it is read
	client.HTTP = brokenDoer{errors.New("connection refused")}
	if _, err := client.ListClaims(); err == nil || !strings.Contains(err.Error(), "connection refused") {
		t.Fatalf("a refused connection: %v", err)
	}
	client.HTTP = cutBodyDoer{}
	if _, err := client.ListClaims(); err == nil || !strings.Contains(err.Error(), "cut in the middle") {
		t.Fatalf("a body cut in the middle: %v", err)
	}
	// no Doer at all falls back to the default client; a base URL that is not a URL is an error
	client.HTTP = nil
	client.BaseURL = "http://127.0.0.1:1"
	if _, err := client.ListClaims(); err == nil {
		t.Fatal("nothing listens on port 1")
	}
	client.BaseURL = "http://bad host/"
	if _, err := client.ListClaims(); err == nil {
		t.Fatal("a base URL with a space must be refused")
	}
}

func TestTheAnswersOfTheServerKeepTheirDetail(t *testing.T) {
	status, answer := 200, `{"reservation":{"ownerId":7,"ownerUsername":"ana","claimedAt":1,"expiresAt":2},"reservationHistory":[],"revision":"r9"}`
	client, seen := edgeServer(t, &status, &answer)
	reason := "done"
	result, err := client.Release(2, &reason, "")
	if err != nil || result.Reservation == nil || result.Reservation.OwnerUsername != "ana" || result.Revision != "r9" {
		t.Fatalf("release answer: %v %+v", err, result)
	}
	if seen.body["reason"] != "done" || seen.body["controllerId"] != "edge-1" {
		t.Fatalf("release body: %v", seen.body)
	}
	// a revision for If-Match travels as a header
	if _, err := client.ReleaseWith(2, ReleaseOptions{IfMatch: `"r9"`}); err != nil || seen.ifMatch != `"r9"` {
		t.Fatalf("If-Match: %v %q", err, seen.ifMatch)
	}
	if _, err := client.CommandWith(2, "stop", map[string]any{"a": 1}, CommandOptions{IfMatch: "*"}); err != nil || seen.ifMatch != "*" {
		t.Fatalf("If-Match star: %v %q", err, seen.ifMatch)
	}
	if params, _ := seen.body["params"].(map[string]any); params["a"] != float64(1) {
		t.Fatalf("command params: %v", seen.body)
	}
	// a table move in relative mode with a rotation
	rz := 90.0
	status, answer = 200, `{"success":true,"applied":{"robotId":2,"x":1,"y":2,"rz":90}}`
	moved, err := client.MoveTable(2, 1, 2, TableOptions{Mode: "relative", RZ: &rz})
	if err != nil || moved.Applied == nil || moved.Applied.RZ == nil || *moved.Applied.RZ != 90 {
		t.Fatalf("table answer: %v %+v", err, moved)
	}
	if params, _ := seen.body["params"].(map[string]any); params["mode"] != "relative" || params["rz"] != float64(90) {
		t.Fatalf("table params: %v", seen.body)
	}
}

func TestAuditQueriesCarryEveryFilter(t *testing.T) {
	limit, after, robot := 10, 4, 3
	request, err := AuditRequest(AuditQuery{Limit: &limit, AfterSeq: &after, Type: "login.fail", RobotID: &robot, Verify: true})
	if err != nil {
		t.Fatal(err)
	}
	want := "/api/audit?limit=10&afterSeq=4&type=login.fail&robotId=3&verify=1"
	if request.Path != want {
		t.Fatalf("audit path %q, want %q", request.Path, want)
	}
	plain, _ := AuditRequest(AuditQuery{})
	if plain.Path != "/api/audit" {
		t.Fatalf("audit path without filters: %q", plain.Path)
	}
}

func TestEveryFormOfTheEnvelopesSurvivesADecodeAndAnEncode(t *testing.T) {
	// extra keys are kept and written back, and never override a field the struct names
	var op Operation
	raw := `{"schema_version":"1","operation_id":"o","correlation_id":"c","kind":"k","target":{"kind":"robot","id":"1","note":"x"},` +
		`"status":"queued","requested_at_utc":"2026-01-01T00:00:00Z","updated_at_utc":"2026-01-01T00:00:00Z","params":{},` +
		`"error":{"code":"E","message":"m","hint":"h"},"result":{"run_id":"r","origin":"real","observers_enabled":true,"outcome":"success","lab":1},"future":true}`
	if err := json.Unmarshal([]byte(raw), &op); err != nil {
		t.Fatal(err)
	}
	if op.Target.Extra["note"] == nil || op.Error.Extra["hint"] == nil || op.Result.Extra["lab"] == nil || op.Extra["future"] == nil {
		t.Fatalf("extra keys lost: %+v", op)
	}
	out, err := json.Marshal(op)
	if err != nil {
		t.Fatal(err)
	}
	var back map[string]json.RawMessage
	if err := json.Unmarshal(out, &back); err != nil || back["future"] == nil {
		t.Fatalf("the extra key must come back: %s", out)
	}
	op.Extra = map[string]json.RawMessage{"kind": json.RawMessage(`"hijack"`)}
	out, _ = json.Marshal(op)
	if !strings.Contains(string(out), `"kind":"k"`) || strings.Contains(string(out), "hijack") {
		t.Fatalf("an extra key must not override a named field: %s", out)
	}
	// a document that is not an object is a decode error, for each of the three shapes
	var target Target
	if err := json.Unmarshal([]byte(`[1]`), &target); err == nil {
		t.Error("target from a list")
	}
	var failure OperationError
	if err := json.Unmarshal([]byte(`"x"`), &failure); err == nil {
		t.Error("error from a string")
	}
	var result OperationResult
	if err := json.Unmarshal([]byte(`7`), &result); err == nil {
		t.Error("result from a number")
	}
	// encoding the pieces on their own
	for _, piece := range []any{op.Target, *op.Error, *op.Result} {
		if _, err := json.Marshal(piece); err != nil {
			t.Fatalf("encoding %T: %v", piece, err)
		}
	}
}

func TestTheNativeVersionPatternHasTwoShapesAndNoThird(t *testing.T) {
	var text NativeVersionPattern
	if err := json.Unmarshal([]byte(`"^v[0-9]+"`), &text); err != nil || text.Pattern != "^v[0-9]+" || text.Components != nil {
		t.Fatalf("string form: %v %+v", err, text)
	}
	if out, err := json.Marshal(text); err != nil || string(out) != `"^v[0-9]+"` {
		t.Fatalf("string form back: %v %s", err, out)
	}
	var parts NativeVersionPattern
	if err := json.Unmarshal([]byte(`{"major":"1","minor":"2","patch":"3"}`), &parts); err != nil || parts.Components == nil || parts.Pattern != "" {
		t.Fatalf("object form: %v %+v", err, parts)
	}
	if out, err := json.Marshal(parts); err != nil || !strings.Contains(string(out), `"minor":"2"`) {
		t.Fatalf("object form back: %v %s", err, out)
	}
	var wrong NativeVersionPattern
	for _, document := range []string{`7`, `[1]`, `{"major":1}`} {
		if err := json.Unmarshal([]byte(document), &wrong); err == nil {
			t.Errorf("%s must not be a native version pattern", document)
		}
	}
}

func TestContractValidationNamesTheContractAndKeepsTheCause(t *testing.T) {
	err := Validate("NoSuchContract", map[string]any{})
	var invalid *ContractValidationError
	if !errors.As(err, &invalid) || invalid.Contract != "NoSuchContract" || !strings.Contains(invalid.Error(), "NoSuchContract: unknown contract") {
		t.Fatalf("unknown contract: %v", err)
	}
	if invalid.Unwrap() == nil {
		t.Fatal("the cause must be kept")
	}
	if err := ValidateJSON("Pose", []byte(`{not json`)); err == nil || !strings.Contains(err.Error(), "invalid JSON") {
		t.Fatalf("broken JSON: %v", err)
	}
	if err := ValidateJSON("Pose", []byte(`{}`)); err == nil {
		t.Fatal("an empty pose must fail its schema")
	}
}

func TestTheVendoredManifestIsIntactAndTolerantOfAByteOrderMark(t *testing.T) {
	manifest, err := LoadContractManifest()
	if err != nil || len(manifest.Contracts) == 0 {
		t.Fatalf("manifest: %v", err)
	}
	if err := VerifyContractManifest(); err != nil {
		t.Fatalf("the vendored schemas must match their digests: %v", err)
	}
}
