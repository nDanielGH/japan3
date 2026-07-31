# Planning workflow

Five stages, in order. Each hub under `hubs/` is self-contained once created.

## 1. Research

- Copy `hubs/_template/` to `hubs/<name>/` for each candidate sleep base.
- Add attraction files to `hubs/<name>/attractions/inbox/`.
- Collect sources and open questions in `hubs/<name>/research/`.

**Done when:** every idea worth exploring has an inbox file or a research note pointing to it.

## 2. Triage

- Move attractions from `inbox/` → `shortlisted/` once you've looked into them.
- Move from `shortlisted/` → `selected/` (confirmed) or `skipped/` (ruled out, with `skip_reason`).

**Done when:** no files remain in `inbox/` or `shortlisted/` unless deliberately deferred.

## 3. Hub clustering

- Decide which hubs exist and which selected attractions belong under each.
- Move any misplaced attraction files to the correct hub.

**Done when:** every selected attraction lives under the hub you'll sleep at when visiting it.

## 4. Time allocation

- Assign **nights/days per hub** (e.g. 5 in Tokyo, 3 in Osaka).
- Record `nights` and `date_range` in each hub's `README.md`.
- Summarize the allocation in `hubs/README.md`.

Do **not** allocate time to individual attractions — that happens in the itinerary.

**Done when:** hub nights sum to the trip span and each hub has a date range.

## 5. Ordering

- Build day-by-day drafts in `hubs/<name>/itinerary/`.
- Respect root `constraints/` and hub `constraints/`, especially daylight for outdoor activities.

**Done when:** each hub day has an ordered plan using selected attractions.
