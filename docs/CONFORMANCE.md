# Conformance

Each contract has valid, backward-compatible, malformed, and unsafe fixtures.
A producer test proves it emits valid payloads. A consumer test proves it
accepts known versions and rejects invalid required state. CI must run these
tests before an artifact is released.

The first conformance suite should cover device discovery, health degradation,
safety inhibition, duplicate command idempotency, and stale telemetry.

## Implemented v1 suite

`conformance/fixtures/v1/` contains one valid and one invalid payload for each
of the 10 published contracts (`DeviceDescriptor`, `HealthReport`,
`SafetyState`, `UpdateManifest`, `EventEnvelope`, `ScenarioOutcome`,
`Operation`, `Capability`, `ServerDiscovery`, `ProjectManifest`). The Python
reference client and the Go, TypeScript and Rust clients judge them, and
`clients/python/tests/test_schema_differential.py` checks that the Python
validator and the normative JSON Schemas agree on them and on boundary cases.

Producer evidence lives under `conformance/fixtures/v1/producers/<producer>/`.
Each `fixtures.json` names the producer, v1 index schema and contract-to-file
mapping. `tools/verify_contract_matrix.py` validates every mapped payload with
the reference validator, so producer evidence cannot silently drift while the
generic fixtures remain valid.

Run the host suite from `clients/python/`:

```text
PYTHONPATH=src python -m unittest discover -s tests -v
```

`conformance/server-routes/cases.json` is the shared case file of the server control clients (claim, release, jog-arm, claims, safety limits and the optional `controllerId`): the requests each client must build, the requests it must refuse before sending, the error answers it must tell apart and the response bodies it must read. The Python, TypeScript, Go and Rust tests replay the same file; see [SERVER_CLIENT.md](SERVER_CLIENT.md).

`conformance/server-routes/cases_v2.json` is the shared case file of the blocks 2 to 5 of the second server contract (the revision of a robot, `If-Match` and its `412`, the atomic `table` command, the audit record and the `claims` message of the WebSocket). The four clients replay it the same way.
