import os
os.environ["MISTRAL_API_KEY"] = "ruQqe2KV9UTYebSxZVrGDf9tIzcEGpbS"

import sys
sys.path.insert(0, "/app")

import cv2
import numpy as np

# Create test chart
h, w = 400, 600
img = np.ones((h, w), dtype=np.uint8) * 255
cv2.line(img, (50, 350), (550, 350), 0, 2)
cv2.line(img, (50, 50), (50, 350), 0, 2)

for i, val in enumerate([0, 1, 2, 3, 4, 5]):
    x = 50 + i * 100
    cv2.line(img, (x, 345), (x, 355), 0, 2)
    cv2.putText(img, str(val), (x-5, 375), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)

for i, val in enumerate([0, 10, 20, 30, 40, 50]):
    y = 350 - i * 60
    cv2.line(img, (45, y), (55, y), 0, 2)
    cv2.putText(img, str(val), (10, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)

# Draw actual data points
for i in range(6):
    x = 50 + i * 100
    y = 350 - i * 60
    cv2.circle(img, (x, y), 6, 0, -1)

cv2.imwrite("/tmp/test_linear.png", img)
print("Created test chart")

from chart2csv.core.llm_extraction import extract_chart_llm

result, conf = extract_chart_llm("/tmp/test_linear.png")
print("Confidence:", conf)

if "error" in result:
    print("Error:", result)
else:
    chart_type = result.get("chart_type", "?")
    data = result.get("data", [])
    print("Chart type:", chart_type)
    print("Points:", len(data))
    
    # Print first 6 points
    for p in data[:6]:
        px = round(p.get("x", 0), 1)
        py = round(p.get("y", 0), 1)
        print(f"  ({px}, {py})")
    
    print("Expected: (0,0), (1,10), (2,20), (3,30), (4,40), (5,50)")
