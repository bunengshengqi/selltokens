# 996 Tokens 部署检查

## 服务器

- 2 核 2G 可承载第一版轻量上线。
- 推荐开启 HTTPS。
- 保留 `www`、`app`、`api` 三个入口。

## 域名

| 子域名 | 用途 |
| --- | --- |
| `www.yourdomain.com` | 官网、价格、文档、状态、关于 |
| `app.yourdomain.com` | 用户控制台 |
| `api.yourdomain.com` | API 调用地址 |

## 上线前检查

- [ ] 证书覆盖全部子域名。
- [ ] 首页、价格页、状态页、关于页不展示内部信息。
- [ ] 登录、注册、充值、API Key、用量记录可用。
- [ ] 首发模型调用测试通过。
- [ ] 支付成功后加赠规则生效。
- [ ] 页脚显示“只向海外用户开放”。

## 首发模型

- `claude-opus-4-7`
- `claude-sonnet-4-6`
- `claude-haiku-4-5`
- `gpt-5.5`
- `gpt-5.4`
- `gpt-5.4-mini`
- `gemini-3.5-flash`
