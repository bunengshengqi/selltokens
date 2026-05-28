from __future__ import annotations

from html import escape
from typing import Any, Iterable

from .config import Settings, settings as default_settings


def home_page(settings: Settings, models: Iterable[dict[str, Any]]) -> str:
    model_list = list(models)
    cards = "".join(_model_card(model, settings, featured=index < 6) for index, model in enumerate(model_list[:9]))
    mix_cards = _provider_mix_cards()
    category_cards = _model_category_cards()
    funnel_cards = _growth_funnel_cards(settings)
    return layout(
        "首页",
        "home",
        f"""
        <section class="landing-hero">
          <div>
            <p class="eyebrow">AI Coding / RPA / Agent API Gateway</p>
            <h1>一个 API Key，统一调用 Claude、GPT、Gemini、DeepSeek、Qwen、豆包。</h1>
            <p>按生产方案接 NewAPI + 混合上游：RightCode 做低价补充，PoloAPI / weelinking 做稳定线，SiliconFlow 做国产主力，jiekou.ai 和 APIMart 做模型补货。</p>
            <div class="hero-actions">
              <a class="button primary" href="{escape(settings.register_url)}">立即注册</a>
              <a class="button" href="{escape(settings.login_url)}">登录控制台</a>
              <a class="text-link inline" href="/claude-code">Claude Code 接入 →</a>
            </div>
          </div>
          <div class="hero-panel">
            <div class="panel-row">
              <span>Base URL</span>
              <strong>{escape(settings.public_api_base)}/v1</strong>
            </div>
            <div class="panel-row">
              <span>推荐模型</span>
              <strong>yu-code-auto</strong>
            </div>
            <div class="route-stack">
              <b>低价</b><b>稳定</b><b>国产</b>
            </div>
            <pre>curl {escape(settings.public_api_base)}/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -d '{{"model":"yu-chat-auto","messages":[{{"role":"user","content":"你好"}}]}}'</pre>
          </div>
        </section>
        <section class="conversion-strip">
          <div>
            <p class="eyebrow">Growth Funnel</p>
            <h1>先试用，再充值，再邀请</h1>
            <p>新用户注册即送体验额度，优先体验 DeepSeek、Qwen、豆包等低成本模型；充值保持微信支付不变，套餐和邀请奖励负责提升转化和复购。</p>
          </div>
          <div class="conversion-grid">{funnel_cards}</div>
        </section>
        <section class="center-head compact">
          <p class="eyebrow">Models</p>
          <h1>支持的模型</h1>
          <p>首页保留 token.chhai 的价格直出，加入 APIMart 的模型市场分类，再强化 jiekou.ai 式 Claude Code / Cursor 接入路径。</p>
          <a class="text-link" href="/pricing">查看全部 {len(model_list)} 个模型详情与定价 →</a>
        </section>
        <section class="model-grid">{cards}</section>
        <section class="center-head compact">
          <p class="eyebrow">Upstream Mix</p>
          <h1>2026 年 5 月上线组合</h1>
          <p>不把命押在单一低价渠道上。每个热门模型至少 2-3 个上游，低价线负责利润空间，稳定线负责口碑，国产线负责规模化调用。</p>
        </section>
        <section class="feature-grid">{mix_cards}</section>
        <section class="center-head compact">
          <p class="eyebrow">Catalog</p>
          <h1>模型分类</h1>
        </section>
        <section class="feature-grid">{category_cards}</section>
        <section class="steps">
          <div><strong>1</strong><h2>注册并充值</h2><p>用户注册后进入控制台，充值余额或兑换额度。</p></div>
          <div><strong>2</strong><h2>创建 API Key</h2><p>在 New API 或本地控制台生成 Token，设置额度和模型权限。</p></div>
          <div><strong>3</strong><h2>改一行 Base URL</h2><p>OpenAI SDK / Cursor / Cline 只需要换成平台地址。</p></div>
        </section>
        <section class="feature-grid">
          <div><h2>自动路由</h2><p>根据价格、成功率、延迟和余额选择上游，失败时自动重试。</p></div>
          <div><h2>利润保护</h2><p>模型售价、上游成本和最低毛利分开管理，避免越用越亏。</p></div>
          <div><h2>New API 底座</h2><p>上线版建议用 New API 接管登录、充值、Token、渠道、日志和模型管理。</p></div>
          <div><h2>小白友好</h2><p>免费试用、小额套餐、微信客服、Cherry Studio / Claude Code 教程一起做转化。</p></div>
        </section>
        """,
        settings=settings,
        variant="public",
    )


def pricing_page(models: Iterable[dict[str, Any]], settings: Settings) -> str:
    plan_cards = _pricing_plan_cards(settings)
    rate_rows = _pricing_rate_rows(settings)
    capacity_cards = _capacity_cards()
    ladder_rows = _pricing_ladder_table(settings)
    referral_rules = _referral_rules(settings)
    rows = []
    for model in models:
        rows.append(
            "<tr>"
            f"<td><strong>{escape(model['internal_model'])}</strong><small>{escape(model['description'] or '')}</small></td>"
            f"<td>{_line_badge(model['line_type'])}</td>"
            f"<td>{_money(model['input_price'], settings, decimals=4)} / M tokens</td>"
            f"<td>{_money(model['output_price'], settings, decimals=4)} / M tokens</td>"
            f"<td>{float(model['min_margin']) * 100:.0f}%</td>"
            "</tr>"
        )
    return layout(
        "Pricing",
        "pricing",
        f"""
        <section class="pricing-stage">
          <div class="pricing-hero">
            <p class="eyebrow">Claude Code API Pricing</p>
            <h1>为高强度 AI 编程准备的模型额度方案</h1>
            <p>统一接入 Claude、Codex/GPT、Gemini 和国产模型。人民币余额计费，套餐决定通道优先级、服务支持和模型倍率，适合个人开发者、工作室和自动化 Agent 团队。</p>
            <div class="billing-toggle" aria-label="计费周期">
              <span class="active">按月付</span>
              <span>按年付 <b>省 2 个月</b></span>
            </div>
            <div class="hero-stats">
              <span><strong>100</strong> 人同时在线目标</span>
              <span><strong>3+</strong> 热门模型冗余上游</span>
              <span><strong>CNY</strong> 余额和支付</span>
            </div>
          </div>
          <section class="plan-grid">{plan_cards}</section>
        </section>
        <section class="capacity-panel">
          <div>
            <p class="eyebrow">Production Target</p>
            <h2>第一版按 100 人同时在线设计</h2>
            <p>页面展示的是套餐，真正承载在线用户的是 NewAPI、上游冗余、支付回调和监控。100 人同时在线不是靠单一上游硬扛，而是通过分组、限流、failover 和缓存把风险拆开。</p>
          </div>
          <div class="capacity-grid">{capacity_cards}</div>
        </section>
        <section class="pricing-note">
          <strong>计费说明</strong>
          <p>套餐负责额度、通道优先级和服务支持；模型实际扣费仍按 NewAPI 的模型倍率和分组价格计算。第一版支付方式保持微信支付，兑换码和人工补单作为兜底。</p>
          <a class="text-link" href="{escape(settings.register_url)}">进入控制台购买套餐 →</a>
        </section>
        <section class="funnel-panel">
          <div>
            <p class="eyebrow">Recharge Ladder</p>
            <h2>阶梯收费标准</h2>
            <p>按量充值用于小额尝试和日常补余额；月卡用于锁定复购。Claude / GPT / Gemini 最新模型走通用余额，低成本模型包只开放 DeepSeek、Qwen、豆包等低风险线路。</p>
          </div>
          <div class="ladder-table">{ladder_rows}</div>
        </section>
        <section class="referral-panel">
          <div>
            <p class="eyebrow">Referral</p>
            <h2>邀请裂变规则</h2>
            <p>先用固定额度奖励快速上线，等真实订单稳定后再接首充返佣。这样能控制薅羊毛风险，同时让 Cursor / Claude Code 社群传播更快。</p>
          </div>
          <div class="referral-rules">{referral_rules}</div>
        </section>
        <section class="rate-panel">
          <div>
            <p class="eyebrow">Model Multipliers</p>
            <h2>模型倍率</h2>
            <p>国外最新大模型更贵，国产模型成本低、利润空间更大。这里给用户看的是清晰可理解的档位，实际倍率在 NewAPI 分组里配置。</p>
          </div>
          <div class="rate-table">{rate_rows}</div>
        </section>
        <section class="feature-grid">{_model_category_cards()}</section>
        <section class="table-wrap">
          <h2>按量模型单价</h2>
          <table>
            <thead><tr><th>模型</th><th>线路</th><th>输入价格</th><th>输出价格</th><th>最低毛利</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
          </table>
        </section>
        """,
        settings=settings,
        variant="public",
    )


