# Edit Workflow Guide

Reference for `imagen:image-editor` — how `edit_image` with `input_fidelity=high` works, how to sequence multi-step edits, when to use masks, and concrete workflows for common editing tasks.

---

## The Core Mechanic: input_fidelity=high

### What It Does

`edit_image` sends an existing image to the OpenAI `/images/edits` endpoint with `input_fidelity=high` (the default). This parameter instructs the model to treat the source image as a constraint — pixels outside the described change region should remain as close to the original as physically possible given the edit.

This is fundamentally different from generation:

| Operation | Behavior |
|-----------|---------|
| `generate_image` | Creates from scratch; no pixel preservation |
| `edit_image (input_fidelity=low)` | Loosely guided by source; may drift significantly |
| `edit_image (input_fidelity=high)` | Anchored to source; unchanged regions preserved |

### Why This Matters for Sequential Editing

Without `input_fidelity=high`, each edit accumulates drift — small unintended changes that compound across steps. By step 4 of a chain, the image may bear little resemblance to step 1 except in the areas you explicitly changed.

With `input_fidelity=high`, each step anchors to the previous output. The composition, perspective, focal length, and all untouched regions remain stable. You can make five changes to an image and end with something that differs from the original in exactly five ways — not fifty.

**The invariant**: Every `edit_image` call in a chain takes the output path of the previous call as `image_path`. Never loop back to a stale step without discarding the intervening work.

### When to Use input_fidelity=low

`input_fidelity=low` is appropriate for radical style transfers — when you explicitly want the model to reinterpret the source image in a completely different aesthetic:

- "Render this photo in the style of Van Gogh's Starry Night"
- "Convert this realistic landscape to a flat vector illustration"
- "Make this architectural photograph look like a watercolor painting"

In these cases, pixel preservation is counterproductive — you want the model to recast the source, not anchor to it.

---

## Edit Sequencing Strategy

The order of edits determines the quality of the final chain. Sequence violations produce the most common failure modes in multi-step editing.

### The Three-Tier Model

#### Tier 1 — Structural Edits (Always First)

Structural edits change the global context that all subsequent edits depend on. If you change the background in step 3, you may invalidate the targeted color work from step 2 (because the new background casts different light on the subject).

**Structural edits include:**
- Background replacement or removal
- Major composition changes (adding or removing large elements)
- Lighting environment overhaul (changing from day to night; studio to outdoor)
- Overall color grade or tone shift for the entire frame
- Subject repositioning

**Execute structural edits first, one structural change per step.**

#### Tier 2 — Targeted Edits (After Structure is Fixed)

Targeted edits affect specific regions or elements within the established structure.

**Targeted edits include:**
- Color change on a specific garment or object
- Material change (make the table mahogany instead of oak)
- Adding or removing a mid-sized object (a plant, a coffee cup, a bag)
- Changing a subject's hair or accessory
- Adjusting the intensity of an existing light source

#### Tier 3 — Atomic / Detail Edits (Last)

Atomic edits add or remove fine-grained details that don't affect overall composition or lighting.

**Atomic edits include:**
- Atmospheric additions: lens flare, fog, rain, bokeh
- Grain, texture overlays, vignetting
- Blemish removal, power-line removal, dust spots
- Small object addition (a ring, a badge, a logo)
- Subtle typography (a small watermark, barely-visible brand mark)

**Why detail edits must come last**: Structural and targeted changes modify the scene's lighting and context. A lens flare added in step 2 will be in the wrong position after a background swap in step 4.

### Sequencing Example

**Request**: "Take this product photo. Remove the white background completely. Then add a dramatic dark marble surface and studio lighting. Then make the bottle gold instead of silver. Then add a subtle lens flare from the upper left."

**Correct sequence**:
```
Step 1 (Structural): Remove background → transparent
Step 2 (Structural): Add dark marble surface + studio lighting
Step 3 (Targeted):   Change bottle material from silver to gold
Step 4 (Atomic):     Add lens flare from upper-left corner
```

**Wrong sequence** (common mistake):
```
Step 1: Change bottle to gold     ← Targeted before structural
Step 2: Add lens flare            ← Atomic before structural
Step 3: Remove background         ← Too late — gold/flare may drift
Step 4: Add marble surface        ← May undo step 1's work
```

---

## The Mask Decision

### Use a Mask When

The edit must be surgically confined to a specific spatial region:

