# Regex Explainer

Regex explainer CLI: turn a regex into a human-readable breakdown and detect a few common footguns (catastrophic backtracking patterns, missing anchors, and overly-permissive dots).

## Status
- Scaffolded MVP with a basic parser + explainer.

## Quickstart
```bash
make setup
make check
python -m regex_explainer "^hello.*world$"
```

## CLI
```bash
python -m regex_explainer "[A-Z]+\d{2,4}"
python -m regex_explainer "(ab)+" --flags=im
```

## License
MIT.
