# 多模型 API 分发平台 MVP 开发方案

> 目标：参考 `token.chhai.cn`、`jiekou.ai`、`apimart.ai` 的产品形态，今晚先上线一个可用的 **多模型 API 分发平台 MVP**。  
> 核心要求：上游成本低、模型更新快、御三家可用、国产模型接入、平台自己有利润、上游崩溃可自动切换。

---

## 0. 一句话定位

不要把产品定位成“灰色 token 中转站”，建议定位成：

> **面向 AI 编程、RPA、Agent 开发者的多模型 API 网关。**

首页文案可以这样写：

```text
一个 API Key，统一调用 GPT、Claude、Gemini、DeepSeek、Qwen、豆包、Kimi 等模型。
支持 Claude Code、Cursor、Cline、OpenAI SDK。
提供经济线、稳定线、自动路由线，适合 AI 编程、RPA Agent 和企业自动化场景。
```

---

## 1. 你现在的核心需求

| 编号 | 需求 | 设计策略 |
|---|---|---|
| 1 | 上游模型价格低 | 接入低价聚合商 + 国产低价模型 |
| 2 | 最新模型必须有，御三家必须有 | OpenAI / Claude / Gemini 通过聚合商快速补货 |
| 3 | 价格低的和稳定的都要有 | 每个模型做 economy / stable / auto 三条线 |
| 4 | 国产模型也要接入 | DeepSeek、Qwen、豆包、Kimi、智谱作为利润主力 |
| 5 | 自己必须有利润 | 成本表 + 毛利阈值 + 自动路由 + 国产模型分流 |
| 6 | 上游崩溃能切换 | 多上游池 + 熔断 + 重试 + 降权 |

---

## 2. 参考产品拆解

### 2.1 token.chhai.cn

推测产品形态：

```text
用户充值
  ↓
生成平台 API Key
  ↓
配置 Base URL
  ↓
调用 Claude / GPT / Gemini / 国产模型
  ↓
平台按 token 扣费
```

适合作为参考：

```text
Claude Code 用户入口
AI 编程工具配置教程
API Key 分发
余额充值
多模型转发
```

### 2.2 jiekou.ai

适合作为参考：

```text
中文开发者市场
Claude Code 资源包
模型价格表
多模型 API 中转
经济线 / 官方线 / 三方资源线
```

对你最重要的是：

```text
Claude 类低价线
新模型上线速度
中文开发者转化路径
```

### 2.3 APIMart.ai

适合作为参考：

```text
AI Model Marketplace
一个 API Key 调 100+ / 500+ 模型
OpenAI-compatible API Gateway
文本 + 图片 + 视频模型
模型详情页
API 文档
竞品替代页 SEO
```

你最该模仿它的是：

```text
模型市场
统一 API
文档教程
模型详情页
多模态模型
开发者 SEO
```

---

## 3. 上游池设计

不要只接一家。要分 4 层。

### 3.1 低价聚合商池

用于 Claude / GPT / Gemini 的低价补货和引流。

```text
1. jiekou.ai
2. token.chhai.cn
3. APIMart
4. OpenRouter
5. 其他可测试聚合商
```

作用：

```text
Claude Code / Cursor / Cline 用户引流
GPT / Claude / Gemini 快速补货
新模型快速上线
```

风险：

```text
价格可能变
稳定性不完全可控
上游来源不透明
可能限制二次分发
```

处理方式：

```text
只作为上游池之一
每个热门模型至少 2-3 个上游
必须做失败切换
必须做成本表和毛利保护
```

---

### 3.2 国产低价主力池

这是你的利润核心。

```text
1. DeepSeek
2. 阿里百炼 / Qwen
3. 火山方舟 / 豆包
4. Kimi / Moonshot
5. 智谱 GLM
6. MiniMax
7. 百度文心
8. 腾讯混元
```

适合承担：

```text
普通问答
JSON 结构化
RPA 文本清洗
网页摘要
数据抽取
表格字段解释
简单代码
中文内容生成
Agent 中间步骤
```

核心策略：

```text
Claude / GPT / Gemini 负责吸引用户
国产模型负责承接大量低价值请求和利润
```

---

### 3.3 稳定兜底池

