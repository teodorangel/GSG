# GSG Project

This is a project repository for GSG (Git Style Guide).

## Project Structure
- `PLANNING.md` - Project planning and architecture details
- `TASK.md` - Project tasks and progress tracking
- `docker-compose.dev.yml` - Docker configuration for development

## Getting Started
Follow these steps to set up and run the backend API and tests; see `web/README.md` for frontend instructions.

### Prerequisites
- Python 3.9 or later
- Poetry (https://python-poetry.org)
- PostgreSQL for the database

### Install dependencies
```bash
poetry install --with dev
```

### Configure environment variables
Create a `.env` file in the project root or export these in your shell:
```bash
export DATABASE_URL=postgresql://user:pass@host:5432/dbname
export PINECONE_API_KEY=your-pinecone-api-key
export PINECONE_ENV=your-pinecone-env
export PINECONE_INDEX_NAME=your-index-name
```

### Database migrations
```bash
alembic upgrade head
```

### Run the API server
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Run tests
```bash
pytest -q --cov
```

## Frontend

The frontend application lives in the `web/` directory. See `web/README.md` for setup and run instructions. 