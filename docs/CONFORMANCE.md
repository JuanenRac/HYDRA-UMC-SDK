# Conformance

Each contract has valid, backward-compatible, malformed, and unsafe fixtures.
A producer test proves it emits valid payloads. A consumer test proves it
accepts known versions and rejects invalid required state. CI must run these
tests before an artifact is released.

The first conformance suite should cover device discovery, health degradation,
safety inhibition, duplicate command idempotency, and stale telemetry.

## Implemented v1 suite

`conformance/fixtures/v1/` contains valid `DeviceDescriptor` and
`HealthReport` payloads plus an invalid health state fixture. The Python
reference client verifies the required fields, schema version, and initial
safety/health state enumerations.

Producer evidence lives under `conformance/fixtures/v1/producers/<producer>/`.
Each `fixtures.json` names the producer, v1 index schema and contract-to-file
mapping. `tools/verify_contract_matrix.py` validates every mapped payload with
the reference validator, so producer evidence cannot silently drift while the
generic fixtures remain valid.

Run the host suite from `clients/python/`:

```text
PYTHONPATH=src python -m unittest discover -s tests -v
```
