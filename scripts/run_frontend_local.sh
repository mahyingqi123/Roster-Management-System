#!/usr/bin/env bash
set -euo pipefail

# Run Vite dev server locally without Docker
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR%/scripts}"
cd "$REPO_ROOT/frontend"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required. Please install Node.js (https://nodejs.org)" >&2
  exit 1
fi

echo "Installing frontend dependencies (if needed)..."
npm install --silent

export VITE_API_BASE=${VITE_API_BASE:-http://localhost:8000}
export FRONTEND_PORT=${FRONTEND_PORT:-8080}

echo "Starting Vite dev server on port $FRONTEND_PORT (API base: $VITE_API_BASE)"
exec npm run dev -- --port "$FRONTEND_PORT"

