from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parent
PROJECT_SOURCE = ROOT / "assets" / "naiwa_reference.png"
TEMP_SOURCE = Path(r"C:\Users\15722\AppData\Local\Temp\codex-clipboard-11948d47-d24f-41bd-81df-3278e435fee3.png")
SOURCE = PROJECT_SOURCE if PROJECT_SOURCE.exists() else TEMP_SOURCE
OUTPUT = ROOT / "assets" / "naiwa.png"


def is_neutral_background(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    spread = max(rgb) - min(rgb)
    brightness = (r + g + b) / 3
    return spread <= 32 and brightness >= 105


def make_cutout() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Reference image not found: {SOURCE}")

    image = Image.open(SOURCE).convert("RGBA")
    rgb = image.convert("RGB")
    width, height = image.size
    pixels = rgb.load()
    background = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def enqueue(x: int, y: int) -> None:
        index = y * width + x
        if background[index] or not is_neutral_background(pixels[x, y]):
            return
        background[index] = 1
        queue.append((x, y))

    for x in range(width):
        enqueue(x, 0)
        enqueue(x, height - 1)
    for y in range(height):
        enqueue(0, y)
        enqueue(width - 1, y)

    while queue:
        x, y = queue.popleft()
        if x:
            enqueue(x - 1, y)
        if x + 1 < width:
            enqueue(x + 1, y)
        if y:
            enqueue(x, y - 1)
        if y + 1 < height:
            enqueue(x, y + 1)

    mask = Image.new("L", image.size, 255)
    mask_pixels = mask.load()
    for y in range(height):
        for x in range(width):
            if background[y * width + x]:
                mask_pixels[x, y] = 0

    # A one-pixel feather removes the white halo left by the source photo.
    mask = mask.filter(ImageFilter.GaussianBlur(1.1))
    # Do not leave a pale halo where the source blends into the white backdrop.
    mask_pixels = mask.load()
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if max(r, g, b) - min(r, g, b) <= 32 and (r + g + b) / 3 >= 120:
                mask_pixels[x, y] = 0
    # Tk's color-key transparency can tint semi-transparent pixels. Keep a
    # crisp alpha boundary so the desktop never shows the key color as a halo.
    mask = mask.point(lambda value: 255 if value >= 128 else 0)
    image.putalpha(mask)
    bbox = mask.getbbox()
    if bbox:
        image = image.crop(bbox)

    # Keep a generous transparent margin so the feet never clip during scaling.
    image = ImageOps.expand(image, border=(8, 8, 8, 8), fill=(0, 0, 0, 0))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, "PNG", optimize=True)
    print(f"Saved {OUTPUT} ({image.width}x{image.height})")


if __name__ == "__main__":
    make_cutout()
