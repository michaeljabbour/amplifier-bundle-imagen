#!/usr/bin/env python3
"""
asciiart.py — bidirectional image <-> ASCII-art converter.

Self-contained CLI used by the `image-ascii-art` skill. Only dependency is
Pillow. Two subcommands:

  to-ascii  IMAGE   -> render an image as ASCII (txt / ANSI color / HTML)
  to-image  ASCII   -> rasterize ASCII text back into a PNG image

Brightness mapping, not randomness: each pixel's luminance picks a glyph from a
dark->light ramp, so the glyphs reconstruct the photo's tones. Run with -h on
either subcommand for the full option list.

Examples:
  python3 asciiart.py to-ascii face.png --width 200 --out face.txt
  python3 asciiart.py to-ascii face.png --width 160 --color            # ANSI in terminal
  python3 asciiart.py to-ascii face.png --width 220 --html face.html   # shareable, zoomable
  python3 asciiart.py to-ascii logo.png --invert                       # light-background terminals
  python3 asciiart.py to-image face.txt --out face_render.png          # ASCII -> image
"""
from __future__ import annotations

import argparse
import html as _html
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required:  pip install Pillow")

# Dark -> light. Index 0 is the densest glyph (for the darkest pixel).
RAMP_STANDARD = "@%#*+=-:. "
RAMP_DETAILED = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "


def _load_gray(img: Image.Image, contrast: float, gamma: float) -> Image.Image:
    g = ImageOps.autocontrast(img.convert("L"), cutoff=2)
    if contrast != 1.0:
        g = ImageEnhance.Contrast(g).enhance(contrast)
    if gamma != 1.0:
        lut = [min(255, int((i / 255.0) ** gamma * 255)) for i in range(256)]
        g = g.point(lut)
    return g


def _grid_size(w: int, h: int, cols: int, char_aspect: float) -> tuple[int, int]:
    """Rows chosen so the glyph grid keeps the image's proportions.

    char_aspect = glyph_height / glyph_width (terminal cells are ~2x tall).
    """
    rows = max(1, int(cols * (h / w) / char_aspect))
    return cols, rows


def to_ascii(
    path: str,
    cols: int = 160,
    contrast: float = 1.5,
    gamma: float = 1.0,
    invert: bool = False,
    detailed: bool = False,
    char_aspect: float = 2.0,
):
    """Return (lines, color_grid).

    lines       : list[str], the plain-glyph rows.
    color_grid  : list[list[(r,g,b)]] sampled from the source for color output.
    """
    src = Image.open(path)
    if src.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", src.size, (0, 0, 0))
        bg.paste(src.convert("RGBA"), mask=src.convert("RGBA").split()[-1])
        src = bg
    else:
        src = src.convert("RGB")

    w, h = src.size
    cols, rows = _grid_size(w, h, cols, char_aspect)

    gray = _load_gray(src, contrast, gamma).resize((cols, rows))
    color = src.resize((cols, rows))
    gpx = gray.load()
    cpx = color.load()
    assert gpx is not None and cpx is not None

    ramp = RAMP_DETAILED if detailed else RAMP_STANDARD
    if invert:
        ramp = ramp[::-1]
    n = len(ramp)

    lines: list[str] = []
    color_grid: list[list[tuple[int, int, int]]] = []
    for y in range(rows):
        row_chars, row_colors = [], []
        for x in range(cols):
            lum = gpx[x, y] / 255.0
            idx = int((1 - lum) * (n - 1))  # dark pixel -> dense glyph
            row_chars.append(ramp[idx])
            row_colors.append(cpx[x, y])
        lines.append("".join(row_chars))
        color_grid.append(row_colors)
    return lines, color_grid


def render_ansi(lines, color_grid) -> str:
    out = []
    for row, colors in zip(lines, color_grid):
        buf = []
        for ch, (r, g, b) in zip(row, colors):
            buf.append(f"\x1b[38;2;{r};{g};{b}m{ch}")
        buf.append("\x1b[0m")
        out.append("".join(buf))
    return "\n".join(out)


