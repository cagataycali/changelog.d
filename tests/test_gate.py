"""The gate, replayed as real commits in real repositories.

The question is what a branch *added*, which is a statement about a merge base,
and a merge base is exactly what a hand-built fixture would assume rather than
exercise. So every test here builds one.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from changelog_d import gate
from changelog_d.cli import main

LOG = """# Changelog

## [Unreleased]

### Fixed: a legacy entry from before fragments


### Fixed:

## [0.1.0] - 2026-01-01

### Added: the beginning
"""


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def write(repo: Path, path: str, text: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def commit(repo: Path, message: str) -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    r.mkdir()
    git(r, "init", "-q", "-b", "main")
    git(r, "config", "user.email", "t@example.com")
    git(r, "config", "user.name", "t")
    write(r, "CHANGELOG.md", LOG)
    write(r, "changelog.d/README.md", "docs\n")
    write(r, "changelog.d/10-already-here.md", "### Added: something already pending\n")
    write(r, "src/app.py", "x = 1\n")
    commit(r, "base")
    git(r, "checkout", "-q", "-b", "feature")
    return r


def verdict(repo: Path, **kw):
    return gate.run(base_ref="main", repo=repo, **kw)


def test_a_fragment_passes(repo):
    write(repo, "src/app.py", "x = 2\n")
    write(repo, "changelog.d/42-x-is-two.md", "### Changed: x is two\n\nBecause.\n")
    commit(repo, "change")
    v = verdict(repo)
    assert v.ok and v.new_fragments == ["changelog.d/42-x-is-two.md"]


def test_a_direct_append_is_refused_and_named(repo):
    write(repo, "CHANGELOG.md", LOG.replace("## [Unreleased]\n", "## [Unreleased]\n\n### Fixed: sneaky\n"))
    commit(repo, "append")
    v = verdict(repo, require=False)
    assert not v.ok and v.unaccounted == ["### Fixed: sneaky"]


def test_the_remedy_it_asks_for_clears_it(repo):
    write(repo, "CHANGELOG.md", LOG.replace("## [Unreleased]\n", "## [Unreleased]\n\n### Fixed: sneaky\n"))
    commit(repo, "append")
    write(repo, "CHANGELOG.md", LOG)
    write(repo, "changelog.d/43-sneaky.md", "### Fixed: sneaky\n")
    commit(repo, "move it")
    assert verdict(repo).ok


def test_a_third_copy_of_a_bare_heading_is_seen(repo):
    write(repo, "CHANGELOG.md", LOG.replace("### Fixed:\n", "### Fixed:\n\n### Fixed:\n"))
    commit(repo, "dup")
    assert verdict(repo, require=False).unaccounted == ["### Fixed:"]


def test_a_release_is_accounted_for_entry_by_entry(repo):
    assert main(["--dir", str(repo / "changelog.d"), "--changelog", str(repo / "CHANGELOG.md"), "apply"]) == 0
    commit(repo, "release")
    v = verdict(repo)
    assert v.ok and v.accounted == ["### Added: something already pending"]


def test_a_release_that_also_hand_writes_one_is_refused_for_that_one(repo):
    main(["--dir", str(repo / "changelog.d"), "--changelog", str(repo / "CHANGELOG.md"), "apply"])
    text = (repo / "CHANGELOG.md").read_text().replace("## [Unreleased]\n", "## [Unreleased]\n\n### Fixed: extra\n")
    write(repo, "CHANGELOG.md", text)
    commit(repo, "release + extra")
    v = verdict(repo)
    assert v.unaccounted == ["### Fixed: extra"] and v.accounted == ["### Added: something already pending"]


def test_editing_or_collapsing_the_log_is_quiet(repo):
    text = LOG.replace("a legacy entry", "an old entry, reworded").replace(
        "## [Unreleased]\n", "## [Unreleased]\n\n## [0.2.0] - 2026-02-02\n"
    )
    write(repo, "CHANGELOG.md", text)
    commit(repo, "bookkeeping")
    assert verdict(repo).ok


def test_a_code_change_without_a_fragment_is_missing(repo):
    write(repo, "src/app.py", "x = 3\n")
    commit(repo, "no fragment")
    v = verdict(repo)
    assert v.missing and not v.ok
    assert "adds no fragment" in gate.report(v)


def test_the_skip_label_and_ignore_globs_excuse_it(repo):
    write(repo, "docs/page.md", "hi\n")
    commit(repo, "docs only")
    assert verdict(repo, ignore=["docs/**"]).ok
    write(repo, "src/app.py", "x = 4\n")
    commit(repo, "code")
    assert not verdict(repo, ignore=["docs/**"]).ok
    assert verdict(repo, ignore=["docs/**"], skip=True).ok


@pytest.mark.parametrize(
    "name, body, needle",
    [
        ("44-ok.md", "Fixed: no hashes\n", "level-3 entry heading"),
        ("0000-ok.md", "### Fixed: x\n", "placeholder"),
        ("9999-ok.md", "### Fixed: x\n", "placeholder"),
        ("44-Bad_Name.md", "### Fixed: x\n", "not a valid fragment name"),
        ("44-two.md", "### Fixed: a\n\n### Fixed: b\n", "one '### ' entry"),
        ("44-forge.md", "### Fixed: a\n\n## [9.9.9]\n", "level-2 heading"),
    ],
)
def test_a_bad_fragment_on_the_branch_is_named(repo, name, body, needle):
    write(repo, f"changelog.d/{name}", body)
    commit(repo, "bad")
    v = verdict(repo)
    assert not v.ok and any(needle in p for _, p in v.problems), v.problems


def test_a_bad_fragment_already_on_the_base_is_not_this_branchs(repo):
    git(repo, "checkout", "-q", "main")
    write(repo, "changelog.d/11-broken.md", "no heading\n")
    commit(repo, "broken on main")
    git(repo, "checkout", "-q", "feature")
    git(repo, "merge", "-q", "main", "-m", "sync")
    write(repo, "changelog.d/45-fine.md", "### Fixed: fine\n")
    commit(repo, "mine")
    assert verdict(repo).ok


def test_match_number_ties_the_fragment_to_the_pr(repo):
    write(repo, "changelog.d/46-x.md", "### Fixed: x\n")
    commit(repo, "x")
    assert verdict(repo, pr_number=46, match_number=True).ok
    assert not verdict(repo, pr_number=47, match_number=True).ok


def test_the_verdict_reads_git_not_the_working_tree(repo):
    write(repo, "changelog.d/48-x.md", "### Fixed: x\n")
    commit(repo, "x")
    write(repo, "changelog.d/48-x.md", "broken in the working tree only\n")
    assert verdict(repo).ok


def test_an_unreachable_base_is_loud(repo):
    with pytest.raises(gate.GitError):
        gate.run(base_ref="nope", repo=repo)
    assert main(["gate", "--base-ref", "nope", "--repo", str(repo), "--summary", ""]) == 2
