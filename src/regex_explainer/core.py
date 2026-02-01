from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    quantifier: Optional[str] = None


@dataclass(frozen=True)
class Warning:
    code: str
    message: str


def tokenize(pattern: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "\\":
            if i + 1 < len(pattern):
                tokens.append(Token("escape", pattern[i : i + 2]))
                i += 2
                continue
            tokens.append(Token("escape", "\\"))
            i += 1
            continue
        if ch in "()*+?.^$|":
            tokens.append(Token("meta", ch))
            i += 1
            continue
        if ch == "[":
            end = i + 1
            depth = 1
            while end < len(pattern) and depth > 0:
                if pattern[end] == "\\":
                    end += 2
                    continue
                if pattern[end] == "]":
                    depth -= 1
                    if depth == 0:
                        break
                end += 1
            if end < len(pattern) and pattern[end] == "]":
                tokens.append(Token("class", pattern[i : end + 1]))
                i = end + 1
            else:
                tokens.append(Token("class", pattern[i:]))
                i = len(pattern)
            continue
        if ch == "{":
            end = pattern.find("}", i + 1)
            if end != -1:
                tokens.append(Token("quantifier", pattern[i : end + 1]))
                i = end + 1
                continue
        tokens.append(Token("literal", ch))
        i += 1

    return _attach_quantifiers(tokens)


def _attach_quantifiers(tokens: List[Token]) -> List[Token]:
    out: List[Token] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if _is_quantifier_token(token):
            out.append(token)
            i += 1
            continue
        if i + 1 < len(tokens) and _can_be_quantified(token):
            nxt = tokens[i + 1]
            if _is_quantifier_token(nxt):
                quantifier = nxt.value
                i += 2
                # Support lazy quantifiers like `*?`, `+?`, `??`, `{m,n}?`.
                if i < len(tokens) and tokens[i].kind == "meta" and tokens[i].value == "?":
                    quantifier = f"{quantifier}?"
                    i += 1
                out.append(Token(token.kind, token.value, quantifier=quantifier))
                continue
        out.append(token)
        i += 1
    return out


def explain_regex(pattern: str) -> List[str]:
    tokens = tokenize(pattern)
    lines: List[str] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.kind == "meta" and token.value == "(":
            special = _try_explain_group_prefix(tokens, i)
            if special is not None:
                line, new_i = special
                lines.append(line)
                i = new_i
                continue
        lines.append(_explain_token(token))
        i += 1
    return lines


def analyze_regex(pattern: str) -> List[Warning]:
    warnings: List[Warning] = []

    anchor_check_pattern = _strip_leading_inline_flags(pattern)
    if not anchor_check_pattern.startswith("^"):
        warnings.append(Warning("missing_start_anchor", "Regex does not start with ^ anchor."))
    if not anchor_check_pattern.endswith("$"):
        warnings.append(Warning("missing_end_anchor", "Regex does not end with $ anchor."))

    for warning in _analyze_wildcards(pattern):
        warnings.append(warning)

    nested = _analyze_nested_quantifiers(pattern)
    if nested is not None:
        warnings.append(nested)

    return warnings


def _explain_token(token: Token) -> str:
    base = _base_description(token)
    if token.quantifier:
        return f"{base} (quantifier {token.quantifier})"
    return base


def _base_description(token: Token) -> str:
    if token.kind == "literal":
        return f"Literal '{token.value}'"
    if token.kind == "escape":
        return _describe_escape(token.value)
    if token.kind == "class":
        return _describe_class(token.value)
    if token.kind == "quantifier":
        return f"Quantifier {token.value}"
    if token.kind == "meta":
        return _meta_description(token.value)
    return f"{token.kind} {token.value}"


def _meta_description(ch: str) -> str:
    mapping = {
        ".": "Any character",
        "^": "Start anchor",
        "$": "End anchor",
        "|": "Alternation",
        "(": "Group start",
        ")": "Group end",
        "*": "Zero or more",
        "+": "One or more",
        "?": "Optional",
    }
    return mapping.get(ch, f"Meta '{ch}'")


def format_explanation(lines: Iterable[str]) -> str:
    return "\n".join(f"- {line}" for line in lines)


def format_warnings(warnings: Iterable[Warning]) -> str:
    return "\n".join(f"- [{warn.code}] {warn.message}" for warn in warnings)


def _is_quantifier_token(token: Token) -> bool:
    return token.kind == "quantifier" or (token.kind == "meta" and token.value in {"*", "+", "?"})


def _can_be_quantified(token: Token) -> bool:
    if token.kind in {"literal", "escape", "class"}:
        return True
    if token.kind != "meta":
        return False
    return token.value in {".", ")", "]"}  # `]` is defensive (not emitted as a token today)


def _strip_leading_inline_flags(pattern: str) -> str:
    # Python-style: `(?im)` / `(?im-sx)` at the very beginning.
    # This intentionally does not try to interpret scoped flags like `(?im:...)`.
    match = re.match(r"^\(\?[aiLmsux]+(?:-[aiLmsux]+)?\)", pattern)
    if match is None:
        return pattern
    return pattern[match.end() :]


def _is_unbounded_quantifier(quantifier: str) -> bool:
    if quantifier in {"*", "+", "*?", "+?"}:
        return True
    if quantifier.startswith("{") and quantifier.endswith("}"):
        inner = quantifier[1:-1]
        if "," in inner:
            _, right = inner.split(",", 1)
            return right.strip() == ""
        return False
    if quantifier.startswith("{") and quantifier.endswith("}?"):
        inner = quantifier[1:-2]
        if "," in inner:
            _, right = inner.split(",", 1)
            return right.strip() == ""
        return False
    return False


def _is_lazy_quantifier(quantifier: str) -> bool:
    return quantifier.endswith("?")


def _analyze_wildcards(pattern: str) -> List[Warning]:
    tokens = tokenize(pattern)
    warnings: List[Warning] = []

    for token in tokens:
        if token.quantifier is None:
            continue
        if _is_lazy_quantifier(token.quantifier):
            continue

        if (
            token.kind == "meta"
            and token.value == "."
            and _is_unbounded_quantifier(token.quantifier)
        ):
            warnings.append(
                Warning(
                    "greedy_dot",
                    "Found greedy unbounded wildcard (e.g. `.*` / `.+`) which can be overly permissive and backtracking-prone.",
                )
            )
            break

        if (
            token.kind == "class"
            and token.value in {r"[\s\S]", r"[\d\D]", r"[\w\W]"}
            and _is_unbounded_quantifier(token.quantifier)
        ):
            warnings.append(
                Warning(
                    "greedy_wide_class",
                    "Found greedy unbounded wide character class (e.g. `[\\s\\S]*`) which behaves like `.*` and can be overly permissive.",
                )
            )
            break

    return warnings


def _quantifier_repeats_group(quantifier: str) -> bool:
    if quantifier in {"*", "+", "*?", "+?"}:
        return True
    if quantifier in {"?", "??"}:
        return False
    if quantifier.startswith("{") and (quantifier.endswith("}") or quantifier.endswith("}?")):
        inner = quantifier[1:-1] if quantifier.endswith("}") else quantifier[1:-2]
        if "," in inner:
            left, right = inner.split(",", 1)
            try:
                minimum = int(left.strip() or "0")
            except ValueError:
                return False
            right = right.strip()
            if right == "":
                return True
            try:
                maximum = int(right)
            except ValueError:
                return False
            return maximum > 1 and minimum < maximum
        try:
            exact = int(inner.strip())
        except ValueError:
            return False
        return exact > 1
    return False


def _analyze_nested_quantifiers(pattern: str) -> Warning | None:
    tokens = tokenize(pattern)
    group_stack: List[int] = []

    for idx, token in enumerate(tokens):
        if token.kind == "meta" and token.value == "(":
            group_stack.append(idx)
            continue
        if token.kind == "meta" and token.value == ")":
            if not group_stack:
                continue
            start = group_stack.pop()
            group_quantifier = token.quantifier
            if group_quantifier is None or not _quantifier_repeats_group(group_quantifier):
                continue

            inner = tokens[start + 1 : idx]
            has_inner_quantifier = any(t.quantifier is not None for t in inner)
            has_alternation = any(t.kind == "meta" and t.value == "|" for t in inner)
            if has_inner_quantifier or has_alternation:
                details = []
                if has_inner_quantifier:
                    details.append("inner quantifier")
                if has_alternation:
                    details.append("alternation")
                detail_str = " and ".join(details)
                return Warning(
                    "nested_quantifier",
                    f"Possible catastrophic backtracking: a repeated group contains {detail_str}.",
                )
    return None


def _describe_escape(value: str) -> str:
    mapping = {
        r"\d": "Digit character",
        r"\D": "Non-digit character",
        r"\w": "Word character",
        r"\W": "Non-word character",
        r"\s": "Whitespace character",
        r"\S": "Non-whitespace character",
        r"\b": "Word boundary",
        r"\B": "Non-word boundary",
        r"\t": "Tab",
        r"\n": "Newline",
        r"\r": "Carriage return",
        r"\\": "Literal backslash",
    }
    return mapping.get(value, f"Escape {value}")


def _describe_class(value: str) -> str:
    if value.startswith("[^"):
        return f"Negated character class {value}"
    return f"Character class {value}"


def _try_explain_group_prefix(tokens: List[Token], start: int) -> tuple[str, int] | None:
    # Collapses common `(?...)` prefixes into a single, clearer line.
    if start + 1 >= len(tokens):
        return None
    if tokens[start + 1].kind != "meta" or tokens[start + 1].value != "?":
        return None

    def tok(i: int) -> str | None:
        if i >= len(tokens):
            return None
        return tokens[i].value

    third = tok(start + 2)
    if third is None:
        return None

    if third == ":":
        return ("Non-capturing group start", start + 3)
    if third == "=":
        return ("Positive lookahead start", start + 3)
    if third == "!":
        return ("Negative lookahead start", start + 3)
    if third == "<" and tok(start + 3) == "=":
        return ("Positive lookbehind start", start + 4)
    if third == "<" and tok(start + 3) == "!":
        return ("Negative lookbehind start", start + 4)
    if third == "P" and tok(start + 3) == "<":
        parsed = _parse_group_name(tokens, start + 4)
        if parsed is not None:
            name, next_i = parsed
            return (f"Named capturing group start (name {name})", next_i)
        return ("Named capturing group start", start + 4)
    if third == "<":
        # PCRE/JS-style: `(?<name>...)`
        parsed = _parse_group_name(tokens, start + 3)
        if parsed is not None:
            name, next_i = parsed
            return (f"Named capturing group start (name {name})", next_i)

    # Inline flags group: `(?im)` (stop at the closing `)` if present).
    i = start + 2
    flag_chars: List[str] = []
    while i < len(tokens):
        value = tokens[i].value
        if value == ":":
            if flag_chars:
                return (f"Inline flags (?{''.join(flag_chars)}:...) group start", i + 1)
            return None
        if value == ")":
            if flag_chars:
                return (f"Inline flags (?{''.join(flag_chars)})", i + 1)
            return None
        if tokens[i].kind != "literal" or not re.fullmatch(r"[a-zA-Z-]", value):
            return None
        flag_chars.append(value)
        i += 1

    return None


def _parse_group_name(tokens: List[Token], start: int) -> tuple[str, int] | None:
    # Parse a group name starting at `start`, stopping at the first unescaped `>`.
    # Returns (name, next_index_after_gt).
    name_chars: List[str] = []
    i = start
    while i < len(tokens):
        value = tokens[i].value
        if value == ">":
            name = "".join(name_chars)
            if name and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                return name, i + 1
            return None
        if tokens[i].kind != "literal" or not re.fullmatch(r"[A-Za-z0-9_]", value):
            return None
        name_chars.append(value)
        i += 1
    return None
