# Chart2CSV - Project Status Report

**Date:** December 11, 2025
**Status:** ✅ MVP Structure Ready for Development
**Location:** `/Users/nick/myprojects/Chart2CSV`

---

## ✅ Completed

### 1. Project Structure
```
Chart2CSV/
├── README.md                    ✅ Comprehensive documentation
├── PROJECT_SUMMARY.md          ✅ High-level overview
├── QUICKSTART.md               ✅ 5-minute setup guide
├── LICENSE                     ✅ MIT License
├── .gitignore                  ✅ Python + project-specific
├── requirements.txt            ✅ All dependencies listed
├── setup.py                    ✅ Package configuration
│
├── chart2csv/
│   ├── __init__.py             ✅ Package entry point
│   ├── core/                   ✅ Core CV/OCR modules
│   │   ├── __init__.py
│   │   ├── types.py            ✅ Data structures (ChartResult, Confidence, etc.)
│   │   ├── pipeline.py         ✅ Main extraction pipeline skeleton
│   │   ├── preprocess.py       ✅ Image preprocessing skeleton
│   │   ├── detection.py        ✅ Axis/tick detection skeleton
│   │   ├── ocr.py              ✅ Tesseract OCR wrapper skeleton
│   │   ├── transform.py        ✅ Pixel→value transformation skeleton
│   │   └── export.py           ✅ CSV/JSON/overlay export skeleton
│   │
│   ├── cli/                    ⏳ Ready for implementation
│   ├── api/                    ⏳ Reserved for Iteration 2
│   └── tests/                  ⏳ Ready for tests
│
├── docs/
│   ├── MVP_ROADMAP.md          ✅ Day-by-day 7-10 day plan
│   └── BENCHMARK_PLAN.md       ✅ Testing & fixtures strategy
│
├── fixtures/                   ⏳ Ready for benchmark images
├── scripts/                    ⏳ Ready for benchmark runner
└── examples/                   ⏳ Ready for code examples
```

---

## 📚 Documentation Created

### User-Facing Documentation

1. **[README.md](README.md)** - 400+ lines
   - Problem statement
   - Quick start examples
   - Full feature list
   - CLI usage examples
   - Confidence system explanation
   - Warning codes reference
   - Architecture overview
   - Roadmap
   - Installation instructions

2. **[QUICKSTART.md](QUICKSTART.md)** - Quick reference
   - 5-minute setup
   - Common workflows
   - Troubleshooting
   - Output format examples

3. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Executive overview
   - Value proposition
   - Architecture decisions
   - Tech stack
   - Success metrics
   - Risk assessment
   - Monetization strategy

### Developer Documentation

4. **[MVP_ROADMAP.md](docs/MVP_ROADMAP.md)** - 600+ lines
   - Day-by-day implementation plan (Days 1-10)
   - Module-by-module breakdown
   - Risk areas identified
   - Mitigation strategies
   - Code structure after MVP
   - Dependencies with licenses
   - Success criteria
   - Checklist before release

5. **[BENCHMARK_PLAN.md](docs/BENCHMARK_PLAN.md)** - 400+ lines
   - 30-50 fixture strategy
   - 4 fixture categories
   - Metrics to track
   - Collection strategy
   - Ground truth annotation
   - Benchmark script design
   - Success criteria

---

## 🏗️ Code Structure Created

### Core Modules (Skeletons Ready)

All modules have:
- ✅ Proper imports
- ✅ Type hints
- ✅ Docstrings
- ✅ Function signatures
- ✅ TODO markers for implementation
- ✅ Error handling patterns

#### 1. `types.py` - Complete
- `ChartType` enum
- `Scale` enum (linear/log)
- `WarningCode` enum (12 codes)
- `Warning` dataclass
- `AxisInfo` dataclass
- `Confidence` dataclass with formula
- `ChartResult` dataclass with `to_dict()`
- `CropBox`, `AxisLine`, `Tick` dataclasses

#### 2. `pipeline.py` - Main Flow
```python
extract_chart(
    image_path,
    crop=None,
    x_axis_pos=None,
    y_axis_pos=None,
    x_scale=Scale.LINEAR,
    y_scale=Scale.LINEAR,
    chart_type=None,
    calibration_points=None,
    generate_overlay_image=True
) -> ChartResult
```

