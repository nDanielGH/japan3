---
name: hub-validate-reconcile
description: Validate Japan-trip repository changes and identify affected Markdown dependents and invariant failures. Use after planning operations or when repository consistency is in doubt.
disable-model-invocation: true
---

# Validate and reconcile

Before editing, follow the repository Mutation protocol. Declare every
dependent, template, dashboard, and instruction file owned by this operation;
stop if any owned path overlaps existing user changes. Back up all owned paths
before the first write so a failed reconciliation can restore only those paths.

## Workflow

1. Read the changed files and inspect their semantic references, not only
   literal links.
2. Before changing Markdown dependents, run:
   `python scripts/validate.py --references <path>`.
3. Update every affected dependent, template, dashboard, or instruction file
   that now contains stale workflow or schema guidance.
4. Run `python scripts/validate.py`.
5. If available, run the repository's Markdown checks on all changed Markdown
   files. If the checker is unavailable, report that fact explicitly.
6. If any check fails, restore every owned path from the pre-operation backup
   and report the failure; preserve unrelated user changes.
7. Re-read the final diff, confirm only owned paths changed, and report
   unresolved questions or validation errors.

Never hide validation failures, suppress a required confirmation, or repair
unrelated user changes. The filesystem, frontmatter, root constraints, schema,
and local hub rules remain authoritative.
