import os
os.environ["MISTRAL_API_KEY"] = "ruQqe2KV9UTYebSxZVrGDf9tIzcEGpbS"

import sys
sys.path.insert(0, "/app")
import cv2
import numpy as np
from chart2csv.core.detection import detect_axes, detect_ticks
from chart2csv.core.ocr import extract_tick_labels
from chart2csv.core.transform import build_transform, apply_transform

# Create a simple test chart
h, w = 400, 600
img = np.ones((h, w), dtype=np.uint8) * 255

# Draw axes
cv2.line(img, (50, 350), (550, 350), 0, 2)
cv2.line(img, (50, 50), (50, 350), 0, 2)

# Draw X labels: 0,1,2,3,4,5
for i, val in enumerate([0, 1, 2, 3, 4, 5]):
    x = 50 + i * 100
    cv2.line(img, (x, 345), (x, 355), 0, 2)
    cv2.putText(img, str(val), (x-5, 375), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)

# Draw Y labels: 0,10,20,30,40,50
for i, val in enumerate([0, 10, 20, 30, 40, 50]):
    y = 350 - i * 60
    cv2.line(img, (45, y), (55, y), 0, 2)
    cv2.putText(img, str(val), (10, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)

axes, conf = detect_axes(img)
x_ax = axes["x"]
y_ax = axes["y"]
print(f"Axes: X at y={x_ax}, Y at x={y_ax}")

ticks, conf = detect_ticks(img, axes)
print(f"X ticks: {sorted(ticks['x'])}")
print(f"Y ticks: {sorted(ticks['y'])}")

ticks_data, ocr_conf = extract_tick_labels(img, axes, use_mistral=True, use_cache=False)
x_ocr = [(t["pixel"], t["value"]) for t in ticks_data["x"]]
y_ocr = [(t["pixel"], t["value"]) for t in ticks_data["y"]]
print(f"OCR X: {x_ocr}")
print(f"OCR Y: {y_ocr}")

if ticks_data["x"] and ticks_data["y"]:
    transform, fit_error = build_transform(ticks=ticks_data)
    xa = transform["x"]["a"]
    xb = transform["x"]["b"]
    ya = transform["y"]["a"]
    yb = transform["y"]["b"]
    print(f"Transform X: a={xa:.6f}, b={xb:.2f}")
    print(f"Transform Y: a={ya:.6f}, b={yb:.2f}")
    print(f"Fit error: {fit_error:.4f}")
    
    # Test pixel (250, 170) should be approximately (2, 30)
    test_px = np.array([[250, 170]])
    result = apply_transform(test_px, transform)
    rx = result[0,0]
    ry = result[0,1]
    print(f"Test: pixel (250,170) -> ({rx:.1f}, {ry:.1f})")
    print(f"Expected: roughly (2, 30)")
