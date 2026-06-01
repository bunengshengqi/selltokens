# 996 Tokens MVP 产品说明

本文件记录公开产品口径，不记录内部商业和后台实现细节。

## 产品定位

996 Tokens 是面向 Claude Code、Cursor、Cline、RPA 和 Agent 开发者的多模型 API 服务。

用户只需要：

1. 注册账户。
2. 充值余额。
3. 创建 API Key。
4. 在工具里替换 Base URL。

## 首发模型

| 系列 | 模型 |
| --- | --- |
| Claude | `claude-opus-4-7`、`claude-sonnet-4-6`、`claude-haiku-4-5` |
| GPT | `gpt-5.5`、`gpt-5.4`、`gpt-5.4-mini` |
| Gemini | `gemini-3.5-flash` |

## 用户页面

- 首页：展示产品、支持模型、Base URL、注册入口。
- 价格页：展示充值规则、月卡、模型单价。
- 文档页：展示 Cursor、Claude Code、OpenAI SDK、curl 示例。
- 状态页：展示 API、控制台、文档、支付服务是否正常。
- 关于页：展示产品介绍、支持模型、服务声明和联系方式。

## 充值规则

- 注册不直接赠送额度。
- 充值或购买月卡后自动加赠：
  - 小于 ¥100：加赠 ¥5。
  - 大于等于 ¥100：加赠 ¥10。
- 最低充值金额：¥10。
- 保留兑换码和人工处理入口。

## 对外文案禁区

公开页面和公开文档不得出现：

- 内部服务商名称。
- 内部结算信息。
- 内部商业模型。
- 后台系统名称。
- 内部路由、权重、容灾、风控实现。

## 接入示例

```bash
curl https://api.996tokens.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-4-5",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```
