"""
Auto-crop detection for Chart2CSV.

Automatically detects the plot area boundaries to exclude
axes labels, titles, and legends.
"""

import cv2
import numpy as np
from typing import Tuple, Optional


def detect_plot_area(
    image: np.ndarray,
    margin: int = 5
) -> Tuple[Optional[Tuple[int, int, int, int]], float]:
    """
    Automatically detect the plot area in a chart image.

    Strategy:
    1. Find the axis lines (usually the darkest straight lines)
    2. Detect the bounding box formed by axes
    3. Return crop coordinates with small margin

    Args:
        image: BGR image from cv2.imread()
        margin: Pixels to add inside detected boundaries

    Returns:
        Tuple of (crop_box, confidence)
        crop_box: (x1, y1, x2, y2) or None if detection fails
        confidence: 0.0-1.0 detection quality estimate
    """
    h, w = image.shape[:2]

    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Edge detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Detect lines using Hough transform
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=100,
        minLineLength=min(w, h) // 4,
        maxLineGap=10
    )

    if lines is None or len(lines) < 2:
        # Fallback: use image edges with margin
        return _fallback_crop(w, h), 0.3

    # Separate horizontal and vertical lines
    horizontal_lines = []
    vertical_lines = []

    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)

        if angle < 10 or angle > 170:  # Horizontal
            horizontal_lines.append((y1 + y2) // 2)
        elif 80 < angle < 100:  # Vertical
            vertical_lines.append((x1 + x2) // 2)

    if not horizontal_lines or not vertical_lines:
        return _fallback_crop(w, h), 0.4

    # Find axis boundaries
    # Y-axis is typically on the left
    # X-axis is typically at the bottom
    left_x = min(vertical_lines)
    right_x = max(vertical_lines)
    top_y = min(horizontal_lines)
    bottom_y = max(horizontal_lines)

    # Validate detected region
    width = right_x - left_x
    height = bottom_y - top_y

    # Plot area should be reasonable size (at least 30% of image)
    if width < w * 0.3 or height < h * 0.3:
        return _fallback_crop(w, h), 0.4

    # Apply margin (shrink crop area slightly)
    x1 = max(0, left_x + margin)
    y1 = max(0, top_y + margin)
    x2 = min(w, right_x - margin)
    y2 = min(h, bottom_y - margin)

    confidence = 0.8
    if width > w * 0.5 and height > h * 0.5:
        confidence = 0.9

    return (x1, y1, x2, y2), confidence


def detect_plot_area_contour(
    image: np.ndarray,
    margin: int = 10
) -> Tuple[Optional[Tuple[int, int, int, int]], float]:
    """
    Alternative plot area detection using contour analysis.

    Looks for the largest rectangular region (plot background).

    Args:
        image: BGR image
        margin: Pixels to shrink from detected boundaries

    Returns:
        Tuple of (crop_box, confidence)
    """
    h, w = image.shape[:2]

    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Threshold to find white/light regions (plot background)
    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return _fallback_crop(w, h), 0.3

    # Find largest rectangular contour
    best_rect = None
    best_area = 0

    for contour in contours:
        # Approximate to polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check if it's roughly rectangular (4 corners)
        if len(approx) >= 4:
            x, y, cw, ch = cv2.boundingRect(contour)
            area = cw * ch

            # Must be substantial portion of image
            if area > best_area and area > (w * h * 0.2):
                best_area = area
                best_rect = (x, y, x + cw, y + ch)

    if best_rect is None:
        return _fallback_crop(w, h), 0.3

    x1, y1, x2, y2 = best_rect

    # Apply margin
    x1 = min(x1 + margin, w - 1)
    y1 = min(y1 + margin, h - 1)
    x2 = max(x2 - margin, 0)
    y2 = max(y2 - margin, 0)

    if x2 <= x1 or y2 <= y1:
        return _fallback_crop(w, h), 0.3

    return (x1, y1, x2, y2), 0.7


def _fallback_crop(w: int, h: int) -> Tuple[int, int, int, int]:
    """
    Return default crop with 10% margin on all sides.
    """
    margin_x = int(w * 0.1)
    margin_y = int(h * 0.1)
    return (margin_x, margin_y, w - margin_x, h - margin_y)


def auto_detect_axes(
    image: np.ndarray,
    crop_box: Optional[Tuple[int, int, int, int]] = None
) -> dict:
    """
    Attempt to detect axis tick positions and values.

    This is a placeholder for future OCR-based axis detection.

    Args:
        image: BGR image
        crop_box: Optional pre-detected crop region

    Returns:
        Dict with detected axis information or empty if detection fails
    """
    # TODO: Implement OCR-based axis detection
    # For now, return empty dict to indicate manual calibration needed
    return {
        "detected": False,
        "message": "Auto-detection not implemented. Use manual calibration.",
        "x_ticks": [],
        "y_ticks": []
    }
