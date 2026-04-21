# Provider Comparison Guide

Reference for choosing between OpenAI (gpt-image-2, gpt-image-1.5, gpt-image-1) and Google (Nano Banana 2, Nano Banana Pro). Covers model roster, capability matrix, decision tree, cost and latency, auto-selection heuristics, model-selection guidance, and deprecation watchlist.

---

## Model Roster

### OpenAI — `openai_model` parameter

| Canonical ID | Default | Speed | Max Resolution | Cost Tier |
|---|---|---|---|---|
| `gpt-image-2` | **Yes** | 3–8 s | 1792×1024 | Standard |
| `gpt-image-1.5` | No | 3–8 s | 1792×1024 | Mid |
| `gpt-image-1` | No | 3–8 s | 1792×1024 | Lower |

All three support: `edit_image` sequential editing, transparent background, inpainting with masks, n=1–10, `quality` tiers, `output_format` (png/jpeg/webp). **`gpt-image-2` is the default and recommended option.**

`gpt-image-1.5` is the designated migration target for workflows currently on DALL-E 3 (DALL-E 3 API ends **2026-05-12**). Prompt style stays similar; the `style` param takes `"vivid"` / `"natural"`.

### Google — `gemini_model` parameter (canonical ID or friendly alias)

**Nano Banana family** — `generate_content` endpoint; full feature set.

| Canonical ID | Alias | Default | Speed | Max Resolution |
|---|---|---|---|---|
| `gemini-3.1-flash-image-preview` | `nano-banana-2` | **Yes** | 8–15 s | 2K |
| `gemini-3-pro-image-preview` | `nano-banana-pro` | No | 15–25 s | 4K |

Both support: reference images (up to 14), Google Search grounding, multi-turn conversational editing, all 10 aspect ratios, 1K/2K/4K sizes. `nano-banana-pro` additionally enables Thinking mode for highest-fidelity output.


---

## Capability Matrix

| Model | Text Rendering | Photorealism | Max Resolution | Ref Images | Search | Edit / Masks | n= | Deprecated |
|-------|---------------|-------------|----------------|-----------|--------|-------------|-----|-----------|
| **`gpt-image-2`** | ~99% | Good | 1792×1024 | No | No | Yes | 1–10 | — |
| **`gpt-image-1.5`** | Good | Good | 1792×1024 | No | No | Yes | 1–10 | — |
| **`gpt-image-1`** | Good | Good | 1792×1024 | No | No | Yes | 1–10 | — |
| **Nano Banana 2** | Moderate | Excellent | 2K | Yes (14) | Yes | No | 1 | — |
| **Nano Banana Pro** | Moderate | Excellent | 4K | Yes (14) | Yes | No | 1 | — |
*Edit/Masks = `edit_image` sequential editing, inpainting with PNG masks, transparent background output (OpenAI only).*

---

## Decision Tree

```
START: What is the primary deliverable?

├── Contains text that must be legible? (menus, labels, posters, UI)
│   └── → OpenAI gpt-image-2

├── Needs to be edited iteratively afterward?
│   └── → OpenAI gpt-image-2  (edit_image only available on OpenAI)

├── Requires transparent background?
│   └── → OpenAI gpt-image-2

├── Photorealistic portrait of a specific person or character?
│   ├── Have reference photos?
│   │   └── → Gemini (reference_images for consistency)
│   └── No references — just description?
│       └── → Gemini (stronger photorealism by default)

├── Product photography requiring material realism?
│   └── → Gemini (glass refraction, fabric texture, metal sheen)

├── Needs 4K output for print or large-format?
│   └── → Gemini (size=4K)

├── Visual based on live/real-time data? (weather, stocks, news)
│   └── → Gemini (enable_google_search=true)

├── Needs multiple output variants quickly?
│   └── → OpenAI (n=3–10 in one call; Gemini is one-at-a-time)

├── Sequential multi-step edits on existing image?
│   └── → OpenAI (edit_image not available on Gemini)

├── Illustrative, conceptual, or graphic-design style?
│   └── → OpenAI (stronger visual adherence to art-direction language)

└── Ambiguous? Photorealistic but no special requirements?
    ├── Subject is a person → Gemini
    └── Subject is a scene or object → Either; OpenAI for speed
```

---

## Cost and Latency Characteristics

*Note: Costs are approximate and subject to provider pricing changes. Check official pricing pages for current rates.*

### OpenAI gpt-image-2

| Quality | Approx. Cost | Approx. Time |
|---------|-------------|-------------|
| `low` | ~$0.011/image | 3–5 s |
| `medium` | ~$0.042/image | 4–6 s |
| `high` | ~$0.167/image | 5–8 s |
| `edit_image` (any quality) | Similar to generation | 5–10 s |

