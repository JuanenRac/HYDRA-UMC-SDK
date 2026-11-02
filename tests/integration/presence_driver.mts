// =============================================================================
// HYDRA-UMC-SDK - tests/integration/presence_driver.mts
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================
// Drives the real dead-man of the presence of the operator of HYDRA-UMC-SERVER (src/operatorPresence.ts) with a clock that the scenario
// moves by hand, and prints what it did as one JSON line. The server source is only read: its path comes from PRESENCE_MODULE.
// Nothing is started, listened on or written; the robots are plain objects.
const modulePath = process.env.PRESENCE_MODULE ?? "";
const { OperatorPresence, presenceSettings } = await import(modulePath);

const action = (process.env.PRESENCE_ACTION ?? "slow") as "slow" | "pause" | "notify" | "stop";
let now = 1_000_000;
const robots = [
  { id: 1, name: "robot-a", playbackState: { isPlaying: true, activeStep: 3, speed: 100 }, reservation: { ownerId: 7 } },
  { id: 2, name: "robot-b", playbackState: { isPlaying: true, activeStep: 1, speed: 80 }, reservation: { ownerId: 99 } },
];
const settings = { controllers: [{ id: "c1", robots }] };
const log: string[] = [];
const audit: { type: string }[] = [];
const warned: string[][] = [];
const deltas: unknown[] = [];

const presence = new OperatorPresence({
  enabled: () => true,
  settings: () => presenceSettings(undefined, action),
  now: () => now,
  getSettings: () => settings,
  isReservationActive: (reservation: unknown) => reservation !== undefined && reservation !== null,
  stoppedPlaybackState: (previous: Record<string, unknown>) => ({ ...previous, isPlaying: false, requestStop: true }),
  stopServerPlayback: () => undefined,
  broadcastRobotDelta: (d: unknown) => { deltas.push(d); },
  persist: async () => undefined,
  log: (line: string) => { log.push(line); },
  audit: (event: { type: string }) => { audit.push(event); },
  warn: (names: string[]) => { warned.push(names); },
});

const user = { id: 7, username: "ana" };
const beat = (sequence: number, state: "PRESENT" | "LEFT" = "PRESENT") => presence.beat(user, { sequence, intervalSeconds: 2, state });
const snapshot = () => ({ speedA: robots[0].playbackState.speed, speedB: robots[1].playbackState.speed, playingA: robots[0].playbackState.isPlaying, state: presence.status(7).state });

const steps: Record<string, unknown> = {};
const timeoutMs = presenceSettings(undefined, action).timeoutMs;

beat(1);
presence.tick();
steps.alive = snapshot();

// the heartbeat keeps coming: nothing is touched
for (let i = 2; i < 8; i++) { now += 2000; beat(i); presence.tick(); }
steps.stillAlive = snapshot();

// the heartbeat stops
now += timeoutMs + 5000;
presence.tick();
steps.lost = snapshot();
steps.warnedAfterLoss = warned.length;

// the operator raises the speed again by hand while lost: it goes back to the cap on the next tick
robots[0].playbackState.speed = 100;
presence.tick();
steps.afterRaise = snapshot();

// the heartbeat comes back: trusted again only after several in a row
let sequence = 100;
const recover = presenceSettings(undefined, action).recoverBeats;
now += 1000; beat(sequence++);
steps.afterOneBeat = snapshot();
for (let i = 1; i < recover; i++) { now += 1000; beat(sequence++); }
steps.recovered = snapshot();

// the speed comes back along the ramp, without a jump
const rampSeconds = presenceSettings(undefined, action).rampMs / 1000;
const ramp: number[] = [];
for (let i = 0; i < rampSeconds + 5; i++) { now += 1000; beat(sequence++); presence.tick(); ramp.push(robots[0].playbackState.speed); }
steps.afterRamp = snapshot();

console.log(JSON.stringify({ ramp, steps, recoverBeats: recover, timeoutMs, auditTypes: audit.map((a) => a.type), warned, deltas: deltas.length, logHasLoss: log.some((l) => l.includes("lost the heartbeat")) }));
