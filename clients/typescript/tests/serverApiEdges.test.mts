// =============================================================================
// HYDRA-UMC-SDK - TypeScript tests: edges of the server client (every call, every refusal, every cut)
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

import assert from "node:assert/strict";
import test from "node:test";

import * as api from "../dist/index.js";

type Seen = { method: string; url: string; headers: Record<string, string>; body: string | null };

/** A transport that records the request and answers with what the test sets. */
function double(status: number, text: string) {
  const seen: Seen[] = [];
  const state = { status, text };
  const transport: api.Transport = async (method, url, headers, body) => {
    seen.push({ method, url, headers, body });
    return { status: state.status, text: state.text };
  };
  return { seen, state, transport };
}

test("every call of the client reaches its route with the token and the session controller", async () => {
  const d = double(200, "{}");
  const client = new api.HydraServerClient("http://host:1///", { token: "tok", controllerId: "edge-1", transport: d.transport });
  const calls: Array<[string, string, string, () => Promise<unknown>]> = [
    ["jog-arm", "POST", "/api/robot/3/jog-arm", () => (d.state.text = '{"armed":true}', client.jogArm(3, true))],
    ["claims", "GET", "/api/claims", () => (d.state.text = '{"claims":[]}', client.listClaims())],
    ["limits", "GET", "/api/safety-limits?robotId=2", () => (d.state.text = "{}", client.safetyLimits(2))],
    ["limits all", "GET", "/api/safety-limits", () => client.safetyLimits()],
    ["update limits", "PUT", "/api/admin/safety-limits", () => client.updateSafetyLimits({ a: 1 })],
    ["robot", "GET", "/api/robot/1", () => (d.state.text = '{"robot":{},"revision":"r1"}', client.robot(1))],
    ["audit", "GET", "/api/audit?limit=5", () => (d.state.text = '{"entries":[]}', client.audit({ limit: 5 }))],
    ["table", "POST", "/api/robot/4/command", () => (d.state.text = '{"success":true,"revision":"r2"}', client.moveTable(4, 1, 2))],
    ["command", "POST", "/api/robot/4/command", () => client.command(4, "stop")],
    ["command result", "POST", "/api/robot/4/command", () => client.commandResult(4, "stop")],
    ["release", "POST", "/api/robot/4/release", () => (d.state.text = "{}", client.release(4))],
    ["claim", "POST", "/api/robot/4/claim", () => client.claim(4)],
  ];
  for (const [name, method, path, call] of calls) {
    d.seen.length = 0;
    await call();
    const sent = d.seen[0]!;
    assert.equal(sent.method, method, name);
    assert.equal(sent.url, "http://host:1" + path, name);
    assert.equal(sent.headers.Authorization, "Bearer tok", name);
  }
  d.seen.length = 0;
  d.state.text = '{"armed":false}';
  await client.jogArm(3, false);
  assert.equal(JSON.parse(d.seen[0]!.body as string).controllerId, "edge-1");
  await client.jogArm(3, false, { controllerId: "mine" });
  assert.equal(JSON.parse(d.seen[1]!.body as string).controllerId, "mine");
});

test("an error answer becomes the most specific typed error, whatever the body is", async () => {
  const d = double(503, "<html>down</html>");
  const client = new api.HydraServerClient("http://h", { transport: d.transport });
  await assert.rejects(client.listClaims(), (error: unknown) => error instanceof api.ApiError && error.status === 503);
  d.state.text = "";
  await assert.rejects(client.listClaims(), (error: unknown) => error instanceof api.ApiError && error.status === 503);
  d.state.status = 409;
  d.state.text = JSON.stringify({ error: "busy", code: "other-account", reservation: { ownerId: 1, ownerUsername: "ana", claimedAt: 1, expiresAt: 2 } });
  await assert.rejects(client.claim(1), (error: unknown) => error instanceof api.ClaimConflictError && error.reservation?.ownerUsername === "ana");
  d.state.status = 412;
  d.state.text = JSON.stringify({ revision: "r7" });
  await assert.rejects(client.robot(1), (error: unknown) => error instanceof api.RevisionMismatchError && error.revision === "r7");
});

