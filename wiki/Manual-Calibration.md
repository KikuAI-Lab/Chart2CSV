# Manual Calibration Guide

> **Use this when automatic extraction fails on Dense charts.**

---

## When to Use

- LLM extraction returns inaccurate data
- Chart has 20+ closely-spaced data points
- You need precise values for research

---

## How It Works

1. Open your chart image in an image editor
2. Note the pixel coordinates of known reference points
3. Provide these as calibration points
4. API uses your calibration to transform pixel → values

---

## API Usage

### Endpoint

```
POST /extract/calibrated
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `file` | file | Chart image |
| `calibration_json` | string | JSON with reference points |

### Calibration Format

```json
{
    "x_axis": [
        {"pixel": 100, "value": 0},
        {"pixel": 500, "value": 20}
    ],
    "y_axis": [
        {"pixel": 350, "value": 0},
        {"pixel": 50, "value": 30}
    ]
}
```

**Important:**
- Provide at least 2 points per axis
- For X-axis: pixel increases left→right, value increases accordingly
- For Y-axis: pixel decreases bottom→top (images have Y=0 at top)

---

## Example

### curl

```bash
curl -X POST "https://chart2csv.kikuai.dev/extract/calibrated" \
  -F "file=@dense_chart.png" \
  -F 'calibration_json={"x_axis":[{"pixel":50,"value":0},{"pixel":550,"value":20}],"y_axis":[{"pixel":350,"value":0},{"pixel":50,"value":30}]}'
```

### Python

```python
import requests
import json

calibration = {
    "x_axis": [
        {"pixel": 50, "value": 0},
        {"pixel": 550, "value": 20}
    ],
    "y_axis": [
        {"pixel": 350, "value": 0},
        {"pixel": 50, "value": 30}
    ]
}

with open("dense_chart.png", "rb") as f:
    response = requests.post(
        "https://chart2csv.kikuai.dev/extract/calibrated",
        files={"file": f},
        data={"calibration_json": json.dumps(calibration)}
    )

print(response.json()["csv"])
```

---

## Tips

1. **Getting pixel coordinates**: Use any image editor (GIMP, Photoshop, Preview) to hover over axis tick marks
2. **Accuracy**: More calibration points = more accurate results
3. **Y-axis direction**: Remember that image Y coordinates are inverted (0 at top)
