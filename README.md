# Downtown Kalamazoo website

The source for downtownkalamazoo.us. A small Python script (`build.py`) turns the files here into the website, and GitHub publishes it automatically whenever something changes.

- **Staff updates** (news, events, board documents, directory changes): see [`content/README.md`](content/README.md).
- **Year-round pages:** `yearround_section.py`
- **Holiday hub** (`/holidays/`): `holiday_content.py` and the holiday builders in `build.py`
- **Plan your day itineraries:** `content/itineraries.yml` (the plans), `itineraries.py` (checks and links them), `plan_section.py`, `plan.css` and `plan.js` (the planner and plan pages)
- **Styles and scripts:** `site.css` and `site.js` (included in every page)
- **Business directory data:** `directory.json`, plus edits in `content/directory-updates.yml`
- **Brand art** (patterns, wallpapers, coloring pages, QR signs): `make_assets.py` writes `assets_out/`. Run it only when the art changes; it needs `pip install cairosvg segno pypdf pillow`.

## Build it on your own computer (optional)

```
pip install markdown pyyaml
python build.py
```

The finished site is in `out/`.

## Publishing

`.github/workflows/publish.yml` builds and publishes on every commit to `main`, and once a day so date-based lists stay current. In the repository's **Settings → Pages**, **Source** must be set to **GitHub Actions**.
