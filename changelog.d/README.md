# changelog.d: news fragments

One file per change. `CHANGELOG.md` is assembled from these at release time
with `changelog-d apply`.

Add `changelog.d/<pr-number>-<slug>.md` holding exactly one
`### <Category>: <summary>` heading followed by a short paragraph:

```markdown
### Fixed: the gate names the file it wants

Measured: ...
```

- `<slug>` is lowercase `a-z0-9` words joined by `-`. `0000-` / `9999-` are placeholders and are refused.
- One `### ` entry per file, no `## ` headings, nothing else in this folder.
- `changelog-d check` validates locally. The `changelog.d` CI check enforces it.

Full rules: https://cagataycali.github.io/changelog.d/fragments/
