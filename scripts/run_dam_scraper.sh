#!/bin/bash
# DAM LMP Scraper - runs every 15 minutes via launchd

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
python -m scrapers.dam_lmp

# Log completion
echo "$(date '+%Y-%m-%d %H:%M:%S') - DAM LMP scraper completed" >> logs/dam_scraper.log
