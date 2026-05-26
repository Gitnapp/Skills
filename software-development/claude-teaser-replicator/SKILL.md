---
name: claude-teaser-replicator
description: Replicate the Claude Design Teaser animation style — scrub-safe, single-file React animations where every scene is a pure function of time (Scene(ctx, t) → JSX). Use when the user wants to reproduce the Claude teaser, build a cinematic product intro, keynote-style explainer, or any animated presentation with precise choreography, keyframe-free transitions, and reproducible frame-by-frame state (similar to Apple product reveals or Figma Config keynote reels). Triggers: "reproduce Claude teaser", "replicate Claude Design Teaser", "build an animated teaser", "cinematic intro", "scrub-safe animation", "React RAF animation", "time-driven scene animation", "single-file HTML animation".
---

# Claude Teaser Replicator

Build cinematic, multi-scene web animations where **the entire visual state is a pure function of one number: `t` (seconds)**. No CSS transitions, no keyframe animations, no `useState` side-effects driving motion. Every frame re-derives everything from `t`.

## Why This Architecture

| Problem with CSS transitions | Why time-as-function wins |
|---|---|
| State is invisible — "what's the cube rotated to right now?" lives in the browser's compositor | Every value is computable from `t` — you can paste `scene(ctx, 3.4)` into devtools and get the exact frame |
| Can't scrub backwards or jump to an arbitrary moment | Move the playhead, re-render. Any direction, any instant. |
| Chained `setTimeout`s drift on slow tabs | `dt` is clamped; scenes compute from absolute `t`, not deltas |
| Composing 7 scenes into one timeline is manual | Each scene exposes `.computeDur(T)`, parent sums to get `starts[i]` cascading |

## When to Use This Skill

**Use when** the user asks to:
- Build a product/feature teaser like the Claude Design Teaser, Stripe intros, Linear keynotes
- Make a cinematic multi-scene animated HTML that ships as one file
- Add a "scrub-safe" or "timeline-editable" animation where they can drag a playhead
- Reproduce a specific animation where CSS transitions will become a maintenance nightmare (10+ beats, coordinated cursor + text + panels)
- Build an in-browser animated explainer embedded in an iframe

**Don't use when** the user wants:
- A simple CSS hover/loading spinner → use CSS `@keyframes`
- A real video → use Remotion (`remotion-best-practices` skill)
- An SVG illustration with a single entrance — use GSAP/Motion

## Core Mental Model

```
                    ┌─────────────────────┐
  requestAnimation  │                     │
  Frame drives t ─> │  Player (RAF loop)  │
                    │                     │
                    └──────────┬──────────┘
                               │ t: seconds
                               ▼
         ┌─────────────────────────────────────┐
         │ TeaserScene(ctx, t) — stitches      │
         │  starts[i] = sum(durs[0..i])        │
         └──────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
    scene1(ctx, t, t0, dur)  scene2(...)       scene3(...)
          │                    │                    │
          ▼                    ▼                    ▼
       lt = t - t0          lt = t - t0         lt = t - t0
       (local time)         (local time)        (local time)
          │                    │                    │
          ▼                    ▼                    ▼
   tUtil.phase, typed,   RevealText, CursorDot,  Layer/Stage
   envelope, track     FolderIngest, MiniBrowser  primitives
          │                    │                    │
          └────────────────────┴────────────────────┘
                               │
                               ▼
                          React JSX tree
                          (fresh every frame)
```

## Quick Start

1. **Copy the template**: `template.html` in this skill directory is a self-contained runnable file with React + Babel standalone from CDN, 3 scenes, a working Player, scale-to-fit, and the timing library inline. Open it in a browser — it runs.

