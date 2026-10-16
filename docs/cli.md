# Command line

```bash
pip install git+https://github.com/cagataycali/changelog.d
```

It works with Python 3.9 or newer and has no dependencies.

| Command | What it does |
|---|---|
| `changelog-d new 42 Fixed "the login button works on phones"` | Creates a note for PR #42 |
| `changelog-d check` | Checks every note. Changes nothing. |
| `changelog-d print` | Shows what would be added to the changelog |
| `changelog-d apply` | Adds the notes to `CHANGELOG.md` and deletes them |
| `changelog-d gate` | Runs the same check as the GitHub Action, on your machine |

```console
$ changelog-d new 42 Fixed "the login button works on phones"
changelog.d/42-the-login-button-works-on-phones.md

$ changelog-d check
changelog fragments OK (3 pending)

$ changelog-d apply
assembled 3 fragment(s) into CHANGELOG.md:
  43-faster-search.md
  42-the-login-button-works-on-phones.md
  41-dark-mode.md
```

Options for every command: `--dir` (the notes folder), `--changelog` (the changelog file) and `--heading` (the section to add to).
