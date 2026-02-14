"""
Tests for the mesh_generation module.
"""
import numpy as np
from mesh_generation import generate_airfoil_points
from benchmark_mesh_generation import generate_airfoil_points_slow

def test_points_match():
    """Test that slow and fast methods produce identical points."""
    num_points = 1000
    points_slow = np.array(generate_airfoil_points_slow(num_points))
    points_fast = generate_airfoil_points(num_points)

    assert np.allclose(points_slow, points_fast), "Points do not match!"

def test_shape():
    """Test that the output shape is correct."""
    num_points = 100
    points = generate_airfoil_points(num_points)
    # Expected shape: (2 * num_points - 1, 3)
    expected_rows = 2 * num_points - 1
    assert points.shape == (expected_rows, 3), \
        f"Expected shape ({expected_rows}, 3), got {points.shape}"

def test_trailing_edge_x():
    """Test that the trailing edge is at x=1."""
    num_points = 100
    points = generate_airfoil_points(num_points)

    first_point = points[0]
    last_point = points[-1]

    assert np.isclose(first_point[0], 1.0), "First point x should be 1.0"
    assert np.isclose(last_point[0], 1.0), "Last point x should be 1.0"
