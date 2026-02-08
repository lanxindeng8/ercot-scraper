#!/bin/bash
# RTM LMP Real-Time Scraper - runs every 5 minutes via launchd
# Uses CDR (Current Day Reports) HTML scraping for near real-time data

# Change to project directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Load environment variables from .env file
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Ensure logs directory exists
mkdir -p "$PROJECT_DIR/logs"

# Run the real-time CDR scraper (provides data within 5 minutes vs 6 hour delay from API)
cd src && "$PROJECT_DIR/venv/bin/python" scraper_rtm_lmp_realtime.py

# Log completion
echo "$(date '+%Y-%m-%d %H:%M:%S') - RTM LMP scraper completed" >> "$PROJECT_DIR/logs/rtm_scraper.log"
