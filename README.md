# Yu Gateway

面向 AI 编程、RPA、Agent 开发者的多模型 API 分发平台。

当前仓库包含两部分：

```text
官网 / 文档 / 获客页：本项目
用户登录 / 充值 / Token / 渠道 / 日志 / 模型管理：推荐接 New API
```

本地版本也内置了一个轻量 API 网关和模拟用户后台，方便上线前验证产品形态和接口链路。

## 产品形态

参考方向：

- `token.chhai.cn`：模型卡片、价格直出、登录注册入口
- `jiekou.ai`：Claude Code / Cursor 用户转化路径
- `apimart.ai`：模型市场、统一 API、开发者文档
- `New API`：生产后台、渠道、Token、充值、日志、模型和权限管理

生产版上游组合：

| 优先级 | 平台 | 类型 | 建议用途 |
|---|---|---|---|
| 1 | RightCode | 极致低价 | Claude / GPT / Gemini 低价补充，赚差价，但低权重 |
| 2 | PoloAPI / weelinking | 稳定中价 | 主力稳定渠道，高权重承接核心流量 |
| 3 | SiliconFlow | 国产最优 | DeepSeek、Qwen、豆包、GLM、Embedding 主力 |
| 4 | jiekou.ai / APIMart / token.chhai.cn | 全能补充 | 模型补货、图像视频、备用线路 |

角色划分：

```text
公开访客：模型、价格、文档、Claude Code、状态页、登录、注册
普通用户：控制台、充值、API Keys、用量记录
管理员：运营面板、New API 后台、上游渠道、用户、订单、日志、毛利
```

## 已实现

- OpenAI-compatible `/v1/chat/completions`
- `/v1/models` 模型列表
- 用户 API Key、余额扣费、请求日志
- economy / stable / auto 三线路价格体系
- 多上游候选、评分路由、利润保护、熔断和重试
- 已种子化 RightCode、PoloAPI、weelinking、SiliconFlow、APIMart、jiekou.ai 等待测上游
- Mock 上游用于无真实 Key 时验证全链路
- 模型页、价格页、文档页、用户控制台、充值页、API Keys、用量记录、运营面板
- 价格页已改成高质感 Free / Pro / Max / Ultra 套餐卡、月付/年付入口、模型倍率、100 人同时在线目标说明和按量单价组合
- 充值页支持固定套餐和自定义金额，第一版默认人民币余额，最低 `¥10`
- New API 上线方案页和 Docker Compose 模板

## Quick Start

```bash
python3 app.py --init-db --seed --host 127.0.0.1 --port 8001
```

打开：

- 首页：http://127.0.0.1:8001/
- 价格：http://127.0.0.1:8001/pricing
- 文档：http://127.0.0.1:8001/docs
- Claude Code：http://127.0.0.1:8001/claude-code
- 状态页：http://127.0.0.1:8001/status
- 登录：http://127.0.0.1:8001/login
- 注册：http://127.0.0.1:8001/register
- 控制台：http://127.0.0.1:8001/dashboard
- 充值：http://127.0.0.1:8001/recharge
- API Keys：http://127.0.0.1:8001/keys
- 用量记录：http://127.0.0.1:8001/usage
- 后台：http://127.0.0.1:8001/admin
- New API 方案：http://127.0.0.1:8001/newapi

本地会种子化一个测试 Key：

```text
sk-yu-demo-local
```

测试调用：

```bash
curl http://127.0.0.1:8001/v1/chat/completions \
  -H "Authorization: Bearer sk-yu-demo-local" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "yu-chat-auto",
    "messages": [
      {"role": "user", "content": "你好，帮我写一个 Python 爬虫"}
    ]
  }'
```

## 配置真实上游

默认真实上游是 disabled，Mock 上游是 active。要接入真实上游：

1. 在环境变量里配置上游 Key，例如 `SILICONFLOW_API_KEY`、`RIGHTCODE_API_KEY`、`POLOAPI_API_KEY`、`WEELINKING_API_KEY`、`JIEKOU_API_KEY`、`APIMART_API_KEY`。
2. 将 SQLite 里的对应 provider 改成 `active`，并设置 `balance >= 20`。
3. 确认 `provider_model_cost` 已存在对应模型映射。

也可以用管理 API 创建或更新上游：

```bash
curl http://127.0.0.1:8001/admin/providers \
  -H "X-Admin-Token: change-me-admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "deepseek",
    "name": "DeepSeek",
    "base_url": "https://api.deepseek.com/v1",
    "api_key_env": "DEEPSEEK_API_KEY",
    "type": "openai",
    "status": "active",
    "priority": 20,
    "balance": 100
  }'
```

生产环境务必修改 `ADMIN_TOKEN`，并把后台放在登录或内网访问之后。

## NewAPI 渠道策略

每个热门模型至少接 2-3 个上游：

| 模型线 | 主渠道 | 低价补充 | 备用 |
|---|---|---|---|
| Claude Sonnet 最新 | PoloAPI / weelinking | RightCode | jiekou.ai |
| GPT-5.x / Codex | PoloAPI / weelinking | RightCode Codex | APIMart |
| Gemini Pro / Flash | PoloAPI / weelinking | RightCode Gemini | APIMart |
| DeepSeek / Qwen / 豆包 | SiliconFlow | 官方直连 | PoloAPI |
| 图像 / 视频 | APIMart / SiliconFlow | jiekou.ai | token.chhai.cn |

NewAPI 里建议：

