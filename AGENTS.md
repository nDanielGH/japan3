# AGENTS.md — operating guide for AI agents

This repo is a git-backed plan for a Japan trip (see [README.md](README.md)).
You are the planner's assistant: keep it accurate, consistent, and current
while executing [workflow.md](workflow.md).

## Authority order

When information appears in more than one place, use this order:

1. The filesystem determines whether a hub, attraction, research note, or
   itinerary day exists and, for attractions, the triage status.
2. YAML frontmatter determines metadata for that file.
3. Root [constraints.md](constraints.md) is the only source of trip-wide
   constants. Hub `constraints.md` files contain only local rules and sourced
   daylight data.
4. The root README Status block is a synchronized cache of the current stage
   and active hub folders; it must match the filesystem.
5. This file governs agent operations; [schema.md](schema.md) governs file
   shape; [workflow.md](workflow.md) governs stage order and completion.

## On session start

1. Read the **Status** block in [README.md](README.md) for the current stage and hub set.
2. Read [workflow.md](workflow.md) (stages and done-criteria), [constraints.md](constraints.md) (hard rules + canonical trip constants), and [schema.md](schema.md) (file conventions).
3. Read [hubs/AGENTS.md](hubs/AGENTS.md) before working inside `hubs/`.
4. Check `hubs/graveyard/` before proposing a hub that may already have been rejected.
5. Work on the current stage. Ask before jumping ahead or reopening a finished stage.
6. Run `python scripts/validate.py` after non-trivial edits and before
   declaring a stage complete.
7. Before editing any Markdown file, audit its dependents with
   `python scripts/validate.py --references <path>`.

## Operations

### Add a hub

1. Copy `hubs/_template/` to `hubs/<name>/` (`<name>` in kebab-case, e.g. `hubs/tokyo/`).
2. Fill the hub README frontmatter (`name`, `nights`, `date_range`, `base_location`).
3. Add the folder name to the `hubs:` list in the root README Status block.

### Reject a hub

- Move the entire rejected hub directory to `hubs/graveyard/<name>/`.
- Do not include graveyard folders in the root README Status `hubs:` list.
- The graveyard location is the record of the rejection; add context to the
  hub's README if useful.

### Add an attraction

1. Copy `hubs/<name>/attractions/_template.md` into
   `hubs/<name>/attractions/inbox/`.
2. Filename: `kebab-case.md`, unique within the hub, no spaces.
3. Fill in what is known; use `null` for unknown frontmatter values. Unknowns go under `## Open questions` as `- [ ]` items.
4. For anything popular (Ghibli Museum, teamLab, Shibuya Sky, USJ, …) check `booking_required`; if yes, set `book_by`.

### Triage an attraction

- `git mv` the file between `inbox/`, `shortlisted/`, `selected/`, `skipped/`. **The folder is the only status indicator** — there is no status field to update.
- A file entering `skipped/` must have `skip_reason` filled in.

### Reference attractions

- In prose and research notes, reference by stable `hub/slug` (for example
  `kyoto/fushimi-inari`). Triage moves change folder paths, so full paths go
  stale.
- Itinerary day files are the exception: use relative links to
  `../attractions/selected/<slug>.md`. Those links must resolve.

### Allocate time (stage 4)

- Set `nights` and `date_range` in each hub's README frontmatter.
- Never allocate time to individual attractions.

### Draft itinerary days (stage 5)

1. Copy `hubs/<name>/itinerary/_day-template.md` to `hubs/<name>/itinerary/YYYY-MM-DD.md`.
2. Fill `sunset:` from the daylight table in
   `hubs/<name>/constraints.md`.
3. Schedule `daylight_sensitive: yes` activities early in the day.

## Facts, uncertainty, and open questions

- **Don't invent facts.** Factual claims in attraction notes and research
  notes need a source line in `research/`:
  `- <claim> — [<title>](URL) — accessed YYYY-MM-DD`.
- If you can't verify a claim, tag it with the exact token `UNVERIFIED`
  (plain ASCII, no dashes) and mirror that claim as a matching unchecked open
  question.
- Open questions are `- [ ]` items, one per line, under a `## Open questions` heading — findable and countable via repo-wide search.
- Ambiguous triage or scheduling call? Add an open question instead of guessing.
- Rejected attractions are documented by `skip_reason`; rejected hubs are
  documented by their location under `hubs/graveyard/`.

## Hard rules

- **Never delete an attraction file.** Ruled-out ideas go to `skipped/` with a `skip_reason`.
- **Never delete a rejected hub directory.** Move it intact to `hubs/graveyard/`.
- **Never edit `hubs/_template/`** unless explicitly asked to change the template itself.
- **Don't change trip dates** in `constraints.md` without user confirmation. The `constraints.md` frontmatter is the canonical source for trip constants — other files reference it, nothing restates it.
- **Do not create parallel indexes** — the filesystem and frontmatter are the
  index; use Glob or ripgrep.
- Keep the **Status** block in `README.md` current whenever the stage or hub set changes.

## Validation

Run:

```text
python scripts/validate.py
```

The validator is the executable form of this checklist. Fix failures or report
why a stage-gated check is intentionally not applicable before finishing.

- Every active hub has the required directory structure and valid metadata.
- Every attraction is in exactly one triage folder, and skipped attractions
  have `skip_reason`.
- IDs and slugs are unique within their collection.
- Markdown links, stable `hub/slug` references, and itinerary selected-links
  resolve.
- Source lines have URLs and access dates; `UNVERIFIED` claims have matching
  unchecked questions; no legacy assumed markers exist.
- The README Status `hubs` list matches active folders.
- From stage 3, selected attractions are under the hub where they will be
  visited.
- From stage 4, hub nights sum to `trip_nights`, date ranges are contiguous
  and valid, and nights equal the number of calendar intervals.
- From stage 5, itinerary filenames, frontmatter dates, hubs, selected links,
  and sourced sunset values are consistent.

## Markdown dependency review

Markdown files are a connected instruction and data system. When editing one,
do not assume that fixing the file itself is sufficient:

1. Run `python scripts/validate.py --references <edited-file>` before editing
   to find inbound links and prose references.
2. Read every referring Markdown file, including templates and agent
   instructions.
3. Update dependent links, duplicated facts, examples, and instructions when
   the edited file's meaning or interface changed. If they remain correct,
   leave them unchanged deliberately.
4. Search for the edited file's key terms, headings, field names, and IDs as
   well as its path; not all semantic references are Markdown links.
5. Run the normal validator afterward and repeat the dependency review for
   every renamed or moved file.

The reference command is a discovery aid, not proof that the dependent files
are semantically consistent. Agents must still review the returned lines.

## Git hook

The repository includes a versioned pre-commit hook at
`.githooks/pre-commit`. Enable it once per clone:

```text
git config core.hooksPath .githooks
```

The hook runs `python scripts/validate.py` and blocks commits that would leave
the planning data inconsistent. Run the validator manually when hook
configuration is unavailable.

## Commit conventions

Small, frequent commits — one logical change each:

```text
triage(kyoto): select fushimi-inari
triage(tokyo): skip robot-cafe — permanently closed
hub(osaka): allocate 4 nights
research(nikko): add autumn-foliage sources
itinerary(tokyo): draft 2026-10-20
docs: update workflow rules
```

## Glossary

- **Hub** — a sleep base; a folder under `hubs/`. Time is allocated per hub, never per attraction.
- **Attraction** — a place or activity; one markdown file, triaged by folder.
- **Triage** — moving an attraction through `inbox → shortlisted → selected/skipped`.
- **Stage** — the repo's current phase of the five in `workflow.md`.
