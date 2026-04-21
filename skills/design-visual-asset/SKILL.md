---
name: design-visual-asset
description: End-to-end pipeline for designing a production-ready visual asset — from an initial user brief through creative direction, prompt engineering, generation, critique, and iterative refinement to final delivery. Delegates each phase to the appropriate specialist agent.
version: 1.0.0
---

# Skill: design-visual-asset

Execute this skill when a user asks to design, create, generate, or produce a visual asset (image, illustration, photo, graphic) and you want the full pipeline: brief → prompt → generate → critique → refine → deliver.

This skill operates by **delegating each phase to the appropriate specialist agent**. The session itself does not do the creative or technical work — it orchestrates the pipeline by calling agents in sequence and passing outputs forward.

---

## Step 1 — Intake: Establish Creative Intent

**Goal**: Determine whether the user's request is fully specified or requires creative direction.

**Assessment criteria** (if all three are met, skip to Step 3):
- The user has provided a complete, specific description of the desired image.
- The style register is clearly named or unmistakably implied.
- The intended provider (OpenAI or Gemini) is determinable from the request.

**If the request is ambiguous or underspecified:**

Delegate to `imagen:image-director` with the user's raw request and the following instruction:
> "Review this image request and produce a complete Creative Brief using the template in your knowledge base. Ask the user 3–5 clarifying questions if needed to resolve: style register, lighting, color direction, mood, framing, and intended use."

Wait for the Creative Brief from `imagen:image-director` before proceeding.

**Outputs**: A complete Creative Brief document or confirmation that the user's request is already fully specified.

---

## Step 2 — Creative Brief Review

**Goal**: Confirm the brief is complete and ready for prompt engineering.

Check the brief produced in Step 1 against this checklist:
- [ ] Style register named (editorial / cinematic / documentary / conceptual / illustrative / graphic-design / product)
- [ ] Lighting specified (direction, quality, source type)
- [ ] Color palette and temperature specified
- [ ] Mood adjectives present (three max)
- [ ] Framing specified (aspect ratio, shot distance, composition rule)
- [ ] Provider recommendation included
- [ ] Intended use stated

If any item is missing, return to `imagen:image-director` with a specific request to complete the missing element.

**Outputs**: A verified, complete Creative Brief.

---

## Step 3 — Prompt Engineering

**Goal**: Translate the creative brief into model-ready prompts and parameter configurations.

Delegate to `imagen:image-prompt-engineer` with:
1. The complete Creative Brief from Step 2.
2. Any additional technical constraints the user specified (specific size, transparent background, output format, etc.).

Instruction to the prompt engineer:
> "Using the creative brief provided, craft a generation-ready prompt optimized for the recommended provider. Follow the five-element structure for OpenAI or the photography-vocabulary structure for Gemini. Select all parameters (quality, size, aspect_ratio, background, output_format, etc.) to match the brief's intended use."

**Outputs**: A finalized prompt string, provider selection, and complete parameter list.

---

## Step 4 — Generation

**Goal**: Call `generate_image` with the engineered prompt and parameters.

Using the prompt and parameters from Step 3, call `generate_image`. For the first attempt:
- Use `quality="medium"` or Gemini `size="2K"` — not maximum quality yet (save cost for confirmed direction).
- If the brief calls for variants, use `n=2` or `n=3` (OpenAI only) to generate alternatives.

Record the output path(s) for Step 5.

**Decision point**: If the user wants visual exploration before committing, use `conversational_image` with `dialogue_mode="skip"` instead of `generate_image` directly. This establishes a conversation thread that supports seamless refinement.

**Outputs**: Generated image file path(s).

---

## Step 5 — Critique

**Goal**: Evaluate the generated image(s) against the creative brief.

Delegate to `imagen:image-researcher` with the generated image path(s) and the creative brief. Instruction:
> "Perform a visual analysis of this generated image and compare it against the following creative brief. Identify the top 1–3 divergences between the brief and the generated image. Format your critique using the five-axis scoring framework (brief adherence, compositional quality, lighting execution, color fidelity, mood resonance). Provide specific revision instructions for any axis scoring below 7."

