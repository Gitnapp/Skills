# Claude Design CDP: contrast-query workflow notes

Session-derived notes for using Claude Design's own chat/runtime to inspect design contrast when the canvas iframe is not directly readable.

## When to use

Use this when the user asks for design-token details, WCAG contrast, accessibility contrast, light/dark theme differences, or similar facts from a Claude Design project.

## Key lesson

The visible design canvas is rendered inside a sandboxed `*.claudeusercontent.com/_bootstrap` iframe that relies on a postMessage handshake from `claude.ai`. Opening that iframe URL directly may show an empty page or `file not found`; do not treat that as the design being missing.

If an opened page/frame errors:
1. Close the bad page/frame or return to the main Claude Design tab.
2. Open `Design Files`.
3. Select the correct entry from the file list (`PAGES`, `COMPONENTS`, or folders such as `screens/`).
4. Return to the top file tab/design view before using toolbar modes.

## Reliable way to read contrast data

Ask Claude Design in its chat input instead of scraping the iframe:

```text
What are the Design Contrast values for the <section name> section? Show me the color contrast ratios, light/dark theme contrast settings, and accessibility contrast info.
```

For Chinese projects, include both English and Chinese section names when known:

```text
What are the Design Contrast values for the Moments (朋友圈) section? Show me the color contrast ratios, light/dark theme contrast settings, and accessibility contrast info.
```

Then wait 20–60 seconds. Claude Design may display status lines like `Running script` or whimsical progress text before the real report appears.

## Expected response shape

A useful contrast report often includes:
- Number of pairings tested in light and dark themes
- AAA / AA / failing counts
- Failure clusters with ratios and where they appear
- Token-level root cause
- Recommended token change(s)
- Non-text contrast notes
- Suggested next actions such as patching tokens or adding a contrast artboard

Example pattern observed:

```text
Computed actual WCAG 2.1 ratios for every text + UI surface in 28 → 28g (light & dark).
Light / Dark pairings tested: 38 / 38
AAA, AA, and fail counts
Root issue: brand-blue token too light in light mode
Recommended fix: darken brand.light from #1FA5E8 to roughly #0F7AB8
```

## Interaction details

- `Design Files` opens the file browser with sections like `FOLDERS`, `PAGES`, and `COMPONENTS`.
- File rows may not be semantic buttons; direct text clicks often work, but if not, walk up to a parent with pointer cursor.
- Top file tabs are separate from the file browser list. Click the correct file tab to get back to the design/canvas toolbar.
- `Tweaks` may be visible only in the design view, not while the file browser is open.
- Context chips such as `Design System (design system)` are references; clicking them may only show tooltip-style context, not a full panel.

## Avoid

- Do not assert the design file is inaccessible just because the iframe URL returns `file not found`.
- Do not manually infer WCAG ratios from screenshots if Claude Design can run a token-aware script.
- Do not keep scraping `document.body.innerText` after asking the question until the script output has actually landed; poll/wait until the response contains concrete ratios or recommendations.
