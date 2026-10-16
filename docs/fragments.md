# Writing a note

A note (some tools call it a *fragment*) is a tiny Markdown file: one heading and a sentence or two.

```markdown title="changelog.d/42-login-button-on-phones.md"
### Fixed: the login button works on phones

It was hidden behind the cookie banner on small screens.
```

That's the whole thing.

## The rules

1. **Name it after the pull request.** For example `42-login-button-on-phones.md`. The number points back to PR #42 and keeps the notes in order. Use lowercase words with dashes.
2. **Use the real number.** Names like `0000-wip.md` or `9999-…` are refused, so rename the file once your PR has a number.
3. **Start with a `### ` heading,** like `### Added: dark mode`. That line becomes the entry in the changelog. The word before the colon is up to you: Added, Fixed, Changed, Docs…
4. **One change per file.** Two changes means two files.
5. **No `## ` headings.** Those are kept for version numbers.
6. **Only notes in the folder.** A stray `notes.txt` is an error, so nothing gets lost quietly. A `README.md` is fine.

## Making one

=== "With the CLI"

    ```bash
    changelog-d new 42 Fixed "the login button works on phones"
    # → changelog.d/42-the-login-button-works-on-phones.md
    ```

=== "By hand"

    Create `changelog.d/42-login-button.md` and write:

    ```markdown
    ### Fixed: the login button works on phones
    ```

## Good notes

- **Write for the user, not for the code.** "Search is twice as fast" beats "refactor query builder".
- **Keep it short.** One heading and a sentence is normal.
- **Add a detail if it helps,** such as a number, a before and after, or which screen.

| 👎 | 👍 |
|---|---|
| `### Fixed: bug` | `### Fixed: saving a draft no longer logs you out` |
| `### Changed: update deps` | `### Changed: needs Python 3.10 or newer` |

## At release time

```bash
changelog-d check    # are all the notes OK?
changelog-d print    # preview what will be added
changelog-d apply    # add them to CHANGELOG.md and delete the files
```

`apply` is all or nothing: if any note has a problem, it changes nothing.
