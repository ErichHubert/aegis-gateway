# services/inspection/Dockerfile

# Use a specific, slim Python base image (avoid 'latest' for reproducibility)
FROM python:3.13.16-slim-trixie@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f

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
# pip is only needed to build the image; remove it and its vendored libraries
# from the runtime image in the same layer.
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.txt \
    && python -m pip uninstall --yes pip

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
