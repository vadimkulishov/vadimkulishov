from pathlib import Path
import html
import os


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "info-card.svg"

WIDTH = 490
HEIGHT = 430

BG = "#0b0d12"
YELLOW = "#fcee0a"
CYAN = "#00f0ff"
MAGENTA = "#ff2a6d"

TEXT = "#e8e8e8"
MUTED = "#777b85"
GRID = "#24262d"


def esc(value):
    return html.escape(str(value))


def main():

    static = os.getenv("STATIC") == "1"

    svg = f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}"
>

<style>

* {{
    font-family:
        "SFMono-Regular",
        "Cascadia Code",
        "Roboto Mono",
        "Courier New",
        monospace;
}}

.panel {{
    fill: {BG};
    stroke: {YELLOW};
    stroke-width: 1.5;
}}

.title {{
    fill: {YELLOW};
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 2px;
}}

.label {{
    fill: {CYAN};
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
}}

.value {{
    fill: {TEXT};
    font-size: 15px;
    font-weight: bold;
}}

.muted {{
    fill: {MUTED};
    font-size: 10px;
}}

.line {{
    stroke: {GRID};
    stroke-width: 1;
}}

.data {{
    opacity: 0;
    animation: boot 0.4s ease-out forwards;
}}

@keyframes boot {{
    from {{
        opacity: 0;
        transform: translateX(15px);
    }}

    to {{
        opacity: 1;
        transform: translateX(0);
    }}
}}

.scan {{
    fill: {CYAN};
    opacity: 0.08;
    animation: scan 3s linear infinite;
}}

@keyframes scan {{
    from {{
        transform: translateY(-420px);
    }}

    to {{
        transform: translateY(420px);
    }}
}}

</style>

<rect
    class="panel"
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
/>

<!-- corner decorations -->

<path
    d="M1 35 H18 V18"
    fill="none"
    stroke="{CYAN}"
    stroke-width="2"
/>

<path
    d="M489 35 H472 V18"
    fill="none"
    stroke="{MAGENTA}"
    stroke-width="2"
/>

<path
    d="M1 395 H18 V412"
    fill="none"
    stroke="{MAGENTA}"
    stroke-width="2"
/>

<path
    d="M489 395 H472 V412"
    fill="none"
    stroke="{CYAN}"
    stroke-width="2"
/>

<!-- scanline -->

<rect
    class="scan"
    x="0"
    y="0"
    width="{WIDTH}"
    height="3"
/>

<!-- header -->

<text
    class="title"
    x="25"
    y="29"
>
    // IDENTITY_MODULE
</text>

<text
    class="muted"
    x="365"
    y="29"
>
    v2.077
</text>

<line
    class="line"
    x1="20"
    y1="45"
    x2="470"
    y2="45"
/>

<!-- identity -->

<g
    class="data"
    style="animation-delay:0.2s"
>

<text
    class="label"
    x="25"
    y="78"
>
    USER
</text>

<text
    class="value"
    x="25"
    y="101"
>
    VADIM KULISHOV
</text>

<text
    class="muted"
    x="25"
    y="120"
>
    @vadimkulishov
</text>

</g>

<!-- role -->

<g
    class="data"
    style="animation-delay:0.35s"
>

<text
    class="label"
    x="25"
    y="157"
>
    ROLE
</text>

<text
    class="value"
    x="25"
    y="180"
>
    FRONTEND DEVELOPER
</text>

</g>

<!-- stack -->

<g
    class="data"
    style="animation-delay:0.5s"
>

<text
    class="label"
    x="25"
    y="218"
>
    STACK
</text>

<text
    class="value"
    x="25"
    y="243"
>
    REACT / TYPESCRIPT / JAVASCRIPT
</text>

<text
    class="value"
    x="25"
    y="267"
>
    HTML / CSS
</text>

</g>

<!-- status -->

<g
    class="data"
    style="animation-delay:0.65s"
>

<text
    class="label"
    x="25"
    y="307"
>
    SYSTEM STATUS
</text>

<circle
    cx="29"
    cy="330"
    r="5"
    fill="{YELLOW}"
/>

<text
    class="value"
    x="45"
    y="335"
>
    ONLINE
</text>

<text
    class="muted"
    x="25"
    y="360"
>
    CONNECTION: SECURE
</text>

</g>

<!-- footer -->

<line
    class="line"
    x1="20"
    y1="385"
    x2="470"
    y2="385"
/>

<text
    class="muted"
    x="25"
    y="407"
>
    NIGHT CITY // LOCAL NODE
</text>

<text
    class="muted"
    x="360"
    y="407"
>
    2077
</text>

</svg>
'''

    OUTPUT.write_text(
        svg,
        encoding="utf-8",
    )

    print(f"Generated: {OUTPUT}")


if __name__ == "__main__":
    main()