# 996 Tokens — 多模型 API 分发平台

> 面向 AI 编程（Claude Code / Cursor）、RPA、Agent 开发者的多模型 API 网关。
> 一个 Key 首发接入 Claude / GPT / Gemini 七个核心模型，人民币余额按量计费，当前只向海外用户开放。

**生产地址：**

| 用途 | 地址 |
|------|------|
| 官网 | https://www.996tokens.com |
| 用户后台（充值 / Key / 用量） | https://app.996tokens.com |
| API 调用地址 | https://api.996tokens.com |

---

## 架构概览

```text
公开访客          普通用户              管理员
─────────         ──────────            ──────────────────
官网首页           控制台                渠道管理
价格页            余额 / 充值           用户管理
模型介绍          API Keys              订单 / 日志
文档              用量记录              模型倍率
注册 / 登录 入口                        毛利统计
        │                │                    │
        ▼                ▼                    ▼
   Yu Gateway        New API 用户后台    New API 管理后台
(www.996tokens.com)  (app.*)            (app.*/admin)
        │
        ▼
   Yu Gateway 路由层
   ├── 多上游候选池
   ├── 评分路由（延迟 × 稳定性 × 毛利）
   ├── 熔断 / 冷却 / 自动重试
   └── 毛利保护（min_margin 兜底）
        │
        ▼
   上游 API（chhai / PoloAPI / ISMaque / 御三家直连…）
```

---

## 首发模型

| 模型 | 加价策略 | 收费（输入/输出，¥/M tokens） |
|------|----------|-------------------------------|
| `claude-opus-4-7` | 上游成本 × 1.6 | 8 / 40 |
| `claude-sonnet-4-6` | 上游成本 × 1.35 | 4.05 / 20.25 |
| `claude-haiku-4-5` | 上游成本 × 1.3 | 1.3 / 6.5 |
| `gpt-5.5` | 上游成本 × 1.5 | 7.5 / 45 |
| `gpt-5.4` | 上游成本 × 1.35 | 3.375 / 20.25 |
| `gpt-5.4-mini` | 上游成本 × 1.3 | 0.975 / 5.85 |
| `gemini-3.5-flash` | 上游成本 × 1.3 | 0.65 / 3.9 |

第一版只开放以上 7 个模型，国产模型、图像、视频和 Embedding 后续逐步接入。

---

## 上游渠道

| 优先级 | Slug | 地址 | 覆盖模型 | 状态 |
|--------|------|------|---------|------|
| 1（主力） | `chhai` | token.chhai.cn | 御三家全线 | 默认启用 |
| 2 | `ismaque` | ismaque.org | 御三家全线 | 备用 |
| 3 | `poloapi` | poloai.top | Claude / GPT / Gemini | 备用 |
| 4 | `jiekou` | jiekou.ai | Claude / GPT | 备用 |
| 5 | `weelinking` | weelinking.com | 御三家 | 备用 |
| 直连 | `openai-direct` / `anthropic-direct` / `google-ai` | 官方 | 各自模型 | 按需启用 |
| 国产 | `siliconflow` / `deepseek` / `qwen` / `doubao` | 各官方 | 国产模型 | 第二阶段启用 |

---

## 本地快速启动

```bash
# 克隆并安装依赖
git clone https://github.com/bunengshengqi/selltokens.git
cd selltokens
pip install -r requirements.txt

# 复制并修改配置
cp .env.example .env

# 启动（自动初始化 DB + 种子数据）
python3 app.py --init-db --seed --host 127.0.0.1 --port 8001
```

本地预览地址：

| 页面 | 地址 |
|------|------|
| 首页 | http://127.0.0.1:8001/ |
| 价格 | http://127.0.0.1:8001/pricing |
| 文档 | http://127.0.0.1:8001/docs |
| 状态页 | http://127.0.0.1:8001/status |
| 管理后台 | http://127.0.0.1:8001/admin |

本地默认测试 Key：

```
sk-yu-demo-local
```

测试调用：

```bash
curl http://127.0.0.1:8001/v1/chat/completions \
  -H "Authorization: Bearer sk-yu-demo-local" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-4-5",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

---

## 配置文件

复制 `.env.example` 为 `.env`，按需填写：

```bash
# 主力上游（必填其中至少一个）
CHHAI_API_KEY=          # token.chhai.cn
ISMAQUE_API_KEY=        # ismaque.org
POLOAPI_API_KEY=        # poloai.top
JIEKOU_API_KEY=         # jiekou.ai

