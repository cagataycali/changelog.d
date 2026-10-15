<p align="center">
  <img src="docs/assets/mark.svg" width="88" alt="changelog.d">
</p>

<h1 align="center">changelog.d</h1>

<p align="center"><b>Every change gets its own file.</b><br>
Parallel pull requests, and the agents opening them, never conflict on <code>CHANGELOG.md</code> again.</p>

<p align="center">
  <a href="https://cagataycali.github.io/changelog.d/">Docs</a> ·
  <a href="#the-action">Action</a> ·
  <a href="#the-cli">CLI</a> ·
  <a href="https://cagataycali.github.io/changelog.d/agents/">For agents</a> ·
  <a href="https://cagataycali.github.io/changelog.d/story/">The story</a>
</p>

---

Every PR that appends to `## [Unreleased]` edits **the same lines**. Merge one and every other open PR conflicts: on ordering, never on meaning. Rebase, push, lose the approval, wait for a second review. With ten agents opening PRs in parallel, the changelog becomes the bottleneck for the whole repo.

`merge=union` doesn't help, because GitHub doesn't run merge drivers when it computes mergeability.

**changelog.d** gives each change its own file:

```text
changelog.d/
├── 41-fixed-the-gripper-reports-millimetres.md
├── 42-the-arm-stops-in-10-ms-not-400.md
└── 43-docs-a-quickstart-that-runs.md
```

```markdown
### Fixed: the arm stops in 10 ms, not 400

Measured on a real SO-101.
```

No two PRs touch the same path, so there's nothing to merge. At release, `changelog-d apply` folds them into `CHANGELOG.md` and deletes them.

Built and tested on [strands-labs/robots](https://github.com/strands-labs/robots): in the 11 weeks after the convention landed, **2,487 of 2,556 commits** on `main` carried a fragment and **zero** edited the changelog by hand.

## The action

```yaml
# .github/workflows/changelog.yml
name: changelog
on:
  pull_request:
    types: [opened, synchronize, reopened, labeled, unlabeled]
jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: cagataycali/changelog.d@main
        with:
          ignore: |
            docs/**
            *.md
```

It runs three checks, all read from git objects and never from the working tree:

1. **Nothing was written straight into `[Unreleased]`.** A release PR passes entry by entry: each new entry must match a fragment deleted in the same diff.
2. **The PR's own fragments are valid:** a real PR number (no `0000-`), one `### ` heading, and no forged `## ` version.
3. **A fragment exists** when code changed. Skip it with the `skip-changelog` label or the `ignore` globs.

| Input | Default | |
|---|---|---|
| `require` | `true` | the PR must add a fragment |
| `skip-label` | `skip-changelog` | waives check 3 only |
| `ignore` | | globs that never need a fragment |
| `match-number` | `false` | fragments must use this PR's number |
| `directory` / `changelog` / `heading` | `changelog.d` / `CHANGELOG.md` / `## [Unreleased]` | layout |
| `placeholder-floor` | `0` | also refuse numbers ≥ this |

Outputs: `ok`, `fragments`. Full reference: [docs/action](https://cagataycali.github.io/changelog.d/action/).

## The CLI

```bash
pip install git+https://github.com/cagataycali/changelog.d

changelog-d new 42 Fixed "the arm stops in 10 ms, not 400"   # write a fragment
changelog-d check                                            # validate all
changelog-d print                                            # preview [Unreleased]
changelog-d apply                                            # fold into CHANGELOG.md, delete
changelog-d gate --base-ref main                             # the action, locally
```

It's pure Python 3.9+ with no dependencies.

## For agents

Paste this into your `AGENTS.md`:

```markdown
Every behavioural change adds ONE `changelog.d/<pr-number>-<slug>.md` holding a single
`### <Category>: <summary>` heading and a short body, and never edits CHANGELOG.md.
Run `changelog-d check`. Nothing user-visible? Ask for the `skip-changelog` label.
```

## Develop

```bash
pip install -e '.[dev,docs]'
pytest -q                 # tests replayed as real commits in real repos
mkdocs serve              # the landing page
```

This repo uses its own convention: every PR adds a fragment to [`changelog.d/`](changelog.d/).

## License

Apache-2.0 · made by [./c²](https://github.com/cagataycali)
