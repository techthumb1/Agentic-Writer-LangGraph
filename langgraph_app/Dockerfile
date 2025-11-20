# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY langgraph_app/requirements.txt /app/requirements.txt
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r /app/requirements.txt

# Copy application code
COPY langgraph_app /app/langgraph_app

# Copy data directory containing templates and style profiles
COPY data /app/data

# Set data directory environment variable
ENV WRITERZ_DATA_DIR=/app/data

# Ensure Python can import from /app
ENV PYTHONPATH=/app

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/healthz || exit 1

CMD ["uvicorn", "langgraph_app.integrated_server:app", "--host", "0.0.0.0", "--port", "8000"]