用于经济线崩溃时兜底。

```text
1. OpenRouter
2. APIMart 稳定线
3. 后续官方 API / 云厂商
4. 大客户自带 Key
```

作用：

```text
低价池挂了以后自动切换
稳定线可以卖高价
防止全站不可用
```

---

### 3.4 多模态高客单池

用于提高收入，不只卖文本 token。

```text
图片生成：Flux、通义万相、豆包图像、GPT Image 类模型
视频生成：可灵、即梦、Sora、Veo、海螺
OCR：阿里 OCR、百度 OCR、PaddleOCR API 化
Embedding：Qwen Embedding、BGE、OpenAI Embedding
Rerank：BGE Reranker、Qwen Rerank
语音：ASR / TTS
```

APIMart 可以作为多模态补货上游。

---

## 4. 上游厂商比较

### 4.1 最便宜候选

| 排名 | 上游 | 适合模型 | 判断 |
|---|---|---|---|
| 1 | jiekou.ai 三方资源线 | Claude / Claude Code | 低价候选，适合 economy，但要实测稳定性 |
| 2 | APIMart | Claude / GPT / Gemini / 图片视频 | 综合便宜，模型丰富，适合补货 |
| 3 | token.chhai.cn | Claude Code / AI 编程 | 价格表需登录实测，可作为待测上游 |
| 4 | 阿里百炼 Qwen | 国产文本 | 极低价，适合利润主力 |
| 5 | DeepSeek | 推理 / 代码 / 中文 | 低价高性价比，适合默认模型 |
| 6 | 豆包 / 火山方舟 | 中文 / 多模态 | 国产低价主力 |
| 7 | Kimi / Moonshot | 长文本中文 | 长文补充 |
| 8 | OpenRouter | GPT / Claude / Gemini / 新模型 | 不一定最便宜，但模型全、稳定、兜底能力强 |

### 4.2 新模型接入最快候选

| 排名 | 上游 | 优势 |
|---|---|---|
| 1 | OpenRouter | 全球聚合，新模型上线快，适合做新模型探针 |
| 2 | jiekou.ai | 中文开发者方向更新快，Claude Code 相关快 |
| 3 | APIMart | 文本 + 图片 + 视频覆盖快 |
| 4 | 阿里百炼 / 火山 / DeepSeek / Kimi | 国产新模型稳定，适合国内用户 |
| 5 | token.chhai.cn | 需要登录后台实测模型更新速度 |

---

## 5. 模型命名体系

你要分两套模型名。

### 5.1 原始模型名

给专业用户用，尽量保持上游模型名。

```text
claude-sonnet-4-6
claude-opus-4-7
gpt-xxx
gemini-xxx
deepseek-chat
deepseek-reasoner
qwen-xxx
doubao-xxx
kimi-xxx
glm-xxx
```

注意：

```text
没有官方模型叫 Claude Code 4.7。
Claude Code 是工具，模型是 claude-opus-4-7 / claude-sonnet-4-6 等。
```

### 5.2 产品化模型名

给普通用户用，允许你做自动路由。

```text
yu-chat-pro       高质量对话，路由 GPT / Claude / Gemini
yu-chat-fast      快速低价，路由 DeepSeek / Qwen / Doubao
yu-code-pro       高质量代码，路由 Claude / GPT / Qwen Coder
yu-code-cheap     低价代码，路由 DeepSeek / Qwen Coder
yu-agent-pro      Agent 场景，路由 Claude / Gemini / GPT
yu-agent-cn       国产 Agent，路由 Qwen / DeepSeek / Doubao
yu-json           结构化输出，路由便宜模型
yu-vision         图片理解 / OCR
yu-video          视频生成
```

原则：

```text
原始模型名：用户指定什么，尽量走什么
平台模型名：允许自动路由，但要在说明里写清楚
```

不要偷偷把 `claude-sonnet` 换成其他模型。
第一版不做自动路由别名，只开放明确模型名。

---

## 6. 三线路价格体系

每个热门模型都要有三条线。

### 6.1 Economy 经济线

```text
价格最低
优先走低价聚合商
高峰期可能波动
适合个人用户
毛利目标：15% - 30%
```

