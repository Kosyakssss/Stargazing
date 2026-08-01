#!/usr/bin/env python3
"""Strengthen focal contours over the exact assertive-crop baseline."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "aligned-source.png"
PALETTE = ROOT.parent / "dist" / "stargazing.json"
OUT = ROOT / "experiments" / "08-assertive-focal-contours"
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

    # A clean Canny pass creates connected focal contours without exposing the
    # dense micro-texture found in the raw DoG response.
    run(magick, crop, "-canny", "0x4+12%+32%", "-negate", focal_detail)
    # Architecture retains iteration 07's deliberately tiny increase.
    run(magick, dog, "-threshold", "77.8%", "-morphology", "Dilate", "Diamond:1", architecture_detail)

    focal_mask = WORK / "focal-mask.png"
    architecture_mask = WORK / "architecture-mask.png"
    run(
        magick, "-size", f"{WIDTH}x{HEIGHT}", "xc:black", "-fill", "white",
        # Socrates: head, torso, robes, and the arm extending toward the cup.
        "-draw", "ellipse 4100,1655 940,1335 0,360",
        # Cup exchange: cup, both hands, wrists, and cup-bearer's forearm.
        "-draw", "ellipse 3065,1465 1070,510 0,360",
        # Socrates' raised forearm and pointing hand.
        "-draw", "ellipse 4435,585 360,600 0,360",
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
    dark = OUT / "mineral-paper-dark.png"
    run(
        magick, final_mask,
        "+level-colors", f"{base['600']['hex']},{base['black']['hex']}",
        "-colorspace", "sRGB", "-define", "png:compression-level=9",
        "-strip", dark,
    )
    run(magick, dark, "-thumbnail", "800x450", "-quality", "90", OUT / "contact-sheet.jpg")
    shutil.rmtree(WORK)
    print(OUT)


if __name__ == "__main__":
    main()
