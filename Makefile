SHELL := /bin/bash

.PHONY: setup dev test lint fmt typecheck build check release

# Prefer a local venv if present, otherwise fall back to python3.
PYTHON ?= $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else command -v python3 2>/dev/null || command -v python; fi)
PYTHONPATH ?= src

setup:
	$(PYTHON) -m pip install -r requirements-dev.txt
	$(PYTHON) -m pip install -e .

fmt:
	$(PYTHON) -m ruff format .

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy src/regex_explainer

test:
	$(PYTHON) -m pytest

dev:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m regex_explainer "^hello.*world$"

build:
	$(PYTHON) -m build

check: lint typecheck test

release:
	$(PYTHON) -m build