# 御三家直连（可选）
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=

# 域名配置
PUBLIC_API_BASE=https://api.yourdomain.com
APP_BASE_URL=https://app.yourdomain.com

# 安全（上线前必须修改）
ADMIN_TOKEN=replace-with-random-token
DEMO_PORTAL_ENABLED=false
```

---

## 生产部署（Docker Compose）

```bash
# 服务器上拉代码
git clone https://github.com/bunengshengqi/selltokens.git /opt/selltokens
cd /opt/selltokens

# 配置环境变量
cp .env.example .env && vim .env

# 申请 SSL 证书（Let's Encrypt）
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com \
  -d api.yourdomain.com -d app.yourdomain.com

# 启动全栈（Yu Gateway + New API + Nginx）
docker compose -f ops/docker-compose.prod.yml up -d
```

详细步骤参考 `docs/deploy-hk.md`。

---

## 赚钱逻辑

```text
用户充值 → 用余额调 API → 你向上游买 Token → 差价 = 利润
```

**价格设置位置：**

- `gateway/db.py` → `model_prices` 表：设置对用户的**售价**（CNY/M tokens）
- `gateway/db.py` → `profile` 字典：设置上游**成本比例**（例如 0.70 = 成本是售价的 70%，利润 30%）
- New API 管理后台 → **系统设置 → 模型倍率设置**：可在线调整每个模型的倍率

**示例（gpt-4o-mini）：**

| 项目 | 数值 |
|------|------|
| 向用户收（输入） | ¥1.4 / M tokens |
| 付给 chhai（70%） | ¥0.98 / M tokens |
| **利润** | **¥0.42 / M tokens（30%）** |

管理员在 New API → **订单管理** 可看到每笔充值记录；**数据看板** 可看用量和消耗。

---

## 变现漏斗

第一版优先做三件事：

| 环节 | 标准 | 目的 |
|------|------|------|
| 注册风控 | 新用户注册 ¥0，必须充值后才送 | 杜绝批量注册直接拿额度 |
| 充值转化 | 100 以下送 ¥5，100 以上送 ¥10 | 用真实支付触发加赠 |
| 邀请裂变 | 邀请奖励绑定首充 | 未首充不发放奖励，降低薅羊毛 |

充值阶梯建议：

| 档位 | 用户支付 | 到账/权益 |
|------|------:|------:|
| 注册账户 | ¥0 | ¥0 |
| 小额充值 | ¥10 | ¥15 等值额度 |
| 入门月卡 | ¥29/月 | ¥34 等值额度 |
| 开发者月卡 | ¥69/月 | ¥74 等值额度 |
| 专业月卡 | ¥129/月 | ¥139 等值额度 |
| 团队月卡 | ¥299/月 | ¥309 等值额度 |
| 大额充值 | ¥500 | ¥510 等值额度 |

更完整的运营规则见 `docs/growth-funnel.md`。

---

## 支付说明

在线充值目前仅支持**微信支付**，主要面向**海外用户**。  
国内用户如需充值，请联系管理员获取**兑换码**。

支付渠道：[快小铺（haoshoumi.com）](https://www.haoshoumi.com) — 易支付协议，New API 原生支持。

---

## 上线前清单

- [ ] `.env` 填入真实域名、站点名、密钥
- [ ] 申请 SSL 证书覆盖全部子域名
- [ ] 至少充值一个上游账号（建议 chhai 或 PoloAPI，各 ¥100 起测）
- [ ] New API 后台创建管理员账号，配置模型倍率
- [ ] New API → 系统设置 → 通用设置：把文档链接改为 `https://app.996tokens.com/about#docs`
- [ ] 运行 `python3 ops/newapi_branding.py` 写入 NewAPI About / Footer 品牌内容
- [ ] 配置微信支付（快小铺）并测试充值流程
- [ ] 关闭 `DEMO_PORTAL_ENABLED=false`
- [ ] 设置强随机 `ADMIN_TOKEN`
- [ ] 用 Claude Code / Cursor / curl 小范围测试 3–5 个用户

---

## 技术栈

| 组件 | 说明 |
|------|------|
| Yu Gateway | Python 3.11 + FastAPI，多上游路由、评分、熔断 |
| New API | Go，用户管理、充值、Token、渠道、日志（Docker 镜像） |
| Nginx | HTTPS 反代 + HTTP→HTTPS 跳转 |
| SQLite | 轻量数据库，单文件，适合 2C2G 小机器 |
| Docker Compose | 一键拉起全栈 |
