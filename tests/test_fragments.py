from __future__ import annotations

from pathlib import Path

import pytest

from changelog_d import fragments as fr
from changelog_d.cli import main


@pytest.fixture
def cfg(tmp_path: Path) -> fr.Config:
    d = tmp_path / "changelog.d"
    d.mkdir()
    (d / "README.md").write_text("docs\n")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n\n### Fixed: old\n\n## [0.1.0]\n")
    return fr.Config(fragment_dir=d, changelog=tmp_path / "CHANGELOG.md")


def args(cfg: fr.Config, *rest: str) -> list[str]:
    return ["--dir", str(cfg.fragment_dir), "--changelog", str(cfg.changelog), *rest]


def test_newest_number_first_and_stable(cfg):
    for n in (3, 12, 7):
        (cfg.fragment_dir / f"{n}-x.md").write_text(f"### Added: {n}\n")
    assert [f.number for f in fr.collect(cfg)] == [12, 7, 3]


def test_a_stray_file_is_a_hard_error_not_a_skip(cfg):
    (cfg.fragment_dir / "notes.txt").write_text("hm")
    assert "not a valid fragment name" in fr.validate(cfg)[0]


def test_apply_folds_verbatim_and_deletes(cfg):
    (cfg.fragment_dir / "5-a.md").write_text("### Added: a\n\nbody a\n")
    (cfg.fragment_dir / "9-b.md").write_text("### Fixed: b\n")
    consumed = fr.apply(cfg)
    assert [f.name for f in consumed] == ["9-b.md", "5-a.md"]
    text = cfg.changelog.read_text()
    assert text.index("### Fixed: b") < text.index("### Added: a") < text.index("### Fixed: old")
    assert sorted(p.name for p in cfg.fragment_dir.iterdir()) == ["README.md"]


def test_apply_is_all_or_nothing(cfg):
    (cfg.fragment_dir / "5-a.md").write_text("### Added: a\n")
    (cfg.fragment_dir / "6-b.md").write_text("no heading\n")
    before = cfg.changelog.read_text()
    with pytest.raises(ValueError):
        fr.apply(cfg)
    assert cfg.changelog.read_text() == before and (cfg.fragment_dir / "5-a.md").exists()


def test_a_missing_anchor_costs_no_fragment(cfg):
    cfg.changelog.write_text("# Changelog\n\n## [Unreleased]\n\n## [Unreleased]\n")
    (cfg.fragment_dir / "5-a.md").write_text("### Added: a\n")
    with pytest.raises(ValueError):
        fr.apply(cfg)
    assert (cfg.fragment_dir / "5-a.md").exists()


def test_new_writes_a_valid_fragment(cfg):
    path = fr.new(42, "Fixed:", "The Robot no longer drifts at 50 Hz!", "Measured.", cfg)
    assert path.name == "42-the-robot-no-longer-drifts-at-50-hz.md"
    assert fr.validate(cfg) == []
    with pytest.raises(FileExistsError):
        fr.new(42, "Fixed", "The Robot no longer drifts at 50 Hz!", config=cfg)
    with pytest.raises(ValueError):
        fr.new(0, "Fixed", "x", config=cfg)


def test_cli_round_trip(cfg, capsys):
    assert main(args(cfg, "new", "7", "Added", "a thing")) == 0
    assert main(args(cfg, "check")) == 0
    assert "1 pending" in capsys.readouterr().out
    assert main(args(cfg, "print")) == 0
    assert "### Added: a thing" in capsys.readouterr().out
    assert main(args(cfg, "apply")) == 0
    assert "### Added: a thing" in cfg.changelog.read_text()


def test_cli_check_fails_on_a_bad_fragment(cfg):
    (cfg.fragment_dir / "0000-wip.md").write_text("### Fixed: x\n")
    assert main(args(cfg, "check")) == 1


def test_a_big_repo_is_not_a_placeholder_unless_it_asks(cfg):
    (cfg.fragment_dir / "12345-big-repo.md").write_text("### Fixed: x\n")
    assert main(args(cfg, "check")) == 0
    assert main(["--placeholder-floor", "9000", *args(cfg, "check")]) == 1


@pytest.mark.parametrize("n, placeholder", [(0, True), (9999, True), (99999, True), (9991, False), (1999, False)])
def test_what_counts_as_a_placeholder(n, placeholder):
    assert fr.Config().is_placeholder(n) is placeholder
