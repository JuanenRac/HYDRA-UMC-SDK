# Changelog

## [0.2.6] - real cross-language contract round-trip tests

New round-trip tests in all 4 reference clients (Python, Go, Rust,
TypeScript), each decoding the same real `conformance/fixtures/v1/*.valid.json`
fixtures the existing schema-validation tests already use, re-encoding
them, and asserting the result is structurally identical to the original -
a different, complementary check from schema validation: a payload can
validate cleanly against its schema while still losing or reordering data
on its way through a language's own encode/decode path. Go and Rust decode
into their own hand-written structs for the 7 contracts that have one
(catching a real risk those two languages specifically have: a struct
missing a field would silently drop it on round trip); the 3 newer
contracts with no dedicated struct yet (Capability, Operation,
ScenarioOutcome) round-trip through the same generic representation each
client's own validator already uses for them. Evaluated
`contracts/openapi/v1/server.openapi.json` for auto-generation from the
JSON Schema contracts: confirmed hand-maintained, but skipped adding a
generator - only 1 of its 23 `components/schemas` entries maps to a real
published JSON Schema contract, the other 22 describe REST-only request/
response bodies with no schema source to generate from.

## [0.2.5] - PROM-G02/G03: a real evidence and promotion-gate standard, describing what the ecosystem's own real closures already do

Two new sections in `docs/PROJECT_MANIFEST.md`, right after "Maturity
levels": "Promotion evidence" and "Promotion gate". Same spirit as
0.2.4's own maturity glossary - neither invents a new process, both
name the real practice this ecosystem's own actual closures already
follow, so it stops being tribal knowledge.

"Promotion evidence" names what a real change's own record should be
able to answer (scope, exact command/test run, environment, result,
known limitations, affected consumers), reusing each repository's own
existing `CHANGELOG.md`/CI rather than a second registry, and keeps 4
real evidence kinds distinct rather than letting a lighter one stand in
for a heavier one: a unit test, a real-process loopback/integration
test, an emulation (proves this code's own handling of a simulated
condition, never that real hardware/a real driver works), and a real
physical-bench/supervised-operation result.

"Promotion gate" is the real checklist this ecosystem's own actual
maturity changes already apply before changing `maturity`: close real
blockers on the dependency path, run the affected real consumer's own
tests too (not just this repository in isolation), a real
non-incremental build/test, install/run the produced package OUTSIDE
its own checkout, exercise one real good case and one real bad case,
and bring manifest/`CHANGELOG.md`/README (all 7 languages)/usage docs
back in sync with what actually shipped - `established` additionally
requires a real restart/cancellation/lost-dependency/recovery within
the promoted scope.

## [0.2.4] - PROM-G01: a real maturity-level glossary, describing what the ecosystem already does

`maturity` (`scaffolding`/`functional`/`established`/`production`) has
been a validated manifest enum since the beginning, but nothing ever
wrote down what actually distinguishes the four values - each
repository's own choice was a judgment call, not a checked criterion.

New "Maturity levels" section in `docs/PROJECT_MANIFEST.md`, grounded in
the real, current split across all 60 manifests (53 `established`, 5
`scaffolding`, 1 `functional`, 0 `production`) rather than inventing a
new rule: `scaffolding` means real, tested code not yet exercised in
its own real operational context (physical hardware, sustained
deployment) - even a repository whose own delivery plan is 100% shipped
(`HYDRA-UMC-DEV-SERVER`) stays `scaffolding` until that happens;
`functional` means real capability validated against SOME real physical
target, not yet at `established`'s breadth (`URTC`); `established` is
real code AND real, sustained use in this ecosystem's own actual
deployment; `production` is reserved, unclaimed by any repository today.
Descriptive, not a new mandate - no repository's own `maturity` value
changes because of this.

## [0.2.3] - real, automatic README section-structure parity between languages

The ecosystem's own Related Projects catalog gap was found by
manual audit - nothing automatically checked whether a translation's
own README structure actually matched its English original.

- New `hydra_umc_sdk.readme_parity` module: `check_readme_section_parity()`
  compares README.md's own ordered `## <emoji>` heading signature
  against every translation's - reports a missing section, an extra
  one, a reordered one, or a mismatched heading emoji, without caring
  about the translated prose at all. Reuses what already exists in
  every repo (the emoji itself is never translated) instead of
  inventing a new `canonical:start/end` marker convention that would
  duplicate information hundreds of files already encode. 9 new unit
  tests.
- New `tools/sync_readme_parity.py`: same real distribution design as
  's `sync_doc_policy.py` (a vendored `tools/_readme_parity.py`
  copy per repo, no live runtime dependency added to any repo's own
  per-commit CI) - adds a real call right after this project's own check in
  each sibling's `ci_validate.py`.
