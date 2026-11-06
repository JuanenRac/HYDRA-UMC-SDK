// =============================================================================
// HYDRA-UMC Kotlin app common - src/main/kotlin/com/hydraumc/common/ReleaseMetadataParser.kt
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================
package com.hydraumc.common

import org.json.JSONObject

/** A stable GitHub release and its explicitly named installable APK asset. */
data class AvailableUpdate(
    val version: SemanticVersion,
    val releaseName: String,
    val notes: String,
    val assetUrl: String,
    /** Lowercase hex SHA-256 the release feed publishes for the APK asset, when it does. */
    val sha256: String? = null,
)

/** Result of checking the trusted public release endpoint. */
sealed interface UpdateCheckResult {
    data object UpToDate : UpdateCheckResult
    data class Available(val update: AvailableUpdate) : UpdateCheckResult
    data class Failed(val message: String) : UpdateCheckResult
}

/** One asset of a release, as far as the update gate cares. */
data class ReleaseAsset(val name: String, val downloadUrl: String, val digest: String = "")

/**
 * What the update gate needs from a release feed entry. An app that reads the feed with
 * another JSON library fills this in itself and calls [ReleaseMetadataParser.evaluate], so
 * the trust decisions (stable tag, newer than installed, exact asset, HTTPS, digest) are
 * the same everywhere.
 */
data class ReleaseInfo(
    val tagName: String,
    val name: String? = null,
    val body: String = "",
    val draft: Boolean = false,
    val prerelease: Boolean = false,
    val assets: List<ReleaseAsset>? = null,
)

/**
 * Pure release-metadata gate used before any APK is downloaded. Free of Context, HTTP and
 * package-manager APIs, so the update channel's trust decisions are testable on the JVM.
 */
object ReleaseMetadataParser {
    /** Reads the GitHub release JSON (org.json, the platform's own) and applies [evaluate]. */
    fun parseLatestStable(payload: String, installedVersionName: String, requiredAsset: String, fallbackName: String = "HYDRA-UMC"): UpdateCheckResult {
        val release = JSONObject(payload)
        val assets = release.optJSONArray("assets")?.let { array ->
            (0 until array.length()).mapNotNull { index ->
                array.optJSONObject(index)?.let {
                    ReleaseAsset(it.optStr("name"), it.optStr("browser_download_url"), it.optStr("digest"))
                }
            }
        }
        return evaluate(
            ReleaseInfo(
                tagName = release.optStr("tag_name"),
                name = if (release.isNull("name")) null else release.optString("name"),
                body = release.optStr("body"),
                draft = release.optBoolean("draft"),
                prerelease = release.optBoolean("prerelease"),
                assets = assets,
            ),
            installedVersionName,
            requiredAsset,
            fallbackName,
        )
    }

    fun evaluate(release: ReleaseInfo, installedVersionName: String, requiredAsset: String, fallbackName: String = "HYDRA-UMC"): UpdateCheckResult {
        if (release.draft || release.prerelease) return UpdateCheckResult.UpToDate
        val remoteVersion = SemanticVersion.parseStable(release.tagName)
            ?: return UpdateCheckResult.Failed("Latest GitHub Release tag is not a stable vMAJOR.MINOR.PATCH value.")
        val localVersion = SemanticVersion.parseStable(installedVersionName)
            ?: return UpdateCheckResult.Failed("Installed application version is not stable semver.")
        if (remoteVersion <= localVersion) return UpdateCheckResult.UpToDate

        val asset = release.assets?.firstOrNull { it.name == requiredAsset }
            ?: return UpdateCheckResult.Failed("Release v$remoteVersion has no $requiredAsset asset.")
        if (!asset.downloadUrl.startsWith("https://")) {
            return UpdateCheckResult.Failed("Release APK URL is not HTTPS.")
        }
        return UpdateCheckResult.Available(
            AvailableUpdate(
                version = remoteVersion,
                releaseName = release.name ?: "$fallbackName v$remoteVersion",
                notes = release.body.trim(),
                assetUrl = asset.downloadUrl,
                sha256 = parseDigest(asset.digest),
            ),
        )
    }

    private val SHA256_HEX = Regex("^[0-9a-f]{64}$")

    /** Reads GitHub's sha256:<hex> asset digest; anything else counts as "not published". */
    fun parseDigest(raw: String): String? {
        val value = raw.trim().lowercase()
        if (!value.startsWith("sha256:")) return null
        return value.removePrefix("sha256:").takeIf { SHA256_HEX.matches(it) }
    }

    /** A release that publishes no digest cannot be checked; one that does must match. */
    fun digestMatches(expected: String?, actual: String): Boolean =
        expected == null || expected.equals(actual, ignoreCase = true)
}
