# Claude Code / Cursor / Cline 配置

## Cursor / Cline

```text
API Provider: OpenAI Compatible
Base URL: https://api.yourdomain.com/v1
API Key: YOUR_API_KEY
Model: claude-sonnet-4-6
```

也可以直接指定：

```text
claude-fable-5
claude-opus-4-7
claude-sonnet-4-6
claude-haiku-4-5
gemini-3.5-flash
```

## Claude Code

如果客户端支持 Anthropic-compatible 环境变量：

```bash
export ANTHROPIC_BASE_URL=https://api.yourdomain.com
export ANTHROPIC_AUTH_TOKEN=YOUR_API_KEY
export ANTHROPIC_MODEL=claude-sonnet-4-6
```

如果客户端支持 OpenAI-compatible，则使用：

```text
Base URL: https://api.yourdomain.com/v1
API Key: YOUR_API_KEY
Model: claude-sonnet-4-6
```

注意：Claude Code 是工具名，不是模型名。平台侧模型名应该明确写成 `claude-fable-5`、`claude-sonnet-4-6`、`claude-haiku-4-5` 或 `claude-opus-4-7`。
