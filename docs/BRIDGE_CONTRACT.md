<!-- =============================================================================
HYDRA-UMC-SDK - External machine bridge contract
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

# HYDRA-UMC External Machine Bridge Contract

`HYDRA-UMC-BRIDGE-ROS2`, `HYDRA-UMC-BRIDGE-OPENPNP`,
`HYDRA-UMC-BRIDGE-PRINTER3D`, `HYDRA-UMC-BRIDGE-CNC`,
`HYDRA-UMC-BRIDGE-LASER`, `HYDRA-UMC-BRIDGE-AMR`,
`HYDRA-UMC-BRIDGE-DROIDS` and `HYDRA-UMC-BRIDGE-UAV` share this v0
boundary - all 8 bridges use `bridge_contract.py`'s `evaluate_job()`.

## Safety authority

An external application can describe a correlated high-level job phase. It
cannot send raw CAN/SPI/UART frames, bypass HYDRA-UMC-SERVER authorisation, or
override MCU limits, watchdogs or E-STOP. The MCU remains the final physical
safety authority.

## Common state gate

Productive phases (`PREPARE`, `LOAD`, `PROCESS`, `UNLOAD`, `COMPLETE`) require
a `READY` HYDRA-UMC cell and an `IDLE` external machine. `ABORT` is always
forwarded to the authorised safety path so a faulted integration can request a
controlled stop rather than becoming unable to stop itself.

Every `BridgeJob` carries `job_id`, `idempotency_key`, source, phase, the
machine state **the requester claims** and string-only integration parameters
(at most 32 of them, names up to 64 characters, values up to 1024, identifiers up
to 128). Bridges must persist or otherwise deduplicate the idempotency key before
retrying an external request.

### The gate uses what the bridge observes

