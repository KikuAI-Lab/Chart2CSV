# Benchmark Plan for Chart2CSV

## Purpose

The benchmark serves as:
1. **Quality metric** - Measurable success rate on realistic fixtures
2. **Regression detection** - Catch quality degradation
3. **User trust** - Transparent about what works and what doesn't
4. **Development guide** - Focus effort on highest-impact improvements

## Target: 30-50 Fixtures

### Why 30-50?
- **Minimum 30** - Statistical significance for metrics
- **Maximum 50** - Manageable for manual verification
- **Balance** - Covers main use cases without overwhelming effort

## Fixture Categories

### Category 1: Clean Scatter Plots (8-10 fixtures)
**Characteristics:**
- Clear axes with readable tick labels
- 10-50 data points
- Good resolution (≥800px)
- No grid or light grid
- High contrast

**Expected success rate:** 80-90% without calibration

**Examples:**
- Scientific paper scatter (biology, chemistry)
- Economics correlation plots
- Simple XY data

### Category 2: Clean Line Plots (8-10 fixtures)
**Characteristics:**
- Single line
- Clear axes
- Good resolution
- Line width 1-3px
- No overlapping elements

**Expected success rate:** 70-80% without calibration

**Examples:**
- Time series (stock prices, temperature)
- Function plots (y = f(x))
- Trend lines

### Category 3: Clean Bar Charts (8-10 fixtures)
**Characteristics:**
- Vertical or horizontal bars
- Clear separation between bars
- Readable axis labels
- 5-20 bars

**Expected success rate:** 75-85% without calibration

**Examples:**
- Category comparisons
- Histogram-style data
- Simple bar charts from presentations

### Category 4: Hard Cases (6-10 fixtures)
**Characteristics:**
- Low resolution (<600px)
- Heavy grid
- Rotated tick labels
- Scientific notation
- Log scale (known ground truth)
- Scanned from old papers (1980s-90s)
- Screenshot with compression artifacts

**Expected success rate:** 20-40% without calibration, 60-80% with calibration

**Purpose:** Test fallback modes and warning system

## Metrics to Track

### Primary Metrics
1. **success_without_calibration** - Percentage with confidence ≥0.7
2. **requires_calibration** - Percentage with 0.4 ≤ confidence < 0.7
3. **failure** - Percentage with confidence < 0.4 even with calibration
4. **median_runtime_ms** - Performance metric
5. **ocr_tick_success_rate** - OCR quality metric

### Secondary Metrics (Iteration 2+)
6. **median_pixel_error** - Accuracy vs ground truth (requires manual annotation)
7. **median_value_error** - Value accuracy (requires manual annotation)

## Fixture Collection Strategy

### Phase 1: Initial 30 Fixtures (Week 1)
**Sources:**
1. **Academic papers** - arXiv, PubMed (scatter, line)
2. **Business reports** - Annual reports, presentations (bar)
3. **Wikipedia** - Charts from articles (mixed)
4. **Synthetic** - Generate with matplotlib (known ground truth)

**Distribution:**
- 8 clean scatter
- 8 clean line
- 8 clean bar
- 6 hard cases

### Phase 2: Expand to 50 (Iteration 1)
**Additional sources:**
1. Real user submissions (if available)
2. Competition datasets (e.g., Kaggle chart extraction)
3. Historical papers (1970s-90s scans)

**Distribution:**
- 10 scatter (2 more hard)
- 10 line (2 more hard)
- 10 bar (2 more hard)
- 10 hard cases
- 10 mixed/edge cases

## Ground Truth Annotation

### MVP (Manual Annotation)
For each fixture:
1. **Image file** - `fixtures/{category}/{id}.png`
2. **Metadata JSON** - `fixtures/{category}/{id}.json`
   ```json
   {
     "id": "scatter_clean_01",
     "category": "scatter_clean",
     "chart_type": "scatter",
     "source": "arXiv:1234.5678 Fig 2",
     "resolution": "1024x768",
     "has_grid": false,
     "difficulty": "easy",
     "notes": "Clear axes, good contrast"
   }
   ```
3. **Ground truth CSV** (optional for MVP) - `fixtures/{category}/{id}_gt.csv`

### Iteration 2+ (Semi-Automatic)
- Use WebPlotDigitizer to extract ground truth
- Store as reference for accuracy metrics

## Benchmark Script

### Usage
```bash
# Run benchmark
python scripts/benchmark.py

# With ground truth comparison (when available)
python scripts/benchmark.py --with-ground-truth

# Specific category
python scripts/benchmark.py --category scatter_clean

# Output detailed report
python scripts/benchmark.py --output bench_report.json
```

### Output Format

