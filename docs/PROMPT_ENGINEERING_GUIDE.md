# Prompt Engineering Guide

Reference for `imagen:image-prompt-engineer` — how to craft model-optimized prompts for OpenAI gpt-image-2 and Gemini Nano Banana Pro, select parameters, and iterate when results miss the mark.

---

## Foundational Principle: Provider Grammar Matters More Than Content

The same creative intent encoded with different vocabulary and structure produces dramatically different results depending on the model. OpenAI gpt-image-2 is trained on an art-description corpus and responds to scene-description grammar. Gemini Nano Banana Pro is trained with photography supervision and responds to cinematographer/photographer briefing grammar. Writing a Gemini-style photography-vocabulary prompt to gpt-image-2 produces good but under-optimized results — and vice versa.

The first decision in any prompt engineering task is: **which provider?** That answer determines everything that follows.

---

## Which Model for Which Job

**`gpt-image-2`** (OpenAI default) — The go-to for anything involving text, UI, diagrams, comics, or conceptual illustration. ~99% character accuracy on menus, posters, labels, speech bubbles. Sequential editing via `edit_image`. Use for most OpenAI tasks unless you have a specific cost or migration reason to choose otherwise.

**`gpt-image-1.5`** — The designated migration target for workflows currently using DALL-E 3 (DALL-E 3 API ends **2026-05-12**). Prompt vocabulary and the `style` param (`"vivid"` / `"natural"`) carry over with minimal changes. Use when porting DALL-E 3 pipelines; choose `gpt-image-2` for new work.

**`gpt-image-1`** — Legacy April 2025 OpenAI model at a lower cost tier. Use when generation volume is high and quality requirements are modest. Not recommended for text-heavy or sequential-edit workflows.

**Nano Banana 2** (`gemini-3.1-flash-image-preview` / `nano-banana-2`) — Google's current default Gemini model; fast, full conversational feature set. Supports reference images (up to 14), Google Search grounding, multi-turn editing. Use when you need Gemini's photorealism at speed.

**Nano Banana Pro** (`gemini-3-pro-image-preview` / `nano-banana-pro`) — Highest fidelity in the Gemini lineup; Thinking mode enabled. Best for luxury product shots, editorial portraits where material physics matter, and 4K large-format output.

---

## Part I — OpenAI gpt-image-2 Prompt Engineering

> **Migrating from DALL-E 3?** Use `openai_model="gpt-image-1.5"` — it's the designated drop-in replacement (DALL-E 3 API ends **2026-05-12**). Prompt vocabulary carries over; the `style` param (`"vivid"` / `"natural"`) is preserved. `gpt-image-2` offers better text accuracy and a fuller feature set for new work.

### The Five-Element Structure

Every gpt-image-2 prompt should flow through five elements in sequence, forming a single coherent description:

```
[Subject + Action/State] [Style Register] [Lighting] [Mood] [Technical Spec]
```

This mirrors how the model was trained: it expects a narrative description of what exists in the scene (subject), how it looks (style), how it is lit (lighting), how it feels (mood), and any technical framing constraints (spec).

**Weak prompt (unstructured):**
```
A beautiful coffee shop with warm lighting and cozy vibes, professional photo quality.
```

**Strong prompt (five-element structure):**
```
The interior of a narrow independent coffee shop at dusk, a lone barista steaming milk behind
a worn marble counter, editorial interior photography in the style of Rineke Dijkstra, warm
amber practical light from pendant lamps blending with cool blue street light through the
front window, intimate and slightly melancholy, medium-wide shot, mild film grain, 3:2 aspect.
```

### Element 1: Subject + Action/State

Be precise about:
- **Who or what** is the primary element (include relevant details: age, ethnicity, clothing, expression for people; material, finish, form for objects; architectural period, condition for spaces).
- **What they are doing or being** — action is more dynamic than static description.
- **Spatial relationships** — "a woman sitting at a table" vs "a woman leaning back in a wrought-iron chair, both hands wrapped around a ceramic mug" — the second anchors the model's composition decisions.

```
# Weak subject
"A chef in a kitchen"

# Strong subject
"A pastry chef in her 40s with flour-dusted hands pinching the edge of a tart crust, 
concentrated expression, white chef's coat, cramped professional kitchen behind her"
```

### Element 2: Style Register

Name the genre or movement that defines the image's visual register. This is the single highest-leverage element — it sets the model's entire interpretation frame.

