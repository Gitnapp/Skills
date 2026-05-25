# Claude Design CDP field notes

Session-proven workflow details for operating Claude Design through local Chrome CDP.

## Error page recovery

If the preview or a manually opened `*.claudeusercontent.com/_bootstrap` page shows an error such as `file not found`, do not conclude that the design is unreadable.

Correct recovery sequence:
1. Close or ignore the error page/tab.
2. Return to the main `https://claude.ai/design/p/<project-id>` page.
3. Open `Design Files` from the left/chat panel.
4. Choose the correct entry under `PAGES` / `COMPONENTS`, or click the active top file tab to return to the design canvas.
5. Continue from the canonical Claude Design page, not the bootstrap iframe URL.

Reason: the `claudeusercontent.com/_bootstrap` iframe is a postMessage bootstrapper. It needs the parent Claude Design page to send an `omelette-preview-init` message with a token and `navigateTo`. Direct navigation bypasses that handshake and can show `file not found` even when the design itself is valid.

## File browser landmarks

When `Design Files` is open, visible sections commonly include:

- `FOLDERS` — e.g. `screens`, `uploads`
- `PAGES` — main HTML pages, e.g. `算力界 内页设计稿.html`
- `COMPONENTS` — JSX components, e.g. `ios-frame.jsx`, `design-canvas.jsx`
- Preview metadata — file name, type, modified time, size

When the file browser is open, toolbar buttons like `Tweaks` may disappear or be replaced by file-browser buttons such as `project`, `New sketch`, `Paste`, `Open`. To return to canvas mode, press Escape a few times or click the main file tab.

## Reading design details despite sandboxing

The canvas iframe is cross-origin/sandboxed. Direct DOM extraction of the rendered design is unreliable. Prefer asking Claude Design through the project chat for semantic/design-system data:

```text
What are the Design Contrast values for the <section> section? Show me color contrast ratios, light/dark theme contrast settings, and accessibility contrast info.
```

For contrast/accessibility questions, Claude Design may run scripts and take 30–60 seconds. Poll until the response replaces progress messages such as `Running script` or playful status text.

## Example contrast report shape

A useful report may include:

- Number of tested pairings in light/dark themes
- AAA / AA / failing counts
- Failure clusters by token and UI location
- Root-cause token recommendations
- Non-text contrast checks
- Proposed next actions: patch token, re-run report, add contrast-tracking artboard

When extracting the result, search page text for terms such as `WCAG`, `ratio`, `contrast`, `AA`, `AAA`, `light`, `dark`, `token`, and the target section name.
