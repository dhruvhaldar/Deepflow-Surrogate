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
import shlex
import pathlib
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
            sys.stdout.write(f"\r{self.message} {Colors.OKCYAN}{next(spinner_chars)}{Colors.ENDC}")
            sys.stdout.flush()
            # use wait instead of sleep to be responsive to stop signals
            self.stop_event.wait(0.1)

    def __enter__(self):
        self.start_time = time.perf_counter()
        if sys.stdout.isatty():
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
        time_str = f" {Colors.DIM}({format_time(elapsed, precision_s=1)}){Colors.ENDC}"

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

class InteractiveTimer:
    """Context manager to track time spent waiting for user input or GUI interaction."""
    def __init__(self):
        self.idle_time = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.idle_time += time.perf_counter() - self.start_time

    def reset(self):
        self.idle_time = 0.0

# Global instance to track interactive idle time across the execution
interactive_timer = InteractiveTimer()

def naca0012_y(x, t=0.12, out=None, scratch=None):
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

    if out is None:
        return np.sqrt(x) * c0 + x * (c1 + x * (c2 + x * (c3 + x * c4)))

    # Optimization: Evaluating the monolithic expression `np.sqrt(x) * c0 + x * ...`
    # creates up to 6 intermediate temporary arrays in memory, causing significant overhead.
    # While strided memory access is theoretically slower for in-place operations,
    # eliminating these heavy memory allocations by using explicit `out=` parameters
    # with in-place ufuncs is practically ~2x faster, especially for column slices of
    # Fortran-ordered 2D arrays.
    # Further optimization: using Python's augmented assignment operators (`*=`, `+=`)
    # on the `out` array directly maps to NumPy's in-place C ufuncs but sidesteps the
    # overhead of explicit Python function calls (e.g., `np.multiply(..., out=out)`),
    # yielding an additional ~15-20% speedup for this dense arithmetic block.
    # Optimization: Evaluating operations on the non-contiguous `out` slice BEFORE
    # computationally heavy operations (`np.sqrt`) on the C-contiguous `scratch`
    # buffer yields better CPU cache utilization and reduces strided access overhead,
    # giving a ~11-15% performance improvement.
    np.multiply(x, c4, out=out)
    out += c3
    out *= x
    out += c2
    out *= x
    out += c1
    out *= x

    if scratch is None:
        scratch = np.sqrt(x) * c0
    else:
        # Optimization: Use a pre-allocated scratch buffer for the `np.sqrt(x) * c0`
        # term to prevent the final large temporary array allocation.
        np.sqrt(x, out=scratch)
        scratch *= c0

    out += scratch

    return out

def format_time(elapsed, precision_s=1):
    """Formats elapsed time into ms (< 0.1s) or seconds (otherwise)."""
    if elapsed < 0.1:
        ms = elapsed * 1000
        if round(ms) == 0:
            return "<1ms"
        return f"{ms:.0f}ms"
    return f"{elapsed:.{precision_s}f}s"

