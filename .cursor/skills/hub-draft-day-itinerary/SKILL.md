---
name: hub-draft-day-itinerary
description: Draft one Japan-trip day from selected attractions while checking hours, duration, transit, ordering, sunset, and meal time. Use when planning a dated itinerary day.
disable-model-invocation: true
---

# Draft day itinerary

## Preconditions

- Require one scheduled hub and a target date within its half-open sleep range.
- Read root and hub constraints, selected attraction records, related research,
  and the day template.
- Confirm local sunset data exists for the target date. Do not infer it from
  the root “before 17:00” guidance.
- For a new day, copy the template first and run
  `python scripts/validate.py --references <new-day-file>` before filling it.
  For a revision, run the reference audit before editing the existing file.
- Follow the repository Mutation protocol. The owned path is the target day
  file; for a new day it must not exist, and for a revision the existing file
  must be explicitly identified. Stop if it overlaps existing user changes.

## Planning rules

1. Use only attractions in that hub's `selected/` collection.
2. Verify opening hours, access restrictions, expected duration, and booking
   requirements from cited research. Treat unknown logistics as a blocker or
   clearly label them for user resolution.
3. Schedule `daylight_sensitive: yes` activities before local sunset.
4. Order activities geographically and temporally, including realistic
   transportation and transition buffers.
5. Allocate meal time unless an attraction already includes it; do not invent
   restaurant bookings.
6. Avoid an overfull day and preserve arrival, departure, and rest constraints.

## Conflict boundary

If selected attractions cannot fit, hours conflict, sources disagree, or the
date is ambiguous, stop with a concise conflict report and questions. Do not
silently deselect, move, or reschedule attractions.

## Output

Create or revise `hubs/<hub>/itinerary/YYYY-MM-DD.md` from the template, use
selected-attraction relative links, fill the sourced local `sunset`, then run
`python scripts/validate.py` and the configured Markdown checks. If any check
fails, restore the target day file from the pre-operation backup and report the
conflict rather than leaving a partial day file.