示例：

```text
claude-sonnet-economy
gpt-economy
gemini-economy
```

### 6.2 Stable 稳定线

```text
稳定优先
优先走高稳定上游
失败自动切换
适合开发团队
毛利目标：25% - 40%
```

示例：

```text
claude-sonnet-stable
gpt-stable
gemini-stable
```

### 6.3 Auto 自动线

```text
平台自动选择当前性价比最高线路
综合价格、成功率、延迟、余额
这是最适合你赚钱的线路
毛利目标：30% - 60%
```

示例：

```text
claude-sonnet-4-6
claude-haiku-4-5
gemini-3.5-flash
```

---

## 7. 利润保护规则

### 7.1 成本价必须入库

每个上游模型都要维护成本表。

```sql
CREATE TABLE provider_model_cost (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    provider_name VARCHAR(100) NOT NULL,
    provider_model VARCHAR(200) NOT NULL,
    internal_model VARCHAR(200) NOT NULL,
    input_cost DECIMAL(18, 8) NOT NULL,
    output_cost DECIMAL(18, 8) NOT NULL,
    cached_input_cost DECIMAL(18, 8) DEFAULT 0,
    currency VARCHAR(20) DEFAULT 'CNY',
    supports_stream BOOLEAN DEFAULT TRUE,
    supports_tools BOOLEAN DEFAULT FALSE,
    supports_vision BOOLEAN DEFAULT FALSE,
    stability_score DECIMAL(5,2) DEFAULT 80,
    avg_latency_ms INT DEFAULT 0,
    error_rate DECIMAL(5,2) DEFAULT 0,
    balance DECIMAL(18,4) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7.2 售价公式

```text
用户售价 = 当前可用最低成本 ÷ (1 - 目标毛利率) + 风险缓冲
```

例子：

```text
上游最低成本：10 元
目标毛利：30%
售价 = 10 / 0.7 = 14.3 元
```

### 7.3 最低毛利阈值

```text
Claude / GPT：最低毛利 15%
Gemini：最低毛利 20%
国产模型：最低毛利 40%
图片 / 视频：最低毛利 30%
Embedding / Rerank：最低毛利 50%
```

如果某次请求预计毛利低于阈值：

```text
1. 换上游
2. 换到同类模型
3. 拒绝请求
4. 临时下架该模型
5. 提示价格调整
```

绝对不要出现：

```text
上游成本 10 元
你卖 8 元
用户越用你越亏
```

---

## 8. 路由策略

### 8.1 请求流程

```text
用户请求 /v1/chat/completions
    ↓
校验 API Key
    ↓
检查余额
    ↓
识别模型
    ↓
找到所有可用上游
    ↓
过滤掉不可用上游
    ↓
按线路类型计算评分
    ↓
选择最优上游
    ↓
请求失败则切换下一家
    ↓
统计 token
    ↓
扣费
    ↓
写日志
    ↓
返回结果
```

### 8.2 上游过滤规则

过滤掉：

```text
余额不足
状态 disabled
错误率过高
连续失败过多
429 冷却中
401 / 403 已下线
延迟超过阈值
毛利低于阈值
```

### 8.3 评分公式

```text
score = 价格分 * 成本权重
      + 成功率 * 稳定权重
      + 延迟分 * 速度权重
      + 余额健康度 * 库存权重
```

### 8.4 不同线路权重

#### Economy

```text
价格权重：70%
稳定权重：20%
速度权重：10%
```

#### Stable

```text
稳定权重：60%
价格权重：25%
速度权重：15%
```

#### Auto

```text
价格权重：45%
稳定权重：40%
速度权重：15%
```

---

## 9. 熔断与重试

### 9.1 熔断规则

```text
连续失败 3 次：暂停该上游 1 分钟
连续失败 10 次：暂停该上游 10 分钟
错误率超过 10%：降权
余额低于 100 元：降权
余额低于 20 元：暂停
延迟超过 10 秒：降权
返回 429：冷却 60 秒
返回 401 / 403：立即下线并告警
```

### 9.2 重试规则

```text
普通请求：最多重试 2 个上游
流式请求：建立连接前可重试，已开始输出后不重试
图片 / 视频：避免重复扣费，失败状态要人工确认
```

---

## 10. MVP 技术架构

今晚要上线，不建议从 0 写完整平台。

### 10.1 最快方案

```text
New API / VoAPI
    ↓
