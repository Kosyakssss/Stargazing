# Color methodology

## Base ramps

Flexoki’s base colors blend a warm paper and ink into a shared neutral ramp. Stargazing retains the same 15 named steps:

`paper, 50, 100, 150, 200, 300, 400, 500, 600, 700, 800, 850, 900, 950, black`

Rather than treating the numeric labels as linear percentages, the generator measures the OKLab lightness of every original Flexoki base value. It normalizes those measurements between Flexoki paper and black, then uses the resulting positions to interpolate each Stargazing paper/ink pair in OKLab.

This preserves the original ramp’s perceptual rhythm while allowing hue temperature to move smoothly from paper to ink. Generated values are converted to sRGB and rounded to exact six-digit hex. Their measured OKLCH coordinates are emitted alongside them.

## Accent ramps

Stargazing includes all eight Flexoki 2 accent families and all thirteen published steps from 50 to 950. Their hex values remain fixed. Flexoki’s accents intentionally do not behave like opacity-derived colors; changing them would alter their pigment-like character.

## Accuracy and gamut

- Canonical endpoints and accents retain exact sRGB hex values.
- Base interpolation uses full-precision floating-point OKLab math.
- Generated hex values are deterministic.
- Emitted OKLCH values describe the generated sRGB colors and are rounded to six decimal places for lightness/chroma and three decimals for hue.
- Validation regenerates artifacts and checks endpoint identity, step order, required semantic mappings, accent fidelity, and contrast.
