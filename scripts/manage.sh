#!/usr/bin/env bash
# Dev helper script to manage services (backend, frontend, DB migrations)
# Usage: ./manage.sh [start|stop|restart|migrate|refresh-db|status]

set -e

# PIDs directory
PID_DIR=".pids"
mkdir -p "$PID_DIR"

# Commands and settings
BACKEND_CMD="poetry run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
DB_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/gsg}"

# Start backend and record PID
start_backend() {
  echo "Starting backend..."
  eval "$BACKEND_CMD" &
  echo $! > "$PID_DIR/backend.pid"
  echo "Backend PID: $(cat $PID_DIR/backend.pid)"
}

# Stop backend using stored PID
stop_backend() {
  if [[ -f "$PID_DIR/backend.pid" ]]; then
    PID=$(cat "$PID_DIR/backend.pid")
    echo "Stopping backend (PID $PID)..."
    kill $PID 2>/dev/null || true
    # Also kill any lingering backend processes on port 8000
    lsof -ti tcp:8000 | xargs -r kill -9
    rm "$PID_DIR/backend.pid"
  else
    echo "No backend.pid found"
  fi
}

# Start frontend and record PID
start_frontend() {
  echo "Starting frontend..."
  # Run Next.js dev inside web/ directory
  (cd web && pnpm dev) &
  echo $! > "$PID_DIR/frontend.pid"
  echo "Frontend PID: $(cat $PID_DIR/frontend.pid)"
}

# Stop frontend
stop_frontend() {
  if [[ -f "$PID_DIR/frontend.pid" ]]; then
    PID=$(cat "$PID_DIR/frontend.pid")
    echo "Stopping frontend (PID $PID)..."
    kill $PID 2>/dev/null || true
    # Also kill any lingering frontend processes on ports 3000-3006
    lsof -ti tcp:3000-3006 | xargs -r kill -9
    rm "$PID_DIR/frontend.pid"
  else
    echo "No frontend.pid found"
  fi
}

# Run Alembic migrations
migrate() {
  echo "Running migrations on $DB_URL..."
  DATABASE_URL="$DB_URL" alembic upgrade head
}

# Drop and recreate schema, then migrate
refresh_db() {
  echo "Refreshing database schema..."
  psql "$DB_URL" -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
  migrate
}

# Show status of services
status() {
  echo "Backend PID:" $(cat "$PID_DIR/backend.pid" 2>/dev/null || echo "stopped")
  echo "Frontend PID:" $(cat "$PID_DIR/frontend.pid" 2>/dev/null || echo "stopped")
}

case "$1" in
  start)
    start_backend
    start_frontend
    ;;
  start-frontend)
    start_frontend
    ;;
  start-backend)
    start_backend
    ;;
  stop-frontend)
    stop_frontend
    ;;
  stop-backend)
    stop_backend
    ;;
  restart-frontend)
    stop_frontend
    start_frontend
    ;;
  restart-backend)
    stop_backend
    start_backend
    ;;
  restart-fastapi)
    # Alias for restarting the FastAPI backend
    stop_backend
    start_backend
    ;;
  logs-backend)
    tail -f uvicorn.log
    ;;
  stop)
    stop_frontend
    stop_backend
    ;;
  restart)
    $0 stop
    $0 start
    ;;
  migrate)
    migrate
    ;;
  "refresh-db")
    refresh_db
    ;;
  status)
    status
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|start-frontend|stop-frontend|start-backend|stop-backend|restart-frontend|restart-backend|restart-fastapi|logs-backend|migrate|refresh-db|status}"
    exit 1
esac 