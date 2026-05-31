# 2026-05 混合上游上线方案

目标是用 NewAPI 快速上线一个一站式、多模型、价格有竞争力的 API 中转站，同时避免单一低价渠道不稳导致口碑崩掉。

## 上游组合

| 优先级 | 平台 | 类型 | 主要覆盖模型 | 建议用途 |
|---|---|---|---|---|
| 1 | PoloAPI / weelinking | 稳定中价 | Claude、GPT、Gemini | 主力稳定渠道，高权重 |
| 2 | RightCode | 极致低价 | Claude、GPT、Gemini | 低价补充，赚差价，低权重 |
| 3 | jiekou.ai / APIMart / token.chhai.cn | 全能补充 | 御三家备用 | 补货、备用 |
| 4 | SiliconFlow | 国产最优 | DeepSeek、Qwen、豆包、GLM、Embedding | 第二阶段开放国产模型 |

## NewAPI 配置原则

首发只开放 7 个模型，每个模型至少接 2 个上游：

- `claude-opus-4-7`：PoloAPI / weelinking 主，RightCode 低价补充，jiekou.ai 备用。
- `claude-sonnet-4-6`：PoloAPI / weelinking 主，RightCode 低价补充，jiekou.ai 备用。
- `claude-haiku-4-5`：PoloAPI / weelinking 主，RightCode 低价补充，jiekou.ai 备用。
- `gpt-5.5` / `gpt-5.4` / `gpt-5.4-mini`：PoloAPI / weelinking 主，RightCode 补充，APIMart 备用。
- `gemini-3.5-flash`：PoloAPI / weelinking 主，RightCode Gemini 补充，APIMart 备用。
- 图像 / 视频：第二阶段再开放，先用 APIMart、SiliconFlow、jiekou.ai 做小范围测试。

权重建议：

```text
稳定渠道：高权重，承接默认流量
国产渠道：第二阶段开放前不进首发模型池
低价渠道：低权重，参与经济线和 failover
备用渠道：中低权重，只在主链路失败时切换
```

## 对外定价

- `claude-opus-4-7` 按上游成本 × 1.6。
- `claude-sonnet-4-6` 按上游成本 × 1.35。
- `claude-haiku-4-5` 按上游成本 × 1.3。
- `gpt-5.5` 按上游成本 × 1.5。
- `gpt-5.4` 按上游成本 × 1.35。
- `gpt-5.4-mini` 和 `gemini-3.5-flash` 按上游成本 × 1.3。
- 注册不送额度，充值和月卡支付成功后按固定金额加赠。

## 测试步骤

1. 每家上游先充值 100-300 元。
2. 在 NewAPI 添加渠道，填 Base URL、API Key、模型映射。
3. 只开放测试通过的模型。
4. 用 Cherry Studio、Claude Code、Cursor、curl 测试。
5. 重点测流式输出、长上下文、工具调用、Prompt Caching、模型替换和高峰期延迟。
6. 记录成功率、平均延迟、扣费偏差、失败错误码。
7. 小范围给 3-5 个用户试用，再开放真实充值。

## 风险提醒

RightCode 这类极低价渠道波动风险较高，可能遇到模型替换、偶发不稳或特性兼容差异。生产策略必须是稳定渠道高权重、低价渠道低权重，首发模型先控制在 7 个以内。

## 当前仓库对应改动

- 首页展示混合上游策略和模型分类。
- NewAPI 方案页展示上游优先级、模型冗余和配置顺序。
- 本地种子上游包含 RightCode Codex、PoloAPI、weelinking、SiliconFlow、APIMart、jiekou.ai。
- 充值页增加充值后加赠和月卡演示。
- README 和 MVP 文档已更新上线步骤。
