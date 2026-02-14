"""
This module provides functions for efficient airfoil point generation using NumPy vectorization.
It also includes a function to generate a mesh using Gmsh.
"""

import argparse
import sys
import numpy as np
import gmsh

def naca0012_y(x, t=0.12):
    """Calculates the y-coordinate of a NACA 0012 airfoil."""
    return 5 * t * (
        0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 +
        0.2843 * x**3 - 0.1015 * x**4
    )

def generate_airfoil_points(num_points):
    """Generates airfoil points using NumPy vectorization (efficient)."""
    x = np.linspace(0, 1, num_points)
    y = naca0012_y(x)

    # Combine upper and lower surfaces efficiently
    # Upper surface: x from 1 to 0, y positive
    # Lower surface: x from 0 to 1, y negative

    x_upper = x[::-1]
    y_upper = y[::-1]

    x_lower = x[1:]
    y_lower = -y[1:]

    x_coords = np.concatenate([x_upper, x_lower])
    y_coords = np.concatenate([y_upper, y_lower])
    z_coords = np.zeros_like(x_coords)

    points = np.column_stack([x_coords, y_coords, z_coords])
    return points

def generate_gmsh_mesh(points_for_gmsh, output_file=None):
    """Generates a mesh using Gmsh based on the provided points."""
    # pylint: disable=too-many-locals
    print(f"\n⚙️  Generating mesh for {len(points_for_gmsh)} points using Gmsh...", flush=True)
    try:
        gmsh.initialize()
        gmsh.option.setNumber("General.Verbosity", 2)  # Reduce console noise
        gmsh.model.add("airfoil")

        lc = 0.1
        point_tags = []
        for p in points_for_gmsh:
            tag = gmsh.model.geo.addPoint(p[0], p[1], p[2], lc)
            point_tags.append(tag)

        # Connect points with splines or lines
        # For simplicity, we use a loop of lines
        line_tags = []
        for i, p1 in enumerate(point_tags):
            p2 = point_tags[(i + 1) % len(point_tags)]
            l = gmsh.model.geo.addLine(p1, p2)
            line_tags.append(l)

        curve_loop = gmsh.model.geo.addCurveLoop(line_tags)
        gmsh.model.geo.addPlaneSurface([curve_loop])

        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate(2)

        # Get mesh statistics
        node_tags, _, _ = gmsh.model.mesh.getNodes()
        num_nodes = len(node_tags)

        _, element_tags, _ = gmsh.model.mesh.getElements()
        num_elements = sum(len(tags) for tags in element_tags)

        print(
            f"📊 Mesh Statistics: {num_nodes} nodes, {num_elements} elements",
            flush=True
        )

        if output_file:
            gmsh.write(output_file)
            print(f"💾 Mesh written to {output_file}", flush=True)
        else:
            print(
                "⚠️  No output file specified. Mesh generated in memory only. "
                "Use --output to save.",
                flush=True
            )

        print("✅ Mesh generation successful.", flush=True)

        gmsh.finalize()
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"❌ Gmsh error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a 2D unstructured mesh around a NACA 0012 airfoil using Gmsh.",
        epilog="Example: python mesh_generation.py --num-points 200 --output airfoil.msh"
    )
    parser.add_argument(
        "--num-points",
        type=int,
        default=100,
        help="Number of points along the airfoil surface (must be > 0)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to save the generated mesh (e.g., 'mesh.msh'). "
             "If omitted, mesh is generated but not saved."
    )

    args = parser.parse_args()

    if args.num_points <= 0:
        print("Error: --num-points must be a positive integer.")
        sys.exit(1)

    airfoil_points = generate_airfoil_points(args.num_points)
    generate_gmsh_mesh(airfoil_points, args.output)
