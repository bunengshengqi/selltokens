# OpenAI-compatible 接入

Base URL:

```text
https://api.yourdomain.com/v1
```

Chat Completions:

```bash
curl https://api.yourdomain.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-haiku-4-5",
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }'
```

Python SDK:

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://api.yourdomain.com/v1",
)

resp = client.chat.completions.create(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": "帮我写一个 Python 爬虫"}],
)

print(resp.choices[0].message.content)
```

推荐模型：

- `claude-opus-4-7`：高质量重任务
- `claude-sonnet-4-6`：Claude Code / Cursor 主力
- `claude-haiku-4-5`：轻量快速调用
- `gpt-5.5` / `gpt-5.4` / `gpt-5.4-mini`：OpenAI 系列
- `gemini-3.5-flash`：低延迟轻量任务
