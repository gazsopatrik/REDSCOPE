.PHONY: help install dev test lint format docker-up docker-down seed

help:
	@echo "RedScope Management Commands:"
	@echo "  make install     Install backend and frontend dependencies"
	@echo "  make dev         Run local development servers"
	@echo "  make test        Run backend unit & integration tests"
	@echo "  make lint        Run ruff linting and mypy type checks"
	@echo "  make format      Auto-format backend code with ruff"
	@echo "  make docker-up   Start all containers via Docker Compose"
	@echo "  make docker-down Stop all containers"
	@echo "  make seed        Seed demo lab project data"

install:
	cd backend && pip install -e .
	cd frontend && npm install

dev:
	cd backend && uvicorn app.main:app --reload --port 8000

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check . && mypy app

format:
	cd backend && ruff format .

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

seed:
	python scripts/seed_demo_data.py
