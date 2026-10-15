# GitHub Action

One step. It runs in a few seconds, before your tests even install.

```yaml title=".github/workflows/changelog.yml"
name: changelog
on:
  pull_request:
    types: [opened, synchronize, reopened, labeled, unlabeled]

permissions:
  contents: read

jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0          # the gate needs the merge base
      - uses: cagataycali/changelog.d@main
        with:
          ignore: |
            docs/**
            .github/**
            *.md
```

The `labeled` / `unlabeled` triggers re-run the check when someone adds `skip-changelog`.

Then make the `changelog` check required in your branch protection.

## What it checks

1. **Nothing was written straight into `## [Unreleased]`.** A release PR that ran `changelog-d apply` passes, because each new entry matches a fragment it deleted.
2. **The fragments this PR adds or changes are valid.** Fragments already on the base branch aren't held against it.
3. **The PR adds a fragment** if it changes anything outside `ignore`. You can turn this off with `require: false`, or skip it per PR with the skip label.

Findings show up as inline annotations on the files and as a short report in the job summary. Every finding says how to fix it.

## Inputs

| Input | Default | What it does |
|---|---|---|
| `require` | `true` | The PR must add a fragment, unless only ignored paths changed. |
| `skip-label` | `skip-changelog` | A PR with this label skips check 3. Checks 1 and 2 always run. |
| `ignore` | *(none)* | Globs, one per line or comma-separated, that never need a fragment. `CHANGELOG.md` and `changelog.d/README.md` are always ignored. |
| `match-number` | `false` | Fragments must be numbered with **this** PR's number. |
| `directory` | `changelog.d` | Where fragments live. |
| `changelog` | `CHANGELOG.md` | The assembled log. |
| `heading` | `## [Unreleased]` | The section fragments fold into. |
| `placeholder-floor` | `0` | Refuse numbers at or above this as placeholders too (`0000` and `9999` are always refused). |
| `base-ref` | PR base, else `main` | The branch being merged into. |
| `head` | PR head SHA | The commit under test. This is the head itself, not the merge commit, which already contains the base. |
| `working-directory` | `.` | The repo root, for monorepos. |
| `python` | `python3` | Any Python 3.9+. Every GitHub-hosted runner already has one, so nothing is installed. |

## Outputs

| Output | |
|---|---|
| `ok` | `"true"` when the PR passes |
| `fragments` | how many fragments the PR adds or changes |

## Design notes

- **It reads git, not files on disk.** Every answer comes from `git show <rev>:<path>`, so whatever is checked out can't change the result.
- **The rules come from the action, not the branch.** The validator runs from the action's own pinned ref, so a PR can't loosen the check in the same diff that would fail it. Pin a tag or SHA for the strictest setup.
- **It fails loudly.** If the base can't be resolved, the step exits `2`. It never reports a green result it couldn't actually compute.
- **Inputs are passed as environment variables**, never pasted into the shell script, so a crafted branch name or label can't inject a command.

!!! note "Private repo"
    While this repo is private, other repos can only use it as an action if you allow that under **Settings → Actions → General → Access**. Once it's public, `uses: cagataycali/changelog.d@<tag>` works anywhere.
