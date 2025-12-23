"""
Data point extraction for different chart types.

Implements multiple extraction strategies for scatter plots:
- Color-based detection (primary)
- Blob detection with grid removal (fallback)
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List


def remove_grid_lines(binary: np.ndarray) -> np.ndarray:
    """
    Remove horizontal and vertical grid lines from binary image.

    Uses morphological operations to detect and remove lines.
    """
    h, w = binary.shape

    # Create horizontal kernel (long and thin)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (w // 30, 1))
    # Detect horizontal lines
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Create vertical kernel (thin and tall)
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, h // 30))
    # Detect vertical lines
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # Combine lines
    grid_mask = cv2.bitwise_or(horizontal_lines, vertical_lines)

    # Dilate slightly to catch edges
    dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    grid_mask = cv2.dilate(grid_mask, dilate_kernel, iterations=1)

    # Remove grid from original
    cleaned = cv2.bitwise_and(binary, cv2.bitwise_not(grid_mask))

    return cleaned


def extract_scatter_points(
    image: np.ndarray,
    crop_box: Optional[Tuple[int, int, int, int]] = None,
    method: str = "auto"
) -> Tuple[np.ndarray, float]:
    """
    Extract scatter plot points using best available method.

    Args:
        image: BGR image from cv2.imread()
        crop_box: Optional (x1, y1, x2, y2) crop region
        method: "auto", "color", or "blob"

    Returns:
        Tuple of (points, confidence)
        points: Nx2 array of (x, y) pixel coordinates
        confidence: 0.0-1.0 extraction quality estimate
    """
    # Try color-based first (works best for colored scatter points)
    if method in ("auto", "color"):
        points_color, conf_color = extract_scatter_points_color(image, crop_box)

        if method == "color" or (len(points_color) > 0 and conf_color >= 0.7):
            return points_color, conf_color

    # Fall back to improved blob detection
    if method in ("auto", "blob"):
        points_blob, conf_blob = extract_scatter_points_blob(image, crop_box)

        if method == "blob":
            return points_blob, conf_blob

        # In auto mode, return whichever found more reasonable results
        if len(points_color) == 0:
            return points_blob, conf_blob
        if len(points_blob) == 0:
            return points_color, conf_color

        # Prefer color method if it found points
        return points_color, conf_color

    return np.array([]), 0.1


def extract_scatter_points_color(
    image: np.ndarray,
    crop_box: Optional[Tuple[int, int, int, int]] = None
) -> Tuple[np.ndarray, float]:
    """
    Extract scatter points using color-based detection.

    Works well for colored points on white/gray backgrounds.
    Filters out grayscale elements (grid, axes, text).
    """
    # Crop if specified
    if crop_box:
        x1, y1, x2, y2 = crop_box
        cropped = image[y1:y2, x1:x2]
        offset_x, offset_y = x1, y1
    else:
        cropped = image
        offset_x, offset_y = 0, 0

    # Convert to HSV for color detection
    hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

    # Saturation channel - colored pixels have high saturation
    # Gray/white/black have low saturation
    saturation = hsv[:, :, 1]

    # Threshold saturation to find colored regions
    # Colored points typically have saturation > 50
    _, color_mask = cv2.threshold(saturation, 40, 255, cv2.THRESH_BINARY)

    # Clean up noise with morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
    color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)

    # Find contours
    contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and extract centroids
    points = []
    areas = []

    for contour in contours:
        area = cv2.contourArea(contour)

        # Filter by area (scatter points are typically 20-2000 pixels)
        if area < 10 or area > 5000:
            continue

        # Calculate circularity to filter out elongated shapes (text, lines)
        perimeter = cv2.arcLength(contour, True)
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            # Accept points with circularity > 0.3 (circles have ~1.0)
            if circularity < 0.3:
                continue

        # Get centroid
        M = cv2.moments(contour)
        if M["m00"] > 0:
            cx = M["m10"] / M["m00"] + offset_x
            cy = M["m01"] / M["m00"] + offset_y
            points.append((cx, cy))
            areas.append(area)

    points = np.array(points) if points else np.array([]).reshape(0, 2)

    # Calculate confidence
    confidence = _calculate_confidence(points, areas)

    return points, confidence


def extract_scatter_points_blob(
    image: np.ndarray,
    crop_box: Optional[Tuple[int, int, int, int]] = None
) -> Tuple[np.ndarray, float]:
    """
    Extract scatter plot points using blob detection with grid removal.

    Args:
        image: BGR image from cv2.imread()
        crop_box: Optional (x1, y1, x2, y2) crop region

    Returns:
        Tuple of (points, confidence)
        points: Nx2 array of (x, y) pixel coordinates
        confidence: 0.0-1.0 extraction quality estimate
    """
    # Crop if specified
    if crop_box:
        x1, y1, x2, y2 = crop_box
        cropped = image[y1:y2, x1:x2]
        offset_x, offset_y = x1, y1
    else:
        cropped = image
        offset_x, offset_y = 0, 0

    # Convert to grayscale
    if len(cropped.shape) == 3:
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    else:
        # Use copy only if we need to modify it later or ensure ownership
        # Here we only read it for brightness check and thresholding
        gray = cropped

    # Invert if needed (white background → black points)
    mean_brightness = np.mean(gray)
    if mean_brightness > 127:
        binary = cv2.bitwise_not(gray)
    else:
        binary = gray

    # Threshold to binary
    _, binary = cv2.threshold(binary, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Remove grid lines
    binary = remove_grid_lines(binary)

    # Blob detector with tuned parameters
    params = cv2.SimpleBlobDetector_Params()

    # Threshold settings
    params.minThreshold = 10
    params.maxThreshold = 200

    # Filter by area
    params.filterByArea = True
    params.minArea = 15  # Increased to avoid grid remnants
    params.maxArea = 2000  # Increased for larger points

    # Filter by circularity (scatter points are usually round)
    params.filterByCircularity = True
    params.minCircularity = 0.5

    # Filter by convexity
    params.filterByConvexity = True
    params.minConvexity = 0.7

    # Filter by inertia (roundness)
    params.filterByInertia = True
    params.minInertiaRatio = 0.4

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(binary)

    # Extract centroids
    if keypoints:
        points = np.array([
            (kp.pt[0] + offset_x, kp.pt[1] + offset_y)
            for kp in keypoints
        ])
        areas = [kp.size ** 2 * np.pi / 4 for kp in keypoints]
    else:
        points = np.array([]).reshape(0, 2)
        areas = []

    confidence = _calculate_confidence(points, areas)

    return points, confidence


def _calculate_confidence(points: np.ndarray, areas: List[float]) -> float:
    """
    Calculate extraction confidence based on multiple factors.
    """
    num_points = len(points)

    if num_points == 0:
        return 0.1

    confidence = 0.5  # Base confidence

    # Factor 1: Point count (reasonable range)
    if 3 <= num_points <= 200:
        confidence += 0.2
    elif num_points > 500:
        confidence -= 0.2  # Likely noise

    # Factor 2: Consistent point sizes
    if len(areas) >= 3:
        area_std = np.std(areas)
        area_mean = np.mean(areas)
        if area_mean > 0:
            cv = area_std / area_mean  # Coefficient of variation
            if cv < 0.5:  # Low variation = consistent points
                confidence += 0.2
            elif cv > 1.5:  # High variation = mixed sources
                confidence -= 0.1

    # Factor 3: Point distribution (not clustered at edges)
    if num_points >= 3 and points.shape[1] == 2:
        x_range = np.ptp(points[:, 0])
        y_range = np.ptp(points[:, 1])
        if x_range > 50 and y_range > 50:  # Points spread out
            confidence += 0.1

    return max(0.1, min(1.0, confidence))


def extract_line_points(
    image: np.ndarray,
    crop_box: Optional[Tuple[int, int, int, int]] = None
) -> Tuple[np.ndarray, float]:
    """
    Extract points from a line chart.
    
    Strategy:
    1. Skeletonize the lines
    2. Optional: track single dominant line
    3. Sample points along the skeleton
    """
    if crop_box:
        x1, y1, x2, y2 = crop_box
        roi = image[y1:y2, x1:x2]
    else:
        roi = image
        x1, y1, x2, y2 = 0, 0, image.shape[1], image.shape[0]

    # Preprocess
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Remove grid
    from chart2csv.core.extraction import remove_grid_lines
    binary = remove_grid_lines(binary)

    # Skeletonization (simplified)
    kernel = np.ones((3,3), np.uint8)
    skeleton = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    # Find active pixels
    y_coords, x_coords = np.where(skeleton > 0)
    
    # For a single line chart, we can group by X and take average Y
    if len(x_coords) == 0:
        return np.array([]), 0.1
        
    unique_x = np.unique(x_coords)
    points = []
    for ux in unique_x:
        uy = np.mean(y_coords[x_coords == ux])
        points.append((ux + x1, uy + y1))
        
    points = np.array(points)
    
    # Confidence based on continuity
    continuity = len(unique_x) / (x2 - x1) if (x2 - x1) > 0 else 0
    confidence = min(1.0, 0.4 + 0.6 * continuity)
    
    return points, confidence


def extract_bar_data(
    image: np.ndarray,
    crop_box: Optional[Tuple[int, int, int, int]] = None
) -> Tuple[np.ndarray, float]:
    """
    Extract data from a bar chart.
    
    Strategy:
    1. Detect rectangular contours
    2. Filter for vertical bars
    3. Extract top-center positions
    """
    if crop_box:
        x1, y1, x2, y2 = crop_box
        roi = image[y1:y2, x1:x2]
    else:
        roi = image
        x1, y1, x2, y2 = 0, 0, image.shape[1], image.shape[0]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Remove grid
    from chart2csv.core.extraction import remove_grid_lines
    binary = remove_grid_lines(binary)
    
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    points = []
    for cnt in contours:
        bx, by, bw, bh = cv2.boundingRect(cnt)
        
        # Filter for bars (aspect ratio, minimum size)
        if bh > 10 and bw > 5:
            # Bar top center
            points.append((bx + bw/2 + x1, by + y1))
            
    # Sort by X
    points.sort(key=lambda p: p[0])
    points = np.array(points)
    
    # Confidence based on finding at least some bars
    confidence = 0.5 + 0.4 * (1.0 if len(points) > 0 else 0.0)
    
    return points, confidence


def visualize_extracted_points(
    image: np.ndarray,
    points: np.ndarray,
    output_path: Optional[str] = None
) -> np.ndarray:
    """
    Draw extracted points on image for verification.

    Args:
        image: Original BGR image
        points: Nx2 array of (x, y) coordinates
        output_path: Optional path to save visualization

    Returns:
        Image with points drawn
    """
    vis = image.copy()

    for (x, y) in points:
        cv2.circle(vis, (int(x), int(y)), 5, (0, 0, 255), 2)  # Red circles

    if output_path:
        cv2.imwrite(output_path, vis)

    return vis
