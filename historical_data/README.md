# ERCOT Historical Data

Downloaded: 2026-02-06

## Data Files

### fuel_mix/
**Fuel Mix Report 2007-2024** (49 MB)
- 各燃料类型发电量 (每15分钟)
- 包含风电 (Wind)、太阳能 (Solar)、天然气 (Gas)、煤炭 (Coal)、核能 (Nuclear) 等
- 时间范围: 2007-2024

### NP4-180-ER/
**Historical DAM Load Zone and Hub Prices**
- DAM (日前市场) 结算点价格
- 按 Hub 和 Load Zone 汇总
- 文件: DAMLZHBSPP_2015.zip, DAMLZHBSPP_2016.zip

### NP4-181-ER/
**Historical DAM Clearing Prices for Capacity**
- DAM (日前市场) 容量清算价格
- AS MCPC (Ancillary Service Market Clearing Price for Capacity)
- 文件: DAMASMCPC_2015.zip, DAMASMCPC_2016.zip

### NP6-785-ER/
**Historical RTM Load Zone and Hub Prices**
- RTM (实时市场) 结算点价格
- 按 Hub 和 Load Zone 汇总
- 文件: RTMLZHBSPP_2015.zip, RTMLZHBSPP_2016.zip

---

## 数据说明

| 缩写 | 全称 | 说明 |
|------|------|------|
| DAM | Day-Ahead Market | 日前市场 |
| RTM | Real-Time Market | 实时市场 |
| LMP | Locational Marginal Price | 节点边际电价 |
| SPP | Settlement Point Price | 结算点价格 |
| LZ | Load Zone | 负荷区 |
| HB | Hub | 交易枢纽 |
| MCPC | Market Clearing Price for Capacity | 容量市场清算价格 |
| AS | Ancillary Service | 辅助服务 |

## 主要交易枢纽 (Hubs)

- **HB_HOUSTON** - 休斯顿枢纽
- **HB_NORTH** - 北部枢纽
- **HB_SOUTH** - 南部枢纽
- **HB_WEST** - 西部枢纽

## 负荷区 (Load Zones)

- **LZ_HOUSTON** - 休斯顿负荷区
- **LZ_NORTH** - 北部负荷区
- **LZ_SOUTH** - 南部负荷区
- **LZ_WEST** - 西部负荷区

---

## 下载脚本

```bash
# 下载更多历史数据
cd /Users/nancy/projects/ercot-scraper
source venv/bin/activate
python scripts/download_historical.py --start-date 2017-01-01 --end-date 2017-12-31
```

## 数据来源

- ERCOT Market Information System (MIS)
- https://www.ercot.com/mktinfo/prices