def dashboard_page(
    user: dict[str, Any],
    usage: dict[str, Any],
    keys: Iterable[dict[str, Any]],
    settings: Settings,
) -> str:
    key_count = len(list(keys))
    balance = _money(user["balance"], settings, decimals=4)
    today_charge = _money(usage["today_charge"], settings, decimals=4)
    return layout(
        "Console",
        "dashboard",
        f"""
        <section class="page-title">
          <div>
            <p class="eyebrow">Console</p>
            <h1>用户控制台</h1>
            <p>{escape(user['email'])} 的余额、Key、调用统计和接入入口。</p>
          </div>
          <a class="button primary" href="/recharge">充值</a>
        </section>
        <section class="metrics">
          <div><strong>{balance}</strong><span>账户余额</span></div>
          <div><strong>{usage['today_requests']}</strong><span>今日请求</span></div>
          <div><strong>{today_charge}</strong><span>今日消耗</span></div>
          <div><strong>{usage['today_input_tokens'] + usage['today_output_tokens']}</strong><span>今日 tokens</span></div>
          <div><strong>{key_count}</strong><span>API Keys</span></div>
          <div><strong>{usage['total_requests']}</strong><span>累计请求</span></div>
        </section>
        <section class="action-grid">
          <a class="action-card" href="/recharge"><strong>充值余额</strong><span>本地演示充值；上线后跳转 NewAPI 支付系统。</span></a>
          <a class="action-card" href="/keys"><strong>API Keys</strong><span>创建和查看调用 Key。</span></a>
          <a class="action-card" href="/usage"><strong>用量记录</strong><span>查看模型、上游、扣费和失败原因。</span></a>
          <a class="action-card" href="/docs"><strong>接入文档</strong><span>Cursor、Cline、Claude Code 和 SDK 示例。</span></a>
        </section>
        """,
        variant="app",
    )


def recharge_page(
    user: dict[str, Any],
    orders: Iterable[dict[str, Any]],
    settings: Settings,
    notice: str = "",
    notice_kind: str = "success",
) -> str:
    amounts = [10, 50, 100, 500]
    plans = [
        ("Pro", 39, "每天 4-5 小时中度使用，适合个人开发者"),
        ("Max", 99, "每天 8 小时高强度使用，适合 Claude Code 主力用户"),
        ("Ultra", 299, "工作室和团队使用，独享高速通道和人工支持"),
    ]
    min_amount = float(settings.min_recharge_amount)
    currency = escape(settings.billing_currency)
    amount_cards = "".join(
        f"""
        <form class="pay-card" method="post" action="/recharge">
          <input type="hidden" name="amount" value="{amount}">
          <strong>{_money(amount, settings, decimals=0)}</strong>
          <span>到账余额 {_money(amount, settings, decimals=2)}</span>
          <button type="submit">演示充值</button>
        </form>
        """
        for amount in amounts
    )
    custom_card = f"""
        <form class="pay-card custom-pay" method="post" action="/recharge">
          <strong>自定义金额</strong>
          <span>账户币种：{currency}，最低 {_money(min_amount, settings, decimals=2)}</span>
          <input
            name="amount"
            type="number"
            inputmode="decimal"
            min="{min_amount:.2f}"
            step="0.01"
            placeholder="输入充值金额"
            required
          >
          <button type="submit">自定义充值</button>
        </form>
    """
    plan_cards = "".join(
        f"""
        <form class="pay-card plan-pay" method="post" action="/recharge">
          <input type="hidden" name="amount" value="{amount}">
          <strong>{escape(name)}</strong>
          <span>{escape(desc)}</span>
          <b>{_money(amount, settings, decimals=2)}</b>
          <button type="submit">演示购买</button>
        </form>
        """
        for name, amount, desc in plans
    )
    rows = []
    for order in orders:
        rows.append(
            "<tr>"
            f"<td>{escape(order['order_no'])}</td>"
            f"<td>{_order_money(order, settings)}</td>"
            f"<td>{escape(order['channel'])}</td>"
            f"<td><span class='status active'>{escape(order['status'])}</span></td>"
            f"<td>{escape(order['created_at'] or '')}</td>"
            "</tr>"
        )
    return layout(
        "Recharge",
        "recharge",
        f"""
        <section class="page-title">
          <div>
            <p class="eyebrow">Billing</p>
            <h1>账户充值</h1>
            <p>第一版账户按 {currency} 计费，最低 {_money(min_amount, settings, decimals=2)}；本地页面只做演示，上线后由 NewAPI 支付系统处理微信支付、兑换码和人工充值。</p>
          </div>
          <div class="balance-pill">余额 {_money(user['balance'], settings, decimals=4)}</div>
        </section>
        {_notice(notice, notice_kind)}
        <section class="pay-grid">{amount_cards}{custom_card}</section>
        <section class="table-wrap">
          <h2>套餐建议</h2>
          <div class="pay-grid">{plan_cards}</div>
        </section>
        <section class="table-wrap">
          <h2>充值订单</h2>
          <table>
            <thead><tr><th>订单号</th><th>金额</th><th>渠道</th><th>状态</th><th>创建时间</th></tr></thead>
            <tbody>{''.join(rows) if rows else _empty_row(5, '暂无充值订单')}</tbody>
          </table>
        </section>
        """,
        variant="app",
    )


def keys_page(user: dict[str, Any], keys: Iterable[dict[str, Any]], new_key: str = "") -> str:
    rows = []
    for item in keys:
        rows.append(
            "<tr>"
            f"<td><strong>{escape(item['name'] or 'API Key')}</strong><small>{escape(item['key_prefix'])}</small></td>"
            f"<td><span class='status {escape(item['status'])}'>{escape(item['status'])}</span></td>"
            f"<td>{int(item['rpm_limit'])}</td>"
            f"<td>{int(item['tpm_limit'])}</td>"
            f"<td>{escape(item['created_at'] or '')}</td>"
            f"<td>{escape(item['last_used_at'] or '-')}</td>"
            "</tr>"
        )
    return layout(
        "API Keys",
        "keys",
        f"""
        <section class="page-title">
          <div>
            <p class="eyebrow">Developer</p>
            <h1>API Keys</h1>
            <p>{escape(user['email'])} 的 API Key。新 Key 只在创建后显示一次。</p>
          </div>
          <form class="inline-form" method="post" action="/keys">
            <input name="name" placeholder="Key 名称" value="Default key">
            <button class="button primary" type="submit">创建 Key</button>
          </form>
        </section>
        {_new_key_box(new_key)}
        <section class="table-wrap">
          <table>
            <thead><tr><th>名称</th><th>状态</th><th>RPM</th><th>TPM</th><th>创建时间</th><th>最后使用</th></tr></thead>
            <tbody>{''.join(rows) if rows else _empty_row(6, '暂无 API Key')}</tbody>
          </table>
        </section>
        """,
        variant="app",
    )


def usage_page(logs: Iterable[dict[str, Any]], settings: Settings) -> str:
    rows = []
    for log in logs:
        rows.append(
            "<tr>"
            f"<td>{escape(log['created_at'] or '')}</td>"
            f"<td><strong>{escape(log['request_model'] or '')}</strong><small>{escape(log['actual_model'] or '')}</small></td>"
            f"<td>{escape(log['actual_provider'] or '')}</td>"
            f"<td>{int(log['input_tokens'] or 0)} / {int(log['output_tokens'] or 0)}</td>"
            f"<td>{_money(log['charge'] or 0, settings, decimals=8)}</td>"
            f"<td><span class='status {escape(log['status'] or '')}'>{escape(log['status'] or '')}</span></td>"
            f"<td>{escape(log['error_message'] or '')}</td>"
            "</tr>"
        )
    return layout(
        "Usage",
        "usage",
        f"""
        <section class="page-title">
          <div>
            <p class="eyebrow">Usage</p>
            <h1>用量记录</h1>
            <p>查看请求模型、实际上游、token 统计、扣费和失败原因。</p>
          </div>
        </section>
        <section class="table-wrap">
          <table>
            <thead><tr><th>时间</th><th>模型</th><th>上游</th><th>输入/输出</th><th>扣费</th><th>状态</th><th>错误</th></tr></thead>
            <tbody>{''.join(rows) if rows else _empty_row(7, '暂无调用记录')}</tbody>
          </table>
        </section>
        """,
        variant="app",
    )


