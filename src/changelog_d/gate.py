"""The pull-request gate: did this branch record its change the changelog.d way?

Three questions, all answered from git objects (``git show <rev>:<path>``),
never from the working tree, so the verdict cannot depend on what is checked out.

1. **Did it write into the log?** Compare the ``### `` headings under
   ``[Unreleased]`` at the merge base with the same set at the head. Legacy
   entries appear on both sides and cancel; only additions are left. An addition
   is excused only by a fragment *deleted in the same diff* whose heading it is,
   which is exactly what ``changelog-d apply`` produces at release time. This is
   checked per entry, so a release PR that also hand-writes one is still refused,
   for that one only. Multiset arithmetic, so a third copy of an existing bare
   ``### Fixed:`` is still seen.
2. **Are its fragments valid?** Only the fragments the branch adds or modifies
   are judged, with the same validator ``changelog-d check`` uses. A bad fragment
   already on the base is not this branch's to fix.
3. **Did it add one at all?** (``require``, on by default.) A branch that changes
   anything outside the ignored paths must add at least one fragment, unless the
   PR carries the skip label.

Why a base diff and not a test: an old ``[Unreleased]`` may already hold
hundreds of hand-written entries, so no static assertion about its contents can
hold. What is wrong is the *act* of adding to it, and an act is only visible as
the difference between two commits.

Every remedy is self-clearing: move the entry into a fragment, fix the
heading, rename the file, or add one. No override is needed.
"""

from __future__ import annotations

import fnmatch
import subprocess
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from . import fragments as fr


class GitError(RuntimeError):
    """A git call the gate depends on failed. Loud on purpose: a gate that cannot
    reach the base must not report the reassuring answer."""


