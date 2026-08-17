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
# SETTINGS
# =========================================================

COLUMNS = 90

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

    return Image.open(SOURCE).convert("L")


def prepare_image(image):

    width, height = image.size

    aspect_ratio = height / width

    rows = int(
        COLUMNS
        * aspect_ratio
        * 0.50
    )

    return image.resize(
        (
            COLUMNS,
            rows
        )
    )


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
        COLUMNS * CHAR_WIDTH
        + PADDING * 2
    )

    height = (
        rows * LINE_HEIGHT
        + 100
    )

    # -----------------------------------------------------
    # ANIMATION
    #
    # Timeline:
    #
    # 0%   -> invisible
    # 30%  -> completely printed
    # 65%  -> stays visible
    # 100% -> disappears
    #
    # Every row receives a slightly different delay,
    # creating a top-to-bottom typing effect.
    # -----------------------------------------------------

    ANIMATION_DURATION = 10

    svg = []

    svg.append(
        f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}"
role="img"
aria-label="Cyberpunk ASCII portrait of Vadim Kulishov"
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


/* =====================================================
   CYBERPUNK HEADER
   ===================================================== */

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


/* =====================================================
   ASCII PRINT ANIMATION
   ===================================================== */

.row {{

    opacity: 0;

    animation:
        print-row
        {ANIMATION_DURATION}s
        ease-in-out
        infinite;

}}


@keyframes print-row {{

    /*
     * START
     */

    0% {{

        opacity: 0;

        clip-path:
            inset(
                0 100% 0 0
            );

    }}


    /*
     * PRINTED
     */

    30% {{

        opacity: 1;

        clip-path:
            inset(
                0 0 0 0
            );

    }}


    /*
     * HOLD
     */

    65% {{

        opacity: 1;

        clip-path:
            inset(
                0 0 0 0
            );

    }}


    /*
     * ERASE
     */

    100% {{

        opacity: 0;

        clip-path:
            inset(
                0 100% 0 0
            );

    }}

}}


/* =====================================================
   SCANLINE
   ===================================================== */

.scan {{

    fill: {CYAN};

    opacity: 0.06;

    animation:
        scan
        4s
        linear
        infinite;

}}


@keyframes scan {{

    from {{

        transform:
            translateY(-20px);

    }}

    to {{

        transform:
            translateY({height}px);

    }}

}}


/* =====================================================
   REDUCED MOTION
   ===================================================== */

@media (prefers-reduced-motion: reduce) {{

    .row {{

        animation: none;

        opacity: 1;

        clip-path:
            inset(
                0 0 0 0
            );

    }}

    .scan {{

        animation: none;

    }}

}}

</style>


<!-- =====================================================
     BACKGROUND
     ===================================================== -->

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


<!-- =====================================================
     HUD CORNERS
     ===================================================== -->

<path
    d="
        M1 35
        H18
        L28 25
        H70
    "
    fill="none"
    stroke="{CYAN}"
    stroke-width="1.5"
/>

<path
    d="
        M{width - 70} 25
        H{width - 28}
        L{width - 18} 35
        H{width - 1}
    "
    fill="none"
    stroke="{MAGENTA}"
    stroke-width="1.5"
/>

<path
    d="
        M1 {height - 30}
        H18
        L28 {height - 20}
        H70
    "
    fill="none"
    stroke="{MAGENTA}"
    stroke-width="1.5"
/>

<path
    d="
        M{width - 70} {height - 20}
        H{width - 28}
        L{width - 18} {height - 30}
        H{width - 1}
    "
    fill="none"
    stroke="{CYAN}"
    stroke-width="1.5"
/>


<!-- =====================================================
     HEADER
     ===================================================== -->

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


<!-- =====================================================
     SCANLINE
     ===================================================== -->

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

    total_rows = len(lines)

    for index, line in enumerate(lines):

        y = (
            start_y
            + index * LINE_HEIGHT
        )

        # Top rows start earlier.
        #
        # This creates the feeling that the portrait
        # is being typed from top to bottom.
        delay = (
            index
            * 0.035
        )

        # SVG animation-delay accepts seconds.
        # The total delay is kept inside the loop.
        #
        # The modulo makes sure every row participates
        # in every animation cycle.

        svg.append(
            f'''
<text
    class="ascii row"
    x="{PADDING}"
    y="{y}"
    style="
        animation-delay:
        {delay:.3f}s;
    "
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
    print("================================")
    print(" CYBERPUNK ASCII GENERATOR")
    print("================================")
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
        "Generating animated SVG..."
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
    print()
    print(
        f"Output: {OUTPUT}"
    )
    print()
    print(
        "Animation:"
    )
    print(
        "  PRINT -> HOLD -> ERASE -> LOOP"
    )
    print()


if __name__ == "__main__":
    main()