def docs_page(settings: Settings) -> str:
    base = escape(settings.public_api_base)
    return layout(
        "Docs",
        "docs",
        f"""
        <section class="center-head compact">
          <p class="eyebrow">Docs</p>
          <h1>接入文档</h1>
          <p>兼容 OpenAI Chat Completions。Cursor、Cline、Claude Code 可以直接走 OpenAI-compatible 配置。</p>
        </section>
        <section class="docs-grid">
          <article>
            <h2>OpenAI SDK</h2>
            <pre>from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="{base}/v1"
)

resp = client.chat.completions.create(
    model="yu-chat-auto",
    messages=[{{"role": "user", "content": "你好"}}]
)
print(resp.choices[0].message.content)</pre>
          </article>
          <article>
            <h2>curl</h2>
            <pre>curl {base}/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "yu-code-auto",
    "messages": [
      {{"role": "user", "content": "写一个 Python 爬虫"}}
    ]
  }}'</pre>
          </article>
          <article>
            <h2>Cursor / Cline</h2>
            <pre>API Provider: OpenAI Compatible
Base URL: {base}/v1
API Key: YOUR_API_KEY
Model: yu-code-auto</pre>
          </article>
          <article>
            <h2>Claude Code</h2>
            <pre>export ANTHROPIC_BASE_URL={base}
export ANTHROPIC_AUTH_TOKEN=YOUR_API_KEY
export ANTHROPIC_MODEL=claude-sonnet-economy</pre>
          </article>
        </section>
        """,
        settings=settings,
        variant="public",
    )


def claude_code_page(settings: Settings) -> str:
    base = escape(settings.public_api_base)
    return layout(
        "Claude Code",
        "claude",
        f"""
        <section class="page-title">
          <div>
            <p class="eyebrow">Claude Code / Cursor / Cline</p>
            <h1>AI 编程工具接入</h1>
            <p>这是最容易转化的入口：用户只需要复制 Base URL、API Key 和模型名，就能把工具切到你的平台。</p>
          </div>
          <a class="button primary" href="{escape(settings.register_url)}">获取 API Key</a>
        </section>
        <section class="tool-grid">
          <article>
            <h2>Cursor / Cline</h2>
            <pre>API Provider: OpenAI Compatible
Base URL: {base}/v1
API Key: YOUR_API_KEY
Model: yu-code-auto</pre>
          </article>
          <article>
            <h2>Claude Code</h2>
            <pre>export ANTHROPIC_BASE_URL={base}
export ANTHROPIC_AUTH_TOKEN=YOUR_API_KEY
export ANTHROPIC_MODEL=claude-sonnet-economy</pre>
          </article>
          <article>
            <h2>经济线</h2>
            <p>适合个人开发者、低频调用、代码解释、脚本生成。</p>
            <code>claude-sonnet-economy</code>
          </article>
          <article>
            <h2>自动线</h2>
            <p>平台自动选择 Claude / GPT / Qwen / DeepSeek，同步考虑价格和稳定性。</p>
            <code>yu-code-auto</code>
          </article>
        </section>
        """,
        settings=settings,
        variant="public",
    )


def status_page(providers: Iterable[dict[str, Any]]) -> str:
    rows = []
    for provider in providers:
        public_status = "online" if provider["status"] == "active" else "standby"
        rows.append(
            "<tr>"
            f"<td><strong>{escape(provider['name'])}</strong><small>{escape(provider['slug'])}</small></td>"
            f"<td><span class='status {escape(provider['status'])}'>{escape(public_status)}</span></td>"
            f"<td>{escape(provider['type'])}</td>"
            f"<td>{int(provider['avg_latency_ms'] or 0)} ms</td>"
            "</tr>"
        )
    return layout(
        "Status",
        "status",
        f"""
        <section class="center-head compact">
          <p class="eyebrow">Status</p>
          <h1>上游状态</h1>
          <p>公开状态页只展示可用性，不暴露上游 Key、真实余额和内部成本。</p>
        </section>
        <section class="table-wrap">
          <table>
            <thead><tr><th>线路</th><th>状态</th><th>类型</th><th>平均延迟</th></tr></thead>
            <tbody>{''.join(rows) if rows else _empty_row(4, '暂无上游')}</tbody>
          </table>
        </section>
        """,
        variant="public",
    )


def login_page(settings: Settings) -> str:
    return auth_page(
        settings,
        title="登录账户",
        subtitle="登录后进入控制台，管理余额、充值、API Key 和用量记录。",
        primary_text="进入控制台",
        primary_href=settings.app_base_url,
        alternate_text="还没有账户？立即注册",
        alternate_href=settings.register_url,
        active="login",
    )


def register_page(settings: Settings) -> str:
    return auth_page(
        settings,
        title="注册账户",
        subtitle="上线后这里会连接 New API 的注册页，也可以接 OAuth / 邀请码 / 邮箱验证。",
        primary_text="创建账户",
        primary_href=settings.app_base_url,
        alternate_text="已有账户？去登录",
        alternate_href=settings.login_url,
        active="register",
    )


def auth_page(
    settings: Settings,
    *,
    title: str,
    subtitle: str,
    primary_text: str,
    primary_href: str,
    alternate_text: str,
    alternate_href: str,
    active: str,
) -> str:
    return layout(
        title,
        active,
        f"""
        <section class="auth-shell">
          <div class="auth-brand">
            <span class="brand-mark">Y</span>
            <strong>{escape(settings.site_name)}</strong>
            <p>多模型 API 分发平台</p>
          </div>
          <div class="auth-card">
            <h1>{escape(title)}</h1>
            <p>{escape(subtitle)}</p>
            <label>邮箱</label>
            <input placeholder="you@example.com">
            <label>密码</label>
            <input placeholder="至少 8 位" type="password">
            <a class="button primary full" href="{escape(primary_href)}">{escape(primary_text)}</a>
            <a class="text-link" href="{escape(alternate_href)}">{escape(alternate_text)}</a>
            <small>生产环境建议直接接 New API 登录/注册，本站只保留品牌入口。</small>
          </div>
        </section>
        """,
        settings=settings,
        variant="auth",
    )


def newapi_plan_page(settings: Settings) -> str:
    newapi = escape(settings.newapi_base_url or "http://127.0.0.1:3000")
    upstream_rows = _upstream_strategy_rows()
    route_rows = _newapi_route_rows()
    return layout(
        "New API Plan",
        "newapi",
        f"""
        <section class="page-title">
          <div>
            <p class="eyebrow">Launch Plan</p>
            <h1>NewAPI 混合上游上线方案</h1>
            <p>生产版用 NewAPI 承接用户、充值、Token、渠道、模型、倍率和日志；本站负责官网、价格、Claude Code 教程和获客。核心策略是低价、稳定、国产三条线同时存在。</p>
          </div>
          <a class="button primary" href="{newapi}">打开 New API</a>
        </section>
        <section class="feature-grid">
          <div><h2>低价主力</h2><p>RightCode 负责 Claude / GPT / Gemini 的利润空间，但低权重运行，必须配合稳定线兜底。</p></div>
          <div><h2>稳定主力</h2><p>PoloAPI 或 weelinking 权重更高，优先保障成功率、延迟和企业口碑。</p></div>
          <div><h2>国产主力</h2><p>SiliconFlow 承接 DeepSeek、Qwen、豆包、GLM、Embedding，是默认利润和规模化调用核心。</p></div>
          <div><h2>全能补充</h2><p>jiekou.ai、APIMart、token.chhai.cn 用作模型补货、图像视频、Claude Code 备用。</p></div>
        </section>
        <section class="table-wrap">
          <h2>上游优先级</h2>
          <table>
            <thead><tr><th>优先级</th><th>平台</th><th>类型</th><th>主要覆盖</th><th>NewAPI 用途</th></tr></thead>
            <tbody>{upstream_rows}</tbody>
          </table>
        </section>
        <section class="table-wrap">
          <h2>热门模型冗余</h2>
          <table>
            <thead><tr><th>模型线</th><th>主渠道</th><th>低价补充</th><th>备用</th><th>备注</th></tr></thead>
            <tbody>{route_rows}</tbody>
          </table>
        </section>
        <section class="quickstart">
          <div>
            <h2>NewAPI 配置顺序</h2>
            <p>先接渠道，再精简模型，再设置分组倍率和 failover。每家先充 100-300 元，只开放通过长上下文、工具调用、Claude Code / Cursor 测试的模型。</p>
          </div>
          <pre>1. 部署 NewAPI
2. 添加 SiliconFlow / RightCode / PoloAPI 或 weelinking / jiekou.ai
3. 每个热门模型保留 2-3 个渠道
4. 稳定渠道权重高，低价渠道权重低
5. 开启失败自动切换和重试
6. 配置支付宝/微信/兑换码/人工充值
7. 用 Cherry Studio、Claude Code、Cursor 做压力和兼容性测试</pre>
        </section>
        <section class="quickstart">
          <div>
            <h2>Docker Compose</h2>
            <p>已生成 <code>ops/newapi-compose.yml</code>，服务器到位后可以直接部署。</p>
          </div>
          <pre>docker compose -f ops/newapi-compose.yml up -d</pre>
        </section>
        <section class="risk-note">
          <strong>风险提醒</strong>
          <p>RightCode 这类极低价渠道只能做补充和利润优化，不能单独承载生产主链路。上线默认策略应是稳定渠道优先，低价渠道参与 failover 或低成本线路，国产模型承担高频和利润主力。</p>
        </section>
        """,
        settings=settings,
        variant="admin",
    )


