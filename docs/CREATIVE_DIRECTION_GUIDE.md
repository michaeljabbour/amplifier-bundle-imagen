# Creative Direction Guide

Reference for `imagen:image-director` — visual design principles, the creative brief format, style vocabulary, and a critique framework for evaluating generated images against briefs.

---

## Purpose of Creative Direction

Creative direction is the discipline of translating intent into specific, unambiguous visual instructions. It sits between what a client or user *wants to feel* and what a prompt engineer can *encode into a model*. Without it, the pipeline suffers from:

- **Aesthetic drift**: Each generation takes a random interpretation of vague intent.
- **Revision loops**: Iterations never converge because there's no target to converge toward.
- **Provider mismatch**: Wrong provider chosen because the style register was never named.
- **Inconsistency in series**: Multiple images that don't feel like they belong together.

Good creative direction is ruthlessly specific. Every adjective should correspond to a visual property the model can encode. Every decision should reduce the space of possible interpretations.

---

## Part I — Visual Design Principles

### Composition

Composition is the arrangement of visual elements within the frame. It determines where the eye goes, what it rests on, and what story the image tells.

#### Rule of Thirds
Divide the frame into a 3×3 grid of nine equal rectangles. The four intersection points (known as "power points") are where the eye naturally rests. Placing primary subjects on these intersections creates visual interest and compositional tension:

- Subject at upper-left third: suggests motion, looking right into frame space.
- Subject at lower-right third: suggests weight, settling, conclusion.
- Horizon at upper third: emphasizes foreground / environmental context.
- Horizon at lower third: emphasizes sky / air / possibility.

#### Golden Ratio
The Fibonacci spiral creates a natural compositional path. The spiral guides the eye from the largest element to increasingly fine details. Use for:
- Organic subject matter (nature, portraiture)
- Compositions that need a fluid, non-mechanical feel
- Layouts where the rule of thirds produces too much visual tension

#### Symmetrical vs Asymmetrical Balance

**Symmetry** (subject centered, mirrored elements): Communicates authority, formality, stability, solemnity. Common in:
- Institutional photography (law, finance, government)
- Product shots requiring neutrality
- Architecture and interior photography emphasizing order

**Asymmetry** (subject off-center, unbalanced elements): Communicates dynamism, modernity, informality, tension. Common in:
- Editorial fashion and documentary
- Action and sports imagery
- Any composition requiring energy

#### Depth and Layering

Three-layer compositions (foreground / midground / background) create a sense of three-dimensional space in a two-dimensional frame:

- **Foreground elements** (partially in-frame, often blurred): Frame the subject; add context; reduce the visual "flatness" of digital imagery.
- **Midground**: The primary subject — where the eye is meant to land.
- **Background**: Context without competition. Should be de-emphasized (bokeh, shadow, distance haze) unless deliberately meaningful.

#### Negative Space

The empty space around and between subjects. Negative space:
- Gives the subject "room to breathe" — amplifies its weight and importance.
- Creates mood: wide negative space = isolation, loneliness, grandeur; tight negative space = intimacy, urgency.
- Is a key differentiator between editorial work (uses negative space deliberately) and commercial stock photography (fills the frame).

"Look room": when a subject faces a direction, leave negative space in that direction — the subject appears to have space to exist in.

### Lighting Design

Lighting is the art director's primary mood tool. The same subject, lit differently, produces completely different emotional registers.

#### The Three Qualities of Light

**Hard light** (point source, direct): Crisp shadow edges, strong texture revelation, high contrast, dramatic.
- Sources: Direct sun, bare flash, spotlight
- Emotional register: Drama, tension, authority, aggression, fashion-forward editorial

**Soft light** (large source, diffuse): Gradual shadow edges, flattering on skin, lower contrast, gentler.
- Sources: Overcast sky, window light through sheer, large softbox, bounce card
- Emotional register: Intimacy, warmth, approachability, lifestyle, calm

