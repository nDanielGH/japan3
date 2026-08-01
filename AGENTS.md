# AGENTS.md — operating guide for AI agents

Git-backed Japan-trip plan (see [README.md](README.md)); keep it accurate and
consistent while executing [workflow.md](workflow.md).

## Authority order

Use this authority order: filesystem for existence and triage status; YAML
frontmatter for file metadata; root [constraints.md](constraints.md) for
trip-wide constants; README Status as a dashboard cache; this file for
operations, [schema.md](schema.md) for file shape, and [workflow.md](workflow.md)
for workstreams and dependencies.

## On session start

1. Read README Status, [workflow.md](workflow.md), [constraints.md](constraints.md),
   and [schema.md](schema.md).
2. Read [hubs/AGENTS.md](hubs/AGENTS.md) before working inside `hubs/`.
3. Check `hubs/graveyard/` before proposing a hub that may already have been rejected.
4. Choose a workstream whose local prerequisites are satisfied; unrelated hubs
   may be at different levels of readiness.
5. Run `python scripts/validate.py` after non-trivial edits and before treating
   a hub or the trip as complete.
6. Before editing Markdown, run `python scripts/validate.py --references <path>`.

## Operations

Project skills in `.cursor/skills/` encode repeatable procedures:

- `hub-create`, `hub-research`, and `hub-reject`
- `attraction-create`, `attraction-research`, and `attraction-triage`
- `hub-draft-schedule` and `hub-draft-day-itinerary`
- `hub-validate-reconcile`

Read the relevant skill before performing one of these operations. Skills may
provide more detailed steps, but they do not override the rules below, the
schema, or canonical constraints.

### References

- In prose and research notes, use stable `hub/slug` references (for example
  `kyoto/fushimi-inari`); do not use triage paths.
- Itinerary days instead use resolving relative links to
  `../attractions/selected/<slug>.md`.

## Facts, uncertainty, and open questions

- **Don't invent facts.** Source attraction/research claims in `research/`:
  `- <claim> — [<title>](URL) — accessed YYYY-MM-DD`.
- Unverifiable claims use exact `UNVERIFIED` plus a matching unchecked
  `## Open questions` item. Use `- [ ]`, one question per line.
- For ambiguous triage/scheduling, add a question instead of guessing.
- Record new trip-wide preferences or constraints as questions and ask the user.

## Hard rules

- Never delete attraction files; move ruled-out ideas to `skipped/` with
  `skip_reason`. Never delete rejected hubs; move them intact to `graveyard/`.
- Never edit `hubs/_template/` unless explicitly asked.
- Never change trip dates without user confirmation; root `constraints.md`
  frontmatter is canonical.
- Do not create parallel indexes; filesystem and frontmatter are the index.
- Keep the README Status dashboard current when the focus, next actions, or hub
  set changes.

## Validation

Run `python scripts/validate.py` and fix failures.

- It validates hub structure/metadata, attraction triage and `skip_reason`,
  unique IDs, links/references, source dates, `UNVERIFIED` questions, and the
  README Status dashboard, including the declared skill inventory.
- It validates every present schedule independently, rejects overlapping
  schedules, and checks full trip coverage when all active hubs are scheduled.
- It validates each present itinerary day against its own hub, schedule, links,
  and sourced sunset metadata. A hub marked `complete` must have every
  scheduled sleep night represented by an itinerary day.

## Markdown dependency review

Use `hub-validate-reconcile` for the full dependency review. Before editing
Markdown, run `python scripts/validate.py --references <path>`; update affected
dependents and run the validator again. The skill owns the detailed discovery
and reconciliation procedure; the reference output is only a discovery aid.

## Mutation protocol

Every operation that creates, edits, moves, or renames repository files must
use this protocol:

1. Before writing, run `git status --short` and identify every path the
   operation owns, including affected dependents. Stop and ask if an owned
   path already has staged, unstaged, or untracked user changes.
2. Confirm all destinations are absent or explicitly approved for revision.
   Never overwrite an existing file or directory implicitly.
3. Capture an exact backup of every owned path, including paths that will be
   moved or deleted, outside the repository before the first write. Keep
   unrelated working-tree changes untouched.
4. Apply the complete operation, then run `python scripts/validate.py` and
   `rumdl check <changed Markdown files>` against every changed Markdown file.
   If Rumdl is unavailable, report that the operation is not fully verified.
5. If any check fails, restore only the owned paths from the backup, remove
   only paths created by the operation, and report the failure. Never use
   destructive Git commands or discard unrelated changes.
6. Re-read the final diff, confirm the operation-owned paths are the only
   changes, and report unresolved questions. Do not commit or push unless the
   user separately asks.

For a move or multi-file change, treat the operation as one transaction:
partial success is not completion. A validation failure must leave the
repository at its pre-operation state for all owned paths.

## Git hook

Enable the versioned hook once per clone:

```text
git config core.hooksPath .githooks
```

The hook runs `python scripts/validate.py` and the configured Markdown checks
before each commit.

## Commit conventions

Use small, logical commits:

```text
triage(kyoto): select fushimi-inari
triage(tokyo): skip robot-cafe — permanently closed
hub(osaka): allocate 4 nights
research(nikko): add autumn-foliage sources
itinerary(tokyo): draft 2026-10-20
docs: update workflow rules
```

## Glossary

- **Hub** — sleep base under `hubs/`; time is allocated per hub.
- **Attraction** — place/activity represented by one triaged Markdown file.
- **Triage** — `inbox → shortlisted → selected/skipped`.
- **Hub schedule** — the higher-level allocation of nights and dates to hubs.
- **Day itinerary** — the ordered plan for one date within one hub.
