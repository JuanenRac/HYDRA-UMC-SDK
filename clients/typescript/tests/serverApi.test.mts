// =============================================================================
// HYDRA-UMC-SDK - TypeScript tests: claim, jog arming and safety-limit client
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

import assert from "node:assert/strict";
import * as fs from "node:fs";
import * as path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import * as api from "../dist/index.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const CASES = JSON.parse(fs.readFileSync(path.resolve(here, "..", "..", "..", "conformance", "server-routes", "cases.json"), "utf-8"));

type Args = Record<string, any>;

function build(call: string, a: Args): api.ServerRequest {
  switch (call) {
    case "claim":
      return api.claimRequest(a.robotId, { ttlMs: a.ttlMs, force: a.force, reason: a.reason, controllerId: a.controllerId });
    case "release":
      return api.releaseRequest(a.robotId, { reason: a.reason, controllerId: a.controllerId });
    case "jogArm":
      return api.jogArmRequest(a.robotId, a.armed, { ttlMs: a.ttlMs, controllerId: a.controllerId });
    case "listClaims":
      return api.listClaimsRequest();
    case "getSafetyLimits":
      return api.safetyLimitsRequest(a.robotId);
    case "updateSafetyLimits":
      return api.updateSafetyLimitsRequest(a.patch);
    case "command":
      return api.commandRequest(a.robotId, a.command, { params: a.params, controllerId: a.controllerId });
  }
  throw new Error(`unknown call ${call}`);
}

const KIND: Record<string, Function> = {
  "claim-conflict": api.ClaimConflictError,
  "controller-id-required": api.ControllerIdRequiredError,
  "invalid-controller-id": api.InvalidControllerIdError,
  "jog-not-armed": api.JogNotArmedError,
  "api-error": api.ApiError,
};

for (const c of CASES.requests) {
  test(`request case ${c.name}`, () => {
    const request = build(c.call, c.args);
    assert.equal(request.method, c.expect.method);
    assert.equal(request.path, c.expect.path);
    assert.deepEqual(request.body, c.expect.body);
  });
}

for (const c of CASES.invalidRequests) {
  test(`invalid request ${c.name} is refused before sending`, () => {
    assert.throws(() => build(c.call, c.args), api.ServerRequestError);
  });
}

test("a robot id must be an integer and armed a boolean", () => {
  assert.throws(() => api.claimRequest(1.5), api.ServerRequestError);
  assert.throws(() => api.claimRequest("1" as unknown as number), api.ServerRequestError);
  assert.throws(() => api.jogArmRequest(1, "yes" as unknown as boolean), api.ServerRequestError);
});

test("a request without a controller id is the v1 request", () => {
  assert.equal("controllerId" in (api.commandRequest(1, "jog", { params: { axis: "x", amount: 1 } }).body ?? {}), false);
});

for (const c of CASES.errors) {
  test(`error case ${c.name}`, () => {
    const error = api.parseApiError(c.status, c.body);
    assert.equal(error.constructor, KIND[c.expect.kind]);
    assert.equal(error.status, c.status);
    assert.equal(error.code, c.expect.code);
    const reservation = (error as api.ClaimConflictError).reservation;
    assert.equal(reservation !== undefined && reservation !== null, c.expect.hasReservation);
  });
}

test("a controller-required error is also a claim conflict and an api error", () => {
  const error = api.parseApiError(409, { error: "x", code: "controller-id-required" });
  assert.ok(error instanceof api.ClaimConflictError);
  assert.ok(error instanceof api.ApiError);
  assert.ok(error instanceof Error);
});

test("responses", () => {
  const claim = api.parseClaimResult(CASES.responses.claim);
  assert.equal(claim.reservation?.controllerId, "tab-1");
  assert.equal(claim.history[0]?.action, "claimed");
  assert.equal(api.parseClaimResult({ success: true, reservation: null }).reservation, null);

  const on = api.parseJogArmResult(CASES.responses.jogArmOn);
  assert.equal(on.armed, true);
  assert.equal(on.ttlMs, 30000);
  const off = api.parseJogArmResult(CASES.responses.jogArmOff);
  assert.equal(off.expiresAt, null);
  assert.throws(() => api.parseJogArmResult({ success: true }), api.ServerRequestError);

  const claims = api.parseClaims(CASES.responses.claims);
  assert.deepEqual(claims.map((e) => e.robotId), [1, 2]);
  assert.equal(claims[0]?.controllerId, "tab-1");
  assert.equal(claims[1]?.controllerId, null);
  assert.equal(claims[1]?.robotName, null);

  const view = api.parseSafetyLimits(CASES.responses.safetyLimits);
  assert.equal(view.robot?.jogArmedUntil, 31000);
  assert.equal(view.robot?.model, "Parol6 (6-DOF)");
  assert.equal((view.hardLimits.armTtlMs as { max: number }).max, 600000);
  assert.equal(api.parseJogArmResult({ ...CASES.responses.jogArmOn, futureField: 1 }).armed, true);
});

function fakeTransport(status: number, body: unknown) {
  const sent: Array<{ method: string; url: string; headers: Record<string, string>; body: string | null }> = [];
  const transport: api.Transport = async (method, url, headers, data) => {
    sent.push({ method, url, headers, body: data });
    return { status, text: body === null ? "not json" : JSON.stringify(body) };
  };
  return { sent, transport };
}

test("the client sends the token and the default controller id", async () => {
  const { sent, transport } = fakeTransport(200, CASES.responses.claim);
  const client = new api.HydraServerClient("http://hydra.local:3000/", { token: "tok", controllerId: "tab-1", transport });
  const result = await client.claim(1, { ttlMs: 1000 });
  assert.equal(sent[0]?.url, "http://hydra.local:3000/api/robot/1/claim");
  assert.equal(sent[0]?.headers.Authorization, "Bearer tok");
  assert.deepEqual(JSON.parse(sent[0]?.body ?? "null"), { ttlMs: 1000, controllerId: "tab-1" });
  assert.equal(result.reservation?.ownerUsername, "alice");
});

test("the controller id of a call wins over the default", async () => {
  const { sent, transport } = fakeTransport(200, CASES.responses.claim);
  await new api.HydraServerClient("http://x", { controllerId: "tab-1", transport }).release(1, { controllerId: "tab-2" });
  assert.equal(JSON.parse(sent[0]?.body ?? "null").controllerId, "tab-2");
});

test("a conflict, an unarmed jog and a non-JSON failure raise typed errors", async () => {
  const conflict = CASES.errors.find((c: Args) => c.name === "other-account");
  await assert.rejects(new api.HydraServerClient("http://x", { transport: fakeTransport(conflict.status, conflict.body).transport }).claim(1), api.ClaimConflictError);
  const unarmed = CASES.errors.find((c: Args) => c.name === "jog-not-armed");
  await assert.rejects(
    new api.HydraServerClient("http://x", { transport: fakeTransport(unarmed.status, unarmed.body).transport }).command(1, "jog", { params: { axis: "x", amount: 1 } }),
    api.JogNotArmedError,
  );
  await assert.rejects(new api.HydraServerClient("http://x", { transport: fakeTransport(502, null).transport }).listClaims(), (error: api.ApiError) => error.status === 502);
});

test("an invalid default controller id is refused", () => {
  assert.throws(() => new api.HydraServerClient("http://x", { controllerId: "no good" }), api.ServerRequestError);
});
