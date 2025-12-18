"""
Generate synthetic test scatter plots with known parameters.

This creates simple, clean test images for development and testing.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path

def generate_scatter_simple():
    """Generate simple scatter plot with 20 points."""
    np.random.seed(42)

    # Generate data
    x = np.linspace(0, 100, 20) + np.random.normal(0, 2, 20)
    y = 2 * x + 10 + np.random.normal(0, 10, 20)

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(x, y, s=50, c='blue', alpha=0.7)

    # Set limits and labels
    ax.set_xlim(-5, 105)
    ax.set_ylim(0, 220)
    ax.set_xlabel('X axis', fontsize=12)
    ax.set_ylabel('Y axis', fontsize=12)
    ax.set_title('Simple Scatter Plot', fontsize=14)
    ax.grid(True, alpha=0.3)

    # Save
    output_dir = Path('fixtures/synthetic')
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / 'test_scatter_simple.png'
    fig.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close(fig)

    # Save metadata
    metadata = {
        'filename': 'test_scatter_simple.png',
        'chart_type': 'scatter',
        'num_points': 20,
        'x_range': [-5, 105],
        'y_range': [0, 220],
        'true_data': [[float(xi), float(yi)] for xi, yi in zip(x, y)],
        'notes': 'Simple scatter, 20 points, clean axes, light grid'
    }

    with open(output_dir / 'test_scatter_simple.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Generated {filepath}")
    return filepath


def generate_scatter_dense():
    """Generate dense scatter plot with 50 points."""
    np.random.seed(123)

    # Generate clustered data
    x = np.random.normal(50, 15, 50)
    y = np.random.normal(100, 25, 50)

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(x, y, s=40, c='red', alpha=0.6)

    # Set limits and labels
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 200)
    ax.set_xlabel('X axis', fontsize=12)
    ax.set_ylabel('Y axis', fontsize=12)
    ax.set_title('Dense Scatter Plot', fontsize=14)
    ax.grid(True, alpha=0.3)

    # Save
    output_dir = Path('fixtures/synthetic')
    filepath = output_dir / 'test_scatter_dense.png'
    fig.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close(fig)

    # Save metadata
    metadata = {
        'filename': 'test_scatter_dense.png',
        'chart_type': 'scatter',
        'num_points': 50,
        'x_range': [0, 100],
        'y_range': [0, 200],
        'true_data': [[float(xi), float(yi)] for xi, yi in zip(x, y)],
        'notes': 'Dense scatter, 50 points, clustered distribution'
    }

    with open(output_dir / 'test_scatter_dense.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Generated {filepath}")
    return filepath


def generate_scatter_sparse():
    """Generate sparse scatter plot with 10 points."""
    np.random.seed(789)

    # Generate wide-spread data
    x = np.random.uniform(0, 100, 10)
    y = np.random.uniform(0, 50, 10)

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(x, y, s=60, c='green', alpha=0.8, marker='o')

    # Set limits and labels
    ax.set_xlim(-10, 110)
    ax.set_ylim(-5, 55)
    ax.set_xlabel('X axis', fontsize=12)
    ax.set_ylabel('Y axis', fontsize=12)
    ax.set_title('Sparse Scatter Plot', fontsize=14)
    ax.grid(True, alpha=0.3)

    # Save
    output_dir = Path('fixtures/synthetic')
    filepath = output_dir / 'test_scatter_sparse.png'
    fig.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close(fig)

    # Save metadata
    metadata = {
        'filename': 'test_scatter_sparse.png',
        'chart_type': 'scatter',
        'num_points': 10,
        'x_range': [-10, 110],
        'y_range': [-5, 55],
        'true_data': [[float(xi), float(yi)] for xi, yi in zip(x, y)],
        'notes': 'Sparse scatter, 10 points, wide spread'
    }

    with open(output_dir / 'test_scatter_sparse.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Generated {filepath}")
    return filepath


def main():
    """Generate all test plots."""
    print("Generating synthetic test plots...")
    print()

    generate_scatter_simple()
    generate_scatter_dense()
    generate_scatter_sparse()

    print()
    print("✓ All test plots generated successfully!")
    print("Location: fixtures/synthetic/")
    print()
    print("Files created:")
    print("  - test_scatter_simple.png + .json")
    print("  - test_scatter_dense.png + .json")
    print("  - test_scatter_sparse.png + .json")


if __name__ == '__main__':
    main()
