# Risk Assessment Survey System - Backend

FastAPI backend for the Risk Assessment Survey System.

## Setup

```bash
# Create virtual environment with UV
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"
```

## Development

```bash
# Run development server
uvicorn src.main:app --reload --port 8000

# Run tests
pytest

# Run linting
ruff check src tests
ruff format src tests
```

## API Documentation

Once running, API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
