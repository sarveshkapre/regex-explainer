# UPDATE

## 2026-02-01
- Fix `make` targets on systems without `python` (prefer `.venv/bin/python`, fall back to `python3`)
- Ensure `python -m regex_explainer` works via `src/regex_explainer/__main__.py`
- Add `--format=json`, `--no-warnings`, stdin pattern support (`-`), `/pattern/flags`, and `--version`
- Add implicit stdin support (when piped) and `--fail-on-warn` for CI-friendly checks
- Improve warning heuristics (lazy quantifiers, inline flags anchor handling, nested quantified groups)
- Improve explanations for group prefixes (scoped flags and named groups)
- Add root `PLAN.md` / `CHANGELOG.md` / `UPDATE.md` and align `docs/` pointers

## Next
- Expand group-prefix explanations (named groups, scoped flags)
- Add more warning rules and reduce false positives

## PR instructions (if `gh` is unavailable)
1. Create a branch: `git checkout -b chore/next`
2. Commit: `git commit -am "..."` (or `git add -A && git commit -m "..."`)
3. Push: `git push -u origin chore/next`
4. Open a PR: `gh pr create --fill`
