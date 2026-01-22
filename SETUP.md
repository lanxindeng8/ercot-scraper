# Setup Guide

Complete guide to set up and deploy the ERCOT scraper.

## Prerequisites

1. **GitHub Account**
   - This project uses GitHub Actions (free for public repositories)

2. **InfluxDB Cloud Account**
   - Sign up at [https://cloud2.influxdata.com](https://cloud2.influxdata.com)
   - Free tier includes:
     - Unlimited writes and queries
     - 30-day data retention
     - 10,000 data points per minute

3. **ERCOT API Credentials**
   - Username and password for ERCOT API
   - Public API subscription key
   - ESR API subscription key (optional)

## Step 1: Fork or Clone Repository

### Option A: Use Existing Repository
```bash
# Clone the repository
git clone https://github.com/lanxindeng8/ercot-scraper.git
cd ercot-scraper
```

### Option B: Fork Repository
1. Go to [https://github.com/lanxindeng8/ercot-scraper](https://github.com/lanxindeng8/ercot-scraper)
2. Click "Fork" button
3. Enable GitHub Actions in your fork

## Step 2: Configure InfluxDB Cloud

1. **Create an account** at [https://cloud2.influxdata.com](https://cloud2.influxdata.com)

2. **Create a bucket**:
   - Go to "Load Data" → "Buckets"
   - Click "Create Bucket"
   - Name: `ercot`
   - Retention: 30 days (free tier)

3. **Generate API token**:
   - Go to "Load Data" → "API Tokens"
   - Click "Generate API Token" → "All Access API Token"
   - Copy and save the token (you won't see it again!)

4. **Note your organization ID**:
   - Go to "Settings" → "About"
   - Copy the "Organization ID"

## Step 3: Configure GitHub Secrets

1. Go to your repository on GitHub
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add the following secrets:

### Required Secrets

| Secret Name | Description | Example |
|------------|-------------|---------|
| `ERCOT_API_USERNAME` | ERCOT API username | `your.email@example.com` |
| `ERCOT_API_PASSWORD` | ERCOT API password | `YourPassword123` |
| `ERCOT_PUBLIC_API_SUBSCRIPTION_KEY` | Public API subscription key | `f263c033603e4a06b924e4b96162b1d4` |
| `ERCOT_ESR_API_SUBSCRIPTION_KEY` | ESR API subscription key | `ee4e781cb6aa441fb7ed7c8e2c3098cc` |
| `INFLUXDB_URL` | InfluxDB Cloud URL | `https://us-east-1-1.aws.cloud2.influxdata.com` |
| `INFLUXDB_TOKEN` | InfluxDB API token | `YourTokenHere==` |
| `INFLUXDB_ORG` | InfluxDB organization ID | `06c9eb5bbc09a965` |
| `INFLUXDB_BUCKET` | InfluxDB bucket name | `ercot` |

### How to Add Each Secret

For each secret:
1. Click "New repository secret"
2. Enter the secret name (exactly as shown above)
3. Paste the value
4. Click "Add secret"

## Step 4: Enable GitHub Actions

1. Go to the "Actions" tab in your repository
2. If prompted, click "I understand my workflows, go ahead and enable them"

## Step 5: Test the Scrapers

### Manual Test Run

1. Go to "Actions" tab
2. Select "ERCOT LMP Scraper" workflow
3. Click "Run workflow" dropdown
4. Click "Run workflow" button
5. Wait for the workflow to complete (should take 1-5 minutes)
6. Check the logs for any errors

Repeat for "ERCOT SPP Day Ahead Scraper" workflow.

### Verify Data in InfluxDB

1. Log in to [https://cloud2.influxdata.com](https://cloud2.influxdata.com)
2. Go to "Data Explorer"
3. Select your bucket (`ercot`)
4. Select measurement:
   - `lmp_by_settlement_point` (for LMP data)
   - `spp_day_ahead_hourly` (for SPP data)
5. Click "Submit" to view the data

## Step 6: Configure Schedule (Optional)

The default schedule is every 5 minutes. To change:

1. Edit `.github/workflows/scraper-lmp.yml`
2. Change the cron expression:
   ```yaml
   schedule:
     - cron: '*/15 * * * *'  # Every 15 minutes
   ```

Cron examples:
- `*/5 * * * *` - Every 5 minutes
- `*/15 * * * *` - Every 15 minutes
- `0 * * * *` - Every hour
- `0 */6 * * *` - Every 6 hours

## Troubleshooting

### Common Issues

#### 1. "Authentication failed"
- Check that `ERCOT_API_USERNAME` and `ERCOT_API_PASSWORD` are correct
- Verify that your ERCOT account is active

#### 2. "InfluxDB write failed"
- Verify `INFLUXDB_TOKEN` has write permissions
- Check that `INFLUXDB_BUCKET` name matches your bucket
- Ensure `INFLUXDB_ORG` is correct

#### 3. "Rate limited"
- ERCOT API has rate limits
- The scraper will automatically retry with exponential backoff
- If persistent, consider increasing the interval between runs

#### 4. Workflow not running on schedule
- GitHub Actions cron can have 3-10 minute delays
- During high load (UTC 00:00), delays may be longer
- Use manual triggers for immediate execution

### Getting Help

1. **Check workflow logs**:
   - Go to "Actions" tab
   - Click on the failed workflow run
   - Review the logs for error messages

2. **Verify secrets**:
   - Settings → Secrets and variables → Actions
   - Ensure all 8 secrets are present
   - Secret names must match exactly (case-sensitive)

3. **Test locally** (optional):
   ```bash
   # Set environment variables
   export ERCOT_API_USERNAME="your_username"
   export ERCOT_API_PASSWORD="your_password"
   # ... (all other env vars)

   # Install dependencies
   pip install -r requirements.txt

   # Run scraper
   cd src
   python scraper_lmp.py
   ```

## Next Steps

- [Usage Guide](./USAGE.md) - How to use the scrapers
- [Development Guide](./DEVELOPMENT.md) - How to modify the code
- [FAQ](./FAQ.md) - Frequently asked questions

## Cost

**$0/month** - This project is 100% free:
- ✅ GitHub Actions: Unlimited for public repositories
- ✅ InfluxDB Cloud: Free tier with 30-day retention
- ✅ No credit card required

## Support

For issues or questions:
- Open an issue on GitHub
- Check the [FAQ](./FAQ.md)
- Review the logs in GitHub Actions
