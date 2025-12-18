#!/bin/bash
# Test minimal CLI with synthetic data

echo "Testing Chart2CSV Minimal CLI"
echo "=============================="
echo ""

# Activate venv
source venv/bin/activate

# Test on simple scatter plot
echo "Test 1: Simple Scatter Plot"
echo "----------------------------"

# For test_scatter_simple.png (x_range: -5 to 105, y_range: 0 to 220)
# We need to provide calibration points
# Looking at matplotlib default, the plot area is approximately:
# - Left edge (x=-5) at pixel ~80
# - Right edge (x=105) at pixel ~730
# - Bottom edge (y=0) at pixel ~530
# - Top edge (y=220) at pixel ~60

# Create input file for calibration
cat > /tmp/calib_simple.txt <<EOF
80
-5
730
105
530
0
60
220
EOF

# Run minimal CLI
python -m chart2csv.cli.minimal \
  fixtures/synthetic/test_scatter_simple.png \
  --calibrate \
  --output fixtures/synthetic/test_scatter_simple_output.csv \
  --visualize fixtures/synthetic/test_scatter_simple_viz.png \
  < /tmp/calib_simple.txt

echo ""
echo "✓ Test complete!"
echo "Check output:"
echo "  - CSV: fixtures/synthetic/test_scatter_simple_output.csv"
echo "  - Visualization: fixtures/synthetic/test_scatter_simple_viz.png"
echo ""
