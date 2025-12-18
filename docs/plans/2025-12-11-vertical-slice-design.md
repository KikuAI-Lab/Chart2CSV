# Vertical Slice Implementation Plan

**Date:** 2025-12-11
**Goal:** Working end-to-end prototype in 1-2 days
**Approach:** Hardcoded simplicity → Iterate to sophistication

---

## Phase 1: Minimal Working Prototype (Day 1)

### What We're Building

A command-line tool that:
1. Takes a scatter plot PNG as input
2. Uses **hardcoded** crop box and axes positions
3. Uses **manual calibration** (user provides 2 points per axis)
4. Extracts scatter points via simple blob detection
5. Outputs CSV file

**Example usage:**
```bash
# User provides calibration
python -m chart2csv.cli.minimal plot.png \
  --calibrate \
  --crop 50,50,750,550 \
  --x-axis y=550 \
  --y-axis x=50

# Interactive prompts:
# X-axis left tick pixel: 100
# X-axis left tick value: 0
# X-axis right tick pixel: 700
# X-axis right tick value: 100
# Y-axis bottom tick pixel: 500
# Y-axis bottom tick value: 0
# Y-axis top tick pixel: 100
# Y-axis top tick value: 50

# Output: plot.csv
```

### Components to Build

#### 1. Test Data Generator (`scripts/generate_test_plots.py`)
**Time: 1-2 hours**

Generates 3 synthetic scatter plots with known parameters:
- `test_scatter_simple.png` - 20 points, clean
- `test_scatter_dense.png` - 50 points, more clustered
- `test_scatter_sparse.png` - 10 points, wide spread

Saves metadata JSON with:
- True data points
- Crop box
- Axes positions
- Calibration points

#### 2. Minimal CLI (`chart2csv/cli/minimal.py`)
**Time: 2-3 hours**

Simple argparse-based CLI:
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Input PNG")
    parser.add_argument("--calibrate", action="store_true")
    parser.add_argument("--crop", help="x1,y1,x2,y2")
    parser.add_argument("--x-axis", help="y=PX")
    parser.add_argument("--y-axis", help="x=PX")
    parser.add_argument("--output", default=None)

    args = parser.parse_args()

    # Load image
    # Get calibration from user
    # Extract points
    # Save CSV
```

#### 3. Calibration Input (`chart2csv/core/calibration.py`)
**Time: 1 hour**

```python
def get_calibration_from_user():
    """Prompt user for calibration points."""
    print("X-axis calibration:")
    x1_px = int(input("  Left tick pixel X: "))
    x1_val = float(input("  Left tick value: "))
    x2_px = int(input("  Right tick pixel X: "))
    x2_val = float(input("  Right tick value: "))

    print("Y-axis calibration:")
    y1_px = int(input("  Bottom tick pixel Y: "))
    y1_val = float(input("  Bottom tick value: "))
    y2_px = int(input("  Top tick pixel Y: "))
    y2_val = float(input("  Top tick value: "))

    return {
        "x": [(x1_px, x1_val), (x2_px, x2_val)],
        "y": [(y1_px, y1_val), (y2_px, y2_val)]
    }
```

#### 4. Simple Transform (use existing `transform.py`)
**Time: 30 min - already implemented**

Use `_build_from_calibration()` - already in skeleton!

#### 5. Scatter Extraction (`chart2csv/core/extraction.py`)
**Time: 2-3 hours**

Simple blob detection:
```python
def extract_scatter_points(image, crop_box):
    """Simple blob detection for scatter plots."""
    x1, y1, x2, y2 = crop_box
    cropped = image[y1:y2, x1:x2]

    # Binary threshold
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Find blobs
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 10
    params.maxArea = 500

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(binary)

    # Extract centroids (in cropped coordinates)
    points = [(kp.pt[0], kp.pt[1]) for kp in keypoints]

    # Convert to original image coordinates
    points = [(x + x1, y + y1) for x, y in points]

    return np.array(points)
```

#### 6. CSV Export (use existing `export.py`)
**Time: 30 min - already implemented**

Use `export_csv()` - already in skeleton!

---

## Phase 1 File Structure

```
chart2csv/
  cli/
    __init__.py
    minimal.py          # NEW - simple CLI
  core/
    calibration.py      # NEW - user input
    extraction.py       # NEW - blob detection
    (rest already exists)

scripts/
  generate_test_plots.py  # NEW - synthetic data

tests/
  test_minimal.py      # NEW - basic tests

fixtures/
  synthetic/
    test_scatter_simple.png
    test_scatter_simple.json
    test_scatter_dense.png
    test_scatter_dense.json
    test_scatter_sparse.png
    test_scatter_sparse.json
