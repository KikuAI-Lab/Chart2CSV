"""
Export utilities for CSV, JSON, and overlay generation.
"""

import json
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

from chart2csv.core.types import ChartResult, ChartType


def export_csv(result: ChartResult, output_path: str):
    """
    Export extracted data to CSV.

    Args:
        result: ChartResult with extracted data
        output_path: Path for CSV file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = result.data

    if result.chart_type in [ChartType.SCATTER, ChartType.LINE]:
        # x,y format
        header = "x,y\n"
        rows = [f"{x:.6g},{y:.6g}\n" for x, y in data]
    elif result.chart_type == ChartType.BAR:
        # category,value or x,value
        header = "x,value\n"
        rows = [f"{x:.6g},{y:.6g}\n" for x, y in data]
    else:
        raise ValueError(f"Cannot export chart type: {result.chart_type}")

    with open(output_path, "w") as f:
        f.write(header)
        f.writelines(rows)


def export_json(result: ChartResult, output_path: str):
    """
    Export metadata to JSON.

    Args:
        result: ChartResult with metadata
        output_path: Path for JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = result.to_dict()

    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)


def generate_overlay(
    original_image: np.ndarray,
    data: np.ndarray,
    crop_box: tuple[int, int, int, int],
    axes: Dict[str, int],
    chart_type: ChartType
) -> np.ndarray:
    """
    Generate overlay image showing extracted data on original.

    Args:
        original_image: Original BGR image
        data: Extracted data points (pixel coordinates)
        crop_box: Crop box (x1, y1, x2, y2)
        axes: Detected axes positions
        chart_type: Type of chart

    Returns:
        BGR image with overlay
    """
    # Make a copy
    overlay = original_image.copy()

    # Colors (BGR)
    COLOR_CROP = (0, 255, 0)      # Green
    COLOR_AXIS = (255, 0, 0)      # Blue
    COLOR_DATA = (0, 0, 255)      # Red
    COLOR_TEXT = (255, 255, 255)  # White

    # 1. Draw crop box
    x1, y1, x2, y2 = crop_box
    cv2.rectangle(overlay, (x1, y1), (x2, y2), COLOR_CROP, 2)
    cv2.putText(overlay, "Plot Area", (x1, y1 - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_CROP, 1)

    # 2. Draw axes
    x_axis_y = axes["x"]
    y_axis_x = axes["y"]
    
    # X axis
    cv2.line(overlay, (x1, x_axis_y), (x2, x_axis_y), COLOR_AXIS, 2)
    # Y axis
    cv2.line(overlay, (y_axis_x, y1), (y_axis_x, y2), COLOR_AXIS, 2)

    # 3. Draw extracted data
    if chart_type == ChartType.SCATTER:
        for (x, y) in data:
            cv2.circle(overlay, (int(x), int(y)), 4, COLOR_DATA, -1)
    elif chart_type == ChartType.LINE:
        if len(data) > 1:
            for i in range(len(data) - 1):
                p1 = (int(data[i][0]), int(data[i][1]))
                p2 = (int(data[i+1][0]), int(data[i+1][1]))
                cv2.line(overlay, p1, p2, COLOR_DATA, 2)
    elif chart_type == ChartType.BAR:
        for (x, y) in data:
            # Draw a marker at the top middle of the bar
            cv2.drawMarker(overlay, (int(x), int(y)), COLOR_DATA, 
                          cv2.MARKER_TILTED_CROSS, 10, 2)

    # 4. Add summary info
    info_text = f"Type: {chart_type.value} | Points: {len(data)}"
    cv2.putText(overlay, info_text, (10, original_image.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(overlay, info_text, (10, original_image.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_TEXT, 1)

    return overlay


def save_overlay(overlay: np.ndarray, output_path: str):
    """
    Save overlay image to file.

    Args:
        overlay: BGR overlay image
        output_path: Path for output image
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cv2.imwrite(str(output_path), overlay)
