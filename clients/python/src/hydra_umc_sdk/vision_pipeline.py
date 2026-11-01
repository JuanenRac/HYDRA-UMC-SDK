# =============================================================================
# HYDRA-UMC-SDK - Data contract of the vision pipeline
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `FrameMeta` and `DetectionFrame` contracts: the frame that a camera produced and the detections that a model found in it.

Before this contract each service of the pipeline wrote its own format (raw frames here, JPEG there, boxes in pixels in one tool, normalised in another, the
order of the corners of a Hailo output in a third). Here the convention is part of the data. A `FrameMeta` says which frame it is (`frame_id`, the instant it
was captured, its size and its pixel format). A `DetectionFrame` ties detections to that frame by `frame_id` and `capture_ts_utc`, says in what unit its boxes
are (`box_unit`: `pixel` or `normalized`, always with the origin at the top left corner of the frame, x to the right and y downwards, corners given as
`x_min`, `y_min`, `x_max`, `y_max`) and may carry the identity of the model (`model`, the five fields of the compatibility record of the vision node).

The schema holds the shape; the clients also check what a schema cannot say: `x_min <= x_max` and `y_min <= y_max` for every box, and a box inside the frame
(0 to 1 for `normalized`).
"""

from __future__ import annotations

from typing import Any

from .contract_rules import SHA256_HEX, check_fields, identifier, one_of, real, require_object, text, whole
from .validation import ContractValidationError, _require_date_time

PIXEL_FORMATS: tuple[str, ...] = ("RGB", "BGR", "RGBA", "BGRA", "GRAY", "YUYV", "NV12", "JPEG")
BOX_UNITS: tuple[str, ...] = ("pixel", "normalized")
MAX_DIMENSION = 8192
MAX_DETECTIONS = 1000
BOX_FIELDS: tuple[str, ...] = ("x_min", "y_min", "x_max", "y_max")
MODEL_FIELDS: tuple[str, ...] = ("model_name", "model_version", "model_sha256", "hailo_arch", "pipeline_version")

_FRAME_REQUIRED = ("schema_version", "frame_id", "capture_ts_utc", "width", "height", "pixel_format")
_FRAME_OPTIONAL = ("session_id", "source_id", "stride", "sequence")
_DETECTION_REQUIRED = ("schema_version", "frame_id", "capture_ts_utc", "box_unit", "detections")
_DETECTION_OPTIONAL = ("session_id", "model")
_ITEM_REQUIRED = ("class_id", "label", "score", "box")


def validate_frame_meta(payload: dict[str, Any]) -> None:
    """The checks of the FrameMeta contract."""
    require_object(payload)
    check_fields(payload, _FRAME_REQUIRED, _FRAME_OPTIONAL)
    for name in ("frame_id", "session_id", "source_id"):
        if name in payload:
            identifier(payload, name)
    _require_date_time(payload, "capture_ts_utc")
    whole(payload, "width", 1, MAX_DIMENSION)
    whole(payload, "height", 1, MAX_DIMENSION)
    one_of(payload, "pixel_format", PIXEL_FORMATS)
    if "stride" in payload:
        whole(payload, "stride", 1)
    if "sequence" in payload:
        whole(payload, "sequence", 0)


def _check_model(payload: dict[str, Any]) -> None:
    model = payload["model"]
    if not isinstance(model, dict):
        raise ContractValidationError("model must be an object")
    check_fields(model, MODEL_FIELDS, (), label="model")
    for name in ("model_name", "model_version", "hailo_arch", "pipeline_version"):
        text(model, name, 64)
    if not (isinstance(model["model_sha256"], str) and SHA256_HEX.fullmatch(model["model_sha256"])):
        raise ContractValidationError("model_sha256 must be 64 lowercase hexadecimal digits")


def _check_detection(item: Any, box_unit: str, index: int) -> None:
    if not isinstance(item, dict):
        raise ContractValidationError(f"detections[{index}] must be an object")
    label = f"detections[{index}]"
    check_fields(item, _ITEM_REQUIRED, (), label=label)
    whole(item, "class_id", 0)
    text(item, "label", 64)
    real(item, "score", 0, 1)
    box = item["box"]
    if not isinstance(box, dict):
        raise ContractValidationError(f"{label}.box must be an object")
    check_fields(box, BOX_FIELDS, (), label=f"{label}.box")
    for name in BOX_FIELDS:
        real(box, name, 0, 1 if box_unit == "normalized" else MAX_DIMENSION)
    if box["x_min"] > box["x_max"] or box["y_min"] > box["y_max"]:
        raise ContractValidationError(f"{label}.box must have x_min <= x_max and y_min <= y_max")


def validate_detection_frame(payload: dict[str, Any]) -> None:
    """The checks of the DetectionFrame contract."""
    require_object(payload)
    check_fields(payload, _DETECTION_REQUIRED, _DETECTION_OPTIONAL)
    identifier(payload, "frame_id")
    if "session_id" in payload:
        identifier(payload, "session_id")
    _require_date_time(payload, "capture_ts_utc")
    one_of(payload, "box_unit", BOX_UNITS)
    detections = payload["detections"]
    if not isinstance(detections, list) or len(detections) > MAX_DETECTIONS:
        raise ContractValidationError(f"detections must be an array of at most {MAX_DETECTIONS} detections")
    for index, item in enumerate(detections):
        _check_detection(item, payload["box_unit"], index)
    if "model" in payload:
        _check_model(payload)


def box_to_pixels(box: dict[str, float], box_unit: str, width: int, height: int) -> dict[str, float]:
    """The corners of a box in pixels of a frame of `width` x `height`, whatever the unit it came in."""
    check_fields(box, BOX_FIELDS, (), label="box")
    if box_unit == "pixel":
        return {name: float(box[name]) for name in BOX_FIELDS}
    if box_unit != "normalized":
        raise ContractValidationError(f"box_unit must be one of {', '.join(BOX_UNITS)}")
    return {"x_min": box["x_min"] * width, "y_min": box["y_min"] * height, "x_max": box["x_max"] * width, "y_max": box["y_max"] * height}
