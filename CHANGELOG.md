# CHANGELOG

## Unreleased
- Add `python -m regex_explainer` entrypoint via `__main__.py`
- Add JSON output (`--format=json`) and `--no-warnings`
- Add stdin pattern support (`-`) and JS-style regex literal parsing (`/pattern/flags`)
- Add `--version`
- Add implicit stdin (when piped) and `--fail-on-warn` for CI usage
- Add `--quiet` and `--explain-only` for script-friendly output
- Explain more group prefixes (scoped flags `(?im:...)`, named groups `(?P<name>...)` / `(?<name>...)`)
- Improve heuristics: lazy quantifiers, inline flag anchor handling, nested-quantifier backtracking warning
- Makefile reliability: prefer `.venv/bin/python`, fall back to `python3`; `make setup` installs editable package
- Packaging: setuptools `src/` discovery; add `build` to dev deps
