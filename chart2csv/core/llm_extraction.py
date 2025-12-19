"""
LLM-First Chart Extraction using Pixtral Vision.

Direct image → JSON extraction without complex CV pipeline.
"""

import os
import base64
import json
import re
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False


def encode_image_base64(image: np.ndarray) -> str:
    """Encode OpenCV image to base64 data URL."""
    success, buffer = cv2.imencode('.png', image)
    if not success:
        raise ValueError("Failed to encode image to PNG")
    return f"data:image/png;base64,{base64.b64encode(buffer).decode('utf-8')}"


def extract_chart_llm(
    image_path: str,
    model: str = "mistral-ocr-latest"
) -> Tuple[Dict[str, Any], float]:
    """
    Extract chart data using LLM vision in a single API call.
    
    Args:
        image_path: Path to chart image
        model: Mistral vision model to use
        
    Returns:
        Tuple of (result_dict, confidence)
        result_dict: {
            "chart_type": str,
            "x_label": str,
            "y_label": str,
            "data": [{"x": float, "y": float}, ...]
        }
    """
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not set")
    
    if not MISTRAL_AVAILABLE:
        raise ImportError("mistralai package not installed")
    
    # Load and encode image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    image_b64 = encode_image_base64(image)
    
    # Create Mistral client
    client = Mistral(api_key=api_key)
    
    # Craft extraction prompt - chain of thought for precision
    prompt = """You are extracting data from a chart. Be EXTREMELY precise.

TASK: Extract the X,Y coordinates of EVERY data point marker in this chart.

STEP 1 - ANALYZE AXES:
First, identify the axis ranges by reading the tick labels.

STEP 2 - LOCATE MARKERS:
For line charts: find every dot/marker on the line (not the line itself, the markers).
For scatter plots: find every dot.
For bar charts: measure the height of each bar.

STEP 3 - READ VALUES:
For EACH marker, look at its position and read:
- X: What X gridline or tick is it at or between?
- Y: What Y gridline is the marker at? If between gridlines, estimate precisely.

CRITICAL: Do NOT interpolate or assume patterns. Each point may have a UNIQUE value.
Many charts have irregular data - do not assume smooth curves.

Return JSON only:
{
    "chart_type": "line" or "scatter" or "bar",
    "x_label": "axis label",
    "y_label": "axis label",
    "data": [{"x": val, "y": val}, ...]
}

Example for irregular data:
{"data": [{"x": 0, "y": 5}, {"x": 1, "y": 8}, {"x": 2, "y": 12}, {"x": 3, "y": 15}]}
Note: each Y is different and not following a pattern."""

    try:
        # Direct extraction with pixtral (OCR doesn't work for charts)
        response = client.chat.complete(
            model="pixtral-large-latest",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": image_b64}
                    ]
                }
            ],
            max_tokens=4096,
            temperature=0.0
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON from response (handle markdown code blocks)
        content = content.replace("```json", "").replace("```", "").strip()
        
        # Try to extract JSON object
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group()
        
        result = json.loads(content)
        
        # Validate required fields
        if "data" not in result or not isinstance(result["data"], list):
            return {"error": "No data extracted", "raw": content}, 0.0
        
        # Calculate confidence based on data quality
        data_points = len(result.get("data", []))
        has_labels = bool(result.get("x_label") or result.get("y_label"))
        has_range = all(k in result for k in ["x_min", "x_max", "y_min", "y_max"])
        
        confidence = 0.5
        if data_points > 0:
            confidence += 0.2
        if data_points > 5:
            confidence += 0.1
        if has_labels:
            confidence += 0.1
        if has_range:
            confidence += 0.1
        
        confidence = min(confidence, 1.0)
        
        return result, confidence
        
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}", "raw": content}, 0.0
    except Exception as e:
        return {"error": str(e)}, 0.0


def llm_result_to_array(result: Dict[str, Any]) -> np.ndarray:
    """Convert LLM extraction result to Nx2 numpy array."""
    data = result.get("data", [])
    if not data:
        return np.array([]).reshape(0, 2)
    
    points = []
    for point in data:
        try:
            x = float(point.get("x", 0))
            y = float(point.get("y", 0))
            points.append([x, y])
        except (TypeError, ValueError):
            continue
    
    return np.array(points) if points else np.array([]).reshape(0, 2)


def llm_result_to_csv(result: Dict[str, Any]) -> str:
    """Convert LLM extraction result to CSV string."""
    data = result.get("data", [])
    
    x_label = result.get("x_label", "x") or "x"
    y_label = result.get("y_label", "y") or "y"
    
    lines = [f"{x_label},{y_label}"]
    
    for point in data:
        try:
            x = point.get("x", "")
            y = point.get("y", "")
            lines.append(f"{x},{y}")
        except:
            continue
    
    return "\n".join(lines)
