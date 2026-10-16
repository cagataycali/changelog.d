# Using it with AI agents

changelog.d started in a repo where AI agents opened most of the pull requests, often ten at once. They never had to coordinate over the changelog, because each one wrote its own file.

## Tell your agents

Paste this into your `AGENTS.md` (or system prompt):

```markdown
## Changelog

Every pull request that changes behaviour adds ONE file and never edits CHANGELOG.md:

- Path: `changelog.d/<pr-number>-<short-name>.md`, lowercase words with dashes.
  Open the PR first to get its number.
- Content: one line `### <Kind>: <what changed, in plain words>`, then one or two sentences.
- Check it with `changelog-d check`.
- Nothing a user would notice? Ask for the `skip-changelog` label instead.
```

## The flow that works

1. The agent opens a draft PR, so it knows its number.
2. It runs `changelog-d new <number> Fixed "…"`.
3. It pushes. The check passes and no other agent touched that file.
4. It can rebase whenever it likes. The notes never conflict.

## Why agents especially need the check

An agent only knows what's in its prompt, and prompts get edited. The check holds the rule even when the prompt forgets it. Its error message names the exact file to create, so an agent can read the error, fix it and go green without a person stepping in.
