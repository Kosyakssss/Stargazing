#!/usr/bin/env python3
"""Add restrained local detail to the exact assertive-crop baseline."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "aligned-source.png"
PALETTE = ROOT.parent / "dist" / "stargazing.json"
OUT = ROOT / "experiments" / "07-assertive-selective-detail"
WORK = OUT / ".work"
WIDTH, HEIGHT = 6016, 3384


def run(*args: object) -> None:
    subprocess.run([str(arg) for arg in args], check=True)


def main() -> None:
    magick = shutil.which("magick")
    if not magick:
        raise SystemExit("ImageMagick 7 is required.")
    shutil.rmtree(OUT, ignore_errors=True)
    WORK.mkdir(parents=True)

    crop = WORK / "crop.png"
    dog = WORK / "dog.png"
    baseline = WORK / "baseline.png"
    focal_detail = WORK / "focal-detail.png"
    architecture_detail = WORK / "architecture-detail.png"

    # These are copied exactly from experiment 03.
    run(
        magick, SOURCE, "-auto-orient", "-filter", "Lanczos",
        "-resize", f"{round(WIDTH * 1.42)}x{round(HEIGHT * 1.42)}^",
        "-gravity", "center", "-extent", f"{WIDTH}x{HEIGHT}",
        "-colorspace", "Gray", "-strip", crop,
    )
    run(magick, crop, "-morphology", "Convolve", "DoG:0,0,2", "-negate", "-normalize", dog)
    run(magick, dog, "-threshold", "77.5%", "-morphology", "Dilate", "Diamond:1", baseline)

    # More permissive thresholds reveal extra local marks. The focal pass is
    # deliberate; architecture changes by only three tenths of one percent.
    run(magick, dog, "-threshold", "79.0%", "-morphology", "Dilate", "Diamond:1", focal_detail)
    run(magick, dog, "-threshold", "77.8%", "-morphology", "Dilate", "Diamond:1", architecture_detail)

    focal_mask = WORK / "focal-mask.png"
    architecture_mask = WORK / "architecture-mask.png"
    run(
        magick, "-size", f"{WIDTH}x{HEIGHT}", "xc:black", "-fill", "white",
        # Socrates, including torso, face, robes, and raised hand.
        "-draw", "ellipse 4100,1800 1450,1900 0,360",
        # The cup, both exchanging hands, and the cup-bearer's forearm.
        "-draw", "ellipse 3000,1510 1150,720 0,360",
        focal_mask,
    )
    run(
        magick, "-size", f"{WIDTH}x{HEIGHT}", "xc:black", "-fill", "white",
        # Visible inner edge and masonry of the cropped arch.
        "-draw", "rectangle 0,0 1850,3384",
        # Upper wall and its major stone joints.
        "-draw", "rectangle 1500,0 6016,1480",
        architecture_mask,
    )

    def isolate(detail: Path, mask: Path, destination: Path) -> None:
        inverse = destination.with_name(destination.stem + "-inverse.png")
        run(magick, mask, "-negate", inverse)
        # White outside the mask; detailed black marks only inside it.
        run(magick, detail, inverse, "-compose", "Lighten", "-composite", destination)

    focal_overlay = WORK / "focal-overlay.png"
    architecture_overlay = WORK / "architecture-overlay.png"
    isolate(focal_detail, focal_mask, focal_overlay)
    isolate(architecture_detail, architecture_mask, architecture_overlay)

    final_mask = WORK / "final-mask.png"
    run(
        magick, baseline, focal_overlay, "-compose", "Darken", "-composite",
        architecture_overlay, "-compose", "Darken", "-composite", final_mask,
    )

    base = json.loads(PALETTE.read_text())["themes"]["mineral-paper"]["base"]
    light = OUT / "mineral-paper-light.png"
    dark = OUT / "mineral-paper-dark.png"
    for destination, line, background in (
        (light, base["500"]["hex"], base["paper"]["hex"]),
        (dark, base["600"]["hex"], base["black"]["hex"]),
    ):
        run(
            magick, final_mask, "+level-colors", f"{line},{background}",
            "-colorspace", "sRGB", "-define", "png:compression-level=9",
            "-strip", destination,
        )

    run(
        magick,
        "(", light, "-thumbnail", "800x450", ")",
        "(", dark, "-thumbnail", "800x450", ")",
        "+append", "-quality", "90", OUT / "contact-sheet.jpg",
    )
    shutil.rmtree(WORK)
    print(OUT)


if __name__ == "__main__":
    main()
