# The fragment

A fragment is the exact Markdown you would have pasted into `CHANGELOG.md`, saved as its own file.

```markdown title="changelog.d/1692-teleop-slew-bound.md"
### Fixed: a teleop command a joint cannot travel that fast is refused

`apply_input_frame` bounded frame rate and magnitude but not rate of change,
so a replayed stream could command a full reversal every frame. It now caps
the per-frame delta at the joint's velocity limit.
```

## The rules

| Rule | Why |
|---|---|
| Name it `<number>-<slug>.md` | `<number>` is the PR (or issue). It's the only link from the release note back to the change, and it sets the order in the log. |
| The slug is lowercase `a-z0-9` words joined by `-` | So names sort and read the same on every machine. |
| `0000-…` and `9999-…` are refused | Those are placeholders. Rename the file once the PR exists. |
| The first line is a `### ` heading | That's the entry. The category wording (`Fixed`, `Added`, `Docs`, `Security`…) is up to you. Only the structure is checked. |
| Exactly one `### ` per file | Two changes means two files. |
| No `## ` headings | A level-2 heading would create a fake version section. |
| Nothing else lives in the folder | A stray `notes.txt` or a misnamed `.md` is an **error**, not a skip. If a file were silently skipped, its entry would never reach the log. |

`README.md` and dotfiles are allowed in the folder.

## Writing one

=== "CLI"

    ```bash
    changelog-d new 42 Fixed "the arm stops in 10 ms, not 400" --body "Measured on a real SO-101."
    # → changelog.d/42-the-arm-stops-in-10-ms-not-400.md
    ```

=== "By hand"

    ```bash
    cat > changelog.d/42-arm-stops-fast.md <<'MD'
    ### Fixed: the arm stops in 10 ms, not 400

    Measured on a real SO-101.
    MD
    ```

## Good fragments

- **Say what a user would notice**, not what you refactored. "The arm stops in 10 ms" beats "refactor estop path".
- **Put the proof in the body:** a number, a before and after, or the command you ran.
- **Keep it short.** One heading and a short paragraph is normal.

## At release time

```bash
changelog-d check    # every fragment valid?
changelog-d print    # preview the [Unreleased] body
changelog-d apply    # fold into CHANGELOG.md, delete the fragments
```

`apply` is all or nothing. It validates every fragment and works out the new log *before* it writes anything, so a bad fragment or a missing `## [Unreleased]` heading never leaves you with a half-written log or a deleted file. The release PR then passes the gate, because each new entry is matched to a fragment deleted in the same diff.
