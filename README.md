# reinstate-revert-revert

A tool for cleaning up reverted-revert git commit messages.

## Simple Case

It will turn

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

## Complex Case

If you have gotten yourself into a bind, it will also convert this:

```
Revert "Revert "Revert "Revert "Revert "Experiment on the flux capacitor"""""
```

into this, making it easier to follow the chain:

```
Revert "Experiment on the flux capacitor"

This reverts commit deadc0dedeadc0dedeadc0dedeadc0dedeadc0de.
And reinstates commit 0d15ea5e0d15ea5e0d15ea5e0d15ea5e0d15ea5e.
And reverts 1337beef1337beef1337beef1337beef1337beef.
And reinstates 1337f0011337f0011337f0011337f0011337f001.
And reverts 1337c0de1337c0de1337c0de1337c0de1337c0de.
```

Though once you’re using this as a pre-commit plugin, you should never get to
this case in the first place.

## Installation

### As a git hook

The simplest way to use this package is as a plugin to [pre-commit](https://pre-commit.com/).

A sample configuration:

```yaml
# Without default_stages, all hooks run in all stages, which means all your
# pre-commit hooks will run in prepare-commit-msg. That is almost certainly
# not what you want. This example will run for the default hooks installed.
# You might have to adjust it for your environment, if you have changed those
# defaults.
default_stages:
  - commit
repos:
  # […]
  - repo: https://github.com/erikogan/reinstate-revert-revert
    rev: v1.0.2
    hooks:
      - id: reinstate-revert-revert
        stages:
          - prepare-commit-msg
```

By default, pre-commit does not install a hook for the `prepare-commit-msg` stage. You probably need to add it for this to work:

```
pre-commit install -t pre-commit -t prepare-commit-msg
```

### As a standalone script

```
pip install reinstate-revert-revert
```

See `reinstate-revert-revert --help` for a full set of options.

`reinstate-revert-revert` takes log message file names as positional arguments.
