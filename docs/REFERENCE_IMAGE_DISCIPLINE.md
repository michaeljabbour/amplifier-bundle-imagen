# Reference-Image Discipline

Use references for continuity only after the rights, consent, and privacy
preflight. Possession of an image does not establish permission to upload,
transform, or reproduce a person's likeness or a protected asset.

## Choose an anchor

For a campaign or sequence, designate one approved artifact as the persistent
visual anchor and record its hash. Use the immediate predecessor for local
continuity and the anchor for campaign-level palette, lighting, or identity.
Every new image is still a distinct artifact and must be QA'd.

```text
shot-01 (approved anchor)
  └─ shot-02 references shot-01
       └─ shot-03 references shot-02 + shot-01
```

Do not claim that references guarantee identity or exact brand reproduction.
Compare generated results with authorized sources and reject drift.

## Label references by role

Map each input explicitly in the prompt:

```text
Image 1: authorized product source; preserve geometry and label.
Image 2: approved campaign anchor; carry forward palette and lighting only.
Image 3: composition reference; do not copy logos, people, or text.
```

This prevents ambiguity about which source supplies subject, style, setting, or
composition. Avoid unnecessary references; each upload increases privacy and
cost exposure.

## Current Gemini model limits

| Model | Limits | Output sizes | Other |
|---|---|---|---|
| Nano Banana 2 (`gemini-3.1-flash-image`) | up to 10 objects and 4 characters | 0.5K, 1K, 2K, 4K; default 1K | Search, SynthID |
| Nano Banana Pro (`gemini-3-pro-image`) | up to 6 objects, 5 characters, 3 style refs; 14 total | 1K, 2K, 4K; default 1K | Search, SynthID |
| Gemini Flash Lite Image (`gemini-3.1-flash-lite-image`) | validate live before reference-heavy use | 1K only | no Search; SynthID + C2PA |

Use GA IDs; preview IDs shut down June 25, 2026. Treat live provider schemas as
authoritative if these limits change.

## GPT Image 2 targeted continuity

For a change to one approved composition, use `edit_image` on that actual file.
GPT Image 2 processes image inputs at high fidelity automatically, so omit
`input_fidelity`. State the requested change and repeat all important invariants.
High fidelity and masks reduce drift but do not make unedited regions
pixel-identical; compare the output with its parent.

For a fundamentally new composition, create a new draft and return it to the
selection gate instead of describing it as a refinement of the old image.

## Reference selection

Rank candidates by the property the new frame must preserve:

1. Authorized identity/asset fidelity
2. Lighting and setting match
3. Composition and shot-distance match
4. Technical quality and clarity

The strongest face crop may be a poor primary reference for a wide scene in
different lighting. Explain each reference's role rather than relying on order
alone.

## Input hygiene

- Crop or redact unrelated people, location clues, account data, and secrets.
- Use the smallest sufficient image; do not apply undocumented dimension
  folklore. Validate provider limits and check whether preprocessing altered
  identity, color, or text.
- Hash the source and retain the authorized original outside public output dirs.
- Do not strip watermarks or provenance marks to improve conditioning.
- Tell the user that selected references leave the machine for the external provider.

## QA and provenance

For each result, record source IDs/hashes, model, parameters, prompt or private
prompt hash, parent artifact, approver, and continuity findings. Inspect:

- identity and object geometry
- authorized labels/marks and literal text
- palette, lighting, setting, and camera relationship
- unrequested additions/removals
- harmful or misleading changes
- provider provenance signals (without claiming independent verification)

Reject drift and branch from the last accepted artifact. Do not average away
identity differences across a sequence or silently approve on the user's behalf.

Google references:

- https://ai.google.dev/gemini-api/docs/image-generation
- https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-image