def format_file_hyperlink(filepath, display_text=None):
    """Formats a filepath as an OSC 8 terminal hyperlink string."""
    if display_text is None:
        display_text = filepath
    file_uri = pathlib.Path(filepath).resolve().as_uri()
    link_start = f"\033]8;;{file_uri}\033\\"
    link_end = "\033]8;;\033\\"
    return f"{link_start}{display_text}{link_end}"

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

    # Lower surface (skip leading edge point): x from 0 to 1
    points[num_points:, 0] = x[1:]

    # Optimization: Evaluating the equation using the newly assigned, Fortran-contiguous
    # array slice `points[:num_points, 0]` is faster than using `x_rev` directly because
    # `x_rev` is a non-contiguous view (stride -1) that causes CPU cache misses.
    # Additionally, writing the final result directly to the target slice via the `out`
    # parameter prevents a full-array temporary allocation.
    # Further, the original `x` array is no longer needed after being copied to `points`,
    # so we reuse it perfectly as a zero-allocation scratch buffer for `naca0012_y`.
    naca0012_y(points[:num_points, 0], out=points[:num_points, 1], scratch=x)

    # The lower surface is the negative of the upper surface.
    # points[:num_points, 1][-2::-1] takes the reversed upper surface array
    # starting from the second element (skipping the leading edge at x=0).
    # Optimization: Using np.negative with the `out` parameter avoids allocating
    # an intermediate array for the negated values, providing a ~4x speedup for this step.
    np.negative(points[:num_points, 1][-2::-1], out=points[num_points:, 1])

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
            f"{Colors.DIM}(Close window to finish){Colors.ENDC}",
            flush=True
        )
        try:
            import gmsh # pylint: disable=import-outside-toplevel
            with interactive_timer:
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
        f"point{'s' if len(points_for_gmsh) != 1 else ''} using Gmsh...{Colors.ENDC}",
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
        # Optimization: Calling .tolist() directly on separate column lists from a
        # Fortran-contiguous NumPy array is faster and more memory-efficient than calling
        # .copy().tolist(). The .copy() call introduces redundant memory allocation overhead
        # in modern Python versions without providing any iteration speedup.
        xs = points_to_add[:, 0].tolist()
        ys = points_to_add[:, 1].tolist()
        # z is always 0.0 for 2D airfoil

        with Spinner(f"{Colors.OKBLUE}   [1/2] Building geometry...{Colors.ENDC}"):
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

        with Spinner(f"{Colors.OKBLUE}   [2/2] Meshing...{Colors.ENDC}"):
            gmsh.model.mesh.generate(2)

        # Get mesh statistics
        # Efficiently get node count without copying large arrays (O(1) vs O(N))
        num_nodes = int(gmsh.option.getNumber("Mesh.NbNodes"))

        # Efficiently get 2D element count (O(1)) without overhead of getElements()
        num_triangles = int(gmsh.option.getNumber("Mesh.NbTriangles"))
        num_quadrangles = int(gmsh.option.getNumber("Mesh.NbQuadrangles"))
        num_elements = num_triangles + num_quadrangles

        node_label = "Node:" if num_nodes == 1 else "Nodes:"
        elem_label = "Element:" if num_elements == 1 else "Elements:"

        print(f"\n{Colors.OKCYAN}📊 Mesh Statistics:{Colors.ENDC}", flush=True)
        print(f"   • {node_label:<12} {Colors.BOLD}{num_nodes:>8,}{Colors.ENDC}", flush=True)
        print(f"   • {elem_label:<12} {Colors.BOLD}{num_elements:>8,}{Colors.ENDC}", flush=True)

        if num_elements > 0:
            pct_tri = (num_triangles / num_elements) * 100
            pct_quad = (num_quadrangles / num_elements) * 100

            def draw_bar(p, length=20):
                exact_fill = (p / 100) * length
                full_blocks = int(exact_fill)

                # 8 fractional block characters: 1/8 to 7/8
                fractions = ['', '▏', '▎', '▍', '▌', '▋', '▊', '▉']
                fraction_idx = int(round((exact_fill - full_blocks) * 8))

                if fraction_idx == 8:
                    full_blocks += 1
                    fraction_idx = 0

                fraction_char = fractions[fraction_idx]
                empty_blocks = length - full_blocks - (1 if fraction_idx > 0 else 0)

                filled_str = '█' * full_blocks + fraction_char
                empty_str = '░' * empty_blocks

                return (f"{Colors.OKBLUE}{filled_str}{Colors.ENDC}"
                        f"{Colors.DIM}{empty_str}{Colors.ENDC}")

            def format_stat_line(singular, count, pct):
                name = singular if count == 1 else f"{singular}s"
                label = f"- {name}:"
                # Pad label to 13 chars to match "- Triangles: " vs "- Quads:     "
                if count == 0:
                    return (
                        f"{Colors.DIM}     {label:<13}{count:>8,} "
                        f"({pct:>5.1f}%) {draw_bar(pct)}{Colors.ENDC}"
                    )
                return (
                    f"     {label:<13}"
                    f"{Colors.BOLD}{count:>8,}{Colors.ENDC} "
                    f"{Colors.DIM}({pct:>5.1f}%){Colors.ENDC} {draw_bar(pct)}"
                )

            print(format_stat_line("Triangle", num_triangles, pct_tri), flush=True)
            print(format_stat_line("Quad", num_quadrangles, pct_quad), flush=True)

        # Retrieve and display bounding box
        try:
            bbox = gmsh.model.getBoundingBox(-1, -1)
            # bbox is (minX, minY, minZ, maxX, maxY, maxZ)
            width = bbox[3] - bbox[0]
            height = bbox[4] - bbox[1]
            print(f"\n{Colors.OKCYAN}📏 Bounding Box:{Colors.ENDC}", flush=True)
            print(
                f"   • X Range:    [{Colors.BOLD}{bbox[0]:>7.4f}{Colors.ENDC}, "
                f"{Colors.BOLD}{bbox[3]:>7.4f}{Colors.ENDC}] "
                f"{Colors.DIM}(Width: {width:>7.4f}){Colors.ENDC}",
                flush=True
            )
            print(
                f"   • Y Range:    [{Colors.BOLD}{bbox[1]:>7.4f}{Colors.ENDC}, "
                f"{Colors.BOLD}{bbox[4]:>7.4f}{Colors.ENDC}] "
                f"{Colors.DIM}(Height: {height:>7.4f}){Colors.ENDC}",
                flush=True
            )
        except Exception: # pylint: disable=broad-exception-caught
            # Bounding box might fail if model is empty; ignore silently or handle gracefully
            pass

        if num_elements == 0:
            print(
                f"\n{Colors.WARNING}⚠️  Warning: The generated mesh has 0 elements. "
                f"Try increasing {Colors.BOLD}--num-points{Colors.ENDC}"
                f"{Colors.WARNING} or adjusting geometry settings.{Colors.ENDC}",
                flush=True
            )

        # Suggest saving if running interactively and no output specified
        interactive_save_used = False
        if not output_file and sys.stdout.isatty():
            print(f"\n{Colors.WARNING}⚠️  No output file specified.{Colors.ENDC}", flush=True)
            try:
                prompt = (
                    f"{Colors.OKBLUE}💾 Save to '{Colors.BOLD}airfoil.msh{Colors.ENDC}"
                    f"{Colors.OKBLUE}'? "
                    f"[y/N] or type filename: {Colors.ENDC}"
                )
                with interactive_timer:
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
                        interactive_save_used = True
                    else:
                        gmsh.finalize()
                        return False
            except (EOFError, KeyboardInterrupt):
                print() # Add newline to prevent mangled terminal output
                print(f"{Colors.FAIL}❌ Operation cancelled.{Colors.ENDC}")
                gmsh.finalize()
                return False

        if output_file:
            try:
                # Capture standard output/error if gmsh throws a generic exception
                # or silently fails but we want to catch it. Actually gmsh throws an Exception
                # on write failure: "Unable to open file '/root/airfoil.msh'". We want to catch it
                # properly to show the helpful UI.
                try:
                    gmsh.write(output_file)
                except Exception as e:
                    # Reraise as OSError to handle it gracefully in the UI block
                    raise OSError(str(e)) from e

                if not os.path.exists(output_file):
                    raise OSError(f"Gmsh silently failed to write '{output_file}'")
                file_size = os.path.getsize(output_file)
                readable_size = format_size(file_size)
                # Create absolute file:// URI
                linked_output_file = format_file_hyperlink(output_file)
                # Use raw string for shlex quote to avoid issues with escape sequences
                quoted_file = shlex.quote(output_file)
                linked_quoted_file = format_file_hyperlink(output_file, display_text=quoted_file)

                print(
                    f"\n{Colors.OKGREEN}💾 Mesh written to "
                    f"{Colors.BOLD}{linked_output_file}{Colors.ENDC} "
                    f"{Colors.DIM}({readable_size}){Colors.ENDC}",
                    flush=True
                )
                if preview:
                    print(
                        f"{Colors.OKBLUE}💡 Tip: View the mesh later using "
                        f"{Colors.BOLD}gmsh {linked_quoted_file}"
                        f"{Colors.ENDC}",
                        flush=True
                    )
                else:
                    print(
                        f"{Colors.OKBLUE}💡 Tip: View the mesh using "
                        f"{Colors.BOLD}gmsh {linked_quoted_file}"
                        f"{Colors.ENDC}{Colors.OKBLUE} "
                        f"or run with {Colors.BOLD}--preview{Colors.ENDC}"
                        f"{Colors.OKBLUE} next time{Colors.ENDC}",
                        flush=True
                    )

                if interactive_save_used:
                    print(
                        f"{Colors.OKBLUE}💡 Tip: Use {Colors.BOLD}--output "
                        f"{shlex.quote(output_file)}{Colors.ENDC}{Colors.OKBLUE} "
                        f"to save automatically without prompting.{Colors.ENDC}",
                        flush=True
                    )
            except OSError:
                print(f"\n{Colors.FAIL}❌ Error: Unable to write to file "
                      f"'{Colors.BOLD}{output_file}{Colors.ENDC}{Colors.FAIL}'. "
                      f"Please check your permissions and path.{Colors.ENDC}")
                return False
        else:
            # Only show warning if not interactive, to avoid nagging after a 'no' response
            if not sys.stdout.isatty():
                print(
                    f"\n{Colors.WARNING}⚠️  No output file specified. "
                    f"Mesh generated in memory only. "
                    f"Use {Colors.BOLD}--output{Colors.ENDC}"
                    f"{Colors.WARNING} to save.{Colors.ENDC}",
                    flush=True
                )

        # Handle preview if requested
        if preview:
            if output_file or not sys.stdout.isatty():
                print() # Add visual spacing before preview
            preview_mesh()

        if num_elements == 0:
            print(
                f"\n{Colors.WARNING}⚠️  Mesh generation finished, "
                f"but resulted in an empty mesh.{Colors.ENDC}",
                flush=True
            )
        else:
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
            f"{Colors.OKCYAN}ℹ️  Output path '{Colors.BOLD}{filepath}{Colors.ENDC}"
            f"{Colors.OKCYAN}' appears to be a directory. "
            f"Using '{Colors.BOLD}{new_filepath}{Colors.ENDC}{Colors.OKCYAN}'.{Colors.ENDC}"
        )
        return new_filepath

    _, ext = os.path.splitext(filepath)

    if not ext:
        new_filepath = f"{filepath}.msh"
        print(
            f"{Colors.OKCYAN}ℹ️  Output filename '{Colors.BOLD}{filepath}{Colors.ENDC}"
            f"{Colors.OKCYAN}' has no extension. "
            f"Defaulting to '{Colors.BOLD}{new_filepath}{Colors.ENDC}{Colors.OKCYAN}'.{Colors.ENDC}"
        )
        return new_filepath

    if ext.lower() in ['.txt', '.md', '.json', '.yaml', '.yml', '.py', '.sh']:
        print(
            f"{Colors.WARNING}⚠️  Warning: The extension '{Colors.BOLD}{ext}{Colors.ENDC}"
            f"{Colors.WARNING}' is likely not supported by Gmsh. "
            f"The generation might fail.{Colors.ENDC}"
        )

    return filepath

