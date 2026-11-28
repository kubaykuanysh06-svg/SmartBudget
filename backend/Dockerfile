FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir .

EXPOSE 8000

# Test image: same code plus pytest. Used by docker-compose.test.yml only.
FROM base AS test
RUN pip install --no-cache-dir ".[dev]"
CMD ["pytest", "-q"]

# Runtime image (default target, keep it last).
FROM base AS runtime
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
