"""
This module provides functions for efficient airfoil point generation using NumPy vectorization.
It also includes a function to generate a mesh using Gmsh.
"""

import argparse
import sys
import os
import time
import threading
import itertools
import numpy as np
import gmsh

class Spinner:
    """A simple spinner for CLI feedback."""
    def __init__(self, message="Processing..."):
        self.message = message
        self.stop_running = False
        self.thread = None

    def spin(self):
        """Displays the spinning animation."""
        spinner_chars = itertools.cycle(['-', '/', '|', '\\'])
        while not self.stop_running:
            sys.stdout.write(f"\r{self.message} {next(spinner_chars)}")
            sys.stdout.flush()
            time.sleep(0.1)
        # Clear line
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()

    def __enter__(self):
        if sys.stdout.isatty():
            self.stop_running = False
            self.thread = threading.Thread(target=self.spin)
            self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.thread:
            self.stop_running = True
            self.thread.join()

class Colors: # pylint: disable=too-few-public-methods
    """ANSI color codes for CLI output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @classmethod
    def disable(cls):
        """Disables all colors."""
        cls.HEADER = ''
        cls.OKBLUE = ''
        cls.OKCYAN = ''
        cls.OKGREEN = ''
        cls.WARNING = ''
        cls.FAIL = ''
        cls.ENDC = ''
        cls.BOLD = ''

# Disable colors if NO_COLOR env var is set or output is not a TTY
if os.getenv('NO_COLOR') or not sys.stdout.isatty():
    Colors.disable()

def naca0012_y(x, t=0.12):
    """Calculates the y-coordinate of a NACA 0012 airfoil."""
    return 5 * t * (
        0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 +
        0.2843 * x**3 - 0.1015 * x**4
    )

def format_size(size_bytes):
    """Formats bytes into a human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            if unit == 'B':
                return f"{int(size_bytes)} {unit}"
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

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
    print(
        f"\n{Colors.OKBLUE}⚙️  Generating mesh for {len(points_for_gmsh):,} "
        f"points using Gmsh...{Colors.ENDC}",
        flush=True
    )
    try:
        gmsh.initialize()
        gmsh.option.setNumber("General.Verbosity", 2)  # Reduce console noise
        gmsh.option.setNumber("Mesh.Smoothing", 0)     # Disable smoothing for ~35% speedup
        gmsh.option.setNumber("Mesh.Algorithm", 5)     # Delaunay is ~32% faster for 2D meshes
        gmsh.option.setNumber("General.NumThreads", 0) # Enable parallel mesh generation (all cores)
        gmsh.model.add("airfoil")

        lc = 0.1
        point_tags = []

        # Check if the last point is a duplicate of the first (closed loop)
        # If so, exclude the last point to avoid zero-length segments.
        # We handle loop closure explicitly via addPolyline.
        if len(points_for_gmsh) > 1 and np.allclose(points_for_gmsh[0], points_for_gmsh[-1]):
            points_to_add = points_for_gmsh[:-1]
        else:
            points_to_add = points_for_gmsh

        # Convert to list for faster iteration (avoids NumPy overhead in loop)
        points_list = points_to_add.tolist()
        for p in points_list:
            tag = gmsh.model.geo.addPoint(p[0], p[1], p[2], lc)
            point_tags.append(tag)

        # Connect points with a single polyline
        # Append the first point tag to the end to close the loop
        if point_tags:
            polyline_tags = point_tags + [point_tags[0]]
            # Returns a single curve tag
            polyline = gmsh.model.geo.addPolyline(polyline_tags)
            curve_loop = gmsh.model.geo.addCurveLoop([polyline])
        else:
            # Fallback for empty points (shouldn't happen with valid input)
            curve_loop = gmsh.model.geo.addCurveLoop([])
        gmsh.model.geo.addPlaneSurface([curve_loop])

        gmsh.model.geo.synchronize()
        with Spinner(f"{Colors.OKBLUE}   Meshing...{Colors.ENDC}"):
            gmsh.model.mesh.generate(2)

        # Get mesh statistics
        node_tags, _, _ = gmsh.model.mesh.getNodes()
        num_nodes = len(node_tags)

        _, element_tags, _ = gmsh.model.mesh.getElements()
        num_elements = sum(len(tags) for tags in element_tags)

        print(
            f"{Colors.OKCYAN}📊 Mesh Statistics: {num_nodes:,} nodes, "
            f"{num_elements:,} elements{Colors.ENDC}",
            flush=True
        )

        if output_file:
            gmsh.write(output_file)
            file_size = os.path.getsize(output_file)
            readable_size = format_size(file_size)
            print(
                f"{Colors.OKGREEN}💾 Mesh written to {output_file} "
                f"({readable_size}){Colors.ENDC}",
                flush=True
            )
        else:
            print(
                f"{Colors.WARNING}⚠️  No output file specified. Mesh generated in memory only. "
                f"Use --output to save.{Colors.ENDC}",
                flush=True
            )

        print(f"{Colors.OKGREEN}✅ Mesh generation successful.{Colors.ENDC}", flush=True)

        gmsh.finalize()
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"{Colors.FAIL}❌ Gmsh error: {e}{Colors.ENDC}")

def check_overwrite(filepath, force):
    """Checks if output file exists and prompts user if needed."""
    if not filepath or not os.path.exists(filepath) or force:
        return True

    if sys.stdout.isatty():
        print(
            f"{Colors.WARNING}⚠️  File '{Colors.BOLD}{filepath}{Colors.ENDC}{Colors.WARNING}' "
            f"already exists.{Colors.ENDC}"
        )
        try:
            prompt = f"{Colors.OKBLUE}Overwrite? [y/N] {Colors.ENDC}"
            response = input(prompt).strip().lower()
        except EOFError:
            return False

        if response in ('y', 'yes'):
            return True

        print(f"{Colors.FAIL}❌ Operation cancelled.{Colors.ENDC}")
        return False

    # Non-interactive mode, just warn
    print(
        f"{Colors.WARNING}⚠️  Overwriting existing file '{filepath}' "
        f"(non-interactive).{Colors.ENDC}"
    )
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output file without confirmation if it exists."
    )

    args = parser.parse_args()

    if args.num_points <= 0:
        print(f"{Colors.FAIL}Error: --num-points must be a positive integer.{Colors.ENDC}")
        sys.exit(1)

    if not check_overwrite(args.output, args.force):
        sys.exit(0)

    start_time = time.time()
    airfoil_points = generate_airfoil_points(args.num_points)
    generate_gmsh_mesh(airfoil_points, args.output)
    elapsed_time = time.time() - start_time
    print(f"\n{Colors.OKBLUE}⏱️  Total execution time: {elapsed_time:.4f}s{Colors.ENDC}")