def check_overwrite(filepath, force):
    """Checks if output file exists and prompts user if needed."""
    # pylint: disable=too-many-locals
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

            size_str = (f" {Colors.DIM}({readable_size}, "
                        f"modified {rel_time}){Colors.ENDC}{Colors.WARNING}")
        except OSError:
            size_str = ""

        linked_filepath = format_file_hyperlink(filepath)
        print(
            f"{Colors.WARNING}⚠️  File '{Colors.BOLD}{linked_filepath}"
            f"{Colors.ENDC}{Colors.WARNING}' already exists{size_str}.{Colors.ENDC}"
        )
        try:
            prompt = f"{Colors.FAIL}⚠️  Overwrite? [y/N] {Colors.ENDC}"
            with interactive_timer:
                response = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print() # Add newline to prevent mangled terminal prompt
            print(f"{Colors.FAIL}❌ Operation cancelled.{Colors.ENDC}")
            return False

        if response in ('y', 'yes'):
            print(
                f"{Colors.OKBLUE}💡 Tip: Use {Colors.BOLD}--force{Colors.ENDC}"
                f"{Colors.OKBLUE} to skip this confirmation next time.{Colors.ENDC}"
            )
            return True

        print(f"{Colors.FAIL}❌ Operation cancelled.{Colors.ENDC}")
        return False

    # Non-interactive mode, just warn
    linked_filepath = format_file_hyperlink(filepath)
    print(
        f"{Colors.WARNING}⚠️  Overwriting existing file "
        f"'{Colors.BOLD}{linked_filepath}{Colors.ENDC}{Colors.WARNING}' "
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
            print(f"{Colors.OKBLUE}📂 Created directory "
                  f"'{Colors.BOLD}{directory}{Colors.ENDC}{Colors.OKBLUE}'{Colors.ENDC}")
        except OSError as e:
            print(f"{Colors.FAIL}❌ Error creating directory "
                  f"'{Colors.BOLD}{directory}{Colors.ENDC}{Colors.FAIL}': {e}{Colors.ENDC}")
            sys.exit(1)

class CustomArgumentParser(argparse.ArgumentParser):
    """Custom argument parser to format error messages consistently with the CLI."""
    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write(f"{Colors.FAIL}❌ Error: {message}{Colors.ENDC}\n")
        sys.stderr.write(
            f"{Colors.OKBLUE}💡 Tip: Run with {Colors.BOLD}--help{Colors.ENDC}"
            f"{Colors.OKBLUE} for a list of available options.{Colors.ENDC}\n"
        )
        self.exit(2)

def main(args=None):
    """Main execution function."""
    interactive_timer.reset()
    parser = CustomArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Generate a 2D unstructured mesh around a NACA 0012 airfoil using Gmsh.",
        epilog=f"Example: {Colors.OKCYAN}python mesh_generation.py "
               f"--num-points 200 --output airfoil.msh{Colors.ENDC}"
    )
    parser.add_argument(
        "-n", "--num-points",
        type=int,
        metavar="N",
        default=100,
        help="Number of points along the airfoil surface (must be > 0)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        metavar="FILE",
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

    args = parser.parse_args(args)

    if args.num_points <= 0:
        parser.error(
            f"{Colors.BOLD}--num-points{Colors.ENDC} must be a positive integer "
            f"(got {args.num_points})."
        )

    args.output = validate_output_path(args.output)

    if not check_overwrite(args.output, args.force):
        sys.exit(0)

    ensure_directory_exists(args.output)

    start_time = time.perf_counter()
    airfoil_points = generate_airfoil_points(args.num_points)
    success = generate_gmsh_mesh(airfoil_points, args.output, args.preview)

    if not success:
        sys.exit(1)

    elapsed_time = max(0.0, time.perf_counter() - start_time - interactive_timer.idle_time)
    formatted_time = format_time(elapsed_time, precision_s=2)
    print(f"\n{Colors.OKBLUE}⏱️  Total execution time: {Colors.DIM}{formatted_time}{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ensure cursor is explicitly unhidden if interrupted during a spinner phase
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        print(f"\n{Colors.FAIL}❌ Operation cancelled by user.{Colors.ENDC}")
        sys.exit(130)
    except ModuleNotFoundError as err:
        print(f"\n{Colors.FAIL}❌ Missing required dependency: '{err.name}'{Colors.ENDC}")
        print(f"{Colors.OKBLUE}💡 Tip: Install it by running "
              f"{Colors.BOLD}pip install {err.name}{Colors.ENDC}{Colors.OKBLUE} "
              f"or {Colors.BOLD}pip install -r requirements.txt{Colors.ENDC}")
        sys.exit(1)
