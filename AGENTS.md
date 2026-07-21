# Stargazing agent rules

## Source of truth

- Edit `src/palette.json`, never generated files in `dist/`.
- Run `python3 scripts/generate.py` after source changes.
- Run `python3 scripts/validate.py` before finishing.
- Keep Flexoki 2 accent values unchanged unless the user explicitly approves a new accent system.
- Preserve the four public names: **Soft Parchment**, **Gallery Plaster**, **Mineral Paper**, and **Blue Hour**.

## Text semantics — non-negotiable

Use semantic tokens by meaning, not by font size.

- `--sg-tx` is the default for body prose, code, labels, menus, form values, settings names, and all text people are expected to read.
- `--sg-tx-2` is only for supporting content: captions, bylines, timestamps, breadcrumbs, descriptions, and subordinate metadata.
- `--sg-tx-3` is only for expendable content: placeholders, disabled labels, line numbers, and decorative annotations.
- Never use `--sg-tx-2` as the default body-text color.
- Never use `--sg-tx-3` for meaningful prose, required instructions, code, or interactive labels.
- A smaller font does not automatically make text muted or faint.
- If primary text feels too strong, do not silently replace it with muted text. Propose a dedicated reading token and validate it first.

## UI semantics

- `--sg-bg`: main background.
- `--sg-bg-2`: secondary background.
- `--sg-ui`: borders and separators.
- `--sg-ui-2`: hovered borders.
- `--sg-ui-3`: active borders.
- Light mode uses accent 600 values for text; dark mode uses accent 400 values.
- Faint text is expected to fail body-text contrast. It must remain nonessential.
- Do not judge accessibility from palette labels. Measure the actual foreground/background pair.

## Color methodology

- Stargazing preserves the exact OKLab lightness positions of Flexoki’s base steps.
- Each base family is interpolated in OKLab between its paper and ink endpoints.
- CSS and JSON expose both reproducible sRGB hex and measured OKLCH values.
- Do not interpolate the accent ramps. Their fixed values preserve Flexoki’s pigment effect.
