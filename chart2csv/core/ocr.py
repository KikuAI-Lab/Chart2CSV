"""
OCR for tick labels using Tesseract or Mistral.
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

from chart2csv.core.mistral_ocr import MistralOCRBackend
from chart2csv.core.cache import get_cached_result, save_to_cache


def extract_tick_labels(
    image: np.ndarray,
    axes: Dict[str, int],
    use_mistral: bool = False,
    use_cache: bool = True
) -> Tuple[Dict[str, List[Dict[str, Any]]], float]:
    """
    Extract tick labels using OCR.

    Args:
        image: Cropped chart image
        axes: Axis positions
        use_mistral: Whether to use Mistral OCR backend
        use_cache: Whether to use cached results

    Returns:
        Tuple of (ticks_data, ocr_confidence)
        ticks_data: {
            "x": [{"pixel": int, "value": float, "text": str}, ...],
            "y": [{"pixel": int, "value": float, "text": str}, ...]
        }
        ocr_confidence: 0.0-1.0 based on parse success rate
    """
    backend_name = "mistral" if use_mistral else "tesseract"
    
    # Check cache first
    if use_cache:
        cached = get_cached_result(image, backend=backend_name)
        if cached:
            return cached["result"], cached["confidence"]
    
    mistral_backend = MistralOCRBackend() if use_mistral else None

    if use_mistral:
        if not mistral_backend or not mistral_backend.is_available():
            print("Mistral OCR requested but not available. Falling back to Tesseract.")
            use_mistral = False
            backend_name = "tesseract"

    if not use_mistral and not TESSERACT_AVAILABLE:
        raise ImportError(
            "pytesseract not installed. "
            "Install with: pip install pytesseract"
        )

    h, w = image.shape[:2]
    x_axis_y = axes["x"]
    y_axis_x = axes["y"]
    
    ticks_data = {"x": [], "y": []}

    # Get tick positions from detection
    from chart2csv.core.detection import detect_ticks
    ticks, _ = detect_ticks(image, axes)

    if use_mistral:
        result, conf = _extract_with_mistral(image, axes, ticks, mistral_backend)
    else:
        result, conf = _extract_with_tesseract(image, axes, ticks)
    
    # Save to cache
    if use_cache:
        # Convert result to JSON-serializable format
        cache_result = {
            "x": [{"pixel": t["pixel"], "value": t["value"], "text": t["text"]} for t in result["x"]],
            "y": [{"pixel": t["pixel"], "value": t["value"], "text": t["text"]} for t in result["y"]]
        }
        save_to_cache(image, cache_result, conf, backend=backend_name)
    
    return result, conf


def _extract_with_mistral(
    image: np.ndarray,
    axes: Dict[str, int],
    ticks: Dict[str, List[int]],
    backend: MistralOCRBackend
) -> Tuple[Dict[str, List[Dict[str, Any]]], float]:
    """Extract ticks using Mistral OCR on axis strips with batch API."""
    h, w = image.shape[:2]
    x_axis_y = axes["x"]
    y_axis_x = axes["y"]
    ticks_data = {"x": [], "y": []}

    # Crop axis strips
    x_strip_y1 = x_axis_y + 5
    x_strip_y2 = min(h, x_axis_y + 60)
    x_strip = image[x_strip_y1:x_strip_y2, 0:w]
    
    y_strip_x1 = max(0, y_axis_x - 80)
    y_strip_x2 = max(0, y_axis_x - 5)
    y_strip = image[0:h, y_strip_x1:y_strip_x2]

    # Use batch API if both strips are valid
    if x_strip.size > 0 and y_strip.size > 0:
        x_values, y_values = backend.process_both_axes(x_strip, y_strip)
    else:
        x_values = backend.process_axis_strip(x_strip) if x_strip.size > 0 else []
        y_values = backend.process_axis_strip(y_strip) if y_strip.size > 0 else []

    # Align X values with detected ticks
    detected_x_ticks = sorted(ticks["x"])
    count = min(len(detected_x_ticks), len(x_values))
    for i in range(count):
        px = detected_x_ticks[i]
        val = x_values[i]
        ticks_data["x"].append({"pixel": px, "value": val, "text": str(val)})

    # Align Y values with detected ticks
    detected_y_ticks = sorted(ticks["y"])
    count = min(len(detected_y_ticks), len(y_values))
    for i in range(count):
        py = detected_y_ticks[i]
        val = y_values[i]
        ticks_data["y"].append({"pixel": py, "value": val, "text": str(val)})

    # Calculate confidence
    total_ticks = len(ticks["x"]) + len(ticks["y"])
    matched_ticks = len(ticks_data["x"]) + len(ticks_data["y"])

    conf = (matched_ticks / total_ticks) if total_ticks > 0 else 0.0
    return ticks_data, conf


def _extract_with_tesseract(
    image: np.ndarray,
    axes: Dict[str, int],
    ticks: Dict[str, List[int]]
) -> Tuple[Dict[str, List[Dict[str, Any]]], float]:
    """Original Tesseract implementation."""
    h, w = image.shape[:2]
    x_axis_y = axes["x"]
    y_axis_x = axes["y"]

    ticks_data = {"x": [], "y": []}
    total_found = 0
    total_parsed = 0
    
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
