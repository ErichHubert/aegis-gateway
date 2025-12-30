# services/inspection/Dockerfile

# Use a specific, slim Python base image (avoid 'latest' for reproducibility)
FROM python:3.13.1-slim@sha256:031ebf3cde9f3719d2db385233bcb18df5162038e9cda20e64e08f49f4b47a2f

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

# Install Python dependencies
# NOTE: If you later want maximum supply-chain hardening, generate a pinned
# requirements.txt (pip-compile) and consider `--require-hashes`.
RUN pip install --no-cache-dir -r requirements.txt

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