def admin_page(
    overview: dict[str, Any],
    providers: Iterable[dict[str, Any]],
    models: Iterable[dict[str, Any]],
    logs: Iterable[dict[str, Any]],
    settings: Settings,
) -> str:
    provider_rows = []
    for provider in providers:
        provider_rows.append(
            "<tr>"
            f"<td><strong>{escape(provider['slug'])}</strong><small>{escape(provider['name'])}</small></td>"
            f"<td><span class='status {escape(provider['status'])}'>{escape(provider['status'])}</span></td>"
            f"<td>{escape(provider['type'])}</td>"
            f"<td>{float(provider['balance']):.2f}</td>"
            f"<td>{int(provider['consecutive_failures'])}</td>"
            f"<td>{float(provider['error_rate']):.1f}%</td>"
            f"<td>{escape(provider['last_error'] or '')}</td>"
            "</tr>"
        )
    model_rows = "".join(
        f"<tr><td>{escape(model['internal_model'])}</td><td>{_line_badge(model['line_type'])}</td><td>{_money(model['input_price'], settings, decimals=3)}</td><td>{_money(model['output_price'], settings, decimals=3)}</td></tr>"
        for model in models
    )
    log_rows = []
    for log in logs:
        log_rows.append(
            "<tr>"
            f"<td>{escape(log['created_at'] or '')}</td>"
            f"<td>{escape(log['email'] or '')}</td>"
            f"<td>{escape(log['request_model'] or '')}</td>"
            f"<td>{escape(log['actual_provider'] or '')}</td>"
            f"<td>{escape(log['status'] or '')}</td>"
            f"<td>{_money(log['charge'] or 0, settings, decimals=8)}</td>"
            f"<td>{_money(log['margin'] or 0, settings, decimals=8)}</td>"
            f"<td>{escape(log['error_message'] or '')}</td>"
            "</tr>"
        )
    return layout(
        "Admin",
        "admin",
        f"""
        <section class="page-title">
          <div>
            <p class="eyebrow">Admin</p>
            <h1>运营面板</h1>
            <p>上游状态、模型价格、流水和毛利监控。</p>
          </div>
        </section>
        <section class="metrics">
          <div><strong>{overview['users']}</strong><span>用户</span></div>
          <div><strong>{overview['active_keys']}</strong><span>可用 Key</span></div>
          <div><strong>{overview['active_providers']}</strong><span>活跃上游</span></div>
          <div><strong>{overview['today_requests']}</strong><span>今日请求</span></div>
          <div><strong>{_money(overview['today_charge'], settings, decimals=4)}</strong><span>今日流水</span></div>
          <div><strong>{_money(overview['today_margin'], settings, decimals=4)}</strong><span>今日毛利</span></div>
        </section>
        <section class="table-wrap">
          <h2>上游监控</h2>
          <table>
            <thead><tr><th>上游</th><th>状态</th><th>类型</th><th>余额</th><th>连续失败</th><th>错误率</th><th>最后错误</th></tr></thead>
            <tbody>{''.join(provider_rows)}</tbody>
          </table>
        </section>
        <section class="table-wrap two">
          <div>
            <h2>模型价格</h2>
            <table><thead><tr><th>模型</th><th>线</th><th>输入</th><th>输出</th></tr></thead><tbody>{model_rows}</tbody></table>
          </div>
          <div>
            <h2>近期日志</h2>
            <table><thead><tr><th>时间</th><th>用户</th><th>模型</th><th>上游</th><th>状态</th><th>扣费</th><th>毛利</th><th>错误</th></tr></thead><tbody>{''.join(log_rows) if log_rows else _empty_row(8, '暂无日志')}</tbody></table>
          </div>
        </section>
        """,
        settings=settings,
        variant="admin",
    )


def _pricing_plan_cards(settings: Settings) -> str:
    plans = [
        {
            "name": "Free",
            "price": 0,
            "yearly": "注册即送 ¥5 体验额度",
            "badge": "",
            "class": "",
            "tagline": "先让用户跑通工具，降低注册后流失。",
            "rights": ["¥5 等值体验额度", "优先体验低成本模型", "高峰期不承诺优先级"],
            "support": ["全天可用", "社区支持", "公开文档和示例"],
            "rates": [("Claude", "按量"), ("Codex", "按量"), ("国产模型", "试用优先")],
            "cta": "免费体验",
        },
        {
            "name": "Starter",
            "price": 29,
            "yearly": "月含 ¥35 等值额度",
            "badge": "",
            "class": "",
            "tagline": "给小白和轻度 Cursor 用户一个低门槛月卡。",
            "rights": ["低成本模型优先", "适合日常问答和轻量代码", "微信支付即可开通"],
            "support": ["全天可用", "工单处理", "异常订单人工补单"],
            "rates": [("Claude", "按量"), ("Codex", "按量"), ("国产模型", "低价包")],
            "cta": "立即购买",
        },
        {
            "name": "Builder",
            "price": 69,
            "yearly": "月含 ¥90 等值额度",
            "badge": "推荐",
            "class": "featured",
            "tagline": "主推套餐，覆盖大多数 AI 编程和 Agent 测试。",
            "rights": ["更高通用额度", "适合 Claude Code / Cursor 日常开发", "热门模型自动路由"],
            "support": ["全天可用", "优先排障", "协助配置 Claude Code / Cursor"],
            "rates": [("Claude", "标准按量"), ("Codex", "标准按量"), ("国产模型", "折扣优先")],
            "cta": "立即购买",
        },
        {
            "name": "Team",
            "price": 199,
            "yearly": "月含 ¥280 等值额度",
            "badge": "顶级",
            "class": "top-tier",
            "tagline": "工作室、RPA、Agent 批量调用和小团队共享。",
            "rights": ["团队额度池", "更高 RPM / TPM", "支持专属模型白名单"],
            "support": ["专属人工支持", "上线接入协助", "异常调用优先处理"],
            "rates": [("Claude", "优先通道"), ("Codex", "优先通道"), ("国产模型", "最低档")],
            "cta": "联系开通",
        },
    ]
    cards = []
    for plan in plans:
        rights = "".join(f"<li>{escape(item)}</li>" for item in plan["rights"])
        support = "".join(f"<li>{escape(item)}</li>" for item in plan["support"])
        rates = "".join(
            f"<span><b>{escape(model)}</b><em>{escape(rate)}</em></span>"
            for model, rate in plan["rates"]
        )
        badge = f"<span class='plan-badge'>{escape(plan['badge'])}</span>" if plan["badge"] else ""
        cards.append(
            f"""
            <article class="plan-card {escape(plan['class'])}">
              <div class="plan-head">
                <div>
                  <span class="plan-name">{escape(plan['name'])}</span>
                  <p>{escape(plan['tagline'])}</p>
                </div>
                {badge}
              </div>
              <div class="plan-price">
                <strong>{_money(plan['price'], settings, decimals=0)}</strong>
                <span>/ 月</span>
              </div>
              <div class="plan-year">{escape(plan['yearly'])}</div>
              <div class="plan-section">
                <h3>套餐权益</h3>
                <ul>{rights}</ul>
              </div>
              <div class="plan-section">
                <h3>服务支持</h3>
                <ul>{support}</ul>
              </div>
              <div class="plan-section">
                <h3>模型倍率</h3>
                <div class="mini-rates">{rates}</div>
              </div>
              <a class="button primary full" href="{escape(settings.register_url)}">{escape(plan['cta'])}</a>
            </article>
            """
        )
    return "".join(cards)


def _growth_funnel_cards(settings: Settings) -> str:
    items = [
        (
            "免费试用",
            "注册即送 ¥5",
            "只推荐 DeepSeek、Qwen、豆包等低成本模型，先让用户跑通 yu-code-auto / Cursor / Claude Code 接入。",
        ),
        (
            "充值转化",
            "¥10 起充，主推 ¥29 月卡",
            "支付方式保持微信支付；按量充值做兜底，月卡负责复购和稳定现金流。",
        ),
        (
            "邀请裂变",
            "被邀额外 ¥3，邀请人 ¥5",
            "第一版用额度奖励快速上线；订单稳定后再做首充 15% 返佣。",
        ),
    ]
    return "".join(
        f"""
        <div class="conversion-card">
          <span>{escape(label)}</span>
          <strong>{escape(metric)}</strong>
          <p>{escape(desc)}</p>
        </div>
        """
        for label, metric, desc in items
    )


