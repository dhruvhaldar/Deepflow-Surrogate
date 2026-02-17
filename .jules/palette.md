## 2024-05-24 - CLI Interaction Patterns
**Learning:** CLI interactive prompts in this project rely on strict case-sensitive matching (e.g., specific 'y' only) and lack visual emphasis for critical warnings, which increases user friction and error potential.
**Action:** Always implement case-insensitive input handling supporting standard synonyms ('yes', 'YES') and use ANSI colors to highlight destructive actions in CLI scripts.
