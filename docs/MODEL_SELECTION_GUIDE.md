# Model Selection Guide — Image Generation

A focused image-only routing reference. The cross-modal version of this guide (with video, audio, and reasoning axes) lives in `amplifier-bundle-creative/context/MODEL_SELECTION_GUIDE.md`. This file extracts the image-relevant axes so consumers of `amplifier-bundle-imagen` (and direct callers of `imagen-mcp`) get the routing wisdom without needing to compose the creative bundle.

For deep provider comparison and cost/capability detail, see the companion `imagen:docs/PROVIDER_COMPARISON.md`. For per-provider prompt grammar, see `imagen:docs/PROMPT_ENGINEERING_GUIDE.md`. For continuity discipline (reference-image conditioning), see `imagen:docs/REFERENCE_IMAGE_DISCIPLINE.md`.

---

## Three image-routing axes

### Axis 1 — Text-rendering choice (gpt-image-2 vs. Nano Banana Pro)

The single sharpest axis. Text fidelity is where the providers diverge most.

| Shot has... | Choose | Why |
|---|---|---|
| Readable copy, menus, labels, posters, infographics, UI mockups | **OpenAI gpt-image-2** | ~99% text accuracy. Nano Banana cannot reliably render non-trivial copy. |
| Logos, specific brand wordmarks, typographic compositions | **OpenAI gpt-image-2** | Same reasoning — text discipline. Critical for product end cards, title cards, branded callouts. |
| Speech bubbles, comic dialogue, chart labels | **OpenAI gpt-image-2** | Text inside containers needs precise rendering. |
| Iterative multi-turn refinement with conversation memory | **OpenAI gpt-image-2** | Responses API conversation threads preserve context across calls. |
| Transparent background needed | **OpenAI gpt-image-2** | Supports `background=transparent`; Nano Banana does not. |
| **No** legible text required, photoreal subject is the focus | **Nano Banana Pro** | Higher style fidelity at photoreal range. |

**Operational rule:** if the shot has *any* text the operator expects to be readable in the final deliverable, route to gpt-image-2. Don't try to coax Nano Banana through a text-heavy generation; the failure mode is "text-shaped pixels" that read as garbled at any resolution.

### Axis 2 — Photorealism / product / portrait (Nano Banana Pro vs. gpt-image-2)

The complement of Axis 1. When text isn't the constraint, photorealism is.

| Shot characteristic | Choose | Why |
|---|---|---|
| Reference-image-first (existing IP, character continuity, brand campaign) | **Nano Banana Pro** | Multi-ref conditioning up to 14 images; respects setting-match ranking; survives character identity across 30+ shots. See REFERENCE_IMAGE_DISCIPLINE.md. |
| Photorealistic product or portrait, no text | **Nano Banana Pro** | Cleanest commercial photography output. |
| 2K or 4K final-resolution required | **Nano Banana Pro** | gpt-image-2 maxes at 1792×1024 widescreen. |
| Real-time data overlay (current weather, live event, recent stock data) | **Nano Banana Pro** | Only provider with Google Search grounding. |
| Hero product macro, beauty shot, advertising-gloss | **Nano Banana Pro** | Material physics, lighting, and shallow-DoF aesthetics are its strength. |
| Editorial portrait, character-driven photoreal | **Nano Banana Pro** | Identity preservation under reference conditioning beats gpt-image-2 in this register. |

### Axis 3 — Vision analysis (when to look at images vs. generate them)

For agents in the `imagen` family that *analyze* operator-supplied images (`imagen:image-researcher`, `imagen:image-director` when reviewing references), match the analysis task to the model:

| Task | Recommended model | Why |
|---|---|---|
| Extract literal printed text from page scans (OCR-like) | gpt-4.1-mini or claude-sonnet | Both handle this cleanly; gpt-4.1-mini is cheaper at volume. |
| Identify a font from text crops (multi-sample, handwriting-vs-serif) | claude-sonnet | Better at typography reasoning. |
| Analyze mockup-video frames or storyboard slides | claude-sonnet or gpt-4.1 | Either; prefer whichever is cheapest in your active matrix. |
| Compare a generated frame to a source reference (drift detection) | claude-sonnet | Best at identifying subtle identity drift. |
| Bulk vision analysis (batch of 30+ images) | gpt-4.1-mini | Volume cost discipline. |

When dispatching parallel vision calls, batch them via `ThreadPoolExecutor` — vision is I/O-bound, serial calls waste wall time.

---

## Decision card (stick this on the wall)

```
┌──────────────────────────────────────────────────────┐
│  TEXT in the image?                                  │
│      → OpenAI gpt-image-2                            │
│                                                      │
│  REFERENCE images for continuity / character / IP?   │
│      → Nano Banana Pro (with reference_images=[…])   │
│      → see REFERENCE_IMAGE_DISCIPLINE.md             │
│                                                      │
│  PHOTOREAL hero, product, portrait, no text?         │
│      → Nano Banana Pro                               │
│                                                      │
│  TARGETED edit of a prior approved shot?             │
│      → gpt-image-2 edit_image, input_fidelity=high   │
│                                                      │
│  ANALYSIS of operator-supplied imagery?              │
│      → vision LLM via delegate (Axis 3 table)        │
└──────────────────────────────────────────────────────┘
```

---

## Cost awareness (rough, not binding)

Per-shot ranges at current matrix rates. Use for budget conversations with the operator, not for auto-throttling.

| Generation | Approximate cost |
|---|---|
| gpt-image-2 single 1024×1024 (high quality) | $0.03 – $0.08 |
| gpt-image-2 single 1024×1536 portrait or 1792×1024 widescreen (high quality) | $0.05 – $0.12 |
| Nano Banana Pro single 2K shot, no refs | $0.04 – $0.10 |
| Nano Banana Pro single 2K shot, 4 ref images | $0.05 – $0.15 |
| Nano Banana Pro 4K | $0.10 – $0.25 |
| Vision analysis (gpt-4.1-mini) per image | $0.005 – $0.015 |
| Vision analysis (claude-sonnet) per image | $0.01 – $0.04 |

For projects with > 30 image generations, surface a budget estimate to the operator before kicking off. They almost always have a tier preference once the number is concrete.

---

## Operator override discipline

The operator can pin any choice. Agents must respect operator pins even when the agent's heuristic would choose otherwise:

- `provider=gpt-image-2` on a photoreal portrait → use gpt-image-2 even though Axis 2 routes elsewhere.
- `gemini_model=nano-banana-2` instead of `nano-banana-pro` (cost optimization on a low-stakes shot) → respect.
- `quality=low` on a high-volume batch where exploration > polish → respect.

Document the pin in the shot spec or call notes. The agent stays authoritative on hard rules (refs ≤ 1400 px before send, valid model parameters, quota ceilings) but never on aesthetic preference.

---

## Cross-references

- `imagen:docs/PROVIDER_COMPARISON.md` — full capability matrix, deprecation watchlist, latency/cost tables.
- `imagen:docs/PROMPT_ENGINEERING_GUIDE.md` — per-provider prompt grammar and iteration strategy.
- `imagen:docs/REFERENCE_IMAGE_DISCIPLINE.md` — D028/D029/D030 distilled with case study.
- `imagen:docs/CREATIVE_DIRECTION_GUIDE.md` — visual brief format and critique framework.
- `imagen:docs/EDIT_WORKFLOW_GUIDE.md` — `edit_image` sequential editing patterns.

For multi-modal pipelines (image + video + audio + cut), pull in `amplifier-bundle-creative` for video-tier and TTS-voice axes that don't apply here.
