// =============================================================================
// HYDRA-UMC-SDK - TypeScript tests: the robot roster of a settings answer
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

import assert from "node:assert/strict";
import test from "node:test";

import * as sdk from "../dist/index.js";

test("the roster lists every robot of every controller with the playback the server set", () => {
  const roster = sdk.rosterFromSettings({
    controllers: [
      { id: "c1", robots: [{ id: 1, online: true, playbackState: { isPlaying: true } }, { id: 2, playbackState: { isPaused: true, isPlaying: true } }] },
      { robots: [{ id: 0, online: true, playbackState: { isFinished: true, isPlaying: true } }, { id: 7 }] },
    ],
  });
  assert.deepEqual(roster, {
    schema_version: "1.0",
    robots: [
      { controller_id: "c1", robot_id: 1, online: true, playback: "playing" },
      { controller_id: "c1", robot_id: 2, online: false, playback: "paused" },
      { controller_id: "controller-2", robot_id: 0, online: true, playback: "finished" },
      { controller_id: "controller-2", robot_id: 7, online: false, playback: "idle" },
    ],
  });
  assert.equal(sdk.isValid("RobotRoster", roster), true);
});

test("what is not understood is skipped and nothing is invented", () => {
  for (const settings of [null, undefined, 5, "x", [], {}, { controllers: "no" }, { controllers: [null, 3, { robots: "no" }, { robots: [null, { id: -1 }, { id: 1.5 }, { id: "1" }, true] }] }]) {
    assert.deepEqual(sdk.rosterFromSettings(settings), { schema_version: "1.0", robots: [] });
  }
});

test("a controller id that is empty or too long is replaced by its position", () => {
  const roster = sdk.rosterFromSettings({ controllers: [{ id: "", robots: [{ id: 1 }] }, { id: "x".repeat(101), robots: [{ id: 2 }] }] });
  assert.deepEqual(roster.robots.map((robot) => robot.controller_id), ["controller-1", "controller-2"]);
});

test("the roster stops at one thousand robots", () => {
  const robots = Array.from({ length: 1200 }, (_, index) => ({ id: index }));
  assert.equal(sdk.rosterFromSettings({ controllers: [{ id: "c", robots }] }).robots.length, 1000);
});
