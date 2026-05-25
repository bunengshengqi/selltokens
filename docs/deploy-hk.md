# 香港服务器完整部署手册

> 适用：Ubuntu 22.04 / Debian 12，香港 VPS，无需备案，可直连 OpenAI/Anthropic/Google。

---

## 一、前置条件

| 项目 | 说明 |
|------|------|
| 服务器 | 香港 VPS，最低 1 核 1G（建议 2核2G） |
| 域名 | 已购买，并解析到服务器 IP |
| 子域名 | `yourdomain.com`（官网）、`api.yourdomain.com`（API）、`app.yourdomain.com`（New API 用户后台） |
| 上游 API Key | 至少注册一个聚合商账号（见下文第二节） |

---

## 二、获取上游 API Key（御三家）

**当前主力：chhai**

| 聚合商 | 注册地址 | 覆盖模型 | 备注 |
|--------|---------|---------|------|
| chhai | https://token.chhai.cn | GPT-4o、Claude Sonnet、Gemini Flash | **当前使用** |
| PoloAPI | https://poloai.top | GPT-4o、Claude Sonnet、Gemini Flash | 生产切换备用 |
| weelinking | https://api.weelinking.com | GPT-4o、Claude、Gemini | 备用 |

注册 chhai，充值后生成 API Key，填入 `.env` 的 `CHHAI_API_KEY`。

**可选：直接注册官方账号（有信用卡时使用）**

| 官方 | 地址 | 备注 |
|------|------|------|
| OpenAI | https://platform.openai.com | 需国际信用卡 |
| Anthropic | https://console.anthropic.com | 需国际信用卡 |
| Google AI | https://aistudio.google.com | 免费额度，无需信用卡 |

---

## 三、服务器初始化

```bash
# 更新系统
apt update && apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker

# 安装 Docker Compose Plugin
apt install -y docker-compose-plugin

# 安装 certbot（Let's Encrypt SSL 证书）
apt install -y certbot

# 验证
docker --version
docker compose version
```

---

## 四、拉取代码

```bash
cd /opt
git clone https://github.com/yourname/selltokens.git
cd selltokens
```

---

## 五、申请 SSL 证书

```bash
# 先确保 80 端口没被占用，然后申请证书
certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  -d api.yourdomain.com \
  -d app.yourdomain.com

# 证书默认保存在 /etc/letsencrypt/live/yourdomain.com/
# 创建 certs 目录并软链接
mkdir -p /opt/selltokens/certs/yourdomain.com
ln -s /etc/letsencrypt/live/yourdomain.com/fullchain.pem \
      /opt/selltokens/certs/yourdomain.com/fullchain.pem
ln -s /etc/letsencrypt/live/yourdomain.com/privkey.pem \
      /opt/selltokens/certs/yourdomain.com/privkey.pem
```

---

## 六、配置环境变量

```bash
cd /opt/selltokens
cp .env.example .env
nano .env   # 或 vim .env
```

**必填项：**

```bash
# 1. 改为你的真实域名
PUBLIC_API_BASE=https://api.yourdomain.com
APP_BASE_URL=https://app.yourdomain.com
LOGIN_URL=https://app.yourdomain.com/login
REGISTER_URL=https://app.yourdomain.com/register
NEWAPI_BASE_URL=https://app.yourdomain.com

# 2. 生成随机 Admin Token（必须改！）
# 运行：python3 -c "import secrets; print(secrets.token_hex(32))"
ADMIN_TOKEN=你生成的随机字符串

# 3. 填入上游 API Key（当前用 chhai）
CHHAI_API_KEY=你的chhai密钥
# 生产时可同步填入 PoloAPI 作为备用：
# POLOAPI_API_KEY=

# 4. 关掉演示门户（用 New API 做用户后台）
DEMO_PORTAL_ENABLED=false
```

---

## 七、配置 New API 密钥

```bash
nano ops/docker-compose.prod.yml
```

