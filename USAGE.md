# Usage Guide

How to use and monitor the ERCOT data scrapers.

## Workflows Overview

This project includes three GitHub Actions workflows:

### 1. ERCOT LMP Scraper
- **File**: `.github/workflows/scraper-lmp.yml`
- **Schedule**: Every 5 minutes
- **Data**: Locational Marginal Prices by Settlement Point
- **Manual trigger**: Yes

### 2. ERCOT SPP Day Ahead Scraper
- **File**: `.github/workflows/scraper-spp.yml`
- **Schedule**: Every 5 minutes
- **Data**: Day-Ahead Settlement Point Prices
- **Manual trigger**: Yes

### 3. Export InfluxDB Data
- **File**: `.github/workflows/export-data.yml`
- **Schedule**: Weekly (Sunday 00:00 UTC)
- **Purpose**: Backup data to CSV
- **Manual trigger**: Yes (with custom days parameter)

## Manual Workflow Execution

### Run a Scraper Manually

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Select the workflow (e.g., "ERCOT LMP Scraper")
4. Click "Run workflow" button
5. Select branch (usually `master` or `main`)
6. Click "Run workflow"

### Run Data Export Manually

1. Go to "Actions" → "Export InfluxDB Data"
2. Click "Run workflow"
3. (Optional) Enter number of days to export
4. Click "Run workflow"

## Monitoring Workflows

### View Workflow Status

1. Go to "Actions" tab
2. See list of recent workflow runs
3. Status indicators:
   - ✅ Green checkmark: Success
   - ❌ Red X: Failed
   - 🟡 Yellow circle: In progress
   - ⚫ Gray circle: Cancelled

### View Workflow Logs

1. Click on a workflow run
2. Click on the job name (e.g., "scrape-lmp")
3. Expand steps to see detailed logs
4. Look for:
   - "Starting LMP scraper..."
   - "Fetching LMP data from ERCOT..."
   - "Successfully wrote X points to InfluxDB"

### Common Log Messages

**Success**:
```
Starting LMP scraper at 2026-01-22T10:45:00Z
Initializing ERCOT client...
Requesting new ERCOT API token...
Successfully obtained ERCOT API token
Fetching LMP data from ERCOT...
Fetching page 1 from /np6-788-cd/lmp_by_settlement_point...
Total records: 50000, Total pages: 10, Fetching: 10
Received 5000 records
Successfully wrote 5000 LMP points to InfluxDB
Completed! Total records processed: 50000
```

**Rate Limited** (normal, will retry):
```
Rate limited, retrying in 1.0s... (attempt 1/3)
```

**Error** (needs attention):
```
Error in LMP scraper: Authentication failed
```

## Querying Data from InfluxDB

### Using InfluxDB Cloud UI

