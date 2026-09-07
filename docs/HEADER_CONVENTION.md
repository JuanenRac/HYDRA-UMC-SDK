<!--
=============================================================================
HYDRA-UMC-SDK - Documentation header convention
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
CC BY-SA 4.0 - see LICENSE.md
=============================================================================
-->

# Header convention

Use this header at the beginning of new source and documentation files.

Executable `.sh` and `.bat` files must also print a visible banner at launch:
project name, script filename, concise operation, copyright, email and license.

| File type | Comment form | License line |
| --- | --- | --- |
| Source code | `#` or the native comment syntax | `GPL-3.0-or-later - see LICENSE` |
| Markdown documentation | `<!-- ... -->` | `CC BY-SA 4.0 - see LICENSE.md` |
| JSON / JSON Schema | No comment header; comments would invalidate JSON | Keep licensing in repository metadata and adjacent documentation. |

The project name in every header must be `HYDRA-UMC-SDK`, never `HYDRA`
alone, and must be followed by a short, file-specific responsibility.
