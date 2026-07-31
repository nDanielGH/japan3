# Planning workflow

Five stages, in order. Each active hub under `hubs/` is self-contained once
created. Do not advance or reopen a stage without the user's approval.

Run `python scripts/validate.py` before declaring a stage complete. Rejected
attractions are recorded in `skip_reason`; rejected hub directories are moved
intact to `hubs/graveyard/`.

## 1. Research

- Copy `hubs/_template/` to `hubs/<name>/` for each candidate sleep base (kebab-case names).
- Add attraction files to `hubs/<name>/attractions/inbox/` (`kebab-case.md` filenames).
- Collect sources and open questions in `hubs/<name>/research/` (copy `_note-template.md` per topic).

**Done when:** every user-requested idea, idea found in a source, or idea that
an agent recommends for a stated reason has either an inbox attraction file or
a research note containing a stable `hub/slug` reference. A passing validator
alone does not prove research completeness.

## 2. Triage

- Move attractions from `inbox/` → `shortlisted/` once you've looked into them.
- Move from `shortlisted/` → `selected/` (confirmed) or `skipped/` (ruled out, with `skip_reason`).

**Done when:** no files remain in `inbox/` or `shortlisted/` unless the file's
open questions explicitly say why it is deliberately deferred and what would
resolve the deferral.

## 3. Hub clustering

- Decide which hubs exist and which selected attractions belong under each.
- Move any misplaced attraction files to the correct hub.

**Done when:** every selected attraction lives under the hub where the trip
will sleep when visiting it. If that decision is not known, leave an open
question instead of moving the file speculatively.

## 4. Time allocation

- Assign **nights/days per hub** (e.g. 5 in Tokyo, 3 in Osaka).
- Record `nights` and `date_range` in each hub's `README.md`.

Do **not** allocate time to individual attractions — that happens in the itinerary.

**Done when:** hub date ranges are contiguous by sharing transfer/check-in
dates, cover the canonical trip span without gaps in sleep intervals, and each
half-open `[start, end)` interval has `nights = end - start` calendar days.
Hub ranges must account for the arrival and departure dates in root
`constraints.md`.

## 5. Ordering

- Build day-by-day drafts in `hubs/<name>/itinerary/` — one `YYYY-MM-DD.md` per day, copied from `_day-template.md`.
- Respect root `constraints.md` and each hub's `constraints.md`, especially daylight for outdoor activities.

**Done when:** every sleep night in every hub range has exactly one itinerary
file, each file has an ordered plan, all attraction links target selected
attractions, and daylight-sensitive activities are scheduled before sunset when
appropriate. Checkout/transfer dates are not duplicated across hubs.
