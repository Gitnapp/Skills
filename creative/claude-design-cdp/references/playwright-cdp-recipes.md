# Playwright CDP Recipes for Claude Design

## Common Connection Template

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        page = browser.contexts[0].pages[0]
        # ... interactions ...
        await browser.close()
asyncio.run(main())
```

## Recipe: Get Page State

```python
title = await page.title()
url = page.url
text = await page.evaluate("() => document.body?.innerText || ''")
```

## Recipe: Click by Text Content

```python
await page.evaluate("""
    document.evaluate('//*[contains(text(), "EXACT TEXT")]', document, null,
        XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue?.click()
""")
```

## Recipe: Click Button by Text

```python
await page.evaluate("""
    const buttons = document.querySelectorAll('button');
    for (const b of buttons) {
        if (b.textContent.trim() === 'Tweaks') b.click();
    }
""")
```

## Recipe: Type + Submit in Chat

```python
await page.fill('textarea[data-testid="chat-composer-input"]', 'Your question here')
await page.click('button[data-testid="chat-send-button"]')
await asyncio.sleep(5)
```

## Recipe: Take Screenshot

```python
await page.screenshot(path='/tmp/claude_design.png', full_page=True)
```

## Recipe: Press Keys / Close Panels

```python
for _ in range(3):
    await page.keyboard.press('Escape')
    await asyncio.sleep(0.3)
```

## Recipe: Navigate File List

```python
await page.evaluate('//*[contains(text(), "Design Files")]')
await asyncio.sleep(2)
# Then click file names in the browser
```

## Recipe: Context Tags

Claude Design shows context reference chips (e.g. "Design System", "garage-elys") in the chat composer. Their `title` attr contains the full prompt context. Clicking a chip removes it.
