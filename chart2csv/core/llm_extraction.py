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
    
    # Two-pass extraction for better accuracy on dense charts
    # Pass 1: Analyze and describe what you see
    # Pass 2: Extract data points one by one
    
    prompt = """You are a precise chart data extraction AI. 

TASK: Extract ALL data points from this chart with maximum precision.

ANALYSIS PHASE - Before extracting, observe:
1. What type of chart is this? (line/scatter/bar)
2. X-axis: What is the range? What are the gridlines?
3. Y-axis: What is the range? What are the gridlines?
4. How many data points/markers are visible? Count them carefully.

EXTRACTION PHASE - For EACH visible marker:
- Look at its horizontal position → determine X value
- Look at its vertical position → determine Y value
- Do NOT smooth or interpolate - real data is often irregular

IMPORTANT FOR LINE CHARTS:
- Count the actual markers/dots on the line, not just the line endpoints
- Each marker may have a DIFFERENT Y value - do not assume a pattern
- If markers are dense (close together), take extra care to read each one

Output ONLY valid JSON:
{
    "chart_type": "line" or "scatter" or "bar",
    "x_label": "axis label",
    "y_label": "axis label",
    "point_count": number of data points you counted,
    "data": [{"x": value, "y": value}, ...]
}

VERIFICATION: Your data array length should match point_count."""

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