**Diffuse light** (ambient, directionless): No discernible shadow, flat and even.
- Sources: Solid overcast, shade without sky, north-facing studio window
- Emotional register: Clinical, graphic, pattern-focused, editorial restraint

#### Light Direction and Emotional Character

| Direction | Shadow Pattern | Character |
|-----------|---------------|-----------|
| **Front-lit** (flat) | Minimal shadows | Bright, open, clinical, catalog |
| **45° front** (Rembrandt) | Shadow triangle under opposite nostril | Flattering, sculptural, classic portraiture |
| **Side-lit** (split) | Half face in shadow | Dramatic, duality, tension, artistic |
| **Backlit** (rim/silhouette) | Subject rimmed or silhouetted | Spiritual, aspirational, mysterious, fashion |
| **Top-lit** | Eye socket shadows, underlighting contrast | Harsh, dramatic, architectural |
| **Under-lit** (footlight) | Upward shadows — unnatural | Eerie, horror, theatrical, surreal |

#### Practical Lighting in Scenes

Practical lights (lamps, candles, neon signs visible within the scene) create believable, naturalistic environments. Their position suggests motivation for the key light, even if the key light itself is a studio instrument. Describe practicals specifically:
- "Warm tungsten table lamp at frame-left"
- "Neon 'OPEN' sign casting red-cyan mixed light from behind subject"
- "Restaurant pendant lights creating warm pools of amber"

### Color Theory for Creative Briefs

Color carries emotional information and cultural associations that the model encodes into image mood.

#### Temperature
- **Warm** (oranges, ambers, reds): Energy, optimism, warmth, urgency, human connection, late afternoon.
- **Cool** (blues, greens, purples): Technology, calm, trust, sophistication, distance, morning or night.
- **Mixed temperature**: Visual tension; warmth vs coolness in the same frame creates dynamism. Common in architectural and landscape photography.

#### Saturation
- **Highly saturated**: Bold, playful, brand-forward, energetic.
- **Natural saturation**: Realistic, documentary, authentic.
- **Muted / desaturated**: Editorial restraint, art-house, timeless, classical.
- **Near-monochromatic**: Maximum focus on form and texture; fashion-forward; graphic.

#### Color Relationships
- **Complementary** (opposite on color wheel — e.g., orange and blue): Maximum visual contrast; punchy; used for hero moments and advertising.
- **Analogous** (neighbors on color wheel — e.g., orange, yellow-orange, yellow): Harmonious; natural; gentle; used for lifestyle and documentary.
- **Monochromatic** (single hue in different values): Sophisticated, deliberate, high-concept.
- **Split complementary**: One base color with the two colors adjacent to its complement; softer than true complementary.

---

## Part II — Style Registers

Style registers are the vocabulary for describing the visual genre an image belongs to. Naming the register precisely is the highest-leverage brief decision.

### Editorial

**Definition**: Photography in the tradition of print journalism and magazine editorial — authentic moments, unposed or minimally staged, often with context and imperfection valued as signal of truth.

**Visual markers**: Natural light preferred; settings are real environments, not controlled studios; subjects caught in action or expression rather than posed; post-processing is restrained (not fantasy-color-graded); slight imperfections (motion blur, grain, off-white whites) are features not bugs.

**Applications**: Magazine features, journalist storytelling, social-issue campaigns, brand editorial (when brand prioritizes authenticity over perfection).

**In briefs, write**: "Editorial photography — unposed, natural light, minimal post-processing, real environment."

### Cinematic

**Definition**: Still images that feel like stills from a film — a story is implied by the frame, and the viewer imagines what happened before and after.

**Visual markers**: Wide aspect ratios (2.39:1, 2:1, 16:9); color graded (most commonly teal-orange, though not exclusively); shallow depth of field used to isolate actors; lighting designed to reveal character (not just illuminate the subject); compositional space that implies offscreen action.

