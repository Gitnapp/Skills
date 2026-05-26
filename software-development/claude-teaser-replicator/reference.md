# Reference — Time-Driven Animation API

Full API for the primitives and utilities the template provides. Read this when extending the template with new scenes or authoring new reusable primitives.

## 1. `tUtil` — Timing Library

All of these are pure, cheap, stateless. Call as often as you like.

### `tUtil.clamp01(t) → number`
Clamp to `[0, 1]`.
```js
tUtil.clamp01(-0.3) // 0
tUtil.clamp01(1.7)  // 1
```

### `tUtil.lerp(a, b, t) → number`
Linear interpolation. No clamping — pass clamped `t` if you need it.
```js
tUtil.lerp(100, 500, 0.25) // 200
```

### `tUtil.smooth(t) → number`
Smootherstep (Perlin's `6t⁵ - 15t⁴ + 10t³`). Gentler than smoothstep at both ends. **Default easing for almost everything.**
```js
tUtil.smooth(0.5) // 0.5, but with 0-derivative ramps at 0 and 1
```

### `tUtil.ein(t) → number`
Ease-in quad: `t²`. Objects accelerating from rest.

### `tUtil.out(t) → number`
Ease-out quad: `1 - (1-t)²`. Objects settling to rest. Good default for entrance animations.

### `tUtil.back(t) → number`
Ease-in-out with subtle overshoot (c1 = 1.70158). Gives text/panels a tiny "land" bounce.

### `tUtil.phase(localTime, start, dur) → number`
**The workhorse.** Returns 0 before `start`, 1 after `start+dur`, linearly interpolated in between.

```js
// A button fades in from t=2s to t=2.5s
const buttonOpacity = tUtil.phase(lt, 2, 0.5);
```

If `dur <= 0` it returns 0 before `start`, 1 after — a step function.

### `tUtil.envelope(t, inStart, inDur, outStart, outDur) → number`
Attack / sustain / release. Ramps 0→1 over `[inStart, inStart+inDur]`, holds at 1, ramps 1→0 over `[outStart, outStart+outDur]`.

```js
// Title appears at 1s (0.4s fade in), dismisses at 4s (0.6s fade out)
const titleOpacity = tUtil.envelope(lt, 1, 0.4, 4, 0.6);
```

Implementation: `pin * (1 - pout)`.

### `tUtil.track(frames, t) → number`
Keyframe interpolation with smootherstep between frames.

```js
// Cursor x-position moves through 4 waypoints
const cursorX = tUtil.track([
  [0, 100],    // at t=0, x=100
  [1, 400],    // at t=1s, x=400
  [1.8, 380],  // subtle overshoot back
  [3, 900],    // at t=3s, x=900
], lt);
```

Frames **must** be sorted by t. Before the first frame returns `frames[0][1]`; after the last, `frames[n-1][1]`. Use for cursor paths, multi-stage panel positions, anything with 3+ keyframes.

### `tUtil.typed(text, t, cps = 22) → number`
Character count for typewriter effect.

```js
const n = tUtil.typed("Meet Claude Design", lt, 18);
return <span>{text.slice(0, n)}</span>;
```

Negative `t` returns 0; past the end, full length.

## 2. Layout Primitives

### `<Stage width height>`
Fixed-size container. Put everything inside. Use `overflow: hidden` to clip off-stage elements. Provides `SelectionContext` for editor mode.

### `<Layer el x y w h scale opacity rotation>`
Absolute-positioned wrapper.
- `x, y` — pixel position on stage (top-left)
- `w, h` — size (optional; some layers just want transform)
- `scale` — uniform scale around center
- `opacity` — 0 skips rendering entirely (early return, saves React work)
- `rotation` — degrees
- `el` — data attribute for editor-mode selection (safe to omit in production)

**Always absolute.** Never float or flex inside `<Stage>`. Use nested `<Layer>`s for hierarchy.

## 3. Text Primitives

### `<RevealText text p q size weight serif align stagger dark />`
Word-by-word reveal. Each word runs blur → scale → fade-in over a stagger window.

Props:
- `text` — the string
- `p` — reveal progress 0→1 (words animate in sequentially)
- `q` — dismiss progress 0→1 (whole block blurs + rises + fades)
- `size` — px font size
- `weight` — font weight (Serif auto-subtracts 170 to match optical weight)
- `serif` — use serif face
- `align` — text-align
- `stagger` — fraction of progress each word's animation spans (default 0.55)
- `dark` — light text for dark backgrounds

Stagger math: `gap = (1 - stagger) / (wordCount - 1)` so word N-1 finishes exactly at `p=1`.

### `<TypeText text chars caret dark size />`
Character-by-character typewriter.
- `text` — the full string
- `chars` — how many chars to show (use `tUtil.typed()` to compute)
- `caret` — show blinking cursor
- `dark`, `size` — styling

## 4. Scene Shape

```js
function sceneFoo(ctx, t, t0, sceneDur) {
  const lt = t - t0;
  const live = lt >= -0.5 && lt <= sceneDur + 0.5;

  // Register tweaks (optional — only needed if you have an editor)
  ctx.el("sFoo", "Foo Scene");
  const typeDur = ctx.num("sFoo_typeDur", 1.2, { label: "Type dur", at: t0 });

  if (!live) return null;

  // Derive ALL state from lt
  const headerP = tUtil.phase(lt, 0, typeDur);
  const dismiss = tUtil.phase(lt, sceneDur - 0.5, 0.5);

  return (
    <Layer x={0} y={0} w={1280} h={720}>
      <RevealText text="Foo" p={headerP} q={dismiss} />
    </Layer>
  );
}

// REQUIRED: lets the player compute the total timeline length.
// Reads tweak values directly from the raw store (no ctx, no manifest push).
sceneFoo.computeDur = (T) => {
  const typeDur = T.sFoo_typeDur ?? 1.2;
  return typeDur + 0.8 + 0.5; // type + hold + dismiss
};
```

### Rules for `.computeDur`
- Reads directly from `T` (the raw tweaks object), **not** from `ctx`.
- Must not push to manifest (no side effects).
- Must return the same value the scene body believes its total length is — if they disagree, the cascade is wrong and later scenes start at the wrong `t0`.

## 5. Background Crossfade Pattern

```js
const SCENE_BG = ["#FAF9F5", "#E3DACC", "#141413"]; // per-scene bg color
const FADE = 0.8; // crossfade window at each boundary

// In TeaserScene:
let idx = 0;
for (let i = 0; i < SCENE_BG.length; i++) {
  if (t < starts[i + 1]) { idx = i; break; }
}
const nextStart = starts[idx + 1] ?? totalDur;
const fadeP = tUtil.clamp01((t - (nextStart - FADE)) / FADE);

return (
  <>
    <div style={{ position: "absolute", inset: 0, background: SCENE_BG[idx] }} />
    {fadeP > 0.001 && (
      <div style={{
        position: "absolute", inset: 0,
        background: SCENE_BG[Math.min(idx + 1, SCENE_BG.length - 1)],
        opacity: tUtil.smooth(fadeP)
      }} />
    )}
    {/* ...scenes... */}
  </>
);
```

**Why two divs and not an index lerp?** RGB-interpolating between two specific colors avoids "flashing slate" when going `heather → ivory` (palette-index tweening would walk through `slate`).

## 6. Cursor Primitive

```jsx
function CursorDot({ x, y, variant = "arrow", scale = 1 }) {
  return (
    <div style={{
      position: "absolute", left: x, top: y,
      transform: `translate(-2px, -2px) scale(${scale})`,
      transformOrigin: "top left",
      pointerEvents: "none",
      zIndex: 100,
    }}>
      {/* SVG arrow / pointer / hand */}
    </div>
  );
}
```

Compute position with `tUtil.track` on a waypoint list:
```js
const x = tUtil.track([[0, 100], [1, 400], [2, 600]], lt);
const y = tUtil.track([[0, 100], [1, 200], [2, 150]], lt);
```

**Own the cursor inside the scene, not in a global layer.** This keeps each scene a self-contained unit — scrubbing to the middle of scene 4 shouldn't require scene 1's cursor state.

## 7. Tweaks Pattern (Editor → Frozen Snapshot)

Development mode uses a `ctx.num(key, default, meta)` API that both:
1. Returns the current value from a tweaks store
2. Pushes a manifest entry `{key, value, label, at, el, ...}` so an editor sidebar can list all knobs

Production builds replace the ctx with a frozen snapshot — scene code doesn't change, but the values are inlined as a `const TWEAKS = {...}` object.

Minimal ctx for player-only builds:
```js
function createTweakCtx(store) {
  return {
    num: (k, fallback) => store[k] ?? fallback,
    text: (k, fallback) => store[k] ?? fallback,
    point: (k, fallback) => store[k] ?? fallback,
    bool: (k, fallback) => store[k] ?? fallback,
    el: () => {},       // no-op in player
    manifest: [],       // unused but kept for shape compat
  };
}
```

For editor builds add `push` calls:
```js
num: (k, fallback, meta) => {
  const v = store[k] ?? fallback;
  ctx.manifest.push({ key: k, value: v, type: "num", ...meta });
  return v;
},
```

## 8. Debugging Tips

### Scrubber
Add an `<input type="range" min="0" max={duration} step="0.01">` on top of the stage. Its `onChange` sets `tRef.current` directly. Now you can drag through the entire animation.

### Frame freezer
Hold Shift while hovering the scrubber to snap to 0.1s ticks — maps to the `type: '_tick'` boundaries the TeaserScene pushes into the manifest.

### "What's at this pixel?"
`document.elementsFromPoint(x, y)` ignores `pointer-events: none`, so you can inspect `data-el` attributes to identify layers.

### Performance
~60 manifest pushes per frame is fine. If you see jank, the culprit is almost always React reconciliation of a very tall tree, not the tweak reads — memoize the expensive subtrees or split the Stage into fewer siblings.

## 9. Canonical File Layout

```
my-teaser/
├── index.html            # template.html, customized
└── (optional) assets/    # SVG/font sources if not inlined
```

One file. Ships anywhere. Embeddable in an iframe.

To inline assets for distribution:
1. Read each asset as binary
2. gzip → base64 → `<script type="bundle/manifest">{uuid: {mime, data}}</script>`
3. Emit a pre-script that decodes via `DecompressionStream('gzip')` and substitutes UUID placeholders in the template with `blob:` URLs

See `Claude Design Teaser.html` for a full reference implementation of the self-extracting bundle.

## 10. Scene Patterns (catalog)

| Pattern | Recipe |
|---|---|
| Typewriter title | `const n = tUtil.typed(text, lt, cps)`; render `text.slice(0, n)` |
| Word-by-word fade-in | `<RevealText p={tUtil.phase(lt, 0, dur)} />` |
| Hold then dismiss | `q={tUtil.phase(lt, dismissStart, dismissDur)}` |
| Cross-scene bg blend | two absolute divs, top one's opacity = `tUtil.smooth(fadeP)` |
| Cursor path with pause | `tUtil.track` with duplicate-time keyframes `[1.2, x], [1.8, x]` (constant for 0.6s) |
| Panel slide-in with overshoot | `x = tUtil.lerp(offscreen, rest, tUtil.back(phase))` |
| Parallax scroll | each layer gets its own `tUtil.phase` rate |
| Button press feedback | `scale = 1 - 0.05 * tUtil.envelope(lt, pressAt, 0.08, pressAt + 0.08, 0.12)` |
