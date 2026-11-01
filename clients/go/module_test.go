// =============================================================================
// HYDRA-UMC-SDK - Go client module is importable
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================
package hydraumc

import (
	"os"
	"regexp"
	"strconv"
	"strings"
	"testing"
)

// The module is imported from another repository by its path and a tag of the
// form clients/go/vX.Y.Z. That works only while go.mod names the path of the
// subdirectory, asks for a Go version that the importers can run (the
// directive must not force a newer toolchain download) and carries nothing
// that an importing module would ignore or choke on.
const modulePath = "github.com/JuanenRac/HYDRA-UMC-SDK/clients/go"

// highestGoDirective is the newest minor version that go.mod may ask for;
// raise it only when the client really needs a newer language feature.
const highestGoDirective = 22

func TestModuleIsImportableFromAnotherRepository(t *testing.T) {
	raw, err := os.ReadFile("go.mod")
	if err != nil {
		t.Fatalf("cannot read go.mod: %v", err)
	}
	text := string(raw)
	if !strings.Contains(text, "module "+modulePath+"\n") {
		t.Errorf("go.mod must declare `module %s`", modulePath)
	}
	directive := regexp.MustCompile(`(?m)^go 1\.(\d+)(?:\.\d+)?$`).FindStringSubmatch(text)
	if directive == nil {
		t.Fatalf("go.mod has no `go 1.N` directive")
	}
	minor, _ := strconv.Atoi(directive[1])
	if minor > highestGoDirective {
		t.Errorf("go directive 1.%d forces importers to a newer toolchain than 1.%d", minor, highestGoDirective)
	}
	for _, forbidden := range []string{"\ntoolchain ", "\nreplace ", "\nexclude ", "\nretract "} {
		if strings.Contains(text, forbidden) {
			t.Errorf("go.mod must not carry a %q directive: an importing module ignores it or breaks on it", strings.TrimSpace(forbidden))
		}
	}
}
