1. **Explore & Identify UX Win**: Analyzed `frontend/app/page.tsx` and identified that the site revolves around CLI commands (presented in `<code>` and `<pre>` blocks) that users are encouraged to run. A significant micro-UX improvement is adding a one-click "Copy to Clipboard" button to these blocks.
2. **Create `CopyButton` Component**:
   - Create `frontend/app/CopyButton.tsx`, a small Client Component that uses `navigator.clipboard.writeText`.
   - Include an accessible `aria-label` and visual feedback (`Copied ✓`) that reverts after 2 seconds.
   - Use the existing `button ghost` class for styling to adhere to the design system.
3. **Integrate `CopyButton`**:
   - Update `frontend/app/page.tsx` to include `<CopyButton>` immediately following the `<code>` blocks in the demo cards and the final `<pre>` block.
4. **Pre-commit Verification**:
   - Run `pnpm lint`, `pnpm build`, and tests in the `frontend` directory to ensure no regressions.
   - Document the pattern in `.jules/palette.md` noting that making core actions (like running commands) frictionless via clipboard integration is a critical UX pattern for developer tooling sites.
5. **Submit**: Create PR with a descriptive title and UX-focused details.
