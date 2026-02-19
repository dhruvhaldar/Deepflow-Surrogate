## 2024-05-24 - CLI Interaction Patterns
**Learning:** CLI interactive prompts in this project rely on strict case-sensitive matching (e.g., specific 'y' only) and lack visual emphasis for critical warnings, which increases user friction and error potential.
**Action:** Always implement case-insensitive input handling supporting standard synonyms ('yes', 'YES') and use ANSI colors to highlight destructive actions in CLI scripts.

## 2025-05-24 - CLI Spinner Behavior
**Learning:** CLI spinners that assume a TTY environment can disappear entirely in CI/CD logs or file redirections, leaving users with no feedback on long-running processes.
**Action:** Implement a dual-mode spinner: animated with cursor hiding (`\033[?25l`) for TTYs, and a single static print (e.g., "Processing...") for non-TTY environments.