配置多个上游渠道
    ↓
配置模型价格
    ↓
开启用户注册 / Key / 余额
    ↓
先手动设置路由和价格
    ↓
后续再加自研 Router
```

### 10.2 推荐架构

```text
Nginx + HTTPS
    ↓
New API / VoAPI：用户、充值、Key、模型、渠道、扣费
    ↓
Router 服务：利润保护、自动路由、熔断、重试
    ↓
MySQL / PostgreSQL
    ↓
Redis：限流、缓存、上游状态
    ↓
上游池
```

### 10.3 服务器建议

```text
第一版：香港 / 新加坡云服务器
配置：2C4G 起步
系统：Ubuntu 22.04
部署：Docker Compose
域名：
  api.xxx.com       API 网关
  app.xxx.com       用户后台
  docs.xxx.com      文档
```

---

## 11. 今晚上线版本范围

今晚不要做太多。只做能收钱、能调用、能切换的 MVP。

### 11.1 必须完成

```text
1. 服务器部署
2. 域名解析
3. HTTPS
4. New API / VoAPI 部署
5. 管理员账号
6. 至少接入 3 个上游
7. 至少上架 10 个模型
8. 支持用户 API Key
9. 支持余额扣费
10. 支持 OpenAI-compatible 调用
11. 写一页 Claude Code / Cursor 配置文档
12. 小范围找 3-5 个用户测试
```

### 11.2 第一晚上游建议

```text
1. APIMart：Claude / GPT / Gemini / 图片视频补货
2. jiekou.ai：Claude Code / Claude 低价线
3. DeepSeek：国产低价主力
4. 阿里百炼 Qwen：国产稳定线
5. 火山方舟豆包：中文低价线
```

如果时间不够，先接：

```text
APIMart
jiekou.ai
DeepSeek
```

### 11.3 第一晚上架模型

```text
claude-opus-4-7
claude-sonnet-4-6
claude-haiku-4-5
gpt-5.5
gpt-5.4
gpt-5.4-mini
gemini-3.5-flash
```

---

## 12. 客户端接入文档

### 12.1 OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    api_key="你的平台 API Key",
    base_url="https://api.yourdomain.com/v1"
)

resp = client.chat.completions.create(
    model="claude-haiku-4-5",
    messages=[
        {"role": "user", "content": "你好，帮我写一个 Python 爬虫"}
    ]
)

print(resp.choices[0].message.content)
```

### 12.2 curl

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

### 12.3 Cursor / Cline

```text
API Provider：OpenAI Compatible
Base URL：https://api.yourdomain.com/v1
API Key：你的平台 Key
Model：claude-sonnet-4-6 或 claude-haiku-4-5
```

### 12.4 Claude Code

Claude Code 有两种常见接入方式：

#### Anthropic-compatible 方式

```bash
export ANTHROPIC_BASE_URL=https://api.yourdomain.com
export ANTHROPIC_AUTH_TOKEN=你的平台Key
export ANTHROPIC_MODEL=claude-sonnet-economy
```

#### OpenAI-compatible 方式

具体取决于客户端是否支持 OpenAI-compatible。文档里要单独说明。

---

## 13. 价格页设计

首页不要把所有上游原价暴露出来。做自己的产品价格。

### 13.1 示例

```text
经济线：
- 价格低
- 适合个人开发者
- 高峰期可能波动
- 自动切换同类低价上游

稳定线：
- 稳定优先
- 失败自动切换
- 适合生产环境
- 价格高于经济线

自动线：
- 平台自动选择最优模型
- 适合不会选模型的用户
- 兼顾成本和质量
```

### 13.2 毛利建议

```text
Claude / GPT 热门模型：15% - 25%
稳定线：25% - 40%
Auto 模型：30% - 60%
国产模型：40% - 100%
图片 / 视频：20% - 50%
Embedding / Rerank：50%+
```

---

## 14. 管理后台必须看哪些指标

### 14.1 上游监控

