import cv2
import numpy as np
import os

def create_synthetic_line_chart(output_path):
    # 500x700 image
    img = np.ones((500, 700, 3), dtype=np.uint8) * 255
    
    # Draw axes
    cv2.line(img, (50, 450), (650, 450), (0, 0, 0), 2)  # X axis
    cv2.line(img, (50, 50), (50, 450), (0, 0, 0), 2)   # Y axis
    
    # Draw line data
    points = []
    for x in range(100, 600, 10):
        y = 450 - (x - 100) * 0.5 - 20 * np.sin(x / 20)
        points.append((x, int(y)))
    
    for i in range(len(points) - 1):
        cv2.line(img, points[i], points[i+1], (0, 0, 0), 2)
        
    cv2.imwrite(output_path, img)
    print(f"Created {output_path}")

def create_synthetic_bar_chart(output_path):
    img = np.ones((500, 700, 3), dtype=np.uint8) * 255
    cv2.line(img, (50, 450), (650, 450), (0, 0, 0), 2)
    cv2.line(img, (50, 50), (50, 450), (0, 0, 0), 2)
    
    vals = [100, 150, 80, 200, 120]
    for i, v in enumerate(vals):
        x = 100 + i * 100
        cv2.rectangle(img, (x, 450 - v), (x + 40, 450), (0, 0, 0), -1)
        
    cv2.imwrite(output_path, img)
    print(f"Created {output_path}")

if __name__ == "__main__":
    os.makedirs("fixtures/synthetic", exist_ok=True)
    create_synthetic_line_chart("fixtures/synthetic/test_line_simple.png")
    create_synthetic_bar_chart("fixtures/synthetic/test_bar_simple.png")
