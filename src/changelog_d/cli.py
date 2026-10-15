"""``changelog-d``: one file per change, assembled at release time.

changelog-d check                 validate every fragment (writes nothing)
changelog-d print                 preview the assembled [Unreleased] body
changelog-d apply                 fold fragments into CHANGELOG.md, delete them
changelog-d new 42 Fixed "..."    write changelog.d/42-<slug>.md
changelog-d gate --base-ref main  judge a branch (what the GitHub Action runs)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __version__
from . import fragments as fr
from . import gate as gt


def _config(args: argparse.Namespace) -> fr.Config:
    return fr.Config(
        fragment_dir=Path(args.dir),
        changelog=Path(args.changelog),
        unreleased_heading=args.heading,
        placeholder_floor=args.placeholder_floor,
    )


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _problems(problems: list[str]) -> int:
    print("invalid changelog fragment(s):", file=sys.stderr)
    for problem in problems:
        print(f"  {problem}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="changelog-d", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--version", action="version", version=f"changelog-d {__version__}")
    parser.add_argument("--dir", default="changelog.d", help="fragment directory (default: changelog.d)")
    parser.add_argument("--changelog", default="CHANGELOG.md", help="the assembled log (default: CHANGELOG.md)")
    parser.add_argument("--heading", default="## [Unreleased]", help="section fragments fold into")
    parser.add_argument(
        "--placeholder-floor",
        type=int,
        default=0,
        help="numbers >= this are placeholders too (default 0 = off; 0000 and 9999 always are)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="validate every fragment")
    sub.add_parser("print", help="print the assembled section")
    sub.add_parser("apply", help="fold fragments into the log and delete them")

    new = sub.add_parser("new", help="write a new fragment")
    new.add_argument("number", type=int, help="PR or issue number")
    new.add_argument("category", help="Added, Fixed, Changed, Docs, Security ...")
    new.add_argument("summary", help="one line a user would understand")
    new.add_argument("--body", default="", help="prose under the heading")

    g = sub.add_parser("gate", help="judge a branch against its base")
    g.add_argument("--base-ref", default=os.environ.get("GITHUB_BASE_REF") or "main")
    g.add_argument("--head", default="HEAD")
    g.add_argument("--repo", default=None)
    g.add_argument("--require", default="true", help="a branch must add a fragment (default: true)")
    g.add_argument("--skip", default="false", help="true when the PR carries the skip label")
    g.add_argument("--skip-label", default="skip-changelog")
    g.add_argument("--ignore", default="", help="newline/comma separated globs that need no fragment")
    g.add_argument("--pr-number", type=int, default=None)
    g.add_argument("--match-number", default="false", help="fragment number must equal the PR number")
    g.add_argument("--summary", default=os.environ.get("GITHUB_STEP_SUMMARY"), help="append the report here")

    args = parser.parse_args(argv)
    config = _config(args)

    if args.command == "new":
        try:
            path = fr.new(args.number, args.category, args.summary, args.body, config)
        except (ValueError, FileExistsError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(path)
        return 0

    if args.command == "gate":
        ignore = [p.strip() for chunk in args.ignore.splitlines() for p in chunk.split(",") if p.strip()]
        try:
            verdict = gt.run(
                base_ref=args.base_ref,
                head=args.head,
                repo=Path(args.repo) if args.repo else None,
                config=config,
                require=_truthy(args.require),
                skip=_truthy(args.skip),
                ignore=ignore,
                pr_number=args.pr_number,
                match_number=_truthy(args.match_number),
            )
        except gt.GitError as exc:
            print(f"::error::changelog.d gate could not run: {exc}", file=sys.stderr)
            return 2
        text = gt.report(verdict, config, args.skip_label)
        print(text, end="")
        if args.summary:
            with open(args.summary, "a", encoding="utf-8") as handle:
                handle.write(text)
        for line in gt.annotations(verdict, config):
            print(line)
        output = os.environ.get("GITHUB_OUTPUT")
        if output:
            with open(output, "a", encoding="utf-8") as handle:
                handle.write(f"ok={'true' if verdict.ok else 'false'}\n")
                handle.write(f"fragments={len(verdict.new_fragments)}\n")
        return 0 if verdict.ok else 1

    problems = fr.validate(config)
    if problems:
        return _problems(problems)
    fragments = fr.collect(config)
    if args.command == "check":
        print(f"changelog fragments OK ({len(fragments)} pending)")
    elif args.command == "print":
        print(fr.render(fragments))
    else:
        try:
            consumed = fr.apply(config)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if not consumed:
            print("no changelog fragments to assemble")
        else:
            print(f"assembled {len(consumed)} fragment(s) into {config.changelog}:")
            for fragment in consumed:
                print(f"  {fragment.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
