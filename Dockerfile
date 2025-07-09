# Use official Python image
FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PORT=8080

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY --chown=appuser:appuser requirements.txt .

# Install Python dependencies
RUN pip install --user --no-warn-script-location -r requirements.txt

# =======================================

# Runtime stage
# =======================================
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/home/appuser/.local/bin:${PATH}" \
    PORT=8080 \
    FLASK_ENV=production

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# Create and switch to non-root user
RUN useradd -m appuser
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder --chown=appuser:appuser /home/appuser/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port (Cloud Run expects 8080)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Set the entrypoint command for Cloud Run
CMD ["gunicorn", "--bind", ":$PORT", "--workers", "2", "--threads", "4", "--timeout", "120", "--worker-class", "gthread", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "wsgi:application"]