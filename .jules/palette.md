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
