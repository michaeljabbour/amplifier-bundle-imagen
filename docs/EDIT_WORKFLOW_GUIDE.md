# Edit Workflow Guide

Reference for `imagen:image-editor`. The durable unit of an edit workflow is an
artifact lineage: every step names its parent, preserves the last accepted file,
and records why a branch was accepted or rejected.

## GPT Image 2 input behavior

GPT Image 2 always processes input images at high fidelity. Omit
`input_fidelity`; the API does not allow changing it for this model. High
fidelity is not a promise that unchanged pixels will be byte-identical. Compare
every output with its parent and state invariants explicitly.

GPT Image 2 does not support transparent output. For a transparent deliverable,
use a separately verified provider or an authorized local cutout/compositing
step and QA the resulting alpha channel.

## Sequence structural → targeted → atomic

1. **Structural** — background replacement, reframing, global lighting/time of
   day, large added/removed elements.
2. **Targeted** — one object's color/material, wardrobe, medium-sized object,
   localized lighting.
3. **Atomic** — small cleanup, grain, haze, catchlight, minor typography fix.

Structural changes alter the context used by later edits. Confirm them before
spending detail work.

## Prompt pattern

Use an imperative change followed by preservation clauses:

```text
Change [specific element] at [location] to [desired state].
Keep [identity/geometry/layout/lighting/labels] unchanged.
Do not alter [critical surrounding elements].
```

Repeat critical invariants on every iteration. Small, single-change follow-ups
are easier to diagnose than overloaded edits.

## Mask use

Use a mask when the change must be spatially confined or surrounding content is
complex. Skip it for global grading or lighting changes.

- Source and mask must have the same format and dimensions and be under the
  provider's current size limit.
- The mask must contain an alpha channel.
- The mask is prompt guidance; the model may not follow its exact shape.
- Protecting a region in a mask does not replace visual comparison afterward.

Do not use masks to remove watermarks, signatures, provenance marks, or safety
labels. A rights-holder's restoration of their own damaged source must preserve
the original and the transformation record.

## Edit chain protocol

For each step:

1. Select the last accepted artifact, never a failed output.
2. Classify the change as structural, targeted, or atomic and reorder if needed.
3. Decide whether a mask improves localization.
4. Record the prompt, source hash, and intended invariants.
5. Call `edit_image` on the accepted source; omit `input_fidelity` for GPT Image 2.
6. Save to a new stable path and record its parent artifact ID.
7. Inspect for the requested change, collateral drift, text/identity changes,
   and policy concerns.
8. Accept, reject, or branch. Never overwrite the parent.

## Example chain

```text
base (approved product photo)
  └─ step-1: replace background with a clean warm-grey studio sweep
       ├─ step-2a: change accent to authorized brand navy  ← accepted
       │    └─ step-3: add a subtle floor reflection       ← final candidate
       └─ step-2b: alternate accent                         ← rejected, retained in log
```

At each step, preserve the authorized label artwork, product geometry, camera
angle, and existing contact shadow unless the user explicitly changes them.

## Failure recovery

| Failure | Response |
|---|---|
| Scope bleed | Return to the parent, tighten invariants, and consider a mask |
| Under-application | Return to the parent and make the imperative more specific |
| Composition/identity drift | Reject the output; split the edit into smaller steps |
| Text corruption | Return to the parent; quote exact copy and QA character-by-character |
| Blocked/user error | Do not retry unchanged or paraphrase to evade; ask for a substantive policy-compliant change |
| Rate limit/server error | Bounded retry/backoff; preserve request diagnostics |

After three failed branches, summarize the evidence and ask the user for new
direction instead of continuing to spend.

## Final QA

The final candidate must be checked after the final edit—not inferred from the
accepted parent. Verify file readability, dimensions, format, requested change,
preserved details, literal text, accessibility, metadata handling, and artifact
manifest completeness. Any cleanup or export creates a new file that must be
verified again.

Authoritative OpenAI reference:
https://developers.openai.com/api/docs/guides/image-generation#edit-images