def _pricing_ladder_table(settings: Settings) -> str:
    rows = [
        ("免费体验", "¥0", "¥5 体验额度", "注册即送；限低成本模型优先体验"),
        ("小额充值", "¥10", "¥10 到账", "验证支付和 API Key，适合首单"),
        ("入门月卡", "¥29/月", "¥35 等值额度", "主推小白转化，适合轻度 Cursor 使用"),
        ("开发者月卡", "¥69/月", "¥90 等值额度", "主推套餐，适合日常 Claude Code / Agent 测试"),
        ("专业月卡", "¥129/月", "¥180 等值额度", "适合高频调用和长上下文调试"),
        ("团队月卡", "¥299/月", "¥450 等值额度", "适合工作室共享额度池和优先支持"),
        ("大额充值", "¥500", "¥625 等值额度", "仅建议熟客/团队使用，人工风控"),
    ]
    rendered = [
        "<div class='ladder-row head'><span>档位</span><span>用户支付</span><span>到账/权益</span><span>定位</span></div>"
    ]
    rendered.extend(
        "<div class='ladder-row'>"
        f"<span><strong>{escape(name)}</strong></span>"
        f"<span>{escape(price)}</span>"
        f"<span>{escape(value)}</span>"
        f"<span>{escape(note)}</span>"
        "</div>"
        for name, price, value, note in rows
    )
    rendered.append(
        f"<div class='rate-foot'>按量充值最低 {_money(settings.min_recharge_amount, settings, decimals=2)}；月卡额度不建议覆盖 Claude / GPT / Gemini 最新模型的亏本调用。</div>"
    )
    return "".join(rendered)


def _referral_rules(settings: Settings) -> str:
    rows = [
        ("新用户", "注册即送 ¥5", "无需支付，降低试用门槛。"),
        ("被邀请人", "额外 +¥3", "使用邀请链接注册后叠加，总体验额度 ¥8。"),
        ("邀请人", "成功邀请 +¥5", "第一版固定额度，避免首期开发复杂度过高。"),
        ("首充返佣", "建议 15%", "第二阶段接订单回调；首充返佣上限 ¥50/人，防刷。"),
        ("风控", "同设备/同 IP 限制", "异常注册不发放奖励，可转人工审核。"),
    ]
    return "".join(
        f"""
        <div class="referral-rule">
          <strong>{escape(role)}</strong>
          <span>{escape(reward)}</span>
          <p>{escape(note)}</p>
        </div>
        """
        for role, reward, note in rows
    )


def _pricing_rate_rows(settings: Settings) -> str:
    rows = [
        ("Anthropic Claude", "1.15x - 1.60x", "国外最新模型，稳定渠道更贵，低价渠道做补充。"),
        ("OpenAI Codex / GPT", "1.15x - 1.50x", "代码、Agent、工具调用重点测试 failover。"),
        ("Google Gemini", "1.20x - 1.45x", "大上下文和多模态补充，按实测模型名开放。"),
        ("DeepSeek / Qwen / 豆包", "0.80x - 1.00x", "国产模型成本低，适合做默认推荐和利润主力。"),
    ]
    rendered = [
        "<div class='rate-row head'><span>模型</span><span>套餐倍率</span><span>说明</span></div>"
    ]
    rendered.extend(
        "<div class='rate-row'>"
        f"<span><strong>{escape(model)}</strong></span>"
        f"<span>{escape(rate)}</span>"
        f"<span>{escape(note)}</span>"
        "</div>"
        for model, rate, note in rows
    )
    rendered.append(
        f"<div class='rate-foot'>最低充值 {_money(settings.min_recharge_amount, settings, decimals=2)}，余额按 {escape(settings.billing_currency)} 扣费。</div>"
    )
    return "".join(rendered)


def _capacity_cards() -> str:
    items = [
        ("NewAPI 底座", "用户、Token、充值、日志和模型倍率交给 NewAPI，官网只负责获客和转化。"),
        ("多上游冗余", "Claude / GPT / Gemini 至少 2-3 个渠道，SiliconFlow 承接国产高频调用。"),
        ("限流与分组", "Free / Pro / Max / Ultra 分组设置 RPM、TPM、倍率和高峰期优先级。"),
        ("监控与补单", "支付回调、余额异常、上游失败和毛利波动都需要后台可见并能人工处理。"),
    ]
    return "".join(
        f"""
        <div class="capacity-card">
          <strong>{escape(title)}</strong>
          <p>{escape(desc)}</p>
        </div>
        """
        for title, desc in items
    )


def _model_card(model: dict[str, Any], settings: Settings, *, featured: bool) -> str:
    border_class = " featured" if featured else ""
    tag = "热门" if featured else model["line_type"]
    provider = _provider_hint(model["internal_model"])
    return f"""
    <article class="model-card{border_class}">
      <div class="card-top">
        <h2>{escape(model['internal_model'])}</h2>
        <span class="tag">{escape(tag)}</span>
      </div>
      <p class="provider">{escape(provider)}</p>
      <p class="desc">{escape(model['description'] or 'OpenAI-compatible route.')}</p>
      <div class="price-lines">
        <span>输入价格 <strong>{_money(model['input_price'], settings, decimals=2)}/M tokens</strong></span>
        <span>输出价格 <strong>{_money(model['output_price'], settings, decimals=2)}/M tokens</strong></span>
      </div>
    </article>
    """


def _provider_hint(model_name: str) -> str:
    if "claude" in model_name:
        return "RightCode / PoloAPI / jiekou"
    if "gpt" in model_name:
        return "RightCode / PoloAPI / weelinking"
    if "gemini" in model_name:
        return "Gemini via Stable Mix"
    if "deepseek" in model_name:
        return "SiliconFlow / DeepSeek"
    if "qwen" in model_name:
        return "SiliconFlow / Qwen"
    if "doubao" in model_name:
        return "SiliconFlow / Doubao"
    return "Auto Route"


def _provider_mix_cards() -> str:
    items = [
        ("RightCode", "极致低价", "Claude / Codex / Gemini 低价补充，适合省成本和赚差价，但必须低权重。"),
        ("PoloAPI / weelinking", "稳定中价", "稳定渠道权重更高，承接 Claude、GPT、Gemini 主力请求和企业用户。"),
        ("SiliconFlow", "国产主力", "DeepSeek、Qwen、豆包、GLM、Embedding 优先接这里，成本低、速度快。"),
        ("jiekou.ai / APIMart", "全能补充", "模型补货、图像视频、Claude Code 备用，适合做覆盖面和应急切换。"),
    ]
    return "".join(f"<div><h2>{escape(name)}</h2><strong>{escape(tag)}</strong><p>{escape(desc)}</p></div>" for name, tag, desc in items)


def _model_category_cards() -> str:
    items = [
        ("文本", "Claude、GPT、Gemini、DeepSeek、Qwen、豆包、Kimi、GLM。"),
        ("代码", "Claude Sonnet、GPT Codex、Qwen Coder、DeepSeek Coder，重点服务 Claude Code / Cursor。"),
        ("图像", "Flux、GPT Image、通义万相、豆包图像，生产版放到 NewAPI 渠道里开放。"),
        ("视频 / Embedding", "Kling / 可灵后续扩展；Embedding 用 Qwen、BGE 等国产低成本线路。"),
    ]
    return "".join(f"<div><h2>{escape(name)}</h2><p>{escape(desc)}</p></div>" for name, desc in items)


def _upstream_strategy_rows() -> str:
    rows = [
        ("1", "RightCode", "极致低价", "Claude Opus / Sonnet、GPT Codex、Gemini", "低价补充、利润优化、Claude Code 专线测试"),
        ("2", "PoloAPI / weelinking", "稳定中价", "Claude、GPT、Gemini、DeepSeek、Qwen", "稳定主力、高权重、企业用户优先"),
        ("3", "SiliconFlow", "国产最优", "DeepSeek、Qwen、豆包、GLM、Embedding", "国产默认主力、高频调用、利润核心"),
        ("4", "jiekou.ai / APIMart / token.chhai.cn", "全能补充", "御三家、图像、视频、备用模型", "补货、备用、模型丰富度"),
    ]
    return "".join(
        "<tr>"
        f"<td>{escape(priority)}</td>"
        f"<td><strong>{escape(platform)}</strong></td>"
        f"<td>{escape(kind)}</td>"
        f"<td>{escape(models)}</td>"
        f"<td>{escape(use)}</td>"
        "</tr>"
        for priority, platform, kind, models, use in rows
    )


