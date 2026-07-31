# Japan Trip Planning

Git-backed Japan-trip planning workspace: research hubs, triage attractions,
allocate nights, and build the itinerary.

## Canonical files

- [constraints.md](constraints.md) — canonical trip constants and rules.
- [AGENTS.md](AGENTS.md) — agent rules and validation.
- [workflow.md](workflow.md) — stages and completion criteria.
- [schema.md](schema.md) — file shape and invariants.
- [hubs/AGENTS.md](hubs/AGENTS.md) — rules for `hubs/`.

## Status

```yaml
stage: 0            # 0 = not started; 1–5 per workflow.md
stage_name: not started
hubs: []            # hub folder names, e.g. [tokyo, kyoto]
next_action: stage 1 — create candidate hubs, fill attraction inboxes
updated: 2026-07-31
```

This synchronized cache lists active hub folders; the filesystem and
frontmatter are authoritative. Run the validator after edits and update this
block when the stage or hub set changes.
