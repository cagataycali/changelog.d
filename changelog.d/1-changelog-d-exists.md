### Added: changelog.d as a CLI and a GitHub Action

The news-fragment convention from strands-labs/robots, packaged for any repo:
`changelog-d new/check/print/apply/gate` and a composite action that refuses
entries written straight into `[Unreleased]`, validates the pull request's own
fragments, and requires one when code changed (skip label and ignore globs
included). 33 tests; the gate ones replay real commits in real repositories.