1. Log in to [https://cloud2.influxdata.com](https://cloud2.influxdata.com)
2. Go to "Data Explorer"
3. Build query:
   - **FROM**: Select bucket (`ercot`)
   - **FILTER**: Select measurement
     - `lmp_by_settlement_point`
     - `spp_day_ahead_hourly`
   - **FILTER**: Select fields (e.g., `lmp`, `settlement_point_price`)
4. Click "Submit"

### Using Flux Queries

Example: Get average LMP for last 24 hours
```flux
from(bucket: "ercot")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "lmp_by_settlement_point")
  |> filter(fn: (r) => r._field == "lmp")
  |> mean()
```

Example: Get SPP by settlement point
```flux
from(bucket: "ercot")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "spp_day_ahead_hourly")
  |> filter(fn: (r) => r.settlement_point == "HB_HOUSTON")
  |> filter(fn: (r) => r._field == "settlement_point_price")
```

## Data Export

### Accessing Exported Data

Exported data is available in two places:

#### 1. GitHub Artifacts (90-day retention)

1. Go to "Actions" → "Export InfluxDB Data"
2. Click on a completed export run
3. Scroll down to "Artifacts"
4. Download `influxdb-export-XXX.zip`

#### 2. GitHub Releases (permanent)

For scheduled weekly exports:
1. Go to "Releases" tab
2. Find release named "Weekly Data Export XXX"
3. Download CSV files from "Assets"

### CSV File Format

Exported CSV files include:
- `lmp_by_settlement_point_YYYYMMDD.csv`
- `spp_day_ahead_hourly_YYYYMMDD.csv`

CSV columns:
- `_time`: Timestamp (ISO 8601)
- Tag columns (e.g., `settlement_point`, `settlement_point_type`)
- Field columns (e.g., `lmp`, `settlement_point_price`)

## Pausing/Resuming Scrapers

### Temporarily Disable a Workflow

1. Go to "Actions" tab
2. Select the workflow
3. Click "..." (three dots)
4. Click "Disable workflow"

### Re-enable a Workflow

1. Go to "Actions" tab
2. Select the disabled workflow
3. Click "Enable workflow"

## Adjusting Schedule

To change how often scrapers run:

1. Edit workflow file (e.g., `.github/workflows/scraper-lmp.yml`)
2. Modify the cron expression:
   ```yaml
   on:
     schedule:
       - cron: '*/15 * * * *'  # Every 15 minutes (changed from 5)
   ```
3. Commit and push changes

Common schedules:
- `*/5 * * * *` - Every 5 minutes (default)
- `*/15 * * * *` - Every 15 minutes
- `0 * * * *` - Every hour
- `0 */6 * * *` - Every 6 hours
- `0 0 * * *` - Daily at midnight

## Monitoring Costs

### GitHub Actions Usage

For public repositories:
- ✅ **Unlimited free minutes**
- No cost tracking needed

For private repositories (if you decide to make it private):
1. Go to "Settings" → "Billing and plans"
2. View "Actions" usage
3. Free tier: 2,000 minutes/month
4. Each scraper run: ~1-3 minutes
5. Estimated monthly usage: ~8,640 minutes (may exceed free tier)

**Recommendation**: Keep repository public to avoid costs

### InfluxDB Cloud Usage

Free tier limits:
- ✅ Unlimited writes
- ✅ Unlimited queries
- ✅ 30-day data retention
- ✅ 10,000 data points/minute write rate

To check usage:
1. Log in to [https://cloud2.influxdata.com](https://cloud2.influxdata.com)
2. Go to "Usage"
3. View write/query statistics

If you exceed limits, consider:
- Reducing scraper frequency
- Filtering data before writing
- Upgrading to paid tier (~$5-10/month)

## Notifications

### GitHub Actions Notifications

By default, GitHub sends email notifications for:
- ✅ Workflow failures
- ❌ First workflow success after failure

To customize:
1. GitHub profile → "Settings" → "Notifications"
2. Configure "Actions" notifications

### Adding Custom Notifications

You can add notifications to Slack, Discord, email, etc. by modifying workflows.

Example: Add email notification on failure
```yaml
- name: Send email on failure
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: ERCOT Scraper Failed
    body: Check logs at ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
    to: your-email@example.com
```

## Best Practices

### 1. Regular Monitoring
- Check workflow runs weekly
- Verify data is being written to InfluxDB
- Review any failures

### 2. Data Retention
- InfluxDB free tier: 30-day retention
- Use weekly export workflow for long-term storage
- Download important exports to local storage

### 3. API Rate Limits
- ERCOT may have rate limits
- Default 5-minute interval is safe
- If rate limited frequently, increase interval

### 4. Backup Strategy
- Weekly automated exports (enabled by default)
- Download critical data manually
- Consider upgrading InfluxDB for longer retention

## Troubleshooting

See [SETUP.md](./SETUP.md#troubleshooting) for common issues and solutions.

## Next Steps

- [Development Guide](./DEVELOPMENT.md) - Modify scrapers or add new data sources
- [FAQ](./FAQ.md) - Frequently asked questions
