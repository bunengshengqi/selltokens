from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LaunchModelSpec:
    model: str
    display_name: str
    provider: str
    line_type: str
    base_input_price: float
    base_output_price: float
    multiplier: float
    description: str

    @property
    def input_price(self) -> float:
        return self.base_input_price * self.multiplier

    @property
    def output_price(self) -> float:
        return self.base_output_price * self.multiplier

    @property
    def min_margin(self) -> float:
        return (self.multiplier - 1) / self.multiplier


FIRST_WAVE_MODEL_SPECS: tuple[LaunchModelSpec, ...] = (
    LaunchModelSpec(
        "claude-opus-4-7",
        "Claude Opus 4.7",
        "Anthropic",
        "premium",
        5.0,
        25.0,
        1.6,
        "最高质量 Claude 线路，适合复杂 Agent、长上下文和高价值代码任务。",
    ),
    LaunchModelSpec(
        "claude-sonnet-4-6",
        "Claude Sonnet 4.6",
        "Anthropic",
        "stable",
        3.0,
        15.0,
        1.35,
        "Claude Code / Cursor 主力模型，兼顾质量、速度和日常使用体验。",
    ),
    LaunchModelSpec(
        "claude-haiku-4-5",
        "Claude Haiku 4.5",
        "Anthropic",
        "economy",
        1.0,
        5.0,
        1.3,
        "轻量 Claude 线路，适合快速问答、摘要、标题和辅助调用。",
    ),
    LaunchModelSpec(
        "gpt-5.5",
        "GPT-5.5",
        "OpenAI",
        "premium",
        5.0,
        30.0,
        1.5,
        "OpenAI 旗舰线路，适合复杂推理、代码审查和高质量生成。",
    ),
    LaunchModelSpec(
        "gpt-5.4",
        "GPT-5.4",
        "OpenAI",
        "stable",
        2.5,
        15.0,
        1.35,
        "OpenAI 稳定主力模型，适合日常开发、Agent 和通用任务。",
    ),
    LaunchModelSpec(
        "gpt-5.4-mini",
        "GPT-5.4 Mini",
        "OpenAI",
        "economy",
        0.75,
        4.5,
        1.3,
        "轻量 GPT 线路，适合批量轻任务和新用户入门。",
    ),
    LaunchModelSpec(
        "gemini-3.5-flash",
        "Gemini 3.5 Flash",
        "Google",
        "economy",
        0.5,
        3.0,
        1.3,
        "高速 Gemini 线路，适合低延迟、大量轻量请求和多轮对话。",
    ),
)

FIRST_WAVE_MODEL_NAMES = tuple(spec.model for spec in FIRST_WAVE_MODEL_SPECS)


def model_price_rows() -> tuple[tuple[str, str, str, float, float, float, str], ...]:
    return tuple(
        (
            spec.model,
            spec.display_name,
            spec.line_type,
            round(spec.input_price, 6),
            round(spec.output_price, 6),
            round(spec.min_margin, 6),
            spec.description,
        )
        for spec in FIRST_WAVE_MODEL_SPECS
    )


def newapi_model_ratio() -> dict[str, float]:
    # NewAPI 当前按 Price=1、QuotaPerUnit=500000 展示时，ModelRatio 约等于输入单价的一半。
    return {spec.model: round(spec.input_price / 2, 6) for spec in FIRST_WAVE_MODEL_SPECS}


def newapi_completion_ratio() -> dict[str, float]:
    return {spec.model: round(spec.output_price / spec.input_price, 6) for spec in FIRST_WAVE_MODEL_SPECS}


def recharge_bonus_amount(paid_amount: float) -> float:
    if paid_amount >= 100:
        return 10.0
    if paid_amount > 0:
        return 5.0
    return 0.0
