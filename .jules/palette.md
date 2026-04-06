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
## 2025-02-28 - Customizing Argparse Error Formatting
**Learning:** Standard argparse errors in Python CLIs lack visual integration with custom styled application outputs, appearing jarring to users when other errors are styled cleanly.
**Action:** Subclass `argparse.ArgumentParser` and override the `error` method to apply standard project styling (e.g., ANSI colors, emojis) ensuring a cohesive Developer Experience.
## 2023-11-20 - Smooth CLI Progress Bars
**Learning:** Smooth Unicode progress bars with fractional block characters (▏, ▎, ▍, ▌, ▋, ▊, ▉) provide significantly better visual granularity than integer-based blocks, improving UI polish and precision in CLI outputs.
**Action:** When implementing or updating CLI progress bars, utilize fractional block rendering instead of simple integer arithmetic to enhance the quality of the visual feedback.

## 2024-05-20 - Enhance CLI visual scannability for commands
**Learning:** `shlex.quote()` conditionally drops quotes for safe strings, breaking the visual consistency when providing file paths in instruction tips.
**Action:** When suggesting commands in CLI output, wrap file paths in literal single quotes (`'{file_path}'`) instead of `shlex.quote()` to ensure consistent visual parsing of the instruction.

## 2024-05-20 - Execution Time Visual Noise
**Learning:** Displaying high-precision execution times (e.g., 4 decimal places like `12.4171s`) in user-facing CLI tools creates unnecessary visual noise and reduces scannability, as sub-millisecond precision is irrelevant outside of dedicated benchmarking contexts.
**Action:** Round overall CLI execution times to 1 or 2 decimal places (e.g., `12.42s`) to improve readability and visual polish.

## 2026-03-15 - Actionable Tips in Argument Parsing Errors
**Learning:** Standard argparse error messages merely print the usage text without an actionable tip, leaving users at a dead end and increasing friction for feature discovery or help menu access.
**Action:** Always append an actionable tip (e.g., 'Run with --help') to custom CLI error handlers to guide users directly back to the command documentation.
## 2024-05-27 - CLI Parameter Validation UX
**Learning:** For Python CLI tools using `argparse`, manually printing validation errors and calling `sys.exit(1)` bypasses the standard error handling, missing out on automatic usage instructions and standard `stderr` routing.
**Action:** Always use `parser.error("message")` for argument validation failures after `parse_args()` to ensure consistent CLI UX, automatic usage hints, and correct exit codes.

## 2026-03-16 - Context-Aware Empty State Success
**Learning:** When an operation technically succeeds but yields an empty or useless result (like a 0-element mesh), displaying a generic '✅ Success' message confuses users. The final status indicator should reflect the qualitative outcome, not just the technical exit code.
**Action:** Always conditionally format final success messages to reflect empty or partial states (e.g., using a warning state `⚠️ Finished with 0 elements`) instead of a blanket success.
## 2026-03-17 - Graceful Degradation of Text-Based UI
**Learning:** Completely hiding text-based visual indicators (like spinners) just because ANSI colors are disabled (e.g., `NO_COLOR=1`) removes valuable feedback for users in non-colored but interactive environments.
**Action:** Ensure CLI UI elements degrade gracefully when colors are disabled by continuing to rely on standard Unicode characters to convey information without color wrappers.

## 2026-03-18 - Execution Time Includes User Idle Time
**Learning:** Including the time a user spends idling on interactive prompts (like `input()`) or GUI viewers (like `gmsh.fltk.run()`) inside the CLI "Total execution time" makes the metric wildly inaccurate and useless for judging actual program performance, confusing users about the tool's speed.
**Action:** Use a context manager to track the duration of all blocking interactive calls (`input`, GUI viewers) and explicitly subtract this `idle_time` from the final execution elapsed time so the metric strictly reflects program execution speed.