Flow:
1. Load image
2. Preprocess
3. Detect plot area (or use manual crop)
4. Detect axes (or use manual)
5. OCR tick labels (or use calibration)
6. Build pixel→value transform
7. Extract data by chart type
8. Generate overlay
9. Calculate confidence
10. Return ChartResult

#### 3. `preprocess.py`
- `preprocess_image()` - Resize, grayscale, CLAHE, denoise
- `detect_plot_area()` - Crop detection
- `remove_grid()` - Grid removal (optional)

#### 4. `detection.py`
- `detect_axes()` - Hough lines + perpendicularity check
- `detect_ticks()` - Tick mark positions

#### 5. `ocr.py`
- `extract_tick_labels()` - Tesseract OCR
- `parse_number()` - Regex for floats, scientific notation
- `preprocess_for_ocr()` - Binarization

#### 6. `transform.py`
- `build_transform()` - From ticks or calibration
- `_build_from_ticks()` - Linear regression
- `_build_from_calibration()` - Manual 2-point transform
- `apply_transform()` - Pixel coords → values

#### 7. `export.py`
- `export_csv()` - Write CSV
- `export_json()` - Write metadata JSON
- `generate_overlay()` - Draw on image
- `save_overlay()` - Save overlay image

---

## 📦 Dependencies Specified

### Core
- `opencv-python>=4.8.0` - Apache 2.0
- `pytesseract>=0.3.10` - Apache 2.0
- `Pillow>=10.0.0` - HPND
- `numpy>=1.24.0` - BSD-3
- `scipy>=1.11.0` - BSD-3
- `scikit-image>=0.21.0` - BSD-3

### Optional
- `pypdfium2>=4.0.0` - Apache 2.0 / BSD-3 (PDF support)
- `click>=8.1.0` - BSD-3 (CLI framework)

### Dev
- `pytest>=7.4.0`
- `black>=23.0.0`
- `mypy>=1.5.0`
- `ruff>=0.0.280`

All licenses checked: ✅ No GPL/AGPL, safe for MIT project

---

## 🎯 Key Design Decisions Documented

### 1. CLI-First Architecture ✅
**Decision:** Build offline-first CLI, API as thin wrapper later

**Rationale:**
- Focus on CV/OCR quality (highest risk)
- Privacy by default
- No deployment overhead
- Fast iteration cycle
- Monetizable without SaaS

**Implementation Ready:** Core library structure allows API wrapper in 1-3 days

### 2. Confidence & Warning System ✅
**Decision:** Honest quality reporting over silent failures

**Formula:**
```
confidence = (
    0.3 × crop_confidence +
    0.25 × axis_confidence +
    0.3 × ocr_confidence +
    0.15 × extraction_confidence
)
```

**Zones:**
- High (≥0.7): Use data
- Medium (0.4-0.7): Check overlay
- Low (<0.4): Requires calibration

**12 Warning Codes:** All mapped to user actions

### 3. Best-Effort Auto + Manual Fallback ✅
**Decision:** Don't promise perfect auto-detection

**Implementation:**
- Every auto step has manual override flag
- Calibration via numeric input (not click UI in MVP)
- Overlay always generated for verification

**Overrides:**
- `--crop x1,y1,x2,y2`
- `--x-axis y=PX` / `--y-axis x=PX`
- `--chart-type scatter|line|bar`
- `--x-scale log|linear` / `--y-scale log|linear`
- `--calibrate` (interactive numeric input)

### 4. MVP Scope (12 Features) ✅
**Supported:**
- 3 chart types (scatter, line single, bar)
- Linear scale only
- PNG/JPG only (PDF via pypdfium2 in roadmap)
- Sequential batch (parallel in roadmap)

**Not Supported:**
- Multi-series
- Legend parsing
- Dual-axis
- Auto log-scale detection
- Click-based calibration
- API/Web UI/Telegram

### 5. Benchmark-Driven Development ✅
**Decision:** 30-50 fixtures, measure quality honestly

**Metrics:**
- success_without_calibration
- requires_calibration
- median_runtime_ms
- ocr_tick_success_rate

**Target:**
- Success: ≥40% (stretch: ≥60%)
- Clean fixtures: ≥70% (stretch: ≥80%)
- Runtime: <2 seconds

