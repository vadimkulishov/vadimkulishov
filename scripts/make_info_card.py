from pathlib import Path
import html
import os


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "info-card.svg"

WIDTH = 490
HEIGHT = 330

BG = "#0d1117"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"

COLORS = [
    "#58a6ff",
    "#79c0ff",
    "#56d364",
    "#a5d6ff",
    "#d2a8ff",
    "#ff7b72",
]

TITLE = "vadim@github"

ROWS = [
    ("Now", "Frontend Developer"),
    ("Stack", "React · TypeScript"),
    ("", "JavaScript · CSS"),
    ("Focus", "UI/UX · Performance"),
    ("Learning", "Web3 · Design Systems"),
    ("GitHub", "github.com/vadimkulishov"),
]


def esc(value: str) -> str:
    return html.escape(value)


def create_svg():
    static = os.getenv("STATIC") == "1"

    lines = []

    lines.append(
        f'''<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
>
<style>
    .background {{
        fill: {BG};
        stroke: {BORDER};
        stroke-width: 1;
    }}

    .title {{
        fill: {MUTED};
        font-family:
            "SFMono-Regular",
            "Cascadia Code",
            "Roboto Mono",
            "Courier New",
            monospace;
        font-size: 13px;
        font-weight: 600;
    }}

    .key {{
        font-family:
            "SFMono-Regular",
            "Cascadia Code",
            "Roboto Mono",
            "Courier New",
            monospace;
        font-size: 14px;
        font-weight: 600;
    }}

    .value {{
        fill: {TEXT};
        font-family:
            "SFMono-Regular",
            "Cascadia Code",
            "Roboto Mono",
            "Courier New",
            monospace;
        font-size: 14px;
    }}

    .line {{
        opacity: 0;
        transform: translateX(-8px);
        animation: appear 0.35s ease-out forwards;
    }}

    @keyframes appear {{
        from {{
            opacity: 0;
            transform: translateX(-8px);
        }}

        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}

    @media (prefers-reduced-motion: reduce) {{
        .line {{
            animation: none;
            opacity: 1;
            transform: none;
        }}
    }}
</style>

<rect
    class="background"
    x="0.5"
    y="0.5"
    width="{WIDTH - 1}"
    height="{HEIGHT - 1}"
    rx="10"
/>

<circle cx="18" cy="18" r="5" fill="#ff5f56"/>
<circle cx="35" cy="18" r="5" fill="#ffbd2e"/>
<circle cx="52" cy="18" r="5" fill="#27c93f"/>

<text
    class="title"
    x="72"
    y="22"
>
    {esc(TITLE)}
</text>

<line
    x1="18"
    y1="43"
    x2="{WIDTH - 18}"
    y2="43"
    stroke="{BORDER}"
/>
'''
    )

    y = 76

    for index, (key, value) in enumerate(ROWS):
        delay = 0 if static else 0.55 + index * 0.12

        if key:
            key_color = COLORS[index % len(COLORS)]

            lines.append(
                f'''<g
    class="line"
    style="animation-delay:{delay:.2f}s"
>
    <text
        class="key"
        fill="{key_color}"
        x="24"
        y="{y}"
    >
        {esc(key)}
    </text>

    <text
        class="value"
        x="145"
        y="{y}"
    >
        {esc(value)}
    </text>
</g>
'''
            )
        else:
            lines.append(
                f'''<g
    class="line"
    style="animation-delay:{delay:.2f}s"
>
    <text
        class="value"
        x="145"
        y="{y}"
    >
        {esc(value)}
    </text>
</g>
'''
            )

        y += 37

    lines.append(
        f'''
<text
    class="title"
    x="24"
    y="{HEIGHT - 22}"
>
    $ whoami
</text>

</svg>
'''
    )

    OUTPUT.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(f"Done: {OUTPUT}")


if __name__ == "__main__":
    create_svg()