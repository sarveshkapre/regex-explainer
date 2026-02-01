from __future__ import annotations

import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version

from .core import analyze_regex, explain_regex, format_explanation, format_warnings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Explain a regex pattern.")
    parser.add_argument(
        "pattern",
        nargs="?",
        help="Regex pattern to explain. Use '-' to read the pattern from stdin. "
        "JS literals like '/pattern/flags' are supported.",
    )
    parser.add_argument(
        "--flags",
        default="",
        help="Optional flags string (e.g. im) for display purposes",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument("--warnings", action="store_true", help="Show warnings only")
    parser.add_argument(
        "--no-warnings",
        action="store_true",
        help="Do not print the warnings section (text format only).",
    )
    parser.add_argument(
        "--fail-on-warn",
        action="store_true",
        help="Exit with status 2 if any warnings are detected.",
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit.")
    return parser


def _read_pattern_from_stdin() -> str:
    data = sys.stdin.read()
    if data.endswith("\n"):
        data = data.rstrip("\n")
    return data


def _is_escaped(text: str, idx: int) -> bool:
    backslashes = 0
    i = idx - 1
    while i >= 0 and text[i] == "\\":
        backslashes += 1
        i -= 1
    return backslashes % 2 == 1


def _parse_js_literal(maybe_literal: str) -> tuple[str, str] | None:
    if len(maybe_literal) < 2 or not maybe_literal.startswith("/"):
        return None
    for i in range(len(maybe_literal) - 1, 0, -1):
        if maybe_literal[i] != "/":
            continue
        if _is_escaped(maybe_literal, i):
            continue
        pattern = maybe_literal[1:i]
        flags = maybe_literal[i + 1 :]
        if flags and not flags.isalpha():
            return None
        if pattern == "":
            return None
        return pattern, flags
    return None


def _get_version() -> str:
    try:
        return version("regex-explainer")
    except PackageNotFoundError:
        return "unknown"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"regex-explainer {_get_version()}")
        return 0

    if args.pattern is None:
        if sys.stdin.isatty():
            parser.error("the following arguments are required: pattern")
        args.pattern = "-"

    pattern = args.pattern
    flags = args.flags

    if pattern == "-":
        pattern = _read_pattern_from_stdin()
        if pattern == "":
            parser.error("stdin was empty; expected a regex pattern")

    js_literal = _parse_js_literal(pattern)
    if js_literal is not None:
        pattern, literal_flags = js_literal
        if not flags:
            flags = literal_flags

    if args.warnings:
        warnings = analyze_regex(pattern)
        if args.format == "json":
            payload = {
                "pattern": pattern,
                "flags": flags,
                "warnings": [{"code": w.code, "message": w.message} for w in warnings],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            if warnings:
                print(format_warnings(warnings))
            else:
                print("- No warnings detected")
        if args.fail_on_warn and warnings:
            return 2
        return 0

    lines = explain_regex(pattern)
    warnings = analyze_regex(pattern)

    if args.format == "json":
        payload = {
            "pattern": pattern,
            "flags": flags,
            "explanation": lines,
            "warnings": [{"code": w.code, "message": w.message} for w in warnings],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        if args.fail_on_warn and warnings:
            return 2
        return 0

    if flags:
        print(f"Pattern: /{pattern}/{flags}")
    else:
        print(f"Pattern: /{pattern}/")
    print("")
    print("Explanation:")
    print(format_explanation(lines))

    if not args.no_warnings:
        print("")
        print("Warnings:")
        if warnings:
            print(format_warnings(warnings))
        else:
            print("- No warnings detected")

    if args.fail_on_warn and warnings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
