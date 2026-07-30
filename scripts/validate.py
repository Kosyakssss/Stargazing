#!/usr/bin/env python3
"""Validate generated Stargazing artifacts and semantic contrast invariants."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / "scripts/generate.py")], check=True, capture_output=True)
spec = json.loads((ROOT / "src/palette.json").read_text())
data = json.loads((ROOT / "dist/stargazing.json").read_text())
css = (ROOT / "dist/stargazing.css").read_text()
steps = ["paper","50","100","150","200","300","400","500","600","700","800","850","900","950","black"]
errors = []

def linear(v):
    v /= 255
    return v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4

def luminance(value):
    r,g,b = [linear(int(value[i:i+2],16)) for i in (1,3,5)]
    return .2126*r + .7152*g + .0722*b

def contrast(a,b):
    hi,lo = sorted((luminance(a),luminance(b)), reverse=True)
    return (hi+.05)/(lo+.05)

if set(data["themes"]) != set(spec["themes"]): errors.append("theme set differs from source")
if len(data["accents"]) != 8: errors.append("expected 8 accent families")
for name, shades in data["accents"].items():
    if len(shades) != 13: errors.append(f"{name}: expected 13 accent steps")
    for step, value in shades.items():
        if value["hex"] != spec["accents"][name][step]: errors.append(f"{name}-{step}: hex drift")

for slug, theme in data["themes"].items():
    source = spec["themes"][slug]
    if "semantic" in source:
        if "base" in theme: errors.append(f"{slug}: sparse semantic family must not expose a fabricated base ramp")
        expected_roles = {"bg", "bg2", "ui", "ui2", "ui3", "tx3", "tx2", "tx", "cursor", "cursorText", "selection", "selectionText"}
        for mode in ("light", "dark"):
            roles = theme["semantic"][mode]
            if set(roles) != expected_roles: errors.append(f"{slug} {mode}: wrong semantic roles")
            for key, value in roles.items():
                if value["hex"] != source["semantic"][mode][key]: errors.append(f"{slug} {mode} {key}: hex drift")
            checks = {
                "primary": (roles["tx"]["hex"], roles["bg"]["hex"], 7.0),
                "muted": (roles["tx2"]["hex"], roles["bg"]["hex"], 4.5),
                "selection": (roles["selectionText"]["hex"], roles["selection"]["hex"], 4.5),
            }
            for label, (fg, bg, minimum) in checks.items():
                ratio = contrast(fg, bg)
                if ratio < minimum: errors.append(f"{slug} {mode} {label}: {ratio:.2f} < {minimum:.1f}")
    else:
        base = theme["base"]
        if list(base) != steps: errors.append(f"{slug}: wrong base steps/order")
        if base["paper"]["hex"] != source["paper"]: errors.append(f"{slug}: paper endpoint drift")
        if base["black"]["hex"] != source["ink"]: errors.append(f"{slug}: ink endpoint drift")
        lightness = [base[k]["oklch"]["l"] for k in steps]
        if not all(a > b for a,b in zip(lightness,lightness[1:])): errors.append(f"{slug}: base lightness is not strictly descending")
        paper,ink = base["paper"]["hex"],base["black"]["hex"]
        checks = {
            "light primary": (ink,paper,7.0), "light muted": (base["600"]["hex"],paper,4.5),
            "dark primary": (base["200"]["hex"],ink,7.0), "dark muted": (base["500"]["hex"],ink,4.5),
        }
        for label,(fg,bg,minimum) in checks.items():
            ratio = contrast(fg,bg)
            if ratio < minimum: errors.append(f"{slug} {label}: {ratio:.2f} < {minimum:.1f}")
    if f'[data-stargazing="{slug}"]' not in css: errors.append(f"{slug}: missing CSS selector")

for token in ("--sg-tx", "--sg-tx-2", "--sg-tx-3", "--sg-bg", "--sg-bg-2"):
    if token not in css: errors.append(f"missing semantic token {token}")
if "-oklch:" not in css: errors.append("CSS has no OKLCH values")

if errors:
    print("Validation failed:")
    for error in errors: print(f"- {error}")
    raise SystemExit(1)
print(f"Validated {len(data['themes'])} themes, {len(data['accents'])} accent families, and semantic contrast invariants.")
