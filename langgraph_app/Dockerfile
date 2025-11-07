# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /usr/src/app

# System deps (curl for healthcheck, gcc for any C extensions)
RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies first (leverages layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY . .

# Expose for Cloud Run
EXPOSE 8080

# Health check (Cloud Run expects port 8080)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the integrated FastAPI server
# NOTE: langgraph_app.integrated_server defines "app = FastAPI(...)"
CMD ["uvicorn", "langgraph_app.integrated_server:app", "--host", "0.0.0.0", "--port", "8080"]
