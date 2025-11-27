# services/inspection/Dockerfile

# Use a specific, slim Python base image (avoid 'latest' for reproducibility)
FROM python:3.13.1-slim AS base

# Disable .pyc generation:
#    - Reduces image size
#    - Avoids stale bytecode issues in containerized deployments
#    - Slightly slower cold starts, but irrelevant for long-running services
#    NOTE: In serverless/FaaS environments you might want to ENABLE .pyc.
ENV PYTHONDONTWRITEBYTECODE=1

# nbuffered logs so they appear immediately in 'docker logs' / logging backends
ENV PYTHONUNBUFFERED=1

# Do NOT run as root inside the container
#    - Create a dedicated user/group with no shell and no password
RUN addgroup --system app && adduser --system --ingroup app app

# Set working directory and ensure ownership
WORKDIR /app
RUN chown -R app:app /app

# Install Python dependencies in a single layer.
# We COPY only requirements first to leverage Docker layer caching.
COPY requirements.txt .

# Optional: set a more strict pip default (no cache, no pip version noise, etc.)
ENV PIP_NO_CACHE_DIR=1
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Fix ownership for the copied files, so non-root user can read them
RUN chown -R app:app /app

# Switch to the non-root user for runtime
USER app
EXPOSE 8000

# NOTE:
# - For production you might later wrap uvicorn with gunicorn (uvicorn worker)

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]