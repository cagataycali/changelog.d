"""Read, validate and assemble ``changelog.d/`` news fragments.

Why this exists
---------------
When every pull request appends its entry to the top of ``## [Unreleased]`` in
``CHANGELOG.md``, every branch inserts at the *same anchor*. Any two open at
once conflict the moment either merges: on ordering alone, never on meaning.
Where stale approvals are dismissed on push, clearing that conflict costs a
full re-review per affected PR, and the cost grows with the number of open PRs.
That is the normal state of a repository driven by many agents in parallel.

``merge=union`` does not fix it: GitHub's mergeability check does not run merge
drivers, so the PR still says ``CONFLICTING``.

A fragment makes the conflict structurally impossible. Each PR adds its own file
under ``changelog.d/``, no two PRs touch the same path, and there is nothing to
reconcile. This module is the release-time half of that bargain: it validates
the accumulated fragments and folds them into ``[Unreleased]``.

Fragment contract
-----------------
- Path: ``changelog.d/<number>-<slug>.md``. ``<number>`` is the PR (or issue)
  number; ``<slug>`` is lowercase ``a-z0-9`` words joined by ``-``. ``0000-``
  and all-nines (``9999-``) are placeholders and are refused, as is anything
  ``>= placeholder_floor`` when one is set: the number is the only pointer from
  the release note back to the change, and ``apply`` deletes the fragment.
- Content: exactly the Markdown that would have gone into ``CHANGELOG.md``:
  one ``### <Category>: <summary>`` heading, then prose.
- No level-2 (``## ``) heading: that would forge a version section.
- Anything else in the directory is a hard error, never a skip. A fragment that
  is silently ignored is a change that never reaches the log.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

#: Files in the fragment directory that document it rather than record a change.
RESERVED_NAMES = frozenset({"README.md"})

FRAGMENT_NAME = re.compile(r"^(?P<number>\d+)-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$")

#: A fragment opens with a level-3 entry heading. The category wording
#: (``Fixed``, ``Added``, ``Docs``...) is not policed: structure, not taxonomy.
FRAGMENT_HEADING = re.compile(r"^### \S")

#: Two blank lines separate sibling entries, like a hand-written log.
ENTRY_SEPARATOR = "\n\n\n"


@dataclass(frozen=True)
class Config:
    """Where the fragments live and what the log looks like."""

    fragment_dir: Path = Path("changelog.d")
    changelog: Path = Path("CHANGELOG.md")
    unreleased_heading: str = "## [Unreleased]"
    #: Numbers at or above this are placeholders too (0 = off). strands-robots
    #: uses 9000 while its PR counter is in the 4000s.
    placeholder_floor: int = 0
    reserved_names: frozenset[str] = field(default_factory=lambda: RESERVED_NAMES)

    def is_placeholder(self, number: int) -> bool:
        """True when ``number`` is a pre-PR placeholder, not a PR or issue number."""
        if number == 0 or (number >= 999 and set(str(number)) == {"9"}):
            return True
        return self.placeholder_floor > 0 and number >= self.placeholder_floor


#: The conventional layout; every function takes a ``Config`` to override it.
DEFAULT = Config()


@dataclass(frozen=True)
class Fragment:
    """One pending changelog entry."""

    path: Path
    number: int
    body: str

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def heading(self) -> str | None:
        """The entry heading (first non-blank line), or ``None`` if it has none."""
        return entry_heading(self.body)


def entry_heading(text: str) -> str | None:
    for line in text.splitlines():
        if line.strip():
            return line.rstrip() if line.startswith("### ") else None
    return None


def parse_name(name: str) -> int | None:
    """Return the number in a valid fragment file name, else ``None``."""
    match = FRAGMENT_NAME.match(name)
    return int(match.group("number")) if match else None


def bad_name(name: str) -> str:
    return f"{name}: not a valid fragment name - expected '<number>-<slug>.md' (lowercase slug, words joined by '-')"


def is_fragment_candidate(name: str, config: Config) -> bool:
    """False for files the directory may hold that are not fragments."""
    return name not in config.reserved_names and not name.startswith(".")


def collect(config: Config = DEFAULT) -> list[Fragment]:
    """Every fragment, newest number first, then by name (stable across machines).

    Raises:
        ValueError: on a file that is neither reserved nor a validly named fragment.
    """
    directory = config.fragment_dir
    if not directory.is_dir():
        return []
    fragments: list[Fragment] = []
    for path in sorted(directory.iterdir()):
        if not is_fragment_candidate(path.name, config):
            continue
        if not path.is_file():
            raise ValueError(f"{path}: the fragment directory must hold files only")
        number = parse_name(path.name)
        if number is None:
            raise ValueError(bad_name(path.name))
        fragments.append(Fragment(path=path, number=number, body=path.read_text(encoding="utf-8")))
    fragments.sort(key=lambda f: (-f.number, f.name))
    return fragments


def validate_fragment(fragment: Fragment, config: Config = DEFAULT) -> list[str]:
    """Every contract violation in one fragment (empty when valid)."""
    problems: list[str] = []
    if config.is_placeholder(fragment.number):
        problems.append(
            f"{fragment.name}: {fragment.number} is a placeholder, not a PR or issue number - "
            "rename the fragment to the number of the change that carries it"
        )
    lines = fragment.body.splitlines()
    content = [line for line in lines if line.strip()]
    if not content:
        problems.append(f"{fragment.name}: fragment is empty")
        return problems
    if not FRAGMENT_HEADING.match(content[0]):
        problems.append(
            f"{fragment.name}: first line must be a level-3 entry heading "
            f"('### <Category>: <summary>'), got {content[0]!r}"
        )
    for line in lines:
        if line.startswith("## "):
            problems.append(
                f"{fragment.name}: fragment may not contain a level-2 heading ({line!r}) - "
                "that would forge a version section"
            )
            break
    if sum(1 for line in lines if line.startswith("### ")) > 1:
        problems.append(f"{fragment.name}: one '### ' entry per fragment - split the others into their own files")
    return problems


def validate(config: Config = DEFAULT) -> list[str]:
    """Every contract violation across the fragment directory."""
    try:
        fragments = collect(config)
    except ValueError as exc:
        return [str(exc)]
    return [problem for fragment in fragments for problem in validate_fragment(fragment, config)]


def render(fragments: list[Fragment]) -> str:
    """The fragments as the body of an ``[Unreleased]`` section, verbatim."""
    return ENTRY_SEPARATOR.join(f.body.strip("\n") for f in fragments)


def insert(changelog_text: str, rendered: str, heading: str = Config.unreleased_heading) -> str:
    """``changelog_text`` with ``rendered`` at the top of its ``[Unreleased]`` section.

    Raises:
        ValueError: unless the log holds exactly one ``[Unreleased]`` heading.
    """
    if not rendered:
        return changelog_text
    lines = changelog_text.splitlines()
    anchors = [i for i, line in enumerate(lines) if line.strip() == heading]
    if len(anchors) != 1:
        raise ValueError(f"{Config.changelog} must hold exactly one '{heading}' heading, found {len(anchors)}")
    anchor = anchors[0]
    tail = lines[anchor + 1 :]
    while tail and not tail[0].strip():
        tail.pop(0)
    head = "\n".join(lines[: anchor + 1])
    rest = "\n".join(tail).strip("\n")
    out = f"{head}\n\n{rendered.strip(chr(10))}"
    if rest:
        out += ENTRY_SEPARATOR + rest
    return out + "\n"


def apply(config: Config = DEFAULT) -> list[Fragment]:
    """Fold every fragment into the log and delete it. All or nothing.

    Validation runs first and the new text is computed before anything is
    written, so a bad fragment or a missing anchor never costs a deleted file.
    """
    problems = validate(config)
    if problems:
        raise ValueError("refusing to assemble - invalid fragment(s):\n  " + "\n  ".join(problems))
    fragments = collect(config)
    if not fragments:
        return []
    text = config.changelog.read_text(encoding="utf-8") if config.changelog.exists() else ""
    if config.unreleased_heading not in text.splitlines():
        text = f"# Changelog\n\n{config.unreleased_heading}\n" if not text.strip() else text
    updated = insert(text, render(fragments), config.unreleased_heading)
    config.changelog.write_text(updated, encoding="utf-8")
    for fragment in fragments:
        fragment.path.unlink()
    return fragments


def slugify(text: str, limit: int = 60) -> str:
    """A fragment slug from a summary: lowercase words joined by ``-``."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    slug = ""
    for word in words:
        candidate = f"{slug}-{word}" if slug else word
        if len(candidate) > limit:
            break
        slug = candidate
    return slug or "change"


def new(number: int, category: str, summary: str, body: str = "", config: Config = DEFAULT) -> Path:
    """Write a new fragment and return its path. Refuses to overwrite."""
    if config.is_placeholder(number):
        raise ValueError(f"{number} is a placeholder - use the PR or issue number")
    path = config.fragment_dir / f"{number}-{slugify(summary)}.md"
    if path.exists():
        raise FileExistsError(f"{path} already exists")
    config.fragment_dir.mkdir(parents=True, exist_ok=True)
    text = f"### {category.strip().rstrip(':')}: {summary.strip()}\n"
    if body.strip():
        text += f"\n{body.strip()}\n"
    path.write_text(text, encoding="utf-8")
    return path