```text
上游余额
上游成功率
上游错误率
上游平均延迟
429 次数
401 / 403 次数
每日成本
每模型成本
```

### 14.2 用户监控

```text
用户余额
今日消耗
请求次数
失败次数
模型偏好
高并发用户
异常消耗用户
```

### 14.3 利润监控

```text
每个模型收入
每个模型成本
每个模型毛利
每个上游毛利
今日总流水
今日总成本
今日毛利
```

---

## 15. 数据库核心表设计

### 15.1 用户表

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100),
    email VARCHAR(200),
    password_hash VARCHAR(255),
    balance DECIMAL(18, 6) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 15.2 API Key 表

```sql
CREATE TABLE api_keys (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    api_key VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    rpm_limit INT DEFAULT 60,
    tpm_limit INT DEFAULT 100000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 15.3 上游渠道表

```sql
CREATE TABLE providers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    api_key TEXT NOT NULL,
    type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    priority INT DEFAULT 100,
    balance DECIMAL(18, 4) DEFAULT 0,
    error_count INT DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 15.4 请求日志表

```sql
CREATE TABLE request_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    api_key_id BIGINT,
    request_model VARCHAR(200),
    actual_provider VARCHAR(100),
    actual_model VARCHAR(200),
    input_tokens INT DEFAULT 0,
    output_tokens INT DEFAULT 0,
    cost DECIMAL(18, 8) DEFAULT 0,
    charge DECIMAL(18, 8) DEFAULT 0,
    margin DECIMAL(18, 8) DEFAULT 0,
    status VARCHAR(20),
    error_message TEXT,
    latency_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 16. Router 伪代码

```python
def route_request(user, request):
    model = request["model"]
    line_type = parse_line_type(model)  # economy / stable / auto

    candidates = find_provider_candidates(model)

    candidates = [
        c for c in candidates
        if c.status == "active"
        and c.balance > c.min_balance
        and c.error_rate < c.max_error_rate
        and c.is_cooldown is False
    ]

    candidates = filter_by_margin(candidates, model, target_margin=line_type.margin)

    if not candidates:
        raise Exception("No available provider with positive margin")

    ranked = rank_candidates(candidates, line_type)

    last_error = None

    for provider in ranked[:3]:
        try:
            resp = call_provider(provider, request)
            usage = parse_usage(resp)
            charge = calculate_charge(user, model, usage)
            cost = calculate_cost(provider, model, usage)

            if charge <= cost:
                mark_provider_warning(provider, "margin_too_low")
                continue

            deduct_balance(user, charge)
            save_log(user, request, provider, usage, cost, charge)
            return resp

        except ProviderError as e:
            last_error = e
            mark_provider_error(provider, e)
            continue

    raise Exception(f"All providers failed: {last_error}")
```

---

## 17. 风控和合规底线

不要做：

```text
盗刷信用卡
骗补贴
共享订阅账号池
售卖来路不明 Key
偷换模型但不告知用户
售卖用户 prompt / 代码 / 数据
承诺无限 Claude
承诺官方同源但实际不是
```

必须做：

```text
明确区分 economy / stable / auto
用户日志脱敏
不要默认保存完整 prompt
敏感信息提示
异常用户限流
上游来源分级
模型可用性说明
```

---

## 18. 今晚执行清单

### 18.1 服务器和域名

```text
[ ] 买香港 / 新加坡服务器
[ ] 解析 api.xxx.com
[ ] 解析 app.xxx.com
[ ] 安装 Docker
[ ] 安装 Docker Compose
[ ] 配置 Nginx
[ ] 配置 HTTPS
```

### 18.2 系统部署

```text
[ ] 部署 New API / VoAPI
[ ] 初始化管理员账号
[ ] 配置数据库
[ ] 配置 Redis
[ ] 登录后台
```

### 18.3 上游配置

```text
[ ] 配置 APIMart 上游
[ ] 配置 jiekou.ai 上游
[ ] 配置 DeepSeek 上游
[ ] 配置阿里百炼 Qwen 上游
[ ] 配置火山豆包上游
[ ] 给每个上游充值小额测试
```

### 18.4 模型配置

```text
[ ] claude-opus-4-7
[ ] claude-sonnet-4-6
[ ] claude-haiku-4-5
[ ] gpt-5.5
[ ] gpt-5.4
[ ] gpt-5.4-mini
[ ] gemini-3.5-flash
```

### 18.5 测试

```text
[ ] curl 测试
[ ] Python OpenAI SDK 测试
[ ] Cursor 测试
[ ] Claude Code 测试
[ ] 余额扣费测试
[ ] 上游失败切换测试
[ ] 日志查看
```

### 18.6 文档

```text
[ ] 首页一句话介绍
[ ] 模型价格页
[ ] OpenAI SDK 接入文档
[ ] Claude Code 配置文档
[ ] Cursor 配置文档
[ ] 常见问题
```

### 18.7 小范围上线

```text
[ ] 找 3-5 个朋友测试
[ ] 每人发 5-10 元额度
[ ] 观察错误率
[ ] 观察上游成本
[ ] 观察真实毛利
[ ] 第二天再开放充值
```

---

## 19. 第一版产品页面结构

```text
首页
├── 一个 API 调用全部模型
├── 支持 Claude Code / Cursor / Cline
├── 经济线 / 稳定线 / 自动线
├── 支持国产模型
├── 立即开始

