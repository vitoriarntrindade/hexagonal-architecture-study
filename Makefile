# Makefile for common development tasks

.PHONY: install run run-factory test lint check

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	python -m uvicorn app.adapters.http.api:app --reload

run-factory:
	python -m uvicorn app.adapters.http.api:create_app --reload --factory

lint:
	python -m ruff check .

test:
	python -m pytest -q

check: lint test
	@echo "All checks passed!"
