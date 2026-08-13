#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ -x ".venv/bin/python" ]]; then
  PYTHON_EXE=".venv/bin/python"
else
  PYTHON_EXE="python3"
fi

BACKEND_HOST="127.0.0.1"
BACKEND_PORT="8000"
FRONTEND_HOST="127.0.0.1"
FRONTEND_PORT="8501"
BACKEND_URL="http://${BACKEND_HOST}:${BACKEND_PORT}/predict"

echo "Starting backend on http://${BACKEND_HOST}:${BACKEND_PORT}"
"$PYTHON_EXE" app.py > backend.log 2>&1 &
BACKEND_PID=$!

echo "Starting frontend on http://${FRONTEND_HOST}:${FRONTEND_PORT}"
BACKEND_URL="$BACKEND_URL" "$PYTHON_EXE" -m streamlit run streamlit_app.py \
  --server.address "$FRONTEND_HOST" --server.port "$FRONTEND_PORT" > streamlit.log 2>&1 &
FRONTEND_PID=$!

cleanup() {
  echo "Stopping services..."
  kill "$FRONTEND_PID" "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo ""
echo "App is running:"
echo "- Backend:  http://${BACKEND_HOST}:${BACKEND_PORT}"
echo "- Frontend: http://${FRONTEND_HOST}:${FRONTEND_PORT}"
echo ""
echo "Logs: backend.log, streamlit.log"
echo "Press Ctrl+C to stop both services."

wait
