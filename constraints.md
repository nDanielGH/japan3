---
trip_start: 2026-10-18
trip_end: 2026-11-19
trip_nights: 32
arrival: Narita (NRT), 2026-10-18 17:05 JST
departure: Narita (NRT), 2026-11-19 15:45 JST
---

# Trip-wide constraints

Rules that apply across all hubs. The frontmatter above is the canonical, machine-readable source for trip constants — other files reference it, nothing restates it. Don't change trip dates without user confirmation.

## Trip dates

|               |                                     |
| ------------- | ----------------------------------- |
| **Arrival**   | Narita (NRT), 2026-10-18, 17:05 JST |
| **Departure** | Narita (NRT), 2026-11-19, 15:45 JST |
| **Span**      | 32 nights / 33 calendar days        |

## Budget

Budget is not a constraint for this trip.

## Daylight

Daylight hours affect itinerary viability, especially for outdoor and scenic days. The sun sets before 17:00 for most of the trip — schedule `daylight_sensitive: yes` activities early.

2026 sunset times are assumed equal to 2025 almanac times (agreed with user, 2026-07-31). Per-hub sunset tables live in `hubs/<name>/constraints.md`; fill them from an almanac (source URL + access date) before drafting itineraries.

Hub-specific constraints belong in `hubs/<name>/constraints.md`.
