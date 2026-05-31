# New API 上线方案

推荐把 New API 作为生产底座：

- 用户注册登录
- 充值和兑换码
- API Token 管理
- 用量日志
- 渠道管理
- 模型价格管理
- 分组计费
- 管理员权限

本站负责：

- 品牌首页
- 模型与价格页
- Claude Code / Cursor / Cline 教程
- OpenAI-compatible 文档
- 状态页
- SEO 获客页

## 2026-05 上游组合

| 优先级 | 平台 | 类型 | 用途 |
|---|---|---|---|
| 1 | PoloAPI / weelinking | 稳定中价 | Claude / GPT / Gemini 主力稳定渠道，高权重 |
| 2 | RightCode | 极致低价 | Claude / GPT / Gemini 低价补充，低权重 |
| 3 | jiekou.ai / APIMart / token.chhai.cn | 全能补充 | 模型补货、备用 |
| 4 | SiliconFlow | 国产最优 | 第二阶段再开放国产模型 |

首发只开放 7 个模型，每个模型至少保留 2 个渠道。稳定渠道权重高，低价渠道权重低，开启失败自动切换。

## 域名建议

```text
www.yourdomain.com   官网和文档
api.yourdomain.com   OpenAI-compatible API
app.yourdomain.com   New API 用户/管理员后台
```

## 部署

```bash
docker compose -f ops/newapi-compose.yml up -d
python3 app.py --init-db --seed --host 0.0.0.0 --port 8001
```

## NewAPI 渠道配置顺序

1. 添加 PoloAPI 或 weelinking，作为 Claude / GPT / Gemini 稳定主力。
2. 添加 RightCode，作为 Claude / GPT / Gemini 的低价补充，低权重。
3. 添加 jiekou.ai、APIMart、token.chhai.cn，做模型补货和备用。
4. 只开放 `claude-opus-4-7`、`claude-sonnet-4-6`、`claude-haiku-4-5`、`gpt-5.5`、`gpt-5.4`、`gpt-5.4-mini`、`gemini-3.5-flash`。
5. 每个首发模型设置至少 2 个渠道，开启 failover。
6. 配置分组倍率和用户等级：Pay Go、Starter、Builder、Team。
7. 配置充值：微信/支付宝、兑换码、人工充值兜底。
8. 用 Cherry Studio、Claude Code、Cursor、curl 全链路测试。

上线前必须修改：

- `SESSION_SECRET`
- `CRYPTO_SECRET`
- `ADMIN_TOKEN`
- 所有上游 API Key
- 支付配置
- 计费币种、最低充值金额和汇率规则
- 邮件配置
- 域名和 HTTPS

## 角色划分

公开访客：

- 看模型
- 看价格
- 看文档
- 登录/注册

普通用户：

- 充值
- 创建 API Key
- 查看用量
- 查看扣费

## 计费口径

第一版默认按 `CNY` 维护用户余额、充值订单和模型扣费展示，最低充值金额默认 `¥10`，可通过 `BILLING_CURRENCY`、`BILLING_SYMBOL`、`MIN_RECHARGE_AMOUNT` 调整。

正式接 NewAPI 时，用户钱包统一用人民币，支付层接易支付/聚合支付支持支付宝和微信；上游成本如果是美元，由账务层维护汇率和折算记录。

## 测试清单

- Claude Code：长上下文、工具调用、Prompt Caching、流式输出。
- Cursor / Cline：OpenAI-compatible Base URL、模型名、失败重试。
- Cherry Studio：模型列表、文本、图像、Embedding。
- 高峰期：连续请求、429、超时、failover 是否生效。
- 计费：NewAPI 日志、上游账单、本项目定价表是否一致。

管理员：

- 配渠道
- 配模型
- 看日志
- 看毛利
- 管用户
- 管充值订单
