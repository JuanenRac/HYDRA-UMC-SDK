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

## Version rule

The compiler may still require `pyproject.toml`, `package.json`, `Cargo.toml`,
a firmware header or a platform-native file. Those locations and parsers are
declared in `native_version`, while the files themselves remain implementation
details. A build-version tool must update its native source and
`hydra-umc.project.json` together; the full-workspace validator in
HYDRA-UMC-UPDATER rejects a mismatch.

This rule preserves real language and firmware toolchains without making the
ecosystem catalog depend on seventeen different version-file conventions.
