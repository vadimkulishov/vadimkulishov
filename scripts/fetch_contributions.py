from pathlib import Path
from datetime import date, timedelta
import json
import re

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent

OUTPUT = ROOT / "data" / "contributions.json"

USERNAME = "vadimkulishov"

URL = f"https://github.com/users/{USERNAME}/contributions"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/139 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Referer": f"https://github.com/{USERNAME}",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_html() -> str:
    print(f"Fetching contributions for @{USERNAME}...")
    print(URL)

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    print(f"HTTP {response.status_code}")

    return response.text


def parse_contributions(html: str) -> list[dict]:
    print("Parsing contribution calendar...")

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    table = soup.select_one(
        "table.ContributionCalendar-grid"
    )

    if table is None:
        raise RuntimeError(
            "Could not find GitHub contribution calendar."
        )

    cells = table.select(
        "td.ContributionCalendar-day[data-date]"
    )

    if not cells:
        raise RuntimeError(
            "Contribution calendar contains no days."
        )

    days = []

    for cell in cells:
        date_value = cell.get("data-date")
        level_value = cell.get("data-level", "0")

        if not date_value:
            continue

        try:
            level = int(level_value)
        except ValueError:
            level = 0

        days.append(
            {
                "date": date_value,
                "level": level,
            }
        )

    days.sort(
        key=lambda item: item["date"]
    )

    # Current GitHub HTML stores the exact contribution
    # count in the tooltip associated with each cell.
    tooltips = {}

    for tooltip in soup.select(
        ".js-calendar-graph tool-tip"
    ):
        tooltip_for = tooltip.get("for")

        if tooltip_for:
            tooltips[tooltip_for] = tooltip.get_text(
                " ",
                strip=True,
            )

    for cell in cells:
        date_value = cell.get("data-date")

        if not date_value:
            continue

        cell_id = cell.get("id")

        count = 0

        if cell_id and cell_id in tooltips:
            text = tooltips[cell_id]

            match = re.search(
                r"(\d+)\s+contribution",
                text,
                re.IGNORECASE,
            )

            if match:
                count = int(match.group(1))

        for day in days:
            if day["date"] == date_value:
                day["count"] = count
                break

    # Some GitHub versions put the text directly inside
    # the calendar cell. Use that as a fallback.
    for cell in cells:
        date_value = cell.get("data-date")

        if not date_value:
            continue

        for day in days:
            if day["date"] != date_value:
                continue

            if day.get("count", 0) > 0:
                break

            text = cell.get_text(
                " ",
                strip=True,
            )

            match = re.search(
                r"(\d+)\s+contribution",
                text,
                re.IGNORECASE,
            )

            if match:
                day["count"] = int(
                    match.group(1)
                )

            break

    return days


def calculate_total(days: list[dict]) -> int:
    return sum(
        day.get("count", 0)
        for day in days
    )


def calculate_best_day(days: list[dict]):
    if not days:
        return None

    best = max(
        days,
        key=lambda day: day.get("count", 0),
    )

    if best.get("count", 0) == 0:
        return None

    return {
        "date": best["date"],
        "count": best["count"],
    }


def calculate_current_streak(
    days: list[dict],
) -> int:

    if not days:
        return 0

    values = {
        day["date"]: day.get("count", 0)
        for day in days
    }

    latest_date = max(values)

    current = date.fromisoformat(
        latest_date
    )

    # GitHub's current day may have 0 contributions.
    # Start from today and allow one empty day if needed.
    if values.get(
        current.isoformat(),
        0,
    ) == 0:
        current -= timedelta(days=1)

    streak = 0

    while True:
        key = current.isoformat()

        if values.get(key, 0) <= 0:
            break

        streak += 1
        current -= timedelta(days=1)

    return streak


def calculate_longest_streak(
    days: list[dict],
):
    if not days:
        return {
            "length": 0,
            "start": None,
            "end": None,
        }

    values = {
        day["date"]: day.get("count", 0)
        for day in days
    }

    sorted_dates = sorted(values)

    longest = 0
    longest_start = None
    longest_end = None

    current_length = 0
    current_start = None
    previous = None

    for date_string in sorted_dates:
        current_date = date.fromisoformat(
            date_string
        )

        count = values[date_string]

        if count > 0:
            if (
                previous is not None
                and current_date
                == previous + timedelta(days=1)
            ):
                current_length += 1
            else:
                current_length = 1
                current_start = current_date

            if current_length > longest:
                longest = current_length
                longest_start = current_start
                longest_end = current_date

        else:
            current_length = 0
            current_start = None

        previous = current_date

    return {
        "length": longest,
        "start": (
            longest_start.isoformat()
            if longest_start
            else None
        ),
        "end": (
            longest_end.isoformat()
            if longest_end
            else None
        ),
    }


def calculate_monthly_totals(
    days: list[dict],
):
    monthly = {}

    for day in days:
        month = day["date"][:7]

        monthly.setdefault(
            month,
            0,
        )

        monthly[month] += day.get(
            "count",
            0,
        )

    return monthly


def main():
    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    html = fetch_html()

    days = parse_contributions(html)

    total = calculate_total(days)

    best_day = calculate_best_day(days)

    current_streak = calculate_current_streak(
        days
    )

    longest_streak = calculate_longest_streak(
        days
    )

    monthly = calculate_monthly_totals(
        days
    )

    data = {
        "username": USERNAME,
        "source": URL,
        "days": days,
        "stats": {
            "total": total,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "best_day": best_day,
            "monthly": monthly,
        },
    }

    OUTPUT.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("================================")
    print(" Contribution statistics")
    print("================================")
    print(f"Days:             {len(days)}")
    print(f"Total:            {total}")
    print(f"Current streak:   {current_streak}")
    print(
        "Longest streak:  "
        f"{longest_streak['length']}"
    )

    if best_day:
        print(
            "Best day:         "
            f"{best_day['count']} "
            f"({best_day['date']})"
        )
    else:
        print("Best day:         0")

    print()
    print(f"Saved to: {OUTPUT}")


if __name__ == "__main__":
    main()