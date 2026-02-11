start:
    uv run uvicorn app.main:app

dev:
    uv run uvicorn app.main:app --reload

typecheck:
    uv run pyrefly check

lint:
    uv run ruff check --fix

format:
    uv run ruff format
