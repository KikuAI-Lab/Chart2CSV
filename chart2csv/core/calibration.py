"""
Manual calibration input for Chart2CSV.

Provides interactive prompts for users to specify calibration points
when auto-detection fails.
"""

from typing import Dict, List, Tuple


def get_calibration_from_user() -> Dict[str, List[Tuple[int, float]]]:
    """
    Prompt user for manual calibration points.

    User provides 2 points per axis:
    - For X-axis: left tick and right tick (pixel X, value)
    - For Y-axis: bottom tick and top tick (pixel Y, value)

    Returns:
        Dictionary with calibration points:
        {
            "x": [(pixel1, value1), (pixel2, value2)],
            "y": [(pixel1, value1), (pixel2, value2)]
        }

    Example:
        >>> calib = get_calibration_from_user()
        X-axis calibration:
          Left tick pixel X: 100
          Left tick value: 0.0
          Right tick pixel X: 700
          Right tick value: 100.0
        Y-axis calibration:
          Bottom tick pixel Y: 500
          Bottom tick value: 0.0
          Top tick pixel Y: 100
          Top tick value: 50.0
    """
    print("\n" + "="*50)
    print("MANUAL CALIBRATION")
    print("="*50)
    print("Please provide calibration points for both axes.")
    print("Pixel coordinates are in image space (0,0 = top-left).")
    print()

    # X-axis calibration
    print("X-AXIS CALIBRATION:")
    print("-" * 30)

    try:
        x1_px = int(input("  Left tick pixel X: "))
        x1_val = float(input("  Left tick value: "))
        x2_px = int(input("  Right tick pixel X: "))
        x2_val = float(input("  Right tick value: "))
    except (ValueError, EOFError) as e:
        raise ValueError(f"Invalid input for X-axis calibration: {e}")

    print()

    # Y-axis calibration
    print("Y-AXIS CALIBRATION:")
    print("-" * 30)

    try:
        y1_px = int(input("  Bottom tick pixel Y: "))
        y1_val = float(input("  Bottom tick value: "))
        y2_px = int(input("  Top tick pixel Y: "))
        y2_val = float(input("  Top tick value: "))
    except (ValueError, EOFError) as e:
        raise ValueError(f"Invalid input for Y-axis calibration: {e}")

    print()
    print("="*50)
    print("Calibration complete!")
    print(f"  X: {x1_val} @ px {x1_px} → {x2_val} @ px {x2_px}")
    print(f"  Y: {y1_val} @ px {y1_px} → {y2_val} @ px {y2_px}")
    print("="*50)
    print()

    return {
        "x": [(x1_px, x1_val), (x2_px, x2_val)],
        "y": [(y1_px, y1_val), (y2_px, y2_val)]
    }


def validate_calibration(
    calibration: Dict[str, List[Tuple[int, float]]]
) -> bool:
    """
    Validate calibration points.

    Checks:
    - Two points per axis
    - Points are different
    - Pixel coordinates are positive

    Args:
        calibration: Calibration dictionary from get_calibration_from_user()

    Returns:
        True if valid, False otherwise
    """
    for axis in ["x", "y"]:
        if axis not in calibration:
            return False

        points = calibration[axis]

        if len(points) != 2:
            return False

        (px1, val1), (px2, val2) = points

        # Check pixels are different
        if px1 == px2:
            print(f"Error: {axis}-axis points have same pixel coordinate")
            return False

        # Check pixels are positive
        if px1 < 0 or px2 < 0:
            print(f"Error: {axis}-axis has negative pixel coordinate")
            return False

        # Check values are different
        if val1 == val2:
            print(f"Warning: {axis}-axis points have same value")

    return True
