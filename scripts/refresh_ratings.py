#!/usr/bin/env python3
"""Re-read stored listing pages and update scores we can actually parse.

A blocked page, a captcha, or a page with no rating is skipped.
The stored score is not replaced with a guess.

    python3 scripts/refresh_ratings.py            # report only
    python3 scripts/refresh_ratings.py --write    # update JSON and rebuild /best/
"""

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "businesses"
UA = "BestOfWestCoastRatings/1.0 (+https://zandergrant.github.io/bestofwestcoast/about/)"


def region_files():
    return sorted(path for path in DATA.glob("*.json") if path.name != "formula.json")


def load_regions():
    loaded = []
    for path in region_files():
        loaded.append((path, json.loads(path.read_text())))
    return loaded


def parse_rating(html):
    block = re.search(
        r'"aggregateRating"\s*:\s*\{([^{}]{0,500})\}',
        html,
        re.I,
    )
    text = block.group(1) if block else html
    rating = re.search(r'"ratingValue"\s*:\s*"?(\d+(?:\.\d+)?)"?', text)
    count = re.search(r'"reviewCount"\s*:\s*"?(\d[\d,]*)"?', text)
    if not rating or not count:
        return None
    return float(rating.group(1)), int(count.group(1).replace(",", ""))


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read(400_000).decode("utf-8", "ignore")
            return response.status, body, None
    except urllib.error.HTTPError as error:
        return error.code, "", "http %s" % error.code
    except Exception as error:
        return None, "", type(error).__name__


def main():
    write = "--write" in sys.argv
    today = date.today().isoformat()
    changed = 0
    blocked = 0
    unparsed = 0
    regions = load_regions()
    for path, payload in regions:
        for business in payload.get("businesses", []):
            for row in business.get("ratings", []):
                status, body, err = fetch(row["url"])
                label = "%s / %s" % (business["id"], row["source"])
                if err or status != 200 or "captcha" in body.lower() or "unusual traffic" in body.lower():
                    blocked += 1
                    print("blocked", label, err or status)
                    continue
                parsed = parse_rating(body)
                if not parsed:
                    unparsed += 1
                    print("no rating on page", label)
                    continue
                rating, count = parsed
                same = rating == row["rating"] and count == row["review_count"]
                print("read", label, rating, count, "unchanged" if same else "update")
                if write and not same:
                    row["rating"] = rating
                    row["review_count"] = count
                    row["checked_date"] = today
                    changed += 1
                elif write and same:
                    row["checked_date"] = today
        if write:
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print("blocked", blocked, "unparsed", unparsed, "updated", changed)
    if write:
        sys.path.insert(0, str(ROOT / "scripts"))
        import render_best
        render_best.main()


if __name__ == "__main__":
    main()
