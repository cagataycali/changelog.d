# Why one file per change

## The line everyone fights over

A normal changelog has one place to write: the top of `## [Unreleased]`. So every pull request edits the same few lines.

Open three PRs and merge one. The other two now conflict with `main`. Nothing about their *meaning* clashes; the only problem is the order of the lines. You still have to rebase, push again, and on most protected repos that push throws away the approval. One merge turned **five** approved PRs `CONFLICTING` on strands-labs/robots, and `CHANGELOG.md` was the only file in conflict on all five.

Every new open PR makes it worse. With one person that's annoying. With a dozen agents working in parallel, the changelog becomes the bottleneck for the whole repo.

## Why `merge=union` doesn't save you

It's the first thing everyone tries. A union merge driver does resolve the lines locally, but **GitHub doesn't run merge drivers** when it decides whether a PR can merge. The PR still says `CONFLICTING`, the button stays grey, and the push that fixes it still dismisses the approval.

## The fix is boring, so it holds

Give each change its own file:

```text
changelog.d/
├── README.md
├── 41-fixed-the-gripper-reports-millimetres.md
├── 42-the-arm-stops-in-10-ms-not-400.md
└── 43-docs-a-quickstart-that-runs.md
```

No two PRs touch the same path, so there's nothing to merge. At release you run `changelog-d apply`, which writes the entries into `CHANGELOG.md` (newest PR first) and deletes the files.

`CHANGELOG.md` is still the log people read. You still edit it by hand for release bookkeeping, such as turning `[Unreleased]` into `## [1.2.0] - 2026-10-15`. You just never append to it from a feature branch.

## Why a gate, not a promise

The convention is easy to write in a README. On the repo where it started, the README and `AGENTS.md` both stated it, sixty-seven fragments followed it, and **nothing enforced it**. A PR with three entries pasted straight under `[Unreleased]` passed every check.

A test can't catch that, because a fragment that was never written leaves nothing to inspect. And an old `[Unreleased]` can already hold hundreds of hand-written entries, so you can't just assert "this section is empty".

The mistake is the *act* of adding to the log, and you can only see an act by comparing two commits. So the gate compares the merge base with the PR head:

- **Old entries** appear on both sides and cancel out.
- **A new entry** is refused, unless a fragment was *deleted in the same diff* with exactly that heading. That's what a release looks like, and it's checked entry by entry.
- **Copies count.** Two `### Fixed:` headings plus a third is still an addition.
- **Edits are fine.** Rewording, reordering or collapsing the section adds no new heading, so the gate stays quiet.

Each fix also makes the error go away by itself. Move the entry into a fragment, fix the heading or rename the file, and the next run is green. There's no override to argue about.

## Who it's for

- **Repos with a lot of open PRs.** This is the problem it was built to remove.
- **Agent-driven repos.** The lanes don't have to coordinate, and an agent can't break the rule without being told exactly which file to write. [For agents →](agents.md)
- **Anyone who wants a changelog that's actually up to date.** Writing the entry is part of the PR, so it doesn't get forgotten.
