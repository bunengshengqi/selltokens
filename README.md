# 996 Tokens

面向 Claude Code、Cursor、Cline、RPA 和 Agent 开发者的多模型 API 服务。

> 一个 API Key 接入 Claude / GPT / Gemini，美元余额计费，人民币支付按固定汇率折算，当前只向海外用户开放。

## 生产地址

| 用途 | 地址 |
| --- | --- |
| 官网 | https://www.996tokens.com |
| 用户控制台 | https://app.996tokens.com |
| API 调用地址 | https://api.996tokens.com |

## 首发模型

| 系列 | 模型 |
| --- | --- |
| Claude | `claude-fable-5`、`claude-opus-4-7`、`claude-sonnet-4-6`、`claude-haiku-4-5` |
| GPT | `gpt-5.5`、`gpt-5.4`、`gpt-5.4-mini` |
| Gemini | `gemini-3.5-flash` |

## 充值规则

- 注册不直接赠送额度。
- 账户余额与模型单价按 USD 计费，微信支付按固定汇率折算为人民币。
- 新用户首笔充值后自动加赠 $1，每个账户仅限一次。
- 充值档位：$3、$5、$10、$20、$50、$100。
- 最低充值金额：$3。
- 当前保留微信支付、兑换码和人工处理入口。

## 本地启动

```bash
python3 app.py --init-db --seed --host 127.0.0.1 --port 8001
```

本地预览：

| 页面 | 地址 |
| --- | --- |
| 首页 | http://127.0.0.1:8001/ |
| 价格 | http://127.0.0.1:8001/pricing |
| 文档 | http://127.0.0.1:8001/docs |
| 状态页 | http://127.0.0.1:8001/status |

本地默认测试 Key：

```text
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

## 页面分工

- `www.996tokens.com`：公开官网、价格、文档、状态、客服。
- `app.996tokens.com`：登录、注册、充值、API Key、用量记录。
- `api.996tokens.com`：OpenAI 兼容 API 调用入口。

## 上线检查

- [ ] 首页、价格页、状态页、客服页不展示内部信息。
- [ ] 只展示首发模型和用户价格。
- [ ] 注册不直接赠送额度。
- [ ] 充值加赠规则生效。
- [ ] 支付回调正常。
- [ ] API Key 创建与调用正常。
- [ ] “只向海外用户开放”声明已展示。