Key cost driver: `usage.output_tokens` (returned in response). High-quality images produce more output tokens and cost proportionally more.

Batch efficiency: `n=4` at `low` quality ≈ `n=1` at `high` quality, useful for exploring options before committing to a high-quality render.

### Gemini

| Model | Size | Approx. Cost | Approx. Time |
|-------|------|-------------|-------------|
| Nano Banana 2 | `1K` | Low | 8–12 s |
| Nano Banana 2 | `2K` | Medium | 10–15 s |
| Nano Banana Pro | `1K` | Low | 10–15 s |
| Nano Banana Pro | `2K` | Medium | 15–20 s |
| Nano Banana Pro | `4K` | Higher | 20–30 s |
Nano Banana models generate one image per call; parallelize concurrent calls for variants.

---

## Auto-Selection Heuristics

The `imagegen` MCP server implements prompt-based auto-selection. Understanding these heuristics helps you predict which provider will be chosen — and when to override.

### OpenAI gpt-image-2 Is Auto-Selected When

The prompt contains keywords or intent signals indicating:

- **Text content**: "menu", "poster", "sign", "label", "infographic", "headline", "text", "word", "letter", "banner", "title"
- **Comic / narrative content**: "comic", "dialogue", "speech bubble", "caption", "panel"
- **Technical diagram**: "diagram", "chart", "wireframe", "UI", "mockup", "screenshot", "interface"
- **Marketing / design**: "marketing", "ad creative", "brand asset", "logo", "icon"

### Gemini Nano Banana Pro Is Auto-Selected When

The prompt contains keywords or intent signals indicating:

- **Portrait photography**: "portrait", "headshot", "person", "face", "model" (human)
- **Product photography**: "product photo", "product shot", "e-commerce", "packshot"
- **High resolution**: "4K", "high resolution", "large format", "print"
- **Reference images provided**: `reference_images` parameter is non-empty
- **Real-time data**: `enable_google_search=true`

### Override When Auto-Selection Is Wrong

Auto-selection uses heuristics; creative intent sometimes diverges from keyword signals. Use explicit `provider=` when:

| Scenario | Override |
|----------|---------|
| Photorealistic portrait with text overlay | `provider="openai"` — text accuracy wins |
| Product shot with branding text on label | `provider="openai"` — text rendering required |
| Conceptual art that happens to mention "person" | `provider="openai"` — illustrative intent |
| Standard headshot, no text, no 4K needed | `provider="gemini"` — better photorealism |
| Building a sequential edit chain that starts with Gemini output | `provider="openai"` — `edit_image` requires OpenAI |

### Model-Level Selection Within a Provider

Auto-selection operates at the **provider level** (OpenAI vs Gemini). Within a provider, the specific model defaults to the provider's current best: `gpt-image-2` for OpenAI; `gemini-3.1-flash-image-preview` (Nano Banana 2) for Gemini. Override at the model level with `openai_model` or `gemini_model`. See **When to Explicitly Pick a Model** below.

---

## When to Explicitly Pick a Model

| Scenario | Model | Why |
|----------|-------|-----|
| Cost matters more than quality | `gpt-image-1` (via `openai_model`) | Legacy OpenAI model at a lower cost tier |
| Migrating from DALL-E 3 | `gpt-image-1.5` (via `openai_model`) | Designated DALL-E 3 migration target; `style="vivid"/"natural"` supported |
| Photorealistic image where text also matters | `nano-banana-pro` (via `gemini_model`) | Thinking mode improves text accuracy in a photorealistic context |


---

## Workflow-Level Provider Decisions

### Research Phase (Exploration)

Use `provider="auto"` with `quality="low"` (OpenAI) or `size="1K"` (Gemini). Generate 3–4 variations quickly to discover composition and style directions before committing to a high-quality render.

```python
# Quick exploration — openai, low quality, 4 variants
generate_image(
    prompt="...",
    quality="low",
    n=4,
    provider="openai"
)
```

### Production Render

Once direction is confirmed, generate at full quality:

```python
# Final production render
generate_image(
    prompt="...",
    quality="high",
    size="1536x1024",
    output_format="jpeg",
    output_compression=92,
    provider="openai"
)
```

### Sequential Edit Chain

Always commit to OpenAI at the start of an edit chain — you cannot switch providers mid-chain:

```python
# Chain step 1 — establish base image
step1 = generate_image(prompt="...", provider="openai", quality="high")

# Chain step 2 — edit the output
step2 = edit_image(
    prompt="Change the background to sunset sky",
    image_path=step1.output_path,
    input_fidelity="high"
)

# Chain step 3 — continue editing
step3 = edit_image(
    prompt="Add lens flare",
    image_path=step2.output_path,
    input_fidelity="high"
)
```

