#!/usr/bin/env python3
"""Hue-shift every gradient stop in nectar-n.svg; geometry untouched."""
import re, sys, colorsys

def knee(hue_deg, start=50.0, slope=0.35):
    """soft-compress hues past `start` so golds never tip into green"""
    if hue_deg > start and hue_deg < 180:
        return start + (hue_deg - start) * slope
    return hue_deg

def shift(svg, deg, reds_only=False, use_knee=False):
    def repl(m):
        r, g, b = (int(m.group(i)) for i in (1, 2, 3))
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        d = deg
        if reds_only:
            # full shift for reds (hue near 0), fading to none by ~30 deg (orange)
            hue_deg = (h * 360) % 360
            dist = min(hue_deg, 360 - hue_deg)          # distance from pure red
            d = deg * max(0.0, 1 - dist / 30.0)
        hd = ((h * 360 + d) % 360)
        if use_knee:
            hd = knee(hd)
        r2, g2, b2 = colorsys.hls_to_rgb(hd / 360.0, l, s)
        return f"rgb({round(r2*255)},{round(g2*255)},{round(b2*255)})"
    return re.sub(r"rgb\((\d+),(\d+),(\d+)\)", repl, svg)

def honey_remap(svg, center=40.0, spread=0.55):
    """re-center the whole palette on amber: hue distances from red (0) compress toward `center`"""
    def repl(m):
        r, g, b = (int(m.group(i)) for i in (1, 2, 3))
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        hd = (h * 360) % 360
        signed = hd if hd <= 180 else hd - 360          # reds ~ -5..+5, oranges ~ +20..+35
        hd2 = knee(center + signed * spread)
        r2, g2, b2 = colorsys.hls_to_rgb((hd2 % 360) / 360.0, l, s)
        return f"rgb({round(r2*255)},{round(g2*255)},{round(b2*255)})"
    return re.sub(r"rgb\((\d+),(\d+),(\d+)\)", repl, svg)

src = open("nectar-n-source-red.svg").read()
for deg, reds_only, name in [
    (4, False, "hue+4"), (8, False, "hue+8"), (12, False, "hue+12"), (16, False, "hue+16"),
    (10, True, "reds+10"),
]:
    out = shift(src, deg, reds_only)
    open(f"nectar-n-{name}.svg", "w").write(out)
    print("wrote", f"nectar-n-{name}.svg")

for deg, name in [(24, "amber+24"), (32, "amber+32"), (40, "amber+40"), (48, "gold+48")]:
    out = shift(src, deg, use_knee=True)
    open(f"nectar-n-{name}.svg", "w").write(out)
    print("wrote", f"nectar-n-{name}.svg")

open("nectar-n-honey.svg", "w").write(honey_remap(src))
print("wrote nectar-n-honey.svg")

def flower_map(svg, base, expand):
    """flower-to-honey: place reds at `base` deg and stretch oranges upward toward gold"""
    def repl(m):
        r, g, b = (int(m.group(i)) for i in (1, 2, 3))
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        hd = (h * 360) % 360
        signed = hd if hd <= 180 else hd - 360
        hd2 = knee(base + signed * expand)
        r2, g2, b2 = colorsys.hls_to_rgb((hd2 % 360) / 360.0, l, s)
        return f"rgb({round(r2*255)},{round(g2*255)},{round(b2*255)})"
    return re.sub(r"rgb\((\d+),(\d+),(\d+)\)", repl, svg)

for base, expand, name in [(13, 1.25, "flower13"), (18, 1.2, "flower18"), (23, 1.1, "flower23")]:
    open(f"nectar-n-{name}.svg", "w").write(flower_map(src, base, expand))
    print("wrote", f"nectar-n-{name}.svg")

def flower_map2(svg, base, expand, sat=1.0, light=1.0, knee_start=50.0, knee_slope=0.35):
    """flower_map with saturation/lightness trim and adjustable gold cap"""
    def repl(m):
        r, g, b = (int(m.group(i)) for i in (1, 2, 3))
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        hd = (h * 360) % 360
        signed = hd if hd <= 180 else hd - 360
        hd2 = knee(base + signed * expand, knee_start, knee_slope)
        s2 = min(1.0, s * sat)
        l2 = min(1.0, max(0.0, l * light))
        r2, g2, b2 = colorsys.hls_to_rgb((hd2 % 360) / 360.0, l2, s2)
        return f"rgb({round(r2*255)},{round(g2*255)},{round(b2*255)})"
    return re.sub(r"rgb\((\d+),(\d+),(\d+)\)", repl, svg)

for name, kw in [
    ("flower20",   dict(base=20, expand=1.1)),
    ("flower22",   dict(base=22, expand=1.05)),
    ("deephoney",  dict(base=21, expand=1.1, sat=1.1, light=0.97)),
    ("restrained", dict(base=22, expand=1.05, knee_start=44, knee_slope=0.3)),
]:
    open(f"nectar-n-{name}.svg", "w").write(flower_map2(src, **kw))
    print("wrote", f"nectar-n-{name}.svg")

# canonical Nectar mark: deep honey body with the restrained gold cap
open("nectar-n.svg", "w").write(
    flower_map2(src, base=21, expand=1.1, sat=1.1, light=0.97, knee_start=44, knee_slope=0.3))
print("wrote nectar-n.svg (canonical: deep honey, restrained gold)")
