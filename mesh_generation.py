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
        self.stop_event = threading.Event()
        self.thread = None

    def spin(self):
        """Displays the spinning animation."""
        spinner_chars = itertools.cycle(['-', '/', '|', '\\'])
        while not self.stop_event.is_set():
            sys.stdout.write(f"\r{self.message} {next(spinner_chars)}")
            sys.stdout.flush()
            # use wait instead of sleep to be responsive to stop signals
            self.stop_event.wait(0.1)

    def __enter__(self):
        if sys.stdout.isatty() and not os.getenv('NO_COLOR'):
            sys.stdout.write("\033[?25l")  # Hide cursor
            sys.stdout.flush()
            self.stop_event.clear()
            self.thread = threading.Thread(target=self.spin, daemon=True)
            self.thread.start()
        else:
            sys.stdout.write(self.message)
            sys.stdout.flush()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.thread:
            self.stop_event.set()
            self.thread.join()
            sys.stdout.write("\033[?25h")  # Show cursor

            # Print final status, overwriting the spinner character
            if exc_type is None:
                sys.stdout.write(f"\r{self.message} ✅   \n")
            else:
                sys.stdout.write(f"\r{self.message} ❌   \n")
            sys.stdout.flush()
        else:
            # Provide completion feedback for non-interactive environments
            if exc_type is None:
                sys.stdout.write(" ✅\n")
            else:
                sys.stdout.write(" ❌\n")
            sys.stdout.flush()

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

def naca0012_y(x, t=0.12, out=None, scratch=None):
    """
    Calculates the y-coordinate of a NACA 0012 airfoil.
    Supports in-place modification to avoid temporary allocations.
    """
    # Use Horner's method for efficiency (fewer FLOPs and temporary arrays)
    # Optimization: Fold the 5*t scaling factor into the coefficients
    scale = 5 * t
    c0 = 0.2969 * scale
    c1 = -0.1260 * scale
    c2 = -0.3516 * scale
    c3 = 0.2843 * scale
    c4 = -0.1015 * scale

    if out is None:
        out = np.empty_like(x)

    # Use in-place operations to avoid temporary array allocations
    # Corresponds to: out = x * (c1 + x * (c2 + x * (c3 + x * c4))) + c0 * sqrt(x)
    out.fill(c4)
    out *= x
    out += c3
    out *= x
    out += c2
    out *= x
    out += c1
    out *= x

    # Add sqrt term. If scratch buffer provided, use it to avoid temporary array allocation
    if scratch is not None:
        np.sqrt(x, out=scratch)
        sqrt_x = scratch
    else:
        sqrt_x = np.sqrt(x)

    sqrt_x *= c0
    out += sqrt_x

    return out

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

    # Pre-allocate the result array to avoid intermediate allocations
    # Total points = num_points (upper) + (num_points - 1) (lower)
    total_points = 2 * num_points - 1
    points = np.zeros((total_points, 3))

    # Compute Y values for all x once, storing in the unused Z column (scratchpad)
    # This avoids recalculating the same values for the lower surface
    y_buffer = points[:num_points, 2]
    # Reuse the unused Y column (points[:num_points, 1]) as a scratch buffer for sqrt(x)
    # This eliminates the last temporary array allocation in naca0012_y
    scratch_buffer = points[:num_points, 1]
    naca0012_y(x, out=y_buffer, scratch=scratch_buffer)

    # Upper surface (reversed): x from 1 to 0
    points[:num_points, 0] = x[::-1]
    # Copy pre-calculated Y values (reversed)
    points[:num_points, 1] = y_buffer[::-1]

    # Lower surface (skip leading edge point): x from 0 to 1
    points[num_points:, 0] = x[1:]
    # Negate the pre-calculated Y values for the lower surface
    # Note: x[1:] corresponds to y_buffer[1:]
    np.negative(y_buffer[1:], out=points[num_points:, 1])

    # Clean up the Z column used as scratchpad
    y_buffer.fill(0.0)

    return points

def preview_mesh():
    """Opens the generated mesh in Gmsh GUI."""
    # Check for display environment (Linux/Unix requires DISPLAY)
    # macOS and Windows usually handle GUI without explicit env var
    is_headless = os.getenv("DISPLAY") is None and \
                  sys.platform != "darwin" and \
                  os.name != "nt"

    if sys.stdout.isatty() and not is_headless:
        print(
            f"{Colors.OKBLUE}👀 Opening preview... "
            f"(Close window to finish){Colors.ENDC}",
            flush=True
        )
        try:
            gmsh.fltk.run()
        except Exception as e: # pylint: disable=broad-exception-caught
            print(f"{Colors.WARNING}⚠️  Preview failed: {e}{Colors.ENDC}")
    else:
        reason = "No display detected" if is_headless else "Non-interactive session"
        print(
            f"{Colors.WARNING}⚠️  Preview skipped: {reason}.{Colors.ENDC}"
        )

