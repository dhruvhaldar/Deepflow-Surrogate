## 2024-05-24 - CLI Interaction Patterns
**Learning:** CLI interactive prompts in this project rely on strict case-sensitive matching (e.g., specific 'y' only) and lack visual emphasis for critical warnings, which increases user friction and error potential.
**Action:** Always implement case-insensitive input handling supporting standard synonyms ('yes', 'YES') and use ANSI colors to highlight destructive actions in CLI scripts.

## 2025-05-24 - CLI Spinner Behavior
**Learning:** CLI spinners that assume a TTY environment can disappear entirely in CI/CD logs or file redirections, leaving users with no feedback on long-running processes.
**Action:** Implement a dual-mode spinner: animated with cursor hiding (`\033[?25l`) for TTYs, and a single static print (e.g., "Processing...") for non-TTY environments.

## 2026-02-20 - CLI Interrupt Handling
**Learning:** Python CLI scripts dump ugly tracebacks on `KeyboardInterrupt` (Ctrl+C), which degrades perceived quality and can confuse non-technical users.
**Action:** Wrap the main execution logic in a `try...except KeyboardInterrupt` block at the entry point to catch the signal, print a clean "Operation cancelled" message, and exit with status code 130.

## 2026-02-24 - Persistent CLI Progress
**Learning:** CLI spinners that clear the line upon completion remove context, making it hard for users to review what steps were successful.
**Action:** Replace spinners with a persistent success (✅) or failure (❌) indicator upon completion to provide a clear history of actions.

## 2026-02-24 - Actionable CLI Success Messages
**Learning:** Users often complete a CLI task (e.g. generation) and immediately wonder "what next?", leading to friction in verification.
**Action:** Append a contextual "Tip" or next step (e.g. viewer command) to success messages to bridge the gap between creation and verification.

## 2026-02-25 - Non-TTY Spinner Completion Feedback
**Learning:** In non-interactive environments (CI/CD, logs), spinners that only print a start message ("Processing...") leave ambiguity about whether the step finished successfully or hung.
**Action:** Ensure non-TTY spinner fallbacks explicitly print a completion indicator (e.g., "Processing... ✅") to provide clear step verification in logs.

## 2026-02-26 - CLI Directory Output Handling
**Learning:** Users often provide directory paths (e.g. `dir/`) expecting the file to be placed inside, but standard filename validation logic may create hidden files (e.g. `dir/.msh`) or confusing names if not handled explicitly.
**Action:** Detect if output path is a directory (existing or trailing separator) and automatically append a sensible default filename (e.g. `dir/default.msh`).

## 2026-02-27 - Technical Statistics Formatting
**Learning:** Dense, single-line technical output (like node counts and bounding boxes) forces users to perform mental parsing and calculations, reducing the immediate utility of the tool.
**Action:** Format key statistics (e.g., mesh element counts, dimensions) into clear, multi-line indented blocks with pre-calculated derived values (e.g., width/height, percentages) to improve readability and decision-making speed.

## 2026-02-28 - Visual Data Representation in CLI
**Learning:** Purely numerical statistics (like percentages) in CLI output can be hard to scan quickly, slowing down user comprehension of data distribution.
**Action:** Augment numerical percentages with simple ASCII visual bars (e.g., `████░░`) to allow users to instantly grasp ratios and distributions at a glance.

## 2026-03-01 - Spinner Duration Context
**Learning:** Users running tools with multiple or long-running blocking operations often lack intuition about which steps are bottlenecks when only total execution time is shown at the end.
**Action:** Append the exact elapsed time (e.g., `(2.4s)`) alongside success/failure indicators when a CLI spinner completes, giving users immediate and granular performance context for each blocking step.

## 2026-03-02 - Destructive Action Feedback
**Learning:** Overwrite warnings that lack context about what is being overwritten, and lack visual emphasis for the destructive action, make users more likely to blindly confirm the action.
**Action:** Include the existing file size in the overwrite warning to provide context, and use a critical color (e.g. red/FAIL) for the confirmation prompt to force a cognitive pause.

## 2026-03-03 - CLI Feature Discovery
**Learning:** Users might miss existing CLI flags if they are only documented in the help menu, leading to suboptimal usage.
**Action:** Incorporate suggestions for useful flags (like `--preview`) into success or tip messages to improve feature discovery and UX.

## 2025-02-21 - Destructive Actions and Context
**Learning:** When prompting users to overwrite files, providing only the file size leaves ambiguity (e.g., "Is this my latest run or an old test?"). Adding relative modification time (e.g., "modified just now" or "modified 2 hours ago") provides crucial context that helps users confidently make destructive decisions.
**Action:** Always include relative modification time or explicit timestamps alongside file sizes in overwrite warnings or file deletion prompts to prevent accidental data loss.

## 2026-03-04 - Dependency Error UX
**Learning:** Python CLI scripts often dump large, intimidating stack traces when a lazy import fails due to a missing dependency, confusing users who aren't familiar with Python environments.
**Action:** Catch `ModuleNotFoundError` at the script's entry point (`__main__` block) to suppress the traceback and instead display a clean, color-coded error with an actionable tip (e.g., "pip install <module>").

