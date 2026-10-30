# =============================================================================
# HYDRA-UMC-SDK - Pose contract: position and orientation as a unit quaternion
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

"""A pose whose orientation is a unit quaternion, and the rotation math that goes with it.

Euler angles do not commute and are singular at pitch +-90 degrees, so an
orientation error or an accumulated rotation must not be computed on them.
This module is the reference for the contract `contracts/json-schema/v1/pose.schema.json`:

* `Quaternion` is `(w, x, y, z)`, Hamilton convention, unit length.
* `Quaternion.from_euler` / `to_euler` use roll, pitch, yaw in radians with the
  intrinsic Z-Y-X order (yaw about Z, then pitch about the new Y, then roll about
  the new X); the earlier Euler field of a pose is read this way.
* The frame of a pose is declared: "base" (fixed to the robot base) or "tool"
  (fixed to the end effector). A rotation delta composes on the left in "base"
  (`delta * current`) and on the right in "tool" (`current * delta`).
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass
from typing import Any

from .validation import ContractValidationError

FRAMES = ("base", "tool")
NORM_TOLERANCE = 1e-6


@dataclass(frozen=True)
class Quaternion:
    w: float
    x: float
    y: float
    z: float

    @classmethod
    def identity(cls) -> "Quaternion":
        return cls(1.0, 0.0, 0.0, 0.0)

    @property
    def norm(self) -> float:
        return math.sqrt(self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z)

    def normalized(self) -> "Quaternion":
        n = self.norm
        if not math.isfinite(n) or n == 0.0:
            raise ContractValidationError("a quaternion with no length has no orientation")
        return Quaternion(self.w / n, self.x / n, self.y / n, self.z / n)

    def conjugate(self) -> "Quaternion":
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def __mul__(self, other: "Quaternion") -> "Quaternion":
        """Hamilton product: the rotation `other` first, then `self`."""
        return Quaternion(
            self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,
            self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
            self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,
            self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w,
        )

    def canonical(self) -> "Quaternion":
        """The same rotation with w >= 0 (q and -q are one orientation); the shortest turn has w >= 0."""
        return self if self.w >= 0.0 else Quaternion(-self.w, -self.x, -self.y, -self.z)

    def to_rotation_vector(self) -> tuple[float, float, float]:
        """Axis times angle (radians), the angle in [0, pi]: what an angular velocity is made of."""
        q = self.normalized().canonical()
        sin_half = math.sqrt(q.x * q.x + q.y * q.y + q.z * q.z)
        if sin_half < 1e-12:
            return (2.0 * q.x, 2.0 * q.y, 2.0 * q.z)  # first order: a vanishing turn
        angle = 2.0 * math.atan2(sin_half, q.w)
        scale = angle / sin_half
        return (q.x * scale, q.y * scale, q.z * scale)

    @classmethod
    def from_rotation_vector(cls, vector: tuple[float, float, float]) -> "Quaternion":
        angle = math.sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)
        if angle < 1e-12:
            return cls(1.0, 0.5 * vector[0], 0.5 * vector[1], 0.5 * vector[2]).normalized()
        half = 0.5 * angle
        s = math.sin(half) / angle
        return cls(math.cos(half), vector[0] * s, vector[1] * s, vector[2] * s)

    @classmethod
    def from_euler(cls, roll: float, pitch: float, yaw: float) -> "Quaternion":
        cr, sr = math.cos(roll / 2.0), math.sin(roll / 2.0)
        cp, sp = math.cos(pitch / 2.0), math.sin(pitch / 2.0)
        cy, sy = math.cos(yaw / 2.0), math.sin(yaw / 2.0)
        return cls(
            cr * cp * cy + sr * sp * sy,
            sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy,
        )

    def to_euler(self) -> tuple[float, float, float]:
        """(roll, pitch, yaw); at pitch +-90 degrees the roll is folded into the yaw (gimbal lock)."""
        q = self.normalized()
        sinp = 2.0 * (q.w * q.y - q.z * q.x)
        if abs(sinp) >= 1.0 - 1e-12:
            # gimbal lock: roll and yaw turn about the same axis; the roll is set to 0 and the yaw takes the whole turn
            return (0.0, math.copysign(math.pi / 2.0, sinp), math.atan2(2.0 * (q.w * q.z - q.x * q.y), 1.0 - 2.0 * (q.x * q.x + q.z * q.z)))
        roll = math.atan2(2.0 * (q.w * q.x + q.y * q.z), 1.0 - 2.0 * (q.x * q.x + q.y * q.y))
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        return (roll, math.asin(sinp), yaw)

    def angle_to(self, other: "Quaternion") -> float:
        """The smallest rotation angle (radians, 0..pi) between two orientations."""
        p, q = self.normalized(), other.normalized()
        dot = abs(p.w * q.w + p.x * q.x + p.y * q.y + p.z * q.z)
        return 2.0 * math.acos(min(1.0, dot))

    def to_dict(self) -> dict[str, float]:
        return {"w": self.w, "x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def from_dict(cls, value: Any) -> "Quaternion":
        if not isinstance(value, dict) or set(value) != {"w", "x", "y", "z"}:
            raise ContractValidationError("orientation must be an object with exactly w, x, y and z")
        numbers = []
        for name in ("w", "x", "y", "z"):
            number = value[name]
            if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(number):
                raise ContractValidationError(f"orientation.{name} must be a finite number")
            numbers.append(float(number))
        quaternion = cls(*numbers)
        if abs(quaternion.norm - 1.0) > NORM_TOLERANCE:
            raise ContractValidationError(f"orientation must be a unit quaternion, its length is {quaternion.norm:.9g}")
        return quaternion


@dataclass(frozen=True)
class Pose:
    position: tuple[float, float, float]
    orientation: Quaternion
    frame: str = "base"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "frame": self.frame,
            "position": {"x": self.position[0], "y": self.position[1], "z": self.position[2]},
            "orientation": self.orientation.to_dict(),
        }


def validate_pose(payload: dict[str, Any]) -> None:
    """The checks of the Pose contract, the unit length of the quaternion included."""
    pose_from_dict(payload)


def pose_from_dict(payload: dict[str, Any]) -> Pose:
    """A `Pose` from a payload of the contract. A payload that carries only the deprecated `euler` is refused:
    the quaternion is required; when both are present they must be the same orientation."""
    if not isinstance(payload, dict):
        raise ContractValidationError("payload must be an object")
    for field in ("schema_version", "frame", "position", "orientation"):
        if field not in payload:
            raise ContractValidationError(f"missing required field: {field}")
    if payload["schema_version"] != "1.0":
        raise ContractValidationError("schema_version must be '1.0'")
    if payload["frame"] not in FRAMES:
        raise ContractValidationError(f"frame must be one of {', '.join(FRAMES)}")
    position = payload["position"]
    if not isinstance(position, dict) or set(position) != {"x", "y", "z"}:
        raise ContractValidationError("position must be an object with exactly x, y and z")
    coordinates = []
    for name in ("x", "y", "z"):
        number = position[name]
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(number):
            raise ContractValidationError(f"position.{name} must be a finite number")
        coordinates.append(float(number))
    orientation = Quaternion.from_dict(payload["orientation"])
    if "euler" in payload:
        warnings.warn("Pose.euler is deprecated: read the orientation quaternion", DeprecationWarning, stacklevel=2)
        euler = payload["euler"]
        if not isinstance(euler, dict) or set(euler) != {"roll", "pitch", "yaw"}:
            raise ContractValidationError("euler must be an object with exactly roll, pitch and yaw")
        try:
            numbers = [float(euler[name]) for name in ("roll", "pitch", "yaw")]
        except (TypeError, ValueError) as error:
            raise ContractValidationError("euler values must be numbers") from error
        if not all(math.isfinite(n) for n in numbers) or any(isinstance(euler[n], bool) for n in euler):
            raise ContractValidationError("euler values must be finite numbers")
        if Quaternion.from_euler(*numbers).angle_to(orientation) > 1e-6:
            raise ContractValidationError("euler and orientation describe different orientations")
    return Pose((coordinates[0], coordinates[1], coordinates[2]), orientation, payload["frame"])


def pose_to_legacy_euler(pose: Pose) -> dict[str, float]:
    """The deprecated roll, pitch, yaw of a pose, for a reader that has not moved to the quaternion yet."""
    roll, pitch, yaw = pose.orientation.to_euler()
    return {"roll": roll, "pitch": pitch, "yaw": yaw}
