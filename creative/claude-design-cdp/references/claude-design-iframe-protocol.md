# Claude Design Iframe Protocol

The design canvas renders inside a cross-origin sandboxed iframe from `*.claudeusercontent.com`.

## Bootstrap Flow

1. **Iframe loads** `/_bootstrap` — minimal HTML with a JS bootstrap
2. **Bootstrap sends** `postMessage({type: 'omelette-bootstrap-ready'}, '*')` to parent
3. **Parent responds** with `token`, `navigateTo`, `expiresAt`
4. **Iframe sets cookie** `__Host-omelette-preview=<token>; Path=/; Secure; SameSite=None; Partitioned; Max-Age=<expiresAt>`
5. **Iframe redirects** to `navigateTo` — the actual design file URL

## Allowed Origins

Only accepts postMessage from `https://claude.ai` and `https://preview.claude.ai`.

## Automation Implications

- **Cannot read iframe content cross-origin** — `frame.evaluate()` fails
- **Cannot manually set `__Host-` prefix cookies** — requires `Set-Cookie` response header
- **Cannot open `navigateTo` URL directly** — requires token from postMessage handshake
- **Cannot intercept the token** — postMessage bypasses CDP

## What Works

- `page.screenshot()` captures rendered design (including iframe) in parent screenshot
- Parent page toolbar, chat, file navigation all work normally via CDP
- Use chat interface to query design properties (color, contrast, tokens) instead

## Error Recovery

If iframe shows "file not found" or content is empty:
- The postMessage handshake likely failed
- Close the panel (Escape), find the correct file entry in the file list/tab bar
- Clicking the correct file tab re-triggers the iframe bootstrap
