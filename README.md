# Best of West Coast

The first version of [Best of West Coast](https://zandergrant.github.io/bestofwestcoast/), a travel guide to the West Coast.

Plain HTML, CSS, and JavaScript. No framework and no build step. Open `index.html`, or serve the folder:

```bash
python3 -m http.server
```

Folder links such as `destinations/` resolve on a static server and on GitHub Pages. Opening a file directly still renders that page.

## GitHub Pages

Canonical URL: https://zandergrant.github.io/bestofwestcoast/

Publish from the `main` branch, folder `/` (root). In the repo: **Settings → Pages → Build and deployment → Deploy from a branch → `main` → `/ (root)` → Save.**

The live site shows whatever is on `main`. This version does not attach the custom domain. To use `bestofwestcoast.com` later, add a `CNAME` file, point DNS at GitHub Pages, and change `/bestofwestcoast/` in `404.html` to `/`.

## Pages

- `/` — homepage
- `/destinations/` — destination hub and the 24-cluster launch map
- `/destinations/<slug>/` — one page per priority cluster. Portland, Cannon Beach, Seattle, and San Francisco link to published guides. The others are still marked coming soon.
- `/destinations/portland/things-to-do/`, `/where-to-stay/`, and `/weekend/` — and the same three paths for Cannon Beach, Seattle, and San Francisco
- `/where-to-stay/`
- `/things-to-do/` — Things to Do, Eat & Drink
- `/road-trips/`
- `/comparisons/`
- `/discover/` — filter the launch map
- `/california/`, `/oregon/`, `/washington/`
- `/about/` — editorial standards
- `/newsletter/` — The West Coast Five (signup is a placeholder)
- `/404.html` — GitHub Pages 404, with root-absolute links

## Photographs

The homepage hero cycles through five photographs. Sources, photographers, and the Unsplash License are in [CREDITS.md](CREDITS.md).

## Places database

`data/places.json` is the place list. Recommendation fields stay empty until they are checked. The HTML repeats the same list so the site works with JavaScript off and when opened as a file.

## Content rules

No fabricated trips, invented reviews, or generated images presented as photographs. No hours, prices, safety, accessibility, or transport claims without a cited check. Unfinished guides say **Coming soon**.
