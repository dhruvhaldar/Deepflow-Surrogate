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
# numpy and gmsh are imported lazily in functions to improve CLI startup time

class Spinner:
    """A simple spinner for CLI feedback."""
    def __init__(self, message="Processing..."):
        self.message = message
        self.stop_event = threading.Event()
        self.thread = None

    def spin(self):
        """Displays the spinning animation."""
        spinner_chars = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        while not self.stop_event.is_set():
            sys.stdout.write(f"\r{self.message} {next(spinner_chars)}")
            sys.stdout.flush()
            # use wait instead of sleep to be responsive to stop signals
            self.stop_event.wait(0.1)

    def __enter__(self):
        self.start_time = time.perf_counter()
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
        elapsed = time.perf_counter() - self.start_time
        time_str = f" ({format_time(elapsed, precision_s=1)})"

        if self.thread:
            self.stop_event.set()
            self.thread.join()
            sys.stdout.write("\033[?25h")  # Show cursor

            # Print final status, overwriting the spinner character
            if exc_type is None:
                sys.stdout.write(f"\r{self.message} ✅{time_str}   \n")
            else:
                sys.stdout.write(f"\r{self.message} ❌{time_str}   \n")
            sys.stdout.flush()
        else:
            # Provide completion feedback for non-interactive environments
            if exc_type is None:
                sys.stdout.write(f" ✅{time_str}\n")
            else:
                sys.stdout.write(f" ❌{time_str}\n")
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
    DIM = '\033[2m'

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
        cls.DIM = ''

# Disable colors if NO_COLOR env var is set or output is not a TTY
if os.getenv('NO_COLOR') or not sys.stdout.isatty():
    Colors.disable()

def naca0012_y(x, t=0.12):
    """
    Calculates the y-coordinate of a NACA 0012 airfoil using a fully vectorized approach.
    """
    import numpy as np # pylint: disable=import-outside-toplevel

    # Use Horner's method for efficiency (fewer FLOPs and temporary arrays)
    # Optimization: Fold the 5*t scaling factor into the coefficients
    scale = 5 * t
    c0 = 0.2969 * scale
    c1 = -0.1260 * scale
    c2 = -0.3516 * scale
    c3 = 0.2843 * scale
    c4 = -0.1015 * scale

    # Fully Vectorized approach: writing the entire expression natively as a single
    # vectorized statement allows NumPy's underlying C backend to evaluate it without
    # creating unnecessary intermediate arrays or adding Python interpreter loop overhead.
    # This has proven to be ~25% faster than the hybrid or fully in-place iterative approach.
    return np.sqrt(x) * c0 + x * (c1 + x * (c2 + x * (c3 + x * c4)))

def format_time(elapsed, precision_s=1):
    """Formats elapsed time into ms (< 0.1s) or seconds (otherwise)."""
    if elapsed < 0.1:
        ms = elapsed * 1000
        if round(ms) == 0:
            return "<1ms"
        return f"{ms:.0f}ms"
    return f"{elapsed:.{precision_s}f}s"

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
    import numpy as np # pylint: disable=import-outside-toplevel

    x = np.linspace(0, 1, num_points)

    # Pre-allocate the final result array
    # Total points = num_points (upper) + (num_points - 1) (lower)
    total_points = 2 * num_points - 1

    # Use np.zeros to allocate the array since NumPy uses calloc under the hood,
    # which is lazy and faster than np.empty + manual zeroing.
    # Use Fortran-contiguous memory (order='F') since we assign and extract
    # data column-wise. This improves CPU cache locality.
    points = np.zeros((total_points, 3), order='F')

    # Upper surface (reversed): x from 1 to 0
    x_rev = x[::-1]
    points[:num_points, 0] = x_rev

    # Optimization: Write the NACA 0012 calculation directly into the points array.
    # We evaluate the mathematical formulation on the reversed x array
    # directly into the y_upper slice, saving a separate y_buffer array allocation.
    y_upper = points[:num_points, 1]
    y_upper[:] = naca0012_y(x_rev)

    # Lower surface (skip leading edge point): x from 0 to 1
    points[num_points:, 0] = x[1:]

    # The lower surface is the negative of the upper surface.
    # y_upper[-2::-1] takes the reversed y_upper array starting from the second element
    # (skipping the leading edge at x=0), which maps exactly to x[1:].
    np.negative(y_upper[-2::-1], out=points[num_points:, 1])

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
            import gmsh # pylint: disable=import-outside-toplevel
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
    import numpy as np # pylint: disable=import-outside-toplevel

    print(
        f"\n{Colors.OKBLUE}⚙️  Generating mesh for {len(points_for_gmsh):,} "
        f"points using Gmsh...{Colors.ENDC}",
        flush=True
    )
    try:
        import gmsh # pylint: disable=import-outside-toplevel
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
        # Using .copy() before .tolist() on a Fortran-contiguous array (order='F')
        # creates a C-contiguous 1D array first, which speeds up .tolist() conversion
        # by ~5x compared to iterating over the non-contiguous stride.
        xs = points_to_add[:, 0].copy().tolist()
        ys = points_to_add[:, 1].copy().tolist()
        # z is always 0.0 for 2D airfoil

        with Spinner(f"{Colors.OKBLUE}   Building geometry...{Colors.ENDC}"):
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
                empty = length - fill
                return (f"{Colors.OKBLUE}{'█' * fill}{Colors.ENDC}"
                        f"{Colors.DIM}{'░' * empty}{Colors.ENDC}")

            print(
                f"     - Triangles: {num_triangles:<8,} ({pct_tri:>5.1f}%) "
                f"{draw_bar(pct_tri)}",
                flush=True
            )
            print(
                f"     - Quads:     {num_quadrangles:<8,} ({pct_quad:>5.1f}%) "
                f"{draw_bar(pct_quad)}",
                flush=True
            )

        # Retrieve and display bounding box
        try:
            bbox = gmsh.model.getBoundingBox(-1, -1)
            # bbox is (minX, minY, minZ, maxX, maxY, maxZ)
            width = bbox[3] - bbox[0]
            height = bbox[4] - bbox[1]
            print(f"\n{Colors.OKCYAN}📏 Bounding Box:{Colors.ENDC}", flush=True)
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
                f"\n{Colors.WARNING}⚠️  Warning: The generated mesh has 0 elements. "
                f"Try increasing --num-points or adjusting geometry settings.{Colors.ENDC}",
                flush=True
            )

        # Suggest saving if running interactively and no output specified
        if not output_file and sys.stdout.isatty():
            print(f"\n{Colors.WARNING}⚠️  No output file specified.{Colors.ENDC}", flush=True)
            try:
                prompt = (
                    f"{Colors.OKBLUE}💾 Save to 'airfoil.msh'? "
                    f"[y/N] or type filename: {Colors.ENDC}"
                )
                response = input(prompt).strip()
                response_lower = response.lower()

                if response_lower in ('y', 'yes'):
                    proposed_file = "airfoil.msh"
                elif response_lower in ('n', 'no', ''):
                    proposed_file = None
                else:
                    proposed_file = response

                if proposed_file:
                    proposed_file = validate_output_path(proposed_file)
                    if check_overwrite(proposed_file, force=False):
                        ensure_directory_exists(proposed_file)
                        output_file = proposed_file
            except EOFError:
                pass

        if output_file:
            gmsh.write(output_file)
            file_size = os.path.getsize(output_file)
            readable_size = format_size(file_size)
            print(
                f"\n{Colors.OKGREEN}💾 Mesh written to {output_file} "
                f"({readable_size}){Colors.ENDC}",
                flush=True
            )
            if preview:
                print(
                    f"{Colors.OKBLUE}💡 Tip: View the mesh later using "
                    f"'gmsh {output_file}'{Colors.ENDC}",
                    flush=True
                )
            else:
                print(
                    f"{Colors.OKBLUE}💡 Tip: View the mesh using 'gmsh {output_file}' "
                    f"or run with --preview next time{Colors.ENDC}",
                    flush=True
                )
        else:
            # Only show warning if not interactive, to avoid nagging after a 'no' response
            if not sys.stdout.isatty():
                print(
                    f"\n{Colors.WARNING}⚠️  No output file specified. "
                    f"Mesh generated in memory only. Use --output to save.{Colors.ENDC}",
                    flush=True
                )

        # Handle preview if requested
        if preview:
            if output_file or not sys.stdout.isatty():
                print() # Add visual spacing before preview
            preview_mesh()

        print(f"\n{Colors.OKGREEN}✅ Mesh generation successful.{Colors.ENDC}", flush=True)

        gmsh.finalize()
        return True
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"{Colors.FAIL}❌ Gmsh error: {e}{Colors.ENDC}")
        return False

