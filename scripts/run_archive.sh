#!/bin/bash
# Archive ERCOT data to SQLite - runs daily at 3 AM via launchd

# Change to project directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Use prediction-service venv (has all dependencies)
PYTHON="/Users/nancy/projects/trueflux/prediction-service/venv/bin/python"

# Load environment variables from .env file
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Ensure logs directory exists
mkdir -p "$PROJECT_DIR/logs"

# Run archive script
echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting archive to SQLite..."
$PYTHON scripts/archive_to_sqlite.py
echo "$(date '+%Y-%m-%d %H:%M:%S') - Archive completed"
