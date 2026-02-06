#!/bin/bash
# RTM LMP Scraper - runs every 5 minutes via launchd

# Change to script directory
cd "$(dirname "$0")/.."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Run the scraper
cd src && python scraper_rtm_lmp.py

# Log completion
echo "$(date '+%Y-%m-%d %H:%M:%S') - RTM LMP scraper completed" >> logs/rtm_scraper.log