- Ran it against the whole ecosystem while building it: found and fixed
  2 real, tiny structural bugs it was designed to catch (`HYDRA-UMC-SDK`
  and `HYDRA-UMC-OS`'s own `README_ita.md` each had `## 🚧Stato` missing
  the space after the emoji, present nowhere in this or 6 other
  languages) - the exact class of drift this check exists to catch
  automatically instead of by manual audit.

## [0.2.2] - the public/private documentation boundary check is a real, tested, canonical module now

Every one of this ecosystem's ~60 repos carried its own byte-for-byte
copy of the same public/private documentation boundary check inside its
own `tools/ci_validate.py` - a real future rule change would have meant
hand-editing ~60 files, since nothing here was a single source of truth.

- New `hydra_umc_sdk.doc_policy` module: `check_public_private_boundary()`,
  the exact same two-part check (a bare private-marker name, and a set
  of private-planning-material phrases) every repo's own CI already ran,
  now real, tested, canonical code instead of ~60 independent copies. 7
  new unit tests against a real throwaway git repository (this check
  shells out to `git grep`, so a fake filesystem alone would never
  exercise the real command it runs).
- New `tools/sync_doc_policy.py`: propagates a vendored copy
  (`tools/_doc_policy.py`, never hand-edited there) into every sibling
  repo, and rewrites each one's own `ci_validate.py` to call it instead
  of carrying an independent copy. Deliberately NOT a live runtime
  dependency on this package for every repo's own per-commit CI - most
  of them are not Python projects at all, and this ecosystem's own CI
  already has enough real fragility from cross-repo checkouts. A future
  rule change now means: edit the one canonical module, run this script
  once.

## [0.2.1] - New docs/TESTING_STRATEGY.md: shared test levels, evidence, and fixture conventions

- Published the shared test-level (per-commit/contract-change/scheduled/
  release-candidate), platform-matrix, minimum-evidence-per-result,
  reproducible-campaign target, fixture-independence, and cost/storage
  conventions every repository's own `build-test`/`ci_validate` already
  approximates on its own - previously only living as a private planning
  document, now a real, linkable guide. Cross-references
  `compare_runs()`/`ScenarioOutcome` as the reproducible-scenario
  level's own "was it actually fixed" check.
- Linked from README.md's "Further documentation" list in all 7
  languages.

## [0.2.0] - Operation.result + Capability, and 2 real cross-client drift bugs fixed along the way

