# Chart2CSV - MVP Roadmap (7-10 Days)

## Executive Summary

**Goal:** Build offline-first CLI tool that extracts data from chart images with honest confidence scoring and calibration fallback.

**Timeline:** 7-10 days solo development
**Risk mitigation:** Best-effort auto + manual overrides + calibration fallback
**Success metric:** 30-50 fixture benchmark with measurable quality

## Day-by-Day Plan

### Day 1-2: Preprocess + Plot Area Detection

**Objectives:**
- Image normalization pipeline
- Plot area cropping (best-effort)
- Manual override support

**Tasks:**
1. **Image preprocessing** (4-6 hours)
   - Resize to max 1200px (long side)
   - Grayscale conversion
   - Contrast enhancement (CLAHE)
   - Denoise (bilateral filter or fastNlMeans)

2. **Plot area detection** (6-8 hours)
   - Attempt 1: Find rectangle with max contrast/lines (Hough lines + bounding box)
   - Attempt 2: Edge detection + largest rectangle
   - Confidence scoring for crop quality
   - Fallback: Use full image if crop uncertain

3. **Manual override** (2-3 hours)
   - Implement `--crop x1,y1,x2,y2` flag
   - Validate crop coordinates
   - Set crop_confidence=1.0 for manual

**Deliverables:**
- `chart2csv/core/preprocess.py`
- `chart2csv/core/detection.py` (crop part)
- Tests with 5-10 sample images

**Risk areas:**
- Complex layouts (subplots, annotations, logos)
- White background without clear boundaries
- **Mitigation:** Warning "CROP_UNCERTAIN" + fallback to full image

---

### Day 3: Axis Detection

**Objectives:**
- Find X and Y axes
- Determine origin point
- Manual override support

**Tasks:**
1. **Axis line detection** (4-5 hours)
   - Find two dominant perpendicular lines (Hough lines)
   - Determine origin (intersection or bottom-left corner)
   - Validate perpendicularity (80-100°)

2. **Fallback detection** (2-3 hours)
   - Projection-based method (sum of dark pixels along X/Y)
   - Find densest vertical/horizontal structures near edges

3. **Manual override** (2-3 hours)
   - Implement `--x-axis y=PX` and `--y-axis x=PX`
   - Validate axis positions
   - Set axis_confidence=1.0 for manual

**Deliverables:**
- `chart2csv/core/detection.py` (axis part)
- Axis detection tests
- Perpendicularity validation

**Risk areas:**
- Graphs without explicit axes (grid only)
- Thick axes or double lines
- Skewed images
- **Mitigation:** Warning "AXES_UNCERTAIN", "SKEW_DETECTED" + manual overrides

---

### Day 4-5: OCR Tick Labels (MOST RISKY)

**Objectives:**
- Extract tick labels from axes
- Parse numeric values
- Build pixel→value mapping

**Tasks:**
1. **Tick region extraction** (3-4 hours)
   - Crop regions along axes (±20px margin)
   - Preprocess for OCR: binarization, invert if needed
   - Detect tick positions (edge detection or template matching)

2. **OCR with Tesseract** (4-6 hours)
   - Config for numbers: `--psm 6 -c tessedit_char_whitelist=0123456789.,-+eE`
   - Parse tick values (float conversion)
   - Handle scientific notation: `[-+]?\d*\.?\d+([eE][-+]?\d+)?`
   - Handle negative numbers (dash vs minus)

3. **OCR confidence scoring** (2-3 hours)
   - Track % of successfully parsed ticks
   - ≥80% → confidence 1.0
   - 60-80% → 0.7
   - 40-60% → 0.5 + warning "OCR_PARTIAL"
   - <40% → 0.2 + warning "OCR_FAILED"

4. **Linear fit validation** (2-3 hours)
   - Build linear mapping: `value = a × pixel + b`
   - Compute residuals between expected and actual tick positions
   - If residuals >10% → warning "POSSIBLE_LOG_SCALE"

**Deliverables:**
- `chart2csv/core/ocr.py`
- `chart2csv/core/transform.py` (pixel→value mapping)
- OCR tests with various fonts/resolutions

**Risk areas (CRITICAL):**
- Low resolution ticks
- Non-standard fonts
- Rotated tick labels
- Scientific notation
- Overlapping labels
- Negative numbers with dash vs minus
- **Mitigation:** Heavy use of warnings + calibration fallback

---

### Day 6: Pixel→Value Transform + Calibration

**Objectives:**
- Build robust coordinate transformation
- Implement calibration fallback
- Handle log scale via manual flag

**Tasks:**
1. **Transform validation** (2-3 hours)
   - Check tick spacing uniformity (linear scale)
   - Compute fit error (residuals)
   - Detect inverted axes (Y grows down)

