## 2024-05-23 - Gmsh Python API Loop Performance
**Learning:** Iterating over a native Python list of coordinates is measurably faster (~20% on the loop) than iterating over a NumPy array when calling `gmsh.model.geo.addPoint`, likely due to avoiding NumPy scalar conversion overhead per call.
**Action:** Always convert NumPy arrays to Python lists (`.tolist()`) before iterating in tight loops that call Gmsh API functions expecting standard Python types.

## 2025-05-27 - Gmsh Mesh Statistics Performance
**Learning:** `gmsh.model.mesh.getNodes()` and `gmsh.model.mesh.getElements()` incur significant overhead (O(N) data transfer) when only counts are needed. For large meshes, this can take hundreds of milliseconds. `gmsh.option.getNumber("Mesh.NbNodes")` and `gmsh.option.getNumber("Mesh.NbTriangles")` provide O(1) access. Also, `getElements()` includes boundary points and lines, inflating the "element" count compared to the number of mesh cells.
**Action:** Use `gmsh.option.getNumber` for retrieving mesh statistics to avoid memory allocation and data transfer overhead. Prefer specific counters (like `Mesh.NbTriangles`) for clearer reporting.
