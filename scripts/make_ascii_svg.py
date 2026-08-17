from pathlib import Path
from PIL import Image
import html


# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

SOURCE = ROOT / "source-prepped.png"
OUTPUT = ROOT / "vadim-ascii.svg"


# =========================================================
# PORTRAIT SETTINGS
# =========================================================

COLUMNS = 72
FONT_SIZE = 7.5

CHAR_WIDTH = 4.5
LINE_HEIGHT = 9

PADDING = 24

# Bright -> dark
CHARS = " .:-=+*#%@"

# =========================================================
# CYBERPUNK COLORS
# =========================================================

BACKGROUND = "#050509"

YELLOW = "#fcee0a"
CYAN = "#00f0ff"
MAGENTA = "#ff2a6d"

ASCII_COLOR = "#d7d7d7"
MUTED = "#777b85"


# =========================================================
# HELPERS
# =========================================================

def esc(value):
    return html.escape(str(value))


def brightness_to_char(brightness):
    """
    Convert grayscale brightness 0..255
    into ASCII character.
    """

    index = int(
        brightness / 255 * (len(CHARS) - 1)
    )

    return CHARS[index]


def load_image():

    if not SOURCE.exists():

        raise FileNotFoundError(
            f"""
Source image not found:

{SOURCE}

Make sure source-prepped.png exists.
"""
        )

    image = Image.open(
        SOURCE
    ).convert("L")

    return image


def prepare_image(image):

    width, height = image.size

    aspect_ratio = height / width

    rows = int(
        COLUMNS
        * aspect_ratio
        * 0.50
    )

    image = image.resize(
        (
            COLUMNS,
            rows
        )
    )

    return image


# =========================================================
# ASCII GENERATION
# =========================================================

def create_ascii(image):

    pixels = image.load()

    width, height = image.size

    lines = []

    for y in range(height):

        line = []

        for x in range(width):

            brightness = pixels[x, y]

            char = brightness_to_char(
                brightness
            )

            line.append(char)

        lines.append(
            "".join(line)
        )

    return lines


# =========================================================
# SVG
# =========================================================

def create_svg(lines):

    rows = len(lines)

    width = (
        COLUMNS
        * CHAR_WIDTH
        + PADDING * 2
    )

    height = (
        rows
        * LINE_HEIGHT
        + 100
    )

    svg = []

    # =====================================================
    # SVG HEADER
    # =====================================================

    svg.append(
        f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}"
role="img"
aria-label="Cyberpunk ASCII portrait"
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

    fill: {ASCII_COLOR};

    dominant-baseline: middle;

    letter-spacing: 0px;
}}

.header {{
    fill: {YELLOW};

    font-family:
        "SFMono-Regular",
        "Cascadia Code",
        "Roboto Mono",
        "Courier New",
        monospace;

    font-size: 11px;

    font-weight: bold;

    letter-spacing: 2px;
}}

.meta {{
    fill: {MUTED};

    font-family:
        "SFMono-Regular",
        "Cascadia Code",
        "Roboto Mono",
        "Courier New",
        monospace;

    font-size: 8px;

    letter-spacing: 1px;
}}

.scan {{
    fill: {CYAN};

    opacity: 0.08;

    animation:
        scan 3s linear infinite;
}}

@keyframes scan {{

    from {{
        transform:
            translateY(-100px);
    }}

    to {{
        transform:
            translateY({height}px);
    }}

}}

.row {{
    opacity: 0;

    animation:
        print-row
        0.25s
        ease-out
        forwards;
}}

@keyframes print-row {{

    from {{
        opacity: 0;

        clip-path:
            inset(
                0
                100%
                0
                0
            );
    }}

    to {{
        opacity: 1;

        clip-path:
            inset(
                0
                0
                0
                0
            );
    }}

}}

.corner {{
    fill: none;

    stroke-width: 1.5;
}}

@media (prefers-reduced-motion: reduce) {{

    .row {{
        animation: none;

        opacity: 1;
    }}

    .scan {{
        animation: none;
    }}

}}

</style>

<!-- BACKGROUND -->

<rect
    x="1"
    y="1"
    width="{width - 2}"
    height="{height - 2}"
    rx="4"
    fill="{BACKGROUND}"
    stroke="{YELLOW}"
    stroke-width="1.5"
/>

<!-- ================================================= -->
<!-- HUD CORNERS -->
<!-- ================================================= -->

<path
    class="corner"
    stroke="{CYAN}"
    d="
        M1 35
        H18
        L28 25
        H70
    "
/>

<path
    class="corner"
    stroke="{MAGENTA}"
    d="
        M{width - 70} 25
        H{width - 28}
        L{width - 18} 35
        H{width - 1}
    "
/>

<path
    class="corner"
    stroke="{MAGENTA}"
    d="
        M1 {height - 30}
        H18
        L28 {height - 20}
        H70
    "
/>

<path
    class="corner"
    stroke="{CYAN}"
    d="
        M{width - 70} {height - 20}
        H{width - 28}
        L{width - 18} {height - 30}
        H{width - 1}
    "
/>

<!-- ================================================= -->
<!-- HEADER -->
<!-- ================================================= -->

<text
    class="header"
    x="{PADDING}"
    y="23"
>
    // VISUAL_ID
</text>

<text
    class="meta"
    x="{width - 170}"
    y="23"
>
    SUBJECT: VADIM
</text>

<line
    x1="{PADDING}"
    y1="38"
    x2="{width - PADDING}"
    y2="38"
    stroke="#24262d"
    stroke-width="1"
/>

<!-- ================================================= -->
<!-- SCANLINE -->
<!-- ================================================= -->

<rect
    class="scan"
    x="0"
    y="0"
    width="{width}"
    height="2"
/>

'''
    )

    # =====================================================
    # ASCII ROWS
    # =====================================================

    start_y = 52

    for index, line in enumerate(lines):

        y = (
            start_y
            + index * LINE_HEIGHT
        )

        delay = (
            index * 0.035
        )

        svg.append(
            f'''
<text
    class="ascii row"
    x="{PADDING}"
    y="{y}"
    style="animation-delay:{delay:.3f}s"
>
    {esc(line)}
</text>
'''
        )

    # =====================================================
    # FOOTER
    # =====================================================

    footer_y = (
        start_y
        + rows * LINE_HEIGHT
        + 20
    )

    svg.append(
        f'''
<line
    x1="{PADDING}"
    y1="{footer_y - 18}"
    x2="{width - PADDING}"
    y2="{footer_y - 18}"
    stroke="#24262d"
    stroke-width="1"
/>

<text
    class="meta"
    x="{PADDING}"
    y="{footer_y}"
>
    SCAN COMPLETE
</text>

<text
    class="meta"
    x="{width - 150}"
    y="{footer_y}"
>
    NODE: NIGHT CITY
</text>

</svg>
'''
    )

    return "\n".join(svg)


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("Loading portrait...")

    image = load_image()

    print(
        f"Original size: "
        f"{image.width}x{image.height}"
    )

    image = prepare_image(
        image
    )

    print(
        f"ASCII grid: "
        f"{image.width}x{image.height}"
    )

    lines = create_ascii(
        image
    )

    print(
        f"Generating SVG..."
    )

    svg = create_svg(
        lines
    )

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print("================================")
    print(" CYBERPUNK ASCII GENERATED")
    print("================================")
    print(
        f"Output: {OUTPUT}"
    )
    print()


if __name__ == "__main__":
    main()