
import time
import numpy as np
import gmsh
from mesh_generation import generate_airfoil_points, naca0012_y

def check_te_closeness():
    points = generate_airfoil_points(100)
    p0 = points[0]
    p_last = points[-1]
    print(f"P0: {p0}")
    print(f"P_last: {p_last}")
    dist = np.linalg.norm(p0 - p_last)
    print(f"Distance: {dist}")
    is_close = np.allclose(p0, p_last)
    print(f"np.allclose: {is_close}")

def profile_add_points():
    num_points = 10000
    points = generate_airfoil_points(num_points)

    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 0)
    gmsh.option.setNumber("Geometry.AutoCoherence", 0)
    gmsh.model.add("test")

    lc = 0.1

    # Current method
    xs = points[:, 0].tolist()
    ys = points[:, 1].tolist()

    start = time.time()
    for x, y in zip(xs, ys):
        gmsh.model.geo.addPoint(x, y, 0.0, lc)
    end = time.time()
    print(f"addPoint loop (N={len(points)}): {end - start:.4f}s")

    gmsh.finalize()

if __name__ == "__main__":
    print("Checking TE Closeness:")
    check_te_closeness()
    print("\nProfiling addPoint:")
    profile_add_points()
