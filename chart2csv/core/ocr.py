"""
OCR for tick labels using Tesseract.
"""

import re
import cv2
import numpy as np
from typing import Dict, List, Tuple, Any, Optional

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


def extract_tick_labels(
    image: np.ndarray,
    axes: Dict[str, int]
) -> Tuple[Dict[str, List[Dict[str, Any]]], float]:
    """
    Extract tick labels using OCR.

    Args:
        image: Cropped chart image
        axes: Axis positions

    Returns:
        Tuple of (ticks_data, ocr_confidence)
        ticks_data: {
            "x": [{"pixel": int, "value": float, "text": str}, ...],
            "y": [{"pixel": int, "value": float, "text": str}, ...]
        }
        ocr_confidence: 0.0-1.0 based on parse success rate
    """
    if not TESSERACT_AVAILABLE:
        raise ImportError(
            "pytesseract not installed. "
            "Install with: pip install pytesseract"
        )

    h, w = image.shape[:2]
    x_axis_y = axes["x"]
    y_axis_x = axes["y"]
    
    ticks_data = {"x": [], "y": []}
    total_found = 0
    total_parsed = 0

    # X-axis OCR (regions below axis)
    # Strategy: find vertical line-like clusters of pixels or just use the detected ticks
    # Since we have detect_ticks, let's use them as anchors
    from chart2csv.core.detection import detect_ticks
    ticks, _ = detect_ticks(image, axes)
    
    # OCR Config for numbers
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.eE+-'

    for px in ticks["x"]:
        # Crop region below this tick
        x1 = max(0, px - 30)
        x2 = min(w, px + 30)
        y1 = x_axis_y + 5
        y2 = min(h, x_axis_y + 40)
        
        region = image[y1:y2, x1:x2]
        if region.size == 0: continue
        
        processed = preprocess_for_ocr(region)
        text = pytesseract.image_to_string(processed, config=custom_config).strip()
        
        val = parse_number(text)
        if val is not None:
            ticks_data["x"].append({"pixel": px, "value": val, "text": text})
            total_parsed += 1
        total_found += 1

    for py in ticks["y"]:
        # Crop region to the left of this tick
        x1 = max(0, y_axis_x - 60)
        x2 = max(0, y_axis_x - 5)
        y1 = max(0, py - 15)
        y2 = min(h, py + 15)
        
        region = image[y1:y2, x1:x2]
        if region.size == 0: continue
        
        processed = preprocess_for_ocr(region)
        text = pytesseract.image_to_string(processed, config=custom_config).strip()
        
        val = parse_number(text)
        if val is not None:
            ticks_data["y"].append({"pixel": py, "value": val, "text": text})
            total_parsed += 1
        total_found += 1

    ocr_confidence = (total_parsed / total_found) if total_found > 0 else 0.0

    return ticks_data, ocr_confidence


def parse_number(text: str) -> Optional[float]:
    """
    Parse a number from OCR text.

    Handles:
    - Regular numbers: 123, 12.34, -5.6
    - Scientific notation: 1e-5, 1.23E+10
    - Negative with dash or minus

    Args:
        text: OCR text

    Returns:
        Parsed float or None if parsing fails
    """
    # Clean text
    text = text.strip()

    # Scientific notation regex
    pattern = r'[-+]?\d*\.?\d+([eE][-+]?\d+)?'

    match = re.search(pattern, text)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None

    return None


def preprocess_for_ocr(image: np.ndarray) -> np.ndarray:
    """
    Preprocess image region for better OCR.

    Args:
        image: Grayscale image region

    Returns:
        Binarized image optimized for Tesseract
    """
    # Adaptive thresholding
    binary = cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    # Invert if most pixels are dark (white text on dark background)
    if np.mean(binary) < 127:
        binary = cv2.bitwise_not(binary)

    return binary
