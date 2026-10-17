---
name: new-day
description: Add or extend a day itinerary under plan/ from the user's notes, then build, check, commit and push. Use whenever the user gives a plan, timings or steps for a specific trip date, or asks to create or update a day page.
---

# Add or update a day plan

Read `AGENTS.md` first; it defines the Markdown format and the rules. Then:

1. **Find the file.** `plan/week N/YYYY-MM-DD_DDD.md` already exists for every
   trip date (stubs contain only the heading). Keep the file name; the weekday
   suffix is validated against the date.
2. **Collect the facts from the user.** For every step you need a start time
   and either an end time or a duration, a kind label, and a one-line summary.
   If a time is missing, ask for it. Never estimate transit or walking times
   yourself unless the user explicitly asks you to.
3. **Write the Markdown** in the format from `AGENTS.md`: header lines
   (`title`, `subtitle`, `index`, `footer`), `## Before leaving`, `## Plan`
   with `### ` steps, `## Quick references`. Use `!!! warning` for tight
   connections, last departures, and safety notes. Put timetable screenshots
   and maps under `plan/assets/YYYY-MM-DD_DDD/` with kebab-case names.
4. **Build and check.**
   ```sh
   python3 scripts/build.py
   python3 scripts/check.py
   ```
   Fix every `ERROR` in the Markdown; never edit the generated HTML.
5. **Review the page** when anything visual changed: open the HTML at a
   390 × 844 viewport, open the current or first step, open each image in the
   viewer, and use the preview control to confirm the "Now" card updates.
6. **Update `trip.md`** if the day fixes a sleeping location, a booking, or a
   rental-car window.
7. **Commit and push** the Markdown, the generated HTML, `index.html`, and any
   assets, with a short imperative message. The pre-commit hook re-runs the
   check.

When the user changes one timing in an existing day, re-read the whole
timeline and update every later step; chained `+duration` steps move on their
own, absolute ones do not.
