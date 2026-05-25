---
name: llm-output-fix
description: "Use when LLM-generated structured output (JSON, enums, schemas) fails parsing or validation. Diagnoses and fixes Zod/JSON schema validation failures, truncated JSON, enum mismatches, and missing fields in AI SDK generateText/streamText pipelines."
---

# Fixing LLM Structured Output Parsing Failures

## When to Use

- Zod `safeParse` fails on LLM-generated JSON
- `extractJsonBlock` returns null despite JSON being present in text
- Schema validation errors on enum fields (model outputs natural language instead of enum values)
- Truncated JSON from multi-step tool-calling agents
- Repair/retry prompts that don't actually fix the issue

## Core Principle: Fix at the Source, Not Downstream

The correct defense order for LLM structured output:

1. **Prompt layer (source)** — Explicitly require English enum values. Separate "enum values must be English" from "content fields use target language".
2. **Schema layer (safety net)** — `z.preprocess` as lightweight fallback only (non-English → default), NOT a translation dictionary.
3. **UI layer (display)** — Map English enums to display language in components (e.g., `bullish` → `看多`).

**Anti-pattern:** Using `z.preprocess` to reverse-map natural language back to enum values (e.g., `"看多" → "bullish"`). This is a downstream patch that grows unbounded and still breaks on unseen variants.

## Diagnostic Protocol

**Step 1: Save the full raw LLM output to a file for inspection.**

Never diagnose from truncated data. The saved report/fallback often contains `.slice(0, N)` which hides the real issue.

```ts
// Temporary debug: save full text before parsing
import { writeFileSync } from "fs";
writeFileSync(`data/debug-${id}.txt`, fullText, "utf-8");
```

**Step 2: Check if JSON extraction works.**

```ts
const json = extractJsonBlock(fullText);
console.log("Extracted:", json === null ? "null" : typeof json);
```

If null → JSON block is malformed or truncated. If object → extraction works, schema validation is the problem.

**Step 3: If extraction works but schema fails, log the Zod errors AND the parsed keys.**

```ts
const parsed = schema.safeParse(json);
if (!parsed.success) {
  console.error("Issues:", parsed.error.issues);
  console.error("Keys:", Object.keys(json));
}
```

This distinguishes "missing fields" (truncated JSON) from "wrong values" (enum mismatch).

## Common Failure Patterns & Fixes

### Pattern 1: Enum Field in Natural Language

**Symptom:** Zod error `Invalid enum value. Expected 'bullish' | 'bearish' | 'neutral', received '中性偏谨慎'`

**Cause:** The prompt says "所有文字使用中文" (use Chinese for all text) without distinguishing enum values from content. The model faithfully translates enum values too.

**Fix (prompt — primary):** Add an explicit language rule section to the output format prompt:

```
### 语言规则
- **枚举值必须使用英文原文**：stance 只能是 "bullish"/"bearish"/"neutral"；
  state 只能是 "verified"/"contested"/"stale"/"unverified"
- **内容字段使用中文**：summary, rationale, description 等描述性文字用中文
```

**Fix (schema — safety net only):** Keep a minimal fallback, not a translation dictionary:

```ts
// Prompt enforces English enums; preprocess is safety net only
stance: z.preprocess(
  (v) => {
    if (typeof v !== "string") return v;
    const s = v.toLowerCase().trim();
    if (["bullish", "bearish", "neutral"].includes(s)) return s;
    return "neutral"; // fallback for any non-English value
  },
  z.enum(["bullish", "bearish", "neutral"])
),
```

### Pattern 2: Truncated JSON (Missing Closing Markers)

**Symptom:** `extractJsonBlock` returns null. Raw text starts with `` ```json `` but has no closing `` ``` ``.

**Cause:** The LLM ran out of output tokens or `stopWhen` terminated the multi-step loop before the JSON was completed.

**Fix (extraction):** Handle unclosed code blocks and bare `{...}` blocks:

```ts
function extractJsonBlock(text: string): unknown | null {
  function tryParse(raw: string): unknown | null {
    const trimmed = raw.trim();
    try { return JSON.parse(trimmed); } catch {}
    try { return JSON.parse(jsonrepair(trimmed)); } catch {}
    return null;
  }

  // 1. Closed ```json ... ``` blocks
  const closed = /```json\s*\n?([\s\S]*?)\n?\s*```/g;
  let match;
  while ((match = closed.exec(text)) !== null) {
    const result = tryParse(match[1]);
    if (result !== null) return result;
  }

  // 2. Unclosed ```json blocks (output truncated)
  const unclosed = /```json\s*\n?([\s\S]+)$/.exec(text);
  if (unclosed) {
    const result = tryParse(unclosed[1]);
    if (result !== null) return result;
  }

  // 3. Outermost { ... } block (no code fence)
  const braceStart = text.indexOf("{");
  const braceEnd = text.lastIndexOf("}");
  if (braceStart !== -1 && braceEnd > braceStart) {
    const result = tryParse(text.slice(braceStart, braceEnd + 1));
    if (result !== null) return result;
  }

  // 4. Raw text as JSON
  return tryParse(text);
}
```