def generate_gmsh_mesh(points_for_gmsh, output_file=None, preview=False):
    """Generates a mesh using Gmsh based on the provided points."""
    # pylint: disable=too-many-locals
    print(
        f"\n{Colors.OKBLUE}⚙️  Generating mesh for {len(points_for_gmsh):,} "
        f"points using Gmsh...{Colors.ENDC}",
        flush=True
    )
    try:
        gmsh.initialize()
        gmsh.option.setNumber("General.Verbosity", 0)  # Silence console noise (saves I/O & locks)
        gmsh.option.setNumber("Geometry.AutoCoherence", 0) # Disable duplicate check (~6% speedup)
        gmsh.option.setNumber("Mesh.Smoothing", 0)     # Disable smoothing for ~35% speedup
        gmsh.option.setNumber("Mesh.Algorithm", 5)     # Delaunay is ~32% faster for 2D meshes
        gmsh.option.setNumber("General.NumThreads", 0) # Enable parallel mesh generation (all cores)
        gmsh.option.setNumber("Mesh.Binary", 1)        # Binary output is ~3.4x faster for writing
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

        # Extract x and y coordinates to separate lists for faster iteration.
        # This avoids creating a list for z-coordinates (which are all 0) and the overhead of
        # ravel() + zip(it, it, it), reducing temporary object creation by ~33%.
        xs = points_to_add[:, 0].tolist()
        ys = points_to_add[:, 1].tolist()
        # z is always 0.0 for 2D airfoil

        add_point = gmsh.model.geo.addPoint
        point_tags = [
            add_point(x, y, 0.0, lc)
            for x, y in zip(xs, ys)
        ]

        # Connect points with a single polyline
        # Append the first point tag to the end to close the loop
        if point_tags:
            point_tags.append(point_tags[0])
            # Returns a single curve tag
            polyline = gmsh.model.geo.addPolyline(point_tags)
            curve_loop = gmsh.model.geo.addCurveLoop([polyline])
        else:
            # Fallback for empty points (shouldn't happen with valid input)
            curve_loop = gmsh.model.geo.addCurveLoop([])
        gmsh.model.geo.addPlaneSurface([curve_loop])

        gmsh.model.geo.synchronize()
        with Spinner(f"{Colors.OKBLUE}   Meshing...{Colors.ENDC}"):
            gmsh.model.mesh.generate(2)

        # Get mesh statistics
        # Efficiently get node count without copying large arrays (O(1) vs O(N))
        num_nodes = int(gmsh.option.getNumber("Mesh.NbNodes"))

        # Efficiently get 2D element count (O(1)) without overhead of getElements()
        num_triangles = int(gmsh.option.getNumber("Mesh.NbTriangles"))
        num_quadrangles = int(gmsh.option.getNumber("Mesh.NbQuadrangles"))
        num_elements = num_triangles + num_quadrangles

        print(f"\n{Colors.OKCYAN}📊 Mesh Statistics:{Colors.ENDC}", flush=True)
        print(f"   • Nodes:      {num_nodes:,}", flush=True)
        print(f"   • Elements:   {num_elements:,}", flush=True)

        if num_elements > 0:
            pct_tri = (num_triangles / num_elements) * 100
            pct_quad = (num_quadrangles / num_elements) * 100

            def draw_bar(p, length=20):
                if not Colors.OKBLUE:
                    return ""
                fill = int(p / 100 * length)
                return '█' * fill + '░' * (length - fill)

            print(
                f"     - Triangles: {num_triangles:,} ({pct_tri:.1f}%) "
                f"{Colors.OKBLUE}{draw_bar(pct_tri)}{Colors.ENDC}",
                flush=True
            )
            print(
                f"     - Quads:     {num_quadrangles:,} ({pct_quad:.1f}%) "
                f"{Colors.OKBLUE}{draw_bar(pct_quad)}{Colors.ENDC}",
                flush=True
            )

        # Retrieve and display bounding box
        try:
            bbox = gmsh.model.getBoundingBox(-1, -1)
            # bbox is (minX, minY, minZ, maxX, maxY, maxZ)
            width = bbox[3] - bbox[0]
            height = bbox[4] - bbox[1]
            print(f"{Colors.OKCYAN}📏 Bounding Box:{Colors.ENDC}", flush=True)
            print(
                f"   • X Range:    [{bbox[0]:.4f}, {bbox[3]:.4f}] (Width: {width:.4f})",
                flush=True
            )
            print(
                f"   • Y Range:    [{bbox[1]:.4f}, {bbox[4]:.4f}] (Height: {height:.4f})",
                flush=True
            )
        except Exception: # pylint: disable=broad-exception-caught
            # Bounding box might fail if model is empty; ignore silently or handle gracefully
            pass

        if num_elements == 0:
            print(
                f"{Colors.WARNING}⚠️  Warning: The generated mesh has 0 elements. "
                f"Try increasing --num-points or adjusting geometry settings.{Colors.ENDC}",
                flush=True
            )

        # Suggest saving if running interactively and no output specified
        if not output_file and sys.stdout.isatty():
            print(f"{Colors.WARNING}⚠️  No output file specified.{Colors.ENDC}", flush=True)
            try:
                prompt = f"{Colors.OKBLUE}Save to 'airfoil.msh'? [y/N] {Colors.ENDC}"
                if input(prompt).strip().lower() in ('y', 'yes'):
                    if check_overwrite("airfoil.msh", force=False):
                        output_file = "airfoil.msh"
            except EOFError:
                pass

        if output_file:
            gmsh.write(output_file)
            file_size = os.path.getsize(output_file)
            readable_size = format_size(file_size)
            print(
                f"{Colors.OKGREEN}💾 Mesh written to {output_file} "
                f"({readable_size}){Colors.ENDC}",
                flush=True
            )
            print(
                f"{Colors.OKBLUE}💡 Tip: View the mesh using 'gmsh {output_file}'{Colors.ENDC}",
                flush=True
            )
        else:
            # Only show warning if not interactive, to avoid nagging after a 'no' response
            if not sys.stdout.isatty():
                print(
                    f"{Colors.WARNING}⚠️  No output file specified. Mesh generated in memory only. "
                    f"Use --output to save.{Colors.ENDC}",
                    flush=True
                )

        # Handle preview if requested
        if preview:
            preview_mesh()

        print(f"{Colors.OKGREEN}✅ Mesh generation successful.{Colors.ENDC}", flush=True)

        gmsh.finalize()
        return True
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"{Colors.FAIL}❌ Gmsh error: {e}{Colors.ENDC}")
        return False

