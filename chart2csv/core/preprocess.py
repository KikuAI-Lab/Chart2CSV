"""
Image preprocessing for Chart2CSV.

Handles image normalization, enhancement, and plot area detection.
"""

import cv2
import numpy as np
from typing import Tuple


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Preprocess chart image for better detection and OCR.

    Steps:
    1. Resize to max 1200px (long side) for performance
    2. Convert to grayscale
    3. Enhance contrast (CLAHE)
    4. Denoise (bilateral filter)

    Args:
        image: Input BGR image from cv2.imread()

    Returns:
        Preprocessed grayscale image
    """
    # Step 1: Resize if too large
    h, w = image.shape[:2]
    max_side = max(h, w)

    if max_side > 1200:
        scale = 1200 / max_side
        new_w = int(w * scale)
        new_h = int(h * scale)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Step 2: Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Step 3: Contrast enhancement with CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Step 4: Denoise
    denoised = cv2.bilateralFilter(enhanced, d=5, sigmaColor=50, sigmaSpace=50)

    return denoised


def detect_plot_area(image: np.ndarray) -> Tuple[Tuple[int, int, int, int], float]:
    """
    Detect the plot area bounding box.

    Uses edge detection and contour analysis to find the main chart region.

    Args:
        image: Preprocessed grayscale image

    Returns:
        Tuple of ((x1, y1, x2, y2), confidence)
        where confidence is 0.0-1.0
    """
    h, w = image.shape[:2]

    # TODO: Implement actual plot area detection
    # Current implementation: return full image with low confidence

    # Placeholder: use full image with margin
    margin = 10
    x1, y1 = margin, margin
    x2, y2 = w - margin, h - margin

    confidence = 0.4  # Low confidence for placeholder

    return (x1, y1, x2, y2), confidence


def remove_grid(image: np.ndarray) -> np.ndarray:
    """
    Remove grid lines from chart image.

    Optional preprocessing step for charts with heavy gridlines.

    Args:
        image: Preprocessed grayscale image

    Returns:
        Image with grid lines removed
    """
    # TODO: Implement grid removal
    # Use morphological operations with long horizontal/vertical kernels
    return image.copy()