## 2026-03-20 - Clickable File Paths in CLI
**Learning:** Modern terminal emulators support OSC 8 escape sequences to create clickable hyperlinks, which significantly reduces copy-paste friction for users who want to view generated files.
**Action:** Use OSC 8 (`\033]8;;{URI}\033\\`) combined with `pathlib.Path(file).resolve().as_uri()` to make file paths clickable in CLI success or tip messages.

## 2026-03-23 - Reactive Flag Discovery
**Learning:** Users often miss automation flags (like `--output` or `--force`) in help menus. Prompting them interactively without highlighting the relevant CLI flags forces them to repeatedly use the slower, manual fallback without learning the faster method.
**Action:** When a user completes a manual interactive flow (like typing a filename or confirming an overwrite), append a context-aware tip suggesting the exact flag they could use next time to skip that prompt entirely.

## 2026-03-24 - Dim Zero-Value Statistics
**Learning:** When displaying structured tabular data (like Mesh Statistics) in the CLI, rows containing a zero value (e.g., 0 Quads) can create visual noise that competes with the actual data points present.
**Action:** Apply dim ANSI styling (`Colors.DIM`) to the entire row of zero-value metrics to visually deprioritize them, allowing the non-zero data to stand out more clearly.

## 2026-03-25 - Robust Input Interrupts
**Learning:** Python's `input()` will raise a `KeyboardInterrupt` if the user hits Ctrl+C, but typical simple `try...except EOFError` blocks (for Ctrl+D) miss this, leading to unexpected stack traces dumped into the user's terminal on an aborted prompt.
**Action:** When wrapping `input()` calls in CLI applications, explicitly catch both `EOFError` and `KeyboardInterrupt` as a single tuple `except (EOFError, KeyboardInterrupt):` to ensure all standard terminal interrupt signals result in a clean exit message.
## 2024-05-19 - Dynamic Noun Pluralization in CLI Outputs
**Learning:** Hardcoded plural nouns in CLI statistics (e.g., "Nodes: 1") look unpolished and grammatically incorrect when the count is exactly one.
**Action:** Dynamically pluralize nouns based on their count variables (e.g., "Node: 1" vs "Nodes: 2") while maintaining fixed-width string formatting to preserve exact vertical alignment of the accompanying numerical data.

## 2024-06-25 - Clickable File Paths in Destructive Prompts
**Learning:** Providing an explicit file path in a warning (e.g., "Overwriting existing file 'abc.msh'") is helpful, but if the user wants to quickly check the file before confirming, they have to manually find it. Adding an OSC 8 terminal hyperlink directly into the prompt drastically reduces friction, allowing them to instantly view the target file.
**Action:** Apply OSC 8 terminal hyperlinks (`\033]8;;{URI}\033\\`) to file paths within destructive or warning CLI prompts (like overwrite confirmations) to improve the Developer Experience.
## 2026-03-26 - Graceful External Write Error Handling
**Learning:** External libraries (like Gmsh) often silently suppress standard file I/O exceptions or throw generic library exceptions when failing to write to a path (e.g., due to permissions or an invalid directory). If unhandled, this causes subsequent `os.path.getsize()` calls to crash with a confusing `FileNotFoundError` stack trace.
**Action:** Always wrap external library file write operations in `try...except Exception` blocks, specifically checking for file existence afterward, and reraise as a standard `OSError` to allow the CLI to render a consistent, styled error message about permissions.

## 2026-03-27 - Cancel Operation Friction
**Learning:** Users who trigger interactive prompts (like save destinations or overwrite confirmations) often experience friction or anxiety if they decide to cancel, because it's not clear whether standard shell interrupt combinations (like `Ctrl+C`) are caught safely or will crash the application.
**Action:** Always append an explicit cancellation hint (e.g., `(Ctrl+C to cancel)`) formatted with dim styling (`Colors.DIM`) to the end of blocking interactive prompts to reassure users and improve overall CLI UX.
