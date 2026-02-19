## 2024-05-24 - CLI Interaction Patterns
**Learning:** CLI interactive prompts in this project rely on strict case-sensitive matching (e.g., specific 'y' only) and lack visual emphasis for critical warnings, which increases user friction and error potential.
**Action:** Always implement case-insensitive input handling supporting standard synonyms ('yes', 'YES') and use ANSI colors to highlight destructive actions in CLI scripts.

## 2024-05-25 - CLI Graceful Exit
**Learning:** Python CLI tools print raw tracebacks on `KeyboardInterrupt` (Ctrl+C), which is intimidating and unprofessional for end-users compared to standard Unix tools.
**Action:** Wrap the `main` execution block in a `try...except KeyboardInterrupt` handler that prints a clean, colored cancellation message and exits with code 130.
