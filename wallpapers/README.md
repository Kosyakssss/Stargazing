# Stargazing wallpapers

This directory preserves the complete working project for the dark-only
Stargazing wallpapers based on Jacques-Louis David's *The Death of Socrates*.

The approved result is source-specific and dark-only. The early
Difference-of-Gaussians pipeline can process another image, but the selected
crop, focal masks, architecture masks, thresholds, and final two-color master
were tuned to this painting. It is not a general “same style from any image”
generator.

## Contents

- `source/` — preserved 6016×3384 aligned painting source and contour work.
- `experiments/` and `iterations/` — retained visual development history.
- `final/` — dark PNGs for every canonical family.
- `generate*.py` — ImageMagick 7 pipelines used during development.
- `generate-final-wallpapers.py` — recolors the approved dark two-color master
  from the current canonical palette.

All scripts resolve paths from this directory and read `../dist/stargazing.json`.
Run the canonical palette generator first, then:

```sh
python3 wallpapers/generate-final-wallpapers.py
```

The static PNG packaging remains in `stargazing-mymac`, because it is an
application port rather than canonical palette artwork.