| Register | Prompt Language |
|----------|----------------|
| Editorial fashion | "editorial photography, reminiscent of early Vogue Italia" |
| Commercial product | "luxury product photography, advertising campaign style" |
| Documentary | "documentary photography, unposed and authentic" |
| Fine art | "fine-art photography, minimal and contemplative" |
| Cinematic | "cinematic still, film photography, letterbox aspect" |
| Conceptual | "conceptual art photography, surrealist juxtaposition" |
| Illustration | "editorial illustration, gouache on paper texture" |
| Flat design | "flat vector illustration, Dribbble-style minimal UI icons" |
| 3D render | "photorealistic 3D render, Cinema4D style, studio HDRI" |

**Tip:** Combine era and photographer references for specificity: "1970s New Journalism photography", "early Stephen Shore color palette", "late-career Hiroshi Sugimoto fog".

### Element 3: Lighting

Lighting is the most misunderstood element. Do not describe lighting as an afterthought ("well-lit", "bright"). Describe:

- **Direction**: front-lit / 45° camera-left / hard side-light / backlit / top-down / practical (from within scene).
- **Quality**: hard (small point source → sharp shadow edge) or soft (large diffuse source → gentle gradient shadow).
- **Source type**: window light / overcast sky / golden-hour sun / studio strobe / neon sign / candle / LED ring.
- **Ratio**: high-contrast (key much brighter than fill) or low-contrast (fill raised to nearly match key).

```
# Weak lighting
"Nice lighting"

# Strong lighting
"Single diffused window light from camera-left, soft and directional with a 4:1 
ratio, casting a subtle Rembrandt triangle shadow beneath the nose, warm 
golden-hour color temperature"
```

**Lighting phrases that work well for gpt-image-2:**

- `"golden-hour sunlight from camera-left, long warm shadows"`
- `"overcast sky diffuse light, flat and shadowless"`
- `"single studio strobe with large octabox, soft wrap"`
- `"Rembrandt lighting — 45° side, shadow triangle beneath opposite nostril"`
- `"practical lamp glow, deep amber warmth, strong falloff"`
- `"neon sign splash, magenta and cyan, high contrast"`
- `"backlit rim light, subject silhouetted with glowing hair edge"`

### Element 4: Mood

Mood communicates the **intended emotional affect** — how the viewer should feel. Use specific mood adjectives and pair them with brief physical explanation.

```
# Weak mood
"moody and dramatic"

# Strong mood
"melancholy solitude — the subject's downward gaze and the fading light 
suggest a moment of private reflection"
```

**Mood vocabulary that encodes reliably:**

Intimate, contemplative, melancholy, aspirational, urgent, serene, joyful, eerie, nostalgic, triumphant, vulnerable, commanding, playful, austere, celebratory, tense, ethereal.

### Element 5: Technical Specification

Close the prompt with technical framing decisions. This guides composition and output format without conflicting with the mood:

- **Shot distance**: extreme close-up / close-up / medium / medium-wide / wide / extreme wide.
- **Depth of field**: "shallow depth of field, subject sharp, background bokeh" / "deep focus, foreground to background sharp".
- **Aspect ratio / crop feel**: "square crop", "3:2 landscape", "letterbox 2.39:1 cinematic", "portrait format 2:3".
- **Film or digital feel**: "Kodak Portra 400 film grain", "sharp digital capture, no grain", "medium-format texture".
- **Post-processing signature**: "desaturated palette, lifted blacks", "cross-processed greens and oranges", "matte finish, no specular highlight".

### gpt-image-2 Parameter Selection Guide

#### Quality

| Scenario | Setting |
|----------|---------|
| Exploration / iteration | `quality="low"` or `"medium"` |
| Client-ready deliverable | `quality="high"` |
| Text-heavy image (menus, posters) | `quality="high"` — always |
| Fast preview to select composition | `quality="low"` |

#### Size

| Use Case | Recommended Size |
|----------|-----------------|
| Social media square (Instagram post) | `1024x1024` |
| Landscape hero (website banner) | `1536x1024` |
| Portrait (mobile story, vertical ad) | `1024x1536` |
| Widescreen / cinematic feel | `1792x1024` |
| Tall mobile (app store screenshot) | `1024x1792` |
| Quick test / low-cost iteration | `512x512` |

#### Background

| Scenario | Setting |
|----------|---------|
| Product photo needing compositing | `background="transparent"` + `output_format="png"` |
| Photo / editorial image | `background="opaque"` |
| Model auto-decides | `background="auto"` (default) |

#### Output Format and Compression

| Scenario | Format | Compression |
|----------|--------|-------------|
| Asset with transparency | `png` | N/A |
| Web photo | `webp` | 85 |
| High-quality deliverable | `jpeg` | 92 |
| Fast iteration | `webp` | 70 |

