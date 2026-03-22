# Makefile for common development tasks

.PHONY: install run test lint

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	# run uvicorn importing the exported `app` (no --factory needed)
	python -m uvicorn app.adapters.http.api:app --reload

run-factory:
	# alternative: run uvicorn using the factory function
	python -m uvicorn app.adapters.http.api:create_app --reload --factory

test:
	python -m pytest -q

lint:
	ruff .
