# Chart2CSV - Quick Start Guide

## 5-Minute Setup

### 1. Install Tesseract (System Dependency)

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

### 2. Install Chart2CSV

```bash
# From source (development)
git clone https://github.com/yourusername/chart2csv.git
cd chart2csv
pip install -e .

# Or from PyPI (when released)
pip install chart2csv
```

### 3. Try It

```bash
# Download a test image
curl -o test_plot.png https://example.com/sample_chart.png

# Extract data
chart2csv test_plot.png --output data.csv --overlay proof.png

# Check results
cat data.csv
open proof.png  # macOS
# or: xdg-open proof.png  # Linux
```

## Common Workflows

### Workflow 1: Quick Extraction
```bash
chart2csv plot.png
# → plot.csv (default output)
```

### Workflow 2: With Verification
```bash
chart2csv plot.png --overlay check.png

# View overlay to verify extraction
open check.png
```

### Workflow 3: Low Confidence → Calibration
```bash
chart2csv plot.png
# Output: "Confidence: 0.35 (low) - Use --calibrate"

chart2csv plot.png --calibrate
# Interactive prompts:
# Enter pixel X for left tick: 120
# Enter value for that tick: 0.0
# ...
```

### Workflow 4: Batch Processing
```bash
chart2csv batch figures/*.png --output-dir results/

# Summary:
# ✓ 12 success
# ⚠ 3 low confidence
# ✗ 0 failed
```

### Workflow 5: Manual Overrides
```bash
# If auto crop fails
chart2csv plot.png --crop 50,30,750,620

# If axes not detected
chart2csv plot.png --x-axis y=600 --y-axis x=80

# Force chart type
chart2csv plot.png --chart-type scatter
```

## Understanding Output

### CSV File
```csv
x,y
0.0,12.5
10.2,15.3
20.1,18.7
```

### JSON Metadata
```json
{
  "chart_type": "scatter",
  "confidence": 0.82,
  "warnings": [],
  "axes": {
    "x": {"min": 0, "max": 100},
    "y": {"min": -5, "max": 50}
  },
  "num_points": 30
}
```

### Confidence Zones
- **High (≥0.7)**: Use data confidently
- **Medium (0.4-0.7)**: Check overlay, may need calibration
- **Low (<0.4)**: Requires calibration

## Troubleshooting

### "Tesseract not found"
```bash
# macOS
brew install tesseract

# Ubuntu
sudo apt-get install tesseract-ocr

# Verify
tesseract --version
```

### "Low confidence: 0.35"
→ Use `--calibrate` for manual input

### "MULTI_SERIES_DETECTED"
→ Not supported in MVP. Extract one series manually or wait for Iteration 2.

### "POSSIBLE_LOG_SCALE"
→ Try: `chart2csv plot.png --calibrate --y-scale log`

## Next Steps

1. Read [README.md](README.md) for full documentation
2. Check [MVP_ROADMAP.md](docs/MVP_ROADMAP.md) for development status
3. Browse [examples/](examples/) for code integration
4. Run benchmark: `python scripts/benchmark.py`

## Get Help

- Issues: https://github.com/yourusername/chart2csv/issues
- Discussions: https://github.com/yourusername/chart2csv/discussions
- Email: your.email@example.com

---

**Remember: Chart2CSV is honest. If confidence is low, we'll tell you. Use calibration fallback for best results.**
