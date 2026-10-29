#!/usr/bin/env python3
"""Rebuild /best/ and the guide rating lines from data/businesses."""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from blend_score import PRIOR_MEAN, PRIOR_REVIEWS, blend_display  # noqa: E402

DATA = ROOT / "data" / "businesses"
PAGE = ROOT / "best" / "index.html"
FORMULA = DATA / "formula.json"
MARK_START = "<!-- BEST-LIST:START -->"
MARK_END = "<!-- BEST-LIST:END -->"

CATEGORY_LABELS = {
    "restaurant": "Restaurant",
    "cafe": "Coffee / cafe",
    "bar": "Bar",
    "hotel": "Hotel",
    "attraction": "Attraction",
}


def load_businesses():
    formula = json.loads(FORMULA.read_text())
    if formula.get("priorMean") != PRIOR_MEAN or formula.get("priorReviews") != PRIOR_REVIEWS:
        raise SystemExit("formula.json does not match scripts/blend_score.py")
    businesses = []
    for path in sorted(DATA.glob("*.json")):
        if path.name == "formula.json":
            continue
        payload = json.loads(path.read_text())
        businesses.extend(payload["businesses"])
    return businesses


def ratings_html(business, directory=False):
    rows = business["ratings"]
    bits = []
    shown = blend_display(rows)
    if shown:
        bits.append('<span class="avg">Blend %s</span>' % shown)
    links = []
    for row in rows:
        scale = row.get("scale") or 5
        score = row["rating"]
        score_text = ("%s/10" % score) if scale == 10 else str(score)
        links.append(
            '<a href="%s">%s</a> %s (%s)'
            % (html.escape(row["url"], quote=True), html.escape(row["source"]), score_text, f'{row["review_count"]:,}')
        )
    bits.append(" · ".join(links))
    checked = rows[0]["checked_date"] if rows else ""
    month = "Oct 2026" if checked.startswith("2026-10") else checked
    bits.append('<span class="when">checked %s</span>' % month)
    attrs = ' class="ratings"'
    if not directory:
        attrs = ' class="ratings" data-business="%s"' % business["id"]
    return "<p%s>%s</p>" % (attrs, " ".join(bits))


def card_html(business):
    shown = blend_display(business["ratings"]) or "0"
    price = business.get("priceBand") or ""
    neighborhood = business.get("neighborhood") or ""
    kicker_bits = [business["regionLabel"]]
    if neighborhood:
        kicker_bits.append(neighborhood)
    kicker_bits.append(CATEGORY_LABELS.get(business["category"], business["category"]))
    if price:
        kicker_bits.append(price)
    search = " ".join([
        business["name"], business["regionLabel"], neighborhood,
        business["category"], business.get("address") or "", price,
    ])
    links = []
    if business.get("website"):
        links.append('<a href="%s">Website</a>' % html.escape(business["website"], quote=True))
    for source in business.get("communitySources") or []:
        links.append('<a href="%s">%s</a>' % (html.escape(source["url"], quote=True), html.escape(source["title"])))
    parts = [
        '<article class="place-card biz-card" data-business-card',
        ' data-region="%s"' % html.escape(business["region"], quote=True),
        ' data-category="%s"' % html.escape(business["category"], quote=True),
        ' data-neighborhood="%s"' % html.escape(neighborhood, quote=True),
        ' data-price="%s"' % html.escape(price, quote=True),
        ' data-blend="%s"' % shown,
        ' data-search="%s">' % html.escape(search, quote=True),
        "<h3>%s</h3>" % html.escape(business["name"]),
        '<p class="biz-kicker">%s</p>' % html.escape(" · ".join(kicker_bits)),
        ratings_html(business, directory=True),
        '<p class="biz-why">%s</p>' % html.escape(business["why"]),
    ]
    if business.get("address"):
        parts.append('<p class="biz-address">%s</p>' % html.escape(business["address"]))
    if links:
        parts.append('<p class="biz-links">%s</p>' % " · ".join(links))
    parts.append("</article>")
    return "".join(parts)


def render_list(businesses):
    ranked = sorted(
        businesses,
        key=lambda business: (-(float(blend_display(business["ratings"]) or 0)), business["name"]),
    )
    return "\n".join(card_html(business) for business in ranked)


def write_page(list_html, count):
    page = PAGE.read_text()
    start = page.find(MARK_START)
    end = page.find(MARK_END)
    if start < 0 or end < 0:
        raise SystemExit("best/index.html is missing list markers")
    page = page[: start + len(MARK_START)] + "\n" + list_html + "\n" + page[end:]
    page = re.sub(
        r'(<p class="result-count" data-result-count>)[^<]*',
        r"\g<1>%d businesses" % count,
        page,
        count=1,
    )
    PAGE.write_text(page)


def sync_guides(businesses):
    by_url = {}
    for business in businesses:
        for row in business["ratings"]:
            by_url[row["url"]] = business
    for path in ROOT.glob("destinations/*/*/index.html"):
        text = path.read_text()

        def replace(match):
            block = match.group(0)
            for url, business in by_url.items():
                if url in block:
                    return ratings_html(business)
            return block

        updated = re.sub(r'<p class="ratings"[^>]*>.*?</p>', replace, text, flags=re.S)
        if updated != text:
            path.write_text(updated)


def main():
    businesses = load_businesses()
    if not businesses:
        raise SystemExit("no businesses")
    write_page(render_list(businesses), len(businesses))
    sync_guides(businesses)
    print("rendered", len(businesses))


if __name__ == "__main__":
    main()
