# Model Selection Guide — Image Generation

Choose a provider from hard workflow requirements, then validate availability
with `list_providers` and the live tool schema. Do not route on brand folklore,
unverified quality percentages, or “4K” alone.

## Decision card

| Requirement | Route | Verification |
|---|---|---|
| Dense literal text, UI, diagram, infographic | GPT Image 2 first | Proofread every character in the actual output |
| Targeted edit through `edit_image` | GPT Image 2 | Edit selected artifact; omit `input_fidelity`; compare with parent |
| Search-grounded image context | Nano Banana 2 or Pro | Confirm Search is enabled and source use is appropriate |
| Many object references | Nano Banana 2 | Max 10 objects, 4 characters |
| Multiple style references / highest-fidelity Gemini route | Nano Banana Pro | Max 6 objects, 5 characters, 3 style refs, 14 total |
| Lowest-cost 1K Gemini draft without Search | Gemini Flash Lite Image | Optional; 1K only, validate availability |
| 4K-class output | Either GPT Image 2 or supported Gemini model | Select on editing/reference/Search/style needs, then verify dimensions |
| Transparent final | Separate verified cutout/compositing workflow | GPT Image 2 does not support transparency |

The current GA Gemini IDs are `gemini-3.1-flash-image`,
`gemini-3-pro-image`, and optional `gemini-3.1-flash-lite-image`. Preview IDs
shut down June 25, 2026.

Search grounding has a presentation obligation: deliver the provider-returned
Google Search Suggestions and source citations with the result. Do not enable
grounding in a client path that cannot preserve and show them.

## GPT Image 2 facts that affect routing

- Accepts `auto` or constrained resolutions: edges are multiples of 16, max
  edge 3840px, ratio ≤3:1, and 655,360–8,294,400 total pixels.
- Outputs above 3,686,400 pixels are experimental.
- Does not support transparent backgrounds.
- Always processes image inputs at high fidelity; omit `input_fidelity`.
- In imagen-mcp conversational mode, each continuation edits the persisted
  prior output and returns a new artifact; one-shot generation does not retain
  conversation state.

## Gemini facts that affect routing

| Model | Size | Reference limits | Search | Signal |
|---|---|---|---|---|
| Nano Banana 2 | 0.5K/1K/2K/4K; default 1K | 10 objects / 4 characters | Yes | SynthID |
| Nano Banana Pro | 1K/2K/4K; default 1K | 6 objects / 5 characters / 3 styles; 14 total | Yes | SynthID |
| Flash Lite Image | 1K only | validate live | No | SynthID + C2PA |

## Cost-aware selection

Call `estimate_cost` for the intended prompt, provider, dimensions, quality,
and count. For Studio batches, surface the estimate and obtain approval before
generating. Provider estimates are approximate and prices can change.

Google standard output prices recorded on 2026-07-13:

- Nano Banana 2: $0.045 / $0.067 / $0.101 / $0.151 at 0.5K / 1K / 2K / 4K.
- Nano Banana Pro: $0.134 at 1K or 2K; $0.24 at 4K.
- Flash Lite Image: $0.0336 at 1K.

For GPT Image 2, total cost includes prompt text, input images for edits, and
image output tokens. Use current pricing/calculators rather than a historical
fixed range.

## Override discipline

Respect the user's explicit provider/model pin if it is supported and safe.
Explain any capability conflict before changing it. Record the pin and reason
in the artifact manifest.

Do not automatically fall back to another provider after a moderation block;
that can become safeguard shopping. A provider change requires a legitimate
capability reason and a substantive policy-compliant request.

## Visual-analysis routing

Use the available vision-capable orchestrator for reference analysis and final
QA. Model names and cost tiers for orchestration change independently of image
generation, so do not hard-code them here. The QA task must inspect the actual
file and compare it with the brief, authorized sources, and parent artifact.

## Sources

- https://developers.openai.com/api/docs/guides/image-generation
- https://ai.google.dev/gemini-api/docs/image-generation
- https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-image
- https://ai.google.dev/gemini-api/docs/pricing
