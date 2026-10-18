// =============================================================================
// HYDRA-UMC-SDK - Go reference client tests: concurrent validation
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

package hydraumc

import (
	"sync"
	"testing"
)

// A server validates from many goroutines at once. The compiled-schema cache
// used to be an unguarded map, which crashes the process ("concurrent map
// writes") or is reported by `go test -race`.
func TestValidateIsSafeFromManyGoroutines(t *testing.T) {
	payload := map[string]interface{}{
		"schema_version": "1.0",
		"state":          "READY",
		"source":         "test",
		"timestamp_utc":  "2026-01-01T00:00:00Z",
	}
	var wg sync.WaitGroup
	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for _, contract := range KnownContracts() {
				_ = Validate(contract, payload)
			}
		}()
	}
	wg.Wait()
}
