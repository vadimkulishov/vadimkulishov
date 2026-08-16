from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "assets" / "photo.jpg"
OUTPUT = ROOT / "source-prepped.png"


def remove_background(input_path: Path):
    print("[1/4] Removing background...")

    image = Image.open(input_path).convert("RGBA")
    result = remove(image)

    return result


def crop_subject(image: Image.Image):
    print("[2/4] Cropping subject...")

    rgba = np.array(image)

    alpha = rgba[:, :, 3]

    # Find pixels belonging to the person.
    ys, xs = np.where(alpha > 30)

    if len(xs) == 0:
        raise RuntimeError("Could not detect subject.")

    left = xs.min()
    right = xs.max()
    top = ys.min()
    bottom = ys.max()

    width = right - left
    height = bottom - top

    # We want the portrait to focus on the head and upper body.
    #
    # Your original photo is full-body, so instead of keeping
    # the entire person we crop around the upper ~65%.
    bottom = top + int(height * 0.68)

    # Add some padding around the subject.
    padding_x = int(width * 0.12)
    padding_top = int(height * 0.05)
    padding_bottom = int(height * 0.05)

    left = max(0, left - padding_x)
    right = min(rgba.shape[1], right + padding_x)

    top = max(0, top - padding_top)
    bottom = min(rgba.shape[0], bottom + padding_bottom)

    cropped = image.crop(
        (left, top, right, bottom)
    )

    return cropped


def improve_contrast(image: Image.Image):
    print("[3/4] Improving contrast...")

    rgba = np.array(image)

    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    gray = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2GRAY
    )

    # Local contrast.
    clahe = cv2.createCLAHE(
        clipLimit=3.0,
        tileGridSize=(8, 8),
    )

    gray = clahe.apply(gray)

    # Slight sharpening.
    blurred = cv2.GaussianBlur(
        gray,
        (0, 0),
        1.2,
    )

    sharpened = cv2.addWeighted(
        gray,
        1.35,
        blurred,
        -0.35,
        0,
    )

    result = cv2.cvtColor(
        sharpened,
        cv2.COLOR_GRAY2RGBA,
    )

    result[:, :, 3] = alpha

    return Image.fromarray(result)


def composite_on_white(image: Image.Image):
    print("[4/4] Compositing on white...")

    rgba = image.convert("RGBA")

    background = Image.new(
        "RGBA",
        rgba.size,
        (255, 255, 255, 255),
    )

    result = Image.alpha_composite(
        background,
        rgba,
    )

    return result.convert("L")


def main():
    if not INPUT.exists():
        print(f"ERROR: file not found: {INPUT}")
        sys.exit(1)

    image = remove_background(INPUT)

    image = crop_subject(image)

    image = improve_contrast(image)

    image = composite_on_white(image)

    image.save(
        OUTPUT,
        format="PNG",
        optimize=True,
    )

    print()
    print(f"Done: {OUTPUT}")


if __name__ == "__main__":
    main()