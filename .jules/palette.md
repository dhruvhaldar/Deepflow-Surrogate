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