def _newapi_route_rows() -> str:
    rows = [
        ("Claude Sonnet 最新", "PoloAPI / weelinking", "RightCode", "jiekou.ai", "代码和 Agent 用户主力，必须测工具调用和长上下文。"),
        ("GPT-5.x / Codex", "PoloAPI / weelinking", "RightCode Codex", "APIMart", "对外可分低价线和稳定线，避免低价渠道全量承载。"),
        ("Gemini Pro / Flash", "PoloAPI / weelinking", "RightCode Gemini", "APIMart", "适合多模态和低价大上下文，实测模型名后开放。"),
        ("DeepSeek / Qwen / 豆包", "SiliconFlow", "官方直连", "PoloAPI", "国产模型做默认推荐和利润主力。"),
        ("图像 / 视频", "APIMart / SiliconFlow", "jiekou.ai", "token.chhai.cn", "第二阶段逐步开放，先不要影响文本 API 稳定。"),
    ]
    return "".join(
        "<tr>"
        f"<td><strong>{escape(model)}</strong></td>"
        f"<td>{escape(primary)}</td>"
        f"<td>{escape(cheap)}</td>"
        f"<td>{escape(backup)}</td>"
        f"<td>{escape(note)}</td>"
        "</tr>"
        for model, primary, cheap, backup, note in rows
    )


def _line_badge(line_type: str) -> str:
    return f"<span class='line-badge {escape(line_type)}'>{escape(line_type)}</span>"


def _money(amount: float | int | str, settings: Settings, *, decimals: int = 2) -> str:
    symbol = escape(settings.billing_symbol)
    return f"{symbol}{float(amount):.{decimals}f}"


def _order_money(order: dict[str, Any], settings: Settings) -> str:
    if str(order.get("channel") or "") == "mock":
        return _money(order["amount"], settings, decimals=2)
    currency = str(order.get("currency") or settings.billing_currency).upper()
    if currency == settings.billing_currency:
        return _money(order["amount"], settings, decimals=2)
    return f"{float(order['amount']):.2f} {escape(currency)}"


def _notice(text: str, kind: str = "success") -> str:
    if not text:
        return ""
    safe_kind = "error" if kind == "error" else "success"
    return f"<div class='notice {safe_kind}'>{escape(text)}</div>"


def _new_key_box(new_key: str) -> str:
    if not new_key:
        return ""
    return f"""
    <section class="secret-box">
      <span>新 API Key</span>
      <code>{escape(new_key)}</code>
    </section>
    """


def _empty_row(colspan: int, text: str) -> str:
    return f"<tr><td colspan='{colspan}' class='empty'>{escape(text)}</td></tr>"


