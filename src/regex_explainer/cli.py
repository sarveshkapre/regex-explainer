from __future__ import annotations

import argparse
import sys

from .core import analyze_regex, explain_regex, format_explanation, format_warnings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Explain a regex pattern.")
    parser.add_argument("pattern", help="Regex pattern to explain")
    parser.add_argument(
        "--flags",
        default="",
        help="Optional flags string (e.g. im) for display purposes",
    )
    parser.add_argument("--warnings", action="store_true", help="Show warnings only")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.warnings:
        warnings = analyze_regex(args.pattern)
        if warnings:
            print(format_warnings(warnings))
        else:
            print("- No warnings detected")
        return 0

    lines = explain_regex(args.pattern)
    if args.flags:
        print(f"Pattern: /{args.pattern}/{args.flags}")
    else:
        print(f"Pattern: /{args.pattern}/")
    print("Explanation:")
    print(format_explanation(lines))

    warnings = analyze_regex(args.pattern)
    print("Warnings:")
    if warnings:
        print(format_warnings(warnings))
    else:
        print("- No warnings detected")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