2. **Calibration mode** (5-6 hours)
   - Implement `--calibrate` flag
   - Show image (matplotlib or system viewer)
   - Prompt for numeric inputs:
     ```
     Enter pixel X for left tick: 120
     Enter value for that tick: 0.0
     Enter pixel X for right tick: 680
     Enter value for that tick: 100.0
     (repeat for Y axis)
     ```
   - Build transform from 2 points per axis
   - Set confidence ≥0.8 for manual calibration

3. **Log scale support** (1-2 hours)
   - `--x-scale log|linear` and `--y-scale log|linear`
   - Only with `--calibrate` (no auto-detection)
   - Transform: `value = 10^(a × pixel + b)`

**Deliverables:**
- `chart2csv/cli/calibrate.py`
- Calibration tests
- Log scale transform

**Risk areas:**
- User entering wrong coordinates
- Broken scale (axis break)
- **Mitigation:** Show overlay with calibration points for verification

---

### Day 7: Data Extraction (3 Chart Types)

**Objectives:**
- Extract scatter, line, and bar data
- Return pixel coordinates → transform to values

**Tasks:**
1. **Scatter extraction** (2-3 hours)
   - Binary threshold + blob detection (`cv2.connectedComponentsWithStats`)
   - Filter by size (remove noise/grid points)
   - Centroids → pixel coords → transform to values
   - Confidence: check point count (5-500 reasonable)

2. **Bar extraction** (2-3 hours)
   - Detect vertical/horizontal (aspect ratio)
   - Contour detection → filter rectangles
   - Top edge (vertical) or right edge (horizontal)
   - Transform to values

3. **Line extraction** (3-4 hours)
   - Edge detection + morphology
   - Skeletonization (`cv2.ximgproc.thinning` or `skimage.morphology.skeletonize`)
   - Resample along X (fixed step)
   - For each X find Y pixel → transform to value
   - Handle gaps: median filter along Y if multiple candidates

**Deliverables:**
- `chart2csv/core/pipeline.py` (extraction part)
- Tests for each chart type
- Extraction confidence scoring

**Risk areas:**
- Line: thick lines, gaps, noise
- Scatter: too many points (noise)
- Bar: overlapping bars, 3D effects
- **Mitigation:** Warnings + overlay verification

---

### Day 8: Export + Overlay + Metadata

**Objectives:**
- Generate CSV output
- Create JSON metadata
- Draw overlay image

**Tasks:**
1. **CSV export** (1-2 hours)
   - Scatter/Line: columns `x,y`
   - Bar: columns `category,value` or `x,value`
   - Clean formatting (2-6 decimal places)

