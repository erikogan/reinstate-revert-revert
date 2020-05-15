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
# Without default_stages, all hooks run in all stages, which means all your
# pre-commit hooks will run in prepare-commit-msg. This is almost certainly
# not what you want. This set will run for the default hooks installed, but
# you may have to adjust it for your environment.
default_stages:
  - commit
  - merge-commit
repos:
  # […]
  - repo: https://github.com/erikogan/reinstate-revert-revert
    rev: v0.1.3
    hooks:
      - id: reinstate-revert-revert
        stages:
          - prepare-commit-msg
```

By default, pre-commit does not install a hook for the `prepare-commit-msg` stage. You probably need to add it for this to work:

```
pre-commit install -t prepare-commit-msg
```

### As a standalone script

```
pip install reinstate-revert-revert
```

See `reinstate-revert-revert --help` for a full set of options.

`reinstate-revert-revert` takes log message file names as positional arguments.
