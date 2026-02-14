"""
This script benchmarks the optimized airfoil point generation against a naive implementation.
"""
import time
import numpy as np
from mesh_generation import generate_airfoil_points, naca0012_y

def generate_airfoil_points_slow(num_points):
    """Generates airfoil points using a for-loop (inefficient) for benchmarking."""
    xs = []
    ys_upper = []
    ys_lower = []

    # Intentionally inefficient list appending
    for i in range(num_points):
        x = i / (num_points - 1)
        xs.append(x)
        y = naca0012_y(x) # This still uses numpy inside, but the loop overhead is real
        ys_upper.append(y)
        ys_lower.append(-y)

    points = []
    # Combine upper and lower surfaces
    for i in range(num_points):
        points.append([xs[num_points - 1 - i], ys_upper[num_points - 1 - i], 0.0])
    for i in range(1, num_points):
        points.append([xs[i], ys_lower[i], 0.0])

    return points

def measure_performance():
    """Measures and compares performance of slow vs fast point generation."""
    num_points = 1000000 # Large number to make it measurable

    print(f"Generating {num_points} points per surface...")

    start_time = time.time()
    points_slow = generate_airfoil_points_slow(num_points)
    end_time = time.time()
    duration_slow = end_time - start_time
    print(f"Slow method duration: {duration_slow:.4f} seconds")

    start_time = time.time()
    points_fast = generate_airfoil_points(num_points)
    end_time = time.time()
    duration_fast = end_time - start_time
    print(f"Fast method duration: {duration_fast:.4f} seconds")

    if duration_fast > 0:
        speedup = duration_slow / duration_fast
        print(f"Speedup: {speedup:.2f}x")
    else:
        print("Fast method was instantaneous!")

    # Verify correctness (basic check)
    points_slow_np = np.array(points_slow)
    if np.allclose(points_slow_np, points_fast):
        print("Verification: Both methods produced identical points.")
    else:
        print("Verification: Methods produced DIFFERENT points!")

if __name__ == "__main__":
    measure_performance()
