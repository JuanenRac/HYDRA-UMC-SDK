// =============================================================================
// HYDRA-UMC-SDK - Go reference client: anti-drift check for vendored schemas
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

package hydraumc

import (
	"bytes"
	"os"
	"path/filepath"
	"testing"
)

// TestVendoredSchemasMatchCanonical proves this client's embedded
// schemas/*.json (validation.go's go:embed) are byte-identical to the
// normative contracts/json-schema/v1/*.json this monorepo publishes -
// real, automatic proof the vendored copies never silently drift from the
// source of truth, the same guarantee tools/verify_contract_matrix.py
// gives the Python reference validator.
func TestVendoredSchemasMatchCanonical(t *testing.T) {
	canonicalDir, err := filepath.Abs(filepath.Join("..", "..", "contracts", "json-schema", "v1"))
	if err != nil {
		t.Fatalf("cannot resolve canonical schema directory: %v", err)
	}
	if info, statErr := os.Stat(canonicalDir); statErr != nil || !info.IsDir() {
		t.Skipf("canonical contracts/json-schema/v1 not found at %s (expected inside a HYDRA-UMC-SDK checkout)", canonicalDir)
	}

	canonicalFiles, err := filepath.Glob(filepath.Join(canonicalDir, "*.json"))
	if err != nil || len(canonicalFiles) == 0 {
		t.Fatalf("no canonical schema files found under %s (err=%v)", canonicalDir, err)
	}

	vendoredNames := map[string]bool{}
	for name := range contractFiles {
		vendoredNames[contractFiles[name]] = true
	}
	vendoredNames["manifest.json"] = true

	seen := map[string]bool{}
	for _, canonicalPath := range canonicalFiles {
		name := filepath.Base(canonicalPath)
		seen[name] = true
		canonicalBytes, err := os.ReadFile(canonicalPath)
		if err != nil {
			t.Fatalf("cannot read canonical %s: %v", name, err)
		}
		embeddedBytes, err := schemas.ReadFile("schemas/" + name)
		if err != nil {
			t.Fatalf("%s exists in contracts/json-schema/v1 but is not vendored under clients/go/schemas: %v", name, err)
		}
		if !bytes.Equal(canonicalBytes, embeddedBytes) {
			t.Errorf("clients/go/schemas/%s has drifted from contracts/json-schema/v1/%s", name, name)
		}
	}

	for name := range vendoredNames {
		if !seen[name] {
			t.Errorf("clients/go/schemas/%s is vendored but contracts/json-schema/v1/%s no longer exists", name, name)
		}
	}
}