模型页
├── Claude
├── GPT
├── Gemini
├── DeepSeek
├── Qwen
├── 豆包
├── Kimi
├── GLM
├── 图片
├── 视频

价格页
├── 经济线
├── 稳定线
├── 国产高性价比线
├── 图片 / 视频线

文档页
├── Quick Start
├── OpenAI SDK
├── curl
├── Claude Code
├── Cursor
├── Cline
├── 常见错误

用户后台
├── 余额
├── 充值
├── API Key
├── 调用日志
├── 用量统计
```

---

## 20. 最重要的战略判断

### 20.1 不要把命押在 Claude 低价上游

Claude / GPT / Gemini 是引流品，不是利润主力。

```text
用户因为 Claude 来
真正利润靠国产模型、auto 路由、缓存、批处理、多模态
```

### 20.2 不要只做普通中转站

普通中转站太卷。你要做垂直定位：

```text
AI 编程 + RPA + Agent 开发者模型网关
```

你的差异化：

```text
懂 RPA
懂 Agent
懂内网自动化
懂爬虫和数据采集
懂 Claude Code / Cursor / OpenClaw 用户需求
```

### 20.3 今晚先上线，不追求完美

今晚目标：

```text
能注册
能充值/发额度
能生成 Key
能调模型
能扣费
能切换上游
能给 Claude Code / Cursor 用
```

第二天再优化：

```text
自动路由
利润报表
SEO 文档
代理分佣
模型详情页
企业版
```

---

## 21. 明天优化方向

```text
1. 做上游价格自动采集
2. 做上游健康检查面板
3. 做模型毛利报表
4. 做 Claude Code 专题页
5. 做 Cursor 配置教程
6. 做 RPA Agent 示例
7. 做邀请码 / 代理返佣
8. 做新模型通知
9. 做国产模型推荐
10. 做 APIMart / OpenRouter / JieKou 对比页
```

---

## 22. 最终结论

你的实现路径应该是：

```text
第一步：用 New API / VoAPI 快速上线
第二步：接 jiekou、APIMart、token.chhai 作为低价聚合上游
第三步：接 DeepSeek、Qwen、豆包、Kimi、GLM 作为利润主力
第四步：做 economy / stable / auto 三线路
第五步：通过成本表、毛利阈值、熔断切换保证自己不亏
第六步：用 Claude Code / Cursor / RPA Agent 教程获客
```

核心原则：

```text
Claude / GPT / Gemini 负责吸引用户
国产模型负责利润
聚合商负责补货
OpenRouter / 稳定线负责兜底
Auto 路由负责赚钱
```

---

## 23. 当前仓库落地状态

本仓库已经从纯方案文档推进到一个可运行的本地 MVP，当前定位调整为：

```text
官网 / 文档 / 获客页：本项目
用户登录 / 充值 / Token / 渠道 / 日志 / 模型管理：生产环境推荐接 New API
自研 Router：保留为后续利润保护、自动路由、熔断和差异化能力
```

已实现页面：

```text
公开访客
├── /                  模型市场首页
├── /pricing           模型与价格
├── /docs              OpenAI-compatible 接入文档
├── /claude-code       Claude Code / Cursor / Cline 教程
├── /status            公开状态页
├── /login             登录入口占位
└── /register          注册入口占位

