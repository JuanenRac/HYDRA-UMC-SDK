// =============================================================================
// HYDRA-UMC Kotlin app common - src/test/kotlin/com/hydraumc/common/SemanticVersionTest.kt
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================
package com.hydraumc.common

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class SemanticVersionTest {
    @Test
    fun `accepts stable release tags with or without v prefix`() {
        assertEquals(SemanticVersion(1, 2, 3), SemanticVersion.parseStable("v1.2.3"))
        assertEquals(SemanticVersion(0, 1, 0), SemanticVersion.parseStable("0.1.0"))
    }

    @Test
    fun `rejects draft style non-stable tags instead of guessing`() {
        assertNull(SemanticVersion.parseStable("v1.2.3-beta.1"))
        assertNull(SemanticVersion.parseStable("release-1.2.3"))
        assertNull(SemanticVersion.parseStable("1.2"))
    }

    @Test
    fun `orders versions by major minor patch`() {
        assertTrue(SemanticVersion(0, 1, 9) < SemanticVersion(0, 2, 0))
        assertTrue(SemanticVersion(1, 0, 0) > SemanticVersion(0, 9, 9))
    }

    @Test
    fun `reads and orders an optional fourth component`() {
        assertEquals(SemanticVersion(0, 8, 0, 3), SemanticVersion.parseStable("v0.8.0.3"))
        assertEquals("0.8.0.3", SemanticVersion.parseStable("0.8.0.3").toString())
        assertNull(SemanticVersion.parseStable("0.8.0.3.1"))
        assertTrue(SemanticVersion(0, 7, 9) < SemanticVersion(0, 8, 0, 0))
        assertTrue(SemanticVersion(0, 8, 0, 9) < SemanticVersion(0, 8, 1, 0))
        assertEquals(0, SemanticVersion(0, 8, 0).compareTo(SemanticVersion(0, 8, 0, 0)))
    }
}
