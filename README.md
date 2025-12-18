# Chart2CSV - Plot Digitizer

Extract data from chart images (PNG/JPG/PDF) to CSV/JSON with Computer Vision and OCR.

## Problem

Scientific papers, reports, and presentations often contain charts without source data. Researchers, analysts, and data scientists need to extract numbers from chart images quickly and reproducibly.

## Solution

**Chart2CSV** is an offline-first CLI tool that:
- Takes PNG/JPG chart images (or PDF pages)
- Returns CSV data + JSON metadata + confidence scores + visual overlay
- Provides honest confidence reporting and manual calibration fallback
- Works completely offline (privacy by default)

## Quick Start

```bash
# Install
pip install chart2csv

# Basic usage
python -m chart2csv.cli.main plot.png --output data.csv

# With overlay for verification
python -m chart2csv.cli.main plot.png --overlay check.png

# Batch processing
python -m chart2csv.cli.main figures/ --batch --output-dir results/

# Manual calibration (when auto fails)
python -m chart2csv.cli.main plot.png --calibrate
```

## Supported Chart Types (MVP)

- ✅ Scatter plots
- ✅ Line plots (single line)
- ✅ Bar charts (simple columns)
- ✅ Linear scales only
- ⏳ Log scale (via manual calibration)
- ❌ Multi-series (roadmap)
- ❌ Dual-axis (roadmap)
- ❌ Stacked bars (roadmap)

## Key Features

### MVP (v0.1.0)
1. **PNG/JPG input** - Standard image formats
2. **Auto-detection** - Plot area, axes, tick labels (best-effort)
3. **Manual overrides** - `--crop`, `--x-axis`, `--y-axis` when auto fails
4. **OCR tick labels** - Tesseract-based number recognition
5. **CSV/JSON export** - Clean data + metadata
6. **Overlay generation** - Visual proof of extraction
7. **Confidence scoring** - 0.0-1.0 with clear zones (high/medium/low)
8. **Warning system** - Honest diagnostics (OCR_FAILED, POSSIBLE_LOG_SCALE, etc.)
9. **Calibration fallback** - Numeric input mode when auto fails
10. **Benchmark mode** - Measure quality on your own fixtures

### Not in MVP
- Multi-series + legend parsing
- Dual-axis charts
- Auto log-scale detection
- Click-based calibration UI
- PDF multi-page auto
- Web UI / API / Telegram bot
- Automatic rotation correction

## Philosophy

**Better to say "not sure" than give wrong data silently.**

- **Confidence is honest** - We tell you when OCR fails
- **Fallback is fast** - Manual calibration takes 15-30 seconds
- **Overlay is proof** - Visual verification included
- **Privacy first** - Everything runs locally, no network

## Use Cases

### 1. Researcher extracting competitor data
```bash
chart2csv competitor_fig2.png
# → CSV with coordinates, confidence 0.82, overlay shows match
# Moment of joy: "Seconds instead of 30 minutes in WebPlotDigitizer"
```

### 2. Analyst batch-processing client report
```bash
chart2csv batch reports/*.png --output-dir extracted/
# → 15 CSV + summary (12 success, 3 low confidence warnings)
# Moment of joy: "Automated what took all day manually"
```

### 3. Student with low-res scan
```bash
chart2csv old_scan.jpg
# → confidence 0.31, warning "OCR_FAILED"

chart2csv old_scan.jpg --calibrate
# → Interactive: click 2 points on X, 2 on Y, enter values
# → CSV with line, confidence ≥0.8
# Moment of joy: "Tool doesn't lie about quality, gives fallback"
```

### 4. ML engineer building dataset
```bash
chart2csv batch papers/*.png --min-confidence 0.7 --output-dir data/
# → 156 success, 44 skipped (low confidence), JSON report
# Moment of joy: "Focus only on 44 hard cases, not all 200"
```

### 5. Compliance/offline requirement
```bash
chart2csv internal.pdf --pages 3,7
# → Data extracted locally, no network, with overlay
# Moment of joy: "Can use in closed environment - compliance out of the box"
```

## Installation

### Prerequisites
- Python 3.8+
- Tesseract OCR (system dependency)
- Poppler/Ghostscript (for PDF, optional)

### Install Tesseract

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### Install Chart2CSV

```bash
pip install chart2csv
```

Or from source:
```bash
git clone https://github.com/yourusername/chart2csv.git
cd chart2csv
pip install -e .
```

## Usage Examples

### Basic Extraction
```bash
# Auto mode
chart2csv plot.png

# Specify output
chart2csv plot.png --output data.csv --metadata meta.json

# Generate overlay for verification
chart2csv plot.png --overlay proof.png
```

### Manual Overrides (when auto fails)
```bash
# Manual crop
chart2csv plot.png --crop 50,30,750,620

# Manual axes
chart2csv plot.png --x-axis y=600 --y-axis x=80

# Force chart type
chart2csv plot.png --chart-type scatter

# Log scale (with calibration)
chart2csv plot.png --calibrate --y-scale log
```

### Batch Processing
```bash
# Process folder
chart2csv batch figures/*.png --output-dir results/

# Filter by confidence
chart2csv batch papers/*.png --min-confidence 0.6 --output-dir clean/

# Parallel processing (roadmap)
chart2csv batch data/*.png --jobs 4
```

