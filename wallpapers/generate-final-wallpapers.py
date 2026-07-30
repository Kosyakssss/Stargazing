#!/usr/bin/env python3
"""Generate all eight final Stargazing wallpapers from the approved gen 11 artwork."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments" / "11-source-aligned-boundaries" / "mineral-paper-light.png"
PALETTE = ROOT.parent / "dist" / "stargazing.json"
OUT = ROOT / "final"

SOURCE_LINE = "#7E8080"
SOURCE_BACKGROUND = "#EDF0EF"


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
        if "semantic" in theme:
            variants = tuple(
                (mode, roles["tx3"]["hex"], roles["bg"]["hex"])
                for mode, roles in theme["semantic"].items()
            )
        else:
            base = theme["base"]
            variants = (
                ("light", base["500"]["hex"], base["paper"]["hex"]),
                ("dark", base["600"]["hex"], base["black"]["hex"]),
            )
        for mode, line, background in variants:
            destination = OUT / f"{slug}-{mode}.png"
            run(
                magick, SOURCE,
                "-fill", line, "-opaque", SOURCE_LINE,
                "-fill", background, "-opaque", SOURCE_BACKGROUND,
                "-colorspace", "sRGB", "-strip",
                "-define", "png:compression-level=9", destination,
            )
            outputs.append(destination)

    rows: list[Path] = []
    for index in range(0, len(outputs), 2):
        row = OUT / f".contact-row-{index // 2}.png"
        run(
            magick,
            "(", outputs[index], "-thumbnail", "800x450", ")",
            "(", outputs[index + 1], "-thumbnail", "800x450", ")",
            "+append", row,
        )
        rows.append(row)
    run(magick, *rows, "-append", "-quality", "92", OUT / "contact-sheet.jpg")
    for row in rows:
        row.unlink()
    print(OUT)


if __name__ == "__main__":
    main()
