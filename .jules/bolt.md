## 2024-05-23 - Gmsh Python API Loop Performance
**Learning:** Iterating over a native Python list of coordinates is measurably faster (~20% on the loop) than iterating over a NumPy array when calling `gmsh.model.geo.addPoint`, likely due to avoiding NumPy scalar conversion overhead per call.
**Action:** Always convert NumPy arrays to Python lists (`.tolist()`) before iterating in tight loops that call Gmsh API functions expecting standard Python types.

## 2025-02-14 - Gmsh Node Count Optimization
**Learning:** `gmsh.model.mesh.getNodes()` returns complete arrays of coordinates and tags, which is an O(N) operation. For simply counting nodes, `gmsh.option.getNumber("Mesh.NbNodes")` is an O(1) alternative that avoids all data marshalling overhead, providing a ~20x speedup for this check on small meshes (and scaling better).
**Action:** Use `gmsh.option.getNumber("Mesh.NbNodes")` when only the node count is needed, instead of retrieving the full mesh data.

## 2025-02-14 - Gmsh Element Count Optimization
**Learning:** `gmsh.model.mesh.getElements()` is an O(N) operation that returns all mesh entities (including boundary lines and points). For reporting 2D mesh statistics, summing `gmsh.option.getNumber("Mesh.NbTriangles")` and `"Mesh.NbQuadrangles"` is O(1), avoids large array allocations, and correctly reflects the number of computational cells.
**Action:** Use `gmsh.option.getNumber` for element counting when only statistics are needed, avoiding `getElements()`.

## 2025-05-23 - NumPy Array Optimization
**Learning:** For generating point clouds, allocating the final NumPy array once (e.g., `np.zeros`) and assigning values via slicing is significantly faster (2-3x) than building intermediate arrays and combining them with `np.concatenate` or `np.column_stack`.
**Action:** Use pre-allocation for constructing large arrays instead of concatenation functions.

## 2025-05-23 - Horner's Method for Polynomials
**Learning:** Using Horner's method for polynomial evaluation reduces the number of floating-point operations and, more importantly in NumPy, avoids the creation of multiple temporary arrays for intermediate power terms (`x**2`, `x**3`), yielding a ~23% speedup.
**Action:** Rewrite high-order polynomials using nested multiplication (Horner's method) in performance-critical code.

## 2025-05-23 - List Flattening for Loop Performance
**Learning:** When passing large arrays of coordinates to a C-extension loop (like `gmsh.model.geo.addPoint`), flattening the array to a single Python list of floats (`ravel().tolist()`) and iterating with `zip` chunking is ~2x faster than iterating over a nested list of lists (`tolist()`), due to reduced object creation overhead.
**Action:** Use `ravel().tolist()` and `zip(it, it, it)` for iterating over coordinate arrays in tight loops.

## 2025-05-24 - NumPy Negation Optimization
**Learning:** Using `np.negative(arr, out=dest)` is significantly faster (~50x for large arrays, ~25% for small ones) than `dest[:] = -arr` because it performs the operation in-place without allocating a temporary intermediate array for the result of `-arr`.
**Action:** Use `np.negative(src, out=dest)` when negating arrays into a pre-allocated buffer.

## 2025-05-24 - Gmsh Binary Output Size
**Learning:** Enabling binary output (`Mesh.Binary=1`) in Gmsh 4.15 increases file size for very small 2D meshes (~14KB vs ~9KB for ASCII) due to binary format overhead, though it scales better for large meshes. For small debugging meshes, ASCII might be preferable.
**Action:** Default to ASCII for small/debugging meshes unless performance or large data size dictates otherwise.

## 2025-05-24 - Threaded Spinner Optimization
**Learning:** Using `threading.Event().wait(timeout)` instead of `time.sleep(timeout)` in a threaded spinner loop allows immediate interruption via `set()`. This eliminates the latency (e.g., ~100ms) caused by waiting for the sleep to finish during thread join, which is critical for short-lived tasks.
**Action:** Always use `threading.Event` for cancellation and timing in worker threads to ensure responsive exits.

## 2024-05-24 - [Micro-Optimization: Polynomial Evaluation & API Caching]
**Learning:** In high-frequency numerical code (like `naca0012_y`), folding constant scaling factors into polynomial coefficients can save significant memory allocation and array traversals (O(N) operations). Also, caching `gmsh` API function lookups before tight loops provides a small but free performance boost.
**Action:** Look for `result = scalar * (poly_eval)` patterns and distribute the scalar into the coefficients. Cache repeated dot-lookups in critical loops.

## 2025-05-25 - [Memory Optimization: Separate Coordinate Lists]
**Learning:** When passing coordinates to `gmsh.model.geo.addPoint`, creating separate lists for `x` and `y` (e.g., `points[:, 0].tolist()`) and using `zip(xs, ys)` is ~1.5x faster and uses ~33% less memory than flattening the entire array (`ravel().tolist()`) and using `zip(it, it, it)`, especially when one coordinate (Z) is constant and can be passed as a literal.
**Action:** Avoid creating full 3D coordinate lists if one dimension is constant; pass it as a literal in the loop.

## 2025-05-25 - Gmsh AutoCoherence Performance
**Learning:** Disabling `Geometry.AutoCoherence` (`gmsh.option.setNumber("Geometry.AutoCoherence", 0)`) when adding a large number of known-unique points (e.g. 200k) improves `addPoint` loop performance by ~6-10% by skipping duplicate entity checks. Also, the OpenCASCADE kernel (`model.occ`) is significantly slower (~18x) than the built-in `geo` kernel for adding large numbers of points individually in a Python loop.
**Action:** Disable `Geometry.AutoCoherence` when programmatically generating geometry where point uniqueness is already guaranteed.