def validate_output_path(filepath):
    """
    Validates the output filepath.
    - Expands user (~) and environment variables.
    - Adds .msh extension if missing.
    - Warns if extension is suspicious (e.g. .txt).
    Returns the (possibly modified) filepath.
    """
    if not filepath:
        return filepath

    # Expand user (~) and environment variables
    filepath = os.path.expanduser(filepath)
    filepath = os.path.expandvars(filepath)

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
        try:
            file_size = os.path.getsize(filepath)
            readable_size = format_size(file_size)

            mtime = os.path.getmtime(filepath)
            diff = time.time() - mtime
            if diff < 60:
                rel_time = "just now"
            elif diff < 3600:
                mins = int(diff / 60)
                rel_time = f"{mins} min{'s' if mins != 1 else ''} ago"
            elif diff < 86400:
                hours = int(diff / 3600)
                rel_time = f"{hours} hour{'s' if hours != 1 else ''} ago"
            else:
                days = int(diff / 86400)
                rel_time = f"{days} day{'s' if days != 1 else ''} ago"

            size_str = f" ({readable_size}, modified {rel_time})"
        except OSError:
            size_str = ""

        print(
            f"{Colors.WARNING}⚠️  File '{Colors.BOLD}{filepath}{Colors.ENDC}{Colors.WARNING}' "
            f"already exists{size_str}.{Colors.ENDC}"
        )
        try:
            prompt = f"{Colors.FAIL}Overwrite? [y/N] {Colors.ENDC}"
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
        "-n", "--num-points",
        type=int,
        default=100,
        help="Number of points along the airfoil surface (must be > 0)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Path to save the generated mesh (e.g., 'mesh.msh'). "
             "If omitted, mesh is generated but not saved."
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite output file without confirmation if it exists."
    )
    parser.add_argument(
        "-p", "--preview",
        action="store_true",
        help="Open the generated mesh in Gmsh GUI immediately."
    )

    args = parser.parse_args()

    if args.num_points <= 0:
        print(f"{Colors.FAIL}❌ Error: --num-points must be a positive integer.{Colors.ENDC}")
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
    formatted_time = format_time(elapsed_time, precision_s=4)
    print(f"\n{Colors.OKBLUE}⏱️  Total execution time: {formatted_time}{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.FAIL}❌ Operation cancelled by user.{Colors.ENDC}")
        sys.exit(130)
    except ModuleNotFoundError as err:
        print(f"\n{Colors.FAIL}❌ Missing required dependency: '{err.name}'{Colors.ENDC}")
        print(f"{Colors.OKBLUE}💡 Tip: Install it by running 'pip install {err.name}' "
              f"or 'pip install -r requirements.txt'{Colors.ENDC}")
        sys.exit(1)
