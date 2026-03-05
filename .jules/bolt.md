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

## 2026-03-05 - NumPy Vectorized Math Hybrid Approach
**Learning:** While single-line vectorized math (`np.sqrt(x) * c0 + x * ...`) is typically faster than fully manual in-place loops (due to NumPy's C-backend efficiency), a hybrid partially in-place approach is even faster (~15-20%). Specifically, extracting the expensive `np.sqrt(x)` operation and executing it in-place first (`res = np.sqrt(x); res *= c0`) and then appending the rest of the expression (`res += x * ...`) hits a sweet spot. It optimizes intermediate array allocations while breaking apart the most expensive operations.
**Action:** When working with expensive math functions (like `np.sqrt`) combined with simpler polynomial evaluations in NumPy, extract the expensive operation into its own buffer and modify it in-place before accumulating the simpler parts.
