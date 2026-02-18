## 2024-05-23 - Gmsh Python API Loop Performance
**Learning:** Iterating over a native Python list of coordinates is measurably faster (~20% on the loop) than iterating over a NumPy array when calling `gmsh.model.geo.addPoint`, likely due to avoiding NumPy scalar conversion overhead per call.
**Action:** Always convert NumPy arrays to Python lists (`.tolist()`) before iterating in tight loops that call Gmsh API functions expecting standard Python types.

## 2025-02-14 - Gmsh Node Count Optimization
**Learning:** `gmsh.model.mesh.getNodes()` returns complete arrays of coordinates and tags, which is an O(N) operation. For simply counting nodes, `gmsh.option.getNumber("Mesh.NbNodes")` is an O(1) alternative that avoids all data marshalling overhead, providing a ~20x speedup for this check on small meshes (and scaling better).
**Action:** Use `gmsh.option.getNumber("Mesh.NbNodes")` when only the node count is needed, instead of retrieving the full mesh data.
