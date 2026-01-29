# ERCOT Data Scraper

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-blue?logo=github-actions)](https://github.com/features/actions)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![InfluxDB Cloud](https://img.shields.io/badge/InfluxDB-Cloud-blue?logo=influxdb)](https://www.influxdata.com/products/influxdb-cloud/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Automated ERCOT (Electric Reliability Council of Texas) data scraper using GitHub Actions and InfluxDB Cloud.

## 🎯 Overview

This project fetches electricity market data from ERCOT APIs and stores it in InfluxDB Cloud for analysis and monitoring. It runs completely free using GitHub Actions and InfluxDB Cloud's free tier.

### Data Sources

- **LMP Node Zone Hub** (`lmp_node_zone_hub`)
  - Real-time Locational Marginal Prices
  - Includes energy, congestion, and loss components
  - Updated every 5 minutes via SCED

- **SPP Day Ahead Hourly** (`dam_stlmnt_pnt_prices`)
  - Day-Ahead Settlement Point Prices
  - Hourly data for next day
  - Updated daily

## ✨ Features

- ✅ **Automated data collection** every 5 minutes via GitHub Actions
- ✅ **Multiple scraper workflows** for different data sources
- ✅ **Data stored in InfluxDB Cloud** (free tier, 30-day retention)
- ✅ **Weekly automated backups** to CSV via GitHub Releases
- ✅ **Smart incremental fetching** - only fetches new data
- ✅ **Rate limit handling** with exponential backoff
- ✅ **100% free** using public repository and free cloud services

## 🏗️ Architecture

### Option 1: GitHub Actions (Free, but delayed)
```
┌─────────────────────┐
│  GitHub Actions     │
│  (Every 5 minutes)  │  ← May have delays on free tier
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  ERCOT Public API   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  InfluxDB Cloud     │
└─────────────────────┘
```

### Option 2: Local Mac (Recommended for reliability)
```
┌─────────────────────┐
│  macOS launchd      │
│  (Exact 5 minutes)  │  ← Reliable, runs 24/7
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  ERCOT Public API   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  InfluxDB Cloud     │
└─────────────────────┘
```

## 🚀 Quick Start

### Option 1: GitHub Actions (Cloud)

1. **Fork this repository**
2. **Configure GitHub Secrets** (see [SETUP.md](./SETUP.md))
3. **Enable GitHub Actions**
4. Done! Scrapers will run automatically

### Option 2: Local Mac Mini (Recommended)

For reliable 5-minute intervals, run locally on macOS:

```bash
# 1. Clone the repository
git clone git@github.com:lanxindeng8/ercot-scraper.git
cd ercot-scraper

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your InfluxDB credentials

# 4. Install launchd services
./scripts/install_launchd.sh
```

This will install two services:
- **RTM LMP Scraper**: runs every 5 minutes
- **DAM LMP Scraper**: runs every 15 minutes

For detailed setup instructions, see [**SETUP.md**](./SETUP.md).

## 📋 Repository Structure

```
ercot-scraper/
├── .github/
│   └── workflows/
│       ├── scraper-rtm-lmp.yml    # RTM LMP scraper (GitHub Actions)
│       ├── scraper-dam-lmp.yml    # DAM LMP scraper (GitHub Actions)
│       └── export-data.yml        # Data export workflow
├── scrapers/
│   ├── rtm_lmp.py                # RTM LMP scraper
│   └── dam_lmp.py                # DAM LMP scraper
├── src/
│   ├── ercot_client.py           # ERCOT API client
│   └── influxdb_writer.py        # InfluxDB writer
├── scripts/                      # Local deployment scripts
│   ├── run_rtm_scraper.sh        # RTM run script
│   ├── run_dam_scraper.sh        # DAM run script
│   ├── install_launchd.sh        # macOS installer
│   └── uninstall_launchd.sh      # macOS uninstaller
├── launchd/                      # macOS launchd configs
│   ├── com.trueflux.rtm-lmp-scraper.plist
│   └── com.trueflux.dam-lmp-scraper.plist
├── README.md                     # This file
├── SETUP.md                      # Setup guide
├── USAGE.md                      # Usage guide
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── .gitignore                    # Git ignore rules
```

## 📚 Documentation

- [**SETUP.md**](./SETUP.md) - Setup and configuration guide
- [**USAGE.md**](./USAGE.md) - Usage and monitoring guide
- [**PROJECT-STATUS.md**](./PROJECT-STATUS.md) - Current project status

## 💰 Cost

**$0/month** - Completely free using:

| Service | Free Tier | Usage |
|---------|-----------|-------|
| **GitHub Actions** | Unlimited (public repos) | ~4,320 min/month |
| **InfluxDB Cloud** | 30-day retention | ~200 points/min |
| **Total Cost** | **$0/month** | ✅ Within free limits |

## 🔄 Migrated From AWS

This project was migrated from AWS Lambda to GitHub Actions to eliminate costs.

**Previous AWS costs**: ~$9-11/month
- EC2 t3.micro: $8.21/month
- EBS 8GB: $0.70/month
- Secrets Manager: $0.40/month
- Lambda, S3, EventBridge: Free tier

**Cost savings**: $9-11/month → $0/month 💰

Original infrastructure:
- AWS Lambda (Node.js/TypeScript)
- EventBridge (cron triggers)
- AWS Secrets Manager
- S3 (deployment packages)

## 🛠️ Technology Stack

- **Language**: Python 3.11
- **API Client**: requests + urllib3
- **Database**: InfluxDB Cloud (time series)
- **Automation**: GitHub Actions
- **Data Format**: CSV exports

## 📊 Data Schema

### LMP Node Zone Hub
```
Measurement: lmp_by_settlement_point
Tags:
  - settlement_point: string (e.g., HB_HOUSTON, LZ_WEST)
  - settlement_point_type: string (Hub, Zone, Node)
Fields:
  - lmp: float ($/MWh)
  - energy_component: float
  - congestion_component: float
  - loss_component: float
Time: SCEDTimestamp (every ~5 minutes)
```

### SPP Day Ahead Hourly
```
Measurement: spp_day_ahead_hourly
Tags:
  - settlement_point: string
  - settlement_point_type: string
Fields:
  - settlement_point_price: float ($/MWh)
Time: DeliveryDate + HourEnding
```

## 🔐 Security

- All credentials stored in GitHub Secrets (encrypted)
- Secrets never appear in logs
- Public repository safe (no sensitive data in code)
- InfluxDB token has write-only permissions

## 📈 Monitoring

View scraper status:
1. Go to "Actions" tab
2. Check recent workflow runs
3. Green ✅ = success, Red ❌ = failed

View data in InfluxDB:
1. Log in to [InfluxDB Cloud](https://cloud2.influxdata.com)
2. Go to "Data Explorer"
3. Query your data

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details

## 👤 Author

Migrated from AWS Lambda to GitHub Actions on 2026-01-22

## 🙏 Acknowledgments

- ERCOT for providing public API access
- InfluxDB for free cloud tier
- GitHub for free Actions on public repositories

---

**Questions?** Check [SETUP.md](./SETUP.md) or [USAGE.md](./USAGE.md)
