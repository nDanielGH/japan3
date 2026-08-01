# Contributing

## Local setup

Enable the versioned Git hooks once per clone:

```text
git config core.hooksPath .githooks
```

Install the Markdown linter once on each machine:

```text
python -m pip install --user rumdl
```

The pre-commit hook exports the staged Git index to a temporary snapshot, then
runs `python scripts/validate.py` and `rumdl check` against that snapshot.
Rumdl applies standard Markdown rules and checks local file links (`MD057`) and
heading anchors (`MD051`). It is installed outside the repository, so the
project does not gain a runtime dependency.
