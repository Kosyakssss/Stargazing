#!/usr/bin/env python3
"""Generate the five final dark Stargazing wallpapers from approved gen 11 artwork."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments" / "11-source-aligned-boundaries" / "mineral-paper-dark.png"
PALETTE = ROOT.parent / "dist" / "stargazing.json"
OUT = ROOT / "final"

SOURCE_LINE = "#686B6A"
SOURCE_BACKGROUND = "#0F1111"

# Grey Fruit keeps its semantic UI palette, but its wallpaper uses the
# Graphite Balanced treatment: neutral, darker, and closer to the other
# Stargazing families' contrast.
WALLPAPER_OVERRIDES = {
    "grey-fruit": {"line": "#626262", "background": "#121212"},
}


def run(*args: object) -> None:
    subprocess.run([str(arg) for arg in args], check=True)


def main() -> None:
    magick = shutil.which("magick")
    if not magick:
        raise SystemExit("ImageMagick 7 is required.")
    if not SOURCE.exists():
        raise SystemExit(f"Approved gen 11 source is missing: {SOURCE}")

    themes = json.loads(PALETTE.read_text())["themes"]
    OUT.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []

    for slug, theme in themes.items():
        override = WALLPAPER_OVERRIDES.get(slug)
        if override:
            line, background = override["line"], override["background"]
        elif "semantic" in theme:
            roles = theme["semantic"]["dark"]
            line, background = roles["tx3"]["hex"], roles["bg"]["hex"]
        else:
            base = theme["base"]
            line, background = base["600"]["hex"], base["black"]["hex"]
        destination = OUT / f"{slug}-dark.png"
        run(
            magick, SOURCE,
            "-fill", line, "-opaque", SOURCE_LINE,
            "-fill", background, "-opaque", SOURCE_BACKGROUND,
            "-colorspace", "sRGB", "-strip",
            "-define", "png:compression-level=9", destination,
        )
        outputs.append(destination)

    thumbnails: list[object] = []
    for image in outputs:
        thumbnails += ["(", image, "-thumbnail", "800x450", ")"]
    run(magick, *thumbnails, "-append", "-quality", "92", OUT / "contact-sheet.jpg")
    print(OUT)


if __name__ == "__main__":
    main()
