# PLAN

## Stack
- Language: Python 3.10+
- CLI: argparse
- Tests: pytest
- Lint/format: ruff
- Typecheck: mypy

## Architecture (MVP)
- Tokenizer: linear scan producing tokens with attached quantifiers.
- Explainer: map tokens to human-readable descriptions.
- Analyzer: heuristic checks for anchors, greedy dot, nested quantifiers.

## Milestones
1. Scaffold repo and CLI entry point
2. Tokenizer + explainer output
3. Warning heuristics + tests
4. Polish docs and examples

## MVP checklist
- [x] Tokenize common regex constructs
- [x] Explain tokens in readable bullets
- [x] Heuristic warnings for footguns
- [x] CLI with output and warnings mode
- [x] Tests for tokenizer/explainer/warnings

## Risks
- Heuristics may be incomplete or overly noisy
- Regex flavor differences are not modeled