**JSON Report:**
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "0.1.0",
  "total_fixtures": 30,
  "summary": {
    "success_without_calibration": 0.67,
    "requires_calibration": 0.23,
    "failure": 0.10,
    "median_runtime_ms": 1450,
    "ocr_tick_success_rate": 0.72
  },
  "by_category": {
    "scatter_clean": {
      "count": 8,
      "success_rate": 0.875,
      "median_runtime_ms": 1200
    },
    "line_clean": {
      "count": 8,
      "success_rate": 0.75,
      "median_runtime_ms": 1500
    },
    "bar_clean": {
      "count": 8,
      "success_rate": 0.80,
      "median_runtime_ms": 1300
    },
    "hard_cases": {
      "count": 6,
      "success_rate": 0.33,
      "median_runtime_ms": 1800
    }
  },
  "failures": [
    {
      "id": "hard_case_02",
      "confidence": 0.28,
      "warnings": ["OCR_FAILED", "LOW_RESOLUTION"],
      "note": "Scanned from 1985 paper, very low res"
    }
  ]
}
```

**Console Output:**
```
========================================
Chart2CSV Benchmark Report
========================================
Version: 0.1.0
Fixtures: 30
Date: 2025-01-15 10:30:00

SUMMARY
-------
✓ Success (no calibration):  20/30 (67%)
⚠ Requires calibration:       7/30 (23%)
✗ Failure:                    3/30 (10%)

Runtime: 1450ms (median)
OCR Success: 72%

BY CATEGORY
-----------
Scatter (clean):  7/8  (88%) ✓✓
Line (clean):     6/8  (75%) ✓
Bar (clean):      6/8  (80%) ✓
Hard cases:       2/6  (33%) ⚠

FAILURES
--------
1. hard_case_02: Low res scan (1985)
   Confidence: 0.28
   Warnings: OCR_FAILED, LOW_RESOLUTION

...
```

## Fixture Naming Convention

```
fixtures/
  scatter_clean/
    scatter_clean_01.png
    scatter_clean_01.json
    scatter_clean_01_gt.csv  (optional)
  line_clean/
    line_clean_01.png
    ...
  bar_clean/
    bar_clean_01.png
    ...
  hard_cases/
    hard_logscale_01.png
    hard_lowres_01.png
    hard_grid_01.png
    hard_scanned_01.png
    ...
```

## Minimizing Manual Annotation Effort

### MVP Approach
1. **No ground truth needed** - Just images and metadata
2. **Quality measured by confidence** - Not by accuracy vs GT
3. **Visual verification** - Use overlay to spot-check

### When to Add Ground Truth
**Iteration 2+** when:
- Want to measure pixel/value accuracy
- Want to compare extraction algorithms
- Have user-reported issues

### Semi-Automated GT Collection
1. Use WebPlotDigitizer on clean fixtures
2. Export CSV as ground truth
3. Store in `_gt.csv` files
4. Compare programmatically

## Success Criteria (MVP)

### Minimum Acceptable Quality
- ✓ Success without calibration: ≥40% overall
- ✓ Clean fixtures success: ≥70%
- ✓ Hard cases: ≥20% (mostly for warning system validation)
- ✓ Median runtime: <2 seconds
- ✓ No silent failures (always warn when uncertain)

### Stretch Goals
- ⭐ Success without calibration: ≥60%
- ⭐ Clean fixtures: ≥80%
- ⭐ Median runtime: <1.5 seconds

## Continuous Benchmarking

### On Every Commit (CI/CD)
```bash
# Quick benchmark (10 representative fixtures)
python scripts/benchmark.py --quick

# Fail if success rate drops >10%
python scripts/benchmark.py --quick --fail-on-regression
```

### Weekly Full Benchmark
- Run on all fixtures
- Track metrics over time
- Detect gradual degradation

## Fixture Contribution Guidelines

When adding new fixtures:
1. **Representative** - Real-world use case
2. **Diverse** - Different styles, sources, difficulties
3. **Documented** - Clear metadata JSON
4. **Legal** - Public domain, CC0, or permissive license
5. **Quality** - Original resolution if possible

## Example Fixture Sources

### Public Domain
- Government reports (USA.gov, Data.gov)
- Historical scientific papers (pre-1923)
- Wikipedia (CC BY-SA)
- NASA data visualizations

### Permissive
- arXiv papers (with attribution)
- Open access journals
- Creative Commons datasets

### Synthetic
- matplotlib-generated (known perfect ground truth)
- Controlled variations (grid, noise, rotation)

## Benchmark Evolution

### MVP (Week 1-2)
- 30 fixtures
- 4 categories
- Basic metrics (success rate, runtime, OCR)

### Iteration 1 (Week 3-4)
- 50 fixtures
- Add ground truth for clean fixtures
- Median pixel/value error metrics

### Iteration 2 (Month 2)
- 100+ fixtures
- User-submitted hard cases
- Category: multi-series (when supported)
- Accuracy benchmarks vs competitors

---

**Remember: The benchmark is not about achieving 100% success. It's about honest measurement and continuous improvement.**
