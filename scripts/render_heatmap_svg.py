from pathlib import Path
from datetime import date, timedelta
import json
import html


# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "contrib-heatmap.svg"


# =========================================================
# CANVAS
# =========================================================

WIDTH = 920
HEIGHT = 205

WEEKS = 53
DAYS = 7

CELL = 12
GAP = 4
STEP = CELL + GAP

LEFT = 28
TOP = 55


# =========================================================
# CYBERPUNK 2077 / NIGHT CITY PALETTE
# =========================================================

BACKGROUND = "#050509"
PANEL = "#0b0d12"

YELLOW = "#fcee0a"
CYAN = "#00f0ff"
MAGENTA = "#ff2a6d"

TEXT = "#e8e8e8"
MUTED = "#777b85"
GRID = "#24262d"

LEVEL_COLORS = {
    0: "#111318",
    1: "#17343a",
    2: "#006b73",
    3: "#00c9d7",
    4: "#fcee0a",
}


# =========================================================
# HELPERS
# =========================================================

def esc(value):
    """Safely escape text for SVG."""
    return html.escape(str(value))


def format_number(number):
    """Format numbers with thousands separators."""
    return f"{number:,}"


def load_data():
    """Load contribution JSON."""

    if not INPUT.exists():
        raise FileNotFoundError(
            f"\nContribution file not found:\n{INPUT}\n"
        )

    return json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )


def normalize_level(count):
    """
    Convert contribution count into
    one of five visual levels.
    """

    if count <= 0:
        return 0

    if count == 1:
        return 1

    if count <= 3:
        return 2

    if count <= 6:
        return 3

    return 4


# =========================================================
# CALENDAR
# =========================================================

def prepare_calendar(days):
    """
    Convert contribution data into
    a 53 x 7 GitHub-style calendar.
    """

    values = {
        item["date"]: item.get("count", 0)
        for item in days
    }

    dates = [
        date.fromisoformat(item["date"])
        for item in days
    ]

    if not dates:
        return []

    latest = max(dates)

    # Find Sunday of the latest week
    latest_sunday = latest - timedelta(
        days=(latest.weekday() + 1) % 7
    )

    # Go back 52 weeks
    start = latest_sunday - timedelta(
        weeks=WEEKS - 1
    )

    cells = []

    for week in range(WEEKS):

        current_week = start + timedelta(
            weeks=week
        )

        for day in range(DAYS):

            current = current_week + timedelta(
                days=day
            )

            key = current.isoformat()

            count = values.get(
                key,
                0
            )

            cells.append({
                "week": week,
                "day": day,
                "date": key,
                "count": count,
                "level": normalize_level(count),
            })

    return cells


# =========================================================
# SVG GENERATION
# =========================================================

def create_svg(data):

    stats = data.get(
        "stats",
        {}
    )

    total = stats.get(
        "total",
        0
    )

    current_streak = stats.get(
        "current_streak",
        0
    )

    longest = stats.get(
        "longest_streak",
        {}
    )

    if isinstance(longest, dict):
        longest_streak = longest.get(
            "length",
            0
        )
    else:
        longest_streak = longest

    username = data.get(
        "username",
        "vadimkulishov"
    )

    cells = prepare_calendar(
        data.get("days", [])
    )

    svg = []

    # =====================================================
    # SVG HEADER + CSS
    # =====================================================

    svg.append(
        f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}"
role="img"
aria-label="Cyberpunk GitHub contribution activity for {esc(username)}"
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

.background {{
    fill: {BACKGROUND};
    stroke: {YELLOW};
    stroke-width: 1.5;
}}

.title {{
    fill: {YELLOW};
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 2px;
}}

.subtitle {{
    fill: {MUTED};
    font-size: 10px;
    letter-spacing: 1px;
}}

.footer {{
    fill: {TEXT};
    font-size: 10px;
    letter-spacing: 0.5px;
}}

.cell {{
    opacity: 0;

    transform-box: fill-box;
    transform-origin: center;

    animation:
        reveal 0.35s ease-out forwards;
}}

@keyframes reveal {{

    from {{
        opacity: 0;

        transform:
            translate(-8px, -8px)
            scale(0.6);
    }}

    to {{
        opacity: 1;

        transform:
            translate(0, 0)
            scale(1);
    }}

}}

.scanline {{
    opacity: 0.08;

    animation:
        scan 4s linear infinite;
}}

@keyframes scan {{

    from {{
        transform: translateY(-20px);
    }}

    to {{
        transform: translateY(220px);
    }}

}}

.pulse {{
    animation:
        pulse 1.8s ease-in-out infinite;
}}

@keyframes pulse {{

    0% {{
        opacity: 0.35;
    }}

    50% {{
        opacity: 1;
    }}

    100% {{
        opacity: 0.35;
    }}

}}

@media (prefers-reduced-motion: reduce) {{

    .cell {{
        animation: none;
        opacity: 1;
    }}

    .scanline {{
        animation: none;
    }}

    .pulse {{
        animation: none;
        opacity: 1;
    }}

}}

</style>
'''
    )

    # =====================================================
    # MAIN BACKGROUND
    # =====================================================

    svg.append(
        f'''
<rect
    class="background"
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="4"
/>
'''
    )

    # =====================================================
    # OUTER HUD CORNERS
    # =====================================================

    # TOP LEFT

    svg.append(
        f'''
<path
    d="M1 35 H22 L32 25 H110"
    fill="none"
    stroke="{CYAN}"
    stroke-width="2"
/>
'''
    )

    # TOP RIGHT

    svg.append(
        f'''
