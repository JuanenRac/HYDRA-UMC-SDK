// =============================================================================
// HYDRA-UMC Kotlin app common - src/main/kotlin/com/hydraumc/common/JsonText.kt
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================
package com.hydraumc.common

import org.json.JSONObject

/**
 * Reads a text field the way the UI means it. `JSONObject.optString` returns the four
 * letters "null" for a field that is present but JSON `null` (and for the default of a
 * missing one it returns the default), so a release without notes showed "null", a robot
 * without a name was called "null" and a login that answered `"token": null` stored the
 * token "null". `isNull` is true for both a missing key and a JSON null, so both give the
 * fallback.
 */
fun JSONObject.optStr(name: String, fallback: String = ""): String =
    if (isNull(name)) fallback else optString(name, fallback)
