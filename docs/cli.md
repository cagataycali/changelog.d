# CLI

```bash
pip install git+https://github.com/cagataycali/changelog.d
```

It's pure Python 3.9+ with no dependencies. `python -m changelog_d` works too.

| Command | |
|---|---|
| `changelog-d check` | Validate every fragment. Writes nothing. Exits `1` on any problem. |
| `changelog-d print` | Print the `[Unreleased]` body the fragments would become. |
| `changelog-d apply` | Fold them into `CHANGELOG.md` and delete them. All or nothing. |
| `changelog-d new <n> <Category> "<summary>" [--body …]` | Write `changelog.d/<n>-<slug>.md`. Refuses to overwrite. |
| `changelog-d gate --base-ref main` | Run the PR gate locally, exactly as the action does. |

Global flags: `--dir`, `--changelog`, `--heading`, `--placeholder-floor`.

```console
$ changelog-d new 42 Fixed "the arm stops in 10 ms, not 400"
changelog.d/42-the-arm-stops-in-10-ms-not-400.md

$ changelog-d check
changelog fragments OK (3 pending)

$ changelog-d gate --base-ref main --ignore "docs/**"
## changelog.d

Base `main` · merge base `5d29a6dfe1c2`

✅ 1 fragment(s), all valid:

- `changelog.d/42-the-arm-stops-in-10-ms-not-400.md`
```

Exit codes: `0` means OK, `1` means there's a finding, and `2` means the check couldn't run (for example, an unknown base ref or a shallow clone with no merge base).