## 2026-03-05 - Context-Aware CLI Suggestions
**Learning:** Suggesting next steps or flags (like `--preview`) that the user has already employed feels redundant and diminishes the perceived intelligence of the tool, causing users to ignore future tips.
**Action:** Always make CLI "Tip" messages context-aware by checking the flags and options the user has already provided, suppressing or adapting suggestions to avoid redundancy.

## 2026-03-06 - Dynamic Precision in Execution Times
**Learning:** Displaying extremely short execution times (e.g., < 0.1s) with fixed second-precision (like `0.0s`) can look buggy and hides the actual performance metrics from the user, reducing the perceived responsiveness of the tool.
**Action:** Implement dynamic time formatting for CLI outputs: switch to milliseconds (e.g., `45ms`) for times under 0.1s to provide accurate, non-zero feedback that feels more responsive.

## 2026-03-07 - CLI Visual Progress Bar Alignment
**Learning:** When adding visual elements like ASCII progress bars to CLI output, inconsistent widths in the preceding dynamic text (like counts or percentages) cause the bars to start at different horizontal positions, breaking the user's ability to easily compare them visually.
**Action:** Always use fixed-width formatters (e.g., `{count:<8,}` and `{percent:>5.1f}%`) for text preceding visual bars to ensure consistent alignment and immediate scannability.

## 2026-03-08 - Interactive Save Prompts Custom Input
**Learning:** Binary yes/no CLI prompts for saving files (e.g., "Save to 'default.msh'? [y/N]") force users to re-run the entire command if they want a different filename, increasing friction and time-to-value.
**Action:** Enhance interactive save prompts to accept custom strings directly (e.g., "[y/N] or type filename:"), automatically parsing non-binary responses as custom output paths.

## 2026-03-09 - Long-Running CLI Phase Feedback
**Learning:** During large mesh generations, the geometric construction and synchronization phases can take several seconds (or over 10 seconds for millions of points). Without an active spinner during this specific phase, the CLI appears to freeze, causing users to potentially interrupt the process prematurely.
**Action:** Always wrap long-running geometric construction loops (like `gmsh.model.geo.addPoint`) and `synchronize()` calls in an active `Spinner` to provide continuous visual feedback and reassure the user that the program is still working.

## 2026-03-10 - Zero-Value Time Feedback
**Learning:** Displaying `0ms` for extremely fast operations feels buggy or broken to users, as it implies the operation didn't happen or timing failed.
**Action:** When formatting execution times rounding down to zero, display `<1ms` instead of `0ms` to provide non-zero, responsive feedback that accurately reflects a fast operation.

## 2026-03-11 - Progress Bar Contrast
**Learning:** ASCII progress bars that use a single color for both filled ('█') and empty ('░') segments lack strong visual contrast, making it slightly harder to perceive the actual fill ratio at a quick glance in terminal environments.
**Action:** Use distinct color styles (like applying a 'dim' or subtle secondary color state) to the empty portions of progress bars to enhance contrast and improve immediate scannability.

## 2026-03-12 - Secondary Context Styling
**Learning:** CLI elements that provide secondary context, such as step durations or background metadata, can cause visual clutter if rendered with the same visual weight as primary status indicators. When success/failure indicators (`✅`/`❌`) share visual prominence with purely informational text, the user's eye has to work harder to extract the primary outcome.
**Action:** Apply distinct, subtle styling (like `\033[2m` or `Colors.DIM`) to secondary informational text (e.g., execution times in spinners) to establish a clear visual hierarchy, ensuring the primary success/failure state remains the immediate focal point while secondary data stays readable but recedes into the background.

## 2026-03-13 - Data Value Alignment
**Learning:** Dense technical output like multi-dimensional bounding boxes is difficult to read when numerical values have varying string lengths (e.g. `[0.0000, 1.0000]` vs `[-0.0600, 0.0600]`). The unaligned text prevents visual scanning of columns.
**Action:** Use right-aligned, fixed-width string formatting (e.g. `{value:>7.4f}`) for structured numerical outputs to ensure decimal points and brackets align perfectly across lines.

## 2026-03-13 - Command Distinctions in Text
**Learning:** Command line suggestions and arguments embedded within larger text blocks (e.g. "Tip: View the mesh using 'gmsh file.msh'") can blend in, causing users to miss the exact actionable copy.
**Action:** Always format actionable CLI inputs, commands, and flags with bold styling (`Colors.BOLD`) to lift them out of the surrounding narrative text and make copy-pasting easier.

## 2024-05-22 - Visual Hierarchy in CLI output
**Learning:** In CLI outputs, applying dimmed styling (e.g., `Colors.DIM`) to secondary context metadata (like file sizes, bounding box dimensions, and percentage values) significantly improves the visual hierarchy. It ensures that this supplementary information does not visually compete with the primary success/failure indicators or core data, making the output cleaner and easier to scan.
**Action:** Always use dimmed ANSI styling for secondary context metadata in CLI interfaces to establish a clear visual hierarchy and prevent visual clutter.

## 2026-03-14 - Copy-Paste Friction in CLI Tips
**Learning:** Surrounding CLI command suggestions (like tips) with literal single or double quotes creates friction because users who double-click to select or drag-select the command often accidentally include the quotes. Pasting this into a shell causes `command not found` errors.
**Action:** Never surround suggested commands in CLI output with literal string quotes. Instead, visually differentiate the command using bold ANSI styling (`Colors.BOLD`), and use `shlex.quote()` on file paths within the command to ensure they are safe for the shell if copy-pasted.
