# InfluxDB Cloud 设置指南

## 注册新账户

### 1. 访问注册页面
https://cloud2.influxdata.com/signup

### 2. 选择注册方式
- 使用Google账户（推荐，最快）
- 或使用邮箱注册

### 3. 选择区域
推荐选择距离你最近的区域：
- **US East (N. Virginia)** - 美国东部
- **US West (Oregon)** - 美国西部
- **EU Central (Frankfurt)** - 欧洲中部
- **Asia Pacific (Tokyo)** - 亚太东京

### 4. 创建Organization
- Organization名称：随意填写（如：`My Organization`）
- 会自动生成 Organization ID

---

## 配置InfluxDB

### 步骤1：创建Bucket

1. 登录后点击左侧菜单 **"Load Data"** → **"Buckets"**
2. 点击 **"Create Bucket"**
3. 配置：
   - **Name**: `ercot` （必须与scraper配置匹配）
   - **Retention**: `30 days` （免费套餐）
   - **Description**: `ERCOT electricity market data`
4. 点击 **"Create"**

### 步骤2：生成API Token

1. 点击左侧菜单 **"Load Data"** → **"API Tokens"**
2. 点击 **"Generate API Token"**
3. 选择 **"All Access API Token"** （推荐）
   - 或选择 **"Read/Write Token"** 并指定 `ercot` bucket
4. **重要**：立即复制Token并保存！（只显示一次）

### 步骤3：获取配置信息

#### 获取Organization ID
1. 点击左侧菜单 **"Settings"**
2. 找到 **"About"** 部分
3. 复制 **"Organization ID"**（形如：`06c9eb5bbc09a965`）

#### 获取InfluxDB URL
查看浏览器地址栏，URL格式为：
```
https://us-east-1-1.aws.cloud2.influxdata.com
```

根据你选择的区域，URL可能是：
- US East: `https://us-east-1-1.aws.cloud2.influxdata.com`
- US West: `https://us-west-2-1.aws.cloud2.influxdata.com`
- EU: `https://eu-central-1-1.aws.cloud2.influxdata.com`
- AP: `https://ap-southeast-2-1.aws.cloud2.influxdata.com`

---

## 更新GitHub Secrets

### 方法1：使用脚本（推荐）

```bash
cd ~/projects/ercot-scraper
./update-influxdb-secrets.sh
```

脚本会交互式地要求你输入：
- InfluxDB URL
- Organization ID
- Bucket名称
- API Token

### 方法2：手动更新

```bash
REPO="lanxindeng8/ercot-scraper"

# 更新4个InfluxDB相关的secrets
echo "YOUR_INFLUXDB_URL" | gh secret set INFLUXDB_URL --repo="$REPO"
echo "YOUR_ORG_ID" | gh secret set INFLUXDB_ORG --repo="$REPO"
echo "ercot" | gh secret set INFLUXDB_BUCKET --repo="$REPO"
echo "YOUR_API_TOKEN" | gh secret set INFLUXDB_TOKEN --repo="$REPO"
```

### 方法3：通过GitHub网页

1. 访问：https://github.com/lanxindeng8/ercot-scraper/settings/secrets/actions
2. 点击每个secret右侧的 **"Update"**
3. 输入新值并保存

需要更新的4个secrets：
- `INFLUXDB_URL`
- `INFLUXDB_ORG`
- `INFLUXDB_BUCKET`
- `INFLUXDB_TOKEN`

---

## 验证配置

### 1. 手动触发workflow测试

```bash
# 触发LMP scraper
gh workflow run "ERCOT LMP Scraper" --repo=lanxindeng8/ercot-scraper

# 查看运行状态
gh run list --repo=lanxindeng8/ercot-scraper --limit 1
```

### 2. 通过GitHub网页触发

1. 访问：https://github.com/lanxindeng8/ercot-scraper/actions
2. 选择 **"ERCOT LMP Scraper"** workflow
3. 点击 **"Run workflow"** → **"Run workflow"**
4. 等待1-2分钟查看结果

### 3. 检查InfluxDB数据

1. 登录 InfluxDB Cloud
2. 点击 **"Data Explorer"**
3. 选择 bucket: `ercot`
4. 选择 measurement:
   - `lmp_by_settlement_point`
   - `spp_day_ahead_hourly`
5. 点击 **"Submit"** 查看数据

---

## 免费套餐限制

InfluxDB Cloud 免费套餐：
- ✅ **数据写入**: 无限制
- ✅ **数据查询**: 无限制
- ✅ **写入速率**: 10,000 点/分钟
- ✅ **查询速率**: 300 MB/5分钟
- ⚠️ **数据保留**: 仅30天
- ✅ **存储容量**: 30天内数据量不限

如果需要更长保留期：
- 使用 **Data Export workflow**（每周自动导出）
- 或升级到付费套餐（~$5-10/月）

---

## 故障排查

### 问题1：无法写入数据

**检查**：
- Token是否有写入权限
- Bucket名称是否正确
- Organization ID是否正确

**解决**：
```bash
# 查看GitHub Actions日志
gh run view --repo=lanxindeng8/ercot-scraper --log-failed
```

### 问题2：Token权限不足

**解决**：
1. 在InfluxDB中重新生成Token
2. 选择 "All Access API Token"
3. 更新GitHub Secret: `INFLUXDB_TOKEN`

### 问题3：找不到Bucket

**解决**：
1. 确认Bucket名称为 `ercot`
2. 或更新代码使用新的Bucket名称
3. 更新GitHub Secret: `INFLUXDB_BUCKET`

---

## 下一步

✅ 完成InfluxDB配置后：
1. 运行 `./update-influxdb-secrets.sh` 更新secrets
2. 手动触发workflow测试
3. 检查InfluxDB中是否有新数据
4. 如果成功，scheduled workflows将自动每5分钟运行

---

**需要帮助？**
- 查看 [SETUP.md](./SETUP.md)
- 查看 [USAGE.md](./USAGE.md)
- GitHub Issues: https://github.com/lanxindeng8/ercot-scraper/issues
