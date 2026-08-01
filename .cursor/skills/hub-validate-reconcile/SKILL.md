---
name: hub-validate-reconcile
description: Validate Japan-trip repository changes and identify affected Markdown dependents and invariant failures. Use after planning operations or when repository consistency is in doubt.
---

# Validate and reconcile

## Workflow

1. Read the changed files and inspect their semantic references, not only
   literal links.
2. Before changing Markdown dependents, run:
   `python scripts/validate.py --references <path>`.
3. Update every affected dependent, template, dashboard, or instruction file
   that now contains stale workflow or schema guidance.
4. Run `python scripts/validate.py`.
5. If available, run the repository's Markdown checks on the changed Markdown
   files. If the checker is unavailable, report that fact explicitly.
6. Re-read the final diff and report unresolved questions or validation errors.

Never hide validation failures, suppress a required confirmation, or repair
unrelated user changes. The filesystem, frontmatter, root constraints, schema,
and local hub rules remain authoritative.
