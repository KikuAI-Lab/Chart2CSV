"""
Pixel-to-value coordinate transformation.
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from chart2csv.core.types import Scale


def build_transform(
    ticks: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    calibration_points: Optional[Dict[str, Any]] = None,
    x_scale: Scale = Scale.LINEAR,
    y_scale: Scale = Scale.LINEAR
) -> Tuple[Dict[str, Any], float]:
    """
    Build pixel→value transformation from ticks or calibration.

    Args:
        ticks: OCR tick data (from extract_tick_labels)
        calibration_points: Manual calibration data
        x_scale: X-axis scale (linear or log)
        y_scale: Y-axis scale (linear or log)

    Returns:
        Tuple of (transform_dict, fit_error)
        transform_dict contains transformation parameters
        fit_error is residual error for linear fit (0.0-1.0)
    """
    if calibration_points:
        # Use manual calibration
        return _build_from_calibration(calibration_points, x_scale, y_scale)
    elif ticks:
        # Use OCR ticks
        return _build_from_ticks(ticks, x_scale, y_scale)
    else:
        raise ValueError("Need either ticks or calibration_points")


def _build_from_ticks(
    ticks: Dict[str, List[Dict[str, Any]]],
    x_scale: Scale,
    y_scale: Scale
) -> Tuple[Dict[str, Any], float]:
    """Build transform from OCR ticks."""
    transform = {}
    total_fit_error = 0.0
    axes_processed = 0

    for axis_name in ["x", "y"]:
        points = ticks.get(axis_name, [])
        if len(points) < 2:
            # Fallback to identity or similar if not enough points
            transform[axis_name] = {"a": 1.0, "b": 0.0, "scale": "linear"}
            continue

        pixels = np.array([p["pixel"] for p in points])
        values = np.array([p["value"] for p in points])
        scale = x_scale if axis_name == "x" else y_scale

        if scale == Scale.LOG:
            # Avoid log(0)
            values = np.clip(values, 1e-10, None)
            target_values = np.log10(values)
        else:
            target_values = values

        # Perform linear fit: target_value = a * pixel + b
        # Using polyfit for 1st degree polynomial
        a, b = np.polyfit(pixels, target_values, 1)
        
        # Calculate residual error
        preds = a * pixels + b
        error = np.mean(np.abs(preds - target_values))
        if np.mean(np.abs(target_values)) > 0:
            error /= np.mean(np.abs(target_values))
        
        total_fit_error += error
        axes_processed += 1

        transform[axis_name] = {
            "a": float(a),
            "b": float(b),
            "scale": scale.value
        }

    avg_fit_error = total_fit_error / axes_processed if axes_processed > 0 else 0.0

    return transform, avg_fit_error


def _build_from_calibration(
    calibration_points: Dict[str, Any],
    x_scale: Scale,
    y_scale: Scale
) -> Tuple[Dict[str, Any], float]:
    """Build transform from manual calibration."""
    # Manual calibration format:
    # {
    #     "x": [(pixel1, value1), (pixel2, value2)],
    #     "y": [(pixel1, value1), (pixel2, value2)]
    # }

    transform = {}

    for axis in ["x", "y"]:
        points = calibration_points.get(axis, [])
        if len(points) < 2:
            raise ValueError(f"Need at least 2 calibration points for {axis}-axis")

        px1, val1 = points[0]
        px2, val2 = points[1]

        scale = x_scale if axis == "x" else y_scale

        if scale == Scale.LINEAR:
            # Linear: value = a * pixel + b
            a = (val2 - val1) / (px2 - px1)
            b = val1 - a * px1
        else:
            # Log: value = 10^(a * pixel + b)
            log_val1 = np.log10(val1) if val1 > 0 else 0
            log_val2 = np.log10(val2) if val2 > 0 else 0
            a = (log_val2 - log_val1) / (px2 - px1)
            b = log_val1 - a * px1

        transform[axis] = {
            "a": float(a),
            "b": float(b),
            "scale": scale.value
        }

    # Manual calibration assumed perfect
    fit_error = 0.0

    return transform, fit_error


def apply_transform(
    pixel_coords: np.ndarray,
    transform: Dict[str, Any]
) -> np.ndarray:
    """
    Apply pixel→value transformation to coordinates.

    Args:
        pixel_coords: Nx2 array of (x_pixel, y_pixel)
        transform: Transform dict from build_transform()

    Returns:
        Nx2 array of (x_value, y_value)
    """
    result = np.zeros_like(pixel_coords, dtype=float)

    for i, axis in enumerate(["x", "y"]):
        t = transform[axis]
        pixels = pixel_coords[:, i]

        if t["scale"] == "linear":
            # Linear: value = a * pixel + b
            values = t["a"] * pixels + t["b"]
        else:
            # Log: value = 10^(a * pixel + b)
            log_values = t["a"] * pixels + t["b"]
            values = np.power(10, log_values)

        result[:, i] = values

    return result
