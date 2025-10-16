#!/usr/bin/env bash
set -euo pipefail

# Start only the Postgres service defined in docker-compose.yml
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR%/scripts}"
cd "$REPO_ROOT"

echo "Starting database container (service: db)..."
docker compose up -d db

echo "Database is starting. Exposed port: 5432"