找到以下两行，替换为随机字符串：
```yaml
SESSION_SECRET: 你生成的随机字符串1
CRYPTO_SECRET: 你生成的随机字符串2
```

生成方法：
```bash
openssl rand -hex 32   # 运行两次，分别用于两个字段
```

---

## 八、修改 Nginx 配置中的域名

```bash
# 把所有 yourdomain.com 替换为你的真实域名
sed -i 's/yourdomain.com/你的真实域名/g' ops/nginx.conf
```

---

## 九、启动所有服务

```bash
cd /opt/selltokens

# 创建数据目录
mkdir -p data/new-api

# 启动（首次会自动构建镜像）
docker compose -f ops/docker-compose.prod.yml up -d

# 查看日志
docker compose -f ops/docker-compose.prod.yml logs -f
```

等待约 30 秒，验证服务：
```bash
curl https://api.yourdomain.com/api/health
# 应返回：{"status": "ok", "service": "yu-gateway"}

curl https://app.yourdomain.com/api/status
# 应返回 New API 状态 JSON
```

---

## 十、配置 New API 渠道（御三家）

1. 浏览器打开 `https://app.yourdomain.com`
2. 首次访问自动进入注册页，注册管理员账号（第一个注册的自动为 admin）
3. 登录后进入 **渠道** → **添加渠道**

按御三家分别添加：

| 渠道 | 类型 | Base URL | API Key |
|------|------|---------|---------|
| PoloAPI（GPT） | OpenAI | https://poloai.top/v1 | 你的PoloAPI Key |
| PoloAPI（Claude） | Anthropic | https://poloai.top | 你的PoloAPI Key |
| PoloAPI（Gemini） | Google Gemini | https://poloai.top/v1 | 你的PoloAPI Key |

> New API 会自动测试渠道是否可用，绿灯即可。

---

## 十一、配置 New API 支付（Stripe）

New API 支持 Stripe 支付，香港服务器可直接使用。

1. 注册 Stripe 账号：https://stripe.com（个人可申请，审核 1-3 天）
2. 获取 API Key（Dashboard → Developers → API Keys）
3. New API 后台 → **系统设置** → **支付设置** → 填入 Stripe Key

---

## 十二、设置 SSL 证书自动续期

```bash
# 测试续期
certbot renew --dry-run

# 添加 cron 自动续期（每天检查一次）
echo "0 3 * * * certbot renew --quiet && docker exec nginx nginx -s reload" | crontab -
```

---

## 十三、防火墙设置

```bash
ufw allow 22    # SSH
ufw allow 80    # HTTP（重定向到 HTTPS）
ufw allow 443   # HTTPS
ufw enable
```

---

## 常用运维命令

```bash
# 查看所有容器状态
docker compose -f ops/docker-compose.prod.yml ps

# 重启某个服务
docker compose -f ops/docker-compose.prod.yml restart yu-gateway

# 更新代码后重新构建
git pull
docker compose -f ops/docker-compose.prod.yml up -d --build yu-gateway

# 查看实时日志
docker compose -f ops/docker-compose.prod.yml logs -f yu-gateway
docker compose -f ops/docker-compose.prod.yml logs -f new-api

# 备份数据库
cp data/gateway.sqlite3 data/gateway.sqlite3.bak.$(date +%Y%m%d)
```

---

## 上线检查清单

- [ ] 域名 DNS 已解析到服务器 IP
- [ ] SSL 证书申请成功，HTTPS 可访问
- [ ] `.env` 中 `ADMIN_TOKEN` 已改为随机字符串
- [ ] `.env` 中至少填入一个聚合商 API Key（POLOAPI 或 WEELINKING）
- [ ] New API SESSION_SECRET / CRYPTO_SECRET 已改为随机字符串
- [ ] New API 渠道测试通过（绿灯）
- [ ] Stripe 支付配置完成（或先用手动充值过渡）
- [ ] `/api/health` 返回 200
- [ ] 用测试 API Key 发一条请求验证路由正常
