from pathlib import Path
import math
import html

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "source-prepped.png"
OUTPUT = ROOT / "vadim-ascii.svg"


# From light -> dark.
# More characters = darker area.
DENSITY = " .'`^\",:;Il!i~+_-?][}{1)(|\\/"
DENSITY += "tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

# Size of the ASCII portrait.
COLUMNS = 180
ROWS = 80

# Character dimensions.
CHAR_WIDTH = 7.0
CHAR_HEIGHT = 10.0

# SVG appearance.
TEXT_COLOR = "#b8b8b8"
FONT_SIZE = 10

# Animation.
ROW_DURATION = 0.45
ROW_STAGGER = 0.055


def brightness_to_char(value: int) -> str:
    """
    Convert brightness (0 = black, 255 = white)
    into an ASCII character.
    """

    # White -> first character (" ")
    # Black -> last character ("@")
    index = int((255 - value) / 255 * (len(DENSITY) - 1))

    return DENSITY[index]


def load_and_resize() -> Image.Image:
    image = Image.open(INPUT).convert("L")

    # ASCII characters are taller than they are wide,
    # so compensate for character aspect ratio.
    target_ratio = COLUMNS / ROWS

    width, height = image.size
    source_ratio = width / height

    if source_ratio > target_ratio:
        new_width = COLUMNS
        new_height = round(COLUMNS / source_ratio)
    else:
        new_height = ROWS
        new_width = round(ROWS * source_ratio)

    image = image.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS,
    )

    # Put image in a white canvas.
    canvas = Image.new(
        "L",
        (COLUMNS, ROWS),
        255,
    )

    x = (COLUMNS - new_width) // 2
    y = (ROWS - new_height) // 2

    canvas.paste(image, (x, y))

    return canvas


def build_ascii(image: Image.Image) -> list[str]:
    lines = []

    for y in range(ROWS):
        line = ""

        for x in range(COLUMNS):
            brightness = image.getpixel((x, y))
            line += brightness_to_char(brightness)

        lines.append(line.rstrip())

    return lines


def escape_text(text: str) -> str:
    return html.escape(text)


def create_svg(lines: list[str]) -> str:
    width = int(COLUMNS * CHAR_WIDTH)
    height = int(ROWS * CHAR_HEIGHT)

    parts = []

    parts.append(
        f'''<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}"
>
<style>
    .ascii {{
        font-family:
            "SFMono-Regular",
            "Cascadia Code",
            "Roboto Mono",
            "Courier New",
            monospace;

        font-size: {FONT_SIZE}px;
        font-weight: 500;
        fill: {TEXT_COLOR};
        white-space: pre;
    }}

    .row {{
        animation-name: reveal;
        animation-duration: {ROW_DURATION}s;
        animation-timing-function: ease-out;
        animation-fill-mode: both;
    }}

    @keyframes reveal {{
        from {{
            opacity: 0;
            transform: translateX(-30px);
        }}

        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}

    @media (prefers-reduced-motion: reduce) {{
        .row {{
            animation: none;
        }}
    }}
</style>
'''
    )

    for row, line in enumerate(lines):
        y = (row + 1) * CHAR_HEIGHT
        delay = row * ROW_STAGGER

        # Slightly delay every row so it looks like
        # the portrait is being printed.
        parts.append(
            f'''<text
    class="ascii row"
    x="0"
    y="{y}"
    style="animation-delay:{delay:.3f}s"
>{escape_text(line)}</text>
'''
        )

    parts.append("</svg>")

    return "\n".join(parts)


def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Input image not found: {INPUT}"
        )

    print("[1/3] Loading image...")
    image = load_and_resize()

    print("[2/3] Building ASCII...")
    lines = build_ascii(image)

    print("[3/3] Writing SVG...")
    svg = create_svg(lines)

    OUTPUT.write_text(
        svg,
        encoding="utf-8",
    )

    print()
    print(f"Done: {OUTPUT}")


if __name__ == "__main__":
    main()