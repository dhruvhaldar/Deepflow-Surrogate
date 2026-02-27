## 2025-05-25 - Lazy Import for CLI Startup
**Learning:** Importing heavy libraries like `numpy` and `gmsh` at the module level adds significant overhead (~0.13s for `numpy` alone) to CLI startup time, affecting responsiveness for simple commands like `--help`.
**Action:** Use lazy imports (import inside functions) for heavy dependencies in CLI tools to keep the interface snappy.
