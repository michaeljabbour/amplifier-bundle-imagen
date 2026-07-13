# Imagen Capability Router

Imagen exposes the live `imagen-mcp` tool contract through native Amplifier
tools. Treat `tools/list` (and the mounted schemas) as authoritative; do not
invent arguments from prose documentation.

## Current Tool Surface

- `generate_image` — generate one or more images with OpenAI or Gemini.
- `generate_image_batch` — run independent prompts concurrently with bounded concurrency.
- `conversational_image` — continue a provider-backed refinement thread.
- `edit_image` — edit the actual source artifact; GPT Image 2 automatically processes image inputs at high fidelity.
- `estimate_cost` — preview an approximate cost without generating.
- `list_providers`, `list_conversations`, `list_gemini_models` — inspect live capabilities and saved state.

## Choose the Smallest Useful Workflow

Honor an explicit user choice of `fast`, `guided`, or `studio`. Otherwise:

| Mode | Use when | Route |
|---|---|---|
| **Fast** | One clear, low-risk generation or edit | policy preflight → direct tool call → file checks → capability-gated visual review → deliver |
| **Guided** | The request has aesthetic ambiguity or needs provider/parameter judgment | one relevant specialist → tool call → capability-gated review → deliver |
| **Studio** | Campaigns, batches, identity/reference images, costly work, public-facing assets, or high-consequence edits | brief → cost/capability preview → user approval → drafts → user selection → refinement of selected artifact → final QA → artifact pack |

Do not force delegation for a fully specified fast request. Use specialists
when their judgment changes the result:

| Specialist | Use for |
|---|---|
| `imagen:image-director` | creative ambiguity, visual systems, campaign consistency |
| `imagen:image-prompt-engineer` | provider-aware prompting and parameter validation |
| `imagen:image-editor` | edits to an existing artifact and multi-step edit branches |
| `imagen:image-researcher` | reference analysis, draft comparison, and final visual QA only when actual pixels are in vision context |

## Non-Negotiable Gates

1. Run the rights, consent, privacy, and safety preflight in
   `imagen:context/image-production-policy.md` before uploading references or
   generating sensitive content.
2. In Studio mode, show drafts and obtain the user's selection before final
   refinement. Do not silently choose on the user's behalf.
3. Refine the selected image or branch from its last approved ancestor. Reusing
   a prompt creates a new image; it is not an upscale of the approved draft.
4. Inspect and QA the exact file being delivered. A path or successful binary
   write is not visual access. If the runtime cannot expose the candidate's
   pixels to a vision model, run verifiable file checks, show the artifact to
   the user, require visual approval, and record visual QA as `pending` rather
   than claiming it passed. Any final re-render is a new artifact and must be
   reviewed again.
5. Deliver an inline preview when the client supports it, a stable path, concise
   alt text, and an artifact record with provider/model, parameters, lineage,
   rights/consent notes, and review status.

## GPT Image 2 Capability Notes

- Write prompts in this order: **background/scene → subject → key details → constraints**, and state the intended use.
- Valid sizes are constrained rather than a short fixed list: both edges must be multiples of 16; max edge 3840px; aspect ratio at most 3:1; total pixels 655,360–8,294,400.
- It does **not** support transparent backgrounds. Use an opaque background or a different verified workflow.
- Omit `input_fidelity` for GPT Image 2; image inputs are always processed at high fidelity.
