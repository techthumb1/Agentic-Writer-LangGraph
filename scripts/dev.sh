#!/bin/bash
echo "🚀 Starting development environment..."

# Start PostgreSQL if not running
if ! docker ps | grep -q postgres-dev; then
    echo "Starting PostgreSQL..."
    docker run -d \
        --name postgres-dev \
        -e POSTGRES_DB=agentic_writer_dev \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=password \
        -p 5432:5432 \
        postgres:15-alpine
    sleep 5
fi

# Start backend
echo "Starting backend..."
cd langgraph_app
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Development servers started!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"

# Cleanup function
cleanup() {
    echo "Stopping development servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM
wait
