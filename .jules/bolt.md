## 2024-05-23 - Gmsh Python API Loop Performance
**Learning:** Iterating over a native Python list of coordinates is measurably faster (~20% on the loop) than iterating over a NumPy array when calling `gmsh.model.geo.addPoint`, likely due to avoiding NumPy scalar conversion overhead per call.
**Action:** Always convert NumPy arrays to Python lists (`.tolist()`) before iterating in tight loops that call Gmsh API functions expecting standard Python types.

## 2025-02-14 - Gmsh Node Count Optimization
**Learning:** `gmsh.model.mesh.getNodes()` returns complete arrays of coordinates and tags, which is an O(N) operation. For simply counting nodes, `gmsh.option.getNumber("Mesh.NbNodes")` is an O(1) alternative that avoids all data marshalling overhead, providing a ~20x speedup for this check on small meshes (and scaling better).
**Action:** Use `gmsh.option.getNumber("Mesh.NbNodes")` when only the node count is needed, instead of retrieving the full mesh data.

## 2025-02-14 - Gmsh Element Count Optimization
**Learning:** `gmsh.model.mesh.getElements()` is an O(N) operation that returns all mesh entities (including boundary lines/points). For reporting 2D mesh statistics, summing `gmsh.option.getNumber("Mesh.NbTriangles")` and `"Mesh.NbQuadrangles"` is O(1), avoids large array allocations, and correctly reflects the number of computational cells.
**Action:** Use `gmsh.option.getNumber` for element counting when only statistics are needed, avoiding `getElements()`.

## 2025-05-23 - NumPy Array Optimization
**Learning:** For generating point clouds, allocating the final NumPy array once (e.g., `np.zeros`) and assigning values via slicing is significantly faster (2-3x) than building intermediate arrays and combining them with `np.concatenate` or `np.column_stack`.
**Action:** Use pre-allocation for constructing large arrays instead of concatenation functions.

## 2025-05-23 - Horner's Method for Polynomials
**Learning:** Using Horner's method for polynomial evaluation reduces the number of floating-point operations and, more importantly in NumPy, avoids the creation of multiple temporary arrays for intermediate power terms (`x**2`, `x**3`), yielding a ~23% speedup.
**Action:** Rewrite high-order polynomials using nested multiplication (Horner's method) in performance-critical code.