- 稳定渠道权重高，低价渠道权重低。
- 开启失败自动切换和重试，热门模型至少 3 次 failover。
- 对外价格初期加价 25%-60%，国产模型可以更高，先用免费试用和小额套餐获客。
- RightCode 这类极低价渠道只做补充和利润优化，不能单独承载生产主链路。

## 计费币种

第一版面向国内用户，默认按 `CNY` 展示余额、充值订单和用量扣费，最低充值 `¥10`。生产环境的真实支付、兑换码和人工充值交给 NewAPI。

相关环境变量：

```bash
BILLING_CURRENCY=CNY
BILLING_SYMBOL=¥
MIN_RECHARGE_AMOUNT=10
```

上游账单可能是美元或人民币，生产记账时要在 NewAPI 或账务层记录汇率和折算来源，不要把汇率硬编码到页面文案里。

## 推荐上线架构

上线最快路径：

```text
官网 / 文档 / SEO 页面：本项目
用户注册 / 登录 / 充值 / Token / 用量 / 渠道 / 模型：New API
API 网关域名：优先 New API，后续再接本项目 Router 做利润保护和自动路由
HTTPS / 反代：Nginx 或 Caddy
```

100 人同时在线目标建议：

```text
NewAPI + MySQL/PostgreSQL + Redis：生产底座
官网本项目：静态获客和文档入口
API 域名：优先走 NewAPI
上游：热门模型至少 2-3 个渠道并开启 failover
服务器：2C2G 可小流量起步，100 人稳定使用建议 2C4G 起，增长后升 4C8G
```

New API 推荐部署：

```bash
docker compose -f ops/newapi-compose.yml up -d
```

上线前把 `.env` 改成真实域名：

```bash
SITE_NAME=你的品牌名
PUBLIC_API_BASE=https://api.yourdomain.com
APP_BASE_URL=https://app.yourdomain.com
LOGIN_URL=https://app.yourdomain.com/login
REGISTER_URL=https://app.yourdomain.com/register
ADMIN_CONSOLE_URL=https://app.yourdomain.com/admin
NEWAPI_BASE_URL=https://app.yourdomain.com
CORS_ALLOW_ORIGIN=https://www.yourdomain.com
DEMO_PORTAL_ENABLED=false
BILLING_CURRENCY=CNY
BILLING_SYMBOL=¥
MIN_RECHARGE_AMOUNT=10
SILICONFLOW_API_KEY=
RIGHTCODE_API_KEY=
POLOAPI_API_KEY=
WEELINKING_API_KEY=
JIEKOU_API_KEY=
APIMART_API_KEY=
```

域名建议：

```text
www.yourdomain.com   官网、价格、文档、SEO 页面
api.yourdomain.com   OpenAI-compatible API
app.yourdomain.com   New API 用户/管理员后台
status.yourdomain.com 可选状态页
```

## 管理 API

生成用户 API Key：

```bash
curl http://127.0.0.1:8001/admin/api-keys \
  -H "X-Admin-Token: change-me-admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tester@example.com",
    "username": "tester",
    "balance": 10,
    "name": "first key"
  }'
```

健康检查：

```bash
curl http://127.0.0.1:8001/api/health
```

模型列表：

```bash
curl http://127.0.0.1:8001/v1/models
```

## 部署建议

第一版可以用 Docker Compose 跑服务，前面挂 Nginx/Caddy 做 HTTPS：

```bash
docker compose -f ops/docker-compose.yml up -d --build
```

推荐域名：

- `www.xxx.com` 指向本站
- `api.xxx.com` 指向 API 网关
- `app.xxx.com` 指向 New API 后台
- `docs.xxx.com` 可直接指向本站 `/docs`

## 已实现的 MVP 范围

已覆盖：

- 至少 10 个模型名
- API Key 和余额扣费
- 用户控制台、演示充值、自定义金额、充值订单、API Key 自助创建、用量记录
- OpenAI-compatible 调用
- 上游池、成本表、售价表
- 毛利阈值过滤
- economy / stable / auto 路由权重
- 连续失败熔断、429 冷却、401/403 下线
- Claude Code / Cursor / curl / OpenAI SDK 文档

未内置：

- 真实充值支付
- 完整生产登录注册系统，推荐交给 New API
- Nginx/HTTPS 自动签发
- 上游价格自动采集
- 多模态生成任务队列

## 上线前清单

- 修改 `.env` 里的域名、站点名和密钥
- 部署 `ops/newapi-compose.yml`
- 配置 Nginx/Caddy HTTPS
- 在 New API 里创建管理员账号
- 配置 SiliconFlow、RightCode、PoloAPI 或 weelinking、jiekou.ai、APIMart 等上游渠道
- 每家上游先充值 100-300 元，完成兼容性和稳定性测试后再扩大额度
- 配置模型价格和分组倍率
- 接入微信/支付宝、兑换码、人工充值兜底
- 关闭或保护本地模拟后台
- 生产环境设置 `DEMO_PORTAL_ENABLED=false`
- 生产环境设置 `LOGIN_URL`、`REGISTER_URL`、`APP_BASE_URL` 指向 NewAPI 用户后台，官网 `/login`、`/register` 会直接跳转
- 生产环境设置强随机 `ADMIN_TOKEN`，访问本项目 `/admin` 时使用 `?token=...` 或反代到内网
- 生产环境设置 `ALLOW_DEFAULT_ADMIN_ON_LOCALHOST=false`，默认开发 token 只允许本机预览
- 生产环境设置 `CORS_ALLOW_ORIGIN=https://www.yourdomain.com`
- 用 Cherry Studio、Claude Code、Cursor、curl 小范围测试 3-5 个用户
