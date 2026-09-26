.PHONY: install install-dev test lint format typecheck docker-build docker-up docker-down clean

install:
	python -m pip install -r requirements.txt

install-dev:
	python -m pip install -r requirements.txt -r requirements-test.txt -e ".[dev]"

test:
	python -m pytest -q

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

typecheck:
	mypy api/

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
