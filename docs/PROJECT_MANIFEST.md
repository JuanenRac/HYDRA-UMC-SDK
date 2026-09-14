<!--
=============================================================================
HYDRA-UMC-SDK - Universal project manifest contract
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
CC BY-SA 4.0 - see LICENSE.md
=============================================================================
-->

# Universal project manifest

Every HYDRA-UMC and URTC repository owns a root-level
`hydra-umc.project.json`. It is the public, machine-readable declaration of
the repository release version, role, technology stack, deployment target,
maturity and ecosystem relationships.

The contract is defined by
[`project-manifest.schema.json`](../contracts/json-schema/v1/project-manifest.schema.json).
The dashboard fetches this exact file from GitHub when it is generated. No
project metadata is written manually into `docs/index.html`.

## Editing rules

- Edit `maturity`, `role`, `stack`, `technologies`, `deployment_target`,
  `family`, `parent`, `build` and `notes` in the repository that owns them.
- Use only the enum values declared by the schema.
- Set `parent` to `null` for a family root; otherwise it must name another
  ecosystem repository.
- Never put passwords, tokens, local network data or private paths in this
  public file.
- `version` is the ecosystem-visible release version. It must match the
  native version source used by that repository's compiler or packager.
- `native_version.file` and `native_version.pattern` declare that native
  source and its version parser. They are repository-owned operational
  metadata: the universal validator reads them instead of keeping a Python
  table of per-project paths or regular expressions.

## Maturity levels

The schema defines `maturity` as one of `scaffolding`, `functional`,
`established`, `production` - the enum itself was already the source of
truth, but nothing spelled out what actually distinguishes them, so
each repository's own choice was really a judgment call, not a checked
criterion. This section describes the real, observed line every
current manifest already draws, rather than inventing a new one - a
repository's own `maturity` value should not change on account of this
section alone.

- **`scaffolding`** - real, tested code exists, but it has not yet been
  exercised in its own real intended operational context: no physical
  hardware validation for a firmware/device-facing project, no
  sustained real deployment for a service, or a stated multi-delivery
  plan with a real, documented, still-open gap. A scaffolding project
  can be internally "feature-complete" against its own delivery plan
  (see `HYDRA-UMC-DEV-SERVER`, all ten deliveries shipped) and still be
  `scaffolding`, because the real, physical or sustained-operation half
  of proving it out has not happened yet.
- **`functional`** - real capability shipped and exercised against some
  real, physical target (see `URTC`: firmware flashed and running real
  physical tool heads), but not yet to the breadth or duration
  `established` implies - typically a hardware-adjacent project where
  reaching sustained, broad real-world operation is inherently slower
  than for a pure software service.
- **`established`** - the common case today (the large majority of
  repositories): real, tested code that has also seen real, sustained
  use in this ecosystem's own actual deployment (the real CM5 at
  `192.168.0.180`/`95.60.192.108`, or equivalent real usage for a
  desktop/mobile client) - not merely "passes its own tests".
- **`production`** - reserved for a real, continuous, unattended
  deployment with no known open gap. Not used by any repository yet as
  of this writing - this ecosystem has no project that honestly clears
  that bar today.

A repository's own README "Status"/"Honesty check" section remains the
real, detailed source for exactly what still needs physical hardware or
sustained operation to close - this glossary only names the levels
that status already implies, it does not replace it.

## Promotion evidence

This section names the real evidence practice this ecosystem's own real
closures already follow - it does not invent a new bureaucratic layer,
and it does not require a second repository or registry: the existing
`docs/`, `CHANGELOG.md` and CI run of the repository being changed are
enough.

A real change worth keeping a record of should leave, in that
repository's own `CHANGELOG.md` entry (or an equivalent commit message
for a change too small for its own entry), enough to answer: what
changed and why, the exact command/test that was run to check it, what
environment it ran in (host-only, a real CI runner, real hardware),
the result, and any known limitation or dependency/consumer that would
need re-checking if this changes again. Never a token, a private IP, a
real username, or an unredacted log/snapshot - a real secret-scan
finding blocks the record the same way it blocks a build (see
`HYDRA-UMC-OS-REBUILDER`'s own `BuildResult(ok=False, ...)` convention
for the same principle applied to image builds).

Keep these four apart, in what the record actually claims, rather than
letting a lighter one stand in for a heavier one:

- a unit test (pure logic, no real process or device on the other end);
- a loopback/integration test against a real running process (real
  code exercised, no physical hardware);
- an emulation (a fake standing in for hardware/a driver - proves this
  code's own handling of a *simulated* condition, never that the real
  hardware/driver itself works);
- a real physical-bench or supervised-operation result (the only kind
  that proves real hardware actually works).

Acceptance: someone else can reproduce the same functional result from
a clean checkout by following the record, and a failure or an
intentionally out-of-scope part stays visible in the record - it is
never edited out to make a change look more complete than it was.

## Promotion gate

Before changing a repository's own `maturity` in its
`hydra-umc.project.json`, the same real gate this ecosystem's own
actual promotions already apply:

1. The repository's own real known blockers, and any blocker on the
   real dependency path a change to it would affect, are closed first.
2. Its own tests pass, AND the real, affected consumer's own tests
   still pass against the changed code - not just this repository in
   isolation.
3. A real, non-incremental build/test run (equivalent to a fresh
   checkout, not relying on stale local build state) passes.
4. The package this repository actually produces installs and runs
   OUTSIDE its own checkout - a real "does this work for someone who
   only just cloned it" check, not merely "works in my own working
   tree".
5. At least one real good case and one real bad case are exercised -
   a genuine failure path checked for real, never only the happy path.
6. `hydra-umc.project.json`, `CHANGELOG.md`, `README.md` and all 6
   translations, and any usage documentation, are brought back in sync
   with what actually shipped - including the README directory
   structure section, in all 7 languages, if real files were added.

`established` adds one more real requirement on top of the above: a
restart, a cancellation, a lost dependency, and a recovery are each
exercised for real within the scope being promoted, not merely assumed
to work because the happy path does.

Only once every step above is genuinely true does `maturity` actually
change - and the change should describe exactly the scope that was
tested, never claim a wider one than what was genuinely exercised.

## Version rule

The compiler may still require `pyproject.toml`, `package.json`, `Cargo.toml`,
a firmware header or a platform-native file. Those locations and parsers are
declared in `native_version`, while the files themselves remain implementation
details. A build-version tool must update its native source and
`hydra-umc.project.json` together; the full-workspace validator in
HYDRA-UMC-UPDATER rejects a mismatch.

This rule preserves real language and firmware toolchains without making the
ecosystem catalog depend on seventeen different version-file conventions.
