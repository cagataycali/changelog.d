# For agents

changelog.d was built for repos where agents write most of the PRs. Two lanes that never talk to each other can't collide on the changelog. If an agent forgets the fragment, the gate tells it the exact file to write, so the agent can fix it without a person stepping in.

## Paste this into `AGENTS.md`

```markdown
## Changelog

Every behavioural change adds ONE news fragment and never edits CHANGELOG.md:

- Path: `changelog.d/<pr-number>-<slug>.md` (lowercase slug, words joined by `-`).
  Open the PR first if you need the number; never merge a `0000-` placeholder.
- Content: one `### <Category>: <summary>` heading, then a short paragraph a user
  would understand. Put the measurement in the body.
- One entry per file. No `## ` headings.
- Check locally: `changelog-d check`. The `changelog` CI check enforces it.
- Nothing user-visible changed? Ask for the `skip-changelog` label instead.
```

## The loop that works

1. The agent opens a draft PR first, so it has a number.
2. It runs `changelog-d new <number> <Category> "<summary>" --body "<proof>"`.
3. It pushes. The gate passes, and no other lane touched that path.
4. It rebases whenever it likes. Fragments never conflict, so an approval is never lost to the changelog.

## Why agents need the gate more than people do

People eventually remember the convention. An agent starting from a fresh context only knows what its prompt says, and prompts drift. The gate makes the rule hold anyway: it names the exact file and heading, and the fix clears the error by itself, so an agent can follow the error message and turn the check green without a human.
