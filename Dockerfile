FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy project metadata
COPY pyproject.toml poetry.lock ./

# Install dependencies (skip dev dependencies)
RUN poetry config virtualenvs.create false \
  && poetry install --without dev --no-interaction --no-ansi --no-root

# Copy application code
COPY . .

# Expose API port
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"] 