- Removing a small object from a complex background (power lines, a person's face, a watermark)
- Changing a specific garment without touching adjacent garments or skin
- Inpainting a damaged or obscured region
- Replacing one object in a densely-packed scene
- Adding to a specific region without affecting the rest (a reflection in a window, text on a sign)

**Signal phrases from users**: "only change X", "without touching Y", "just the Z", "remove only the W".

### Skip the Mask When

- The change is global (mood, color grade, overall lighting)
- The change is large and well-bounded (entire background replacement)
- The edit region is described so clearly in text that the model can infer it
- Speed is prioritized and some spillover is acceptable

### Mask Format

Masks for `edit_image` are **PNG files** where:
- **Transparent pixels (alpha = 0)**: The edit region — what the model should change.
- **Opaque pixels (alpha = 255)**: Protected regions — what the model must preserve.

**Creating a mask**:
1. Take the source image dimensions.
2. Create a grayscale or RGBA PNG of the same size.
3. Paint the edit region white/transparent; paint protected regions black/opaque.
4. Save as PNG with alpha channel.
5. Pass the mask path as `mask_path` to `edit_image`.

The mask does not need to be perfectly precise — it should be slightly larger than the edit region to avoid hard edges at the boundary.

---

## Edit Prompt Grammar

Edit prompts differ from generation prompts in two important ways:

1. **Imperative voice**: Tell the model what to do, not what to describe.
2. **Preservation clauses**: Explicitly state what must not change.

### Pattern

```
[Action verb] [the specific element] [from/in/at location] [to/with/using description],
[keeping/without affecting/preserving] [what must not change].
```

### Examples

**Background replacement:**
```
Replace the plain white background with a deep indigo-to-midnight-blue gradient 
that darkens toward the bottom, keeping the product and its shadow on the floor 
plane completely unchanged.
```

**Color change:**
```
Change the model's blazer from charcoal grey to a saturated forest green, 
preserving the existing shadow detail in the fabric folds and the lapel highlights.
```

**Atmospheric addition:**
```
Add a single warm lens flare entering from the upper-left corner, creating 
a soft golden streak across the upper quarter of the frame without obscuring 
the subject's face or any critical product text.
```

**Removal:**
```
Remove the power lines crossing the sky in the upper portion of the frame, 
replacing them with a continuation of the overcast sky that matches surrounding 
texture and color exactly, without touching the treeline below.
```

**Inpainting:**
```
Fill the obscured region at the bottom-left corner with natural stone pavement 
matching the texture, color, and perspective of the surrounding visible 
pavement — seamless, no visible boundary.
```

---

## Common Multi-Step Workflows

### 1. Product Photography Enhancement Chain

A raw product photo needs background removal, surface staging, and brand color alignment.

```
Base:   Raw product photo on white seamless

Step 1 [Structural]: Remove background, output with transparent PNG
        prompt: "Remove the background entirely, keeping only the product 
                 and its natural shadow footprint."
        output_format: "png", background: "transparent"

Step 2 [Structural]: Composite onto brand surface
        prompt: "Add a dark grey brushed concrete surface beneath the 
                 product, matching the shadow footprint from the previous 
                 step, with subtle ambient occlusion at the base."

Step 3 [Targeted]: Brand color alignment
        prompt: "Shift the product accent color from the current light grey 
                 to the brand's midnight navy blue, preserving all surface 
                 texture and light reflection patterns."

Step 4 [Atomic]: Lifestyle finish
        prompt: "Add a very subtle warm vignette around the frame edges 
                 and a soft ambient lens reflection in the lower-left 
                 corner to suggest premium studio lighting."
```

### 2. Portrait Retouching and Environment Change

Editorial portrait that needs environment swap and then targeted retouching.

```
Base:   Portrait shot in front of generic office background

Step 1 [Structural]: Environment replacement
        prompt: "Replace the office background with a warm-lit Moroccan 
                 tile interior — terracotta and turquoise geometric patterns — 
                 keeping the subject's lighting, position, and scale unchanged."

Step 2 [Targeted]: Wardrobe adjustment
        prompt: "Change the subject's jacket from light blue to deep burgundy 
                 red, maintaining the existing crease shadows and collar highlights."

Step 3 [Targeted]: Lighting warmth
        prompt: "Warm the overall color temperature of the light falling on 
                 the subject to match the warm amber tones of the Moroccan 
                 tile background — shift the key light highlights from cool 
                 white to warm golden, keeping shadow areas cool."

Step 4 [Atomic]: Finishing
        prompt: "Add subtle film grain across the frame (ISO 800 feel) 
                 and a slight warm vignette from the corners inward."
```

### 3. Scene Transformation (Day to Night)

Exterior scene that needs time-of-day change with consistent lighting logic.

```
Base:   Daytime street scene

Step 1 [Structural]: Time-of-day change
        prompt: "Transform this daytime street scene to late night — 
                 replace the blue sky with a deep navy starfield, 
                 darken all surfaces and shadows to night-level exposure, 
                 and turn off any visible daylight."

Step 2 [Structural]: Add artificial lighting
        prompt: "Add warm amber street lamp pools of light on the pavement 
                 below each visible street lamp post, with realistic falloff. 
                 Add warm glow from shop windows on the left side of the frame."

Step 3 [Targeted]: Subject lighting adjustment
        prompt: "Adjust the lighting on any people visible in the frame 
                 to be lit by the newly-added street lamps — warm top-light 
                 with cool ambient shadow fill — removing any trace of 
                 the original daylight illumination."

Step 4 [Atomic]: Night atmosphere
        prompt: "Add subtle wet pavement reflections below each street lamp, 
                 a light lens flare on the nearest lamp post, and stars 
                 visible in the dark sky patches."
```

---

## Failure Recovery Protocol

When an edit step produces an unacceptable result:

### Step 1: Stop the Chain

Do not continue the chain from the bad output. Continuing from a compromised step compounds the problem.

### Step 2: Identify the Failure Axis

- **Scope bleed**: The edit changed more than intended. → Add a mask or refine the spatial constraint in the prompt.
- **Under-application**: The change wasn't applied strongly enough. → Strengthen the imperative, reduce preservation clause scope.
- **Composition shift**: The edit changed subject position or scale. → Input image may be degraded; return to previous step and try `input_fidelity=high` explicitly.
- **Color contamination**: The edit's color bled into protected areas. → Mask the protected area explicitly.

### Step 3: Branch from Last Good Step

Return to the **output path** of the last accepted step (not the current bad output). Start a new branch:

```
Good chain so far:  base → step1_output → step2_output (last good)

Failed:             step2_output → step3_FAILED (discard this)

Branch:             step2_output → step3_revised_A (try revised prompt)
                    step2_output → step3_revised_B (try with mask)
                    step2_output → step3_revised_C (try n=3 variants)
```

Select the best result from the branch and continue.

### Step 4: Document the Branch

Log:
- Failed step prompt
- Failure description and axis
- Revised prompt used
- Whether mask was added
- Outcome (success / further branch needed)

This creates an edit log that helps identify prompt patterns that work for the specific image.
