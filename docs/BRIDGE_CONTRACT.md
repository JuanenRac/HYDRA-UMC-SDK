<!-- =============================================================================
HYDRA-UMC-SDK - External machine bridge contract
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

# HYDRA-UMC External Machine Bridge Contract

`HYDRA-UMC-BRIDGE-ROS2`, `HYDRA-UMC-BRIDGE-OPENPNP`,
`HYDRA-UMC-BRIDGE-PRINTER3D`, `HYDRA-UMC-BRIDGE-CNC` and
`HYDRA-UMC-BRIDGE-LASER` share this v0 boundary.

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

Every `BridgeJob` carries `job_id`, `idempotency_key`, source, phase, observed
machine state and string-only integration parameters. Bridges must persist or
otherwise deduplicate the idempotency key before retrying an external request.

## Bridge-specific meaning

- ROS 2 maps continuous state to topics, short inspection to services and
  cancellable long work to actions.
- OpenPnP coordinates board/job phases with its machine lifecycle; it does not
  delegate placement kinematics to a robot unless a future explicit adapter
  proves that safe.
- Printer, CNC and laser bridges coordinate auxiliaries around native G-code
  machine work. They do not replace the controller firmware or its interlocks.