普通用户
├── /dashboard         用户控制台
├── /recharge          演示充值、自定义金额和充值订单
├── /keys              API Key 自助创建
└── /usage             用量记录

管理员
├── /admin             运营面板
└── /newapi            New API 上线方案
```

已实现后端能力：

```text
OpenAI-compatible /v1/chat/completions
/v1/models
SQLite 数据库
API Key 校验
用户余额扣费
充值最低金额校验
请求日志
模型售价表
上游成本表
economy / stable / auto 路由权重
毛利阈值过滤
上游失败重试
429 冷却
401 / 403 下线
Mock 上游用于本地测试
```

本地运行：

```bash
python3 app.py --init-db --seed --host 127.0.0.1 --port 8001
```

测试 Key：

```text
sk-yu-demo-local
```

---

## 24. 上线版架构建议

不要把所有后台能力从 0 重写。上线最快路径是：

```text
www.yourdomain.com   本项目：官网、价格、文档、Claude Code 教程、SEO
app.yourdomain.com   New API：用户注册、登录、充值、Token、用量、管理员后台
api.yourdomain.com   New API 或本项目 Router：OpenAI-compatible API
```

New API 适合承接：

```text
用户注册登录
管理员权限
API Token 管理
充值 / 兑换码
用量日志
渠道管理
模型管理
分组计费
系统设置
```

本项目继续负责：

```text
品牌官网
模型市场页
价格页
Claude Code / Cursor / Cline 教程
OpenAI SDK 文档
公开状态页
SEO 页面
后续自研 Router 差异化
```

仓库已提供 New API Compose 模板：

```bash
docker compose -f ops/newapi-compose.yml up -d
```

上线前环境变量：

```bash
SITE_NAME=你的品牌名
PUBLIC_API_BASE=https://api.yourdomain.com
APP_BASE_URL=https://app.yourdomain.com
LOGIN_URL=https://app.yourdomain.com/login
REGISTER_URL=https://app.yourdomain.com/register
ADMIN_CONSOLE_URL=https://app.yourdomain.com/admin
NEWAPI_BASE_URL=https://app.yourdomain.com
ADMIN_TOKEN=替换成长随机字符串
ALLOW_DEFAULT_ADMIN_ON_LOCALHOST=false
CORS_ALLOW_ORIGIN=https://www.yourdomain.com
DEMO_PORTAL_ENABLED=false
BILLING_CURRENCY=CNY
BILLING_SYMBOL=¥
MIN_RECHARGE_AMOUNT=10
```

上线优先级：

```text
1. 部署 New API
2. 配置域名和 HTTPS
3. 配置上游渠道和模型价格
4. 配置本站官网环境变量
5. 登录/注册按钮跳转到 New API
6. 小范围测试充值、Key、Cursor、Claude Code
7. 再开放真实充值
```

安全注意：

```text
生产环境必须关闭本项目内置 demo 用户后台：
DEMO_PORTAL_ENABLED=false

生产环境必须替换默认 ADMIN_TOKEN。
设置真实 ADMIN_TOKEN 后，本项目 /admin 和 /newapi 需要通过 ?token=... 或 X-Admin-Token 访问。
默认开发 token 只允许 localhost 预览，生产建议显式设置 ALLOW_DEFAULT_ADMIN_ON_LOCALHOST=false。

生产环境不要使用 sk-yu-demo-local。
公开文档使用 YOUR_API_KEY 占位，真实 Key 只从 New API 后台生成。
```

计费口径：

```text
第一版默认按 CNY 展示用户余额、充值订单和用量扣费，最低充值 ¥10。
充值页支持固定套餐和自定义金额，本地只做演示；生产环境由 NewAPI 接管真实支付、兑换码和人工充值。
如果上游账单使用 USD，需要在 NewAPI 或账务层记录汇率和折算来源，避免把汇率写死在页面价格里。
```

---

## 25. 竞品参考后的页面取舍

从三个参考站提炼出的落地策略：

```text
token.chhai.cn
- 首页先展示模型和价格
- 顶部只保留文档、登录、注册等轻导航
- 模型卡片价格直出，降低用户理解成本

