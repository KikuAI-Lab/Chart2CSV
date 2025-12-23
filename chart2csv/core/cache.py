"""
OCR Cache for Chart2CSV.

Provides disk-based caching of OCR results to avoid redundant API calls.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np


def get_cache_dir() -> Path:
    """Get cache directory, creating if needed."""
    cache_dir = Path.home() / ".cache" / "chart2csv" / "ocr"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def compute_image_hash(image: np.ndarray) -> str:
    """Compute hash of image for cache key."""
    # Optimization: Use buffer protocol directly if contiguous to avoid copy
    if image.flags['C_CONTIGUOUS']:
        return hashlib.md5(image).hexdigest()
    # Fallback to tobytes() which handles non-contiguous arrays (by copying)
    return hashlib.md5(image.tobytes()).hexdigest()


def get_cached_result(image: np.ndarray, backend: str = "tesseract") -> Optional[Dict[str, Any]]:
    """
    Get cached OCR result if available.
    
    Args:
        image: Input image
        backend: OCR backend used ("tesseract" or "mistral")
        
    Returns:
        Cached result dict or None if not cached
    """
    cache_dir = get_cache_dir()
    image_hash = compute_image_hash(image)
    cache_file = cache_dir / f"{backend}_{image_hash}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None


def save_to_cache(
    image: np.ndarray, 
    result: Dict[str, Any], 
    confidence: float,
    backend: str = "tesseract"
) -> None:
    """
    Save OCR result to cache.
    
    Args:
        image: Input image
        result: OCR result dict
        confidence: OCR confidence score
        backend: OCR backend used
    """
    cache_dir = get_cache_dir()
    image_hash = compute_image_hash(image)
    cache_file = cache_dir / f"{backend}_{image_hash}.json"
    
    cache_data = {
        "result": result,
        "confidence": confidence,
        "backend": backend
    }
    
    try:
        with open(cache_file, "w") as f:
            json.dump(cache_data, f)
    except IOError:
        pass  # Silently fail if cache write fails


def clear_cache() -> int:
    """Clear all cached OCR results. Returns number of files deleted."""
    cache_dir = get_cache_dir()
    count = 0
    for f in cache_dir.glob("*.json"):
        try:
            f.unlink()
            count += 1
        except IOError:
            pass
    return count