def layout(
    title: str,
    active: str,
    body: str,
    *,
    settings: Settings | None = None,
    variant: str = "public",
) -> str:
    cfg = settings or default_settings
    if variant == "app":
        nav = [
            ("dashboard", "/dashboard", "控制台"),
            ("recharge", "/recharge", "充值"),
            ("keys", "/keys", "API Keys"),
            ("usage", "/usage", "用量"),
            ("docs", "/docs", "文档"),
        ]
        actions = f"<a class='button ghost' href='/'>返回官网</a>"
    elif variant == "admin":
        nav = [
            ("admin", "/admin", "运营面板"),
            ("newapi", "/newapi", "New API 方案"),
            ("status", "/status", "状态页"),
            ("models", "/", "官网"),
        ]
        actions = f"<a class='button ghost' href='{escape(cfg.admin_console_url)}'>管理入口</a>"
    elif variant == "auth":
        nav = [("models", "/", "返回官网"), ("docs", "/docs", "文档")]
        actions = ""
    else:
        nav = [
            ("home", "/", "首页"),
            ("pricing", "/pricing", "价格"),
            ("docs", "/docs", "文档"),
            ("claude", "/claude-code", "Claude Code"),
            ("status", "/status", "状态"),
        ]
        actions = (
            f"<a class='button ghost' href='{escape(cfg.login_url)}'>登录</a>"
            f"<a class='button primary' href='{escape(cfg.register_url)}'>注册</a>"
        )
    links = "".join(
        f"<a class='{'active' if key == active else ''}' href='{href}'>{label}</a>"
        for key, href, label in nav
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} · Yu Gateway</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #111827;
      --muted: #526071;
      --soft: #718096;
      --line: #e3e7ee;
      --paper: #ffffff;
      --wash: #f8fafc;
      --blue: #2563eb;
      --blue-dark: #1d4ed8;
      --green: #16a34a;
      --green-soft: #dcfce7;
      --red: #b91c1c;
      --amber: #b7791f;
      --shadow: 0 8px 24px rgba(15, 23, 42, .06);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: var(--paper); letter-spacing: 0; }}
    header {{ position: sticky; top: 0; z-index: 2; display: flex; justify-content: space-between; align-items: center; gap: 18px; min-height: 64px; padding: 12px 34px; border-bottom: 1px solid var(--line); background: rgba(255,255,255,.96); backdrop-filter: blur(10px); }}
    .brand {{ display: inline-flex; align-items: center; gap: 10px; color: var(--ink); text-decoration: none; font-size: 20px; font-weight: 800; }}
    .brand-mark {{ width: 30px; height: 30px; border: 2px solid var(--blue); border-radius: 8px; display: grid; place-items: center; color: var(--blue); font-weight: 900; line-height: 1; }}
    .nav-wrap {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    nav {{ display: flex; align-items: center; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }}
    nav a {{ color: var(--ink); text-decoration: none; padding: 8px 10px; border-radius: 8px; font-size: 14px; white-space: nowrap; }}
    nav a.active, nav a:hover {{ background: #edf2ff; color: var(--blue-dark); }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 26px 18px 70px; }}
    .center-head {{ text-align: center; padding: 16px 0 34px; }}
    .center-head.compact {{ padding-bottom: 22px; }}
    .pricing-stage {{ position: relative; margin: 0 -18px 34px; padding: 54px 18px 38px; border-radius: 0 0 26px 26px; background: #08111f; color: #f8fafc; overflow: hidden; }}
    .pricing-stage::before {{ content: ""; position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,.055) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.055) 1px, transparent 1px); background-size: 46px 46px; opacity: .35; pointer-events: none; }}
    .pricing-stage::after {{ content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(34, 197, 94, .8), rgba(245, 158, 11, .65), transparent); }}
    .pricing-stage > * {{ position: relative; z-index: 1; max-width: 1204px; margin-left: auto; margin-right: auto; }}
    .pricing-hero {{ text-align: center; padding: 18px 0 34px; }}
    .pricing-hero .eyebrow {{ color: #93c5fd; letter-spacing: 0; }}
    .pricing-hero h1 {{ max-width: 900px; margin: 0 auto; font-size: 52px; line-height: 1.08; color: #fff; }}
    .pricing-hero p {{ margin: 18px auto 0; max-width: 820px; color: #b8c4d5; font-size: 17px; line-height: 1.8; }}
    .billing-toggle {{ width: fit-content; margin: 24px auto 0; display: inline-flex; gap: 4px; padding: 5px; border: 1px solid rgba(255,255,255,.16); border-radius: 12px; background: rgba(255,255,255,.08); backdrop-filter: blur(10px); }}
    .billing-toggle span {{ min-width: 108px; padding: 9px 13px; border-radius: 9px; font-weight: 900; color: #b8c4d5; font-size: 14px; }}
    .billing-toggle span.active {{ background: #fff; color: #08111f; box-shadow: 0 16px 38px rgba(0,0,0,.24); }}
    .billing-toggle b {{ color: #86efac; font-size: 12px; }}
    .hero-stats {{ margin: 24px auto 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; max-width: 760px; }}
    .hero-stats span {{ border: 1px solid rgba(255,255,255,.14); border-radius: 12px; background: rgba(255,255,255,.07); color: #b8c4d5; padding: 13px 14px; font-weight: 800; }}
    .hero-stats strong {{ display: block; color: #fff; font-size: 24px; line-height: 1.1; }}
    .plan-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; align-items: stretch; margin: 10px 0 0; }}
    .plan-card {{ position: relative; display: flex; flex-direction: column; min-height: 650px; border: 1px solid rgba(255,255,255,.13); border-radius: 18px; background: rgba(255,255,255,.082); padding: 22px; box-shadow: 0 30px 70px rgba(0,0,0,.28); backdrop-filter: blur(16px); }}
    .plan-card.featured {{ border-color: rgba(34, 197, 94, .85); box-shadow: 0 30px 80px rgba(34, 197, 94, .18); background: rgba(14, 47, 37, .58); }}
    .plan-card.top-tier {{ border-color: rgba(245, 158, 11, .9); box-shadow: 0 30px 80px rgba(245, 158, 11, .16); background: rgba(51, 37, 14, .54); }}
    .plan-head {{ min-height: 96px; display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }}
    .plan-name {{ display: block; margin-bottom: 8px; color: #fff; font-size: 24px; font-weight: 900; }}
    .plan-head p {{ margin: 0; color: #b8c4d5; line-height: 1.55; }}
    .plan-badge {{ flex: 0 0 auto; padding: 5px 9px; border-radius: 999px; background: #dcfce7; color: #166534; font-size: 12px; font-weight: 900; }}
    .top-tier .plan-badge {{ background: #fef3c7; color: #92400e; }}
    .plan-price {{ margin-top: 8px; display: flex; align-items: baseline; gap: 6px; }}
    .plan-price strong {{ color: #fff; font-size: 46px; letter-spacing: 0; }}
    .plan-price span, .plan-year {{ color: #b8c4d5; font-weight: 700; }}
    .plan-year {{ min-height: 24px; margin: 2px 0 18px; }}
    .plan-section {{ padding: 15px 0; border-top: 1px solid rgba(255,255,255,.12); }}
    .plan-section h3 {{ margin: 0 0 10px; color: #fff; font-size: 15px; }}
    .plan-section ul {{ margin: 0; padding-left: 18px; color: #cbd5e1; line-height: 1.65; }}
    .mini-rates {{ display: grid; gap: 7px; }}
    .mini-rates span {{ display: flex; justify-content: space-between; gap: 10px; font-size: 13px; }}
    .mini-rates b {{ color: #e2e8f0; }}
    .mini-rates em {{ color: #93c5fd; font-style: normal; font-weight: 900; }}
    .plan-card .button.full {{ margin-top: auto; }}
    .capacity-panel {{ margin: 0 0 28px; display: grid; grid-template-columns: .8fr 1.2fr; gap: 18px; align-items: start; border: 1px solid var(--line); border-radius: 16px; padding: 24px; background: #fff; box-shadow: var(--shadow); }}
    .capacity-panel p {{ color: var(--muted); line-height: 1.7; }}
    .capacity-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    .capacity-card {{ border: 1px solid var(--line); border-radius: 12px; padding: 16px; background: var(--wash); }}
    .capacity-card strong {{ display: block; margin-bottom: 8px; font-size: 16px; }}
    .capacity-card p {{ margin: 0; font-size: 14px; }}
    .pricing-note {{ margin: 18px 0 28px; display: grid; gap: 6px; border: 1px solid #bbf7d0; background: #f0fdf4; color: #14532d; border-radius: 12px; padding: 18px 20px; }}
    .pricing-note p {{ margin: 0; line-height: 1.6; }}
    .pricing-note .text-link {{ margin-top: 4px; color: #166534; }}
    .rate-panel {{ margin: 28px 0; display: grid; grid-template-columns: .75fr 1.25fr; gap: 18px; align-items: start; border: 1px solid var(--line); border-radius: 14px; padding: 24px; background: var(--wash); }}
    .rate-panel p {{ color: var(--muted); line-height: 1.65; }}
    .rate-table {{ border: 1px solid var(--line); border-radius: 12px; overflow: hidden; background: #fff; }}
    .rate-row {{ display: grid; grid-template-columns: 1fr .65fr 1.4fr; gap: 12px; padding: 13px 14px; border-bottom: 1px solid var(--line); align-items: center; color: var(--muted); }}
    .rate-row.head {{ background: #f1f5f9; color: var(--ink); font-size: 12px; font-weight: 900; text-transform: uppercase; }}
    .rate-row strong {{ color: var(--ink); }}
    .rate-foot {{ padding: 13px 14px; color: var(--muted); font-weight: 700; }}
    .conversion-strip, .funnel-panel, .referral-panel {{ margin: 18px 0 30px; border: 1px solid var(--line); border-radius: 16px; padding: 24px; background: #fff; box-shadow: var(--shadow); }}
    .conversion-strip {{ display: grid; grid-template-columns: .78fr 1.22fr; gap: 18px; align-items: start; }}
    .conversion-strip p, .funnel-panel p, .referral-panel p {{ color: var(--muted); line-height: 1.7; }}
    .conversion-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .conversion-card {{ min-height: 190px; border: 1px solid var(--line); border-radius: 12px; padding: 18px; background: var(--wash); }}
    .conversion-card span {{ display: inline-flex; margin-bottom: 12px; color: var(--blue-dark); font-size: 13px; font-weight: 900; }}
    .conversion-card strong {{ display: block; font-size: 24px; line-height: 1.2; }}
    .conversion-card p {{ margin: 12px 0 0; font-size: 14px; }}
    .funnel-panel, .referral-panel {{ display: grid; grid-template-columns: .72fr 1.28fr; gap: 18px; align-items: start; }}
    .ladder-table {{ border: 1px solid var(--line); border-radius: 12px; overflow: hidden; background: #fff; }}
    .ladder-row {{ display: grid; grid-template-columns: .8fr .7fr .9fr 1.5fr; gap: 12px; padding: 13px 14px; border-bottom: 1px solid var(--line); align-items: center; color: var(--muted); }}
    .ladder-row.head {{ background: #f1f5f9; color: var(--ink); font-size: 12px; font-weight: 900; text-transform: uppercase; }}
    .ladder-row strong {{ color: var(--ink); }}
    .referral-rules {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; }}
    .referral-rule {{ border: 1px solid var(--line); border-radius: 12px; padding: 15px; background: var(--wash); }}
    .referral-rule strong {{ display: block; margin-bottom: 8px; }}
    .referral-rule span {{ display: block; color: var(--blue-dark); font-size: 18px; font-weight: 900; }}
    .referral-rule p {{ margin: 10px 0 0; font-size: 13px; }}
    .landing-hero {{ display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(340px, .95fr); gap: 32px; align-items: center; padding: 46px 0 54px; }}
    .landing-hero h1 {{ font-size: 44px; max-width: 760px; }}
    .landing-hero p {{ color: var(--muted); font-size: 17px; line-height: 1.75; max-width: 720px; }}
    .hero-actions {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-top: 24px; }}
    .hero-panel {{ border: 1px solid var(--line); border-radius: 16px; padding: 22px; background: linear-gradient(180deg, #ffffff, #f8fafc); box-shadow: 0 24px 70px rgba(37, 99, 235, .12); }}
    .panel-row {{ display: flex; justify-content: space-between; gap: 18px; padding: 11px 0; border-bottom: 1px solid var(--line); color: var(--muted); }}
    .panel-row strong {{ color: var(--ink); overflow-wrap: anywhere; }}
    .route-stack {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 16px 0; }}
    .route-stack b {{ text-align: center; border-radius: 8px; background: #edf2ff; color: var(--blue-dark); padding: 9px 8px; font-size: 13px; }}
    .eyebrow {{ margin: 0 0 8px; color: var(--blue); font-size: 13px; font-weight: 800; text-transform: uppercase; }}
    h1 {{ margin: 0; font-size: 32px; line-height: 1.18; }}
    h2 {{ margin: 0 0 14px; font-size: 23px; }}
    .center-head p, .page-title p {{ margin: 13px auto 0; max-width: 720px; color: var(--muted); font-size: 16px; line-height: 1.7; }}
    .text-link {{ display: inline-flex; margin-top: 24px; color: var(--blue); font-weight: 700; text-decoration: none; }}
    .page-title {{ display: flex; align-items: center; justify-content: space-between; gap: 20px; margin: 12px 0 22px; }}
    .button, button {{ min-height: 40px; display: inline-flex; align-items: center; justify-content: center; border: 1px solid var(--line); border-radius: 8px; background: #fff; color: var(--ink); padding: 9px 14px; font-weight: 800; cursor: pointer; text-decoration: none; }}
    .button.primary, button.primary, .pay-card button {{ background: var(--blue); color: white; border-color: var(--blue); }}
    .button.ghost {{ background: #fff; color: var(--ink); }}
    .button.full {{ width: 100%; margin-top: 14px; }}
    .model-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 26px; }}
    .model-card {{ min-height: 255px; border: 1px solid var(--line); border-radius: 12px; background: #fff; padding: 28px; box-shadow: var(--shadow); display: flex; flex-direction: column; }}
    .model-card.featured {{ border-color: #86efac; }}
    .card-top {{ display: flex; justify-content: space-between; gap: 14px; align-items: start; }}
    .card-top h2 {{ font-size: 21px; line-height: 1.35; overflow-wrap: anywhere; }}
    .tag, .line-badge {{ display: inline-flex; align-items: center; min-height: 24px; padding: 3px 9px; border-radius: 6px; background: #dbeafe; color: var(--blue); font-size: 12px; font-weight: 800; }}
    .line-badge.auto {{ background: #e0f2fe; color: #0369a1; }}
    .line-badge.economy {{ background: #dcfce7; color: #15803d; }}
    .line-badge.stable {{ background: #fef3c7; color: #92400e; }}
    .provider {{ margin: 6px 0 18px; color: var(--muted); }}
    .desc {{ color: #334155; line-height: 1.55; margin: 0 0 18px; flex: 1; }}
    .price-lines {{ border-top: 1px solid var(--line); padding-top: 14px; display: grid; gap: 7px; color: var(--muted); font-size: 13px; }}
    .price-lines span {{ display: flex; justify-content: space-between; gap: 12px; }}
    .price-lines strong {{ color: var(--muted); font-weight: 600; }}
    .quickstart {{ margin-top: 28px; display: grid; grid-template-columns: .8fr 1.2fr; gap: 18px; align-items: center; border: 1px solid var(--line); border-radius: 12px; padding: 24px; background: var(--wash); }}
    pre {{ margin: 0; background: #0f172a; color: #e5e7eb; padding: 18px; border-radius: 10px; overflow: auto; white-space: pre-wrap; overflow-wrap: anywhere; line-height: 1.55; font-size: 13px; }}
    code {{ background: #eef2ff; color: var(--blue-dark); padding: 2px 5px; border-radius: 4px; }}
    .docs-grid, .tool-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    article h2 {{ color: var(--ink); }}
    article pre {{ min-height: 240px; }}
    article {{ border: 1px solid var(--line); border-radius: 12px; padding: 22px; box-shadow: var(--shadow); background: #fff; }}
    .steps, .feature-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 28px; }}
    .feature-grid {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    .steps div, .feature-grid div {{ border: 1px solid var(--line); border-radius: 12px; background: #fff; box-shadow: var(--shadow); padding: 20px; }}
    .steps strong {{ width: 28px; height: 28px; display: grid; place-items: center; border-radius: 50%; background: var(--blue); color: white; margin-bottom: 12px; }}
    .steps p, .feature-grid p, .tool-grid p {{ color: var(--muted); line-height: 1.6; }}
    .feature-grid strong {{ display: inline-flex; margin-bottom: 10px; color: var(--blue-dark); font-size: 13px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(6, minmax(120px, 1fr)); gap: 12px; margin-bottom: 26px; }}
    .metrics div, .action-card, .pay-card, .balance-pill, .secret-box {{ border: 1px solid var(--line); background: #fff; border-radius: 12px; box-shadow: var(--shadow); }}
    .metrics div {{ padding: 18px; }}
    .metrics strong {{ display: block; font-size: 25px; line-height: 1.2; }}
    .metrics span {{ color: var(--muted); font-size: 13px; }}
    .action-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }}
    .pay-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; }}
    .action-card {{ padding: 20px; text-decoration: none; color: var(--ink); min-height: 120px; }}
    .action-card strong {{ display: block; margin-bottom: 8px; }}
    .action-card span {{ color: var(--muted); line-height: 1.5; }}
    .pay-card {{ padding: 22px; display: grid; gap: 10px; }}
    .pay-card strong {{ font-size: 30px; }}
    .pay-card span {{ color: var(--muted); }}
    .custom-pay strong {{ font-size: 22px; }}
    .custom-pay input {{ min-width: 0; width: 100%; }}
    .plan-pay strong {{ font-size: 22px; }}
    .plan-pay b {{ font-size: 26px; }}
    .balance-pill {{ padding: 13px 16px; font-weight: 900; color: var(--blue-dark); }}
    .notice {{ margin: 0 0 16px; border: 1px solid #bbf7d0; color: #166534; background: #f0fdf4; border-radius: 10px; padding: 12px 14px; font-weight: 700; }}
    .notice.error {{ border-color: #fecaca; color: #991b1b; background: #fef2f2; }}
    .secret-box {{ margin-bottom: 18px; padding: 16px; display: grid; gap: 8px; }}
    .secret-box span {{ color: var(--muted); font-weight: 700; }}
    .secret-box code {{ display: block; overflow-wrap: anywhere; padding: 10px; }}
    .inline-form {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }}
    input {{ min-height: 40px; border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; font: inherit; min-width: 210px; }}
    label {{ display: block; margin: 12px 0 6px; color: var(--muted); font-weight: 800; font-size: 13px; }}
    .auth-shell {{ min-height: calc(100vh - 118px); display: grid; place-items: center; padding: 42px 16px; background: radial-gradient(circle at 50% 20%, rgba(37,99,235,.18), transparent 30%), #101b3d; border-radius: 0 0 18px 18px; margin: -26px -18px -70px; }}
    .auth-brand {{ text-align: center; color: white; margin-bottom: 20px; }}
    .auth-brand .brand-mark {{ margin: 0 auto 10px; background: rgba(255,255,255,.08); color: white; border-color: rgba(255,255,255,.5); }}
    .auth-brand p {{ color: rgba(255,255,255,.7); }}
    .auth-card {{ width: min(440px, 100%); border: 1px solid rgba(255,255,255,.14); border-radius: 16px; background: rgba(255,255,255,.08); color: white; padding: 28px; box-shadow: 0 28px 70px rgba(0,0,0,.22); backdrop-filter: blur(16px); }}
    .auth-card p, .auth-card small {{ color: rgba(255,255,255,.72); line-height: 1.6; }}
    .auth-card input {{ width: 100%; background: rgba(255,255,255,.08); color: white; border-color: rgba(255,255,255,.18); }}
    .auth-card .text-link {{ color: #93c5fd; }}
    .table-wrap {{ margin-top: 24px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid var(--line); border-radius: 12px; overflow: hidden; box-shadow: var(--shadow); }}
    th, td {{ text-align: left; border-bottom: 1px solid var(--line); padding: 13px 14px; vertical-align: top; font-size: 14px; }}
    th {{ color: var(--muted); font-size: 12px; background: #f1f5f9; }}
    td small {{ display: block; color: var(--muted); margin-top: 4px; line-height: 1.45; }}
    .status {{ font-weight: 900; color: var(--amber); }}
    .status.active, .status.success, .status.success_stream_estimated, .status.paid {{ color: var(--green); }}
    .status.disabled, .status.failed, .status.failed_stream {{ color: var(--red); }}
    .empty {{ text-align: center; color: var(--muted); padding: 32px; }}
    .two {{ display: grid; grid-template-columns: .8fr 1.2fr; gap: 16px; align-items: start; }}
    .risk-note {{ margin-top: 24px; border: 1px solid #fed7aa; background: #fff7ed; color: #7c2d12; border-radius: 12px; padding: 18px 20px; }}
    .risk-note p {{ margin: 8px 0 0; line-height: 1.6; }}
    @media (max-width: 980px) {{
      header {{ align-items: flex-start; flex-direction: column; }}
      nav {{ justify-content: flex-start; }}
      .landing-hero, .conversion-strip, .conversion-grid, .funnel-panel, .referral-panel, .referral-rules, .plan-grid, .capacity-panel, .capacity-grid, .rate-panel, .model-grid, .quickstart, .docs-grid, .tool-grid, .two, .steps, .feature-grid {{ grid-template-columns: 1fr; }}
      .plan-card {{ min-height: 0; }}
      .rate-row, .ladder-row {{ grid-template-columns: 1fr; }}
      .metrics, .action-grid, .pay-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .page-title {{ align-items: flex-start; flex-direction: column; }}
      .landing-hero h1 {{ font-size: 34px; }}
      .pricing-hero h1 {{ font-size: 40px; }}
      .hero-stats {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 560px) {{
      header {{ padding: 12px 16px; }}
      main {{ padding: 22px 14px 54px; }}
      h1, .landing-hero h1, .pricing-hero h1 {{ font-size: 28px; }}
      .pricing-stage {{ margin-left: -14px; margin-right: -14px; padding: 36px 14px 28px; border-radius: 0 0 20px 20px; }}
      .billing-toggle {{ width: 100%; }}
      .billing-toggle span {{ min-width: 0; flex: 1; }}
      .model-card {{ padding: 20px; min-height: 0; }}
      .metrics, .action-grid, .pay-grid {{ grid-template-columns: 1fr; }}
      table {{ display: block; overflow-x: auto; }}
      .inline-form {{ justify-content: stretch; width: 100%; }}
      input, .inline-form button {{ width: 100%; }}
    }}
  </style>
</head>
<body>
  <header>
    <a class="brand" href="/"><span class="brand-mark">Y</span><span>{escape(cfg.site_name)}</span></a>
    <div class="nav-wrap"><nav>{links}</nav>{actions}</div>
  </header>
  <main>{body}</main>
</body>
</html>"""