test("a transport that fails, fails the call and sends nothing twice", async () => {
  const client = new api.HydraServerClient("http://h", {
    transport: async () => {
      throw new Error("connection refused");
    },
  });
  await assert.rejects(client.listClaims(), /connection refused/);
});

test("the default transport asks fetch and hands back the status and the text", async () => {
  const real = globalThis.fetch;
  const asked: Array<{ url: string; init: any }> = [];
  (globalThis as any).fetch = async (url: string, init: object) => {
    asked.push({ url, init });
    return { status: 200, text: async () => '{"claims":[]}' };
  };
  try {
    const client = new api.HydraServerClient("http://h");
    assert.deepEqual(await client.listClaims(), []);
    assert.equal(asked[0]!.url, "http://h/api/claims");
    assert.equal(asked[0]!.init.method, "GET");
  } finally {
    (globalThis as any).fetch = real;
  }
});

test("the parsers refuse what is not their shape and keep what is", () => {
  assert.throws(() => api.parseJogArmResult({}), api.ServerRequestError);
  assert.throws(() => api.parseJogArmResult({ armed: "yes" }), api.ServerRequestError);
  assert.throws(() => api.parseClaims({}), api.ServerRequestError);
  assert.throws(() => api.parseClaims([]), api.ServerRequestError);
  assert.throws(() => api.parseClaims({ claims: [7] }), api.ServerRequestError);
  assert.throws(() => api.parseRobot({ robot: {} }), api.ServerRequestError);
  assert.throws(() => api.parseCommandResult("text"), api.ServerRequestError);
  assert.throws(() => api.parseAudit(null), api.ServerRequestError);
  assert.throws(() => api.parseSafetyLimits([]), api.ServerRequestError);
  const view = api.parseSafetyLimits({ limits: {}, robot: { id: 2, model: "m", jog: {}, temperature: {}, jogArmedUntil: 5 } });
  assert.equal(view.robot?.id, 2);
  assert.equal(view.robot?.jogArmedUntil, 5);
  assert.equal(api.parseSafetyLimits({}).robot, null);
  const result = api.parseCommandResult({ success: true, applied: { robotId: 1, x: 1, y: 2, rz: 3 }, warnings: [{ a: 1 }, 7, [1], null] });
  assert.equal(result.applied?.rz, 3);
  assert.equal(result.warnings.length, 1);
  assert.equal(api.parseCommandResult({}).applied, null);
  const audit = api.parseAudit({ entries: [{ seq: 1, detail: [1], username: 5 }], verification: [1] });
  assert.equal(audit.entries[0]!.username, null);
  assert.deepEqual(audit.entries[0]!.detail, {});
  assert.equal(audit.verification, null);
  assert.equal(api.parseClaimsEvent({ type: "other" }), null);
  assert.equal(api.parseClaimsEvent("not an object"), null);
  assert.deepEqual(api.parseClaimsEvent({ type: "claims", claims: [] }), []);
});

test("a request that cannot be built is refused before anything is sent", async () => {
  const d = double(200, "{}");
  const client = new api.HydraServerClient("http://h", { transport: d.transport });
  await assert.rejects(client.jogArm(1, true, { controllerId: "bad id!" }), api.ServerRequestError);
  await assert.rejects(client.moveTable(1, Number.NaN, 0), api.ServerRequestError);
  await assert.rejects(client.moveTable(1, 0, Number.POSITIVE_INFINITY), api.ServerRequestError);
  await assert.rejects(client.moveTable(1, 0, 0, { mode: "diagonal" as never }), api.ServerRequestError);
  await assert.rejects(client.command(1, ""), api.ServerRequestError);
  await assert.rejects(client.audit({ type: "a b;c" }), api.ServerRequestError);
  assert.equal(d.seen.length, 0);
});

test("the contract validator refuses an unknown contract and the manifest decodes", () => {
  assert.throws(() => api.validate("NoSuchContract" as never, {}), api.ContractValidationError);
  assert.equal(api.isValid("NoSuchContract" as never, {}), false);
  assert.ok(api.loadContractManifest().contracts.length > 0);
  assert.deepEqual(api.verifyContractManifest(), []);
});