<path
    d="M{WIDTH - 110} 25 H{WIDTH - 32} L{WIDTH - 22} 35 H{WIDTH - 1}"
    fill="none"
    stroke="{MAGENTA}"
    stroke-width="2"
/>
'''
    )

    # BOTTOM LEFT

    svg.append(
        f'''
<path
    d="M1 {HEIGHT - 30} H22 L32 {HEIGHT - 20} H110"
    fill="none"
    stroke="{MAGENTA}"
    stroke-width="2"
/>
'''
    )

    # BOTTOM RIGHT

    svg.append(
        f'''
<path
    d="M{WIDTH - 110} {HEIGHT - 20} H{WIDTH - 32} L{WIDTH - 22} {HEIGHT - 30} H{WIDTH - 1}"
    fill="none"
    stroke="{CYAN}"
    stroke-width="2"
/>
'''
    )

    # =====================================================
    # HEADER
    # =====================================================

    svg.append(
        f'''
<text
    class="title"
    x="28"
    y="25"
>
    // NET_ACTIVITY
</text>

<text
    class="subtitle"
    x="28"
    y="42"
>
    {format_number(total)} CONTRIBUTIONS // LAST 365 DAYS
</text>

<circle
    class="pulse"
    cx="{WIDTH - 160}"
    cy="20"
    r="4"
    fill="{YELLOW}"
/>

<text
    class="subtitle"
    x="{WIDTH - 148}"
    y="24"
>
    NODE: ONLINE
</text>
'''
    )

    # =====================================================
    # DECORATIVE HEADER LINES
    # =====================================================

    svg.append(
        f'''
<line
    x1="28"
    y1="47"
    x2="{WIDTH - 28}"
    y2="47"
    stroke="{GRID}"
    stroke-width="1"
/>

<line
    x1="{WIDTH - 205}"
    y1="30"
    x2="{WIDTH - 28}"
    y2="30"
    stroke="{GRID}"
    stroke-width="1"
/>
'''
    )

    # =====================================================
    # SCANLINE
    # =====================================================

    svg.append(
        f'''
<rect
    class="scanline"
    x="0"
    y="0"
    width="{WIDTH}"
    height="2"
    fill="{CYAN}"
/>
'''
    )

    # =====================================================
    # HEATMAP CELLS
    # =====================================================

    for cell in cells:

        week = cell["week"]
        day = cell["day"]

        x = LEFT + week * STEP
        y = TOP + day * STEP

        level = cell["level"]
        count = cell["count"]

        color = LEVEL_COLORS[level]

        # Diagonal animation
        delay = (
            week * 0.018
            + day * 0.025
        )

        tooltip = (
            f'{count} contribution'
            f'{"s" if count != 1 else ""}'
            f' on {cell["date"]}'
        )

        svg.append(
            f'''
<rect
    class="cell"
    x="{x}"
    y="{y}"
    width="{CELL}"
    height="{CELL}"
    rx="2"
    fill="{color}"
    style="animation-delay:{delay:.3f}s"
>
    <title>{esc(tooltip)}</title>
</rect>
'''
        )

    # =====================================================
    # LEGEND
    # =====================================================

    legend_x = WIDTH - 180
    legend_y = 45

    svg.append(
        f'''
<text
    class="subtitle"
    x="{legend_x - 32}"
    y="{legend_y + 9}"
>
    LESS
</text>
'''
    )

    for level in range(5):

        x = legend_x + level * 16

        svg.append(
            f'''
<rect
    x="{x}"
    y="{legend_y}"
    width="12"
    height="12"
    rx="2"
    fill="{LEVEL_COLORS[level]}"
/>
'''
        )

    svg.append(
        f'''
<text
    class="subtitle"
    x="{legend_x + 86}"
    y="{legend_y + 9}"
>
    MORE
</text>
'''
    )

    # =====================================================
    # SIDE TECHNICAL LABELS
    # =====================================================

    svg.append(
        f'''
<text
    class="subtitle"
    x="28"
    y="166"
>
    ACTIVITY_MATRIX
</text>

<text
    class="subtitle"
    x="28"
    y="180"
>
    53 WEEKS / 07 DAYS
</text>
'''
    )

    # =====================================================
    # FOOTER
    # =====================================================

    footer_y = HEIGHT - 17

    svg.append(
        f'''
<text
    class="footer"
    x="28"
    y="{footer_y}"
>
    STREAK: {current_streak} DAYS
</text>

<text
    class="footer"
    x="190"
    y="{footer_y}"
>
    LONGEST: {longest_streak} DAYS
</text>

<text
    class="footer"
    x="{WIDTH - 205}"
    y="{footer_y}"
>
    VADIM // NIGHT CITY NODE
</text>
'''
    )

    # =====================================================
    # CLOSE SVG
    # =====================================================

    svg.append(
        '''
</svg>
'''
    )

    return "\n".join(svg)


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("Loading contribution data...")

    data = load_data()

    print(
        f"User: {data.get('username', 'unknown')}"
    )

    print(
        f"Days: {len(data.get('days', []))}"
    )

    print()
    print("Rendering Cyberpunk heatmap...")

    svg = create_svg(data)

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print("================================")
    print(" CYBERPUNK HEATMAP GENERATED")
    print("================================")
    print(
        f"Contributions: "
        f"{data.get('stats', {}).get('total', 0)}"
    )
    print(
        f"Current streak: "
        f"{data.get('stats', {}).get('current_streak', 0)}"
    )
    print(
        f"Output: {OUTPUT}"
    )
    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()