# Japan Trip Planning

This is a git-backed planning workspace for a vacation in Japan, not an
application. Agents use it to research candidate hubs, triage attractions,
allocate nights, and order the final itinerary.

## Canonical files

- [constraints.md](constraints.md) — canonical trip dates, transport, budget,
  and trip-wide rules.
- [AGENTS.md](AGENTS.md) — agent operating rules, authority order, and
  validation command.
- [workflow.md](workflow.md) — the five planning stages and their completion
  criteria.
- [schema.md](schema.md) — frontmatter, filenames, references, and invariants.
- [hubs/AGENTS.md](hubs/AGENTS.md) — rules that apply inside `hubs/`.

## Status

```yaml
stage: 0            # 0 = not started; then 1–5 per workflow.md
stage_name: not started
hubs: []            # hub folder names, e.g. [tokyo, kyoto]
next_action: stage 1 — create candidate hubs, fill attraction inboxes
updated: 2026-07-31
```

The status block is a synchronized cache, not a second source of truth:
`hubs` must contain only active hub folder names. The filesystem and
frontmatter are authoritative. Run the validator after edits; update this
block whenever the stage or active hub set changes.