def _git(*args: str, repo: Path | None = None) -> str:
    command = ["git"] + (["-C", str(repo)] if repo else []) + list(args)
    done = subprocess.run(command, capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise GitError(f"{' '.join(command)} exited {done.returncode}: {done.stderr.strip()}")
    return done.stdout


def resolve_base(ref: str, repo: Path | None = None) -> str:
    """``origin/<ref>`` when it exists (a CI checkout has no local base branch), else ``<ref>``."""
    for candidate in (f"origin/{ref}", ref):
        try:
            _git("rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}", repo=repo)
            return candidate
        except GitError:
            continue
    raise GitError(f"cannot resolve base ref {ref!r} as 'origin/{ref}' or '{ref}' - fetch it first (fetch-depth: 0)")


def merge_base(base: str, head: str, repo: Path | None = None) -> str:
    sha = _git("merge-base", base, head, repo=repo).strip()
    if not sha:
        raise GitError(f"no merge base between {base!r} and {head!r} - is the clone shallow?")
    return sha


def file_at(rev: str, path: str, repo: Path | None = None) -> str:
    """A file at a revision, or ``""`` when it does not exist there."""
    try:
        return _git("show", f"{rev}:{path}", repo=repo)
    except GitError:
        return ""


def changed_paths(start: str, end: str, flt: str, pathspec: str | None = None, repo: Path | None = None) -> list[str]:
    """Paths changed between two commits. ``--no-renames``: a renamed fragment is
    a delete plus an add, so it neither counts as consumed nor dodges the name rule."""
    args = ["diff", "--name-only", "--no-renames", f"--diff-filter={flt}", f"{start}..{end}"]
    if pathspec:
        args += ["--", pathspec]
    return [line for line in _git(*args, repo=repo).splitlines() if line]


def unreleased_entries(text: str, heading: str) -> list[str]:
    """``### `` headings under ``[Unreleased]``, stopping at the next ``## ``."""
    entries, inside = [], False
    for line in text.splitlines():
        if line.strip() == heading:
            inside = True
            continue
        if inside and line.startswith("## "):
            break
        if inside and line.startswith("### "):
            entries.append(line.rstrip())
    return entries


def surplus(more: Iterable[str], less: Iterable[str]) -> list[str]:
    """Multiset difference, sorted for a reproducible report."""
    return sorted((Counter(more) - Counter(less)).elements())


@dataclass
class Verdict:
    base_ref: str
    merge_base: str
    added: list[str] = field(default_factory=list)
    accounted: list[str] = field(default_factory=list)
    unaccounted: list[str] = field(default_factory=list)
    problems: list[tuple[str, str]] = field(default_factory=list)
    new_fragments: list[str] = field(default_factory=list)
    missing: bool = False
    skipped_reason: str = ""

    @property
    def ok(self) -> bool:
        return not (self.unaccounted or self.problems or self.missing)


def _ignored(path: str, patterns: Sequence[str]) -> bool:
    p = PurePosixPath(path)
    return any(fnmatch.fnmatch(path, pat) or p.match(pat) for pat in patterns)


def run(
    *,
    base_ref: str = "main",
    head: str = "HEAD",
    repo: Path | None = None,
    config: fr.Config = fr.DEFAULT,
    require: bool = True,
    skip: bool = False,
    ignore: Sequence[str] = (),
    pr_number: int | None = None,
    match_number: bool = False,
) -> Verdict:
    """Judge one branch. Raises ``GitError`` when the answer cannot be computed."""
    frag_dir = config.fragment_dir.as_posix().strip("/")
    log = config.changelog.as_posix()
    base = resolve_base(base_ref, repo)
    fork = merge_base(base, head, repo)
    v = Verdict(base_ref=base_ref, merge_base=fork)

    # 1. entries written straight into the log
    before = unreleased_entries(file_at(fork, log, repo), config.unreleased_heading)
    after = unreleased_entries(file_at(head, log, repo), config.unreleased_heading)
    consumed = [
        h
        for path in changed_paths(fork, head, "D", frag_dir, repo)
        if fr.is_fragment_candidate(PurePosixPath(path).name, config)
        and (h := fr.entry_heading(file_at(fork, path, repo))) is not None
    ]
    v.added = surplus(after, before)
    v.unaccounted = surplus(v.added, consumed)
    v.accounted = surplus(v.added, v.unaccounted)

    # 2. the branch's own fragments
    mine = [
        p
        for p in changed_paths(fork, head, "AM", frag_dir, repo)
        if fr.is_fragment_candidate(PurePosixPath(p).name, config)
    ]
    v.new_fragments = mine
    for path in mine:
        name = PurePosixPath(path).name
        number = fr.parse_name(name)
        if number is None:
            v.problems.append((path, fr.bad_name(name)))
            continue
        fragment = fr.Fragment(path=Path(path), number=number, body=file_at(head, path, repo))
        v.problems.extend((path, problem) for problem in fr.validate_fragment(fragment, config))
        if match_number and pr_number and number != pr_number:
            v.problems.append((path, f"{name}: numbered {number}, but this pull request is #{pr_number}"))

    # 3. a fragment at all
    if require and not mine and not v.accounted:
        if skip:
            v.skipped_reason = "the pull request carries the skip label"
        else:
            bookkeeping = {log, f"{frag_dir}/README.md"}  # release + docs edits need no fragment
            relevant = [
                p
                for p in changed_paths(fork, head, "ACDMRT", None, repo)
                if p not in bookkeeping and not _ignored(p, ignore)
            ]
            if relevant:
                v.missing = True
            else:
                v.skipped_reason = "every changed path matches an ignore pattern"
    return v


def report(v: Verdict, config: fr.Config = fr.DEFAULT, skip_label: str = "skip-changelog") -> str:
    """Markdown for the job summary. Every finding names its own remedy."""
    d, log, ur = config.fragment_dir.as_posix(), config.changelog.as_posix(), config.unreleased_heading
    out = ["## changelog.d", "", f"Base `{v.base_ref}` · merge base `{v.merge_base[:12]}`", ""]
    if v.ok:
        if v.new_fragments:
            out += (
                [f"✅ {len(v.new_fragments)} fragment(s), all valid:", ""]
                + [f"- `{p}`" for p in v.new_fragments]
                + [""]
            )
        elif v.accounted:
            out += [
                f"✅ release: {len(v.accounted)} entr{'y' if len(v.accounted) == 1 else 'ies'} folded in from fragments.",
                "",
            ]
        elif v.skipped_reason:
            out += [f"⏭️ No fragment needed: {v.skipped_reason}.", ""]
        else:
            out += ["✅ Nothing to record.", ""]
    if v.unaccounted:
        out += [
            f"❌ {len(v.unaccounted)} entr{'y' if len(v.unaccounted) == 1 else 'ies'} written straight into `{ur}` of `{log}`:",
            "",
        ]
        out += [f"- `{e}`" for e in v.unaccounted]
        out += [
            "",
            (
                f"Move each into `{d}/<number>-<slug>.md` and drop it from the log. Every branch appends at the "
                "same anchor, so two doing it at once conflict on ordering alone; a fragment is its own file and "
                "there is nothing to reconcile."
            ),
            "",
        ]
    if v.problems:
        out += [f"❌ {len(v.problems)} problem(s) in this branch's fragments:", ""]
        for path, problem in v.problems:
            name = PurePosixPath(path).name + ": "
            out.append(f"- `{path}`: {problem.removeprefix(name)}")
        out += ["", "`changelog-d check` reproduces these locally.", ""]
    if v.missing:
        out += [
            "❌ This branch changes code but adds no fragment.",
            "",
            (
                f"Add `{d}/<pr-number>-<slug>.md` holding one `### <Category>: <summary>` heading and a short "
                f"body, or label the pull request `{skip_label}` if there is truly nothing to tell a user."
            ),
            "",
            "```bash",
            'changelog-d new <pr-number> Fixed "what a user would notice"',
            "```",
            "",
        ]
    return "\n".join(out) + "\n"


def annotations(v: Verdict, config: fr.Config = fr.DEFAULT) -> list[str]:
    """GitHub workflow-command lines, one per finding."""
    lines = [
        f"::error file={config.changelog.as_posix()}::{e} was added to {config.unreleased_heading} directly; "
        f"record it as {config.fragment_dir.as_posix()}/<number>-<slug>.md instead"
        for e in v.unaccounted
    ]
    lines += [f"::error file={path},line=1::{problem}" for path, problem in v.problems]
    if v.missing:
        lines.append(f"::error::no {config.fragment_dir.as_posix()}/<number>-<slug>.md fragment in this pull request")
    return lines