jiekou.ai
- 强化 Claude Code / Cursor 用户路径
- 把 AI 编程工具配置做成单独转化页
- 注册登录后再进入用户后台

apimart.ai
- 做模型市场和统一 API 的心智
- 强化 OpenAI-compatible API 和开发者文档
- 后续可扩展图片、视频、语音、多模态模型
```

因此当前站点不再把 `运营后台` 暴露在公开导航里，而是分成三套入口：

```text
公开站：模型 / 价格 / 文档 / Claude Code / 状态 / 登录 / 注册
用户端：控制台 / 充值 / API Keys / 用量 / 文档
管理员端：运营面板 / New API 方案 / 状态页 / 官网
```

---

## 26. 2026-05 混合上游生产方案

上线版不走单一上游，而是使用 NewAPI 管理混合渠道：

| 优先级 | 平台 | 类型 | 优势 | 主要覆盖模型 | 建议用途 |
|---|---|---|---|---|---|
| 1 | RightCode | 极致低价 | Claude / GPT / Gemini 成本低 | Claude、GPT Codex、Gemini | 低价补充，赚差价 |
| 2 | PoloAPI / weelinking | 稳定中价 | 稳定、延迟低、企业服务好 | 御三家 + 部分国产 | 主力稳定渠道 |
| 3 | SiliconFlow | 国产最优 | 国产模型便宜、快、稳定 | DeepSeek、Qwen、豆包、GLM、Embedding | 国产主力 |
| 4 | jiekou.ai / APIMart / token.chhai.cn | 全能补充 | 模型全、兼容性强 | 御三家 + 图像 / 视频 | 备用 + 补货 |

NewAPI 配置原则：

```text
每个热门模型至少 2-3 个渠道
稳定渠道权重高
国产渠道权重高
低价渠道权重低
开启失败自动切换
先小额充值测试，再开放真实充值
```

热门模型冗余建议：

```text
Claude Sonnet 最新：PoloAPI / weelinking + RightCode + jiekou.ai
GPT-5.x / Codex：PoloAPI / weelinking + RightCode Codex + APIMart
Gemini Pro / Flash：PoloAPI / weelinking + RightCode Gemini + APIMart
DeepSeek / Qwen / 豆包：SiliconFlow 主，官方直连或 PoloAPI 备用
图像 / 视频：APIMart / SiliconFlow / jiekou.ai 第二阶段开放
```

对外定价：

```text
御三家：初期加价 25%-60%，先保守积累用户
国产模型：成本低，可承担更高毛利
注册不送：必须充值后才加赠，降低爬虫薅羊毛
充值套餐：自定义金额 + 月卡 + 季卡 + 团队包
```

落地步骤：

```text
1. 每家上游先充值 100-300 元
2. 部署 NewAPI
3. 添加 SiliconFlow / RightCode / PoloAPI 或 weelinking / jiekou.ai / APIMart
4. 精简模型列表，只开放测试通过的模型
5. 配置渠道权重、分组倍率、failover 和重试次数
6. 接入微信/支付宝、兑换码、人工充值兜底
7. 用 Cherry Studio、Claude Code、Cursor、curl 压测
8. 小范围 3-5 个用户试用
9. 再开放真实充值和公开推广
```

风险提醒：

```text
RightCode 这类极低价渠道可能有模型替换、波动、兼容性差异。
生产环境不能全靠低价渠道。
稳定渠道负责口碑，国产渠道负责利润，低价渠道负责补充和差价。
```

当前仓库已按该方案更新：

```text
首页：混合上游、模型分类、Claude Code 转化入口
NewAPI 方案页：上游优先级、热门模型冗余、配置顺序
数据库种子：RightCode Codex、PoloAPI、weelinking、SiliconFlow、APIMart、jiekou.ai
充值页：自定义金额、固定充值、月卡、季卡、团队包
文档：README、docs/newapi-launch.md、docs/upstream-mix-2026-05.md
```
