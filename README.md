# reinstate-revert-revert

A tool for cleaning up reverted-revert git commit messages. It will turn

```
Revert "Revert "Experiment on the flux capacitor""

This reverts commit deadc0dedeadc0dedeadc0dedeadc0dedeadc0de.
```

into

```
Reinstate "Experiment on the flux capacitor"

This reverts commit deadc0dedeadc0dedeadc0dedeadc0dedeadc0de.
And reinstates commit 0d15ea5e0d15ea5e0d15ea5e0d15ea5e0d15ea5e.
```

## Installation

### As a git hook

The simplest way to use this package is as a plugin to [pre-commit](https://github.com/pre-commit/pre-commit).

A sample configuration:

```yaml
- repo: https://github.com/erikogan/reinstate-revert-revert
  rev: v0.1.2
  hooks:
  - id: reinstate-revert-revert
```

### As a standalone script

```
pip install reinstate-revert-revert
```

See `reinstate-revert-revert --help` for a full set of options.

`reinstate-revert-revert` takes log message file names as positional arguments.
