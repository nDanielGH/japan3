# Japan itinerary PWA

This directory contains the shared mobile interface for every trip day. The UI is intentionally data-driven: new itineraries belong in `days/`, while shared appearance and behavior remain in `styles.css` and `app.js`.

## Preview locally

From the repository root:

```powershell
python -m http.server 8765
```

Then open:

```text
http://localhost:8765/plan/pwa/?day=2026-10-20
```

A PWA requires `https://` or `localhost`. Opening `index.html` directly as a file will not provide service-worker or installation support.

## Add another day

1. Copy `days/2026-10-20.json` to a file named for the new date.
2. Replace the itinerary data while preserving the documented structure.
3. Keep supporting images under `plan/assets/<day-name>/` and reference them relative to the PWA directory, such as `../assets/2026-10-21_WED/map.png`.
4. Run the validator:

```powershell
python plan/pwa/scripts/validate_days.py
```

5. Preview the page at `?day=YYYY-MM-DD` at phone width.
6. Load it once while online so its data and images are cached for offline use.

Do not copy `index.html` or create day-specific CSS. The JSON file is the day’s source of truth.

## Supported content

Steps support these types:

- `transit`
- `walk`
- `meal`
- `visit`
- `task`
- `break`

Step content uses structured `blocks`:

- `paragraph` with `text`
- `warning` with `text`
- `list` with `items` and optional `ordered`

Actions and quick resources are either:

- `link` with `label` and `url`
- `image` with `label`, `imageLabel`, and `src`

Text supports `**bold emphasis**`. Arbitrary HTML is deliberately unsupported so day data cannot change the shared design.

The canonical structure is `schema/day.schema.json`. The browser also validates essential fields before rendering, and `scripts/validate_days.py` checks every day plus local image paths.

## Shared UI changes

Treat Tuesday (`2026-10-20`) as the visual reference. When changing `index.html`, `styles.css`, or `app.js`:

1. Verify Tuesday at a 390 × 844 viewport.
2. Test live and preview-time states.
3. Open an image, an external link, and a timeline card.
4. Confirm the preparation checklist persists after reload.
5. Increment `CACHE_VERSION` in `service-worker.js` so installed copies receive the update.

## Offline and installation

The service worker precaches the application shell and Tuesday. Once another day is opened online, its JSON and referenced images are cached automatically. External websites and map links still require a network connection.

For phone installation, deploy `plan/pwa/` and the sibling `plan/assets/` directory to an HTTPS host. Open the deployed page once, then use the browser’s “Add to Home Screen” or “Install” command.
