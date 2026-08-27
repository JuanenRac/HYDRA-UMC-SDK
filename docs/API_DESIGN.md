# API design

HYDRA-UMC-SERVER exposes public HTTP/WebSocket APIs. The SDK publishes the
OpenAPI source and typed clients, but it does not turn every service into an
HTTP server. Public routes are versioned under `/api/v1`.

Separate read, command, and real-time planes. UI and external integrations
call Server. Server calls an adapter. Only the hardware adapter talks to the
MCU or URTC transport. MQTT is appropriate for telemetry/events, not an
unvalidated motion-control channel.

Command results use `ACCEPTED`, `REJECTED`, `RUNNING`, `COMPLETED`, or
`FAILED`, with a correlation identifier and structured error code.
