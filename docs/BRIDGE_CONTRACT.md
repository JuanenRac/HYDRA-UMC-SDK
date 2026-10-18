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

`evaluate_job` then ignores the claim. Without an observation it falls back to
the claim, which is only acceptable for a bridge that has no way to observe its
machine yet.

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