### Calibration Mode
```bash
chart2csv plot.png --calibrate

# Interactive prompts:
# Enter pixel X for left tick: 120
# Enter value for that tick: 0.0
# Enter pixel X for right tick: 680
# Enter value for that tick: 100.0
# (repeat for Y axis)
```

### Benchmark Your Fixtures
```bash
# Run benchmark
chart2csv benchmark my_fixtures/ --output bench.json

# Metrics reported:
# - success_without_calibration
# - requires_calibration
# - median_runtime_ms
# - ocr_tick_success_rate
```

## Output Formats

### CSV
```csv
x,y
0.0,12.5
10.2,15.3
20.1,18.7
...
```

### JSON Metadata
```json
{
  "chart_type": "scatter",
  "confidence": 0.82,
  "warnings": ["LOW_RESOLUTION"],
  "axes": {
    "x": {"min": 0, "max": 100, "scale": "linear"},
    "y": {"min": -5, "max": 50, "scale": "linear"}
  },
  "num_points": 30,
  "runtime_ms": 1234,
  "ocr_success_rate": 0.85
}
```

## Confidence Zones

| Zone | Range | Meaning | Action |
|------|-------|---------|--------|
| **High** | ≥0.7 | Likely correct | Use data |
| **Medium** | 0.4-0.7 | Check overlay | Consider calibration |
| **Low** | <0.4 | Don't use | Requires calibration |

### Confidence Formula
```
confidence = (
    0.3 × crop_confidence +
    0.25 × axis_confidence +
    0.3 × ocr_confidence +
    0.15 × extraction_confidence
)
```

## Warning System

| Warning | Cause | Recommendation |
|---------|-------|----------------|
| `LOW_RESOLUTION` | Image <600px | Use higher resolution |
| `CROP_UNCERTAIN` | Auto crop failed | Use `--crop x1,y1,x2,y2` |
| `AXES_UNCERTAIN` | Axes not found | Use `--x-axis`/`--y-axis` |
| `SKEW_DETECTED` | Axes not perpendicular | Rotate image first |
| `OCR_FAILED` | <40% ticks recognized | Use `--calibrate` |
| `OCR_PARTIAL` | 40-60% ticks recognized | Check overlay, consider `--calibrate` |
| `POSSIBLE_LOG_SCALE` | Linear fit poor | Use `--calibrate --y-scale log` |
| `MULTI_SERIES_DETECTED` | Multiple lines found | Not supported in MVP |
| `LEGEND_DETECTED` | Text blocks detected | Multi-series not supported |
| `NOISE_DETECTED` | Too many points | Check overlay |

## Architecture

```
chart2csv/
  core/           # Pure CV/OCR logic (library)
    pipeline.py   # Main: extract_chart(img) -> ChartResult
    preprocess.py # Image cleanup
    detection.py  # Axes, ticks, plot area
    ocr.py        # Tesseract wrapper
    transform.py  # Pixel→value mapping
    export.py     # CSV/JSON writers
    types.py      # ChartResult, Confidence, Warnings
  cli/            # CLI interface
    main.py       # argparse + core calls
    calibrate.py  # Interactive calibration
    batch.py      # Batch processing
  api/            # (empty in MVP, ready for later)
  tests/          # Unit tests
  fixtures/       # Benchmark dataset
```

## Roadmap

### MVP (v0.1.0) - 7-10 days
- ✅ Core pipeline (preprocess, detect, OCR, extract)
- ✅ 3 chart types (scatter, line, bar)
- ✅ CLI with overrides
- ✅ Calibration fallback
- ✅ Confidence + warnings
- ✅ Overlay generation
- ✅ Benchmark mode

### Iteration 1 (v0.2.0) - 2-3 weeks
- Click-based calibration UI
- PDF multi-page support (Pro)
- Batch parallelization
- Grid removal option
- Improved OCR (preprocessing variants)

### Iteration 2 (v0.3.0) - 2-3 weeks
- Log-scale auto-detection
- Multi-series support (beta)
- Legend parsing (beta)
- API wrapper (FastAPI)
- Web UI prototype

### Iteration 3 (v0.4.0) - 2-3 weeks
- Dual-axis support
- Stacked bars
- Advanced confidence (ML-based)
- Telegram bot interface
- Enterprise features

## Monetization

- **Free tier:** PNG single file, basic chart types, open source
- **Pro license:** $29-99 one-time or $9-19/month
  - PDF pages
  - Batch folders
  - Overlay generation
  - Benchmark mode
  - Priority support
- **Enterprise:** Custom binaries, on-premise deployment, training on custom data

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License (core library)

See [THIRD_PARTY.md](THIRD_PARTY.md) for dependency licenses:
- Tesseract: Apache 2.0
- OpenCV: Apache 2.0
- pypdfium2: Apache 2.0/BSD-3-Clause

## Support

- **Documentation:** [docs/](docs/)
- **Issues:** https://github.com/yourusername/chart2csv/issues
- **Discussions:** https://github.com/yourusername/chart2csv/discussions

## Citation

If you use Chart2CSV in research, please cite:

```bibtex
@software{chart2csv,
  title = {Chart2CSV: Honest Plot Digitizer with Confidence Scoring},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/chart2csv}
}
```

---

**Made with honesty. Privacy-first. Offline-capable.**
