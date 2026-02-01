# AGENTS

## Purpose
Regex Explainer: a small CLI that explains regex patterns and flags common footguns.

## Guardrails
- Keep explanations deterministic and easy to read.
- Avoid executing regex patterns against untrusted input.
- Prefer simple heuristics for warnings; list limitations in docs.

## Commands
- Setup: `make setup`
- Dev: `make dev`
- Test: `make test`
- Lint: `make lint`
- Typecheck: `make typecheck`
- Build: `make build`
- Quality gate: `make check`
- Release: `make release`
