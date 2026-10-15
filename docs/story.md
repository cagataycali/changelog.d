# The story

changelog.d wasn't designed up front. It came out of building [strands-labs/robots](https://github.com/strands-labs/robots), where [Strands Agents](https://strandsagents.com) lanes opened pull requests around the clock and the changelog kept getting in the way.

## Timeline

**#1692 · 2026-07-28: record entries as fragments.** The append-to-`[Unreleased]` habit was costing a re-approval round per PR. In one recorded case, a single merge turned five approved PRs `CONFLICTING`, and `CHANGELOG.md` was the only conflicting file in all of them. Fragments and an assembler fixed that.

**#1785 · 2026-07-30: a gate behind it.** The convention was written down in two places and sixty-seven fragments followed it, but a PR that pasted three entries straight into the log still passed every check. A test can't see a file that was never written, so the gate became a comparison between commits: what did this branch *add*?

**#2163: validate the branch's own fragments.** One PR's only defect was a fragment that began `Fixed:` instead of `### Fixed:`. The check named after the convention passed it, and the failure showed up 20 minutes later as an unrelated-looking test failure. Now the gate runs the assembler's own validator on the files the branch adds, and only those, so a bad fragment already on `main` isn't blamed on someone else.

**#3715 · 2026-09-15: placeholders are refused.** `0000-wip.md` sorts below everything and points to no PR, and once `apply` deletes it, that entry can never be traced back. Now you rename it before it merges.

## What it did

<div class="cd-stat">
  <span class="cd-stat__n">97%</span>
  <span class="cd-stat__t">of commits on <code>main</code> between 2026-07-28 and 2026-10-13 (2,487 of 2,556) carried a fragment. In the same window, no commit edited <code>CHANGELOG.md</code>.</span>
</div>

The rest were reverts, release chores and merges, which is what `skip-changelog` and `ignore` are for.

## What this repo adds

The robots version was scripts in one repo. This repo turns it into something any repo can use:

- `changelog-d`, a CLI you can `pip install`, with `new` so agents don't have to work out slugs.
- A **GitHub Action** with all three checks, where the robots version had only the first two. It adds a *fragment required* check with a skip label and ignore globs, and an optional *number must match the PR* check.
- Settings for the folder, the log file, the section heading and placeholder numbers.
- The same tests, built on real git commits and real merge bases.

<p style="font-family: var(--cd-hand); font-size: 1.8rem; color: var(--cd-orange); margin-top: 2rem;">one file per change. that's the whole trick. ./c²</p>
