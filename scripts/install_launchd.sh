#!/bin/bash
# Install launchd services for ERCOT scrapers on macOS
# Run this script on your Mac Mini after cloning the repo

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== ERCOT Scraper Launchd Installer ===${NC}"

# Get the absolute path to the scraper directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRAPER_PATH="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Scraper path: ${SCRAPER_PATH}${NC}"

# Create logs directory
mkdir -p "$SCRAPER_PATH/logs"

# Check if .env file exists
if [ ! -f "$SCRAPER_PATH/.env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create .env file with your InfluxDB credentials:"
    echo ""
    echo "INFLUXDB_URL=https://your-influxdb-url"
    echo "INFLUXDB_TOKEN=your-token"
    echo "INFLUXDB_ORG=your-org"
    echo "INFLUXDB_BUCKET=your-bucket"
    exit 1
fi

# Make scripts executable
chmod +x "$SCRAPER_PATH/scripts/run_rtm_scraper.sh"
chmod +x "$SCRAPER_PATH/scripts/run_dam_scraper.sh"

# Create LaunchAgents directory if not exists
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$LAUNCH_AGENTS_DIR"

# Process and install RTM plist
echo -e "${YELLOW}Installing RTM LMP scraper (every 5 minutes)...${NC}"
sed "s|SCRAPER_PATH|$SCRAPER_PATH|g" "$SCRAPER_PATH/launchd/com.trueflux.rtm-lmp-scraper.plist" > "$LAUNCH_AGENTS_DIR/com.trueflux.rtm-lmp-scraper.plist"

# Process and install DAM plist
echo -e "${YELLOW}Installing DAM LMP scraper (every 15 minutes)...${NC}"
sed "s|SCRAPER_PATH|$SCRAPER_PATH|g" "$SCRAPER_PATH/launchd/com.trueflux.dam-lmp-scraper.plist" > "$LAUNCH_AGENTS_DIR/com.trueflux.dam-lmp-scraper.plist"

# Unload existing services (if any)
launchctl unload "$LAUNCH_AGENTS_DIR/com.trueflux.rtm-lmp-scraper.plist" 2>/dev/null || true
launchctl unload "$LAUNCH_AGENTS_DIR/com.trueflux.dam-lmp-scraper.plist" 2>/dev/null || true

# Load new services
echo -e "${YELLOW}Loading services...${NC}"
launchctl load "$LAUNCH_AGENTS_DIR/com.trueflux.rtm-lmp-scraper.plist"
launchctl load "$LAUNCH_AGENTS_DIR/com.trueflux.dam-lmp-scraper.plist"

echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo "Services installed:"
echo "  - RTM LMP Scraper: runs every 5 minutes"
echo "  - DAM LMP Scraper: runs every 15 minutes"
echo ""
echo "Useful commands:"
echo "  # Check service status"
echo "  launchctl list | grep trueflux"
echo ""
echo "  # View logs"
echo "  tail -f $SCRAPER_PATH/logs/rtm_stdout.log"
echo "  tail -f $SCRAPER_PATH/logs/dam_stdout.log"
echo ""
echo "  # Stop services"
echo "  launchctl unload ~/Library/LaunchAgents/com.trueflux.rtm-lmp-scraper.plist"
echo "  launchctl unload ~/Library/LaunchAgents/com.trueflux.dam-lmp-scraper.plist"
echo ""
echo "  # Start services"
echo "  launchctl load ~/Library/LaunchAgents/com.trueflux.rtm-lmp-scraper.plist"
echo "  launchctl load ~/Library/LaunchAgents/com.trueflux.dam-lmp-scraper.plist"
