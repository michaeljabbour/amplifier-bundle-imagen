# Reference-Image Discipline

**Owner agent:** `imagen:image-prompt-engineer` (with handoff hooks for `imagen:image-director`).
**Companion docs:** `imagen:docs/PROVIDER_COMPARISON.md`, `imagen:docs/PROMPT_ENGINEERING_GUIDE.md`.

When the work involves named characters, existing IP, or any continuity across multiple shots, **reference-image conditioning is not optional**. Text-only prompts produce identity drift within 2–3 generations. This document codifies the reference-image protocol learned from real production cycles (see Case Study below).

The principles here are extracted and re-scoped to image-only from `amplifier-bundle-creative/spec/DECISIONS.md` (decisions D028, D029, D030). They apply universally to image generation through this bundle, not only to creative-bundle pipelines.

---

## Principle 1 — Reference-image-first for any continuity work

If the next image must match characters, settings, or branded elements established in earlier images, **never start from a text-only prompt**. Always condition on the prior approved image as a reference.

This applies to:
- **Named characters** across multiple shots (book trailer, character-driven series, sequential storytelling)
- **Brand identity** carried across a campaign (consistent product, consistent palette, consistent typography)
- **Setting continuity** (same room, same lighting, same time of day)
- **Identity preservation** when iterating (the operator approved shot 7; shot 8 should look like it's from the same world)

Without reference conditioning, even a meticulous prompt like *"young brown-haired woman, blue cardigan, warm kitchen, late afternoon light"* will drift over successive generations — different face shape each time, different exact hue of cardigan, different lighting angle. The model converges on its statistical center, not on your specific established world.

**Mechanism in this bundle:**

- **Nano Banana Pro** — pass references via the `reference_images` parameter (up to 14 images: 6 for objects, 5 for human portraits). The model conditions on visual properties of those refs.
- **gpt-image-2** — pass the prior frame via `edit_image` with `input_fidelity=high`, applying targeted prompt language for the change you want. This preserves all unchanged pixels exactly.

Choose the mechanism by job:

| Goal | Use |
|---|---|
| New composition that *carries forward* characters/setting from a prior shot | Nano Banana Pro `generate_image` with `reference_images=[prior_shot]` |
| Same composition with *targeted modification* (color change, element addition) | gpt-image-2 `edit_image` with `input_fidelity=high` |
| Multi-shot series where every frame should belong to the same campaign | Nano Banana Pro with the *first approved frame* as the persistent anchor reference, then chain |

---

## Principle 2 — Setting-match first, face-clarity second

When you have multiple candidate references and must rank them, **setting-match wins over face-clarity**. A reference image where the lighting and environment match your target shot will produce better results than a face-perfect reference shot in the wrong setting — even if the face in the second ref is sharper.

The reasoning: the model has to extrapolate the subject INTO the new context. If the reference already lives in roughly the right context, the extrapolation is small and identity is preserved. If the reference is from a wildly different lighting/setting, the model has to do compositional surgery, and identity gets sacrificed in the process.

**Ranking heuristic (apply in order):**

1. **Lighting type match** — golden-hour ref for golden-hour target; soft-diffuse for soft-diffuse; cool morning for cool morning.
2. **Setting category match** — interior/exterior, indoor-environment, scale-of-space.
3. **Composition match** — close-up vs. medium vs. wide-shot; if your target is a close-up, prefer a close-up ref over a wide one.
4. **Face clarity** — only use this to break ties between refs that match items 1–3.

If you have a face-perfect ref but it's from the wrong setting, **don't use it as the primary anchor**. Use it as the second or third ref (Nano Banana Pro takes up to 5 portrait refs) and let the setting-matched ref dominate.

---

## Principle 3 — Downsize before sending to Nano Banana Pro

Reference images sent to Nano Banana Pro must be **≤ 1400 px on the longest edge**. Larger references can produce silent failures (the API returns a generation with no apparent reference conditioning, as if the refs were ignored).

**Recipe (ImageMagick):**

```bash
convert SOURCE_REF.png -resize 1400x1400\> -quality 95 RESIZED_REF.png
```

The `\>` after the dimensions tells ImageMagick "only downsize if larger; never upscale." The `-quality 95` keeps JPEG/PNG compression artifacts well below visible thresholds.

For Python:

```python
from PIL import Image
img = Image.open(source_ref)
img.thumbnail((1400, 1400), Image.LANCZOS)
img.save(resized_ref, quality=95, optimize=True)
```

For each project, downsize **once** (caches in your project's `02_preproduction/refs_resized/` or equivalent), then reuse the resized file for every generation that conditions on it. Don't re-downsize for each call.

---

## Principle 4 — Chain references across multi-shot sequences

For a sequence of N shots that must share continuity, the reference-chaining pattern looks like this:

```
Shot 1: text-only prompt OR ref to operator's source IP
        ↓ approved Shot 1 PNG becomes a ref for ↓
Shot 2: prompt + [Shot 1 PNG]
        ↓ approved Shot 2 PNG becomes the primary ref for ↓
Shot 3: prompt + [Shot 2 PNG, Shot 1 PNG]   ← shot 1 still in ref set as the anchor
        ↓                                     ↓
        ...                                   ...
Shot N: prompt + [Shot N-1 PNG, Shot 1 PNG (or another stable anchor)]
```

The first approved frame becomes the **persistent anchor** — it stays in the reference set for every subsequent shot. This locks the campaign-level look (palette, lighting register, brand identity) even as the immediate predecessor shot drives character/composition continuity.

For sequences > 5 shots: rotate the secondary reference (n-1) but keep the persistent anchor. Once you exceed Nano Banana Pro's 5-portrait-ref ceiling, drop the oldest secondary ref but never the anchor.

For **branded campaign work** (where the brand identity is the anchor): use the establishing shot as the anchor, even if no character appears in it. The screen, the product, the logo treatment — all of those carry forward.

---

## Case Study — milk-racing-spot v1 → v2 (operator-driven QA cycle)

A real production cycle illustrating what happens when you skip reference-image discipline and what fixing it looks like.

### v1 (skipped reference conditioning)

Three frames generated independently from text prompts only. Each prompt was meticulously written with palette, lighting, lens, and subject specs. Output:

- Shot 1 (macro pour): great standalone product shot
- Shot 2 (person sipping): different "type of person" than shot 3 implied
- Shot 3 (over-the-shoulder typing): different setting, different glass shape, different laptop, different hair color than shot 2

**Operator QA verdict:** "Branding is non-existent, voice over is kinda weird, images don't all line up." The "images don't line up" part was reference-discipline failure. The agent had ALL the right prompt language for each shot independently, but no shot conditioned on its predecessor.

### v2 (proper reference chaining)

Shot 1 regenerated fresh with explicit Microsoft Copilot brand identity (gradient + sparkle icon) on the laptop screen as the persistent anchor. Then:

- **Shot 2** — generated via `generate_image` with `reference_images=[shot_01_v2.png]`. Prompt explicitly asked the model to keep the laptop, glass, marble countertop, and Copilot gradient from the reference image, while introducing a new element (the person, mid-sip).
- **Shot 3** — generated via `generate_image` with `reference_images=[shot_02_v2.png, shot_01_v2.png]`. Shot 2 was the primary ref (carries character identity and the moment's lighting); shot 1 stayed in the ref set as the anchor (locks brand identity and glass).

**Result:** character/setting/glass/laptop/branding visibly carried across all three frames. Same person. Same loft. Same milk. Same Copilot gradient on the screen across all three shots. The piece read as a campaign instead of three unrelated generations.

**The diff between v1 and v2 was almost entirely reference-image protocol.** The prompts in v2 were not dramatically different — what changed was the conditioning. That's why this discipline matters more than prompt prose elegance.

---

## Quick Reference Card

When you're invoked for image work involving any continuity:

```
┌────────────────────────────────────────────────────────────────┐
│  Multiple shots / characters / brand in play?                  │
│      → YES: reference-image conditioning required              │
│                                                                │
│  Have a prior approved shot from this project?                 │
│      → use it as the primary reference                         │
│                                                                │
│  Have an anchor (first approved frame OR operator-supplied)?   │
│      → keep it in the ref set every generation                 │
│                                                                │
│  Multiple candidate refs?                                      │
│      → rank: lighting > setting > composition > face-clarity   │
│                                                                │
│  Refs > 1400px on the longest edge?                            │
│      → downsize before sending to Nano Banana Pro              │
│                                                                │
│  Targeted modification of a single approved shot?              │
│      → use gpt-image-2 edit_image with input_fidelity=high     │
│      → not generate_image with refs                            │
└────────────────────────────────────────────────────────────────┘
```

If you're invoked without any prior context (greenfield first shot, no operator IP supplied), there's nothing to condition on — proceed text-only. But generate the **first approved frame** with awareness that it will become the anchor for everything that follows. Make it strong.
