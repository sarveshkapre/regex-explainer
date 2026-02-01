SHELL := /bin/bash

.PHONY: setup dev test lint typecheck build check release

setup:
	python -m pip install -r requirements-dev.txt

fmt:
	ruff format .

lint:
	ruff check .

typecheck:
	mypy src/regex_explainer

test:
	pytest

dev:
	python -m regex_explainer "^hello.*world$"

build:
	python -m build

check: lint typecheck test

release:
	python -m build
