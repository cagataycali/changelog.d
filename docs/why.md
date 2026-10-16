# Why one file per change

## The usual way breaks

A changelog is a list of what changed in each release, newest at the top:

```markdown
## [Unreleased]

### Added: dark mode
### Fixed: the login button works on phones
```

The usual rule is "add your line under `[Unreleased]`". The trouble is that **everyone adds to the same spot**.

Say three people open pull requests on Monday, and each adds a line in that spot. On Tuesday one gets merged. Git now sees the other two editing lines that just changed, and calls it a **conflict**. Nothing is really wrong, since the three changes have nothing to do with each other, but someone still has to fix it by hand, push again and often ask for another review.

With three pull requests that's annoying. With thirty, or with AI agents opening them all day, it's most of the job.

## The fix

Give every change **its own file**:

```text
changelog.d/
├── 41-dark-mode.md
├── 42-login-button-on-phones.md
└── 43-faster-search.md
```

Two pull requests never touch the same file, so they can't conflict. When you release, `changelog-d apply` copies every note into `CHANGELOG.md` (newest first) and deletes the files.

<div class="cd-aside" markdown>
**Why not let git merge the lines automatically?** You can tell git to keep both sides (`merge=union`), but GitHub ignores that when it decides whether a pull request can merge. The button stays grey.
</div>

## Why a check, and not just a rule

Writing "please add a note" in the README isn't enough. People forget, and so do agents. The GitHub Action checks every pull request for three things:

1. **No one edited `CHANGELOG.md` directly.** Only new entries count, so fixing a typo in an old entry is fine. Release pull requests are fine too.
2. **The note is written correctly:** a real PR number, and a heading that starts with `###`.
3. **There is a note at all**, if the pull request changes code. Docs-only changes, or anything labelled `skip-changelog`, can skip it.

Every error says exactly how to fix it, and once you fix it, the check passes. There's nothing to override.

## Who it's for

- Repos with lots of open pull requests at once
- Repos where AI agents write a lot of the code ([more on that](agents.md))
- Anyone who wants a changelog that's actually up to date, because writing the note is part of the pull request