---

## Part II — Gemini Nano Banana Pro Prompt Engineering

### Photography Crew Briefing Grammar

Gemini Nano Banana Pro is trained with photographic supervision. Write prompts as if briefing a Director of Photography and their crew for a real shoot:

```
[Camera + Lens] [Subject description] [Environment and setting] [Lighting setup] [Color grade / processing]
```

This grammar signals to the model that you want photorealistic output from a professional setup.

### Element 1: Camera and Lens

Specify a real camera and lens combination. The model uses these to infer:
- **Sensor size** (full-frame, medium format, APS-C) → detail and dynamic range character.
- **Focal length** → perspective compression and field of view.
- **Aperture** → depth of field and background separation.

```
"Sony A7 IV, 85mm f/1.4"          — Portrait lens, shallow DoF, flattering compression
"Canon EOS R5, 100mm macro f/2.8" — Product/detail, exquisite sharpness
"Leica M11, 28mm f/2.8"           — Street, environmental, classic Leica rendering
"Hasselblad X2D, 80mm f/1.9"      — Medium format, skin tones, luxury feel
"Fujifilm GFX 100S, 110mm f/2"    — Commercial, editorial, film-simulation style
```

### Element 2: Subject Description

For portraits, describe physical characteristics explicitly — age range, ethnicity, hair, expression, clothing, posture. The model uses this to avoid generic "generic stock photo person" output.

```
# Weak
"a woman"

# Strong
"a South Asian woman in her mid-30s with natural dark hair pinned up, 
wearing a tailored cream linen blazer, relaxed open expression, 
seated with one arm on the armrest"
```

For products, describe material, finish, and form:

```
"a hand-thrown ceramic mug with iron oxide slip exterior, slightly rough 
texture, matte dark brown glaze, cream interior, subtle fingerprint 
impressions from the maker visible in the clay"
```

### Element 3: Environment and Setting

Be specific about:
- Location category (indoor / outdoor / controlled studio / on-location).
- Surface materials the subject rests on or is surrounded by.
- Time of day and weather (which determines light quality for outdoor shots).
- Era or style of the space.

```
"in a narrow Kyoto alley at dusk, stone paving wet from recent rain, 
paper lanterns beginning to glow, traditional machiya shopfront behind"
```

### Element 4: Lighting Setup

Use professional lighting vocabulary:

```
"single large softbox from 45° camera-left, 3:1 key-to-fill ratio, 
white V-flat reflector camera-right, clean catch light in both eyes"

"backlit by late-afternoon golden-hour sun from behind the subject, 
rim-lit silhouette with warm orange glow, subtle fill from an open sky camera-left"

"three-point studio setup: key strobe at 45° left, fill at half-power 
camera-right, hair light above and behind to separate from background"
```

### Element 5: Color Grade

Use film simulation names, color lab references, or specific grade descriptions:

```
"Fujifilm Pro Neg Hi simulation — subtle, warm, creamy highlights"
"Kodak Portra 400 scan — slightly overexposed, lifted shadows, warm cast"
"muted editorial palette — desaturated by 30%, cool shadow tint, warm highlight rolloff"
"high-contrast commercial — deep blacks, clean whites, neutral mid-tones"
```

### Gemini Reference Images

When using `reference_images` for character or object consistency:

- Maximum 14 images total; max 5 human portraits; max 6 distinct objects.
- Best results: 3–5 reference images from different angles / lighting conditions.
- Include reference images showing the subject in the target environment type (indoor vs outdoor) if possible.
- Encode images as base64 strings.

```python
import base64

def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

references = [encode_image("ref1.jpg"), encode_image("ref2.jpg")]
```

Pass as `reference_images=references` to `generate_image` or `conversational_image`.

### Gemini Parameter Selection

| Scenario | `size` | `aspect_ratio` |
|----------|--------|----------------|
| Social portrait | `2K` | `4:5` |
| Landscape editorial | `2K` | `3:2` |
| Vertical story / mobile | `2K` | `9:16` |
| Print / large format | `4K` | `3:2` or `4:3` |
| Fast iteration | `1K` | `1:1` |
| Cinematic widescreen | `2K` | `21:9` |

---

## Part III — Same Intent, Different Provider Expression

The following examples show how to express the same creative brief optimally for each provider.

### Brief: Moody portrait of a jazz musician backstage

