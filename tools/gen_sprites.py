"""
Generate Swarmbreaker's creature sprites.

The originals were ~20px flat placeholder blobs. These are drawn at 8x
supersample with shading, outlines and highlights, then downsampled to the
exact original dimensions so the game's load-time scale factors (and therefore
gameplay hitboxes) are unchanged. Deterministic, no external assets - safe to
re-run.

Run from the repo root:  python tools/gen_sprites.py
"""

from __future__ import annotations

import os
from PIL import Image, ImageDraw

SS = 8  # supersample factor

# (name, width, height) at final on-disk size - must match the originals.
TARGETS = {
    "player": (20, 20),
    "mushroom": (20, 20),
    "centipede_head": (20, 20),
    "centipede_body": (20, 20),
    "flea": (14, 18),
    "scorpion": (28, 16),
    "spider": (28, 18),
}

OUT_DIR = os.path.join("assets", "images")


def canvas(w: int, h: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def finish(img: Image.Image, w: int, h: int, path: str) -> None:
    small = img.resize((w, h), Image.LANCZOS)
    small.save(path)


def E(d, box, **kw):
    d.ellipse(box, **kw)


def draw_player(w, h):
    img, d = canvas(w, h)
    W, H = w * SS, h * SS
    cx = W / 2
    hull = (58, 226, 173, 255)
    hull_d = (26, 150, 120, 255)
    glow = (150, 255, 224, 255)
    edge = (10, 40, 34, 255)
    # thruster glow
    E(d, [cx - W * 0.16, H * 0.78, cx + W * 0.16, H * 1.02], fill=(120, 240, 255, 120))
    # hull: arrow / gunship pointing up
    body = [(cx, H * 0.06), (W * 0.86, H * 0.72), (cx, H * 0.60), (W * 0.14, H * 0.72)]
    d.polygon(body, fill=hull, outline=edge)
    # side pods
    E(d, [W * 0.04, H * 0.52, W * 0.30, H * 0.86], fill=hull_d, outline=edge)
    E(d, [W * 0.70, H * 0.52, W * 0.96, H * 0.86], fill=hull_d, outline=edge)
    # cockpit
    E(d, [cx - W * 0.14, H * 0.26, cx + W * 0.14, H * 0.56], fill=(18, 60, 80, 255), outline=edge)
    E(d, [cx - W * 0.08, H * 0.30, cx + W * 0.05, H * 0.44], fill=glow)
    # nose highlight
    d.line([(cx, H * 0.10), (cx, H * 0.34)], fill=glow, width=max(1, SS))
    return finish(img, w, h, os.path.join(OUT_DIR, "player.png")) or img


def draw_mushroom(w, h):
    img, d = canvas(w, h)
    W, H = w * SS, h * SS
    cap = (232, 74, 95, 255)
    cap_d = (176, 40, 66, 255)
    stem = (244, 226, 194, 255)
    stem_d = (196, 170, 132, 255)
    edge = (60, 18, 26, 255)
    # stem
    d.rounded_rectangle([W * 0.34, H * 0.52, W * 0.66, H * 0.92], radius=W * 0.10,
                        fill=stem, outline=edge)
    d.rectangle([W * 0.52, H * 0.54, W * 0.66, H * 0.90], fill=stem_d)
    # cap
    d.pieslice([W * 0.10, H * 0.10, W * 0.90, H * 0.86], 180, 360, fill=cap, outline=edge)
    d.pieslice([W * 0.50, H * 0.10, W * 0.90, H * 0.86], 180, 360, fill=cap_d)
    # spots
    for sx, sy, r in [(0.32, 0.34, 0.07), (0.56, 0.28, 0.06), (0.70, 0.42, 0.05), (0.44, 0.46, 0.05)]:
        E(d, [W * (sx - r), H * (sy - r), W * (sx + r), H * (sy + r)], fill=stem)
    return finish(img, w, h, os.path.join(OUT_DIR, "mushroom.png")) or img


def _segment(w, h, head: bool):
    img, d = canvas(w, h)
    W, H = w * SS, h * SS
    body = (150, 214, 74, 255) if not head else (196, 236, 92, 255)
    body_d = (96, 158, 42, 255)
    edge = (28, 54, 12, 255)
    leg = (60, 96, 30, 255)
    cy = H * 0.52
    # legs
    for lx in (0.30, 0.50, 0.70):
        d.line([(W * lx, cy), (W * (lx - 0.12), H * 0.94)], fill=leg, width=max(1, int(SS * 0.9)))
        d.line([(W * lx, cy), (W * (lx - 0.12), H * 0.06)], fill=leg, width=max(1, int(SS * 0.9)))
    # shell
    E(d, [W * 0.10, H * 0.16, W * 0.90, H * 0.88], fill=body, outline=edge)
    E(d, [W * 0.52, H * 0.24, W * 0.86, H * 0.80], fill=body_d)
    E(d, [W * 0.20, H * 0.26, W * 0.44, H * 0.5], fill=(220, 245, 160, 200))
    if head:
        # eyes + mandibles
        E(d, [W * 0.16, H * 0.30, W * 0.30, H * 0.46], fill=(250, 250, 250, 255), outline=edge)
        E(d, [W * 0.18, H * 0.42, W * 0.26, H * 0.52], fill=(20, 20, 20, 255))
        E(d, [W * 0.16, H * 0.56, W * 0.30, H * 0.72], fill=(250, 250, 250, 255), outline=edge)
        E(d, [W * 0.18, H * 0.60, W * 0.26, H * 0.70], fill=(20, 20, 20, 255))
        d.line([(W * 0.10, H * 0.34), (W * -0.02, H * 0.22)], fill=edge, width=max(1, SS))
        d.line([(W * 0.10, H * 0.68), (W * -0.02, H * 0.80)], fill=edge, width=max(1, SS))
    name = "centipede_head" if head else "centipede_body"
    return finish(img, w, h, os.path.join(OUT_DIR, name + ".png")) or img


def draw_flea(w, h):
    img, d = canvas(w, h)
    W, H = w * SS, h * SS
    body = (120, 196, 236, 255)
    body_d = (58, 130, 180, 255)
    edge = (16, 40, 60, 255)
    # legs (springy)
    for ly in (0.5, 0.66, 0.82):
        d.line([(W * 0.5, H * ly), (W * 0.05, H * (ly + 0.14))], fill=(40, 80, 110, 255), width=max(1, SS))
        d.line([(W * 0.5, H * ly), (W * 0.95, H * (ly + 0.14))], fill=(40, 80, 110, 255), width=max(1, SS))
    E(d, [W * 0.22, H * 0.06, W * 0.78, H * 0.74], fill=body, outline=edge)
    E(d, [W * 0.44, H * 0.16, W * 0.72, H * 0.62], fill=body_d)
    E(d, [W * 0.30, H * 0.14, W * 0.48, H * 0.34], fill=(220, 245, 255, 220))
    E(d, [W * 0.40, H * 0.02, W * 0.60, H * 0.22], fill=body, outline=edge)  # head
    return finish(img, w, h, os.path.join(OUT_DIR, "flea.png")) or img


def draw_scorpion(w, h):
    img, d = canvas(w, h)
    W, H = w * SS, h * SS
    body = (236, 176, 74, 255)
    body_d = (188, 120, 40, 255)
    edge = (70, 40, 12, 255)
    cy = H * 0.52
    # legs
    for lx in (0.34, 0.48, 0.62):
        d.line([(W * lx, cy), (W * (lx - 0.06), H * 0.96)], fill=body_d, width=max(1, SS))
        d.line([(W * lx, cy), (W * (lx - 0.06), H * 0.08)], fill=body_d, width=max(1, SS))
    # segmented body
    for i, sx in enumerate((0.30, 0.44, 0.58)):
        E(d, [W * (sx - 0.11), cy - H * 0.20, W * (sx + 0.11), cy + H * 0.20],
          fill=body if i % 2 == 0 else body_d, outline=edge)
    # claws (front, left)
    E(d, [W * 0.06, cy - H * 0.24, W * 0.24, cy - H * 0.02], fill=body, outline=edge)
    E(d, [W * 0.06, cy + H * 0.02, W * 0.24, cy + H * 0.24], fill=body, outline=edge)
    # tail curling up-right
    pts = [(0.66, 0.52), (0.80, 0.40), (0.90, 0.22), (0.84, 0.08)]
    for i in range(len(pts) - 1):
        d.line([(W * pts[i][0], H * pts[i][1]), (W * pts[i + 1][0], H * pts[i + 1][1])],
               fill=body_d, width=max(1, int(SS * 2)))
    E(d, [W * 0.78, H * 0.00, W * 0.94, H * 0.16], fill=(232, 74, 95, 255), outline=edge)  # stinger
    return finish(img, w, h, os.path.join(OUT_DIR, "scorpion.png")) or img


def draw_spider(w, h):
    img, d = canvas(w, h)
    W, H = w * SS, h * SS
    body = (176, 108, 214, 255)
    body_d = (120, 60, 168, 255)
    edge = (44, 18, 64, 255)
    cx, cy = W * 0.5, H * 0.5
    # 8 legs
    for i, ly in enumerate((0.26, 0.44, 0.60, 0.78)):
        for sign in (-1, 1):
            ex = cx + sign * W * 0.5
            mx = cx + sign * W * 0.30
            d.line([(cx, cy), (mx, H * ly)], fill=body_d, width=max(1, SS))
            d.line([(mx, H * ly), (ex, H * (ly + (0.08 if i < 2 else -0.08)))],
                   fill=(60, 30, 90, 255), width=max(1, SS))
    # abdomen + head
    E(d, [W * 0.34, H * 0.20, W * 0.66, H * 0.80], fill=body, outline=edge)
    E(d, [W * 0.40, H * 0.30, W * 0.60, H * 0.66], fill=body_d)
    E(d, [W * 0.42, H * 0.06, W * 0.58, H * 0.30], fill=body, outline=edge)
    # eyes
    E(d, [W * 0.45, H * 0.12, W * 0.50, H * 0.18], fill=(250, 240, 120, 255))
    E(d, [W * 0.52, H * 0.12, W * 0.57, H * 0.18], fill=(250, 240, 120, 255))
    return finish(img, w, h, os.path.join(OUT_DIR, "spider.png")) or img


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    draw_player(*TARGETS["player"])
    draw_mushroom(*TARGETS["mushroom"])
    _segment(*TARGETS["centipede_head"], head=True)
    _segment(*TARGETS["centipede_body"], head=False)
    draw_flea(*TARGETS["flea"])
    draw_scorpion(*TARGETS["scorpion"])
    draw_spider(*TARGETS["spider"])
    for name, (w, h) in TARGETS.items():
        p = os.path.join(OUT_DIR, name + ".png")
        print(f"{name}: {Image.open(p).size}  {os.path.getsize(p)} bytes")


if __name__ == "__main__":
    main()
