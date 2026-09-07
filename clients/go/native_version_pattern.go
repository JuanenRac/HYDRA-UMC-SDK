// =============================================================================
// HYDRA-UMC-SDK - Go reference client: native_version.pattern (string | object)
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

package hydraumc

import (
	"encoding/json"
	"fmt"
)

// UnmarshalJSON accepts either shape project-manifest.schema.json's
// native_version.pattern allows: a single non-empty string, or an object
// with exactly major/minor/patch string fields. Anything else is a real
// decode error, not a silently zeroed struct.
func (p *NativeVersionPattern) UnmarshalJSON(data []byte) error {
	var asString string
	if err := json.Unmarshal(data, &asString); err == nil {
		p.Pattern = asString
		p.Components = nil
		return nil
	}

	var asComponents NativeVersionPatternComponents
	if err := json.Unmarshal(data, &asComponents); err != nil {
		return fmt.Errorf("native_version.pattern must be a string or a {major,minor,patch} object: %w", err)
	}
	p.Pattern = ""
	p.Components = &asComponents
	return nil
}

// MarshalJSON is the exact inverse of UnmarshalJSON.
func (p NativeVersionPattern) MarshalJSON() ([]byte, error) {
	if p.Components != nil {
		return json.Marshal(p.Components)
	}
	return json.Marshal(p.Pattern)
}