**gpt-image-2 version:**
```
A weathered Black jazz trumpeter in his 60s seated backstage, 
his trumpet resting across his thighs, eyes downcast, 
documentary portrait photography in the style of Herman Leonard, 
single practical lamp from stage right casting deep amber warmth 
with strong shadow falling across the left side of his face, 
melancholy dignity, medium close-up, Kodak Tri-X film grain feel.
```
*Parameters: quality=high, 1024x1024, jpeg, compression=90*

**Gemini Nano Banana Pro version:**
```
Leica M11, 50mm f/1.4, a weathered Black jazz trumpeter in his early 60s 
seated backstage in a cramped dressing room, worn trumpet resting across his thighs, 
eyes cast downward in private reflection, single practical tungsten bulb to stage-right, 
creating deep amber warmth and strong contrast across his face, 
backstage mirror and costumes visible and out-of-focus in background, 
Kodak Tri-X 400 film simulation — high contrast, grain visible, rich blacks.
```
*Parameters: size=2K, aspect_ratio=4:5*

### Brief: E-commerce product shot of a perfume bottle

**gpt-image-2 version:**
```
An Art Deco glass perfume bottle with gold filigree cap, standing on 
a white marble slab, luxury product photography, single diffused 
backlight creating internal refraction and a rim of soft light around 
the bottle edges, minimal and aspirational, tack-sharp from base to cap, 
1:1 square crop, pure white background.
```
*Parameters: quality=high, 1024x1024, background=transparent, output_format=png*

**Gemini Nano Banana Pro version:**
```
Canon EOS R5, 100mm macro f/5.6, an Art Deco glass perfume bottle with 
gold filigree cap standing on white Carrara marble, single diffused 
Broncolor strobe from directly behind the bottle creating internal 
refraction — light refracting through the glass facets in fan patterns — 
with a secondary fill panel to camera-left at 1/4 power, 
pure white seamless background, no post-processing grade, clean commercial look.
```
*Parameters: size=4K, aspect_ratio=1:1*

---

## Part IV — Anti-Patterns

### ❌ Superlative Stacking Without Anchors

```
# BAD: Every adjective without grounding
"a beautiful professional stunning high-quality amazing detailed photo 
of a fantastic modern minimalist product"

# GOOD: Adjectives grounded in specific visual decisions
"a white ceramic mug with thin walls, matte exterior, handle just wide 
enough for two fingers, luxury product photography, single studio key 
light from above-left, clean white seamless background, tack-sharp"
```

### ❌ Telling the Model What NOT to Do

Negative instructions consume tokens without anchoring model behavior. Models can't "not do" something as reliably as they can "do something specific":

```
# BAD
"no blur, not too bright, no distracting background, avoid over-saturation, 
don't make it look AI-generated"

# GOOD
"crisp digital sharpness, balanced exposure, clean studio seamless background, 
natural desaturated palette"
```

### ❌ Overloading a Single Prompt

One image, one scene, one story. Attempting to cram multiple competing elements creates compositional confusion:

```
# BAD
"A busy coffee shop with people and plants and a rainy window and a cat 
and books and a barista and a warm fire and soft music visualized as 
floating notes and a neon sign and fairy lights"

# GOOD (pick the story)
"An empty coffee shop just before opening — morning light cuts through 
the window across the counter, a single stool askew, steam rising from 
a forgotten espresso, editorial interior photography, 3:2 landscape."
```

### ❌ Style Terms Without Anchors

```
# BAD
"cinematic moody dramatic aesthetic vibe"

# GOOD
"cinematic still — 2.39:1 letterbox, teal-orange grade, 
lens flare at upper left, shallow focus on subject"
```

---

## Part V — Iteration Strategy

When a generation misses:

1. **Identify the failure axis** — composition, lighting, color, subject accuracy, style register, technical quality. One axis at a time.

2. **Amplify the correct instruction** — if lighting is wrong, add three times more lighting detail. Don't add unrelated elements.

3. **Reduce prompt noise** — long prompts with many competing elements often produce muddled results. Strip to: subject + one dominant style anchor + lighting.

4. **Change the style reference anchor** — "editorial photography" vs "advertising photography" produces very different moods even with identical subject descriptions.

5. **Adjust parameters, not just prompt** — `quality=high` often resolves sharpness issues. `size` changes can shift composition dramatically. Try `background=opaque` if model keeps adding unwanted background elements.

6. **Switch to `edit_image` for refinement** — if the overall composition is right but specific details are wrong, don't re-generate. Hand the output path to `imagen:image-editor` for surgical correction.

7. **Try `enhance_prompt=false`** — if the model is reinterpreting your carefully-engineered prompt, disable the enhancement to run your exact text.
