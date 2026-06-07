# asciiart.py

Self-contained, bidirectional image ↔ ASCII-art converter. Pillow is the only
dependency.

```bash
pip install Pillow

# image -> ASCII
python3 asciiart.py to-ascii face.png --width 200 --out face.txt
python3 asciiart.py to-ascii face.png --width 160 --color          # ANSI in terminal
python3 asciiart.py to-ascii face.png --width 220 --html face.html # shareable / zoomable
python3 asciiart.py to-ascii logo.png --invert --detailed          # light bg + fine ramp

# ASCII -> image
python3 asciiart.py to-image face.txt --out face_render.png
```

`to-ascii -h` / `to-image -h` list every flag. It works as a plain CLI; the
`SKILL.md` one level up wraps it with image-generation and direction-choosing
logic.