---

## 📋 Next Steps for Development

### Immediate (Week 1)
1. ✅ Project structure created
2. ⏳ Set up dev environment
   ```bash
   cd /Users/nick/myprojects/Chart2CSV
   python3 -m venv venv
   source venv/bin/activate
   pip install -e ".[dev]"
   brew install tesseract
   ```

3. ⏳ Collect 10 initial fixtures
   - 3 scatter (clean)
   - 3 line (clean)
   - 3 bar (clean)
   - 1 hard case

4. ⏳ Implement Day 1-2: Preprocess + crop detection
   - Fill in `preprocess.py`
   - Test on 10 fixtures
   - Verify resize/CLAHE/denoise works

5. ⏳ Implement Day 3: Axis detection
   - Hough lines method
   - Perpendicularity check
   - Manual override flags

6. ⏳ Implement Day 4-5: OCR (RISKY)
   - Tesseract integration
   - Number parsing (regex)
   - Scientific notation handling
   - Success rate tracking

7. ⏳ Implement Day 6: Transform + calibration
   - Linear fit
   - Calibration mode (numeric input)
   - Log scale transform

8. ⏳ Implement Day 7: Data extraction
   - Scatter: blob detection
   - Bar: contour detection
   - Line: skeletonization

9. ⏳ Implement Day 8-10: Export + Polish
   - CSV/JSON export
   - Overlay drawing
   - Confidence calculation
   - Warning integration
   - Batch mode
   - Benchmark script

### Week 2
10. ⏳ Collect remaining 20-40 fixtures
11. ⏳ Run full benchmark
12. ⏳ Write tests
13. ⏳ Polish documentation
14. ⏳ Prepare for release

---

## 🔑 Key Files to Reference

### For Implementation
- **Start here:** [MVP_ROADMAP.md](docs/MVP_ROADMAP.md) - Day-by-day guide
- **Architecture:** Check module skeletons in `chart2csv/core/`
- **Types:** [types.py](chart2csv/core/types.py) - All data structures

### For Testing
- **Benchmark plan:** [BENCHMARK_PLAN.md](docs/BENCHMARK_PLAN.md)
- **Fixtures:** `fixtures/` directory structure defined

### For Users (Post-MVP)
- **Quick start:** [QUICKSTART.md](QUICKSTART.md)
- **Full docs:** [README.md](README.md)
- **Overview:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## ⚠️ Important Reminders

### During Implementation

1. **OCR is the riskiest part** - Expect 40-60% failure rate
   - Always provide calibration fallback
   - Track success rate
   - Generate warnings

2. **Don't over-engineer** - Stick to MVP scope
   - No multi-series in MVP
   - No auto log-scale in MVP
   - No click UI in MVP

3. **Test early, test often** - Use real fixtures from Day 1
   - Don't wait till Day 10 to test extraction
   - Visual verification via overlay

4. **Trust the fallback** - Calibration is a feature
   - 15-30 seconds of manual input is acceptable
   - Better than wrong data

5. **Be honest with confidence** - Never silently fail
   - Warning codes are your friend
   - Confidence formula is transparent

### Code Quality

- ✅ Type hints everywhere
- ✅ Docstrings for all public functions
- ✅ Unit tests (pytest)
- ✅ Format with black
- ✅ Lint with ruff
- ✅ Type check with mypy

---

## 📊 Project Metrics

| Metric | Value |
|--------|-------|
| **Documentation** | ~2,500 lines |
| **Code skeletons** | ~1,000 lines |
| **Total files created** | 17 files |
| **Estimated MVP time** | 7-10 days |
| **Target benchmark fixtures** | 30-50 images |
| **Supported chart types** | 3 (scatter, line, bar) |
| **Warning codes** | 12 |
| **Dependencies** | 6 core + 3 optional |

---

## 🎉 Status: Ready to Start Development

All planning, architecture, and scaffolding complete.

**Recommended first command:**
```bash
cd /Users/nick/myprojects/Chart2CSV
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pytest  # Should pass (no tests yet)
```

Then start with Day 1 from [MVP_ROADMAP.md](docs/MVP_ROADMAP.md).

---

**Project prepared by:** Claude Code
**Date:** December 11, 2025
**Next:** Begin implementation following MVP roadmap
