# PLAN

Regex Explainer: a fast, safe CLI that turns a regex pattern into a readable breakdown and flags common footguns.

## Features
- CLI explainer (`regex-explainer` / `python -m regex_explainer`)
- Token-by-token breakdown (literals, escapes, classes, groups, alternation, quantifiers)
- Safety-focused warnings (e.g., missing anchors, overly-permissive wildcards, backtracking risks)

## Top risks / unknowns
- Regex dialect differences (PCRE vs Python vs JS) can make explanations misleading.
- Warning heuristics can be noisy or miss real issues without a true AST + engine model.
- Avoid ever executing untrusted patterns against large/untrusted input.

## Commands
- Setup: `make setup`
- Format: `make fmt`
- Lint: `make lint`
- Typecheck: `make typecheck`
- Test: `make test`
- Quality gate: `make check`
- Build: `make build`

More: `docs/PROJECT.md`.

## Shipped (latest)
- `python -m regex_explainer` works via `src/regex_explainer/__main__.py`
- `make` targets work on systems without `python` (prefers `.venv/bin/python`, falls back to `python3`)
- `make setup` installs dev deps + editable package; `make build` works (adds `build` dev dep + setuptools src discovery)
- Better output + automation: `--format=json`, `--no-warnings`, stdin (`-`), `/pattern/flags`, `--version`
- Better heuristics: lazy quantifiers (`*?`/`+?`/`{m,n}?`), inline flags handling for anchors, nested-quantifier backtracking warning
- Better explanations for group prefixes: scoped flags (`(?im:...)`) and named groups (`(?P<name>...)`, `(?<name>...)`)
- Root-level `PLAN.md`, `CHANGELOG.md`, `UPDATE.md` added (docs files point to these)

## Next
- Expand group-prefix explanations (named groups, scoped flags `(?im:...)`)
- Add more warning rules (ambiguous alternation, backreference-heavy patterns)
- Improve tokenizer/AST so warnings are less heuristic and more structural