2. **Add a scene**: a scene is a function `(ctx, t, t0, dur) => JSX | null` with a `.computeDur(T)` static method.

   ```jsx
   function sceneFoo(ctx, t, t0, dur) {
     const lt = t - t0; // local time
     if (lt < 0 || lt > dur) return null;

     const typeP = tUtil.phase(lt, 0, 1.2);     // type-in over 1.2s
     const holdQ = tUtil.phase(lt, 1.2, 0.8);   // hold, then dismiss
     const dismiss = tUtil.phase(lt, dur - 0.5, 0.5);

     return (
       <Layer x={0} y={0} w={1280} h={720}>
         <RevealText text="Hello" p={typeP} q={dismiss} />
       </Layer>
     );
   }
   sceneFoo.computeDur = (T) => 1.2 + 0.8 + 0.5; // read-only tweak probe
   ```

3. **Register it**: add to `SCENE_FNS` array in the template. Background color for that scene? add to `SCENE_BG[i]`.

4. **Iterate**: reload the page; adjust times; reload. For faster loops add a scrubber input that sets `tRef.current` manually.

## Architectural Rules (NON-NEGOTIABLE)

1. **No CSS transitions / animations.** If you find yourself writing `transition: transform 0.3s`, you're breaking scrub-safety. Compute the transform per-frame from `t`.

2. **Scenes are pure.** No `useState`, no `useEffect` inside scene code. React component *primitives* (RevealText etc.) can have memos, but the scene function itself just reads `t` and returns JSX.

3. **Local time inside scenes.** Always `const lt = t - t0` on entry. Everything inside the scene uses `lt ∈ [0, dur]`.

4. **Cull, don't conditionally branch.** Return `null` when `lt < -0.5 || lt > dur + 0.5` — but keep any tweak-registration calls above the cull so the editor manifest is complete.

5. **Clamp dt on resume.** `dt = Math.min((now - last)/1000, 0.1)`. A hidden tab can pause RAF for seconds; without the clamp you'll skip whole scenes on resume.

6. **Fixed stage, scale to fit.** Render at 1280×720 (or 1920×1080). Outer wrapper uses `transform: scale(Math.min(w/STAGE_W, h/STAGE_H))`. Never let scenes know the real viewport size.

## Progressive Disclosure

- **reference.md** — full `tUtil` API, primitive component reference (Layer, Stage, RevealText, TypeText, CursorDot), background crossfade pattern, tweaks snapshot pattern, debugging tips.
- **template.html** — runnable starter. Read it before editing; every section is commented.

## Common Pitfalls (from the field)

**"My animation judders on tab refocus."**
Your dt isn't clamped. Cap at 0.1s.

**"Scrubbing forward works but backward breaks."**
Something's holding state across frames. Search scenes for `useRef` / `useState` / module-level `let` variables that mutate. Move that state into `t`-derived reads.

**"I changed scene 3's duration and scene 5 is now wrong."**
Good — that proves the cascade works. Make sure you used `starts[i] = starts[i-1] + durs[i-1]`, not a hardcoded `t0 = 10`. And make sure `computeDur` actually reads the same tweak your scene body reads.

**"Text is blurry after dismissing."**
`filter: blur()` on a parent doesn't clean up — always pair with `opacity: 0` at the end of the envelope so the blurred ghost can't be seen.

**"The animation never stops."**
Check that `doneRef` guard fires `postMessage` exactly once, and `raf` is not re-scheduled after `next >= duration`.

## Output Format Options

- **Single HTML, CDN React**: fastest to iterate. Use `template.html` as-is.
- **Single HTML, inlined assets**: production. Gzip+base64 each asset into a manifest block, decompress with `DecompressionStream('gzip')` on load. See Claude Design Teaser for a reference implementation (self-extracting bundle pattern).
- **Vite project**: if the user wants a real dev server, port the same patterns into React + TypeScript. The architecture doesn't change.

## Attribution

Pattern distilled from the `Claude Design Teaser.html` single-file React player (Anthropic). The core insight — "scene as pure function of time, manifest-driven editor" — predates CSS animations and shows up in After Effects, Remotion, and any timeline-based tool; this skill adapts it for plain React + RAF with no external deps.
