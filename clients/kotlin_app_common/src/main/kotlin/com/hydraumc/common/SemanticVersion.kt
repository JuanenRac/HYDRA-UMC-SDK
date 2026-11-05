// =============================================================================
// HYDRA-UMC Kotlin app common - src/main/kotlin/com/hydraumc/common/SemanticVersion.kt
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================
package com.hydraumc.common

/**
 * A release version accepted by the HYDRA-UMC Android distribution channel.
 * Pre-release labels are intentionally rejected: the stable application must
 * never treat a draft, nightly, or malformed GitHub tag as an update.
 */
data class SemanticVersion(val major: Int, val minor: Int, val patch: Int, val build: Int? = null) : Comparable<SemanticVersion> {
    // A missing fourth component compares as 0.
    override fun compareTo(other: SemanticVersion): Int = compareValuesBy(
        this,
        other,
        SemanticVersion::major,
        SemanticVersion::minor,
        SemanticVersion::patch,
        { version: SemanticVersion -> version.build ?: 0 },
    )

    override fun toString(): String = if (build == null) "$major.$minor.$patch" else "$major.$minor.$patch.$build"

    companion object {
        private val stablePattern = Regex("^v?(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:\\.(0|[1-9]\\d*))?$")

        /** Returns null instead of guessing when a GitHub tag is not stable semver. */
        fun parseStable(value: String): SemanticVersion? {
            val match = stablePattern.matchEntire(value.trim()) ?: return null
            return SemanticVersion(
                major = match.groupValues[1].toInt(),
                minor = match.groupValues[2].toInt(),
                patch = match.groupValues[3].toInt(),
                build = match.groupValues[4].takeIf { it.isNotEmpty() }?.toInt(),
            )
        }
    }
}