**Applications**: Brand storytelling, film and entertainment marketing, luxury automotive, adventure travel.

**In briefs, write**: "Cinematic still — 2.39:1 letterbox, color-graded with [color grade description], shallow focus, story implied."

### Documentary

**Definition**: Images that record reality with minimal intervention. Authenticity above aesthetics. The photographer sees rather than directs.

**Visual markers**: Available light; subjects in natural postures and expressions; environments that reveal life rather than presenting it; color treatment is representational, not dramatic; grain or noise accepted as cost of available light.

**Applications**: Social enterprise, nonprofit, journalism, any brand prioritizing real human stories over aspirational fantasy.

**In briefs, write**: "Documentary photography — available light, unstaged, authentic environment."

### Conceptual

**Definition**: Visual metaphor and symbolic imagery. The image expresses an idea rather than depicting a literal subject.

**Visual markers**: Surrealist juxtaposition (unexpected combinations); scale distortion (tiny people, giant objects); visual puns; abstraction; references to art history or cultural iconography; color and composition serve the concept rather than naturalism.

**Applications**: Thought leadership, philosophy or academic brands, abstract financial or tech concepts, opinion journalism.

**In briefs, write**: "Conceptual photography — visual metaphor [describe the metaphor], surreal scale/juxtaposition, [concept being illustrated]."

### Illustrative

**Definition**: Drawn, rendered, or hybrid visual aesthetic. Ranges from flat vector to oil-on-canvas to 3D render to ink wash.

**Sub-registers**:
- **Flat vector**: Clean geometric shapes, limited palette, no gradients or shadows. Used for icons, UI illustration, editorial spots.
- **Painterly**: Brush stroke texture, painterly color mixing, impressionist or expressionist feel.
- **Ink / line art**: Defined outlines, crosshatching, editorial spot illustration tradition.
- **3D render**: Photorealistic render from 3D software — CGI product, architectural visualization, game-adjacent.
- **Character illustration**: Figures with specific stylistic treatment — caricature, kawaii, realistic, heroic.

**In briefs, write**: "Illustrative — [sub-register], [palette constraint], [style reference]."

### Graphic Design

**Definition**: Composition is designed, not photographed. Grid-based, typography-integrated, brand-palette-driven.

**Visual markers**: Strong geometric structure; explicit type hierarchy; limited color palette from a brand system; icons and graphical elements; photography used as a texture or element, not as the primary story; white space used architecturally, not emotionally.

**Applications**: Infographics, marketing materials, event collateral, social media templates, advertising.

**In briefs, write**: "Graphic design aesthetic — grid-based, [palette], [typography weight/style], [tone]."

### Product

**Definition**: Subject-isolated photography optimized for e-commerce and packaging. Lighting reveals form, texture, and material quality.

**Visual markers**: Subject on white, grey, or lifestyle-relevant surface; background serves subject (never competes); lighting designed to show material properties (specular highlights for glass/metal, diffuse for matte surfaces, texture lighting for fabric); all angles considered for information completeness; no distracting environmental context.

**In briefs, write**: "Product photography — [background treatment], [surface material], [lighting to reveal X material property]."

---

## Part III — The Creative Brief Template

Use this template for every brief produced by `imagen:image-director`:

```markdown
## Creative Brief

**Project**: [One-line description of the deliverable]

**Intent**: [What this image must make the viewer feel, believe, or do]

**Subject**: [Precise primary subject description — include all relevant visual details]

**Secondary Elements**: [Supporting elements, their positions and relationships]

**Style Register**: [One from: editorial / cinematic / documentary / conceptual / illustrative / graphic-design / product — plus any sub-register]

**Framing**:
- Aspect ratio: [e.g., 3:2 landscape / 16:9 widescreen / 1:1 square / 2:3 portrait]
- Shot distance: [extreme close-up / close-up / medium / medium-wide / wide / extreme wide]
- Composition rule: [rule of thirds / centered / environmental / over-shoulder / etc.]

**Lighting**:
- Direction: [front / 45° left or right / side / back / top-down]
- Quality: [hard / soft / diffuse]
- Source type: [natural / studio / practical — specify type]
- Temperature: [warm / cool / neutral / mixed]

**Color**:
- Palette: [specific colors or color families — 2–3 dominant + 1 accent]
- Temperature: [warm / cool / neutral]
- Saturation: [high / natural / muted / near-monochromatic]
- Grade reference: [e.g., "Fuji Provia color pop", "desaturated editorial", "warm vintage film"]

**Mood**: [Three adjectives — e.g., "melancholy, intimate, contemplative"]

**Negative Space**: [What the image must avoid — competing elements, specific colors, tonal regions]

**Negative Constraints**: [What NOT to include — objects, people, colors, treatments]

**Provider Recommendation**: [OpenAI gpt-image-2 / Gemini Nano Banana Pro — one-sentence rationale]

**Size / Aspect**: [e.g., 1536×1024 / 2K + 16:9]

**Intended Use**: [Where this image will appear — website hero / social post / print / app store / etc.]

**Reference Feel**: [1–2 cultural shorthand references — photographer names, film titles, brand campaigns, art movements]
```

---

## Part IV — Critique Framework

When evaluating a generated image against a brief, score and comment on five axes. Any axis below 7 requires a specific revision instruction.

### Axis 1: Brief Adherence (0–10)

- Does the subject match the brief description?
- Are secondary elements present and positioned correctly?
- Is the style register correct?
- Is the framing (aspect, shot distance, composition) as specified?

**Revision trigger**: "The brief specified side-lighting; the generated image has flat front-lighting. Instruction for re-generation: [lighting revision]."

### Axis 2: Compositional Quality (0–10)

- Is the primary subject placed on a compositional power point?
- Is there appropriate negative space?
- Are leading lines present where specified?
- Does the composition direct the eye to the intended subject?

**Revision trigger**: "Subject is centered when the brief specified rule-of-thirds placement at left intersection. Instruction: adjust composition rule in prompt."

### Axis 3: Lighting Execution (0–10)

- Does the light direction match the brief?
- Is light quality (hard/soft) as specified?
- Is the shadow density appropriate for the brief's contrast requirement?
- Is the color temperature correct?

**Revision trigger**: "Light appears to be front-lit and flat; brief required Rembrandt side-lighting with triangle shadow. Add explicit lighting vocabulary to prompt."

### Axis 4: Color Fidelity (0–10)

- Does the overall palette match the brief's specified colors?
- Is the temperature (warm/cool) correct?
- Is saturation at the right level?
- Is any color grade or film simulation rendering?

**Revision trigger**: "Image appears cool and blue-shifted; brief specified warm amber palette. Adjust color description: add 'warm amber tones, orange-tinted shadows' to prompt."

### Axis 5: Mood Resonance (0–10)

- Does the image produce the intended emotional affect?
- Are all three mood adjectives from the brief present as visual experiences?
- Does anything in the image contradict the intended mood?

**Revision trigger**: "The brief specified 'melancholy'; the image feels neutral or pleasant rather than melancholy. Add: 'downcast gaze, underexposed by ½ stop, desaturated palette with cool shadow tone.'"

### Critique Output Format

```markdown
## Image Critique: [filename or generation ID]

| Axis | Score | Notes |
|------|-------|-------|
| Brief adherence | X/10 | [What matches / what doesn't] |
| Compositional quality | X/10 | [Composition assessment] |
| Lighting execution | X/10 | [Lighting match or gap] |
| Color fidelity | X/10 | [Color assessment] |
| Mood resonance | X/10 | [Emotional affect assessment] |

**Overall**: X/10 — [Accept / Revise / Regenerate]

**Revision Instructions** (for image-prompt-engineer):
[Specific, actionable revision instructions for any axis below 7]
```