A job arrives in a message that anybody on the broker may publish, so the
`machine_state` inside it is a claim, not a fact. A bridge that can read the
state of its machine (a printer's Moonraker status, a CNC's GRBL status, the
OpenPnP machine state, the AMR's fleet state...) must read it just before the
gate and pass it:

```python
decision = evaluate_job(job, cell_state, observed_machine_state=machine.state_now())
```

`evaluate_job` then ignores the claim. **Without an observation the gate refuses
the job** (it fails closed): the claim arrives in a message anybody on the broker
may publish, so it is not a state to trust. A bridge that has no way to observe its
machine yet is blocked until it does; `allow_unobserved=True` is the explicit,
temporary opt-in that makes the gate use the claim again, and it should not stay.

### Job intake: retained messages and repeated keys

Two rules every bridge needs are carried by the SDK so that they are written once
(`hydra_umc_sdk.job_intake`):

- **A retained message is not a request.** The broker replays a retained command at
  every reconnect, which would start a physical action again each time. `JobIntake`
  ignores any message whose retain flag is set.
- **A key is handled once.** MQTT QoS 1 may deliver a command twice and a client may
  retry it. `IdempotencyStore` remembers the keys (SQLite when given a file, so a
  restart does not forget; 24 hours and 10 000 keys by default) and, if the bridge
  stores it with `remember()`, the answer that was given, so a repeat is answered
  again instead of being run again.

```python
store = IdempotencyStore("/var/lib/hydra-umc/bridge-keys.sqlite")
intake = JobIntake(store)

def on_message(message):
    result = intake.accept(json.loads(message.payload), retained=message.retain)
    if result.duplicate:
        publish(store.recall(result.job.idempotency_key))   # the same answer, nothing runs twice
        return
    if not result.accepted:
        return                                              # retained or malformed
    decision = evaluate_job(result.job, cell_state, observed_machine_state=machine.state_now())
    store.remember(result.job.idempotency_key, decision.reason)
    ...
```

A job refused by the gate keeps its key: to try again, the sender uses a new one.

### The handler of `cmd/job`, once

`read_job_message(intake, topic, payload, retained=...)` is the whole first half of the handler of `cmd/job` that each bridge used to write for itself: a retained message is ignored, a payload over 16 KiB or that is not JSON is refused, `JobIntake` looks at the job and a repeat is answered with the stored answer (or refused as in doubt when none was stored). It never raises and returns a `JobMessage` with exactly one of `ignore`, `refusal` (the `{"allowed": false, "reason": ...}` to publish on the result topic), `repeat_answer` (to publish again) or `job` (new, well formed and, when asked, signed). The bridge then only decides about the job and calls `store.remember(...)`.

### Signed commands with an expiry (off by default)

Anyone who may publish on a command topic can make a bridge act, and a message that the network delivers late is carried out as if it were new. With the switch on, every `cmd/job` carries `issued_at_ms`, `expires_in_ms` and `signature` (`hydra_umc_sdk.signed_commands`):

- the signature is the HMAC-SHA256 (64 lowercase hexadecimal digits) of `hydra-umc-cmd-v1`, a newline, the topic, a newline and the payload without `signature` written as JSON with sorted keys, no spaces and ASCII escapes; the job of a bridge holds strings, booleans and whole numbers only, so every language writes the same bytes;
- the key is one per bridge, in a file that only the service can read (at least 32 characters, for example 64 hexadecimal digits; on a POSIX system a file readable by the group or the others is refused);
- a command that is unsigned, signed with another key or for another topic, altered after it was signed, expired, issued in the future by more than the allowed clock skew, or that asks to stay valid longer than the bridge accepts, is refused with the reason on the result topic; a retained message is ignored before any of this;
- the switch and its limits are in the environment of the service: `HYDRA_UMC_<NAME>_SIGNED_COMMANDS` (yes or no; off by default, and a value that is neither raises an error), `HYDRA_UMC_<NAME>_COMMAND_KEY_FILE`, `HYDRA_UMC_<NAME>_COMMAND_MAX_SKEW_MS` (5000) and `HYDRA_UMC_<NAME>_COMMAND_MAX_EXPIRES_MS` (300000). With the switch on and no usable key the service does not start; with it off nothing changes and no key is read.

```python
verifier = CommandVerifier.from_environment("CNC")           # raises at the start when it is on and the key is unusable
intake = JobIntake(store, verifier)
message = read_job_message(intake, topic, payload, retained=retained)

# the sender
signed = sign_command(topic, job_dict, key, expires_in_ms=30_000)
```

### Bridge health on one retained topic (off by default)

With `HYDRA_UMC_<NAME>_BRIDGE_HEALTH=yes` a bridge publishes its state on `hydra/bridges/<name>/health`, retained at QoS 1, in the shape of the `HealthReport` contract (`hydra_umc_sdk.bridge_health`): `READY` with the check `link` passing when its connection is accepted, `DEGRADED`, `INHIBITED`, `FAULT` or `SAFE_STOP` with the checks that explain it, and `FAULT` with `link` failing as its Last Will if it disappears. The server and the dashboard read one topic family instead of probing every bridge. An MQTT connection has one Last Will, so with the switch on the will is on the health topic, `availability` is no longer maintained and the retained message an earlier run left there is cleared when the bridge connects; a consumer reads the health topic only. Pass `health=BridgeHealth("<name>")` to `open_bridge_client`. The broker's ACL must let the bridge publish on its own health topic.

### The shared transport

`hydra_umc_sdk.bridge_transport` holds what every command and state bridge needs of MQTT: the retry of the first connection, the dispatcher that keeps a stop command from waiting behind a slow one and ignores retained replays, and the client that sets the Last Will on `availability` (or on the health topic, see below), subscribes to `cmd/#` and announces `online` after every connect. A bridge keeps only what its topics mean.

### The shared phase coordinator

`hydra_umc_sdk.phase_coordinator.PhaseCoordinator` is the one place that maps a job phase onto the named action of a bridge: it looks the action up, checks the parameters the action needs (a validator says what they mean and returns the values to forward), asks `evaluate_job` (the fail-closed gate), lets the actions that bring the machine to a safe state through whatever the gate said, and describes the static vocabulary without opening a transport. The UAV, AMR and droid bridges use it and keep only their own table of actions, their parameters and what they do with the answer. It never relaxes the gate: an action that is not in `safe_actions` is refused exactly as before, and a de-escalation that has no phase (sit, land, disarm, pause) is `always_forwarded`, while a productive standalone request (stand up) is `gated_request` and goes through the same gate as a job.

### The shared GRBL serial link

`hydra_umc_sdk.serial_link` is what the CNC and laser bridges need to talk to a GRBL controller: `SerialLike`, the one lazy import of `pyserial` (the port is opened closed and with the control lines off, so an Arduino-based board is not reset), `resolve_serial_device_path` / `open_serial_port_by_id` to find a device by a stable id, `ReconnectingSerialConnection` to reopen it after a replug, `read_status_line` (sends `?` and returns the report that answers that query, not an old line), `parse_status_report` (the fields of a report: state, positions, feed, spindle or laser speed, overrides) and `send_realtime` (writes one real-time byte and says whether it really went out). It never streams a G-code program.

### Connecting to the broker: credentials and TLS

A production HYDRA-UMC-MQTT-BROKER demands a user and a password, and evaluates its ACL for the identity of the credential (its `clientIdPrefix`), not for the client ID the
client picked. A bridge therefore connects with the settings of its service environment (`hydra_umc_sdk.mqtt_connection`), never with values written in code or in a committed file:

| Variable | Meaning |
|---|---|
| `HYDRA_MQTT_USERNAME` / `HYDRA_MQTT_PASSWORD` | The MQTT credential (the password only together with the user name). The bridge's client ID must start with the prefix of its credential. |
| `HYDRA_MQTT_PASSWORD_FILE` | The password read from a file (a Docker or systemd secret), used when `HYDRA_MQTT_PASSWORD` is not set. |
| `HYDRA_MQTT_TLS_CA` | The CA certificate that signed the broker's certificate: the link is then TLS and the certificate is verified. |
| `HYDRA_MQTT_TLS` | `1` turns TLS on with the system's trusted CAs (a broker certificate from a public CA). |
| `HYDRA_MQTT_TLS_CERT` / `HYDRA_MQTT_TLS_KEY` | The client certificate and key for a broker that demands mutual TLS; both are needed. |

A TLS broker listens on its own port (8883 by default); the bridge passes that port when it connects.

With none of them set the connection is anonymous and plain, as it always was (a development broker).

## Bridge-specific meaning

- ROS 2 maps continuous state to topics, short inspection to services and
  cancellable long work to actions.
- OpenPnP coordinates board/job phases with its machine lifecycle; it does not
  delegate placement kinematics to a robot unless a future explicit adapter
  proves that safe.
- Printer, CNC and laser bridges coordinate auxiliaries around native G-code
  machine work. They do not replace the controller firmware or its interlocks.
- AMR coordinates a VDA-5050-inspired order vocabulary over MQTT; path
  planning stays the AMR's own navigation stack, never this bridge's.
- Droids coordinate a named walk/pick/place action vocabulary over a real
  Boston Dynamics Spot transport; gait and balance stay on the droid's own
  controller.
- UAV coordinates a named flight-request vocabulary over a real MAVLink
  transport, with a deterministic heartbeat/link-loss failsafe watchdog;
  flight control itself stays on the UAV's own autopilot.
