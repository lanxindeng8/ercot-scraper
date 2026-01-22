# ERCOT API 配置指南

## 当前状态

⚠️ **ERCOT API认证端点失效**

原因：ERCOT API认证端点返回404错误
- 原端点：`https://ercotb2c.b2clogin.com/.../oauth2/v2.0/token`
- 最后成功使用：2026-01-04
- 当前状态：404 Not Found

**需要行动**：重新申请ERCOT API访问权限

---

## 重新申请ERCOT API

### 1. 访问ERCOT开发者门户

https://developer.ercot.com/

### 2. 申请或检查API访问

可能需要：
- 创建新的开发者账户
- 申请API访问权限
- 订阅Public API服务
- 获取新的API订阅密钥

### 3. 获取以下信息

申请成功后，你需要获取：

| 信息 | 说明 | 示例 |
|------|------|------|
| **Username** | ERCOT API用户名 | `your.email@example.com` |
| **Password** | ERCOT API密码 | `YourPassword123` |
| **Public API Key** | 公开API订阅密钥 | `f263c033603e4a06...` |
| **ESR API Key** | ESR API订阅密钥（可选）| `ee4e781cb6aa441f...` |

### 4. 验证新的认证端点

ERCOT可能已更改认证方式，需要确认：
- 新的Token URL是什么
- 认证流程是否有变化
- Client ID是否仍然相同

---

## 更新GitHub Secrets

### 方法1：使用脚本（推荐）

创建更新脚本：
```bash
cd ~/projects/ercot-scraper

cat > update-ercot-secrets.sh << 'EOF'
#!/bin/bash
REPO="lanxindeng8/ercot-scraper"

read -p "ERCOT Username: " USERNAME
read -p "ERCOT Password: " PASSWORD
read -p "Public API Key: " PUBLIC_KEY
read -p "ESR API Key: " ESR_KEY

echo "$USERNAME" | gh secret set ERCOT_API_USERNAME --repo="$REPO"
echo "$PASSWORD" | gh secret set ERCOT_API_PASSWORD --repo="$REPO"
echo "$PUBLIC_KEY" | gh secret set ERCOT_PUBLIC_API_SUBSCRIPTION_KEY --repo="$REPO"
echo "$ESR_KEY" | gh secret set ERCOT_ESR_API_SUBSCRIPTION_KEY --repo="$REPO"

echo "✅ ERCOT凭据已更新！"
EOF

chmod +x update-ercot-secrets.sh
./update-ercot-secrets.sh
```

### 方法2：手动更新

```bash
REPO="lanxindeng8/ercot-scraper"

echo "YOUR_USERNAME" | gh secret set ERCOT_API_USERNAME --repo="$REPO"
echo "YOUR_PASSWORD" | gh secret set ERCOT_API_PASSWORD --repo="$REPO"
echo "YOUR_PUBLIC_KEY" | gh secret set ERCOT_PUBLIC_API_SUBSCRIPTION_KEY --repo="$REPO"
echo "YOUR_ESR_KEY" | gh secret set ERCOT_ESR_API_SUBSCRIPTION_KEY --repo="$REPO"
```

### 方法3：通过GitHub网页

1. 访问：https://github.com/lanxindeng8/ercot-scraper/settings/secrets/actions
2. 更新以下4个secrets：
   - `ERCOT_API_USERNAME`
   - `ERCOT_API_PASSWORD`
   - `ERCOT_PUBLIC_API_SUBSCRIPTION_KEY`
   - `ERCOT_ESR_API_SUBSCRIPTION_KEY`

---

## 更新代码（如果API端点已更改）

### 如果ERCOT更改了认证端点

编辑 `src/ercot_client.py`：

```python
# 找到这一行（约第32行）
TOKEN_URL = "https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1A_ResourceOwnerv2/oauth2/v2.0/token"

# 替换为新的端点
TOKEN_URL = "新的认证端点URL"
```

### 如果Client ID已更改

```python
# 找到这一行（约第33行）
CLIENT_ID = "e9b8f377-e530-42f1-9988-c35ecba37e6f"

# 替换为新的Client ID
CLIENT_ID = "新的Client ID"
```

### 提交更改

```bash
cd ~/projects/ercot-scraper

git add src/ercot_client.py
git commit -m "Update ERCOT API endpoints

- Update TOKEN_URL to new authentication endpoint
- Update CLIENT_ID if changed

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push origin master
```

---

## 测试新配置

### 1. 本地测试（可选）

