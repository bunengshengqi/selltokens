# Claude Code / Cursor / Cline 配置

## Cursor / Cline

```text
API Provider: OpenAI Compatible
Base URL: https://api.yourdomain.com/v1
API Key: YOUR_API_KEY
Model: yu-code-auto
```

也可以直接指定：

```text
claude-sonnet-economy
claude-sonnet-stable
qwen-coder
deepseek-chat
```

## Claude Code

如果客户端支持 Anthropic-compatible 环境变量：

```bash
export ANTHROPIC_BASE_URL=https://api.yourdomain.com
export ANTHROPIC_AUTH_TOKEN=YOUR_API_KEY
export ANTHROPIC_MODEL=claude-sonnet-economy
```

如果客户端支持 OpenAI-compatible，则使用：

```text
Base URL: https://api.yourdomain.com/v1
API Key: YOUR_API_KEY
Model: yu-code-auto
```

注意：Claude Code 是工具名，不是模型名。平台侧模型名应该明确写成 `claude-sonnet-economy`、`claude-sonnet-stable` 或 `yu-code-auto`。
