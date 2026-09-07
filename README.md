# The Ballroom Archive

An independent Dancing with the Stars fan archive built with Flask, pandas, Jinja, and vanilla CSS/JavaScript. The bundled historical dataset covers U.S. seasons 1–32: 394 contestant-season entries, 381 distinct celebrity names, and 51 professional partner names.

## Explore

- Browse each season’s cast, ordered by final placement, average judge score, or name.
- Search stars and professionals with keyboard-accessible, debounced suggestions.
- Follow links between celebrity profiles and professional partnerships.
- View weekly scores, scoring breakdowns, pro career results, and season rankings.
- Compare score ranks with actual placements and explore the highest season averages.

Pages, search, filters, and analytics render on the server and work without JavaScript. JavaScript enhances autocomplete; styling supports phones, keyboard focus, and reduced motion. The mirrorball illustration is CSS and requires no image assets.

## Run locally

Use Python 3.11 or newer:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --port 5050
```

Open http://127.0.0.1:5050. Google Fonts is optional; local fallback fonts are provided.

## Test

```bash
pip install pytest
python -m pytest -q
```

Tests cover season filtering and sorting, server-rendered pages, literal search queries, escaping, API compatibility, and score ranking with missing weeks and ties.

## Scoring and coverage

Average judge score is the mean of recorded weekly average judge scores, excluding zeros and missing weeks. Score rank orders these averages within a season, with ties sharing the minimum rank. It excludes audience votes and does not establish who deserved to win. Contestants have different run lengths; scoring formats and judging standards vary. Weekly totals are shown as recorded, not normalized across judging panels.

The archive is not a live results service. To extend coverage, update `dancing_with_the_stars_dataset.csv` with verified records matching its schema and restart the app. Season choices and archive counts derive from the data automatically. The loader expects numeric placement and season fields. Legacy API field names such as `should_have_placed` remain available for compatibility; the interface calls this metric “score rank.”

## Deployment

```bash
docker build -t ballroom-archive .
docker run --rm -p 8080:8080 -e SECRET_KEY=your-secret -e FLASK_ENV=production ballroom-archive
```

Production mode enforces HTTPS, so place the container behind an HTTPS proxy. For direct local Docker testing, omit `FLASK_ENV=production`. The image runs Gunicorn as a non-root user. Set a stable `SECRET_KEY` in production. Flask-Talisman applies a content security policy that permits local scripts and Google Fonts, without inline script or style exceptions.

Rate limits use in-process memory, suitable for the existing single-worker deployment. Multiple workers or replicas need shared rate-limit storage. The retained JSON endpoints are `/api/search`, `/api/names`, `/api/pros`, `/api/pros/names`, `/api/pros/search`, and `/api/analytics`.
