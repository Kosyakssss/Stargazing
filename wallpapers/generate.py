#!/usr/bin/env python3
"""Generate Stargazing Death of Socrates engraving wallpapers."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "aligned-source.png"
PALETTE = ROOT.parent / "dist" / "stargazing.json"
OUTPUT = ROOT / "6k"
WORK = ROOT / ".work"
WIDTH, HEIGHT = 6016, 3384


def run(*args: object) -> None:
    subprocess.run([str(arg) for arg in args], check=True)


def main() -> None:
    magick = shutil.which("magick")
    if not magick:
        raise SystemExit("ImageMagick 7 is required.")
    if not SOURCE.is_file():
        raise SystemExit(f"Missing source image: {SOURCE}")

    palette = json.loads(PALETTE.read_text())
    OUTPUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    master = WORK / "engraving-master.png"

    # Difference-of-Gaussians reconstructs linework rather than retaining the
    # painting's tonal blocks. The threshold leaves sparse etched texture in
    # stone and cloth while keeping the broad background quiet.
    run(
        magick, SOURCE,
        "-auto-orient",
        "-filter", "Lanczos",
        "-resize", f"{WIDTH}x{HEIGHT}^",
        "-gravity", "center",
        "-extent", f"{WIDTH}x{HEIGHT}",
        "-colorspace", "Gray",
        "-morphology", "Convolve", "DoG:0,0,2",
        "-negate",
        "-normalize",
        "-threshold", "76%",
        "-morphology", "Dilate", "Diamond:1",
        "-strip",
        master,
    )

    files: list[Path] = []
    for slug, theme in palette["themes"].items():
        base = theme["base"]
        variants = {
            "light": (base["400"]["hex"], base["paper"]["hex"]),
            "dark": (base["700"]["hex"], base["black"]["hex"]),
        }
        for mode, (line, background) in variants.items():
            destination = OUTPUT / f"{slug}-{mode}.png"
            run(
                magick, master,
                "+level-colors", f"{line},{background}",
                "-colorspace", "sRGB",
                "-define", "png:compression-level=9",
                "-strip",
                destination,
            )
            files.append(destination)
            print(destination)

    # Two columns: light and dark. Rows follow palette family order.
    rows: list[Path] = []
    for index in range(0, len(files), 2):
        row = WORK / f"row-{index // 2}.png"
        run(
            magick,
            "(", files[index], "-thumbnail", "800x450", ")",
            "(", files[index + 1], "-thumbnail", "800x450", ")",
            "+append", row,
        )
        rows.append(row)
    run(magick, *rows, "-append", "-quality", "90", ROOT / "contact-sheet.jpg")


if __name__ == "__main__":
    main()
