## 2025-05-25 - Lazy Import for CLI Startup
**Learning:** Importing heavy libraries like `numpy` and `gmsh` at the module level adds significant overhead (~0.13s for `numpy` alone) to CLI startup time, affecting responsiveness for simple commands like `--help`.
**Action:** Use lazy imports (import inside functions) for heavy dependencies in CLI tools to keep the interface snappy.

## 2026-02-27 - NumPy Contiguous Memory vs Allocation
**Learning:** Trying to save memory allocations by using columns of a 2D array as scratch buffers (e.g., `points[:, 1]`) for intensive math operations is significantly slower (~65% overhead) than allocating fresh 1D arrays (`np.empty_like`). The memory non-contiguity (stride > 1) causes cache misses that far outweigh the cost of allocating temporary arrays.
**Action:** Prioritize contiguous memory access for vectorized NumPy math operations, even if it requires temporary 1D allocations.

## 2025-05-27 - Vectorized Math Evaluation vs Explicit Arrays
**Learning:** We previously believed that manually orchestrating in-place modifications (`out.fill`, `*=`, `+=`) and using explicit buffer allocations (`np.empty_like`) avoided allocations and was thus faster. However, replacing it with a single vectorized math expression (`np.sqrt(x) * c0 + x * (c1 + x * (c2 + x * (c3 + x * c4)))`) and omitting manual buffers proved to be natively ~20% faster. NumPy's C-backend handles the intermediate evaluation of mathematical operators more efficiently than doing it explicitly from Python.
**Action:** Prefer writing single-line vectorized math expressions over managing explicit loops of `out.fill` and `+=` when dealing with relatively simple polynomials, as NumPy's internal evaluation is highly optimized.

## 2026-03-04 - NumPy Non-Contiguous Array to List Conversion
**Learning:** Extracting a column from a 2D Fortran-ordered array (e.g., `points[:, 0]`) into a Python list using `.tolist()` is surprisingly slow because iterating over a non-contiguous memory stride (stride > 1) to build Python objects is unoptimized. Calling `.copy()` first to force a contiguous 1D array before calling `.tolist()` is approximately 5x faster (e.g., dropping from ~0.25s to ~0.05s for 200k points) despite the extra memory allocation overhead.
**Action:** When converting non-contiguous NumPy slices (or columns from Fortran arrays) to Python lists, always insert `.copy()` before `.tolist()` to ensure the conversion operates on contiguous memory layout.

## 2026-03-05 - NumPy Vectorized Math Hybrid Approach (SUPERSEDED)
**Learning:** We previously believed that a hybrid approach combining `np.sqrt(x)` and manual in-place evaluations was optimal. However, further testing revealed that a completely pure vectorized Horner expression (`np.sqrt(x) * c0 + x * (c1 + x * (c2 + x * (c3 + x * c4)))`) outperforms even the hybrid in-place logic by about ~25%.
**Action:** Trust NumPy's backend to optimize pure vectorized operations and avoid manual loop-unrolling and in-place buffer management for polynomials where possible.

## 2026-03-08 - np.zeros vs np.empty + Explicit Zeroing
**Learning:** We previously thought that using `np.empty()` and only zeroing the necessary slices (e.g., `points[:, 2] = 0.0`) was faster than `np.zeros()` to avoid unnecessary zero-filling. However, testing shows that `np.zeros()` is actually faster. This is because modern OS and NumPy use lazy zeroed memory pages (like `mmap` with `MAP_ANONYMOUS`), so allocating zeroed memory is nearly instant, while manually writing `0.0` triggers page faults and CPU cache traffic.
**Action:** Always prefer `np.zeros` over `np.empty` + manual zeroing for array initializations, even if only part of the array needs to be zero, as OS-level optimizations make `np.zeros` faster.