### Conversational Refinement

The `conversational_image` tool locks the provider for the duration of a conversation. Choose wisely at the start:

- `provider="openai"` for text, graphics, style exploration.
- `provider="gemini"` for photorealistic portrait or product refinement.

```python
# Start a conversation — provider locked from here
conv = conversational_image(
    prompt="I need a hero image for a wellness brand",
    dialogue_mode="guided",
    provider="gemini"  # locks to Gemini for all turns
)
```

---

## Provider Strengths Deep Dive

### Why OpenAI gpt-image-2 Excels at Text

gpt-image-2 was trained with reinforcement from text-accuracy feedback signals. It places characters with ~99% accuracy, handles kerning and baseline, supports multiple scripts (Latin, CJK, Arabic, Hebrew), and maintains consistent text style across a composition. This makes it the only viable provider for:

- Restaurant menus with legible item names and prices
- Poster designs with headlines and body copy
- Infographics with labeled data points
- Comics and illustrated stories with dialogue bubbles
- UI mockups where button labels must read correctly
- Business cards, flyers, packaging with brand text

### Why Gemini Nano Banana Pro Excels at Photorealism

Gemini Nano Banana Pro is trained on a photographic corpus with quality signals from professional photographers. It models:

- **Skin tone and texture**: Pore-level micro-detail, natural subsurface scattering, accurate ethnicity representation without bias.
- **Material physics**: Glass refraction, metal specular highlights, fabric weave structure, water reflections, leather grain.
- **Lens physics**: True bokeh shape (circular or anamorphic), chromatic aberration at edge of frame, barrel distortion at wide angles.
- **Lighting physics**: Shadow softness corresponding to light source size and distance, color temperature mixing from multiple sources.

This physical accuracy is why Gemini consistently outperforms OpenAI on product photography and portraiture — it models the physics rather than imitating the aesthetic.

### Sequential Editing as an OpenAI Differentiator

`edit_image` with `input_fidelity=high` is exclusive to OpenAI. This capability enables workflows that are impossible with generation alone:

- **Brand asset iteration**: Generate a product base image, then make 5 color variant edits (blue, red, green, gold, black) as sequential edits from the same base — each variant shares pixel-perfect composition.
- **Progressive refinement**: Large structural change first (background swap), then targeted color change (jacket color), then atmospheric detail (lens flare) — each step anchored to the previous output.
- **Inpainting**: Remove a person from a crowd scene using a PNG mask; surrounding pixels untouched.

No Gemini workflow offers equivalent sequential edit precision.

---

## Common Misconceptions

**"OpenAI is for text, Gemini is for photos — I can decide based on subject type."**
Partially true but insufficient. An AI-illustrated portrait goes to OpenAI. A photorealistic product shot without text goes to Gemini. Subject type is one signal; intended aesthetic register and downstream workflow requirements are equally important.

**"I should always use Gemini for portraits because it's more photorealistic."**
Only if you want photorealism. If the brief calls for editorial illustration, conceptual art, or graphic-novel style portraiture, OpenAI's adherence to art-direction language produces better results.

**"Gemini's 4K output is always worth it."**
4K is worth it for print, large-format display, or when you need to crop significantly. For web and social media, 2K (Gemini) or 1536×1024 (OpenAI) is sufficient and costs less.

**"Auto-selection will always get it right."**
Auto-selection uses prompt text heuristics. Complex briefs with mixed signals (e.g., a photorealistic painting of a coffee menu) require explicit `provider=` override. When you have a clear provider preference, always set it explicitly rather than relying on auto-selection.
test

---

## Deprecation Watchlist

All long-lived pipelines should plan around these hard shutdown dates.

| Model / API | Shutdown Date | Migration Target | Notes |
|-------------|--------------|-----------------|-------|
| DALL-E 3 API | **2026-05-12** | `gpt-image-1.5` | DALL-E 3 API endpoint ends; prompt style stays compatible |
| `gemini-2.5-flash-preview-image-generation` | **2026-10-02** | `nano-banana-2` | Legacy Gemini flash image model |
*Dates reflect public deprecation announcements. Verify against official provider docs before planning mission-critical migrations.*

### Removed in v0.3.0

The `generate_images`-based Google model family (Standard, Ultra, Fast) was removed from `imagen-mcp` in v0.3.0. The entire family shuts down **2026-06-24** and provided no editing, reference image, or Google Search support — the bundle's specialist agents could not meaningfully use it. **Migration:** → **Nano Banana 2** (speed match) or **Nano Banana Pro** (quality match).
