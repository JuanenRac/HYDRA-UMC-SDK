// =============================================================================
// HYDRA-UMC Kotlin app common - src/test/kotlin/com/hydraumc/common/ReleaseMetadataParserTest.kt
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================
package com.hydraumc.common

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** The trust gate on an already-read release; it needs no JSON library. */
class ReleaseMetadataParserTest {
    private val asset = "APP-release.apk"

    private fun release(tag: String, url: String = "https://example.invalid/app.apk", draft: Boolean = false) =
        ReleaseInfo(tag, "Release $tag", " notes ", draft, false, listOf(ReleaseAsset(asset, url)))

    @Test
    fun `offers only a newer stable release with the exact HTTPS asset`() {
        val result = ReleaseMetadataParser.evaluate(release("v0.4.5"), "0.4.4", asset)
        assertTrue(result is UpdateCheckResult.Available)
        val update = (result as UpdateCheckResult.Available).update
        assertEquals(SemanticVersion(0, 4, 5), update.version)
        assertEquals("notes", update.notes)
    }

    @Test
    fun `the four component versions compare as the apps ship them`() {
        assertTrue(ReleaseMetadataParser.evaluate(release("v0.8.0.1"), "0.8.0", asset) is UpdateCheckResult.Available)
        assertEquals(UpdateCheckResult.UpToDate, ReleaseMetadataParser.evaluate(release("v0.8.0.0"), "0.8.0", asset))
    }

    @Test
    fun `rejects a tag that is not stable, a missing asset and a URL that is not HTTPS`() {
        assertTrue(ReleaseMetadataParser.evaluate(release("v0.4.5-beta"), "0.4.4", asset) is UpdateCheckResult.Failed)
        assertTrue(ReleaseMetadataParser.evaluate(ReleaseInfo("v0.4.5", assets = emptyList()), "0.4.4", asset) is UpdateCheckResult.Failed)
        assertTrue(ReleaseMetadataParser.evaluate(ReleaseInfo("v0.4.5"), "0.4.4", asset) is UpdateCheckResult.Failed)
        assertTrue(ReleaseMetadataParser.evaluate(release("v0.4.5", "http://example.invalid/app.apk"), "0.4.4", asset) is UpdateCheckResult.Failed)
    }

    @Test
    fun `does not offer a draft, a prerelease or a release that is not newer`() {
        assertEquals(UpdateCheckResult.UpToDate, ReleaseMetadataParser.evaluate(release("v0.4.5", draft = true), "0.4.4", asset))
        assertEquals(UpdateCheckResult.UpToDate, ReleaseMetadataParser.evaluate(release("v0.4.5").copy(prerelease = true), "0.4.4", asset))
        assertEquals(UpdateCheckResult.UpToDate, ReleaseMetadataParser.evaluate(release("v0.4.4"), "0.4.4", asset))
    }

    @Test
    fun `a release without a name gets the app's fallback`() {
        val result = ReleaseMetadataParser.evaluate(release("v0.4.5").copy(name = null), "0.4.4", asset, "APP")
        assertEquals("APP v0.4.5", (result as UpdateCheckResult.Available).update.releaseName)
    }

    @Test
    fun `reads the sha256 digest the feed publishes and ignores anything else`() {
        val hex = "a".repeat(64)
        assertEquals(hex, ReleaseMetadataParser.parseDigest("sha256:${hex.uppercase()}"))
        assertNull(ReleaseMetadataParser.parseDigest("sha1:$hex"))
        assertNull(ReleaseMetadataParser.parseDigest("sha256:abc"))
        assertNull(ReleaseMetadataParser.parseDigest(""))
    }

    @Test
    fun `a published digest must match and a missing one cannot be checked`() {
        val hex = "b".repeat(64)
        assertTrue(ReleaseMetadataParser.digestMatches(hex, hex))
        assertTrue(!ReleaseMetadataParser.digestMatches(hex, "c".repeat(64)))
        assertTrue(ReleaseMetadataParser.digestMatches(null, hex))
    }
}
