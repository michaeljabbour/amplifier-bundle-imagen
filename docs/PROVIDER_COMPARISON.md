# Provider Comparison Guide

Use this guide for routing judgment, then validate the actual request against
the mounted tool schema and `list_providers`. Capability and price claims drift;
the live provider contract wins.

## Current model roster

| Provider/model | Size choices | Reference inputs | Search | Provenance signal |
|---|---|---|---|---|
| OpenAI `gpt-image-2` | `auto` or constrained `WIDTHxHEIGHT`, up to a 3840px edge | Image edits and references; always processed at high fidelity | No | Do not claim a credential unless separately produced and verified |
| Google `gemini-3.1-flash-image` (Nano Banana 2) | 0.5K, 1K, 2K, 4K; default 1K | Up to 10 objects and 4 characters | Yes | SynthID |
| Google `gemini-3-pro-image` (Nano Banana Pro) | 1K, 2K, 4K; default 1K | Up to 6 objects, 5 characters, and 3 style references; 14 total | Yes | SynthID |
| Google `gemini-3.1-flash-lite-image` | 1K only | Validate live | No | SynthID and C2PA |

The Gemini preview IDs shut down on June 25, 2026. Use the GA IDs above.

## GPT Image 2 constraints

- Prompt in the order background/scene → subject → key details → constraints,
  and state the intended use.
- Both size edges must be multiples of 16; maximum edge 3840px; long:short
  ratio at most 3:1; total pixels 655,360–8,294,400.
- Outputs above 3,686,400 pixels are currently described as experimental.
- `quality` supports `auto`, `low`, `medium`, and `high`. Start with `low` for
  drafts and compare higher tiers for dense text, identity-sensitive edits,
  close portraits, or production output.
- GPT Image 2 does not support transparent backgrounds.
- Omit `input_fidelity`; GPT Image 2 image inputs are always high fidelity.
- Masks guide edits but may not be followed with exact pixel boundaries.

## Routing axes

| Need | First choice | Why / caveat |
|---|---|---|
| Dense literal text, UI, diagram, or infographic | GPT Image 2 | Strong text-oriented workflow; still verify every character in the actual output |
| Targeted edit through this bundle's `edit_image` tool | GPT Image 2 | The current dedicated edit tool uses OpenAI; always compare output with its parent |
| Many visual references or Search-grounded context | Appropriate Gemini model | Reference limits and Search support differ by model; validate live |
| Lowest-cost 1K Gemini draft, no Search | Gemini Flash Lite | Optional model; confirm availability and reference needs |
| Fast Gemini iteration with flexible resolution | Nano Banana 2 | Supports 0.5K through 4K and more object references than Pro |
| Highest-fidelity Gemini work or multiple style references | Nano Banana Pro | Supports three style refs and up to 14 inputs total |
| 4K-class output | Either provider | 4K is not a provider-selection rule; choose by editing, reference, Search, and style needs |
| Transparent deliverable | Neither by assumption | GPT Image 2 cannot do it; use a separately verified provider or local cutout/compositing workflow |

Auto-selection is a convenience heuristic. Pin `provider`/model when a hard
requirement determines the choice, and record the override in the artifact
manifest.

## Cost discipline

Use `estimate_cost` before Studio batches and confirm current official pricing
for material spend. Estimates are approximate and do not replace provider bills.

Google standard image-output prices recorded for this 2026-07-13 guide:

| Model | Resolution | Standard output price |
|---|---:|---:|
| Nano Banana 2 | 0.5K / 1K / 2K / 4K | $0.045 / $0.067 / $0.101 / $0.151 |
| Nano Banana Pro | 1K or 2K / 4K | $0.134 / $0.24 |
| Gemini Flash Lite Image | 1K | $0.0336 |

OpenAI cost varies with text input, image inputs for edits, and image output
tokens. Larger dimensions do not always map monotonically to token cost. Use
the current OpenAI calculator/pricing page and the server estimator rather than
copying a historical per-image table.

## Workflow patterns

### Draft then select

1. Estimate cost.
2. Generate named low-cost drafts.
3. QA the actual files.
4. Show previews and let the user select in Studio mode.
5. Refine the selected artifact.
6. QA any new production render again.

### Reference-driven series

Use only authorized sources. Label every reference by index and purpose. Keep a
stable approved anchor, but do not overload the provider's model-specific
reference limits. Hash sources and record lineage in the artifact manifest.

### Targeted edit

Call `edit_image` on the last approved artifact. Omit `input_fidelity` for GPT
Image 2, state the change and invariants, and branch from the last good output
if the edit drifts. A mask is guidance, not a pixel lock.

## Safety and provenance

- Do not retry moderation-blocked/user errors unchanged or rephrase to evade a
  safeguard. Retry only after a substantive, policy-compliant user/input change.
- Do not remove watermarks, signatures, provenance marks, or safety labels.
- Gemini 3 image outputs include SynthID; Flash Lite also supports C2PA. Record
  the provider signal, but do not claim you independently verified it unless you did.
- Label synthetic/materially edited imagery when omission could mislead.

## Authoritative references

- OpenAI image generation: https://developers.openai.com/api/docs/guides/image-generation
- Google Gemini image generation: https://ai.google.dev/gemini-api/docs/image-generation
- Nano Banana 2 model: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-image
- Google pricing: https://ai.google.dev/gemini-api/docs/pricing
- Google model changelog: https://ai.google.dev/gemini-api/docs/changelog