**Decision points**:
- **All axes ≥ 7**: Accept the image and proceed to Step 6 (delivery).
- **1–2 axes below 7**: Proceed to Step 5b (prompt refinement).
- **3+ axes below 7 or overall composition is wrong**: Proceed to Step 5c (re-generation).
- **Structural composition is right but details need adjustment**: Proceed to Step 5d (edit chain).

---

## Step 5b — Prompt Refinement (Minor Issues)

**Goal**: Improve specific failing axes without re-doing the full pipeline.

Return to `imagen:image-prompt-engineer` with:
1. The original creative brief.
2. The critique from Step 5 (specific axis scores and revision instructions).

Instruction:
> "Refine the generation prompt to address the specific issues identified in the critique. Do not alter elements that scored 7 or above. Focus only on the failing axes."

After receiving the refined prompt, return to Step 4 with `quality="medium"` for another iteration.

---

## Step 5c — Re-Generation (Major Issues)

**Goal**: Start over with a more precisely specified brief when the overall direction is wrong.

Return to `imagen:image-director` with:
1. The original brief.
2. The generated image path (for visual reference).
3. The critique analysis.

Instruction:
> "The generation significantly diverges from the brief in [list failing axes]. Please review and revise the brief to provide more precise specifications for these elements."

After receiving the revised brief, return to Step 3 (prompt engineering) and then Step 4 (generation).

Limit re-generation cycles to **3 total iterations** before escalating to the user with a summary of what's been tried and requesting additional guidance.

---

## Step 5d — Edit Chain (Right Composition, Wrong Details)

**Goal**: Use `edit_image` to make surgical corrections without re-generating the whole image.

Delegate to `imagen:image-editor` with:
1. The accepted base image path.
2. The critique's specific revision instructions (translated to edit prompts).

Instruction:
> "Use `edit_image` with `input_fidelity=high` to correct the following specific issues in the image. Use the three-tier sequencing rule (structural edits first, targeted second, atomic last). For each edit step, provide the output path."

After the edit chain completes, return the final edit output path to Step 6.

---

## Step 6 — Final Production Render (if not already at max quality)

**Goal**: Produce the final deliverable at maximum quality.

If the accepted image was generated at medium quality, produce a final high-quality render:

- **OpenAI**: Re-run with the accepted prompt at `quality="high"` and the final size/format from the brief.
- **Gemini**: Re-run with the accepted prompt at `size="4K"` (if the brief calls for high resolution) or `size="2K"`.

If the accepted image already used maximum quality parameters (or was produced by `edit_image`), skip this step and proceed directly to delivery.

---

## Step 7 — Delivery

**Goal**: Present the final image to the user with a summary.

Report to the user:
1. The final image file path.
2. A brief description of what was produced (style register, key visual decisions, provider used).
3. The full generation pipeline used (which steps executed, any iterations required).
4. Next steps the user can take:
   - "Request iterative edits via `imagen:image-editor`"
   - "Generate variants with a modified brief"
   - "Use `conversational_image` to continue exploration in the same thread"

---

## Pipeline Summary

```
User Request
    │
    ▼
Step 1: intake + brief (imagen:image-director if needed)
    │
    ▼
Step 2: brief verification
    │
    ▼
Step 3: prompt engineering (imagen:image-prompt-engineer)
    │
    ▼
Step 4: generation (generate_image)
    │
    ▼
Step 5: critique (imagen:image-researcher)
    │
    ├── all good → Step 6
    ├── minor issues → Step 5b → Step 4
    ├── major issues → Step 5c → Step 3
    └── edit needed → Step 5d (imagen:image-editor)
                          │
                          ▼
Step 6: final production render (if needed)
    │
    ▼
Step 7: delivery
```

---

## Guardrails

- **Do not skip the critique step** for any non-trivial asset. Brief adherence without objective evaluation risks delivering images that satisfy the prompt but not the intent.
- **Do not run more than 3 full generation loops** without escalating to the user. If the model consistently fails to hit the brief after three refined prompts, the brief may need fundamental revision.
- **Do not start an edit chain before establishing a good base image**. An edit chain that starts from a weak generation will never fully converge.
- **Preserve the output path at every step**. The edit chain depends on having the correct preceding step's output path. Log each step's output.
