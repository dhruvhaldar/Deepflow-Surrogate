## 2024-05-23 - Gmsh Python API Loop Performance
**Learning:** Iterating over a native Python list of coordinates is measurably faster (~20% on the loop) than iterating over a NumPy array when calling `gmsh.model.geo.addPoint`, likely due to avoiding NumPy scalar conversion overhead per call.
**Action:** Always convert NumPy arrays to Python lists (`.tolist()`) before iterating in tight loops that call Gmsh API functions expecting standard Python types.
