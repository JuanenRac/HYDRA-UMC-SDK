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

## Version rule

The compiler may still require `pyproject.toml`, `package.json`, `Cargo.toml`,
a firmware header or a platform-native file. Those locations and parsers are
declared in `native_version`, while the files themselves remain implementation
details. A build-version tool must update its native source and
`hydra-umc.project.json` together; the full-workspace validator in
HYDRA-UMC-UPDATER rejects a mismatch.

This rule preserves real language and firmware toolchains without making the
ecosystem catalog depend on seventeen different version-file conventions.
