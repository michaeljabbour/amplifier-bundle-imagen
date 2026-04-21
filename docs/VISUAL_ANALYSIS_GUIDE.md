# Visual Analysis Guide

Reference for `imagen:image-researcher` — how to systematically extract visual properties from images, produce structured analysis reports, handle URL vs local-file sources, and generate reverse-prompt reconstructions for handoff to `imagen:image-prompt-engineer`.

---

## Purpose of Visual Analysis

Visual analysis serves three functions in the imagen pipeline:

1. **Style matching**: When a user provides a reference image they want to match, visual analysis extracts the visual DNA in text form so a prompt engineer can reproduce it without needing to pass the reference image to the model (which only Gemini supports, and only for up to 14 images).

2. **Quality assessment**: When evaluating generated images against a brief, visual analysis provides objective observation before the subjective critique. What is actually in the image vs what the brief specified?

3. **Exploration and explanation**: When a user wants to understand why an image works (or doesn't), visual analysis names the technical mechanisms behind the aesthetic effect.

---

## The Seven-Dimension Framework

Analyze every image across all seven dimensions. Even dimensions that seem irrelevant (e.g., "no grain in this clean digital image") should be noted — their absence is also informative.

### Dimension 1: Compositional Structure

**What to look for:**

- **Subject placement**: Where is the primary subject in the frame? Express as fraction of frame width/height from left/top. Map to compositional rule (e.g., "left third, eye level — rule of thirds").
- **Aspect ratio**: Measure or estimate. Common: 1:1, 3:2, 4:3, 16:9, 2.39:1.
- **Orientation**: Portrait (taller than wide) / landscape (wider than tall) / square.
- **Shot distance**: Extreme close-up (full frame = detail of face/object) / close-up (head and shoulders) / medium (waist up) / medium-wide (full figure with context) / wide (environment dominant) / extreme wide (environment dominant, subject small).
- **Depth layers**: How many distinct planes? Foreground / midground / background? Are they distinguishable or compressed (telephoto)?
- **Leading lines**: Any diagonal, curved, or converging lines that guide the eye?
- **Negative space**: Amount and location. Does the subject have "look room" (space in the direction they face)?
- **Frame within frame**: Architectural or environmental elements that form a natural frame around the subject?
- **Symmetry**: Is the composition balanced symmetrically, or asymmetrically?

**Output format:**
```
Composition:
  Subject placement: [description + fraction]
  Shot distance: [type]
  Aspect ratio: [ratio]
  Depth: [layer description]
  Leading lines: [present/absent + description]
  Negative space: [amount + position]
  Compositional rule: [rule of thirds / centered / etc.]
```

### Dimension 2: Lighting

**What to look for:**

- **Key light direction**: Where is the primary light coming from? Look at shadow direction and position on face/subject. Shadow falls away from the light source.
  - Shadow directly behind subject → front-lit
  - Shadow at side → side-lit
  - Shadow forward of subject → backlit
  - Shadow at 45° → 45° lighting (Rembrandt-style)
- **Key light quality**: Look at shadow edge sharpness.
  - Hard edge → hard light (small source or distant source)
  - Soft gradient edge → soft light (large source, close)
  - No shadow → flat/ambient/diffuse light
- **Shadow density**: Ratio of light to shadow. Deep, crushed shadows → high ratio (dramatic). Open, visible shadow detail → low ratio (gentle).
- **Catchlights**: In portrait subjects, the shape and position of the catchlight in the eye reveals the light source type (circle = octabox/ring flash; square = softbox; horizontal strip = strip light; diffuse = window).
- **Color temperature of light**: Warm (amber, orange) / Cool (blue, teal) / Neutral (white) / Mixed.
- **Practical lights**: Are there visible light sources in frame? (Lamps, neon, windows, candles.) Their presence explains the ambient fill.
- **Rim / backlight**: Is there a rim or backlight separating subject from background?

**Output format:**
```
Lighting:
  Key direction: [front / 45° left or right / side / back]
  Key quality: [hard / soft / diffuse]
  Shadow density: [deep-crushed / natural / open / no shadow]
  Color temperature: [warm / cool / neutral / mixed — approximate Kelvin if assessable]
  Catchlight shape (if portrait): [circle / square / strip / diffuse]
  Rim/backlight: [present/absent]
  Practical lights: [visible/absent — describe if present]
```

### Dimension 3: Color Palette

**What to look for:**

- **Dominant hues**: The 2–3 colors that occupy the most visual area. Name them specifically (not just "blue" — "desaturated steel blue" or "warm amber").
- **Accent hues**: Contrasting or complementary colors used sparingly for visual interest.
- **Overall temperature**: Warm / cool / neutral / mixed.
- **Saturation level**: Rate from 1–10 or describe: highly saturated / natural / muted / near-monochromatic.
- **Tonal range**: Full-range (deep blacks and bright whites) / high-key (compressed toward bright) / low-key (compressed toward dark).
- **Highlight character**: Blown out? Rolled off? Warm or cool highlights?
- **Shadow character**: Crushed to black? Open shadow detail? Warm or cool shadow tones?
- **Color grade signature**: Look for:
  - **Orange skin + teal background** → teal-orange Hollywood grade
  - **Lifted blacks** → matte/faded finish (Instagram-era)
  - **Green shadows** → cross-process film grade
  - **Warm highlights + cool shadows** → split-tone (common in portrait work)
  - **Even, natural tone curve** → no visible grade

**Output format:**
```
Color:
  Dominant hues: [list 2–3 with adjectives]
  Accent hues: [list or "none"]
  Temperature: [warm / cool / neutral / mixed]
  Saturation: [1–10 or descriptive]
  Tonal range: [full / high-key / low-key]
  Grade signature: [teal-orange / matte / cross-process / split-tone / natural / etc.]
```

### Dimension 4: Style Register

Identify the style register by asking:

- Is this photographed or illustrated? If photographed, does it look staged or authentic?
- Is the image optimized for beauty or for truth?
- What publication or context would this image appear in?
- Is the post-processing visible and dramatic, or restrained and naturalistic?

Use the register vocabulary from the Creative Direction Guide:
**editorial / cinematic / documentary / conceptual / illustrative / graphic-design / product**

Add sub-registers where relevant (e.g., "editorial portrait", "cinematic — film noir influenced", "product — luxury packaging").

### Dimension 5: Mood and Affect

**What to look for:**

Describe in three adjectives, then explain **which visual elements produce that affect**:

```
Mood: [adjective 1, adjective 2, adjective 3]

Mechanisms:
- [adjective 1] produced by: [specific technical elements]
- [adjective 2] produced by: [specific technical elements]
- [adjective 3] produced by: [specific technical elements]
```

**Examples of mood → mechanism mapping:**

| Mood | Technical Mechanism |
|------|-------------------|
| Melancholy | Subject gaze averted; underexposed -½ stop; cool desaturated shadows; negative space in direction of gaze |
| Energetic | Warm saturated palette; motion blur or frozen action; wide angle close-up; high key exposure |
| Authoritative | Centered symmetry; low camera angle (subject looks down at viewer); neutral or cool palette; sharp focus |
| Intimate | Shallow DoF blurring context; soft window light; subject looking at camera; warm temperature; tight framing |
| Serene | Wide negative space; blue-hour or overcast light; horizontal composition; muted palette; no action |
| Eerie | Under-lighting; unexpected scale; absence of human presence in human context; strong shadow; cool cast |

### Dimension 6: Technical Qualities

**What to look for:**

- **Apparent resolution**: Tack-sharp detail (high resolution) / soft but intentional (low DoF or medium format softness) / soft and unintentional (motion blur, compression artifacts).
- **Depth of field**: Estimate aperture equivalent from background blur. Near-wide-open (f/1.2–f/2) → heavy bokeh, very shallow. f/5.6–f/8 → moderate. f/11+ → deep focus.
- **Shutter character**: Frozen motion (fast shutter) / motion blur (slow shutter / panning) / unclear.
- **Grain / noise character**: None (clean digital) / fine-grained (high-ISO digital or medium-speed film) / heavy grain (high-ISO or pushed film) / chromatic noise (high-ISO digital).
- **Lens character**: Any visible distortion (barrel = wide angle), vignetting, chromatic aberration at edges, anamorphic oval bokeh?
- **Format feel**: Does it look like a phone camera, a full-frame DSLR, medium format, a film scan, or a drone?
- **Post-processing intensity**: Unprocessed / lightly processed / heavily processed.

### Dimension 7: Subject-Specific Properties

Report properties relevant to the image's primary subject:

**For portraits:**
- Apparent age range
- Ethnicity (as relevant to brief accuracy)
- Expression and emotional state
- Gaze direction (at camera / averted / downward / upward)
- Clothing style and color
- Hair style, length, color
- Visible skin quality (makeup, natural, textured)

**For products:**
- Material (glass, metal, ceramic, fabric, plastic, wood)
- Surface treatment (matte, gloss, brushed, rough, polished)
- Form language (round / angular / organic / geometric)
- Scale indicators (surrounding context objects that suggest product size)

**For environments / spaces:**
- Architectural style and era
- Indoor / outdoor
- Season and weather
- Time of day
- Geographic or cultural feel

**For abstract / conceptual:**
- Symbolic elements present
- Visual metaphors or juxtapositions
- Color symbolism
- Compositional geometry (circle, triangle, diagonal tension)

---

## Handling Image Sources

### Local File Paths

When given a local path (e.g., `/tmp/reference.jpg`, `~/Downloads/inspiration.png`):

1. Confirm the file exists using filesystem tools before attempting analysis.
2. Use vision-capable model analysis to inspect the image content directly.
3. Report the file resolution and format in the technical dimension.

### URLs

When given an image URL:
1. Attempt to fetch the image directly.
2. If the URL is a CDN or direct image URL, it should be accessible for analysis.
3. If access fails (authentication required, region-blocked), flag this and request the user provide a local copy.
4. Note: Some social media platform URLs embed session tokens that expire — flag if the URL may not be stable.

### Multiple Reference Images

When analyzing multiple images for a shared style:

**Step 1**: Analyze each image independently using the full seven-dimension framework.

**Step 2**: Create a comparison table:

| Dimension | Image 1 | Image 2 | Image 3 |
|-----------|---------|---------|---------|
| Composition | ... | ... | ... |
| Lighting | ... | ... | ... |
| Color | ... | ... | ... |
| Style register | ... | ... | ... |
| Mood | ... | ... | ... |
| Technical | ... | ... | ... |

**Step 3**: Identify the intersection (consistent across all images) vs divergence (varies between images).

**Step 4**: Synthesize a unified "visual signature" brief from the intersection elements. Flag divergences as decisions for `imagen:image-director`.

---

## Prompt Reconstruction Section

Every analysis report should close with a "Prompt Reconstruction" section — a concise prompt in the appropriate provider grammar that would likely reproduce the image's aesthetic.

### Format

```markdown
## Prompt Reconstruction

**Provider recommendation**: [OpenAI gpt-image-2 / Gemini Nano Banana Pro]
**Rationale**: [One sentence on why this provider]

**gpt-image-2 version** (if OpenAI):
[Subject + style + lighting + mood + technical — one paragraph]

**Gemini version** (if Gemini):
[Camera + lens + subject + environment + lighting + grade — one paragraph]

**Key parameters**:
- quality/size: [value]
- aspect_ratio/size: [value]
- output_format: [value if relevant]
```

### Example

```markdown
## Prompt Reconstruction

**Provider recommendation**: Gemini Nano Banana Pro
**Rationale**: Photorealistic portrait with material detail (worn leather, skin texture) — Gemini's strength.

**Gemini version**:
Sony A7 IV, 85mm f/1.4, a man in his late 50s with silver beard and weathered face 
wearing a worn leather jacket, seated at a small bar, warm amber practical light from 
a single low-watt bulb at frame-right, one hand wrapped around a glass, gaze downward 
and reflective, bar mirror catching soft light in the background at bokeh, 
muted desaturated palette, Kodak Portra 800 pushed film simulation, strong shadow 
on left side of face.

**Key parameters**:
- size: 2K
- aspect_ratio: 4:5
```

---

## Output Template

```markdown
## Visual Analysis: [image identifier]

### Composition
- Aspect ratio: [ratio]
- Subject placement: [position + compositional rule]
- Shot distance: [type]
- Depth: [layer description]
- Leading lines: [description or "none prominent"]
- Negative space: [amount + position]

### Lighting
- Key direction: [direction]
- Key quality: [hard / soft / diffuse]
- Shadow density: [description]
- Temperature: [warm / cool / neutral / mixed]
- Notable: [catchlights, rim light, practicals — describe]

### Color
- Dominant palette: [2–3 named hues]
- Accent: [or "none"]
- Temperature: [warm / cool / neutral]
- Saturation: [level]
- Grade signature: [or "natural / ungraded"]

### Style Register
[Named register + one-sentence justification]

### Mood
[Three adjectives]
- [Adjective 1] → [technical mechanism]
- [Adjective 2] → [technical mechanism]
- [Adjective 3] → [technical mechanism]

### Technical Qualities
- Apparent resolution: [assessment]
- Depth of field: [shallow / normal / deep + aperture estimate]
- Grain/noise: [none / fine / heavy / character description]
- Format feel: [full-frame digital / medium format / film scan / phone / etc.]
- Post-processing: [none / light / heavy + style]

### Subject Properties
[Subject-specific properties as relevant]

---

## Prompt Reconstruction
[Provider recommendation + rationale + prompt version(s) + key parameters]
```
