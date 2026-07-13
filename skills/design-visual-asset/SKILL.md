---
name: design-visual-asset
description: Production workflow for a visual asset with adaptive fast/guided/studio routing, rights and privacy preflight, cost preview, user selection of concrete drafts, artifact-anchored refinement, final-file QA, accessibility, and provenance-aware delivery.
version: 2.0.0
---

# Skill: design-visual-asset

Use this skill for a production-ready image, illustration, photo, or graphic.
The workflow's invariant is simple: **approve, refine, inspect, and deliver
artifacts—not prompts**.

## 0. Select the workflow and open an artifact record

Honor an explicit user choice. Otherwise choose:

- **Fast** — one fully specified, low-risk image or edit. Preflight, call the
  tool directly, inspect the output, and deliver.
- **Guided** — one image with aesthetic or technical ambiguity. Use only the
  specialist whose judgment resolves that ambiguity, then generate and QA.
- **Studio** — campaigns, batches, reference/identity images, costly output,
  public-facing work, or high-consequence edits. Run every gate below.

Before uploading a reference or generating, apply
`imagen:context/image-production-policy.md`. Confirm rights and consent when
unclear; disclose external-provider upload of sensitive images; minimize data;
and do not remove watermarks, signatures, provenance marks, or safety labels.

Open a machine-readable artifact record using
`imagen:schemas/artifact-manifest.schema.json`. Record each source, draft, branch, and
final candidate as a distinct artifact with a stable ID and parent relationship.

## 1. Establish the creative brief

If the request is already complete, normalize it into this brief. Otherwise
delegate to `imagen:image-director` and ask no more than 3–5 focused questions.

- Intent and intended use
- Scene/background and subject
- Style, lighting, palette, mood
- Framing, safe areas, and target dimensions
- Literal text and brand/source assets
- Provider preference and constraints
- Rights, consent, privacy, and disclosure notes
- Acceptance criteria and approver

Do not proceed until the acceptance criteria can be checked against an image.

## 2. Validate live capability, cost, and user intent

Treat the mounted tool schemas as authoritative. Use `list_providers` when
provider availability is uncertain and `estimate_cost` before a Studio batch or
expensive final render. Surface that the estimate is approximate.

For Studio mode, show the brief, planned provider/model, dimensions, draft
count, cost estimate, and sensitive-data handling, then obtain user approval
before generation.

GPT Image 2 rules:

- Prompt order: background/scene → subject → key details → constraints, plus
  intended use.
- Size: `auto` or dimensions whose edges are multiples of 16, max edge 3840,
  ratio at most 3:1, and 655,360–8,294,400 total pixels.
- Transparent backgrounds are unsupported.
- Omit `input_fidelity`; image inputs are always processed at high fidelity.

## 3. Engineer the production prompt

Delegate to `imagen:image-prompt-engineer` when provider choice or technical
encoding is material. Require this output:

1. Provider/model and rationale
2. Exact prompt
3. Complete parameters validated against the live schema
4. Draft count and expected cost/latency tradeoff
5. Preserve/exclusion constraints
6. Source-reference mapping by index and description

Never ask the prompt engineer to soften, disguise, or rephrase content to evade
a provider safety decision.

## 4. Generate named drafts

Generate low-cost drafts first (`quality="low"` for GPT Image 2 or an
appropriate verified Gemini draft setting). Use `generate_image_batch` for
independent multi-prompt work; use bounded concurrency. Give every output a
human-readable label and artifact ID, save its path and hash, and record the
provider response metadata.

Do not overwrite drafts. Provider errors are part of the record:

- Retry transient rate-limit/server failures with bounded backoff.
- Do not automatically retry a moderation-blocked or other user error.
- Give the user a generic safety message; keep request ID, stable error code,
  stage, and coarse categories in developer diagnostics.
- A new attempt requires a substantive, policy-compliant change approved by
  the user—not a filter-bypass paraphrase.

## 5. QA drafts and obtain selection

Delegate visual comparison to `imagen:image-researcher` only when the actual
candidate pixels are attached to a vision-capable context. A path or successful
file read check is not visual access. Otherwise perform deterministic file
checks, ask the user to review the candidates, and keep visual QA pending.
When pixels are available, inspect the actual files and score:

1. Brief adherence
2. Composition
3. Lighting
4. Color
5. Mood
6. Literal-text accuracy
7. Identity/reference fidelity
8. Accessibility at intended display size
9. Policy and rights concerns

Present previews or a contact sheet labeled with artifact IDs, plus a short
tradeoff summary. In Studio mode, **stop for the user's selection or rejection**.
Do not silently choose the winner. Record the selected artifact and approver.

## 6. Refine the selected artifact

For local changes, delegate to `imagen:image-editor` and edit the selected
file. Sequence structural → targeted → atomic changes. Restate invariants on
every step, inspect each output, and branch from the last accepted artifact if
an edit fails.

For a fundamentally different composition, return to prompt generation. That
output is a new draft—not an upscale or refinement of the selected image—and
must return to Step 5 for selection.

Limit full direction loops to three. Then summarize what was tried and ask the
user for new direction.

## 7. Create and QA the production candidate

The selected draft may already be the production candidate. If the user needs a
higher-quality or different-size render, make one with the approved constraints
and label it as a **new artifact**; rerunning the same prompt can change the
composition.

Run QA on the exact candidate file after every final render or edit. Compare it
with the approved parent, verify dimensions/format and on-image text, inspect
for collateral edits, and check the acceptance criteria. If it fails, do not
deliver it as final; return to the last approved artifact.

For sensitive output, inspect and remove location/EXIF metadata with an
appropriate local tool, then verify the cleaned copy. Never claim metadata was
removed without checking the delivered file.

## 8. Accessibility, provenance, and delivery

Deliver:

1. Inline preview when the client supports it and a stable final path
2. Final artifact ID, dimensions, format, provider/model, and selected parent
3. Concise alt text focused on purpose and meaningful content
4. Plain-text transcript of literal on-image text
5. QA/approval status and any known limitations
6. Rights/consent and synthetic-edit disclosure appropriate to the use
7. The artifact manifest and source/edit lineage

Do not claim authenticity credentials, C2PA provenance, or invisible
watermarking unless those were actually produced and verified.

## Completion checklist

- [ ] Rights/consent/privacy preflight completed
- [ ] Live tool schema and provider availability checked
- [ ] Studio brief/cost plan approved
- [ ] Drafts saved and QA'd as separate artifacts
- [ ] User selected the concrete draft in Studio mode
- [ ] Refinement branched from the selected/last-good file
- [ ] Exact final file passed visual and technical QA
- [ ] Alt text and literal-text transcript supplied
- [ ] Artifact manifest complete and provenance claims verified