2. **JSON metadata** (2-3 hours)
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
     "ocr_success_rate": 0.85,
     "extraction_params": {
       "crop": "auto",
       "axes": "auto",
       "calibration": false
     }
   }
   ```

3. **Overlay generation** (2-3 hours)
   - Draw extracted data on original image
   - Scatter: red dots
   - Line: green line
   - Bar: blue rectangles
   - Include axes and tick marks if detected

**Deliverables:**
- `chart2csv/core/export.py`
- Overlay drawing function
- Export tests

---

### Day 9: Confidence System + Warning Architecture

**Objectives:**
- Implement full confidence scoring
- Add all warning types
- Integrate into pipeline

**Tasks:**
1. **Confidence calculation** (3-4 hours)
   ```python
   confidence = (
       0.3 * crop_confidence +
       0.25 * axis_confidence +
       0.3 * ocr_confidence +
       0.15 * extraction_confidence
   )
   ```
   - Implement each component
   - Define thresholds for each

2. **Warning system** (2-3 hours)
   - Define all warning codes
   - Add warning generation in each module
   - Collect warnings in pipeline result

3. **User-facing output** (1-2 hours)
   - Pretty-print confidence and warnings in CLI
   - Color coding (high=green, medium=yellow, low=red)
   - Recommendations for each warning

**Deliverables:**
- `chart2csv/core/types.py` (ChartResult, Confidence, Warnings)
- Confidence tests
- Warning integration

**Warning codes to implement:**
- `LOW_RESOLUTION`
- `CROP_UNCERTAIN`
- `AXES_UNCERTAIN`
- `SKEW_DETECTED`
- `OCR_FAILED`
- `OCR_PARTIAL`
- `POSSIBLE_LOG_SCALE`
- `MULTI_SERIES_DETECTED`
- `LEGEND_DETECTED`
- `NOISE_DETECTED`
- `LINE_GAPS`
- `FEW_POINTS`

---

### Day 10: Batch Mode + Benchmark + Polish

**Objectives:**
- Implement batch processing
- Create benchmark mode
- Final integration and testing

**Tasks:**
1. **Batch processing** (2-3 hours)
   - `chart2csv batch <pattern> --output-dir <dir>`
   - Sequential processing (parallel in roadmap)
   - Summary report (success/failed/low-confidence counts)
   - Individual CSV + metadata for each

2. **Benchmark mode** (3-4 hours)
   - `chart2csv benchmark <fixtures-dir> --output <report.json>`
   - Metrics:
     - `success_without_calibration` (confidence ≥0.7)
     - `requires_calibration` (confidence <0.7)
     - `median_runtime_ms`
     - `ocr_tick_success_rate`
   - JSON report output
   - (Median error vs GT → roadmap)

3. **CLI polish** (2-3 hours)
   - Help text and examples
   - Argument validation
   - Error messages
   - Progress bars for batch

4. **Documentation** (2 hours)
   - Usage examples
   - API documentation
   - Troubleshooting guide

**Deliverables:**
- `chart2csv/cli/batch.py`
- Benchmark script
- Complete CLI
- Documentation

---

## File Structure After MVP

```
Chart2CSV/
├── README.md                    # Main documentation
├── setup.py                     # Package setup
├── requirements.txt             # Dependencies
├── .gitignore
├── LICENSE                      # MIT
├── THIRD_PARTY.md              # Dependency licenses
│
├── chart2csv/
│   ├── __init__.py
│   │
│   ├── core/                   # Pure CV/OCR logic
│   │   ├── __init__.py
│   │   ├── pipeline.py         # Main: extract_chart()
│   │   ├── preprocess.py       # Image cleanup
│   │   ├── detection.py        # Axes, ticks, plot area
│   │   ├── ocr.py              # Tesseract wrapper
│   │   ├── transform.py        # Pixel→value mapping
│   │   ├── export.py           # CSV/JSON/overlay
│   │   └── types.py            # ChartResult, Confidence
│   │
│   ├── cli/                    # CLI interface
│   │   ├── __init__.py
│   │   ├── main.py             # argparse entry point
│   │   ├── calibrate.py        # Interactive calibration
│   │   └── batch.py            # Batch processing
│   │
│   ├── api/                    # (empty in MVP)
│   │   └── __init__.py
│   │
│   └── tests/                  # Unit tests
│       ├── __init__.py
│       ├── test_preprocess.py
│       ├── test_detection.py
│       ├── test_ocr.py
│       ├── test_transform.py
│       ├── test_export.py
│       └── test_pipeline.py
│
├── scripts/
│   ├── benchmark.py            # Benchmark runner
│   └── collect_fixtures.py     # Helper for fixtures
│
├── fixtures/                   # Benchmark dataset
│   ├── scatter/
│   ├── line/
│   ├── bar/
│   └── hard_cases/
│
├── docs/
│   ├── MVP_ROADMAP.md          # This file
│   ├── ARCHITECTURE.md         # Technical design
│   ├── CONFIDENCE.md           # Confidence system details
│   ├── TROUBLESHOOTING.md      # Common issues
│   └── API.md                  # Future API design
│
└── examples/
    ├── basic_usage.py
    ├── batch_processing.py
    └── calibration_example.py
