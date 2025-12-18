"""
Minimal CLI for Chart2CSV vertical slice.

Simple command-line interface for testing the core pipeline:
- Manual calibration
- Scatter point extraction
- CSV output
"""

import argparse
import sys
from pathlib import Path
import cv2
import numpy as np

from chart2csv.core.calibration import get_calibration_from_user, validate_calibration
from chart2csv.core.extraction import extract_scatter_points, visualize_extracted_points
from chart2csv.core.transform import build_transform, apply_transform
from chart2csv.core.autocrop import detect_plot_area


def parse_crop(crop_str: str) -> tuple:
    """Parse crop string 'x1,y1,x2,y2' to tuple."""
    try:
        parts = crop_str.split(',')
        if len(parts) != 4:
            raise ValueError("Crop must be 4 values: x1,y1,x2,y2")
        return tuple(map(int, parts))
    except Exception as e:
        raise ValueError(f"Invalid crop format: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Chart2CSV Minimal - Extract data from scatter plots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with calibration
  python -m chart2csv.cli.minimal plot.png --calibrate

  # With crop box
  python -m chart2csv.cli.minimal plot.png --calibrate --crop 50,50,750,550

  # Specify output file
  python -m chart2csv.cli.minimal plot.png --calibrate --output data.csv

  # Save visualization
  python -m chart2csv.cli.minimal plot.png --calibrate --visualize check.png
        """
    )

    parser.add_argument(
        "image",
        type=str,
        help="Input image file (PNG/JPG)"
    )

    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="Use manual calibration (interactive prompts)"
    )

    parser.add_argument(
        "--crop",
        type=str,
        default=None,
        help="Crop box as x1,y1,x2,y2 (default: use full image)"
    )

    parser.add_argument(
        "--auto-crop",
        action="store_true",
        help="Automatically detect plot area boundaries"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output CSV file (default: <input>_output.csv)"
    )

    parser.add_argument(
        "--visualize",
        type=str,
        default=None,
        help="Save visualization image with extracted points"
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.image)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    print()
    print("="*60)
    print("CHART2CSV - Minimal Scatter Extraction")
    print("="*60)
    print(f"Input: {input_path}")
    print()

    # Load image
    print("Loading image...")
    image = cv2.imread(str(input_path))
    if image is None:
        print(f"Error: Failed to load image: {input_path}", file=sys.stderr)
        return 1

    h, w = image.shape[:2]
    print(f"  Image size: {w}x{h}")

    # Parse crop box
    crop_box = None
    if args.crop:
        try:
            crop_box = parse_crop(args.crop)
            print(f"  Crop box (manual): {crop_box}")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    elif getattr(args, 'auto_crop', False):
        print("  Detecting plot area...")
        crop_box, crop_conf = detect_plot_area(image)
        if crop_box:
            print(f"  Crop box (auto): {crop_box}")
            print(f"  Detection confidence: {crop_conf:.2f}")
        else:
            print("  Auto-crop failed, using full image")
    else:
        print("  Crop: Using full image")

    print()

    # Get calibration
    if not args.calibrate:
        print("Error: --calibrate is required in minimal CLI", file=sys.stderr)
        print("       (Auto-detection coming in Phase 2)", file=sys.stderr)
        return 1

    calibration = get_calibration_from_user()

    if not validate_calibration(calibration):
        print("Error: Invalid calibration", file=sys.stderr)
        return 1

    # Build transform
    print("Building coordinate transform...")
    transform, fit_error = build_transform(
        calibration_points=calibration
    )
    print(f"  Transform built (fit_error: {fit_error:.4f})")
    print()

    # Extract scatter points
    print("Extracting scatter points...")
    points_px, extraction_conf = extract_scatter_points(image, crop_box)

    if len(points_px) == 0:
        print("Warning: No points detected!", file=sys.stderr)
        print("  Try adjusting crop box or check image", file=sys.stderr)
        return 1

    print(f"  Detected {len(points_px)} points")
    print(f"  Extraction confidence: {extraction_conf:.2f}")
    print()

    # Transform to values
    print("Transforming pixel coordinates to values...")
    points_values = apply_transform(points_px, transform)
    print(f"  Transformed {len(points_values)} points")
    print()

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_output.csv"

    # Save CSV
    print(f"Saving CSV to: {output_path}")
    save_csv(points_values, output_path)
    print("  ✓ CSV saved")
    print()

    # Save visualization if requested
    if args.visualize:
        vis_path = Path(args.visualize)
        print(f"Saving visualization to: {vis_path}")
        visualize_extracted_points(image, points_px, str(vis_path))
        print("  ✓ Visualization saved")
        print()

    # Summary
    print("="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)
    print(f"Points extracted: {len(points_values)}")
    print(f"Output CSV: {output_path}")
    if args.visualize:
        print(f"Visualization: {args.visualize}")
    print()
    print("Next steps:")
    print("  1. Open CSV to verify data")
    if args.visualize:
        print("  2. Check visualization to verify point detection")
    print("="*60)
    print()

    return 0


def save_csv(points: np.ndarray, output_path: Path):
    """
    Save points to CSV file.

    Args:
        points: Nx2 array of (x, y) values
        output_path: Output file path
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("x,y\n")
        for x, y in points:
            f.write(f"{x:.6f},{y:.6f}\n")


if __name__ == '__main__':
    sys.exit(main())
