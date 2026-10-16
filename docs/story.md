# The story

changelog.d wasn't planned. It grew out of building [strands-labs/robots](https://github.com/strands-labs/robots), where [Strands Agents](https://strandsagents.com) opened pull requests around the clock and the changelog kept getting in the way.

**July 2026: the pain.** In one case, a single merge broke five pull requests that were already approved, and `CHANGELOG.md` was the only conflict in all five. The repo switched to one note per change ([#1692](https://github.com/strands-labs/robots/pull/1692)).

**Two days later: the check.** The rule was written down, but nothing enforced it. A pull request that pasted entries straight into the changelog still passed. So the check was added ([#1785](https://github.com/strands-labs/robots/pull/1785)).

**Then: catching typos early.** One note started with `Fixed:` instead of `### Fixed:`. The check now reads each pull request's own notes, so a mistake like that shows up in seconds instead of 20 minutes later as a confusing test failure ([#2163](https://github.com/strands-labs/robots/issues/2163)).

**September: no made-up numbers.** A note named `0000-wip.md` points to no pull request, so after release nobody can tell where it came from. Those are now refused ([#3715](https://github.com/strands-labs/robots/pull/3715)).

<div class="cd-stat">
  <span class="cd-stat__n">97%</span>
  <p class="cd-stat__t">of commits on <code>main</code> from July 28 to October 13, 2026 (<b>2,487 of 2,556</b>) carried a note.
  <b>None</b> edited <code>CHANGELOG.md</code> by hand. The rest were reverts and chores.</p>
</div>

## What this repo adds

The robots version was a few scripts inside one project. This repo makes it usable in any repo:

- a command line tool you can `pip install`, including `new` so nobody has to make up file names
- a GitHub Action with all three checks, plus a skip label and ignore patterns
- settings for the folder, the file and the section name
- tests that use real git history

<p style="font-family: var(--cd-hand); font-size: 1.8rem; color: var(--cd-accent); margin-top: 2rem;">one file per change. that's the whole trick. ./c²</p>
