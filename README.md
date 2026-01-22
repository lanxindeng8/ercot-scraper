# ERCOT Data Scraper

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-blue?logo=github-actions)](https://github.com/features/actions)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![InfluxDB Cloud](https://img.shields.io/badge/InfluxDB-Cloud-blue?logo=influxdb)](https://www.influxdata.com/products/influxdb-cloud/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Automated ERCOT (Electric Reliability Council of Texas) data scraper using GitHub Actions and InfluxDB Cloud.

## 🎯 Overview

This project fetches electricity market data from ERCOT APIs and stores it in InfluxDB Cloud for analysis and monitoring. It runs completely free using GitHub Actions and InfluxDB Cloud's free tier.

### Data Sources

- **LMP by Settlement Point** (`lmp_by_settlement_point`)
  - Real-time Locational Marginal Prices
  - Includes energy, congestion, and loss components
  - Updated every 5 minutes

- **SPP Day Ahead Hourly** (`spp_day_ahead_hourly`)
  - Day-Ahead Settlement Point Prices
  - Hourly data for next day
  - Updated every 5 minutes

## ✨ Features

- ✅ **Automated data collection** every 5 minutes via GitHub Actions
- ✅ **Multiple scraper workflows** for different data sources
- ✅ **Data stored in InfluxDB Cloud** (free tier, 30-day retention)
- ✅ **Weekly automated backups** to CSV via GitHub Releases
- ✅ **Smart incremental fetching** - only fetches new data
- ✅ **Rate limit handling** with exponential backoff
- ✅ **100% free** using public repository and free cloud services

## 🏗️ Architecture

```
┌─────────────────────┐
│  GitHub Actions     │
│  (Every 5 minutes)  │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  ERCOT Public API   │
│  - Authentication   │
│  - Paginated Data   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  InfluxDB Cloud     │
│  - Time Series DB   │
│  - 30-day Retention │
└─────────────────────┘
```

## 🚀 Quick Start

1. **Fork this repository**
2. **Configure GitHub Secrets** (see [SETUP.md](./SETUP.md))
3. **Enable GitHub Actions**
4. Done! Scrapers will run automatically

For detailed setup instructions, see [**SETUP.md**](./SETUP.md).

## 📋 Repository Structure

```
ercot-scraper/
├── .github/
│   └── workflows/
│       ├── scraper-lmp.yml        # LMP scraper workflow
│       ├── scraper-spp.yml        # SPP scraper workflow
│       └── export-data.yml        # Data export workflow
├── src/
│   ├── ercot_client.py           # ERCOT API client
│   ├── influxdb_writer.py        # InfluxDB writer
│   ├── scraper_lmp.py            # LMP scraper script
│   ├── scraper_spp.py            # SPP scraper script
│   └── export_data.py            # Data export script
├── README.md                     # This file
├── SETUP.md                      # Setup guide
├── USAGE.md                      # Usage guide
├── requirements.txt              # Python dependencies
└── .gitignore                    # Git ignore rules
```

## 📚 Documentation

- [**SETUP.md**](./SETUP.md) - Complete setup and configuration guide
- [**USAGE.md**](./USAGE.md) - Usage instructions and monitoring guide

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

### LMP by Settlement Point
```
Measurement: lmp_by_settlement_point
Tags:
  - settlement_point: string
  - settlement_point_type: string
Fields:
  - lmp: float
  - energy_component: float
  - congestion_component: float
  - loss_component: float
Time: SCEDTimestamp
```

### SPP Day Ahead Hourly
```
Measurement: spp_day_ahead_hourly
Tags:
  - settlement_point: string
  - settlement_point_type: string
Fields:
  - settlement_point_price: float
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
