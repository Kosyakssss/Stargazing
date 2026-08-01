#!/usr/bin/env python3
"""Generate Mineral Paper engraving experiments for The Death of Socrates."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "aligned-source.png"
PALETTE = ROOT.parent / "dist" / "stargazing.json"
WORK = ROOT / ".experiments-work"
WIDTH, HEIGHT = 6016, 3384


def run(*args: object) -> None:
    subprocess.run([str(arg) for arg in args], check=True)


def colorize(magick: str, mask: Path, destination: Path, line: str, background: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    run(
        magick, mask,
        "+level-colors", f"{line},{background}",
        "-colorspace", "sRGB",
        "-define", "png:compression-level=9",
        "-strip", destination,
    )


def contact_sheet(magick: str, image: Path, destination: Path) -> None:
    run(magick, image, "-thumbnail", "800x450", "-quality", "90", destination)


def main() -> None:
    magick = shutil.which("magick")
    if not magick:
        raise SystemExit("ImageMagick 7 is required.")

    palette = json.loads(PALETTE.read_text())
    base = palette["themes"]["mineral-paper"]["base"]
    dark_colors = (base["600"]["hex"], base["black"]["hex"])

    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    base_image = WORK / "base.png"
    crop_image = WORK / "crop.png"

    run(
        magick, SOURCE, "-auto-orient", "-filter", "Lanczos",
        "-resize", f"{WIDTH}x{HEIGHT}^", "-gravity", "center",
        "-extent", f"{WIDTH}x{HEIGHT}", "-colorspace", "Gray",
        "-strip", base_image,
    )
    run(
        magick, SOURCE, "-auto-orient", "-filter", "Lanczos",
        "-resize", f"{round(WIDTH * 1.42)}x{round(HEIGHT * 1.42)}^",
        "-gravity", "center", "-extent", f"{WIDTH}x{HEIGHT}",
        "-colorspace", "Gray", "-strip", crop_image,
    )

    def edges(source: Path, destination: Path, threshold: str = "77.5%", organic: bool = False) -> None:
        command: list[object] = [
            magick, source, "-morphology", "Convolve", "DoG:0,0,2",
            "-negate", "-normalize",
        ]
        if organic:
            command += ["-attenuate", "0.10", "+noise", "Multiplicative"]
        command += ["-threshold", threshold, "-morphology", "Dilate", "Diamond:1", destination]
        run(*command)

    standard_edges = WORK / "standard-edges.png"
    crop_edges = WORK / "crop-edges.png"
    organic_edges = WORK / "organic-edges.png"
    combined_edges = WORK / "combined-edges.png"
    edges(base_image, standard_edges)
    edges(crop_image, crop_edges)
    edges(base_image, organic_edges, "77.8%", organic=True)
    edges(crop_image, combined_edges, "77.8%", organic=True)

    # Sparse binary shadow marks restore broad engraved masses without copying
    # the painting's smooth tonal gradients.
    tonal_marks = WORK / "tonal-marks.png"
    crop_tonal_marks = WORK / "crop-tonal-marks.png"
    for source, destination in ((base_image, tonal_marks), (crop_image, crop_tonal_marks)):
        run(
            magick, source,
            "-contrast-stretch", "4%x2%",
            "-ordered-dither", "o8x8,2",
            "-threshold", "31%",
            "-morphology", "Dilate", "Diamond:1",
            destination,
        )

    tonal = WORK / "tonal.png"
    run(magick, standard_edges, tonal_marks, "-compose", "Darken", "-composite", tonal)

    # Fade architecture and peripheral figures while preserving the central
    # gesture. A blurred ellipse creates continuous line hierarchy.
    focus_mask = WORK / "focus-mask.png"
    run(
        magick, "-size", f"{WIDTH}x{HEIGHT}", "xc:black",
        "-fill", "white", "-draw", "ellipse 3730,1810 2450,1450 0,360",
        "-blur", "0x520", focus_mask,
    )
    focal = WORK / "focal.png"
    run(
        magick, "-size", f"{WIDTH}x{HEIGHT}", "xc:white",
        standard_edges, focus_mask,
        "-compose", "Over", "-composite", focal,
    )

    # Noise before threshold breaks and varies marks without erasing detail.
    organic = organic_edges

    combined_mass = WORK / "combined-mass.png"
    run(magick, combined_edges, crop_tonal_marks, "-compose", "Darken", "-composite", combined_mass)
    combined = WORK / "combined.png"
    run(
        magick, "-size", f"{WIDTH}x{HEIGHT}", "xc:white",
        combined_mass, focus_mask,
        "-compose", "Over", "-composite", combined,
    )

    experiments = {
        "01-tonal-mass": tonal,
        "02-focal-hierarchy": focal,
        "03-assertive-crop": crop_edges,
        "04-organic-lines": organic,
        "05-combined": combined,
    }

    comparison_rows: list[Path] = []
    for index, (name, mask) in enumerate(experiments.items(), start=1):
        directory = ROOT / "experiments" / name
        dark = directory / "mineral-paper-dark.png"
        colorize(magick, mask, dark, *dark_colors)
        contact_sheet(magick, dark, directory / "contact-sheet.jpg")
        row = WORK / f"comparison-{index}.png"
        contact_sheet(magick, dark, row)
        comparison_rows.append(row)
        print(directory)

    run(magick, *comparison_rows, "-append", "-quality", "90", ROOT / "experiments" / "comparison-contact-sheet.jpg")
    shutil.rmtree(WORK)


if __name__ == "__main__":
    main()
