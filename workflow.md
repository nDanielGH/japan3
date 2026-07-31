# Planning workflow

Five ordered stages. Active hubs are self-contained. Do not advance or reopen
a stage without user approval; when its done-criteria are met, stop and ask.

Run `python scripts/validate.py` before declaring a stage complete. Record
rejected attractions in `skip_reason`; move rejected hubs intact to
`hubs/graveyard/`.

## 1. Research

- Copy `hubs/_template/` to `hubs/<name>/` for each candidate sleep base.
- Add attraction files to `hubs/<name>/attractions/inbox/` (`kebab-case.md` filenames).
- Collect sources and open questions in `hubs/<name>/research/` (copy `_note-template.md` per topic).

**Done when:** every user-requested, sourced, or agent-recommended idea has an
inbox attraction file or research note with a stable `hub/slug` reference. A
passing validator alone does not prove research completeness.

## 2. Triage

- Move researched attractions from `inbox/` → `shortlisted/`.
- After user confirmation, move to `selected/` or `skipped/`; only skipped
  files get `skip_reason`.

**Done when:** `inbox/` and `shortlisted/` are empty, except for files whose
open questions explain the deferral and its resolution.

## 3. Hub clustering

- Decide the hubs and assign selected attractions to them.
- Move misplaced attraction files to the correct hub.

**Done when:** every selected attraction is under the hub where the trip will
sleep when visiting it. If unknown, leave an open question rather than move it.

## 4. Time allocation

- Assign **nights/days per hub**.
- Record `nights` and `date_range` in each hub's `README.md`.

Do **not** allocate time to individual attractions; that happens in the itinerary.

**Done when:** ranges are contiguous, cover the canonical trip span, and each
half-open `[start, end)` interval has `nights = end - start` calendar days,
including arrival and departure dates.

## 5. Ordering

- Build one `YYYY-MM-DD.md` per sleep night in each hub's `itinerary/`, from
  `_day-template.md`.
- Respect root and hub constraints, especially daylight.

**Done when:** every sleep night has one itinerary file with an ordered plan,
selected-attraction links, and daylight-sensitive activities before sunset.
Checkout/transfer dates are not duplicated across hubs.
