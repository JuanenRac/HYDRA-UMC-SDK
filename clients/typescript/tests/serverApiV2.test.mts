// =============================================================================
// HYDRA-UMC-SDK - TypeScript tests: blocks 2 to 5 of the second server contract
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
const CASES = JSON.parse(fs.readFileSync(path.resolve(here, "..", "..", "..", "conformance", "server-routes", "cases_v2.json"), "utf-8"));

type Args = Record<string, any>;

function build(call: string, a: Args): api.ServerRequest {
  switch (call) {
    case "getRobot":
      return api.getRobotRequest(a.robotId);
    case "claim":
      return api.claimRequest(a.robotId, { controllerId: a.controllerId, ifMatch: a.ifMatch });
    case "release":
      return api.releaseRequest(a.robotId, { controllerId: a.controllerId, ifMatch: a.ifMatch });
    case "command":
      return api.commandRequest(a.robotId, a.command, { params: a.params, controllerId: a.controllerId, ifMatch: a.ifMatch });
    case "table":
      return api.tableCommandRequest(a.robotId, a.x, a.y, { rz: a.rz, mode: a.mode, controllerId: a.controllerId, ifMatch: a.ifMatch });
    case "audit":
      return api.auditRequest({ limit: a.limit, afterSeq: a.afterSeq, type: a.type, robotId: a.robotId, verify: a.verify });
  }
  throw new Error(`unknown call ${call}`);
}

const KIND: Record<string, Function> = {
  "revision-mismatch": api.RevisionMismatchError,
  "table-move": api.TableMoveError,
};

for (const c of CASES.requests) {
  test(`v2 request case ${c.name}`, () => {
    const request = build(c.call, c.args);
    assert.equal(request.method, c.expect.method);
    assert.equal(request.path, c.expect.path);
    assert.deepEqual(request.body, c.expect.body);
    assert.deepEqual(request.headers, c.expect.headers);
  });
}

for (const c of CASES.invalidRequests) {
  test(`v2 invalid request ${c.name} is refused before sending`, () => {
    assert.throws(() => build(c.call, c.args), api.ServerRequestError);
  });
}

for (const c of CASES.errors) {
  test(`v2 error case ${c.name}`, () => {
    const error = api.parseApiError(c.status, c.body);
    assert.equal(error.constructor, KIND[c.expect.kind]);
    assert.equal(error.status, c.status);
    assert.equal(error.code, c.expect.code);
    if (c.expect.kind === "revision-mismatch") assert.equal((error as api.RevisionMismatchError).revision, c.expect.revision);
  });
}

test("a robot with its revision", () => {
  const view = api.parseRobot(CASES.responses.robot);
  assert.equal(view.revision, "0123456789abcdef");
  assert.equal(view.robot.name, "B");
  assert.equal(view.cellId, "c1");
  assert.throws(() => api.parseRobot({ robot: {} }), api.ServerRequestError);
});

test("command results", () => {
  const plain = api.parseCommandResult(CASES.responses.commandPlain);
  assert.equal(plain.success, true);
  assert.equal(plain.revision, "fedcba9876543210");
  assert.equal(plain.applied, null);
  const table = api.parseCommandResult(CASES.responses.commandTable);
  assert.deepEqual(table.applied, { robotId: 1, x: 40, y: 65, rz: 15 });
});

test("a claim answer carries the new revision", () => {
  assert.equal(api.parseClaimResult(CASES.responses.claimWithRevision).revision, "0123456789abcdef");
  assert.equal(api.parseClaimResult({ success: true, reservation: null }).revision, null);
});

test("audit", () => {
  const view = api.parseAudit(CASES.responses.audit);
  assert.equal(view.enabled, true);
  assert.equal(view.lockedOff, false);
  assert.deepEqual(view.entries.map((e) => e.seq), [1, 2]);
  assert.equal(view.entries[0]!.controllerId, "tab-1");
  assert.equal(view.entries[0]!.detail.action, "claimed");
  assert.equal(view.entries[1]!.username, null);
  assert.equal(view.verification?.entries, 2);
});

test("the claims event", () => {
  const claims = api.parseClaimsEvent(CASES.responses.claimsEvent);
  assert.deepEqual(claims?.map((c) => c.robotId), [1, 2]);
  assert.equal(claims![0]!.jogArmedUntil, 31000);
  assert.equal(claims![1]!.jogArmedUntil, null);
  assert.equal(api.parseClaimsEvent(CASES.responses.otherMessage), null);
  assert.equal(api.parseClaimsEvent("not a message"), null);
});

function client(status: number, body: unknown) {
  const sent: Array<{ method: string; url: string; headers: Record<string, string>; body: string | null }> = [];
  const transport: api.Transport = async (method, url, headers, payload) => {
    sent.push({ method, url, headers, body: payload });
    return { status, text: JSON.stringify(body) };
  };
  return { api: new api.HydraServerClient("http://hydra.local:3000", { token: "tok", controllerId: "tab-1", transport }), sent };
}

test("the revision that was read is sent back as If-Match", async () => {
  const first = client(200, CASES.responses.robot);
  const view = await first.api.robot(3);
  assert.equal(first.sent[0]!.url, "http://hydra.local:3000/api/robot/3");
  const second = client(200, CASES.responses.commandTable);
  const result = await second.api.moveTable(3, 40, 65, { rz: 15, ifMatch: view.revision });
  assert.equal(second.sent[0]!.headers["If-Match"], '"0123456789abcdef"');
  assert.deepEqual(JSON.parse(second.sent[0]!.body ?? "{}").params, { x: 40, y: 65, mode: "absolute", rz: 15 });
  assert.equal(JSON.parse(second.sent[0]!.body ?? "{}").controllerId, "tab-1");
  assert.equal(result.applied?.robotId, 1);
});

test("a stale revision raises with the current one", async () => {
  const c = CASES.errors.find((e: any) => e.name === "revision-mismatch");
  const { api: stale } = client(c.status, c.body);
  await assert.rejects(stale.command(1, "jog", { params: { axis: "x", amount: 1 }, ifMatch: "old" }), (error: any) => {
    assert.ok(error instanceof api.RevisionMismatchError);
    assert.equal(error.revision, "0123456789abcdef");
    return true;
  });
});

test("a refused table move raises", async () => {
  const c = CASES.errors.find((e: any) => e.name === "table-out-of-limit");
  const { api: refused } = client(c.status, c.body);
  await assert.rejects(refused.moveTable(1, 5000, 0), api.TableMoveError);
});

test("audit goes to the route with the filters", async () => {
  const { api: audit, sent } = client(200, CASES.responses.audit);
  const view = await audit.audit({ limit: 5, type: "claim", verify: true });
  assert.equal(sent[0]!.url, "http://hydra.local:3000/api/audit?limit=5&type=claim&verify=1");
  assert.equal(view.entries.length, 2);
});