**Fix (root cause):** Use `prepareStep` to remove tools on the last step, forcing pure text output:

```ts
const result = streamText({
  model,
  tools: { search: searchTool },
  stopWhen: stepCountIs(maxSteps),
  prepareStep: ({ stepNumber }) => {
    // Last step: no tools, model MUST output text (JSON)
    if (stepNumber >= maxSteps - 1) return { activeTools: [] };
    return {};
  },
  // ...
});
```

### Pattern 3: Optional Fields Omitted by Model

**Symptom:** Zod error `expected string, received undefined` on a field like `rationale`.

**Cause:** The LLM deems a field unnecessary and skips it. Common with `rationale`, `description`, `explanation` fields when the model puts that info elsewhere.

**Fix:** Make non-critical string fields optional with defaults:

```ts
const schema = z.object({
  level: z.enum(["high", "medium", "low"]),
  rationale: z.string().optional().default(""),
  gaps: z.array(z.string()).optional().default([]),
});
```

**Rule of thumb:** Any field that's "nice to have" for the UI (rationale, description, sources) should be `.optional().default(fallback)`. Only truly required fields (id, level, name) should be strict.

### Pattern 4: Repair Prompt Without Context

**Symptom:** First LLM call produces garbage (greeting, refusal, or incomplete JSON). Repair prompt also fails.

**Cause:** The repair prompt only includes the failed output, not the original input material. The repair model has no useful context.

**Fix:** Always include the original input in the repair prompt:

```ts
const repair = await generateText({
  model,
  prompt: [
    "Output the following as valid JSON...",
    "## Original input material",
    originalInput,              // THE KEY: include the source data
    "",
    previousOutput
      ? `## Previous attempt (may be incomplete)\n${previousOutput.slice(0, 4000)}`
      : "",
  ].filter(Boolean).join("\n"),
});
```

### Pattern 5: Enum Alias Mismatches

**Symptom:** Model uses `"high"` when schema expects `"strong"`, or `"medium"` when schema expects `"moderate"`.

**Cause:** The model knows the concept but uses a different word. Common when the schema uses domain-specific enum values that differ from standard English (e.g., `strong/moderate/weak` instead of `high/medium/low`).

**Fix (prompt — primary):** List exact allowed values in the output format prompt with explicit warnings:

```
evidenceStrength: "strong" | "moderate" | "weak"（不得用 high/medium/low）
verdict: "leaning_bull" | "leaning_bear" | "inconclusive"（不得用 bullish/bearish/neutral）
```

**Fix (schema — safety net):** Map common aliases:

```ts
evidenceStrength: z.preprocess(
  (v) => (v === "high" ? "strong" : v === "medium" ? "moderate" : v === "low" ? "weak" : v),
  z.enum(["strong", "moderate", "weak"])
),
```

## Defensive Schema Design Checklist

When defining a Zod schema for LLM output:

- [ ] **Prompt explicitly lists all enum values** with a "语言规则" section separating enum values (English) from content (target language)
- [ ] **Every enum field** has a lightweight `z.preprocess` safety net (non-matching → sensible default)
- [ ] **Every non-critical string field** (rationale, description, sources) uses `.optional().default("")`
- [ ] **Every non-critical array field** (gaps, sources, tags) uses `.optional().default([])`
- [ ] **Numeric fields that might be strings** have `z.preprocess((v) => typeof v === "string" ? parseFloat(v) : v, z.number())`
- [ ] **`extractJsonBlock`** handles: closed blocks, unclosed blocks, bare `{...}`, and uses `jsonrepair`
- [ ] **Multi-step agents** use `prepareStep` to remove tools on the last step
- [ ] **Repair prompts** include the original input material, not just the failed output

## AI SDK Specific Notes

- `streamText` with `stopWhen: stepCountIs(N)` stops after N steps. If the model uses ALL steps for tool calls, it never produces text output. Use `prepareStep` to force the last step to be text-only.
- `textStream` yields text from ALL steps concatenated. If the model writes partial text across steps, the concatenation may contain text + JSON fragments.
- `maxOutputTokens` applies per step, not total. A 32K limit per step is usually sufficient for structured output.
- When using `generateText` (not streaming), the model naturally completes its output. `streamText` with multi-step tool loops is where truncation issues arise.
