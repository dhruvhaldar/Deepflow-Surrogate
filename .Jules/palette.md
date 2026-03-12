## 2024-05-24 - Enhance CLI Numerical Data Readability
**Learning:** Wrapping numerical values in structured sections (like Mesh Statistics or Bounding Boxes) in `Colors.BOLD` improves visual hierarchy and scannability against their labels. This greatly enhances CLI UX because users can quickly scan key figures visually separated from normal-weighted label text.
**Action:** When printing structured data in a CLI, always emphasize the numeric output using ANSI bold formatting to make it stand out from descriptive text.

## 2025-03-12 - Prevent Mangled Terminal on EOF
**Learning:** When using `input()` for CLI prompts, users pressing `Ctrl+D` (EOF) immediately abort the input without printing a newline. If the script subsequently prints messages or exits, those messages or the user's terminal shell prompt will be printed on the same line as the aborted prompt, resulting in a mangled, visually confusing UX.
**Action:** Always wrap `input()` in a `try...except EOFError` block and explicitly `print()` an empty newline to gracefully reset the cursor before proceeding or exiting.