def render_html(lines, color_grid, title: str = "ASCII Art") -> str:
    rows = []
    for row, colors in zip(lines, color_grid):
        spans = []
        for ch, (r, g, b) in zip(row, colors):
            ec = _html.escape(ch)
            spans.append(f'<span style="color:#{r:02x}{g:02x}{b:02x}">{ec}</span>')
        rows.append("".join(spans))
    body = "\n".join(rows)
    return (
        "<!doctype html><meta charset='utf-8'>"
        f"<title>{_html.escape(title)}</title>"
        "<style>"
        "html,body{margin:0;background:#000}"
        "pre{font-family:'SF Mono',Menlo,Consolas,monospace;"
        "font-size:7px;line-height:7px;letter-spacing:0;white-space:pre;"
        "color:#fff;padding:12px}"
        "</style>"
        f"<pre>{body}</pre>"
    )


def to_image(
    ascii_path: str,
    out_path: str,
    font_size: int = 14,
    fg: tuple[int, int, int] = (235, 235, 235),
    bg: tuple[int, int, int] = (0, 0, 0),
):
    """Rasterize an ASCII .txt file back into a PNG image."""
    text = Path(ascii_path).read_text(encoding="utf-8", errors="replace").rstrip("\n")
    lines = text.split("\n")
    cols = max((len(ln) for ln in lines), default=1)
    rows = len(lines)

    font = None
    for name in ("Menlo.ttc", "DejaVuSansMono.ttf", "Consola.ttf", "Courier New.ttf"):
        try:
            font = ImageFont.truetype(name, font_size)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()

    # measure a representative monospace cell
    box = font.getbbox("M")
    cw = max(1, box[2] - box[0])
    ch = max(1, int((box[3] - box[1]) * 1.35))

    img = Image.new("RGB", (int(cols * cw + 16), int(rows * ch + 16)), bg)
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        draw.text((8, 8 + i * ch), line, font=font, fill=fg)
    img.save(out_path)
    return img.size


def _cmd_to_ascii(a) -> int:
    lines, colors = to_ascii(
        a.image,
        cols=a.width,
        contrast=a.contrast,
        gamma=a.gamma,
        invert=a.invert,
        detailed=a.detailed,
        char_aspect=a.char_aspect,
    )
    if a.html:
        Path(a.html).write_text(render_html(lines, colors, Path(a.image).stem), encoding="utf-8")
        print(f"HTML written: {a.html}  ({len(lines[0])}x{len(lines)} cells)")
    if a.out:
        Path(a.out).write_text("\n".join(lines), encoding="utf-8")
        print(f"Text written: {a.out}  ({len(lines[0])}x{len(lines)} chars)")
    wrote_file = bool(a.html or a.out)
    if a.color:
        print(render_ansi(lines, colors))  # color always goes to the terminal
    elif not wrote_file:
        print("\n".join(lines))  # no files, no color -> plain text to stdout
    return 0


def _cmd_to_image(a) -> int:
    size = to_image(a.ascii, a.out, font_size=a.font_size)
    print(f"Image written: {a.out}  ({size[0]}x{size[1]} px)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("to-ascii", help="image -> ASCII art")
    a.add_argument("image")
    a.add_argument("--width", type=int, default=160, help="columns of output (detail). default 160")
    a.add_argument("--out", help="write plain ASCII to this .txt")
    a.add_argument("--html", help="write a colored, zoomable .html")
    a.add_argument("--color", action="store_true", help="print 24-bit ANSI color to terminal")
    a.add_argument("--invert", action="store_true", help="invert ramp (light-background terminals)")
    a.add_argument("--detailed", action="store_true", help="use the 70-level ramp for finer detail")
    a.add_argument("--contrast", type=float, default=1.5, help="contrast boost. default 1.5")
    a.add_argument("--gamma", type=float, default=1.0, help="gamma. <1 brightens shadows. default 1.0")
    a.add_argument("--char-aspect", type=float, default=2.0, help="glyph height/width ratio. default 2.0")
    a.set_defaults(func=_cmd_to_ascii)

    b = sub.add_parser("to-image", help="ASCII art -> PNG image")
    b.add_argument("ascii", help="path to an ASCII .txt file")
    b.add_argument("--out", required=True, help="output .png path")
    b.add_argument("--font-size", type=int, default=14)
    b.set_defaults(func=_cmd_to_image)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