A real evidence-of-execution contract, distinct from a merely declared
capability: an Operation reaching a terminal status was never, by
itself, proof anything really happened - a queue can report
`status: "terminated"` with observation entirely disabled. New optional
`result` on the `Operation` contract (`run_id`, `revision`, `origin`
real/simulated, `observers_enabled`, `accepted_at_utc`/`executed_at_utc`/
`observed_at_utc`, `outcome` success/failure/unknown with a required
`outcome_reason` whenever it isn't success) plus `operation.py`'s new
`concludes_success()` - the real gate that refuses to conclude success
from a result belonging to a different run, one produced with observers
disabled, or one never actually observed. New standalone `Capability`
contract (`target`, `kind`, `declared`, `last_checked_at_utc`,
`checked_configuration`, `max_age_seconds`, `last_check_outcome`) plus
`capability.py`'s `is_capability_usable()` - whether a target *declares*
support for an operation kind at all is now modeled as data distinct
from whether that support was *recently, actually verified*; a declared
but never-checked or gone-stale capability is never treated as usable.
Both mirror this ecosystem's own established calibration/observation
freshness pattern (HYDRA-UMC-SAFETY-ZONES' `calibration.py`/
`observation.py`). 10 real contracts now, vendored across all 4
reference clients (Python/Go/TypeScript/Rust) with matching conformance
fixtures.

Also fixed two real, unrelated drift bugs found while doing this work:

- This repository's own `hydra-umc.project.json` declared `native_version.file`
  as `CHANGELOG.md` with a bare `(\d+)\.(\d+)\.(\d+)` pattern - a
  self-referential, tautological check that could never actually catch
  the native version (`clients/python/pyproject.toml`) drifting out of
  sync with the manifest, which is exactly what had already happened:
  the previous 0.1.9 release bumped the manifest and `CHANGELOG.md` but
  never `pyproject.toml`/`__init__.py` themselves. Fixed the manifest to
  point at the real file, and synced the real native version to 0.1.9
  before bumping to this release.
- `clients/rust/src/validation.rs`'s `CONTRACT_FILES` map (and the test
  suite's own `CONTRACT_FIXTURE_STEM`) had silently never gained
  `ScenarioOutcome` or `Operation` entries, even though both schemas
  were correctly embedded - `validate("Operation", ...)` returned
  "unknown contract" for every real payload in the Rust client, through
  two whole prior contract additions, because `tools/verify_contract_matrix.py`'s
  cross-client coverage check only ever compared Go and TypeScript
  against the published schemas, never Rust. Both contracts restored;
  the matrix script now also cross-checks Rust, so this drift class is
  caught automatically going forward for all three non-Python clients.

22 new Python tests (`test_capability.py`, `test_operation.py`,
`test_validation.py`), Go/Rust/TypeScript fixture-loop coverage extended
automatically via their existing dynamic fixture maps. Verified: python
161 passed + 20 subtests, go test ok, cargo test 9/9, npm test 28/28
(tsc clean), verify_contract_matrix PASS contracts=10 (incl. new Rust
coverage check), ci_validate PASS. README x7 synced (9 -> 10 contracts).

## [0.1.9] - Recover a health check left pending by a crash, not just a rename

Checkpoints backed by real postconditions, not just a rename: a
promotion that finishes its 2 renames is not necessarily a HEALTHY
promotion - the real postcondition is that the service was actually
checked, not merely that files were moved. `PromotionRecord`
gains an optional `health_check_url` (only set when a project's own
`hydra-umc.project.json` declares a `service_health_path`); new
`check_service_health(url)` does a real, minimal HTTP GET - deliberately
STRICTER than a bare reachability probe (compare
HYDRA-UMC-LOCAL-TECHNICIAN's own `network.connectivity`, where any real
HTTP response counts as reachable): here, only a real 2xx counts as
healthy, since a 4xx/5xx means the freshly-promoted code IS running but
is not well, and must not be waved through as success.

`recover()`'s own PROMOTED branch used to say "nothing to recover" for
every promoted record - now, when a `health_check_url` is set, it runs
the real pending check right now (never repeating the actual clone/build)
and only marks the promotion `COMPLETE` if it genuinely passes; a check
that still fails leaves the record pending for a human/next run instead
of announcing success prematurely - the acceptance test:
cut the process after promoting and before checking health, restart,
and the pending check runs for real rather than being silently skipped.

8 new tests (`test_promotion_journal.py`, `CheckServiceHealthTests` +
extensions to `RecoverTests`): a real local HTTP server answering 200
(health check passes, promotion completes), one answering 500 (fails,
stays pending), a real closed port (fails, stays pending), `health_check_url`
surviving `advance()` across phase transitions, and an older-shaped
journal file (no `health_check_url` key at all) still loading with it
defaulting to `None`.

## [0.1.8] - A durable, transactional promotion journal

### Added

- **`clients/python/src/hydra_umc_sdk/promotion_journal.py`** - the real,
  durable version of the mitigation HYDRA-UMC-UPDATER's own
  `install.py` already carries inline (previously an honest, bounded
  mitigation rather than the full transactional journal/rollback, which
  needed designing once and sharing with HYDRA-UMC-OPS-AGENT's own
  `canary_deploy.py`). Both installers stage a verified candidate, then
  promote it over a live installation with 2 back-to-back directory
  renames; each already added its own in-process self-heal for the
  narrow gap between them, but that only survives an exception inside
  the same Python call stack - a full process crash, `kill -9`, power
  loss, or a reboot mid-promotion leaves nothing to run.
  `PromotionJournal` writes a `PromotionRecord` to a small JSON file,
  atomically (write-to-temp + `os.replace`), BEFORE the first real
  filesystem mutation - `begin()`/`advance()`/`complete()`/`pending()`.
  `recover(journal)` finds every promotion left short of `COMPLETE` and
  applies the same real self-heal rule those installers' own inline code
  already uses (restore `backup_path` -> `target_path` if the crash
  happened right after the first rename; nothing to do if it happened
  after the second), generalized so it also survives the process itself
  having died - runnable the NEXT time an installer starts, not only
  within the same run. A record whose filesystem state genuinely can't
  be resolved (neither `target_path` nor `backup_path` exist) is left
  pending for a human rather than silently pruned.
- 16 new tests (`test_promotion_journal.py`), including a real crash
  simulation restored by a completely fresh `PromotionJournal` instance,
  a corrupt-journal-file degradation path, and an unresolvable case left
  pending on purpose. New example
  (`examples/python/recover_interrupted_promotion.py`).

## [0.1.7] - Cross-service failure tracing + a real observability toolkit

### Added

- **`clients/python/src/hydra_umc_sdk/lifecycle.py`** - a real observability
  deliverable. `ProcessLifecycleState` (`alive`/`ready`/`degraded`/
  `disconnected`/`unknown`) - 5 real, distinct process-liveness
  states, never collapsed into a boolean "up"/"down". Distinct
  from `HealthReport`/`SafetyState` (a ROBOT's or MACHINE's own safety
  state) - a different, complementary concern.
  `StructuredLogEntry(component, correlation_id, version, timestamp_utc,
  level, message, error_cause, caused_by)` - the payload a service puts
  inside an existing `EventEnvelope`, not a competing wire shape.
  `caused_by` is the field that makes real cross-service tracing
  possible: `trace_first_failure()` walks a `caused_by` chain
  across however many services' own log entries back to the ACTUAL first
  component that failed - not whichever entry a caller happened to look
  at first (in practice, usually the LAST service to notice and report
  it, since that's typically the one an operator gets paged for). Stops
  honestly at the earliest entry actually collected if the chain extends
  further back than what was gathered, and never loops forever on a
  cyclic `caused_by` reference in malformed input.
  `StructuredLogEntry.redacted(redactor)` - exporting a sanitized
  diagnostic as real code: only `message`/`error_cause` are ever passed
  through a redactor, every structural field (`component`/
  `correlation_id`/`version`/`caused_by`) is left untouched, since those
  are identifiers, never where a real secret would land.
  `BoundedLog(max_entries)` - bounding the size of logs, queues and
  retries as enforced behavior: drops the OLDEST entry once over
  capacity (same drop-oldest policy this ecosystem's own bounded queues
  already use elsewhere, e.g. HYDRA-UMC's `RelayRxQueue`), tracks
  `dropped_count`.
- 14 new tests (`test_lifecycle.py`), including a real multi-service
  cause-chain trace (`urtc-relay` -> `hydra-umc-server` -> `studio`) and
  a new example (`examples/python/trace_first_failure.py`) walking that
  exact scenario end to end, redaction included.

## [0.1.6] - New `Operation` contract: shared, strict, versioned lifecycle

### Added

- **`contracts/json-schema/v1/operation.schema.json`** - a shared shape for anything crossing
  a service boundary in this ecosystem (SERVER, ORCHESTRATOR, DEV-SERVER,
  OPS-AGENT, ...) to report its own real progress through 6 genuinely
  distinct states - `received`, `authorized`, `queued`, `sent`,
  `confirmed`, `terminated` (plus `rejected`) - instead of collapsing
  everything into a single "executed" bucket. `target` names what the
  operation is directed at (`kind`/`id`, domain-agnostic on purpose);
  `correlation_id` ties related operations together; `params` carries the
  operation-specific payload; `error` is optional and only meaningful
  once `rejected`.
- **`clients/python/src/hydra_umc_sdk/operation.py`** - the real,
  enforced lifecycle: `validate_status_transition(previous, next)` is the
  concrete enforcement of that idea - never collapsing every real state into
  a single "executed" bucket - the only
  legal forward path is received -> authorized -> queued -> sent ->
  confirmed -> terminated, `rejected` is reachable from any non-terminal
  status but nothing is ever reachable FROM a terminal one. `is_terminal()`
  and a small validated `OperationRecord` dataclass round out the module.
  Distinct from `bridge_contract.py`'s own `BridgeJob`/`JobPhase` (a
  narrower, domain-specific safety gate for external machine bridges) -
  the two are not redundant.
- Vendored to `clients/{go,rust,typescript}/schemas/`, `manifest.json`
  regenerated in all 4 locations, `conformance/fixtures/v1/operation.
  {valid,invalid}.json` (the invalid fixture uses `status: "executed"` -
  exactly the collapsed bucket this contract exists to forbid), and a new
  example (`examples/python/operation_lifecycle.py`).
- 12 new Python tests (`test_operation.py` + `test_validation.py`), 1 new
  Rust conformance test (embedded schema), 4 new TypeScript fixture tests,
  1 new Go fixture round-trip.

### Fixed

- **Real cross-client drift found while adding this contract**:
  `ScenarioOutcome` (added in 0.1.5) had a published schema and a working
  Python validator entry, but was never added to the Go client's
  `contractFiles` map or the TypeScript client's `ContractName` type/
  `CONTRACT_FILES` map - `tools/verify_contract_matrix.py` only ever
  cross-checked the Python validator against the schema files, so this
  went uncaught through a whole prior contract addition. Both clients
  fixed (`ScenarioOutcome` and `Operation` now both wired end to end in
  all 4 languages); `verify_contract_matrix.py` extended with a real
  Go/TypeScript coverage cross-check so this drift class can't recur
  silently again. `docs/PYTHON_CLIENT.md`'s own required-fields table was
  also missing `ProjectManifest` and `ScenarioOutcome` rows (pre-existing
  gaps, unrelated to this specific drift) - added, alongside the new
  `Operation` row.

## [0.1.5] - New `ScenarioOutcome` contract + a real before/after check

### Added

- **`contracts/json-schema/v1/scenario-outcome.schema.json`** - one run
  of a fixed reproduction scenario, `before` or `after` a candidate fix:
  a stable `scenario_id` + `repro_case` say WHAT is reproduced, `run_id`
  + `base_fingerprint` pin THIS run to an exact source state, and
  `observed.outcome` (`reproduced` / `not-reproduced` / `error`) says
  what happened. Vendored into the Go/Rust/TypeScript client
  `schemas/`; `conformance/fixtures/v1/scenario-outcome.{valid,invalid}.json`
  added; `validation.py` gained the matching `ScenarioOutcome` entry so
  `tools/verify_contract_matrix.py` still passes (`contracts=8`).
- **`clients/python/src/hydra_umc_sdk/scenario.py`** - `compare_runs(before,
  after) -> ScenarioComparison`, the reference consumer. It is the same
  "apparent success" control HYDRA-UMC-DEV-SERVER's own DS08 repair cycle
  applies, published once so every promotion path (DEV-SERVER,
  HYDRA-UMC-OPS-AGENT) judges a pair the same way. Verdicts:
  `regression-fixed` (reproduced before, not after, **and the base
  genuinely moved**), `still-broken`, `apparent-success` (stopped
  reproducing but the base fingerprint never changed - nothing was
  applied), `inconclusive` (phases out of order, a different
  `scenario_id`/`repro_case` - evidence for the wrong case - the
  after-run errored, or the before-run never reproduced the failure).
  Only a genuine `regression-fixed` is `is_promotable`.
- `examples/python/compare_scenario_runs.py` - two real recorded runs
  (an `apparent-success` and a `regression-fixed`) and the verdict for
  each.
- 12 new tests (`clients/python/tests/test_scenario.py` + `ScenarioOutcome`
  cases in `test_validation.py`).

## [0.1.4] - docs/BRIDGE_CONTRACT.md: list all 8 bridges that actually use it

### Fixed

- `docs/BRIDGE_CONTRACT.md`'s own scope line only listed 5 of the 8
  bridges that genuinely import `bridge_contract.py`/call
  `evaluate_job()` - `HYDRA-UMC-BRIDGE-AMR`, `HYDRA-UMC-BRIDGE-DROIDS`
  and `HYDRA-UMC-BRIDGE-UAV` were missing despite using the same real
  contract, confirmed by grepping every bridge's own source. Added,
  plus their own bridge-specific meaning entries.
- Removed a private-document allusion from `CHANGELOG.md`'s own 0.1.3
  entry and from `validation.py`'s own comment for the same change - a
  compatible manifest extension is documented on its own real merits,
  never by citing an unnamed external plan's section number.

## [0.1.3] - ProjectManifest: new `deployment_target` value `dev-server`

### Added

- `clients/python/src/hydra_umc_sdk/validation.py` - `"dev-server"` added
  to `PROJECT_MANIFEST_ENUMS["deployment_target"]` for the new
  HYDRA-UMC-DEV-SERVER project (a Raspberry Pi 5/CM5 host dedicated to
  development and task execution, distinct from `"cm5"`, the operational
  node that talks to real machines/robots). A compatible manifest
  extension - no existing value changed meaning, no consumer needs to
  change. New test `test_accepts_dev_server_deployment_target`.

## [0.1.2] - BridgeJob's direct constructor now validates `parameters` before using it

### Fixed

- **`clients/python/src/hydra_umc_sdk/bridge_contract.py`'s `BridgeJob`**
  (found in a second review pass; same class of gap as
  the [0.1.1] fix below, this time on `parameters` instead of
  `phase`/`machine_state`): `parameters` is typed as `Mapping[str, str]`
  in the dataclass annotation, but Python never enforces that at
  runtime. `job_from_dict()` already guarded this before ever
  constructing a `BridgeJob` (its own `isinstance(parameters, Mapping)`
  check), but the public constructor's own `__post_init__` called
  `self.parameters.items()` directly with no equivalent guard -
  constructing `BridgeJob(..., parameters=[])` directly used to raise a
  bare `AttributeError: 'list' object has no attribute 'items'` instead
  of the intended `BridgeError` every other invalid-shape input on this
  same constructor already raises. `__post_init__` now checks
  `isinstance(self.parameters, Mapping)` first, so every construction
  path fails the same clean way. 2 new regression tests reproduce the
  finding's own exact scenario (a list, and a real mapping with a
  non-string value, both rejected with `BridgeError`).
  **Checked for the same ecosystem-wide breakage the [0.1.1] fix caused
  (5 consumer bridges' own tests broke on that fix):** every real
  `BridgeJob(...)` call site across the ecosystem (all 9 bridges plus
  CONNECTOR-HUB's `sdk_gate.py`) was grepped - every one already passes
  a real `dict`/`{}` or another job's own already-valid `.parameters`,
  never a list or other non-mapping. No consumer breakage from this
  fix. `PYTHONPATH=clients/python/src python -m unittest discover -s
  clients/python/tests -v`: 53/53 passing.

## [0.1.1] - Enforce real enum membership at the BridgeJob constructor

### Fixed

- **`clients/python/src/hydra_umc_sdk/bridge_contract.py`'s `BridgeJob`:**
  `phase`/`machine_state` are typed as `JobPhase`/`MachineState` in the
  dataclass annotation, but Python never enforces that at runtime -
  constructing `BridgeJob` directly (not through `job_from_dict`, which
  already validated this) with an unrecognised string for either field
  used to construct successfully, and `evaluate_job` could then return
  `allowed=True` for a phase it never actually recognised (`job.phase is
  JobPhase.ABORT` is simply `False` for a garbage value, falling through
  to the same "ready" path a real, known phase would take).
  `__post_init__` now rejects a non-`JobPhase`/non-`MachineState` value
  outright, so the public constructor and `job_from_dict` reject the
  exact same invalid input identically. 2 new regression tests reproduce
  the finding's own exact scenario. `PYTHONPATH=clients/python/src
  python -m unittest discover -s clients/python/tests -v`: 51/51
  passing.

## [0.1.0] - Real first OpenAPI v1 slice for HYDRA-UMC-SERVER's own HTTP surface

### Added

- **`contracts/openapi/v1/server.openapi.json`** (new) - the SDK's own charter
  (`docs/API_DESIGN.md`) commits to publishing "the OpenAPI source and typed
  clients"; this is its first real slice, hand-verified against
  HYDRA-UMC-SERVER's own `src/server.ts`, not a placeholder. Covers
  discovery (`GET /api/hydra-info`), authentication (`POST /api/login`), the
  fleet roster (`GET`/`POST /api/settings`), and the real-time command plane
  (`POST /api/robot/{id}/command`, all 13 real command types: stop, play,
  pause, jog, reset, jogStep, reset3D, tool, valve, pump, speed, trajectory,
  vision - each modeled as its own `oneOf` variant with a `command`
  discriminator). Deliberately does not cover every route in `server.ts`:
  admin-only account/log/integration management, camera process
  supervision, CAN-OTA transfer, and power/system-service control are real
  but operational rather than SDK-contract surface, left for a later slice.
  Honestly documents one real discrepancy instead of papering over it:
  `docs/API_DESIGN.md`'s own command-result vocabulary
  (`ACCEPTED`/`REJECTED`/`RUNNING`/`COMPLETED`/`FAILED` plus a correlation
  identifier) is not what `POST /api/robot/{id}/command` actually returns -
  the real implementation replies with a plain `{success, affectedCount}`
  once the mutation is already applied and broadcast. Fixing that gap is
  Server-side product work, out of scope for this SDK.
- **`tools/verify_openapi.py`** (new) - dependency-free structural gate
  (stdlib `json` only, matching `verify_contract_matrix.py`'s own
  convention): every declared path has a real HTTP method, and every
  `$ref`/discriminator mapping target actually resolves inside the
  document. Also validated once by hand against `openapi-spec-validator`'s
  real OAS 3.1 validator while authoring the document (not vendored as a
  dependency here, to keep this repository's own tooling dependency-free).
  Wired into both `tools/build_test.py` and `.github/workflows/ci.yml`.

### Fixed

- **`.github/workflows/ci.yml`** - found while wiring in the check above:
  `tools/verify_contract_matrix.py` was already documented
  (`docs/CONTRACTS.md`) as this SDK's "mandatory compatibility gate", but
  this repository's own real CI workflow never actually ran it - only the
  local, non-CI `tools/build_test.py` did. Real CI now runs both
  `verify_contract_matrix.py` and the new `verify_openapi.py`.
- **`bump_version.py`** - its own auto-generated CHANGELOG stub entry
  embedded a literal calendar date (`date.today().isoformat()`) into this
  public file - every real entry in this CHANGELOG is dated only by its
  position, never a literal date. Removed before it could ever actually
  land one (this repository's version history shows no prior real build
  ran the script mechanically without hand-editing the stub first).

## [0.0.9] - Fix the TypeScript client's real CI failure on Node 20

### Fixed

- **`clients/typescript`** - the real GitHub Actions run for `[0.0.8]`
  failed: `npm test` executed `tests/*.test.mts` directly via `node
  --test`, relying on Node's unflagged TypeScript type stripping (only
  available from Node v22.18/v23.6 onward). It passed locally only
  because local development happened on a newer Node than this
  repository's own CI pins (`node-version: "20"` in
  `.github/workflows/ci.yml`, matching `package.json`'s declared
  `"engines": {"node": ">=20"}`) - so it broke silently until the actual
  workflow run was checked, not just simulated locally. Fixed by adding
  `tsconfig.test.json` (a second, test-only config compiling
  `tests/**/*.mts` to a git-ignored `dist-tests/`) and having `npm test`
  run the compiled `.mjs` output instead of the TypeScript source, so the
  test run no longer depends on that newer runtime feature at all.
  Re-verified against a clean `npm ci --ignore-scripts` (matching CI
  exactly, not a reused local `node_modules`): `npm run typecheck`,
  `npm test` (22/22), and `npm run lint --if-present` all pass.

## [0.0.8] - Go, TypeScript and Rust reference clients

### Added

- **`clients/go`** - real, tested Go reference client: hand-written struct
  types field-for-field from the v1 schemas (`types.go`), a custom
  `MarshalJSON`/`UnmarshalJSON` pair for `native_version.pattern`'s real
  `oneOf` shape (`native_version_pattern.go`, since `encoding/json` has no
  native union-type support), and real Draft 2020-12 validation
  (`validation.go`) via `github.com/santhosh-tekuri/jsonschema/v5`
  compiling this client's own `//go:embed`-vendored schema copies -
  enforcing the full published schema, not a reimplemented subset.
- **`clients/typescript`** - real, tested TypeScript reference client:
  hand-written interfaces (`src/types.ts`) and real Draft 2020-12
  validation (`src/validation.ts`) via Ajv (`ajv` + `ajv-formats`)
  compiling this package's own vendored `schemas/`.
- **`clients/rust`** - real, tested Rust reference client: hand-written
  structs (`src/types.rs`, including a real `#[serde(untagged)]` enum for
  `native_version.pattern`'s `oneOf`) and real Draft 2020-12 validation
  (`src/validation.rs`) via the `jsonschema` crate compiling this crate's
  own `include_str!`-embedded schema copies, with `should_validate_formats(true)`
  set explicitly since format validation is draft-dependent and not on by
  default in that crate.
- Every one of the three new clients has its own anti-drift test proving
  its vendored `schemas/*.json` stays byte-identical to
  `contracts/json-schema/v1/`, and its own full pass over
  `conformance/fixtures/v1/*.valid.json`/`*.invalid.json` - the same
  fixtures the Python reference client's own tests already use.

### Fixed

- **`.github/workflows/ci.yml`** - the Node/TypeScript, Rust and Go
  validation steps only ever looked for `package.json`/`Cargo.toml`/`go.mod`
  at the repository root (`hashFiles('package.json')` etc. are not
  recursive), so none of them ever actually ran for this repository's own
  `clients/go`, `clients/rust` and `clients/typescript` - a real, silent
  CI gap now closed by also matching `clients/**/package.json` etc. and by
  `cd`-ing into the discovered client directory before running
  `npm`/`cargo`/`go`, mirroring the existing Go step's own module-discovery
  pattern.
- **`contracts/json-schema/v1/manifest.json`** - the recorded sha256 for
  `update-manifest.schema.json` was stale (the schema file was edited for
  the `[0.0.5]` SemVer `pattern` addition, but the manifest was never
  regenerated afterwards). Every one of the three new clients' own
  integrity check caught this independently; fixed by re-running
  `contracts/generate_manifest.py` and correcting the one stale digest.

## [0.0.7] - Real JSON wire shape for BridgeJob/GateDecision

### Added

- **`bridge_contract.py`** - `job_to_dict()`/`job_from_dict()`/
  `decision_to_dict()`, the real shared JSON shape for a `BridgeJob`/
  `GateDecision` now that `HYDRA-UMC-BRIDGE-CNC`/`-LASER`/`-OPENPNP`/
  `-PRINTER3D`/`-ROS2` all reach `HYDRA-UMC-MQTT-BROKER`: one wire format
  every bridge parses/serializes identically, instead of each one
  reinventing its own ad-hoc JSON mapping for the same dataclass.
  `job_from_dict()` fails closed with `BridgeError` (never a bare
  `KeyError`/`ValueError`/`AttributeError`) on malformed input - the real
  parse boundary for a job arriving over an untrusted external transport
  (an MQTT PUBLISH payload, in practice). 8 new tests, including a real
  round-trip and every rejected-input case.

## [0.0.6] - Dependency-free mock server for testing without hardware

### Added

- **`hydra-umc-sdk-mock-server`** (`mock_server.py`, new) - a real,
  stdlib-only HTTP server that serves one example payload per known
  contract (`GET /mock/<Contract>`, plus `GET /mock/` for the contract
  list), so a UI, adapter or integration test can be written and exercised
  against a real HTTP endpoint before any actual CM5/robot/MCU hardware
  exists to talk to. Every example is proven, by this module's own tests,
  to pass this SDK's real `validate()` for its declared contract - the
  mock can never silently drift from what the SDK itself considers valid.
  Fails loudly at import time (not silently at first request) if a
  contract and its example payload ever fall out of 1:1 sync. Not a fake
  robot or a device-behavior simulation: every route is a static GET,
  nothing is ever accepted as a write, and no claim about real timing,
  concurrency, or physical state is made. 6 new tests, including a real
  end-to-end HTTP round-trip per contract over an ephemeral port.
- Added a named `HYDRA-UMC-OS` producer-fixture index and extended the
  contract matrix to validate every producer-declared contract payload. This
  makes producer evidence executable rather than unexamined JSON alongside
  the generic valid/invalid fixtures.

## [0.0.5] - Strict semver enforcement on UpdateManifest.version, wider fixture coverage

### Fixed

- **`validation.py`** - `UpdateManifest.version` was only checked for a
  matching `sha256`; a value like `"latest"` or `"v1"` passed straight
  through. It's now validated against the same `SEMVER_PATTERN` already
  used elsewhere in this file, and `update-manifest.schema.json` gained
  the matching JSON Schema `pattern`, so the reference validator and the
  published schema agree again.

### Added

- **Invalid conformance fixtures for every contract that was missing
  one** (`device-descriptor.invalid.json`, `event-envelope.invalid.json`,
  `safety-state.invalid.json`/`.valid.json`,
  `server-discovery.invalid.json`,
  `update-manifest.invalid.json`/`.valid.json`) - the compatibility
  matrix's own claim to check "one accepted and one rejected payload per
  contract" (see `docs/CONTRACTS.md`) wasn't true yet for these; now it
  is. New `CONTRACT_MATRIX_UPDATE_VERSION` check in
  `tools/verify_contract_matrix.py` proves the non-semver rejection
  directly. 35/35 tests passing, 14/14 fixtures across all 7 contracts.

## External machine bridge contract (no odometer bump)

Landed after [0.0.4] and before [0.0.5] above without going through the
odometer build script - `evaluate_job()` and `BridgeJob` were already in
use by [0.0.5]'s "all 7 contracts" fixture count, and [0.0.7] later
extends this same contract with its real JSON wire shape.

### Added

- Public, dependency-free Python v0 external-machine bridge contract:
  `BridgeJob`, bridge/machine/cell state enums and `evaluate_job()` safety
  gate. It is the shared high-level boundary for the ROS 2, OpenPnP, 3D
  printer, CNC and laser integrations; it does not expose motion control.
- `docs/BRIDGE_CONTRACT.md` and five focused unit tests proving productive
  work is rejected when either side is not ready while `ABORT` remains
  requestable through the authorised safety path.

### Fixed

- UpdateManifest validation now requires an HTTPS artifact URL with a real
  hostname, rejecting malformed strings such as `https:///artifact.deb`.

- The dependency-free Python validator now rejects invalid RFC 3339
  `timestamp_utc` values and JSON booleans supplied where the `EventEnvelope`
  sequence or `ServerDiscovery` numeric counters require integers. Python
  treats `bool` as an `int` subclass, which previously let invalid contract
  payloads pass reference validation.

## [0.0.4] - Automatic contract/validator compatibility matrix

### Added

- **`tools/verify_contract_matrix.py`** (new) - a real, automatic compatibility matrix between the published v1 JSON Schema files and this SDK's own Python reference validator. It discovers every real `*.schema.json` under `contracts/json-schema/v1/`, cross-checks that each one has a matching `validate()` entry (and vice versa - a stale validator entry with no real schema file is flagged too), runs every conformance fixture through `validate()` and confirms it's judged the way its own `.valid.json`/`.invalid.json` filename claims, and proves the two negative cases this matrix specifically guards: an unknown contract name and an incompatible `schema_version`.
- **`ProjectManifest` contract validation** (`validation.py`) - the matrix immediately found a real, concrete gap it was built to catch: `project-manifest.schema.json` (the `hydra-umc.project.json` contract every repository in this ecosystem publishes) had no corresponding entry in the Python validator at all - it could never actually be validated. Added the real required-field/enum/pattern checks mirroring the schema (`ecosystem`, `name` pattern, semver `version`, `role`/`deployment_target`/`maturity` enums, non-empty unique `technologies`, nullable `parent`, `native_version`'s string-or-component `pattern`), plus real conformance fixtures (`project-manifest.valid.json`/`.invalid.json`).
- 22 new tests (`test_validation.py`) = 30 total.

### Fixed

- `tools/build_test.py`'s non-mutating `build-test.sh` check compiled Python sources but never actually ran the real conformance test suite (`clients/python/tests`) or the new contract matrix - both are now wired in, so the "test" step genuinely tests something.

### Changed

- Automated build version increment from 0.0.3.

## Documentation

### Added

- `docs/PYTHON_CLIENT.md` - full reference for the `validate()` function
  and `hydra-umc-contract-validate` CLI in `clients/python`: the exact
  required-fields and extra-validation-rule table for all 6 contracts
  (`DeviceDescriptor`, `HealthReport`, `SafetyState`, `UpdateManifest`,
  `EventEnvelope`, `ServerDiscovery`), previously only readable from
  `validation.py`'s own source. Verified live against the real function
  and CLI. Linked from `docs/CONTRACTS.md`. Documentation-only - no code
  changed, no version bump.

## [0.0.3]

### Changed

- Automated build version increment from 0.0.2.

## [0.0.2]

### Added

- JSON Schema v1 for `DeviceDescriptor`, `HealthReport`, `SafetyState`, and
  `UpdateManifest`.
- Dependency-free Python reference validator and command-line entry point.
- Valid and invalid conformance fixtures plus four host-side validation tests.
- Runnable Python example for `HealthReport` validation.

### Limits

- Protobuf, OpenAPI, package publication, and non-Python clients are not part
  of this initial contract release.

## [0.0.1]

### Added

- Initial SDK documentation, multilingual README files, and target layout.
- Contract, API, conformance, and adapter-boundary specifications.
