from pathlib import Path
from datetime import date, timedelta
import json
import html


ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "contrib-heatmap.svg"


# ---------------------------------------------------------
# Layout
# ---------------------------------------------------------

WEEKS = 53
DAYS = 7

CELL = 12
GAP = 4

STEP = CELL + GAP

LEFT = 28
TOP = 42

GRID_WIDTH = WEEKS * STEP
GRID_HEIGHT = DAYS * STEP

WIDTH = 860
HEIGHT = 180


# ---------------------------------------------------------
# Colors
# ---------------------------------------------------------

BACKGROUND = "#0d1117"
BORDER = "#30363d"

TEXT = "#c9d1d9"
MUTED = "#8b949e"

LEVEL_COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def esc(value):
    return html.escape(str(value))


def load_data():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Contribution data not found: {INPUT}"
        )

    return json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )


def normalize_level(count):
    """
    Convert an exact contribution count into
    one of GitHub-style levels 0-4.
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


def prepare_calendar(days):
    """
    Create exactly 53 columns × 7 rows.

    GitHub contribution calendars are Sunday -> Saturday.
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

    # Find Sunday at the beginning of the latest week.
    latest_sunday = latest - timedelta(
        days=(latest.weekday() + 1) % 7
    )

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
                0,
            )

            cells.append(
                {
                    "week": week,
                    "day": day,
                    "date": key,
                    "count": count,
                    "level": normalize_level(count),
                }
            )

    return cells


def format_number(number):
    return f"{number:,}"


# ---------------------------------------------------------
# SVG
# ---------------------------------------------------------

def create_svg(data):
    stats = data["stats"]

    total = stats.get(
        "total",
        0,
    )

    current_streak = stats.get(
        "current_streak",
        0,
    )

    longest = stats.get(
        "longest_streak",
        {},
    )

    longest_streak = longest.get(
        "length",
        0,
    )

    cells = prepare_calendar(
        data["days"]
    )

    svg = []

    svg.append(
        f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}"
role="img"
aria-label="GitHub contribution heatmap for {esc(data["username"])}"
>

<style>

.background {{
    fill: {BACKGROUND};
    stroke: {BORDER};
    stroke-width: 1;
}}

.title {{
    fill: {TEXT};
    font-family:
        "SFMono-Regular",
        "Cascadia Code",
        "Roboto Mono",
        "Courier New",
        monospace;

    font-size: 14px;
    font-weight: 600;
}}

.subtitle {{
    fill: {MUTED};
    font-family:
        "SFMono-Regular",
        "Cascadia Code",
        "Roboto Mono",
        "Courier New",
        monospace;

    font-size: 11px;
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
            translate(-10px, -10px)
            scale(0.65);
    }}

    to {{
        opacity: 1;
        transform:
            translate(0, 0)
            scale(1);
    }}

}}

@media (prefers-reduced-motion: reduce) {{

    .cell {{
        animation: none;
        opacity: 1;
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

<text
    class="title"
    x="24"
    y="23"
>
    $ git log --activity
</text>

<text
    class="subtitle"
    x="24"
    y="39"
>
    {format_number(total)} contributions in the last year
</text>
'''
    )

    # -----------------------------------------------------
    # Contribution cells
    # -----------------------------------------------------

    for cell in cells:

        week = cell["week"]
        day = cell["day"]
        level = cell["level"]

        x = LEFT + week * STEP
        y = TOP + day * STEP

        color = LEVEL_COLORS[level]

        # Diagonal animation.
        delay = (
            week * 0.018
            + day * 0.025
        )

        count = cell["count"]

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
    rx="3"
    fill="{color}"
    style="animation-delay:{delay:.3f}s"
>
    <title>{esc(tooltip)}</title>
</rect>
'''
        )

    # -----------------------------------------------------
    # Legend
    # -----------------------------------------------------

    legend_x = WIDTH - 145
    legend_y = 20

    svg.append(
        f'''
<text
    class="subtitle"
    x="{legend_x - 30}"
    y="{legend_y + 9}"
>
    Less
</text>
'''
    )

    for level in range(5):

        x = (
            legend_x
            + level * (CELL + 3)
        )

        svg.append(
            f'''
<rect
    x="{x}"
    y="{legend_y}"
    width="{CELL}"
    height="{CELL}"
    rx="3"
    fill="{LEVEL_COLORS[level]}"
/>
'''
        )

    svg.append(
        f'''
<text
    class="subtitle"
    x="{legend_x + 5 * (CELL + 3) + 3}"
    y="{legend_y + 9}"
>
    More
</text>
'''
    )

    # -----------------------------------------------------
    # Footer stats
    # -----------------------------------------------------

    footer_y = HEIGHT - 19

    svg.append(
        f'''
<text
    class="subtitle"
    x="24"
    y="{footer_y}"
>
    current streak: {current_streak} days
</text>

<text
    class="subtitle"
    x="210"
    y="{footer_y}"
>
    longest streak: {longest_streak} days
</text>

<text
    class="subtitle"
    x="{WIDTH - 190}"
    y="{footer_y}"
>
    @vadimkulishov
</text>
'''
    )

    svg.append("</svg>")

    return "\n".join(svg)


def main():

    print("[1/2] Loading contribution data...")

    data = load_data()

    print("[2/2] Rendering heatmap...")

    svg = create_svg(data)

    OUTPUT.write_text(
        svg,
        encoding="utf-8",
    )

    print()
    print(f"Done: {OUTPUT}")
    print(
        f"Total contributions: "
        f"{data['stats']['total']}"
    )


if __name__ == "__main__":
    main()