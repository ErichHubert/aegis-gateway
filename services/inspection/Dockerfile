# services/inspection/Dockerfile

# Use a specific, slim Python base image (avoid 'latest' for reproducibility)
FROM python:3.13.12-slim-trixie@sha256:f1927c75e81efd1e091dbd64b6c0ecaa5630b38635a3d1c04034ac636e1f94c8

# Runtime-focused defaults:
# - no .pyc files in long-running containers (smaller image, fewer stale-cache surprises)
# - unbuffered stdout/stderr so logs show up immediately
# - disable pip version checks/noise and disable pip cache
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Do NOT run as root inside the container
# - Create a dedicated user/group with no shell and no password
RUN addgroup --system app && adduser --system --ingroup app app

# Set working directory
WORKDIR /app

# Copy only dependency manifest first (better layer caching)
COPY requirements.txt ./

# Install Python dependencies from the compiled, hash-pinned lockfile.
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.txt

# Copy the application code
# Use --chown to avoid an extra chown layer and ensure the non-root user can read files.
COPY --chown=app:app . .

# Drop privileges
USER app

# Expose port used by uvicorn
EXPOSE 8000

# Start FastAPI via uvicorn
# NOTE: Keep single-worker for now. 
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
