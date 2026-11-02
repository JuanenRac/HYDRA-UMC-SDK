<!--
=============================================================================
HYDRA-UMC-SDK - Reading the contracts of A.R.M.O.R. in the words of this SDK
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
CC BY-SA 4.0 - see LICENSE.md
=============================================================================
-->

# Alignment with A.R.M.O.R.

A.R.M.O.R. keeps its own library of contracts (ARMOR-COMMON) and this SDK keeps
another. Neither imports the other and neither is about to replace the other: they
describe different machines. What can be shared is the **convention**, so that a
bridge between the two (for example, the alarm of a house reaching the safety state of
a robot cell) is a conversion of words and not a second protocol.

## The conventions side by side

| Subject | A.R.M.O.R. (ARMOR-COMMON) | This SDK | Conversion |
| --- | --- | --- | --- |
| Time | `timestamp_ms`: integer milliseconds since the Unix epoch | `timestamp_utc`: RFC 3339 date-time | `armor_timestamp_ms_to_utc`, `utc_to_armor_timestamp_ms` (millisecond resolution, never a time before the epoch) |
| What it is | `kind` in the body (`alarm`, `node_health`, ...) | `type` of an `EventEnvelope` | `armor.<kind>` |
| Who sent it | `node_id` in the body and in the topic (a mismatch is refused) | `source` | `armor:<node_id>` |
| Version | none in the body; a new field is a new optional field of a closed schema | `schema_version: "1.0"` in every contract | added by the envelope, not by the message |
| Closed messages | every schema has `additionalProperties: false` | closed for the newer contracts, open for the first ones (`EventEnvelope`, `SafetyState`) | the original body travels untouched in `data` |
| Order | none | `sequence` of an `EventEnvelope` | given by the caller (the order in which it saw the messages) |
| Safety words | the phase of an alarm panel: `disarmed`, `exit_delay`, `armed`, `entry_delay`, `alarm` | `SafetyState`: `READY`, `INHIBITED`, `FAULT`, `SAFE_STOP` | `armor_alarm_to_safety_state` with a table |

## What the Python client does

* `armor_state_to_event_envelope(message, sequence, topic=None)`: wraps a state message of
  A.R.M.O.R. in a valid `EventEnvelope` (`event_id` is `armor:<node_id>:<kind>:<timestamp_ms>`,
  so the same message is the same event). It reads the header (`kind`, `node_id`,
  `timestamp_ms`), refuses a `node_id` that is not in the topic when the topic is given, and
  keeps the body as it came.
* `armor_alarm_to_safety_state(message, mapping=None)`: the `SafetyState` that an alarm
  message stands for. **This is the only place where a meaning is chosen**, so the table is a
  parameter. The default (`DEFAULT_ALARM_TO_SAFETY`) says that a sounding alarm is `INHIBITED`
  and every other phase is `READY`. Nothing becomes `SAFE_STOP` unless the installation puts
  it in its own table: stopping machines because a house alarm sounds is a decision of the
  installation, not of a library. The state keeps the original phase in `armor_phase`.

## What is not done

* Nothing publishes on a broker: the functions convert a message that the caller already has.
  Reading `armor/alarm/<node_id>/state` and deciding who may act on the result belongs to
  a service of the installation.
* The messages of the machines of this SDK are not converted the other way: A.R.M.O.R. does not
  read them.
* The default table is a proposal. Whether an alarm should inhibit the job gate of a cell,
  stop it, or only be shown is open until the owner of an installation chooses.
