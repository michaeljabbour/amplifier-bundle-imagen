# Prompt Engineering Guide

Reference for `imagen:image-prompt-engineer`. Validate parameters against the
mounted tool schema; this guide supplies workflow and wording, not a substitute
for the live contract.

## Start with the intended use

Name the deliverable—ad, editorial opener, UI mockup, infographic, portrait,
product page, or concept frame. Intended use sets the polish level, hierarchy,
safe areas, and accessibility checks. Then identify acceptance criteria that can
be verified against an actual file.

## GPT Image 2 prompting

Use the current OpenAI-recommended order:

1. **Background/scene** — place, time, atmosphere, scale, and composition.
2. **Subject** — appearance, pose/action, gaze, framing, and spatial relationship.
3. **Key details** — medium, materials, lighting, palette, texture, typography.
4. **Constraints** — intended use, exact text, placement, invariants, exclusions, safe areas.

For complex requests, use short labeled segments or line breaks. A paragraph,
JSON-like block, or tags can all work; choose the most maintainable form.

```text
Background/scene: Rainy independent café at dusk, warm interior against cool street light.
Subject: One reader at the right third, hands around a ceramic mug, looking at the book.
Key details: Editorial photograph, diffuse window light, mild grain, muted amber and blue.
Constraints: Magazine opener; clean negative space at left; no logos or extra people.
```

### Composition and people

- Specify shot distance, viewpoint, angle, lighting, and placement.
- Describe people by scale, full/partial body framing, gaze, and interaction
  with objects. Do not rely on camera-model trivia for exact physical simulation.
- Say `photorealistic` when that mode is required, then add concrete materials,
  textures, and lighting rather than stacking vague quality adjectives.

### Literal text

- Put exact copy in quotes or ALL CAPS and specify style, size, color, and placement.
- Spell out unusual names when character accuracy is critical.
- Use medium/high comparisons for dense or small text and verify every character
  in the delivered file. Model-rendered copy is never proofread by assumption.
- Supply the final copy as a plain-text transcript for accessibility.

### Reference inputs and edits

- Label each source by index and role: `Image 1: product source`, `Image 2: style reference`.
- State which details may change and which must remain invariant on every edit.
- For a focused edit, say “change only X; keep everything else the same,” then
  list important layout, label, camera-angle, and color invariants.
- GPT Image 2 processes image inputs at high fidelity automatically. Omit
  `input_fidelity`; a mask guides but does not guarantee exact isolation.

### Parameters

| Parameter | Current GPT Image 2 rule |
|---|---|
| `quality` | `auto`, `low`, `medium`, `high`; start low for drafts, compare higher for production-sensitive work |
| `size` | `auto` or dimensions with 16px-multiple edges, max 3840px edge, ratio ≤3:1, 655,360–8,294,400 total pixels |
| `background` | `auto` or opaque; transparent output is unsupported |
| output format | PNG, JPEG, or WebP; JPEG is useful when latency matters, compression applies to JPEG/WebP |
| `n` | Use multiple named drafts for exploration when supported; do not silently select for the user in Studio mode |

Outputs above 3,686,400 pixels are currently experimental. A 4K request is not
by itself a reason to leave OpenAI; select the provider by the whole workflow.

## Gemini 3 image prompting and models

Gemini also benefits from explicit scene, subject, details, and constraints.
Photography-oriented work can add high-level lens/framing and lighting language,
but prioritize visible outcomes over an over-specified camera simulation.

| Model | Output sizes | Reference limits | Search | Provenance |
|---|---|---|---|---|
| `gemini-3.1-flash-image` / Nano Banana 2 | 0.5K, 1K, 2K, 4K; default 1K | up to 10 objects / 4 characters | Yes | SynthID |
| `gemini-3-pro-image` / Nano Banana Pro | 1K, 2K, 4K; default 1K | up to 6 objects / 5 characters / 3 styles, 14 total | Yes | SynthID |
| `gemini-3.1-flash-lite-image` | 1K only | validate live | No | SynthID + C2PA |

Use GA IDs. Preview IDs shut down June 25, 2026.
Gemini 3.1 Flash and Flash Lite accept optional `thinking_level` values
`minimal` and `high`; validate against the selected model. Google Search
grounding is opt-in and requires presenting the returned Search Suggestions and
source citations to the user.

Reference mapping example:

```text
Image 1: authorized product photograph; preserve geometry, label, and materials.
Image 2: approved campaign anchor; carry forward palette and lighting only.
Scene: slate studio surface with soft side light and negative space at right.
Subject: place the product from Image 1 at the left third.
Constraints: do not invent marks or change label text; intended for a web hero.
```

## Iteration discipline

1. Diagnose one failure axis: composition, subject, lighting, palette, text, or continuity.
2. Make the smallest prompt delta that addresses it.
3. Preserve successful details explicitly.
4. Edit the selected artifact for local changes; regenerate only for a new composition.
5. Treat every regeneration or higher-quality rerender as a new artifact.
6. QA the exact new file and return it for user selection when direction changes.

Avoid long negative-only lists. Express the desired positive state, then add
short exclusions or invariants. Avoid style-name cargo culting; describe the
visible properties required and respect source/reference rights.

## Safety failures

- Keep moderation enabled.
- Do not automatically retry moderation-blocked or other user errors.
- Do not disguise, split, euphemize, or generically reword a request to bypass
  provider safeguards.
- Give the user a generic message; retain request ID, stable error code,
  moderation stage, and coarse public categories in developer diagnostics.
- Retry only transient failures automatically. A user-error retry needs a
  substantive, policy-compliant change to the request or inputs.

## Sources

- OpenAI image generation: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI GPT Image prompting guide: https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide
- Google Gemini image generation: https://ai.google.dev/gemini-api/docs/image-generation
