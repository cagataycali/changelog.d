# GitHub Action

Add this file to your repo:

```yaml title=".github/workflows/changelog.yml"
name: changelog
on:
  pull_request:
    types: [opened, synchronize, reopened, labeled, unlabeled]

jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0          # it needs the history to compare against
      - uses: cagataycali/changelog.d@main
        with:
          ignore: |
            docs/**
            *.md
```

That's it. Every pull request now gets a **changelog** check that finishes in seconds. To make it required, turn it on in your branch protection settings.

## What it checks

1. **Nobody wrote into `CHANGELOG.md` directly.** Release pull requests made with `changelog-d apply` pass.
2. **The pull request's notes are written correctly.** Notes that were already on `main` don't count against it.
3. **There's a note, if code changed.** Files matching `ignore` don't need one, and neither does anything labelled `skip-changelog`.

When something's wrong, the check points at the exact file and says how to fix it.

## Settings

| Setting | Default | What it does |
|---|---|---|
| `require` | `true` | Ask for a note when code changes. Set it to `false` to only check notes that exist. |
| `skip-label` | `skip-changelog` | A PR with this label doesn't need a note. |
| `ignore` | *(nothing)* | Files that never need a note, e.g. `docs/**`. |
| `match-number` | `false` | The note's number must be this PR's number. |
| `directory` | `changelog.d` | Where the notes live. |
| `changelog` | `CHANGELOG.md` | Your changelog file. |
| `heading` | `## [Unreleased]` | The section the notes go under. |
| `working-directory` | `.` | For monorepos. |

It also gives you two outputs: `ok` (`"true"` or `"false"`) and `fragments` (how many notes the PR adds).

## Good to know

- **It installs nothing.** It uses the Python that every GitHub runner already has.
- **A pull request can't weaken the check.** The rules come from the action itself, not from the branch being checked.
- **It's safe with odd branch names.** No input is ever pasted into a shell command.

!!! note "While this repo is private"
    Other repos can only use this action if you allow it in **Settings → Actions → General → Access**.
