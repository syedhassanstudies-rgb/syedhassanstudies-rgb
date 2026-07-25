"""
Prepare a portrait photo for clean ASCII conversion:
  1. get a clean subject/background split -- either by reading an
     already-background-removed RGBA image (e.g. exported from remove.bg,
     removal.ai, etc.), or, for a plain photo, by face-detecting a square
     crop and running GrabCut (classical CV, works fully offline)
  2. boost LOCAL contrast (CLAHE) so flat lighting gains highlights and
     shadows -- this is what turns a dark blob into a recognizable face
  3. composite the subject onto pure white so the background reads as blank
     (white -> spaces in the ascii ramp)

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.
Run once whenever the source photo changes; the ascii SVG itself is static.

    python scripts/prep_photo.py <input.png|.jpg> [output.png]

Defaults to source-cutout.png (a pre-background-removed RGBA image) if it
exists, otherwise falls back to source-photo.jpg and does the removal itself.

NOTE: the upstream version of this script used `rembg` for the from-scratch
case. That needs a one-time model download, which wasn't possible in the
offline environment this was built in, so GrabCut stands in for it there.
Everything downstream (CLAHE, white composite, the ascii SVG itself) is
identical either way.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_CUTOUT = os.path.join(HERE, "..", "source-cutout.png")
_DEFAULT_RAW = os.path.join(HERE, "..", "source-photo.jpg")
_DEFAULT_INP = _DEFAULT_CUTOUT if os.path.exists(_DEFAULT_CUTOUT) else _DEFAULT_RAW
INP = sys.argv[1] if len(sys.argv) > 1 else _DEFAULT_INP
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

# ---- path A: input already has a real alpha channel (pre-cut elsewhere) ---
_pil_probe = Image.open(INP)
has_alpha = _pil_probe.mode in ("RGBA", "LA") and _pil_probe.getchannel("A").getextrema() != (255, 255)

if has_alpha:
    rgba = np.array(_pil_probe.convert("RGBA"))
    rgb, alpha = rgba[:, :, :3], rgba[:, :, 3]

    # pad to square (keeps 100% of the cutout -- no cropping needed) instead
    # of the crop+GrabCut path below
    ph, pw = rgb.shape[:2]
    side = max(ph, pw)
    canvas_rgb = np.full((side, side, 3), 255, np.uint8)
    canvas_a = np.zeros((side, side), np.uint8)
    oy, ox = (side - ph) // 2, (side - pw) // 2
    canvas_rgb[oy:oy + ph, ox:ox + pw] = rgb
    canvas_a[oy:oy + ph, ox:ox + pw] = alpha
    crop_bgr = cv2.cvtColor(canvas_rgb, cv2.COLOR_RGB2BGR)
    crop_bgr = cv2.resize(crop_bgr, (900, 900), interpolation=cv2.INTER_AREA)
    fg_mask = cv2.resize(canvas_a, (900, 900), interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    gray = cv2.convertScaleAbs(gray, alpha=1.05, beta=18)

    mask_f = cv2.GaussianBlur(fg_mask.astype(np.float32) / 255.0, (0, 0), 1.5)
    out = gray.astype(np.float32) * mask_f + 255.0 * (1.0 - mask_f)
    out = np.clip(out, 0, 255).astype(np.uint8)
    Image.fromarray(out, mode="L").save(OUT)
    print("wrote", OUT, out.shape, "(alpha-channel path, from", os.path.basename(INP) + ")")
    sys.exit(0)

# ---- path B: plain photo -- face-detect + GrabCut (see docstring) ---------
bgr = cv2.imread(INP)
h, w = bgr.shape[:2]

# 1. face-detect -> square crop (head + shoulders + a little torso, like a
#    standard headshot). Falls back to a centered square if detection misses.
gray_full = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
faces = cascade.detectMultiScale(gray_full, scaleFactor=1.08, minNeighbors=5, minSize=(80, 80))

if len(faces):
    # largest detected face
    fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
    cx, cy = fx + fw / 2, fy + fh / 2
    # crop side = ~4.4x face height, positions the face in the upper-middle
    # third with room for shoulders below (matches a typical bust portrait)
    side = int(fh * 4.4)
    top = int(cy - side * 0.38)
    left = int(cx - side * 0.5)
else:
    side = min(h, w)
    top = int(h * 0.06)
    left = (w - side) // 2

side = min(side, w, h)
top = max(0, min(top, h - side))
left = max(0, min(left, w - side))
crop = bgr[top:top + side, left:left + side]
crop = cv2.resize(crop, (900, 900), interpolation=cv2.INTER_AREA)

# 2. GrabCut foreground isolation. A plain rectangle seed tends to lose the
#    lower torso in bust portraits: dark clothing and shadowed green foliage
#    can look similar in the color model with no other guidance. So seed with
#    an explicit mask instead of just a rect -- a thin definite-background
#    border, a generous probable-foreground interior, and (crucially) a
#    definite-foreground "core" running from the face down to the bottom of
#    the frame, which is structurally guaranteed to be the subject in a
#    face-detected bust crop and anchors the color model correctly.
cs = crop.shape[0]  # crop is square
mask = np.full((cs, cs), cv2.GC_PR_BGD, np.uint8)
m = int(cs * 0.06)
mask[m:cs - m, m:cs - m] = cv2.GC_PR_FGD
core_x0, core_x1 = int(cs * 0.30), int(cs * 0.72)
core_y0 = int(cs * 0.22)
mask[core_y0:cs - m, core_x0:core_x1] = cv2.GC_FGD

bgd_model = np.zeros((1, 65), np.float64)
fgd_model = np.zeros((1, 65), np.float64)
cv2.grabCut(crop, mask, None, bgd_model, fgd_model, 10, cv2.GC_INIT_WITH_MASK)
fg_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
# clean up small holes/specks
fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

# 3. local-contrast the luminance (CLAHE) -- identical to upstream
gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
gray = clahe.apply(gray)
gray = cv2.convertScaleAbs(gray, alpha=1.05, beta=18)

# 4. paste onto white using the mask (feathered a hair to avoid a halo)
mask_f = (fg_mask.astype(np.float32) / 255.0)
mask_f = cv2.GaussianBlur(mask_f, (0, 0), 2.0)
out = gray.astype(np.float32) * mask_f + 255.0 * (1.0 - mask_f)
out = np.clip(out, 0, 255).astype(np.uint8)

Image.fromarray(out, mode="L").save(OUT)
print("wrote", OUT, out.shape)