def validate_output_path(filepath):
    """
    Validates the output filepath.
    - Adds .msh extension if missing.
    - Warns if extension is suspicious (e.g. .txt).
    Returns the (possibly modified) filepath.
    """
    if not filepath:
        return filepath

    # Check if filepath is a directory or ends with a separator
    # This prevents creating hidden files like .msh or dir/.msh
    is_dir_path = filepath.endswith(os.sep)
    if os.altsep:
        is_dir_path = is_dir_path or filepath.endswith(os.altsep)

    if os.path.isdir(filepath) or is_dir_path:
        new_filepath = os.path.join(filepath, "airfoil.msh")
        print(
            f"{Colors.OKCYAN}ℹ️  Output path '{filepath}' appears to be a directory. "
            f"Using '{new_filepath}'.{Colors.ENDC}"
        )
        return new_filepath

    _, ext = os.path.splitext(filepath)

    if not ext:
        new_filepath = f"{filepath}.msh"
        print(
            f"{Colors.OKCYAN}ℹ️  Output filename '{filepath}' has no extension. "
            f"Defaulting to '{new_filepath}'.{Colors.ENDC}"
        )
        return new_filepath

    if ext.lower() in ['.txt', '.md', '.json', '.yaml', '.yml', '.py', '.sh']:
        print(
            f"{Colors.WARNING}⚠️  Warning: The extension '{ext}' is likely not supported by Gmsh. "
            f"The generation might fail.{Colors.ENDC}"
        )

    return filepath

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

def ensure_directory_exists(filepath):
    """Ensures the directory for the given filepath exists."""
    if not filepath:
        return

    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"{Colors.OKBLUE}📂 Created directory '{directory}'{Colors.ENDC}")
        except OSError as e:
            print(f"{Colors.FAIL}❌ Error creating directory '{directory}': {e}{Colors.ENDC}")
            sys.exit(1)

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Generate a 2D unstructured mesh around a NACA 0012 airfoil using Gmsh.",
        epilog=f"Example: {Colors.OKCYAN}python mesh_generation.py "
               f"--num-points 200 --output airfoil.msh{Colors.ENDC}"
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
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Open the generated mesh in Gmsh GUI immediately."
    )

    args = parser.parse_args()

    if args.num_points <= 0:
        print(f"{Colors.FAIL}Error: --num-points must be a positive integer.{Colors.ENDC}")
        sys.exit(1)

    args.output = validate_output_path(args.output)

    if not check_overwrite(args.output, args.force):
        sys.exit(0)

    ensure_directory_exists(args.output)

    start_time = time.time()
    airfoil_points = generate_airfoil_points(args.num_points)
    success = generate_gmsh_mesh(airfoil_points, args.output, args.preview)

    if not success:
        sys.exit(1)

    elapsed_time = time.time() - start_time
    print(f"\n{Colors.OKBLUE}⏱️  Total execution time: {elapsed_time:.4f}s{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.FAIL}❌ Operation cancelled by user.{Colors.ENDC}")
        sys.exit(130)