```

---

## Phase 1 Success Criteria

✅ Can run: `python -m chart2csv.cli.minimal test.png --calibrate`
✅ Prompts for 4 calibration points
✅ Outputs CSV with extracted points
✅ Works on 3 synthetic test images
✅ Point extraction accuracy: visual inspection (no metrics yet)

---

## Phase 2: Add Real Images + Basic Auto-Detection (Day 2)

### What We Add

1. **3 Real Chart Images**
   - Download from arXiv/Wikipedia
   - Store in `fixtures/real/`

2. **Simple Auto-Crop**
   - Edge detection → largest rectangle
   - Fallback to `--crop` if confidence low

3. **Simple Axis Detection**
   - Hough lines → find 2 perpendicular lines
   - Fallback to `--x-axis`/`--y-axis` if fails

4. **Confidence Scoring (basic)**
   - Just crop_confidence and axis_confidence
   - Print warning if low

### Phase 2 Components

#### 1. Real Image Collector (`scripts/collect_real_images.py`)
**Time: 1-2 hours**

Downloads and saves:
- 1 scatter from arXiv
- 1 line plot from Wikipedia
- 1 bar chart from public dataset

#### 2. Auto-Crop (`core/preprocess.py` - fill skeleton)
**Time: 2-3 hours**

```python
def detect_plot_area(image):
    # Edge detection
    edges = cv2.Canny(image, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Largest rectangle
    if contours:
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        confidence = 0.8  # Simple heuristic
        return (x, y, x+w, y+h), confidence

    # Fallback: full image
    h, w = image.shape[:2]
    return (0, 0, w, h), 0.3
```

#### 3. Auto-Axis Detection (`core/detection.py` - fill skeleton)
**Time: 3-4 hours**

```python
def detect_axes(image):
    # Hough line transform
    edges = cv2.Canny(image, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)

    # Find vertical and horizontal lines
    vertical = []
    horizontal = []

    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.arctan2(y2-y1, x2-x1) * 180 / np.pi

        if abs(angle) < 10:  # Horizontal
            horizontal.append((y1+y2)//2)
        elif abs(abs(angle) - 90) < 10:  # Vertical
            vertical.append((x1+x2)//2)

    if horizontal and vertical:
        x_axis_y = max(horizontal)  # Bottom
        y_axis_x = min(vertical)    # Left
        return {"x": x_axis_y, "y": y_axis_x}, 0.8

    return None, 0.2
```

---

## Phase 2 Success Criteria

✅ Auto-crop works on 2/3 real images
✅ Auto-axis works on 2/3 real images
✅ Falls back to manual when confidence low
✅ Can extract points from at least 1 real chart

---

## Phase 3: OCR Attempt (Day 2 evening / Day 3)

Only if Phase 1-2 work smoothly.

Add simple OCR:
- Crop tick regions along axes
- Run Tesseract
- Parse numbers
- Fall back to calibration if <50% success

---

## Implementation Order

**Day 1 Morning (4 hours):**
1. ✅ Create `scripts/generate_test_plots.py`
2. ✅ Generate 3 synthetic images
3. ✅ Create `chart2csv/core/calibration.py`
4. ✅ Create `chart2csv/core/extraction.py` (scatter only)

**Day 1 Afternoon (4 hours):**
5. ✅ Create `chart2csv/cli/minimal.py`
6. ✅ Wire everything together
7. ✅ Test on synthetic images
8. ✅ Fix bugs, iterate

**Day 2 Morning (4 hours):**
9. ✅ Download 3 real images
10. ✅ Implement auto-crop in `preprocess.py`
11. ✅ Implement auto-axis in `detection.py`
12. ✅ Test on real images

**Day 2 Afternoon (4 hours):**
13. ✅ Add confidence warnings
14. ✅ Polish CLI output
15. ✅ Write basic tests
16. ✅ (Optional) Start OCR if time permits

---

## Key Principles

1. **Hardcode first, generalize later**
   - Start with scatter only
   - Add line/bar in Phase 2/3

2. **Manual fallback always available**
   - Every auto feature has `--flag` override

3. **Visual verification**
   - Can we eyeball that it works?
   - Metrics come later

4. **Fail fast on real images**
   - If real images break everything, adjust approach

---

## Next Steps

1. Set up dev environment
2. Create test data generator
3. Build minimal CLI
4. Test, iterate, improve

---

**Status:** Ready to implement
**Estimated time:** 1-2 days
**Risk:** Low - everything is simple and testable
