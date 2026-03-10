## 2024-05-24 - Enhance CLI Numerical Data Readability
**Learning:** Wrapping numerical values in structured sections (like Mesh Statistics or Bounding Boxes) in `Colors.BOLD` improves visual hierarchy and scannability against their labels. This greatly enhances CLI UX because users can quickly scan key figures visually separated from normal-weighted label text.
**Action:** When printing structured data in a CLI, always emphasize the numeric output using ANSI bold formatting to make it stand out from descriptive text.
