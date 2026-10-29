"""Photo -> source-prepped.png (background removed, CLAHE contrast, on white). Run once per photo.

usage: python scripts/prep_photo.py source-photo.jpg [--no-rembg]
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "source-prepped.png"


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    img = Image.open(sys.argv[1]).convert("RGBA")

    if "--grabcut" in sys.argv:
        # offline fallback: OpenCV GrabCut seeded with a rect (subject roughly centered, touching the bottom)
        rgb = np.array(img.convert("RGB"))[:, :, ::-1].copy()
        h, w = rgb.shape[:2]
        top = int(h * 0.28)
        mask = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
        mask[top:, :] = cv2.GC_PR_FGD
        hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
        ycc = cv2.cvtColor(rgb, cv2.COLOR_BGR2YCrCb)
        skin = (ycc[..., 1] > 138) & (ycc[..., 1] < 180) & (ycc[..., 2] > 85) & (ycc[..., 2] < 130)
        sides = np.zeros((h, w), bool)
        sides[:, : int(w * 0.32)] = sides[:, int(w * 0.83):] = True
        grayish = (hsv[..., 1] < 45) & sides
        grayish[: top, :] = False
        mask[:top // 2, :] = cv2.GC_BGD
        mask[grayish & ~skin] = cv2.GC_BGD
        mask[cv2.erode(skin.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0] = cv2.GC_FGD
        cx, cy = w // 2, int(h * 0.48)  # face/head core
        cv2.ellipse(mask, (cx + int(w * 0.06), cy), (int(w * 0.14), int(h * 0.12)), 0, 0, 360, cv2.GC_FGD, -1)
        cv2.ellipse(mask, (cx + int(w * 0.07), int(h * 0.39)), (int(w * 0.2), int(h * 0.06)), 0, 0, 360, cv2.GC_FGD, -1)  # hair
        mask[int(h * 0.85):, int(w * 0.1):int(w * 0.9)] = cv2.GC_FGD  # sweater/shoulders
        cv2.grabCut(rgb, mask, None, np.zeros((1, 65)), np.zeros((1, 65)), 6, cv2.GC_INIT_WITH_MASK)
        fg = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
        n, lab, stats, _ = cv2.connectedComponentsWithStats(fg)
        if n > 1:  # keep only the largest blob (the person)
            fg = np.where(lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]), 255, 0).astype(np.uint8)
        img.putalpha(Image.fromarray(cv2.GaussianBlur(fg, (5, 5), 0)))
    elif "--no-rembg" not in sys.argv:
        from rembg import remove  # downloads its model (~170MB) on first run
        img = remove(img)

    # composite onto white so the background maps to spaces
    white = Image.new("RGBA", img.size, (255, 255, 255, 255))
    gray = np.array(Image.alpha_composite(white, img).convert("L"))

    # local contrast: gives flat faces real highlights/shadows
    gray = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)

    # crop to subject bounding box (+ small margin)
    ys, xs = np.where(gray < 245)
    if len(xs):
        m = int(0.04 * max(gray.shape))
        y0, y1 = max(ys.min() - m, 0), min(ys.max() + m, gray.shape[0])
        x0, x1 = max(xs.min() - m, 0), min(xs.max() + m, gray.shape[1])
        gray = gray[y0:y1, x0:x1]

    Image.fromarray(gray).save(OUT)
    print(f"wrote {OUT} {gray.shape[1]}x{gray.shape[0]}")


if __name__ == "__main__":
    main()
