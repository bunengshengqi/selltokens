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
    "model": "yu-chat-auto",
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
    model="yu-chat-auto",
    messages=[{"role": "user", "content": "帮我写一个 Python 爬虫"}],
)

print(resp.choices[0].message.content)
```

推荐模型：

- `yu-chat-auto`：通用自动路由
- `yu-code-auto`：AI 编程自动路由
- `yu-json`：结构化输出
- `claude-sonnet-economy`：Claude-like 经济线
- `claude-sonnet-stable`：Claude-like 稳定线