```

---

## Dependencies

### Core (MVP)
```
opencv-python>=4.8.0        # Apache 2.0
pytesseract>=0.3.10         # Apache 2.0
Pillow>=10.0.0              # HPND
numpy>=1.24.0               # BSD-3
scipy>=1.11.0               # BSD-3
scikit-image>=0.21.0        # BSD-3
matplotlib>=3.7.0           # PSF (for calibration display)
```

### Optional (Pro features)
```
pypdfium2>=4.0.0            # Apache 2.0 / BSD-3
```

### Development
```
pytest>=7.4.0
black>=23.0.0
mypy>=1.5.0
ruff>=0.0.280
```

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **OCR fails on >50% of fixtures** | HIGH | HIGH | Warning system + calibration fallback |
| **Log-scale false negatives** | MEDIUM | HIGH | Warning "POSSIBLE_LOG_SCALE", require manual `--y-scale log` |
| **Line extraction poor quality** | MEDIUM | MEDIUM | Start with scatter/bar, iterate on line |
| **Thick lines cause double detection** | MEDIUM | LOW | Morphological thinning, median filter |
| **Grid interferes with extraction** | MEDIUM | MEDIUM | Optional `--remove-grid`, show overlay |
| **Low resolution inputs** | HIGH | MEDIUM | Warning "LOW_RESOLUTION", suggest higher res |
| **Skewed/rotated images** | MEDIUM | MEDIUM | Warning "ROTATION_DETECTED", no auto-correction in MVP |

### Product Risks

| Risk | Mitigation |
|------|------------|
| **Users expect perfect auto-detection** | Clear documentation: "best-effort + calibration fallback" |
| **Multi-series confusion** | Warning "MULTI_SERIES_DETECTED", chart_type=unknown |
| **Log scale silent failures** | Never auto-assume log, always warn if suspicious |
| **Installation friction (Tesseract)** | Clear install docs, consider self-contained binary (roadmap) |

### Legal Risks

| Risk | Mitigation |
|------|------------|
| **OCR model license unclear** | Use Tesseract (Apache 2.0), document in THIRD_PARTY.md |
| **PDF library AGPL** | Use pypdfium2 (Apache/BSD), NOT PyMuPDF (AGPL) |
| **GPL contamination** | Avoid GPL dependencies, use MIT/Apache/BSD only |

---

## Success Metrics (MVP)

### Functional Goals
- [ ] Processes PNG/JPG scatter/line/bar charts
- [ ] Generates CSV + JSON + overlay
- [ ] Manual overrides work (`--crop`, `--x-axis`, `--y-axis`)
- [ ] Calibration mode functional
- [ ] Batch processing works
- [ ] Benchmark mode runs

### Quality Goals (on 30-50 fixture dataset)
- [ ] Success without calibration: ≥40% (confidence ≥0.7)
- [ ] Requires calibration: 40-50%
- [ ] Total failures (even with calibration): ≤10%
- [ ] OCR tick success rate: ≥60% average
- [ ] Median runtime: <2 seconds per image
- [ ] No silent wrong data (always warn when uncertain)

### Developer Experience Goals
- [ ] `pip install chart2csv` works (with Tesseract pre-installed)
- [ ] `chart2csv --help` clear and comprehensive
- [ ] Error messages actionable
- [ ] Overlay always generated for verification
- [ ] Warnings map to specific fixes

---

## Post-MVP Priorities (Iteration 1)

### Week 2-3 (Iteration 1)
1. **Click-based calibration UI** (3-4 days)
   - Matplotlib event handling
   - Cross-platform support (Mac/Linux/Windows)
   - Coordinate capture and validation

2. **PDF multi-page support** (2-3 days)
   - `--pages 3,5-8,12` syntax
   - Batch PDF processing
   - Pro feature flag

3. **Improved OCR preprocessing** (2-3 days)
   - Multiple preprocessing variants
   - Vote best OCR result
   - Adaptive binarization

4. **Grid removal option** (1-2 days)
   - `--remove-grid` flag
   - Morphological operations
   - Before/after overlay

5. **Batch parallelization** (1-2 days)
   - `--jobs N` flag
   - Multiprocessing pool
   - Progress bar

### Week 4-5 (Iteration 2)
1. **Log-scale auto-detection** (experimental)
2. **Multi-series support** (beta)
3. **Legend parsing** (beta)
4. **API wrapper** (FastAPI, 1-3 days)
5. **Improved confidence** (ML-based features)

---

## Dev Environment Setup

```bash
# Clone repo
git clone https://github.com/yourusername/chart2csv.git
cd chart2csv

# Create venv
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dev dependencies
pip install -e ".[dev]"

# Install Tesseract (if not already)
brew install tesseract  # macOS
# or apt-get install tesseract-ocr  # Ubuntu

# Run tests
pytest

# Format code
black chart2csv/
ruff check chart2csv/

# Type check
mypy chart2csv/
```

---

## Notes for Developer Agent

When implementing this roadmap:

1. **Start with simplest case first:** Perfect images, clear axes, good resolution
2. **Add complexity gradually:** Then handle edge cases
3. **Test continuously:** Don't wait till day 10 to test extraction
4. **Commit atomic changes:** Each day's work should be a clean commit
5. **Write docstrings:** Every function should have clear docstring
6. **Use type hints:** Makes code self-documenting
7. **Don't over-engineer:** Resist temptation to add features not in MVP
8. **Trust the fallback:** Calibration is not a failure, it's a feature
9. **Overlay everything:** Visual verification is critical
10. **Be honest with confidence:** Better to warn than silently fail

---

## Final Checklist Before Release

- [ ] All MVP features implemented
- [ ] 30-50 fixtures collected and benchmarked
- [ ] README.md complete with examples
- [ ] THIRD_PARTY.md with all dependency licenses
- [ ] CLI help text comprehensive
- [ ] Error messages clear and actionable
- [ ] Tests passing
- [ ] Type checking passing
- [ ] Code formatted (black)
- [ ] No hardcoded paths
- [ ] Works on clean Python 3.8+ install
- [ ] Tesseract install documented
- [ ] Example outputs in docs/
- [ ] GitHub repo set up
- [ ] PyPI package prepared (for future)

---

**Remember: The goal is not perfection. The goal is honest, useful, and fast extraction with clear fallbacks.**
