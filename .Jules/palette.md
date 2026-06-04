## 2024-05-24 - Enhance CLI Numerical Data Readability
**Learning:** Wrapping numerical values in structured sections (like Mesh Statistics or Bounding Boxes) in `Colors.BOLD` improves visual hierarchy and scannability against their labels. This greatly enhances CLI UX because users can quickly scan key figures visually separated from normal-weighted label text.
**Action:** When printing structured data in a CLI, always emphasize the numeric output using ANSI bold formatting to make it stand out from descriptive text.

## 2025-03-12 - Prevent Mangled Terminal on EOF
**Learning:** When using `input()` for CLI prompts, users pressing `Ctrl+D` (EOF) immediately abort the input without printing a newline. If the script subsequently prints messages or exits, those messages or the user's terminal shell prompt will be printed on the same line as the aborted prompt, resulting in a mangled, visually confusing UX.
**Action:** Always wrap `input()` in a `try...except EOFError` block and explicitly `print()` an empty newline to gracefully reset the cursor before proceeding or exiting.

## 2025-03-17 - Add Multi-Step Sequence Indicators to Progress Spinners
**Learning:** When a CLI tool has a multi-step process utilizing separate loading spinners, adding explicit step indicators (e.g., `[1/2]`, `[2/2]`) to the spinner messages significantly improves the user's mental model by establishing clear expectations about the total duration and remaining phases of the operation.
**Action:** Always prepend step indicators to progressive loading spinners when the operation involves multiple distinct phases.

## 2025-03-24 - Align Inline Dimensions in CLI Outputs
**Learning:** When displaying grouped secondary context inline (like Width and Height next to coordinate ranges), using exact character spacing to vertically align the labels (e.g., `Width:  ` vs `Height: `) significantly enhances visual harmony and scannability, turning chaotic terminal output into structured tabular data.
**Action:** Always pad inline descriptive labels within the same visual block to match the width of the longest label, ensuring the subsequent dynamic data aligns perfectly on the vertical axis.

## 2024-05-25 - Provide Actionable Tips for CLI Warnings
**Learning:** When displaying a warning about an unsupported user action or input (like an invalid file extension), providing a concrete, actionable tip (e.g., suggesting the preferred `.msh` extension) significantly reduces user friction and helps them self-correct without needing to consult documentation.
**Action:** Always follow up CLI warnings with a `Colors.OKBLUE` tip explicitly stating the recommended fix or preferred value.

## 2024-05-27 - Frictionless Core Actions via Clipboard Integration
**Learning:** For developer tooling sites where the core user journey involves running CLI commands, manually selecting and copying code snippets is a high-friction interaction. Providing an explicit, accessible one-click "Copy to Clipboard" button directly alongside the commands dramatically improves UX. Adding temporary visual feedback ("Copied ✓") with `aria-live` regions ensures confidence without disorienting screen readers.
**Action:** When displaying instructional CLI commands or code snippets in a web interface, always accompany them with an accessible one-click copy button to make the execution path as frictionless as possible.
## 2024-05-29 - Making Scrollable Code Blocks Keyboard Accessible
**Learning:** Elements like `<pre>` or `<code>` with `overflow-x: auto` are often inaccessible to keyboard-only users because they are not focusable by default, meaning users cannot use arrow keys to scroll horizontally to see the full content.
**Action:** Always add `tabIndex={0}` and clear `:focus-visible` styles to any container with scrollable overflow to ensure keyboard-only users can focus and interact with the hidden content.

## 2025-05-30 - Inclusive Smooth Scrolling
**Learning:** Adding `scroll-behavior: smooth` drastically improves the experience of anchor link navigation by providing context of where the user is moving on the page, instead of a jarring instant jump. However, this motion can trigger nausea or dizziness in users with vestibular disorders.
**Action:** Always wrap `scroll-behavior: smooth` inside a `@media (prefers-reduced-motion: no-preference)` query to respect system-level accessibility settings and ensure inclusive UX.

## 2025-05-30 - Prevent Checking in Build Artifacts
**Learning:** During frontend development or testing with Next.js, running `pnpm build` creates a `frontend/.next` folder with massive build artifacts. If these files are added to git, it bloats the repository and pollutes pull requests.
**Action:** Ensure that the `frontend/.next` folder is properly excluded in `.gitignore` (which it was), but also be extremely careful when staging files (e.g. `git add -A`) to avoid adding ignored or untracked build output to the index. Always verify `git status` before requesting code review.

## 2025-05-30 - Clarify Internal Scroll Navigation
**Learning:** For single-page layouts, users can hesitate when clicking links like "Explore demos" because they fear being navigated away to a completely different page.
**Action:** Always add a downward directional arrow (`↓`) to internal anchor links (e.g. `href="#demos"`) to visually communicate that the link will simply scroll them down the current page, reducing hesitation and setting correct expectations.
## 2024-06-01 - Context-Aware ARIA Labels for Repeated UI Elements
**Learning:** When using repeated generic interactive elements (like a "Copy" button inside a list of demo cards), providing a static generic `aria-label` (e.g., "Copy to clipboard") forces screen reader users to listen to the surrounding context to understand *what* is being copied.
**Action:** Always provide unique, context-aware `aria-label`s for repeated interactive elements (e.g., "Copy command for Deterministic Mesh Generation") to make their purpose immediately clear in isolation.

## 2025-06-03 - Accessible Skip Links for SPAs
**Learning:** In Single Page Applications (like Next.js React apps), screen reader and keyboard-only users often have to tab through repetitive global navigation or header structures on every route change. Adding a visually hidden "Skip to main content" link as the first focusable element on the page drastically improves accessibility.
**Action:** Always include an accessible skip link (`<a href="#main-content" className="skip-link">...</a>`) positioned off-screen that reveals itself on `:focus`, and ensure the target `<main>` container has `id="main-content"` and `tabIndex={-1}` to programmatically receive focus without a jarring focus outline.

## 2025-06-03 - Native Button Pointer Feedback
**Learning:** While CSS frameworks or standard resets often strip default styling from native `<button>` elements, they often forget to explicitly add `cursor: pointer`. This causes buttons (like standalone Copy Buttons) to display a default text or arrow cursor, leading to user hesitation as it breaks the expected interaction model of clickable web elements (like `<a>` tags).
**Action:** Always ensure any class used on native `<button>` elements (e.g., `.button`) explicitly includes `cursor: pointer;` to provide confident, expected hover feedback.
