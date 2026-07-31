---
trip_start: 2026-10-18
trip_end: 2026-11-19
trip_nights: 32
arrival: Narita (NRT), 2026-10-18 17:05 JST
departure: Narita (NRT), 2026-11-19 15:45 JST
---

# Trip-wide constraints

Frontmatter is canonical for trip constants; other files reference it. Do not
change trip dates without user confirmation.

## Budget

Budget is not a constraint.

## Daylight

The sun sets before 17:00 for most of the trip; schedule
`daylight_sensitive: yes` activities early.

2026 sunset times equal 2025 almanac times, as agreed with the user on
2026-07-31. Fill sourced per-hub tables in
`hubs/<name>/constraints.md` before drafting itineraries.

Hub-specific constraints belong in `hubs/<name>/constraints.md`.
