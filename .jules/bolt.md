## 2025-05-25 - Lazy Import for CLI Startup
**Learning:** Importing heavy libraries like `numpy` and `gmsh` at the module level adds significant overhead (~0.13s for `numpy` alone) to CLI startup time, affecting responsiveness for simple commands like `--help`.
**Action:** Use lazy imports (import inside functions) for heavy dependencies in CLI tools to keep the interface snappy.

## 2026-02-27 - NumPy Contiguous Memory vs Allocation
**Learning:** Trying to save memory allocations by using columns of a 2D array as scratch buffers (e.g., `points[:, 1]`) for intensive math operations is significantly slower (~65% overhead) than allocating fresh 1D arrays (`np.empty_like`). The memory non-contiguity (stride > 1) causes cache misses that far outweigh the cost of allocating temporary arrays.
**Action:** Prioritize contiguous memory access for vectorized NumPy math operations, even if it requires temporary 1D allocations.
