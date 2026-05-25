---
name: claude-design-cdp
description: "Control Claude Design web UI via Chrome DevTools Protocol (CDP) — login, navigate, browse files, read design tokens/contrast via chat, interact with design projects programmatically."
version: 2.0.0
author: Eric
platforms: [macos]
metadata:
  hermes:
    tags: [claude-design, cdp, chrome, design, browser-automation, contrast, accessibility]
    related_skills: [claude-design, popular-web-designs]
---

# Claude Design CDP

Use this skill when the user wants to control Claude Design's web UI
(https://claude.ai/design) programmatically via Chrome DevTools Protocol.

This works by:
1. Launching Chrome locally with `--remote-debugging-port=9222`
2. Connecting via Playwright's `connect_over_cdp`
3. The user logs in once on the GUI Chrome window
4. After login, all interactions happen via CDP (navigation, click, type, extract)

**Requirement:** Python package `playwright` must be installed:
```bash
pip3 install playwright
```

## Workflow

### Step 1: Clean up and launch Chrome with CDP

```bash
# Kill any Chrome processes that may hold locks
osascript -e 'quit app "Google Chrome"' 2>/dev/null
sleep 1
rm -f ~/Library/Application\ Support/Google/Chrome/SingletonLock 2>/dev/null

# Launch Chrome with remote debugging on fresh profile
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --no-first-run \
  --user-data-dir=/tmp/chrome_fresh_cdp &
```

Use `background=true` on the terminal call since Chrome is a long-lived process.
Alternative: use `open -a "Google Chrome" --args --remote-debugging-port=9222 --no-first-run`
if `&` is not available.

### Step 2: Wait for port 9222 to be ready

```bash
for i in $(seq 1 10); do
  if lsof -i :9222 -P 2>/dev/null | grep -q "LISTEN"; then
    echo "Port 9222 ready"
    break
  fi
  sleep 2
done
```

### Step 3: Connect and navigate to Claude Design

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        page = browser.contexts[0].pages[0]
        await page.goto('https://claude.ai/design', wait_until='domcontentloaded')
        await asyncio.sleep(2)
        # User logs in manually on the Chrome GUI window
        # After login, continue...
        await browser.close()
asyncio.run(main())
```

### Step 4: After user logs in, interact with the design page

## Field notes

Additional session-proven details live in `references/field-notes.md`. Read it when dealing with error pages, `claudeusercontent.com/_bootstrap`, the `Design Files` panel, or Design Contrast/WCAG extraction.

## Page Structure

Claude Design has a split layout:
- **Left panel (400px):** Chat/messages area with file tabs at top
- **Right panel (canvas):** Design preview in a sandboxed iframe
- **Top toolbar:** Present, Share, Edit, Mark up, Tweaks, Comments, zoom

## Key Interactions

### Opening projects
Click on a project card from the main projects list. The URL becomes:
`https://claude.ai/design/p/{projectId}?file={filename}`

### File browser (Design Files)
Click "Design Files" to open the file panel showing:
- **FOLDERS:** screens/, uploads/
- **PAGES:** Main HTML design files (e.g., `设计稿.html`)
- **COMPONENTS:** JSX components (e.g., ios-frame.jsx, design-canvas.jsx)
- Each file shows size and last modified time

To browse files:
```python
# Click "Design Files"
await page.evaluate('() => document.querySelector(\'[class*="sc-fuIQnM"]\').click()')

# Click on a folder/file in the list
clicked = await page.evaluate("""() => {
    const allEls = document.querySelectorAll('*');
    for (const el of allEls) {
        if (el.children.length === 0 && el.textContent.trim() === 'filename.jsx') {
            el.click(); return 'Clicked';
        }
    }
    return 'Not found';
}""")
```

### Navigating back from file browser
Press Escape or click the file tab at the top to return to the design view:
```python
await page.keyboard.press('Escape')
```

### Reading design content via chat
The design file is rendered in a **sandboxed iframe** (`*.claudeusercontent.com/_bootstrap`)
using a postMessage-based auth handshake. You CANNOT read the iframe content directly
(cross-origin sandbox). The iframe shows "file not found" if accessed directly.

**Instead, use the chat interface** to ask Claude Design about the design:

```python
# Type a question in the chat textarea
await page.evaluate("""() => {
    const ta = document.querySelector('textarea');
    ta.value = 'Your question here';
    ta.dispatchEvent(new Event('input', { bubbles: true }));
}""")
await page.keyboard.type("What are the Design Contrast values for section X?", delay=20)

# Click Send
await page.evaluate("""() => {
    const buttons = document.querySelectorAll('button');
    for (const b of buttons) {
        if (b.getAttribute('data-testid') === 'chat-send-button') b.click();
    }
}""")

# Wait for response (15-30 seconds for analysis)
await asyncio.sleep(20)

# Read the response
text = await page.evaluate("() => document.body?.innerText || ''")
lines = [l.strip() for l in text.split('\n') if l.strip()]
```

### Handling error iframes
If the design iframe shows an error ("file not found"):
1. Close the error page (user or script)
2. Check the file list for the correct file entry
3. Click the correct file tab at the top to reload the canvas

### Toolbar modes
- **Edit** — Canvas enters edit mode ("Click anything on the canvas to edit it")
- **Mark up** — Annotation mode
- **Tweaks** — Settings/tweaks panel (may appear as a mode indicator, not always visible)
- **Comments** — Comment/discussion mode
- **Present** — Full-screen presentation
- **Share** — Share design link

### Context tags (chat input area)
The chat input area may show context reference tags like:
- "Design System (design system)" — A design system loaded as visual reference
- "garage-elys" — Another context reference file

These are removable chips - clicking them doesn't open a panel but can show tooltips.

## Use Case: Reading Design Contrast

Detailed workflow notes and an observed response shape live in `references/contrast-query-workflow.md`.

To get WCAG contrast analysis for a specific section (e.g., "朋友圈/Moments"):

1. Navigate to the project
2. If a directly opened iframe/page errors (`file not found`, blank bootstrap, etc.), close it and use `Design Files` to select the correct file entry instead of treating the design as inaccessible
3. Type a specific question in the chat:
   *"What are the Design Contrast values for the [section name] section? Show me color contrast ratios, light/dark theme contrast settings, and accessibility contrast info."*
4. Claude Design will run a script to analyze the design tokens
5. Wait for the response (20-60 seconds; status lines like `Running script` may appear before the useful report)
6. The report typically includes:
   - Number of pairings tested (light + dark)
   - AAA/AA/Fail counts
   - Specific failing ratios and locations
   - Token-level fix recommendations

## Use Case: Applying Design Fixes

After getting the contrast report, you can ask Claude Design to:
1. Patch the brand token to a darker value
2. Re-run the contrast report
3. Add a contrast-tracking artboard to the canvas
4. Both — patch + add the artboard

## Helper: Get all visible text from page

```python
text = await page.evaluate("() => document.body?.innerText || ''")
lines = [l.strip() for l in text.split('\n') if l.strip()]
```

## Helper: Get interactive elements

```python
buttons = await page.evaluate("""() => {
    return Array.from(document.querySelectorAll('button, a, [role="button"]'))
        .map(el => el.textContent.trim())
        .filter(t => t);
}""")
```

## Helper: Take screenshot

```python
await page.screenshot(path='/tmp/claude_design.png', full_page=True)
```

Note: Screenshots can't be shown to the user via terminal. Use `vision_analyze` if
the model supports image inputs, or describe the content verbally.

## Pitfalls

- **Chrome must be launched with a fresh profile** (`--user-data-dir=/tmp/...`) to avoid
  singleton lock conflicts with the user's existing Chrome session.
- **The `osascript -e 'quit app "Google Chrome"'` only works if Chrome was launched
  normally.** Use `kill` as fallback.
- **Playwright's `connect_over_cdp` connects to the browser level, not a specific profile.**
  After connecting, access pages via `browser.contexts[0].pages[0]`.
- **If no pages are open when connecting**, create one with `await browser.contexts[0].new_page()`.
- **Cloudflare verification requires the user to manually log in** on the Chrome GUI window.
- **DO NOT directly open the claudeusercontent.com iframe URL** — it's a bootstrapper that
  requires a postMessage handshake and will show "file not found" if accessed directly.
- **When a page/iframe shows an error, close it and find the correct entry** in the
  file list / file tabs instead.
- **The design canvas iframe is sandboxed** — you cannot read its HTML content cross-origin.
  Always use the chat interface to query design properties.
- **When done, clean up**: `kill <chrome_pid>` or `osascript -e 'quit app "Google Chrome"'`
- **Port 9222 binding can fail** if another Chrome instance is already holding the
  SingletonLock. Kill all Chrome processes first, then retry.