```bash
cd ~/projects/ercot-scraper

# 设置环境变量
export ERCOT_API_USERNAME="your_username"
export ERCOT_API_PASSWORD="your_password"
export ERCOT_PUBLIC_API_SUBSCRIPTION_KEY="your_key"
export ERCOT_ESR_API_SUBSCRIPTION_KEY="your_esr_key"
export INFLUXDB_URL="https://us-east-1-1.aws.cloud2.influxdata.com"
export INFLUXDB_ORG="0691bd05e35a51b2"
export INFLUXDB_BUCKET="ercot"
export INFLUXDB_TOKEN="your_influxdb_token"

# 安装依赖
pip install -r requirements.txt

# 测试认证
cd src
python -c "from ercot_client import create_client_from_env; client = create_client_from_env(); client.get_token(); print('认证成功！')"
```

### 2. GitHub Actions测试

```bash
# 手动触发workflow
gh workflow run "ERCOT LMP Scraper" --repo=lanxindeng8/ercot-scraper

# 查看运行状态
sleep 10
gh run list --repo=lanxindeng8/ercot-scraper --limit 1

# 查看详细日志
gh run view --repo=lanxindeng8/ercot-scraper --log
```

### 3. 验证数据写入InfluxDB

1. 登录 InfluxDB Cloud：https://cloud2.influxdata.com
2. 进入 Data Explorer
3. 选择 bucket: `ercot`
4. 选择 measurement: `lmp_by_settlement_point`
5. 查看是否有新数据

---

## 故障排查

### 问题1：仍然显示404错误

**可能原因**：
- 认证端点URL不正确
- Client ID已更改

**解决**：
1. 查看ERCOT API文档确认新端点
2. 更新 `src/ercot_client.py` 中的URL
3. 重新测试

### 问题2：401 Unauthorized

**可能原因**：
- 用户名或密码错误
- API订阅密钥无效

**解决**：
1. 确认ERCOT账户仍然有效
2. 重新生成API订阅密钥
3. 更新GitHub Secrets

### 问题3：403 Forbidden

**可能原因**：
- API访问权限未获批准
- 订阅已过期

**解决**：
1. 登录ERCOT开发者门户检查订阅状态
2. 续订或重新申请API访问

---

## 当前配置状态

### ✅ 已完成配置

| 组件 | 状态 | 值 |
|------|------|-----|
| GitHub仓库 | ✅ 完成 | https://github.com/lanxindeng8/ercot-scraper |
| InfluxDB URL | ✅ 已配置 | `https://us-east-1-1.aws.cloud2.influxdata.com` |
| InfluxDB Org | ✅ 已配置 | `0691bd05e35a51b2` |
| InfluxDB Bucket | ✅ 已配置 | `ercot` |
| InfluxDB Token | ✅ 已配置 | ✓ |
| GitHub Actions | ✅ 部署完成 | 3个workflows |

### ⏳ 等待配置

| 组件 | 状态 | 下一步 |
|------|------|--------|
| ERCOT API凭据 | ⏳ 待更新 | 重新申请API访问 |
| ERCOT认证端点 | ⏳ 待确认 | 确认新端点URL |

---

## 准备就绪检查清单

在重新启用scrapers之前，确认：

- [ ] ERCOT API访问已获批准
- [ ] 获得新的用户名和密码
- [ ] 获得新的API订阅密钥
- [ ] 确认认证端点URL
- [ ] 更新GitHub Secrets
- [ ] （如需要）更新代码中的端点URL
- [ ] 测试认证成功
- [ ] 验证数据写入InfluxDB

---

## 快速启动（当ERCOT API准备好后）

```bash
# 1. 更新GitHub Secrets
cd ~/projects/ercot-scraper
./update-ercot-secrets.sh  # 或手动更新

# 2. 如果API端点已更改，更新代码
# 编辑 src/ercot_client.py，更新TOKEN_URL和CLIENT_ID
# git commit && git push

# 3. 测试运行
gh workflow run "ERCOT LMP Scraper" --repo=lanxindeng8/ercot-scraper

# 4. 查看结果
gh run view --repo=lanxindeng8/ercot-scraper --log

# 5. 启用定时运行（workflows自动每5分钟运行）
# 无需额外操作，GitHub Actions会自动执行
```

---

## 联系支持

### ERCOT支持
- 开发者门户：https://developer.ercot.com/
- 技术支持：查看开发者门户的联系方式

### 项目支持
- GitHub Issues：https://github.com/lanxindeng8/ercot-scraper/issues
- 文档：[SETUP.md](./SETUP.md) | [USAGE.md](./USAGE.md)

---

**最后更新**：2026-01-22
**状态**：等待ERCOT API访问
