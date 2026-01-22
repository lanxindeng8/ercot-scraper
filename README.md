# ERCOT Data Scraper

Automated ERCOT (Electric Reliability Council of Texas) data scraper using GitHub Actions and InfluxDB Cloud.

## Overview

This project fetches electricity market data from ERCOT APIs and stores it in InfluxDB Cloud for analysis and monitoring.

### Data Sources

- **LMP by Settlement Point**: Real-time Locational Marginal Prices
- **SPP Day Ahead Hourly**: Day-Ahead Settlement Point Prices

## Features

- ✅ Automated data collection every 5 minutes via GitHub Actions
- ✅ Multiple scraper workflows for different data sources
- ✅ Data stored in InfluxDB Cloud (free tier)
- ✅ Periodic data export for backup
- ✅ 100% free using GitHub Actions public repository

## Architecture

```
GitHub Actions (scheduled)
    ↓
ERCOT Public API
    ↓
InfluxDB Cloud (free tier)
```

## Setup

### Prerequisites

- GitHub account
- InfluxDB Cloud account (free tier)
- ERCOT API credentials

### Configuration

1. Fork this repository
2. Add the following secrets in GitHub Settings → Secrets and variables → Actions:
   - `ERCOT_API_USERNAME`
   - `ERCOT_API_PASSWORD`
   - `ERCOT_PUBLIC_API_SUBSCRIPTION_KEY`
   - `ERCOT_ESR_API_SUBSCRIPTION_KEY`
   - `INFLUXDB_URL`
   - `INFLUXDB_ORG`
   - `INFLUXDB_DATABASE`
   - `INFLUXDB_TOKEN`

3. Enable GitHub Actions in your repository

## Usage

The scrapers run automatically based on the schedule defined in `.github/workflows/`.

To manually trigger a scraper:
1. Go to Actions tab
2. Select the workflow
3. Click "Run workflow"

## Cost

**$0/month** - Completely free using:
- GitHub Actions (unlimited for public repositories)
- InfluxDB Cloud Free Tier (30-day data retention)

## Migrated From

This project was migrated from AWS Lambda to GitHub Actions to eliminate AWS costs (~$9-11/month).

Original infrastructure:
- AWS Lambda + EventBridge
- AWS Secrets Manager
- AWS S3

## License

MIT

## Author

Migrated to GitHub Actions on 2026-01-22
