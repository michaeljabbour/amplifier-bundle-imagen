# Tool Reference

The MCP `tools/list` response and mounted Amplifier schemas are the executable
contract. This document explains intent and safe composition; it deliberately
does not duplicate every field. Reject unknown parameters rather than guessing.

## Current surface

| Tool | Purpose | Side effects |
|---|---|---|
| `generate_image` | Generate one request through OpenAI/Gemini with optional explicit routing | Provider call and saved image(s) |
| `generate_image_batch` | Generate independent items concurrently with bounded concurrency | Multiple provider calls and files |
| `conversational_image` | Start or continue an iterative provider-backed image thread | Provider call, files, conversation state |
| `edit_image` | Edit an existing file through the OpenAI image-edit workflow | Provider call and new file(s) |
| `estimate_cost` | Approximate cost without generating | Read-only local estimate |
| `list_providers` | Inspect configured providers and live capabilities | Read-only |
| `list_conversations` | Inspect resumable conversation state | Read-only |
| `list_gemini_models` | Query Gemini image-model availability | Read-only network query |

If `tools/list` returns a different surface, use the live result and report the
contract drift rather than fabricating a call.

## `generate_image`

Always provide a non-empty prompt. Optional fields cover provider/model routing,
provider-specific dimensions, quality/format, reference inputs, Search,
variant count, response format, and a stable output path. Pass only fields in
the live schema.

GPT Image 2:

- Prompt order: background/scene → subject → key details → constraints.
- `size` may be `auto` or constrained dimensions: edges are multiples of 16,
  max edge 3840px, ratio ≤3:1, and total pixels 655,360–8,294,400.
- Transparent background is unsupported.
- PNG, JPEG, and WebP are supported; compression applies to JPEG/WebP.
- Low quality is useful for drafts. Inspect medium/high for production-sensitive work.

Gemini 3 image:

- Nano Banana 2 GA ID: `gemini-3.1-flash-image`; 0.5K/1K/2K/4K, default 1K.
- Nano Banana Pro GA ID: `gemini-3-pro-image`; 1K/2K/4K, default 1K.
- Optional Lite ID: `gemini-3.1-flash-lite-image`; 1K only, no Search.
- Preview IDs shut down June 25, 2026.

## `generate_image_batch`

Use for independent prompts, not sequential edits. Set a bounded concurrency
appropriate to rate limits. Assign each item a distinct output path and artifact
ID. One item failure must remain attributable to that item; do not discard
successful outputs or automatically rephrase blocked items.

Before a costly Studio batch, call `estimate_cost`, show the approximate total,
and obtain approval.

## `conversational_image`

Use when continuity benefits from provider-backed conversation state. Record
the conversation ID and provider/model. A conversational response is still a
new artifact; save and QA its concrete file. Do not assume a conversation
preserves every visual detail.

Conversational mode persists prompts and prior image bytes locally so a later
turn can edit the actual predecessor. Use it only when resumability is needed,
keep the storage directory private, and retain the default 30-day cleanup (or
set a shorter `conversation_retention_days`) for sensitive work.

## `edit_image`

Supply the actual accepted `image_path`, an imperative edit prompt, and an
optional valid mask. Save every output separately and record its parent.

For GPT Image 2, omit `input_fidelity`; it automatically processes every input
image at high fidelity. High fidelity and masks do not guarantee byte-identical
preservation or exact mask boundaries. Compare output with parent and repeat
important invariants in every prompt.

GPT Image 2 does not support transparent output. A mask's alpha channel guides
where to edit; it is not a request for a transparent final background.

## `estimate_cost`

Pass the same routing, dimensions, quality, and count intended for generation.
Treat the result as a ballpark: live billing may include prompt text, reference
image input, output tokens, and price changes. Record estimate time and inputs.

## Inspection tools

- Call `list_providers` before relying on auto-routing or when a key/model is uncertain.
- Use `list_gemini_models` to confirm optional/GA model availability; do not switch
  to a preview ID that has shut down.
- Use `list_conversations` only for state the user is authorized to access.

## Errors

- Retry transient rate-limit and server failures with bounded backoff.
- Do not automatically retry moderation-blocked or other user errors.
- Do not disguise or paraphrase a request to evade a safeguard or switch
  providers for safeguard shopping.
- Show a generic user message; retain request ID, stable code, provider,
  moderation stage, and coarse categories in developer diagnostics.
- Never log API keys or raw sensitive reference data.

## Artifact record

Every side-effecting call should record:

- artifact and parent IDs
- stable output path and content hash
- timestamp, provider/model, and parameters
- prompt or privacy-preserving prompt hash
- source image hashes and consent/rights assertion
- request/conversation ID when available
- QA status, approver, alt text, and literal-text transcript
- errors and branch decisions

Use `imagen:schemas/artifact-manifest.schema.json` for machine-readable records.
