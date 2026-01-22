#!/bin/bash
# 更新InfluxDB GitHub Secrets

set -e

REPO="lanxindeng8/ercot-scraper"

echo "========================================="
echo "更新InfluxDB配置到GitHub Secrets"
echo "========================================="
echo ""

# 提示用户输入新的InfluxDB信息
echo "请输入新的InfluxDB信息："
echo ""

read -p "InfluxDB URL (例: https://us-east-1-1.aws.cloud2.influxdata.com): " INFLUXDB_URL
read -p "Organization ID (例: 06c9eb5bbc09a965): " INFLUXDB_ORG
read -p "Bucket名称 (例: ercot): " INFLUXDB_BUCKET
read -p "API Token: " INFLUXDB_TOKEN

echo ""
echo "========================================="
echo "确认信息"
echo "========================================="
echo "URL: $INFLUXDB_URL"
echo "Org: $INFLUXDB_ORG"
echo "Bucket: $INFLUXDB_BUCKET"
echo "Token: ${INFLUXDB_TOKEN:0:20}...${INFLUXDB_TOKEN: -10}"
echo ""

read -p "确认更新？(y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "取消更新"
    exit 0
fi

echo ""
echo "========================================="
echo "更新GitHub Secrets..."
echo "========================================="
echo ""

echo "更新 INFLUXDB_URL..."
echo "$INFLUXDB_URL" | gh secret set INFLUXDB_URL --repo="$REPO"

echo "更新 INFLUXDB_ORG..."
echo "$INFLUXDB_ORG" | gh secret set INFLUXDB_ORG --repo="$REPO"

echo "更新 INFLUXDB_BUCKET..."
echo "$INFLUXDB_BUCKET" | gh secret set INFLUXDB_BUCKET --repo="$REPO"

echo "更新 INFLUXDB_TOKEN..."
echo "$INFLUXDB_TOKEN" | gh secret set INFLUXDB_TOKEN --repo="$REPO"

echo ""
echo "========================================="
echo "✅ InfluxDB配置更新完成！"
echo "========================================="
echo ""
echo "查看所有Secrets："
gh secret list --repo="$REPO"
echo ""
echo "下一步："
echo "1. 访问：https://github.com/$REPO/actions"
echo "2. 手动触发workflow测试新配置"
echo ""
