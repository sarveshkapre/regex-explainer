# Regex Explainer

Regex explainer CLI: turn a regex into a human-readable breakdown and detect a few common footguns (catastrophic backtracking patterns, missing anchors, and overly-permissive dots).

## Status
- Scaffolded MVP with a basic parser + explainer.

## Quickstart
```bash
make setup
make check
regex-explainer "^hello.*world$"
```

## CLI
```bash
regex-explainer "[A-Z]+\d{2,4}"
regex-explainer "(ab)+" --flags=im
regex-explainer "/[A-Z]+\\d{2,4}/im" --format=json
echo "^hello.*world$" | regex-explainer - --warnings
echo "^hello.*world$" | regex-explainer --format=json
regex-explainer "(?im)^hello$" --warnings
regex-explainer "hello.*world" --format=json
regex-explainer "hello.*world" --fail-on-warn
```

## License
MIT.
