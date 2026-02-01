from __future__ import annotations

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
        if token.kind in {"quantifier", "meta"} and token.value in {"*", "+", "?"}:
            out.append(token)
            i += 1
            continue
        if i + 1 < len(tokens):
            nxt = tokens[i + 1]
            if nxt.kind == "quantifier" or (nxt.kind == "meta" and nxt.value in {"*", "+", "?"}):
                out.append(Token(token.kind, token.value, quantifier=nxt.value))
                i += 2
                continue
        out.append(token)
        i += 1
    return out


def explain_regex(pattern: str) -> List[str]:
    tokens = tokenize(pattern)
    lines: List[str] = []
    for token in tokens:
        lines.append(_explain_token(token))
    return lines


def analyze_regex(pattern: str) -> List[Warning]:
    warnings: List[Warning] = []

    if not pattern.startswith("^"):
        warnings.append(
            Warning("missing_start_anchor", "Regex does not start with ^ anchor.")
        )
    if not pattern.endswith("$"):
        warnings.append(Warning("missing_end_anchor", "Regex does not end with $ anchor."))

    if ".*" in pattern and not pattern.startswith("^.*"):
        warnings.append(
            Warning(
                "greedy_dot", "Found '.*' which can be overly permissive and backtracking-prone."
            )
        )

    if "(.*)+" in pattern or "(.+)" in pattern and ")+" in pattern:
        warnings.append(
            Warning(
                "nested_quantifier",
                "Possible catastrophic backtracking: nested quantified group.",
            )
        )

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
        return f"Escape {token.value}"
    if token.kind == "class":
        return f"Character class {token.value}"
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
