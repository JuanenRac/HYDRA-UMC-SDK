# Testing strategy

The shared, ecosystem-wide levels, evidence shape, and fixture conventions
every repository's own `build-test`/`ci_validate`/CI workflow already
approximates on its own. This exists to name that convention explicitly, so
a repo can check itself against it instead of reinventing its own rules.
`compare_runs()` (see the main README's "Contracts" section, and
`clients/python/src/hydra_umc_sdk/scenario.py`) is the shared
"was it actually fixed" check this strategy's own reproducible-scenario
level (below) relies on.

## Levels

Run the smallest check that actually covers the change:

- **Every change**: syntax, formatting, metadata validation, unit tests and
  regressions of the component touched. This is what a repo's own
  `build-test`/`ci_validate` already runs on every push.
- **Contract changes**: the producer/consumer matrix for the changed
  contract (see [CONFORMANCE.md](CONFORMANCE.md) and
  `tools/verify_contract_matrix.py`).
- **Scheduled or manually-scoped runs**: cross-process/cross-package
  integration (a bridge against its own protocol emulator, a client
  against a real local server instance).
- **Before a release candidate**: clean install, migrations, restoration,
  and a long-running session (see "Reproducible campaigns" below).

Do not run every heavy build of every project on every documentation change.
Scope checks to the paths and dependencies that actually changed, and avoid a
workflow that updates metadata triggering itself recursively.

Never hide a failure to reduce noise. Distinguish a new failure, a repeated
one, an external service being unavailable, and a skipped test. A skip must
say what evidence is missing - it is never counted as a pass.

## Platform matrix

Record the real combination exercised: OS, architecture, runtime, and tool
versions. Prioritize the platforms a project actually targets. Test `.bat`
and `.sh` scripts in their own real environment - do not assume one implies
the other. In CI, never block on a confirmation prompt; in an interactive
run, keep the user-requested "press Enter to close" behavior, but always
propagate the real exit code. Do not install a duplicate toolchain when a
valid one is already present on the machine.

## Minimum evidence per result

A real test result records, at minimum:

- Project, commit (or a patch hash when there is no commit yet).
- The exact command, environment, dependencies, and fixture version.
- Expected result, actual result, and case count.
- Time and resources observed, and the run's own limits.
- Evidence level (see [CONFORMANCE.md](CONFORMANCE.md)'s E0-E4 scale) and
  whether real hardware was actually connected.
- A reference to the issue this closes and the test that prevents its
  return.

For a `ScenarioOutcome` pair (`compare_runs()`), also record:
`run_id` and generation, `scenario_id`, model configuration/hash where
applicable, seed, clock mode, active observers, coverage window, and the
reason for any value that could not be measured. Missing fields are never
filled in with an assumption - document what was not measured instead.

Public logs must be sanitized. Never make a private artifact a required
input for an external user to reproduce a result.

## Reproducible campaigns

Starting targets, adjustable by cost and observed behavior - not results
already obtained, and not a universal requirement for every project:

- Ten runs of a critical path against the same data with a stable result.
- Fifty disconnect/reconnect cycles of a simulated transport.
- A restart at every persistence boundary of an update or mission.
- A four-hour isolated session before attempting a twenty-four-hour one.

Measure a baseline first, then set a resource budget. A long run does not
prove the absence of a leak by itself - watch the trend and the cause, not
just whether it finished.

## Independent fixtures

Document the provenance and expectation of each case. Include targeted
negative controls: altering an axis, a scale, a timestamp, or an attempt/
resource identity must fail the related criterion. Alterations happen only
in test fixtures/workspaces, never in production.

A conversion followed by its own inverse can hide two errors that cancel
out - pair a round-trip with an independently-computed expected result.
For geometry, use figures that can be computed by hand with explicit
frames. For protocols, combine minimal valid cases with malformed input and,
where they exist, authorized captures. For models, mark whether real
inference or a deterministic substitute was used. Never fabricate telemetry
presented as if it came from a real robot.

## Cost and storage

Set a disk quota for builds, temporary environments, logs, and fixtures.
Reuse already-installed tools and caches rather than duplicating a
toolchain (Flutter, an Android SDK, WSL, ...) without a documented reason.
Clean up only identified test output - never a user's own data,
repositories, or profile. Do not download a large model for a contract test
that a small fixture can already resolve.
