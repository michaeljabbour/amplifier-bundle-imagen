---
name: image-ascii-art
description: Bidirectional image <-> ASCII-art pipeline. Generate (or take) an image and render it as photorealistic ASCII via brightness mapping, OR rasterize ASCII back into an image — and decide which direction yields the best result, iterating between them. Supports adjustable width/detail, inverted ramps, 24-bit ANSI color, and zoomable HTML export. USE WHEN the user says 'ASCII art', 'make ASCII art of X', 'convert to ASCII', 'render as text/characters', 'ASCII portrait', 'image to ASCII', or 'ASCII to image'.
version: 1.1.0
---

# Skill: image-ascii-art

Turn pictures into ASCII art and ASCII art back into pictures. The core insight:
**good ASCII art is not random characters** — it is brightness mapping. Each
pixel's luminance selects a glyph from a dark→light ramp (`@%#*+=-:.<space>`),
so the glyphs reconstruct the photo's tones. Random characters only produce
static.

This skill pairs a self-contained converter (`scripts/asciiart.py`, Pillow-only)
with the image-generation tools so you can run the pipeline in **either
direction** and **iterate** until the result is good.

---

## When to use which direction

Assess the request, then pick a starting direction. You are expected to switch
direction or loop if the first result is weak.

| Situation | Direction |
|---|---|
| User has/wants a real picture rendered as text | **image → ASCII** (`to-ascii`) |
| User gives you ASCII and wants a real image of it | **ASCII → image** (`to-image`, then optionally feed as reference to `generate_image`) |
| User names a subject ("ASCII art of a fox") and has no image | **generate then convert**: `generate_image` → `to-ascii` |
| First ASCII looks muddy / unrecognizable | **loop back**: regenerate the source image with higher contrast / simpler composition, then re-convert |

There is no fixed order. If producing the ASCII first gives you a cleaner
structural target for the image (or vice versa), do that. Optimize for the
final artifact the user actually wants.

---

## Step 1 — Get a source image

- **Already have one?** Use its path directly.
- **Need to generate one?** Call the `generate_image` tool (from imagen-mcp /
  the `tool-imagen` module). For ASCII conversion, **bias the prompt toward
  high-contrast, well-lit, centered subjects on a plain background** — this is
  what makes the brightness ramp legible:

  > "Photorealistic dramatic high-contrast studio portrait of <subject>,
  > centered and filling the frame, strong rim lighting, plain dark background,
  > cinematic headshot."

  Save with `output_path` so you have a stable file path. If the provider
  returns a moderation-blocked or other user error, do not automatically retry
  or rephrase it to evade the decision. Explain the block generically and ask
  the user whether they want a substantively different, policy-compliant
  subject.

---

## Step 2 — Convert image → ASCII

Run the converter. Default width is 160 columns; raise it for more detail.

```bash
python3 scripts/asciiart.py to-ascii <image> --width 160 --out out.txt
```

Useful flags (all combinable):

| Flag | Effect |
|---|---|
| `--width N` | columns of output = detail level. 80 quick, 160 default, 200–300 fine |
| `--out FILE.txt` | write plain ASCII to a file |
| `--html FILE.html` | write a **colored, zoomable** HTML version (best "wow") |
| `--color` | print **24-bit ANSI color** to the terminal |
| `--invert` | flip the ramp for **light-background** terminals/editors |
| `--detailed` | use the 70-level ramp for finer tonal gradation |
| `--contrast F` / `--gamma F` | tune if the result is too flat/dark (defaults 1.5 / 1.0) |
| `--char-aspect F` | glyph height/width ratio; lower if output looks vertically stretched |

**Quality check (do this every time):** glance at the output. If the subject is
not recognizable, the fix is almost always at the *source*, not the ramp —
regenerate a higher-contrast, simpler image (Step 1) and re-convert. Only then
reach for `--contrast` / `--gamma` / `--detailed`.

---

## Step 3 — Convert ASCII → image (reverse direction)

To rasterize an ASCII `.txt` back into a real PNG (e.g. so it can be shared as
an image, or fed back to `generate_image` as a structural reference):

```bash
python3 scripts/asciiart.py to-image art.txt --out art_render.png --font-size 14
```

To then produce a *polished* image guided by the ASCII structure, pass
`art_render.png` to `generate_image` as a `reference_image` (Gemini) with a
prompt describing the desired finish.

---

## Step 4 — Deliver

- Show the user the ASCII inline (it reads best **zoomed out** in a monospace
  font — say so).
- Report the saved file paths (`.txt`, `.html`, `.png`).
- If you wrote an `.html`, mention it's the most shareable/zoomable form.
- Offer the obvious next knob: wider/more detail, inverted, colored, or the
  reverse direction.

---

## Notes

- **Dependency:** Pillow only (`pip install Pillow`). No network needed for
  conversion itself; only Step 1 generation uses the image tools.
- **Terminal viewing:** ANSI color needs a truecolor terminal. HTML works
  everywhere and zooms cleanly.
- **Editors wrapping lines:** wide output (160+ cols) must not be soft-wrapped
  or the picture breaks — tell the user to disable wrap / shrink font.
- **Portability:** this same folder works as a Claude Code / Claude Desktop
  skill under `~/.claude/skills/image-ascii-art/` and as an Amplifier bundle
  skill under `amplifier-bundle-imagen/skills/image-ascii-art/`.
