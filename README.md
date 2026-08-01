# Japan Trip Planning

Git-backed Japan-trip planning workspace: research hubs, triage attractions,
allocate nights, and build the itinerary.

## Canonical files

- [constraints.md](constraints.md) — canonical trip constants and rules.
- [AGENTS.md](AGENTS.md) — agent rules and validation.
- [workflow.md](workflow.md) — iterative workstreams and completion criteria.
- [schema.md](schema.md) — file shape and invariants.
- [CONTRIBUTING.md](CONTRIBUTING.md) — local setup and contribution checks.
- [hubs/AGENTS.md](hubs/AGENTS.md) — rules for `hubs/`.

## Status

```yaml
focus: hub discovery and attraction research
hubs: []            # active hub folder names, e.g. [tokyo, kyoto]
next_actions: add candidate hubs; add researched attractions to inboxes
updated: 2026-07-31
```

This dashboard summarizes current work; it is not a workflow state machine.
The filesystem and frontmatter are authoritative for hub and attraction
readiness. Run the validator after edits and update this block when the active
hub set, focus, or next actions change.
