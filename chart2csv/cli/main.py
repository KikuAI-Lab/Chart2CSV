import argparse
import sys
import os
from pathlib import Path
import cv2

from chart2csv.core.pipeline import extract_chart
from chart2csv.core.types import ChartType, Scale
from chart2csv.core.export import export_csv, export_json, save_overlay
from chart2csv.core.calibration import get_calibration_from_user

def main():
    parser = argparse.ArgumentParser(
        description="Chart2CSV - Extract data from chart images",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("input", help="Input image file or directory")
    parser.add_argument("--output", "-o", help="Output CSV file")
    parser.add_argument("--metadata", help="Output JSON metadata file")
    parser.add_argument("--overlay", help="Output overlay image file")
    
    # Overrides
    parser.add_argument("--chart-type", choices=[c.value for c in ChartType], help="Force chart type")
    parser.add_argument("--x-scale", choices=["linear", "log"], default="linear", help="X-axis scale")
    parser.add_argument("--y-scale", choices=["linear", "log"], default="linear", help="Y-axis scale")
    parser.add_argument("--crop", help="Manual crop x1,y1,x2,y2")
    parser.add_argument("--x-axis", type=int, help="Manual X-axis Y-position")
    parser.add_argument("--y-axis", type=int, help="Manual Y-axis X-position")
    parser.add_argument("--calibrate", action="store_true", help="Manual calibration")
    
    # Batch options
    parser.add_argument("--batch", action="store_true", help="Process directory")
    parser.add_argument("--output-dir", help="Output directory for batch mode")

    args = parser.parse_args()

    # Handle single file vs batch
    if args.batch:
        process_batch(args)
    else:
        process_single(args)

def process_single(args):
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    # Handle calibration
    calibration = None
    if args.calibrate:
        calibration = get_calibration_from_user()

    # Parse crop
    crop = None
    if args.crop:
        crop = tuple(map(int, args.crop.split(",")))

    print(f"Processing {input_path}...")
    
    try:
        result = extract_chart(
            image_path=input_path,
            crop=crop,
            x_axis_pos=args.x_axis,
            y_axis_pos=args.y_axis,
            x_scale=Scale(args.x_scale),
            y_scale=Scale(args.y_scale),
            chart_type=ChartType(args.chart_type) if args.chart_type else None,
            calibration_points=calibration,
            generate_overlay_image=True if args.overlay else False
        )
    except Exception as e:
        print(f"Error during extraction: {e}")
        sys.exit(1)

    # Save results
    csv_path = args.output or input_path.with_suffix(".csv")
    export_csv(result, csv_path)
    print(f"✓ Saved data to {csv_path}")

    if args.metadata:
        export_json(result, args.metadata)
        print(f"✓ Saved metadata to {args.metadata}")

    if args.overlay and result.overlay is not None:
        save_overlay(result.overlay, args.overlay)
        print(f"✓ Saved overlay to {args.overlay}")

    # Summary
    print(f"\nExtraction complete:")
    print(f"  Chart Type: {result.chart_type.value}")
    print(f"  Confidence: {result.confidence.overall():.2f}")
    if result.warnings:
        print(f"  Warnings: {len(result.warnings)}")
        for w in result.warnings:
            print(f"    - [{w.code.value}] {w.message}")

def process_batch(args):
    input_dir = Path(args.input)
    if not input_dir.is_dir():
        print(f"Error: Not a directory: {input_dir}")
        sys.exit(1)

    output_dir = Path(args.output_dir or "output")
    output_dir.mkdir(parents=True, exist_ok=True)

    extensions = [".png", ".jpg", ".jpeg"]
    files = [f for f in input_dir.iterdir() if f.suffix.lower() in extensions]

    print(f"Batch processing {len(files)} files into {output_dir}...")

    for f in files:
        print(f"  [{f.name}]", end=" ", flush=True)
        try:
            result = extract_chart(f, generate_overlay_image=True)
            export_csv(result, output_dir / f.with_suffix(".csv").name)
            save_overlay(result.overlay, (output_dir / f"{f.stem}_overlay.png"))
            print(f"✓ (conf: {result.confidence.overall():.2f})")
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()
