#!/bin/bash
# Configure GitHub Secrets Helper Script
# This script helps you add secrets to your GitHub repository using gh CLI

set -e

REPO="lanxindeng8/ercot-scraper"

echo "========================================="
echo "GitHub Secrets Configuration Helper"
echo "========================================="
echo ""
echo "This script will help you configure GitHub Secrets for the ERCOT scraper."
echo "You need to have 'gh' CLI installed and authenticated."
echo ""
echo "Repository: $REPO"
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: 'gh' CLI is not installed."
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: You are not authenticated with GitHub."
    echo "Please run: gh auth login"
    exit 1
fi

echo "✅ gh CLI is installed and authenticated"
echo ""

# Function to set secret
set_secret() {
    local name=$1
    local value=$2

    if [ -z "$value" ]; then
        echo "⚠️  Skipping $name (empty value)"
        return
    fi

    echo "Setting $name..."
    echo "$value" | gh secret set "$name" --repo="$REPO"
    echo "✅ $name set successfully"
}

# Read credentials from backup file
CREDS_FILE="$HOME/aws-backup/secrets/ercot-credentials.json"

if [ -f "$CREDS_FILE" ]; then
    echo "Found credentials file: $CREDS_FILE"
    echo "Reading credentials..."

    ERCOT_API_USERNAME=$(jq -r '.ERCOT_API_USERNAME' "$CREDS_FILE")
    ERCOT_API_PASSWORD=$(jq -r '.ERCOT_API_PASSWORD' "$CREDS_FILE")
    ERCOT_PUBLIC_API_SUBSCRIPTION_KEY=$(jq -r '.ERCOT_PUBLIC_API_SUBSCRIPTION_KEY' "$CREDS_FILE")
    ERCOT_ESR_API_SUBSCRIPTION_KEY=$(jq -r '.ERCOT_ESR_API_SUBSCRIPTION_KEY' "$CREDS_FILE")
    INFLUXDB_URL=$(jq -r '.INFLUXDB_URL' "$CREDS_FILE")
    INFLUXDB_ORG=$(jq -r '.INFLUXDB_ORG' "$CREDS_FILE")
    INFLUXDB_DATABASE=$(jq -r '.INFLUXDB_DATABASE' "$CREDS_FILE")
    INFLUXDB_TOKEN=$(jq -r '.INFLUXDB_TOKEN' "$CREDS_FILE")

    echo ""
    echo "========================================="
    echo "Setting GitHub Secrets..."
    echo "========================================="
    echo ""

    set_secret "ERCOT_API_USERNAME" "$ERCOT_API_USERNAME"
    set_secret "ERCOT_API_PASSWORD" "$ERCOT_API_PASSWORD"
    set_secret "ERCOT_PUBLIC_API_SUBSCRIPTION_KEY" "$ERCOT_PUBLIC_API_SUBSCRIPTION_KEY"
    set_secret "ERCOT_ESR_API_SUBSCRIPTION_KEY" "$ERCOT_ESR_API_SUBSCRIPTION_KEY"
    set_secret "INFLUXDB_URL" "$INFLUXDB_URL"
    set_secret "INFLUXDB_ORG" "$INFLUXDB_ORG"
    set_secret "INFLUXDB_BUCKET" "$INFLUXDB_DATABASE"
    set_secret "INFLUXDB_TOKEN" "$INFLUXDB_TOKEN"

    echo ""
    echo "========================================="
    echo "✅ All secrets configured successfully!"
    echo "========================================="
    echo ""
    echo "Next steps:"
    echo "1. Go to https://github.com/$REPO/actions"
    echo "2. Enable GitHub Actions if not already enabled"
    echo "3. Manually trigger a workflow to test"
    echo ""

else
    echo "❌ Credentials file not found: $CREDS_FILE"
    echo ""
    echo "You can manually set secrets using:"
    echo "  gh secret set SECRET_NAME --repo=$REPO"
    echo ""
    echo "Required secrets:"
    echo "  - ERCOT_API_USERNAME"
    echo "  - ERCOT_API_PASSWORD"
    echo "  - ERCOT_PUBLIC_API_SUBSCRIPTION_KEY"
    echo "  - ERCOT_ESR_API_SUBSCRIPTION_KEY"
    echo "  - INFLUXDB_URL"
    echo "  - INFLUXDB_ORG"
    echo "  - INFLUXDB_BUCKET"
    echo "  - INFLUXDB_TOKEN"
    echo ""
    exit 1
fi
