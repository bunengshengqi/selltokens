from __future__ import annotations

from html import escape
from typing import Any, Iterable

from .config import Settings, settings as default_settings
from .policy import FIRST_RECHARGE_BONUS_USD, FIRST_WAVE_MODEL_SPECS, TOPUP_USD_AMOUNTS


def home_page(settings: Settings, models: Iterable[dict[str, Any]]) -> str:
    model_list = _launch_model_rows()
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
            <h1>一个 API Key，先开放 Claude、GPT、Gemini 七个核心模型。</h1>
          <p>面向 Claude Code、Cursor、Cline 和各类 Agent 工具，一个账户统一管理余额、API Key 和用量记录。</p>
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
              <strong>claude-sonnet-4-6</strong>
            </div>
            <div class="route-stack">
              <b>Claude</b><b>GPT</b><b>Gemini</b>
            </div>
            <pre>curl {escape(settings.public_api_base)}/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -d '{{"model":"claude-haiku-4-5","messages":[{{"role":"user","content":"你好"}}]}}'</pre>
          </div>
        </section>
        <section class="conversion-strip">
          <div>
            <p class="eyebrow">New User Bonus</p>
            <h1>先充值，再加赠，再邀请</h1>
            <p>新用户完成首笔充值后自动加赠 $1 美元额度。账户余额按 USD 展示，微信支付时按固定汇率折算成人民币。</p>
          </div>
          <div class="conversion-grid">{funnel_cards}</div>
        </section>
        <section class="center-head compact">
          <p class="eyebrow">Models</p>
          <h1>支持的模型</h1>
          <p>精选 Claude、GPT、Gemini 系列模型，覆盖高质量推理、日常编程和轻量快速调用。</p>
          <a class="text-link" href="/pricing">查看全部 {len(model_list)} 个模型详情与定价 →</a>
        </section>
        <section class="model-grid">{cards}</section>
        <section class="center-head compact">
          <p class="eyebrow">Why 996 Tokens</p>
          <h1>为开发者准备的 API 服务</h1>
          <p>少折腾配置，多关注自己的项目。我们把模型、余额、文档和接入入口整理成一个清晰的使用体验。</p>
        </section>
        <section class="feature-grid">{mix_cards}</section>
        <section class="center-head compact">
          <p class="eyebrow">Catalog</p>
          <h1>模型分类</h1>
        </section>
        <section class="feature-grid">{category_cards}</section>
        <section class="steps">
          <div><strong>1</strong><h2>注册并充值</h2><p>用户注册后进入控制台，充值余额或兑换额度。</p></div>
          <div><strong>2</strong><h2>创建 API Key</h2><p>在控制台生成 Key，复制后保存到你的开发工具。</p></div>
          <div><strong>3</strong><h2>改一行 Base URL</h2><p>OpenAI SDK / Cursor / Cline 只需要换成平台地址。</p></div>
        </section>
        <section class="feature-grid">
          <div><h2>接入简单</h2><p>兼容 OpenAI 格式，常见 SDK 和工具只需要替换 Base URL。</p></div>
          <div><h2>余额清晰</h2><p>美元余额展示，充值、扣费和用量记录都能在控制台查看；人民币只作为微信支付实付金额。</p></div>
          <div><h2>模型精选</h2><p>默认只展示常用模型，减少选择困扰。</p></div>
          <div><h2>新手友好</h2><p>提供文档、示例命令和常见工具配置教程。</p></div>
        </section>
        """,
        settings=settings,
        variant="public",
    )


def pricing_page(models: Iterable[dict[str, Any]], settings: Settings) -> str:
    plan_cards = _pricing_plan_cards(settings)
    capacity_cards = _capacity_cards()
    ladder_rows = _pricing_ladder_table(settings)
    referral_rules = _referral_rules(settings)
    rows = []
    for model in _launch_model_rows():
        rows.append(
            "<tr>"
            f"<td><strong>{escape(model['internal_model'])}</strong><small>{escape(model['description'] or '')}</small></td>"
            f"<td>{_line_badge(model['line_type'])}</td>"
            f"<td>{_money(model['input_price'], settings, decimals=4)} / M tokens</td>"
            f"<td>{_money(model['output_price'], settings, decimals=4)} / M tokens</td>"
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
            <p>第一版聚焦 Claude、GPT、Gemini 七个核心模型。账户余额和模型单价按 USD 计费，微信支付按固定汇率折算成人民币。</p>
            <div class="billing-toggle" aria-label="充值方式">
              <span class="active">额度充值</span>
              <span>微信支付按汇率折算</span>
            </div>
            <div class="hero-stats">
              <span><strong>100</strong> 人同时在线目标</span>
              <span><strong>7</strong> 个首发模型</span>
              <span><strong>USD</strong> 余额与扣费</span>
            </div>
          </div>
          <section class="plan-grid">{plan_cards}</section>
        </section>
        <section class="capacity-panel">
          <div>
            <p class="eyebrow">Service Target</p>
            <h2>面向高频开发场景设计</h2>
            <p>适合 Claude Code、Cursor、Cline、自动化脚本和 Agent 调用。你只需要管理余额和 API Key，剩下的连接体验由平台处理。</p>
          </div>
          <div class="capacity-grid">{capacity_cards}</div>
        </section>
        <section class="pricing-note">
          <strong>计费说明</strong>
          <p>余额按美元展示并按实际调用扣费。充值时按固定汇率折算成人民币支付，新用户首笔充值后加赠 $1 美元额度。</p>
          <a class="text-link" href="{escape(settings.register_url)}">进入控制台充值额度 →</a>
        </section>
        <section class="funnel-panel">
          <div>
            <p class="eyebrow">Recharge Ladder</p>
            <h2>阶梯收费标准</h2>
            <p>按量充值用于小额尝试和日常补余额。所有加赠都绑定真实支付订单，注册本身不再发放免费额度。</p>
          </div>
          <div class="ladder-table">{ladder_rows}</div>
        </section>
        <section class="referral-panel">
          <div>
            <p class="eyebrow">Referral</p>
            <h2>邀请裂变规则</h2>
            <p>邀请规则会围绕真实充值订单发放奖励，具体额度以活动页和控制台展示为准。</p>
          </div>
          <div class="referral-rules">{referral_rules}</div>
        </section>
        <section class="feature-grid">{_model_category_cards()}</section>
        <section class="table-wrap">
          <h2>按量模型单价</h2>
          <table>
            <thead><tr><th>模型</th><th>类型</th><th>输入价格</th><th>输出价格</th></tr></thead>
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
          <a class="action-card" href="/recharge"><strong>充值余额</strong><span>充值后即可使用模型调用额度。</span></a>
          <a class="action-card" href="/keys"><strong>API Keys</strong><span>创建和查看调用 Key。</span></a>
          <a class="action-card" href="/usage"><strong>用量记录</strong><span>查看模型、tokens、扣费和请求状态。</span></a>
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
    amounts = list(TOPUP_USD_AMOUNTS)
    min_amount = float(settings.min_recharge_amount)
    currency = escape(settings.billing_currency)
    pay_currency = escape(settings.payment_currency)
    amount_cards = "".join(
        f"""
        <form class="pay-card" method="post" action="/recharge">
          <input type="hidden" name="amount" value="{amount}">
          <strong>{_money(amount, settings, decimals=0)} 额度</strong>
          <span>预计实付 {_payment_money(amount, settings)} {pay_currency}，首笔付款加赠 {_money(FIRST_RECHARGE_BONUS_USD, settings, decimals=0)}</span>
          <button type="submit">演示充值</button>
        </form>
        """
        for amount in amounts
    )
    custom_card = f"""
        <form class="pay-card custom-pay" method="post" action="/recharge">
          <strong>自定义金额</strong>
          <span>账户币种：{currency}，最低 {_money(min_amount, settings, decimals=2)}；按汇率折算为人民币支付</span>
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
            <p>账户按 {currency} 计费，最低 {_money(min_amount, settings, decimals=2)}；微信支付按固定汇率 1 USD = {_payment_money(1, settings)} 折算。注册不送额度，新用户首笔付款后加赠 {_money(FIRST_RECHARGE_BONUS_USD, settings, decimals=2)}。</p>
          </div>
          <div class="balance-pill">余额 {_money(user['balance'], settings, decimals=4)}</div>
        </section>
        {_notice(notice, notice_kind)}
        <section class="pay-grid">{amount_cards}{custom_card}</section>
        <section class="table-wrap">
          <h2>充值订单</h2>
          <table>
            <thead><tr><th>订单号</th><th>金额</th><th>支付方式</th><th>状态</th><th>创建时间</th></tr></thead>
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
            <p>查看请求模型、token 统计、扣费和请求状态。</p>
          </div>
        </section>
        <section class="table-wrap">
          <table>
            <thead><tr><th>时间</th><th>模型</th><th>服务</th><th>输入/输出</th><th>扣费</th><th>状态</th><th>错误</th></tr></thead>
            <tbody>{''.join(rows) if rows else _empty_row(7, '暂无调用记录')}</tbody>
          </table>
        </section>
        """,
        variant="app",
    )


def docs_page(settings: Settings, *, portal: bool = False) -> str:
    base = escape(settings.public_api_base)
    register = escape(settings.register_url)
    app = escape(settings.app_base_url)
    console = escape(settings.app_base_url.rstrip("/") + "/console")
    topup = escape(settings.app_base_url.rstrip("/") + "/console/topup")
    models = escape(settings.app_base_url.rstrip("/") + "/pricing")
    primary_href = console if portal else register
    primary_text = "返回控制台" if portal else "注册并获取 API Key"
    secondary_href = topup if portal else app
    secondary_text = "账户充值" if portal else "已登录？进控制台"
    cta_title = "继续使用后台"
    cta_desc = "你可以在控制台创建 API Key、充值美元余额、查看用量和扣费记录。"
    cta_primary_href = models
    cta_primary_text = "打开模型广场"
    cta_secondary_href = console
    cta_secondary_text = "返回控制台"
    if not portal:
        cta_title = "准备好了吗？"
        cta_desc = "注册后先充值再获得可用额度，新用户首笔付款后加赠 $1 美元额度。"
        cta_primary_href = register
        cta_primary_text = "注册并充值"
        cta_secondary_href = app
        cta_secondary_text = "进控制台"
    steps = [
        ("01", "创建账户", "注册后进入控制台，完成首笔充值即可获得可用余额。"),
        ("02", "复制 API Key", "在令牌管理中创建 Key，只在创建时完整显示一次，请妥善保存。"),
        ("03", "填写 Base URL", f"在工具或 SDK 中填写 {settings.public_api_base}/v1。"),
        ("04", "选择模型名", "从模型广场复制模型名，先用轻量模型测试，再切换到主力模型。"),
    ]
    tools = [
        ("/docs/cursor", "CU", "Cursor / Cline", "图形界面接入", "覆盖 Base URL，添加模型名，即可在 AI 编程工具里调用。"),
        ("/docs/claude-code-cli", "CC", "Claude Code CLI", "命令行 Agent 接入", "设置环境变量后启动 claude，适合完整项目开发。"),
        ("#sdk", "SDK", "OpenAI SDK", "Python / Node.js", "只改 base_url 和 api_key，保留原有 Chat Completions 代码。"),
        ("#curl", "HTTP", "curl / HTTP", "任意语言直调", "标准 Bearer Token 鉴权，适合脚本、后端服务和自动化任务。"),
    ]
    faqs = [
        ("余额为什么显示美元？", "平台模型按美元计价，账户余额和扣费统一显示为 USD，方便和模型价格直接对应。"),
        ("微信支付怎么计算？", "微信实际支付人民币，系统会按固定汇率把你选择的美元充值金额折算成人民币发起支付。"),
        ("新用户有免费额度吗？", "为避免无效注册，首笔成功付款后自动加赠 $1 美元额度，每个账户仅赠送一次。"),
        ("调用失败怎么排查？", "先确认 Key、余额、Base URL 和模型名是否正确，再到控制台使用日志查看请求状态。"),
    ]
    step_html = "".join(
        f"""<div class="doc-step-card">
          <span>{escape(num)}</span>
          <strong>{escape(title)}</strong>
          <p>{escape(desc)}</p>
        </div>"""
        for num, title, desc in steps
    )
    tool_html = "".join(
        f"""<a class="doc-tool-card" href="{href}" id="doc-tool-{href.lstrip('/').replace('/', '-').lstrip('#')}">
          <div class="dtc-icon">{icon}</div>
          <div class="dtc-body">
            <strong>{escape(name)}</strong>
            <span class="dtc-tag">{escape(tag)}</span>
            <p>{escape(desc)}</p>
          </div>
          <div class="dtc-arrow">→</div>
        </a>"""
        for href, icon, name, tag, desc in tools
    )
    faq_html = "".join(
        f"""<div class="doc-faq-card">
          <strong>{escape(question)}</strong>
          <p>{escape(answer)}</p>
        </div>"""
        for question, answer in faqs
    )
    return layout(
        "Docs",
        "docs",
        f"""
        <section class="docs-dark-hero">
          <div class="ddh-bg"></div>
          <div class="ddh-content">
            <p class="ddh-eyebrow">接入文档</p>
            <h1>5 分钟接入 996 Tokens API</h1>
            <p class="ddh-sub">一个 API Key 调用 Claude、GPT、Gemini。兼容 OpenAI Chat Completions，适配 Cursor、Cline、Claude Code 和常见 SDK。</p>
            <div class="ddh-endpoint">
              <span class="ddh-label">Base URL</span>
              <code class="ddh-url">{base}/v1</code>
            </div>
            <div class="ddh-meta-row">
              <span>美元余额</span>
              <span>$3 起充</span>
              <span>微信按汇率折算人民币支付</span>
              <span>首笔付款加赠 $1</span>
            </div>
            <div class="ddh-actions">
              <a class="button ddh-btn-primary" href="{primary_href}">{escape(primary_text)}</a>
              <a class="button ddh-btn-ghost" href="{secondary_href}">{escape(secondary_text)}</a>
            </div>
          </div>
        </section>

        <section class="docs-steps-section">
          <div class="dts-head">
            <p class="eyebrow">Start Here</p>
            <h2>四步完成接入</h2>
            <p>先跑通一个最小请求，再根据场景切换模型和工具。</p>
          </div>
          <div class="doc-steps-grid">{step_html}</div>
        </section>

        <section class="docs-tools-section">
          <div class="dts-head">
            <p class="eyebrow">Quick Start</p>
            <h2>选择你的接入方式</h2>
          </div>
          <div class="doc-tools-grid">{tool_html}</div>
        </section>

        <section class="docs-code-section">
          <div class="dcs-head">
            <p class="eyebrow">Code Examples</p>
            <h2>示例代码</h2>
          </div>
          <div class="docs-grid">
            <article id="sdk">
              <div class="article-tag">Python · OpenAI SDK</div>
              <h2>OpenAI SDK</h2>
              <pre>from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="{base}/v1"
)

resp = client.chat.completions.create(
    model="claude-haiku-4-5",
    messages=[{{"role": "user", "content": "你好"}}]
)
print(resp.choices[0].message.content)</pre>
            </article>
            <article id="curl">
              <div class="article-tag">Shell · curl</div>
              <h2>curl</h2>
              <pre>curl {base}/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "claude-sonnet-4-6",
    "messages": [
      {{"role": "user", "content": "写一个 Python 爬虫"}}
    ]
  }}'</pre>
            </article>
            <article>
              <div class="article-tag">Cursor · Cline · OpenAI Compatible</div>
              <h2>Cursor / Cline</h2>
              <pre>API Provider: OpenAI Compatible
Base URL: {base}/v1
API Key:   YOUR_API_KEY
Model:     claude-sonnet-4-6</pre>
            </article>
            <article>
              <div class="article-tag">Claude Code CLI · 环境变量</div>
              <h2>Claude Code</h2>
              <pre>export ANTHROPIC_BASE_URL={base}
export ANTHROPIC_AUTH_TOKEN=YOUR_API_KEY
export ANTHROPIC_MODEL=claude-sonnet-4-6

claude  # 直接启动</pre>
            </article>
          </div>
        </section>

        <section class="docs-faq-section">
          <div class="dcs-head">
            <p class="eyebrow">FAQ</p>
            <h2>常见问题</h2>
          </div>
          <div class="doc-faq-grid">{faq_html}</div>
        </section>

        <section class="docs-cta-strip">
          <div class="docs-cta-inner">
            <div>
              <strong>{escape(cta_title)}</strong>
              <p>{escape(cta_desc)}</p>
            </div>
            <div class="docs-cta-btns">
              <a class="button primary" href="{cta_primary_href}">{escape(cta_primary_text)}</a>
              <a class="button" href="{cta_secondary_href}">{escape(cta_secondary_text)}</a>
            </div>
          </div>
        </section>
        """,
        settings=settings,
        variant="portal" if portal else "public",
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
Model: claude-sonnet-4-6</pre>
          </article>
          <article>
            <h2>Claude Code</h2>
            <pre>export ANTHROPIC_BASE_URL={base}
export ANTHROPIC_AUTH_TOKEN=YOUR_API_KEY
export ANTHROPIC_MODEL=claude-sonnet-4-6</pre>
          </article>
          <article>
            <h2>轻量线</h2>
            <p>适合个人开发者、低频调用、代码解释、脚本生成。</p>
            <code>claude-haiku-4-5</code>
          </article>
          <article>
            <h2>主力线</h2>
            <p>Claude Code / Cursor 默认先用 Sonnet，重任务再切 Opus。</p>
            <code>claude-sonnet-4-6</code>
          </article>
        </section>
        """,
        settings=settings,
        variant="public",
    )


def cursor_guide_page(settings: Settings, *, portal: bool = False) -> str:
    base = escape(settings.public_api_base)
    register = escape(settings.register_url)
    console = escape(settings.app_base_url.rstrip("/") + "/console")
    primary_href = console if portal else register
    primary_text = "回控制台创建 Key" if portal else "获取 API Key"
    steps = [
        ("1", "注册并获取 API Key", "注册账户后进入控制台 → API Keys，创建一个 Key（只在创建时显示一次，请妥善保存）。"),
        ("2", "打开 Cursor 模型设置", "Cursor → Settings → Cursor Settings → Models，找到 “OpenAI API Key” 区域。"),
        ("3", "填入 Key 并覆盖 Base URL", "勾选 OpenAI API Key 填入你的 Key，展开 “Override OpenAI Base URL”，填入下方平台地址。"),
        ("4", "添加平台模型名", "在模型列表点 “Add model”，添加 claude-sonnet-4-6、claude-haiku-4-5 等平台模型名，再点 Verify 验证。"),
    ]
    step_html = "".join(
        f"<div><strong>{escape(num)}</strong><h2>{escape(title)}</h2><p>{escape(desc)}</p></div>"
        for num, title, desc in steps
    )
    models = [
        ("claude-sonnet-4-6", "Claude Sonnet 4.6，复杂重构、长上下文主力"),
        ("claude-haiku-4-5", "Claude Haiku 4.5，轻量快速调用"),
        ("gpt-5.4", "GPT 5.4，通用对话与代码"),
        ("gemini-3.5-flash", "Gemini 3.5 Flash，低延迟轻量任务"),
    ]
    model_rows = "".join(
        f"<tr><td><code>{escape(name)}</code></td><td>{escape(desc)}</td></tr>"
        for name, desc in models
    )
    faqs = [
        ("Tab 补全 / Agent 还能用吗？", "覆盖 Base URL 后，自定义模型主要作用于 Chat。Cursor 的 Tab 补全和部分 Composer 能力仍走 Cursor 官方，不受影响。"),
        ("提示 model not found？", "确认在模型列表里添加的名字是平台支持的模型名（如 claude-sonnet-4-6），不要填 Cursor 默认的 claude-3.5-sonnet 之类。"),
        ("Verify 失败？", "检查 Base URL 是否以 /v1 结尾、Key 是否有效且账户有余额，必要时在控制台用量记录查看错误原因。"),
        ("如何控制预算？", "轻任务用 claude-haiku-4-5 或 gemini-3.5-flash；重任务再切 claude-sonnet-4-6 / claude-opus-4-7。"),
    ]
    faq_html = "".join(
        f"<div><h2>{escape(q)}</h2><p>{escape(a)}</p></div>" for q, a in faqs
    )
    return layout(
        "Cursor 接入",
        "docs",
        f"""
        <section class="page-title">
          <div>
            <p class="eyebrow">Guide · Cursor</p>
            <h1>在 Cursor 接入 996 Tokens API</h1>
            <p>用 OpenAI 兼容方式把 Cursor 的对话模型切到本平台，一个 Key 调用 Claude / GPT / Gemini 首发模型。</p>
          </div>
          <a class="button primary" href="{primary_href}">{escape(primary_text)}</a>
        </section>
        <section class="steps">{step_html}</section>
        <section class="docs-grid">
          <article>
            <h2>推荐配置</h2>
            <pre>API Provider: OpenAI Compatible
Override Base URL: {base}/v1
API Key: YOUR_API_KEY
Model: claude-sonnet-4-6</pre>
          </article>
          <article>
            <h2>验证调用</h2>
            <pre>curl {base}/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{"model":"claude-sonnet-4-6","messages":[{{"role":"user","content":"你好"}}]}}'</pre>
          </article>
        </section>
        <section class="table-wrap">
          <h2>常用模型</h2>
          <table>
            <thead><tr><th>模型名</th><th>说明</th></tr></thead>
            <tbody>{model_rows}</tbody>
          </table>
        </section>
        <section class="center-head compact">
          <p class="eyebrow">FAQ</p>
          <h1>常见问题</h1>
        </section>
        <section class="feature-grid">{faq_html}</section>
        <section class="pricing-note">
          <strong>下一步</strong>
          <p>如果你更习惯命令行，试试 Claude Code CLI 接入，体验完整的 Agent 编码。</p>
          <a class="text-link" href="/docs/claude-code-cli">Claude Code CLI 接入教程 →</a>
        </section>
        """,
        settings=settings,
        variant="portal" if portal else "public",
    )


def claude_code_cli_page(settings: Settings, *, portal: bool = False) -> str:
    base = escape(settings.public_api_base)
    register = escape(settings.register_url)
    app = escape(settings.app_base_url)
    console = escape(settings.app_base_url.rstrip("/") + "/console")
    topup = escape(settings.app_base_url.rstrip("/") + "/console/topup")
    primary_href = console if portal else register
    primary_text = "回控制台创建 Key →" if portal else "注册获取 API Key →"
    secondary_href = topup if portal else app
    secondary_text = "账户充值" if portal else "已有 Key？进控制台"
    settings_json = """{
  "env": {
    "ANTHROPIC_BASE_URL": "%s",
    "ANTHROPIC_AUTH_TOKEN": "YOUR_API_KEY",
    "ANTHROPIC_MODEL": "claude-sonnet-4-6",
    "ANTHROPIC_SMALL_FAST_MODEL": "claude-haiku-4-5"
  }
}""" % settings.public_api_base
    settings_json = escape(settings_json)
    steps = [
        ("1", "安装 Claude Code CLI", "需要 Node.js 18+，终端运行安装命令。", "npm install -g @anthropic-ai/claude-code"),
        ("2", "获取 API Key", "注册后进入控制台 → API Keys，点击新建 Key（只显示一次，请保存好）。", ""),
        ("3", "配置环境变量", "将平台地址和 Key 写入环境变量，或直接持久化到 shell 配置文件。", ""),
        ("4", "启动并验证", "cd 进项目目录，运行 claude，用 /status 确认接入成功。", "claude"),
    ]
    models = [
        ("claude-sonnet-4-6", "ANTHROPIC_MODEL", "主力模型，复杂任务与长上下文", "stable"),
        ("claude-haiku-4-5", "ANTHROPIC_SMALL_FAST_MODEL", "轻量快速模型，用于标题/补全等低频调用", "economy"),
        ("claude-opus-4-7", "手动切换", "高价值重任务、架构分析和复杂 Agent", "premium"),
    ]
    model_rows = "".join(
        f"<tr><td><code>{escape(name)}</code></td><td><span class='line-badge {badge}'>{escape(env)}</span></td><td>{escape(desc)}</td></tr>"
        for name, env, desc, badge in models
    )
    faqs = [
        ("❓", "ANTHROPIC_BASE_URL 要不要带 /v1？", "不要。Claude Code 走 Anthropic 原生协议，Base URL 只填根域名，平台自动适配 /v1/messages 转发。"),
        ("🔑", "AUTH_TOKEN 和 API_KEY 有什么区别？", "用 ANTHROPIC_AUTH_TOKEN 填平台 Key 即可。若客户端只识别 ANTHROPIC_API_KEY，填同一个 Key 也能用。"),
        ("💳", "提示余额不足 / 402 错误？", "前往控制台充值，账户余额为 0 时网关直接拒绝请求并返回 402。"),
        ("💰", "如何控制预算？", "把 ANTHROPIC_SMALL_FAST_MODEL 设为 claude-haiku-4-5，大量轻量调用走快速模型，重任务再使用 Sonnet。"),
    ]
    faq_html = "".join(
        f"""<div class="cli-faq-card">
          <div class="faq-emoji">{escape(emoji)}</div>
          <strong>{escape(q)}</strong>
          <p>{escape(a)}</p>
        </div>"""
        for emoji, q, a in faqs
    )
    step_html = "".join(
        f"""<div class="cli-step">
          <div class="cli-step-num">{escape(num)}</div>
          <div class="cli-step-body">
            <strong>{escape(title)}</strong>
            <p>{escape(desc)}</p>
            {f'<pre class="cli-step-code">{escape(code)}</pre>' if code else ''}
          </div>
        </div>"""
        for num, title, desc, code in steps
    )
    return layout(
        "Claude Code CLI 接入",
        "docs",
        f"""
        <section class="cli-hero">
          <div class="cli-hero-text">
            <p class="eyebrow">Guide · Claude Code CLI</p>
            <h1>在 Claude Code 接入 996 Tokens</h1>
            <p>通过环境变量把官方 Claude Code CLI 指向本平台，美元余额计费，4 步完成完整 Agent 编码接入。</p>
            <div class="cli-hero-actions">
              <a class="button primary" href="{primary_href}">{escape(primary_text)}</a>
              <a class="button" href="{secondary_href}">{escape(secondary_text)}</a>
            </div>
          </div>
          <div class="cli-hero-badge">
            <div class="chb-inner">
              <div class="chb-row"><span>Base URL</span><code>{base}</code></div>
              <div class="chb-row"><span>协议</span><code>Anthropic native</code></div>
              <div class="chb-row"><span>主力模型</span><code>claude-sonnet-4-6</code></div>
              <div class="chb-row"><span>轻量模型</span><code>claude-haiku-4-5</code></div>
            </div>
          </div>
        </section>

        <section class="cli-steps-section">
          <div class="css-head">
            <p class="eyebrow">Steps</p>
            <h2>四步接入</h2>
          </div>
          <div class="cli-steps-grid">{step_html}</div>
        </section>

        <section class="docs-code-section">
          <div class="dcs-head">
            <p class="eyebrow">Configuration</p>
            <h2>三种配置方式</h2>
          </div>
          <div class="docs-grid">
            <article>
              <div class="article-tag">方式一 · 临时环境变量（测试用）</div>
              <h2>export 命令</h2>
              <pre>export ANTHROPIC_BASE_URL={base}
export ANTHROPIC_AUTH_TOKEN=YOUR_API_KEY
export ANTHROPIC_MODEL=claude-sonnet-4-6
export ANTHROPIC_SMALL_FAST_MODEL=claude-haiku-4-5

claude</pre>
            </article>
            <article>
              <div class="article-tag">方式二 · 持久化到 Shell 配置</div>
              <h2>写入 ~/.zshrc / ~/.bashrc</h2>
              <pre>echo 'export ANTHROPIC_BASE_URL={base}' >> ~/.zshrc
echo 'export ANTHROPIC_AUTH_TOKEN=YOUR_API_KEY' >> ~/.zshrc
echo 'export ANTHROPIC_MODEL=claude-sonnet-4-6' >> ~/.zshrc
source ~/.zshrc

claude</pre>
            </article>
            <article>
              <div class="article-tag">方式三 · settings.json（推荐）</div>
              <h2>~/.claude/settings.json</h2>
              <pre>{settings_json}</pre>
            </article>
            <article>
              <div class="article-tag">验证接入</div>
              <h2>确认配置正确</h2>
              <pre># 启动后在 Claude Code 内执行
/status    # 查看当前模型和连接状态
/model     # 确认模型名

# 或用 curl 快速测试
curl {base}/v1/messages \\
  -H "x-api-key: YOUR_API_KEY" \\
  -H "anthropic-version: 2023-06-01" \\
  -H "Content-Type: application/json" \\
  -d '{{"model":"claude-sonnet-4-6","max_tokens":64,"messages":[{{"role":"user","content":"hi"}}]}}'</pre>
            </article>
          </div>
        </section>

        <section class="cli-models-section">
          <div class="dcs-head">
            <p class="eyebrow">Models</p>
            <h2>推荐模型组合</h2>
          </div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>模型名</th><th>环境变量</th><th>用途说明</th></tr></thead>
              <tbody>{model_rows}</tbody>
            </table>
          </div>
        </section>

        <section class="cli-faq-section">
          <div class="dcs-head">
            <p class="eyebrow">FAQ</p>
            <h2>常见问题</h2>
          </div>
          <div class="cli-faq-grid">{faq_html}</div>
        </section>

        <section class="docs-cta-strip">
          <div class="docs-cta-inner">
            <div>
              <strong>更喜欢图形界面？</strong>
              <p>查看 Cursor / Cline 接入教程，3 步完成配置。</p>
            </div>
            <div class="docs-cta-btns">
              <a class="button primary" href="/docs/cursor">Cursor 接入教程 →</a>
              <a class="button" href="{app}">进控制台</a>
            </div>
          </div>
        </section>
        """,
        settings=settings,
        variant="portal" if portal else "public",
    )


def about_page(settings: Settings, *, portal: bool = False) -> str:
    base = escape(settings.public_api_base)
    console = escape(settings.app_base_url.rstrip("/") + "/console")
    topup = escape(settings.app_base_url.rstrip("/") + "/console/topup")
    primary_href = console if portal else escape(settings.register_url)
    primary_text = "返回控制台" if portal else "注册并充值"
    secondary_href = topup if portal else "/docs"
    secondary_text = "账户充值" if portal else "查看接入文档"
    features = [
        ("API", "统一接口", "兼容 OpenAI Chat Completions，常见 SDK 和开发工具都能快速接入。"),
        ("AI", "精选模型", "提供 Claude、GPT、Gemini 系列模型，覆盖编程、推理、写作和轻量任务。"),
        ("USD", "美元余额", "账户余额以 USD 展示，充值、扣费和用量记录清晰可查。"),
        ("SSE", "流式输出", "支持 SSE streaming，Claude Code 和 Cursor 对话体验更顺畅。"),
        ("KEY", "权限清晰", "用户可以在控制台创建 API Key，并按模型和余额控制使用范围。"),
        ("OS", "海外开放", "当前服务只向海外用户开放，如需企业合作请先联系管理员确认。"),
    ]
    model_groups = [
        ("C", "Claude 系列", "claude", "Opus、Sonnet、Haiku，适合 AI 编程、复杂分析和长文本任务。"),
        ("G", "GPT 系列", "gpt", "适合通用对话、代码生成、Agent 和自动化工作流。"),
        ("M", "Gemini 系列", "extra", "适合快速响应、轻量任务和多工具组合调用。"),
    ]
    stats = [
        ("7", "首发核心模型"),
        ("USD", "美元余额"),
        ("$3", "最低充值"),
        ("QQ", "61943181 客服"),
    ]
    billing_cards = [
        ("01", "美元余额", "模型价格、账户余额和扣费记录统一以 USD 展示，便于直接对照模型广场价格。"),
        ("02", "人民币支付", "微信支付会按固定汇率把美元充值金额折算成人民币，支付后入账美元余额。"),
        ("03", "$3 起充", "低门槛试用，先用小额充值验证工具配置和模型效果，再按需加额。"),
        ("04", "首充赠送", "新用户首笔成功付款后自动加赠 $1 美元额度，每个账户仅一次。"),
    ]
    feature_html = "".join(
        f"""<div class="af-card">
          <div class="af-icon">{escape(icon)}</div>
          <h3>{escape(title)}</h3>
          <p>{escape(desc)}</p>
        </div>"""
        for icon, title, desc in features
    )
    model_group_html = "".join(
        f"""<div class="up-card up-{slug}">
          <div class="up-icon">{escape(icon)}</div>
          <strong>{escape(name)}</strong>
          <p>{escape(desc)}</p>
        </div>"""
        for icon, name, slug, desc in model_groups
    )
    stats_html = "".join(
        f"""<div class="about-stat">
          <strong>{escape(val)}</strong>
          <span>{escape(label)}</span>
        </div>"""
        for val, label in stats
    )
    billing_html = "".join(
        f"""<div class="billing-card">
          <span>{escape(num)}</span>
          <strong>{escape(title)}</strong>
          <p>{escape(desc)}</p>
        </div>"""
        for num, title, desc in billing_cards
    )
    return layout(
        "About",
        "about",
        f"""
        <section class="about-dark-hero">
          <div class="adh-bg"></div>
          <div class="adh-content">
            <p class="adh-eyebrow">About 996 Tokens</p>
            <h1>一个账号，接入 Claude、GPT、Gemini</h1>
            <p class="adh-sub">996 Tokens 面向 AI 编程、自动化脚本和 Agent 开发者。你只需要一个 API Key，就能在 Cursor、Claude Code、Cline、OpenAI SDK 和后端服务中统一调用常用模型。</p>
            <div class="adh-actions">
              <a class="button primary adh-btn-primary" href="{primary_href}">{escape(primary_text)}</a>
              <a class="button adh-btn-ghost" href="{secondary_href}">{escape(secondary_text)}</a>
            </div>
            <div class="about-stats-row">{stats_html}</div>
          </div>
        </section>

        <section class="about-section">
          <div class="about-section-head">
            <p class="eyebrow">Features</p>
            <h2>六大核心能力</h2>
            <p>每一项能力都围绕开发者实际接入和日常调用体验。</p>
          </div>
          <div class="af-grid">{feature_html}</div>
        </section>

        <section class="about-arch-section">
          <div class="aas-inner">
            <div class="aas-left">
              <p class="eyebrow">Getting Started</p>
              <h2>从注册到调用</h2>
              <p>注册账户、充值美元余额、创建 API Key，然后在你的开发工具里替换 Base URL 即可开始调用。</p>
              <div class="arch-diagram">
                <div class="arch-node arch-user">用户请求</div>
                <div class="arch-arrow">↓</div>
                <div class="arch-node arch-nginx">996 Tokens</div>
                <div class="arch-arrow">↓</div>
                <div class="arch-branches">
                  <div class="arch-branch">
                    <div class="arch-node arch-www">官网<small>价格 / 文档 / 教程</small></div>
                  </div>
                  <div class="arch-branch">
                    <div class="arch-node arch-api">API<small>OpenAI 兼容入口</small></div>
                  </div>
                  <div class="arch-branch">
                    <div class="arch-node arch-app">控制台<small>充值 / Key / 用量</small></div>
                  </div>
                </div>
                <div class="arch-arrow">↓</div>
                <div class="arch-node arch-pool">模型服务<small>Claude / GPT / Gemini</small></div>
                <div class="arch-arrow">↓</div>
                <div class="arch-node arch-models">Claude · GPT · Gemini</div>
              </div>
            </div>
            <div class="aas-right">
              <p class="eyebrow">Models</p>
              <h2>支持模型</h2>
              <p>第一版先提供最常用的 Claude、GPT、Gemini 模型，保持模型列表精简、清晰、可直接使用。</p>
              <div class="up-grid">{model_group_html}</div>
            </div>
          </div>
        </section>

        <section class="about-billing-section">
          <div class="about-section-head">
            <p class="eyebrow">Billing</p>
            <h2>计费与充值</h2>
            <p>余额按美元展示，支付按人民币完成，用户看到的扣费和模型价格保持一致。</p>
          </div>
          <div class="billing-grid">{billing_html}</div>
        </section>

        <section class="about-contact-section">
          <div class="acs-head">
            <p class="eyebrow">Contact</p>
            <h2>联系我们</h2>
            <p>有问题或想合作，欢迎通过以下方式联系：</p>
          </div>
          <div class="acs-grid">
            <div class="acs-card">
              <div class="acs-icon">QQ</div>
              <strong>QQ 客服</strong>
              <p><span class="acs-code">61943181</span></p>
              <p style="margin-top:6px;color:var(--muted);font-size:13px;">充值、Key、扣费或接入问题都可以联系处理。</p>
            </div>
            <div class="acs-card">
              <div class="acs-icon">DOC</div>
              <strong>接入文档</strong>
              <p><a class="acs-link" href="/docs">www.996tokens.com/docs</a></p>
              <p style="margin-top:6px;color:var(--muted);font-size:13px;">Cursor、Claude Code、OpenAI SDK 接入教程。</p>
            </div>
            <div class="acs-card">
              <div class="acs-icon">API</div>
              <strong>API Base URL</strong>
              <p><code class="acs-code">{base}/v1</code></p>
              <p style="margin-top:6px;color:var(--muted);font-size:13px;">兼容 OpenAI Chat Completions，换一行即接入。</p>
            </div>
            <div class="acs-card">
              <div class="acs-icon">OS</div>
              <strong>服务声明</strong>
              <p>996 Tokens 当前只向海外用户开放；如需企业合作、兑换码或异常订单处理，请先联系管理员确认。</p>
            </div>
          </div>
        </section>
        """,
        settings=settings,
        variant="portal" if portal else "public",
    )


def support_page(settings: Settings, *, portal: bool = False) -> str:
    qq = "61943181"
    console = escape(settings.app_base_url.rstrip("/") + "/console")
    topup = escape(settings.app_base_url.rstrip("/") + "/console/topup")
    primary_href = console if portal else escape(settings.register_url)
    primary_text = "返回控制台 →" if portal else "登录/注册控制台 →"
    common_cases = [
        ("充值问题", "支付后余额未到账、订单异常、兑换码无法使用。"),
        ("接入问题", "Cursor、Claude Code、Cline、SDK 配置失败。"),
        ("账户问题", "API Key 创建、余额显示、调用记录查询。"),
        ("企业合作", "团队额度、批量接入、长期使用咨询。"),
    ]
    case_cards = "".join(
        f"""<div>
          <h2>{escape(title)}</h2>
          <p>{escape(desc)}</p>
        </div>"""
        for title, desc in common_cases
    )
    return layout(
        "客服",
        "support",
        f"""
        <section class="page-title">
          <div>
            <p class="eyebrow">Support</p>
            <h1>联系客服</h1>
            <p>使用过程中遇到充值、API Key、扣费或接入配置问题，请打开 QQ 搜索客服号并添加好友。</p>
          </div>
          <a class="button primary" href="{primary_href}">{escape(primary_text)}</a>
        </section>
        <section class="support-card">
          <div class="support-main">
            <span class="support-label">QQ 客服</span>
            <strong>{qq}</strong>
            <p>请复制 QQ 号，在 QQ 里搜索并添加好友。联系时建议附上注册邮箱、订单金额、问题截图和出现问题的页面地址，方便快速定位。</p>
            <div class="support-actions">
              <a class="button" href="{topup}">充值页面</a>
              <a class="button" href="/docs">接入文档</a>
            </div>
          </div>
          <div class="support-side">
            <span>服务范围</span>
            <b>充值 / API Key / 用量 / 接入</b>
            <small>当前服务只向海外用户开放。</small>
          </div>
        </section>
        <section class="center-head compact">
          <p class="eyebrow">Help Topics</p>
          <h1>常见咨询类型</h1>
        </section>
        <section class="feature-grid">{case_cards}</section>
        <section class="pricing-note">
          <strong>联系客服前建议准备</strong>
          <p>注册邮箱、订单号或支付金额、API Key 前 8 位、报错截图。不要把完整 API Key 发给任何人。</p>
        </section>
        """,
        settings=settings,
        variant="portal" if portal else "public",
    )


def status_page(providers: Iterable[dict[str, Any]]) -> str:
    items = [
        ("API 接口", "online", "可用", "OpenAI 兼容接口正常服务"),
        ("用户控制台", "online", "可用", "登录、充值、Key 管理和用量查询正常"),
        ("接入文档", "online", "可用", "Cursor、Claude Code、SDK 示例可访问"),
        ("支付服务", "online", "可用", "微信支付和人工处理通道正常"),
    ]
    rows = [
        "<tr>"
        f"<td><strong>{escape(name)}</strong><small>{escape(desc)}</small></td>"
        f"<td><span class='status active'>{escape(status)}</span></td>"
        f"<td>{escape(note)}</td>"
        "</tr>"
        for name, _, status, desc in items
        for note in ["正常运行"]
    ]
    return layout(
        "Status",
        "status",
        f"""
        <section class="center-head compact">
          <p class="eyebrow">Status</p>
          <h1>平台状态</h1>
          <p>这里展示用户会直接使用到的服务状态。如遇到充值、Key 或调用异常，请联系管理员处理。</p>
        </section>
        <section class="table-wrap">
          <table>
            <thead><tr><th>服务</th><th>状态</th><th>说明</th></tr></thead>
            <tbody>{''.join(rows) if rows else _empty_row(3, '暂无状态')}</tbody>
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
        subtitle="创建账户后进入控制台，充值余额、创建 API Key 并查看用量。",
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
            <small>注册和登录将在控制台完成，本站保留品牌入口和接入说明。</small>
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
        "部署方案",
        "deploy",
        f"""
        <section class="page-title">
          <div>
            <p class="eyebrow">Launch Plan</p>
            <h1>部署方案</h1>
            <p>生产版分为官网、用户控制台和 API 调用入口。第一版面向开发者提供 7 个 Claude / GPT / Gemini 模型。</p>
          </div>
          <a class="button primary" href="{newapi}">打开控制台</a>
        </section>
        <section class="feature-grid">
          <div><h2>官网入口</h2><p>展示首页、价格、文档、状态和关于页面。</p></div>
          <div><h2>用户控制台</h2><p>承接登录、注册、充值、API Key、用量记录和模型列表。</p></div>
          <div><h2>API 域名</h2><p>提供 OpenAI 兼容调用入口，方便 SDK 和开发工具接入。</p></div>
          <div><h2>服务支持</h2><p>保留人工处理入口，用于充值异常和接入问题。</p></div>
        </section>
        <section class="table-wrap">
          <h2>域名分工</h2>
          <table>
            <thead><tr><th>域名</th><th>用途</th><th>用户看到什么</th><th>说明</th></tr></thead>
            <tbody>{upstream_rows}</tbody>
          </table>
        </section>
        <section class="table-wrap">
          <h2>首发模型</h2>
          <table>
            <thead><tr><th>系列</th><th>模型</th><th>适合场景</th><th>说明</th></tr></thead>
            <tbody>{route_rows}</tbody>
          </table>
        </section>
        <section class="quickstart">
          <div>
            <h2>配置顺序</h2>
            <p>先确认域名和证书，再完成用户控制台、支付、模型列表和文档入口配置。</p>
          </div>
          <pre>1. 部署用户控制台
2. 配置 www / app / api 三个域名
3. 开启 HTTPS
4. 配置登录、注册、充值和 API Key
5. 只展示 7 个首发模型
6. 用 Cherry Studio、Claude Code、Cursor 做接入测试</pre>
        </section>
        <section class="quickstart">
          <div>
            <h2>Docker Compose</h2>
            <p>已生成 <code>ops/newapi-compose.yml</code>，服务器到位后可以直接部署。</p>
          </div>
          <pre>docker compose -f ops/newapi-compose.yml up -d</pre>
        </section>
        <section class="risk-note">
          <strong>提醒</strong>
          <p>公开页面只展示用户需要知道的信息：模型、价格、文档、充值和服务状态。内部配置不出现在官网页面。</p>
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
            <p>服务状态、模型价格、流水和内部报表。</p>
          </div>
        </section>
        <section class="metrics">
          <div><strong>{overview['users']}</strong><span>用户</span></div>
          <div><strong>{overview['active_keys']}</strong><span>可用 Key</span></div>
          <div><strong>{overview['active_providers']}</strong><span>活跃服务</span></div>
          <div><strong>{overview['today_requests']}</strong><span>今日请求</span></div>
          <div><strong>{_money(overview['today_charge'], settings, decimals=4)}</strong><span>今日流水</span></div>
          <div><strong>{_money(overview['today_margin'], settings, decimals=4)}</strong><span>今日差额</span></div>
        </section>
        <section class="table-wrap">
          <h2>服务监控</h2>
          <table>
            <thead><tr><th>服务</th><th>状态</th><th>类型</th><th>余额</th><th>连续失败</th><th>错误率</th><th>最后错误</th></tr></thead>
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
            <table><thead><tr><th>时间</th><th>用户</th><th>模型</th><th>服务</th><th>状态</th><th>扣费</th><th>差额</th><th>错误</th></tr></thead><tbody>{''.join(log_rows) if log_rows else _empty_row(8, '暂无日志')}</tbody></table>
          </div>
        </section>
        """,
        settings=settings,
        variant="admin",
    )


def _pricing_plan_cards(settings: Settings) -> str:
    plans = []
    for amount in TOPUP_USD_AMOUNTS:
        plans.append(
            {
                "name": f"{_money(amount, settings, decimals=0)} 额度",
                "price": amount,
                "payment": f"实付 {_payment_money(amount, settings)}",
                "badge": "推荐" if amount == 5 else "",
                "class": "featured" if amount == 5 else "top-tier" if amount == 30 else "",
                "tagline": "充值后按实际调用扣费",
                "rights": [
                    f"到账 {_money(amount, settings, decimals=2)} 美元额度",
                    "新用户首笔付款后加赠 $1",
                    "微信支付按固定汇率折算",
                ],
                "support": ["全天可用", "用量记录可查", "异常订单人工处理"],
                "rates": [("Claude", "按量"), ("GPT", "按量"), ("Gemini", "按量")],
                "cta": "立即充值",
            }
        )
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
                <span>额度</span>
              </div>
              <div class="plan-year">{escape(plan['payment'])}</div>
              <div class="plan-section">
                <h3>充值说明</h3>
                <ul>{rights}</ul>
              </div>
              <div class="plan-section">
                <h3>服务支持</h3>
                <ul>{support}</ul>
              </div>
              <div class="plan-section">
                <h3>模型使用</h3>
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
            "注册账户",
            "先了解",
            "注册后可查看文档、价格和控制台入口，充值后再发放加赠额度。",
        ),
        (
            "充值转化",
            "首笔送 $1",
            "额度充值绑定真实支付订单，微信支付按固定汇率折算。",
        ),
        (
            "复购激励",
            "$1 起充",
            "1 / 3 / 5 / 10 / 20 / 30 美元档位，低门槛跑通接入。",
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
        ("注册账户", "$0", "无免费额度", "可查看文档和控制台，首笔付款后发放加赠"),
        ("试用充值", "$1", f"$1 额度 / 实付 {_payment_money(1, settings)}", "验证支付和 API Key，适合首单"),
        ("入门充值", "$3", f"$3 额度 / 实付 {_payment_money(3, settings)}", "轻量 Cursor / Claude Code 使用"),
        ("开发者充值", "$5", f"$5 额度 / 实付 {_payment_money(5, settings)}", "主推档位，适合日常 AI 编程"),
        ("专业充值", "$10", f"$10 额度 / 实付 {_payment_money(10, settings)}", "适合高频调用和长上下文调试"),
        ("工作室充值", "$20", f"$20 额度 / 实付 {_payment_money(20, settings)}", "适合多工具和多 Key 使用"),
        ("团队充值", "$30", f"$30 额度 / 实付 {_payment_money(30, settings)}", "适合工作室共享额度池和优先支持"),
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
        f"<div class='rate-foot'>按量充值最低 {_money(settings.min_recharge_amount, settings, decimals=2)}；当前固定汇率 1 USD = {_payment_money(1, settings)}，新用户首笔付款后加赠 {_money(FIRST_RECHARGE_BONUS_USD, settings, decimals=2)}。</div>"
    )
    return "".join(rendered)


def _referral_rules(settings: Settings) -> str:
    rows = [
        ("新用户", "注册 $0", "注册本身不发放免费额度，防止无效注册消耗。"),
        ("首笔充值", "+$1", "用户完成首笔充值后发放，每个账户仅限一次。"),
        ("后续充值", "按实到账", "后续订单不重复发放首充奖励。"),
        ("邀请奖励", "绑定首充", "邀请奖励以后续活动页和控制台展示为准。"),
        ("异常订单", "人工处理", "充值未到账或订单异常时可联系管理员处理。"),
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
        (spec.model, spec.line_type, spec.description)
        for spec in FIRST_WAVE_MODEL_SPECS
    ]
    rendered = [
        "<div class='rate-row head'><span>模型</span><span>类型</span><span>说明</span></div>"
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
        f"<div class='rate-foot'>最低充值 {_money(settings.min_recharge_amount, settings, decimals=2)}，余额按 {escape(settings.billing_currency)} 扣费，微信支付按 1 USD = {_payment_money(1, settings)} 折算。</div>"
    )
    return "".join(rendered)


def _launch_model_rows() -> list[dict[str, Any]]:
    return [
        {
            "internal_model": spec.model,
            "display_name": spec.display_name,
            "line_type": spec.line_type,
            "input_price": spec.input_price,
            "output_price": spec.output_price,
            "description": spec.description,
        }
        for spec in FIRST_WAVE_MODEL_SPECS
    ]


def _capacity_cards() -> str:
    items = [
        ("统一账户", "余额、API Key、用量记录和充值入口集中在控制台里。"),
        ("稳定体验", "面向持续开发和自动化调用优化，减少频繁切换工具的麻烦。"),
        ("清晰额度", "充值后余额实时展示，调用扣费可在后台查看。"),
        ("人工支持", "充值异常、接入问题和工具配置问题都可以联系处理。"),
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
        return "Claude 系列"
    if "gpt" in model_name:
        return "GPT 系列"
    if "gemini" in model_name:
        return "Gemini 系列"
    return "通用模型"


def _provider_mix_cards() -> str:
    items = [
        ("Claude Code 友好", "AI 编程", "提供 Claude 系列模型和命令行工具接入教程，适合代码生成、重构和项目分析。"),
        ("OpenAI 兼容", "标准接口", "兼容常见 OpenAI SDK、Cursor、Cline、Cherry Studio 等工具。"),
        ("美元余额", "清晰扣费", "余额、充值和用量记录集中展示，人民币只用于支付结算。"),
        ("快速上手", "文档示例", "提供 curl、Python SDK、Cursor 和 Claude Code 配置示例。"),
    ]
    return "".join(f"<div><h2>{escape(name)}</h2><strong>{escape(tag)}</strong><p>{escape(desc)}</p></div>" for name, tag, desc in items)


def _model_category_cards() -> str:
    items = [
        ("Claude", "claude-opus-4-7、claude-sonnet-4-6、claude-haiku-4-5。"),
        ("GPT", "gpt-5.5、gpt-5.4、gpt-5.4-mini。"),
        ("Gemini", "gemini-3.5-flash，负责低延迟轻量请求。"),
        ("首发范围", "第一版只展示以上 7 个核心模型，后续按用户需求逐步扩展。"),
    ]
    return "".join(f"<div><h2>{escape(name)}</h2><p>{escape(desc)}</p></div>" for name, desc in items)


def _upstream_strategy_rows() -> str:
    rows = [
        ("www.996tokens.com", "公开官网", "首页 / 价格 / 文档 / 状态 / 关于", "给访客了解产品和接入方式"),
        ("app.996tokens.com", "用户控制台", "登录 / 注册 / 充值 / API Key / 用量", "给注册用户日常使用"),
        ("api.996tokens.com", "API 入口", "OpenAI 兼容接口", "给 SDK 和开发工具调用"),
    ]
    return "".join(
        "<tr>"
        f"<td><strong>{escape(domain)}</strong></td>"
        f"<td>{escape(purpose)}</td>"
        f"<td>{escape(surface)}</td>"
        f"<td>{escape(note)}</td>"
        "</tr>"
        for domain, purpose, surface, note in rows
    )


def _newapi_route_rows() -> str:
    rows = [
        ("Claude", "claude-opus-4-7 / claude-sonnet-4-6 / claude-haiku-4-5", "AI 编程、复杂分析、长文本", "Claude Code 和 Cursor 常用"),
        ("GPT", "gpt-5.5 / gpt-5.4 / gpt-5.4-mini", "通用对话、代码、Agent", "适合日常开发与自动化任务"),
        ("Gemini", "gemini-3.5-flash", "快速响应、轻量任务", "适合低延迟使用场景"),
    ]
    return "".join(
        "<tr>"
        f"<td><strong>{escape(series)}</strong></td>"
        f"<td>{escape(models)}</td>"
        f"<td>{escape(use)}</td>"
        f"<td>{escape(note)}</td>"
        "</tr>"
        for series, models, use, note in rows
    )


def _line_badge(line_type: str) -> str:
    return f"<span class='line-badge {escape(line_type)}'>{escape(line_type)}</span>"


def _money(amount: float | int | str, settings: Settings, *, decimals: int = 2) -> str:
    symbol = escape(settings.billing_symbol)
    return f"{symbol}{float(amount):.{decimals}f}"


def _payment_money(usd_amount: float | int | str, settings: Settings, *, decimals: int = 2) -> str:
    symbol = escape(settings.payment_symbol)
    amount = float(usd_amount) * float(settings.usd_cny_exchange_rate)
    return f"{symbol}{amount:.{decimals}f}"


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
            ("support", "/support", "客服"),
        ]
        actions = f"<a class='button ghost' href='/'>返回官网</a>"
    elif variant == "portal":
        app_root = cfg.app_base_url.rstrip("/")
        nav = [
            ("console", f"{app_root}/console", "控制台"),
            ("pricing", f"{app_root}/pricing", "模型广场"),
            ("docs", "/docs", "文档"),
            ("claude", "/docs/claude-code-cli", "Claude Code"),
            ("support", "/support", "客服"),
            ("about", "/about", "关于"),
        ]
        actions = f"<a class='button primary' href='{escape(app_root)}/console'>返回控制台</a>"
    elif variant == "admin":
        nav = [
            ("admin", "/admin", "运营面板"),
            ("deploy", "/newapi", "部署方案"),
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
            ("support", "/support", "客服"),
            ("about", "/about", "关于"),
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
  <title>{escape(title)} · {escape(cfg.site_name)}</title>
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
    .support-card {{ margin: 18px 0 32px; display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(280px, .55fr); gap: 18px; align-items: stretch; border: 1px solid var(--line); border-radius: 18px; padding: 28px; background: linear-gradient(135deg, #ffffff, #f8fbff); box-shadow: 0 22px 70px rgba(37,99,235,.12); }}
    .support-main strong {{ display: block; margin: 8px 0 12px; color: var(--blue-dark); font-size: 46px; line-height: 1.05; letter-spacing: 0; }}
    .support-main p {{ max-width: 720px; color: var(--muted); line-height: 1.7; }}
    .support-label {{ display: inline-flex; padding: 5px 10px; border-radius: 999px; background: #dbeafe; color: var(--blue-dark); font-size: 13px; font-weight: 900; }}
    .support-actions {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 18px; }}
    .support-side {{ border: 1px solid #bfdbfe; border-radius: 14px; padding: 22px; background: #eff6ff; display: grid; align-content: center; gap: 10px; }}
    .support-side span {{ color: var(--blue-dark); font-weight: 900; }}
    .support-side b {{ font-size: 20px; line-height: 1.35; }}
    .support-side small {{ color: var(--muted); line-height: 1.6; }}
    .model-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 26px; }}
    .model-card {{ min-height: 255px; border: 1px solid var(--line); border-radius: 12px; background: #fff; padding: 28px; box-shadow: var(--shadow); display: flex; flex-direction: column; }}
    .model-card.featured {{ border-color: #86efac; }}
    .card-top {{ display: flex; justify-content: space-between; gap: 14px; align-items: start; }}
    .card-top h2 {{ font-size: 21px; line-height: 1.35; overflow-wrap: anywhere; }}
    .tag, .line-badge {{ display: inline-flex; align-items: center; min-height: 24px; padding: 3px 9px; border-radius: 6px; background: #dbeafe; color: var(--blue); font-size: 12px; font-weight: 800; }}
    .line-badge.auto {{ background: #e0f2fe; color: #0369a1; }}
    .line-badge.economy {{ background: #dcfce7; color: #15803d; }}
    .line-badge.stable {{ background: #fef3c7; color: #92400e; }}
    .line-badge.premium {{ background: #f3e8ff; color: #7e22ce; }}
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
    .status.active, .status.success, .status.success_stream, .status.success_stream_estimated, .status.paid {{ color: var(--green); }}
    .status.disabled, .status.failed, .status.failed_stream {{ color: var(--red); }}
    .empty {{ text-align: center; color: var(--muted); padding: 32px; }}
    .two {{ display: grid; grid-template-columns: .8fr 1.2fr; gap: 16px; align-items: start; }}
    .risk-note {{ margin-top: 24px; border: 1px solid #fed7aa; background: #fff7ed; color: #7c2d12; border-radius: 12px; padding: 18px 20px; }}
    .risk-note p {{ margin: 8px 0 0; line-height: 1.6; }}
    /* ── Docs page redesign ── */
    .docs-dark-hero, .cli-hero {{ position: relative; margin: -26px -18px 0; overflow: hidden; border-radius: 0 0 24px 24px; background: #07101f; color: #f8fafc; padding: 76px 18px 62px; }}
    .ddh-bg {{ position: absolute; inset: 0; background: radial-gradient(ellipse 72% 58% at 18% 28%, rgba(37,99,235,.32), transparent 62%), radial-gradient(ellipse 58% 50% at 84% 72%, rgba(20,184,166,.18), transparent 58%); pointer-events: none; }}
    .ddh-bg::after, .cli-hero::after {{ content: ""; position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,.045) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.045) 1px, transparent 1px); background-size: 42px 42px; opacity: .72; pointer-events: none; }}
    .ddh-content {{ position: relative; z-index: 1; max-width: 980px; margin: 0 auto; text-align: center; }}
    .ddh-eyebrow, .article-tag {{ display: inline-flex; align-items: center; width: fit-content; min-height: 28px; border-radius: 999px; padding: 5px 11px; font-size: 12px; font-weight: 900; color: #93c5fd; background: rgba(37,99,235,.16); border: 1px solid rgba(147,197,253,.32); }}
    .docs-dark-hero h1, .cli-hero h1 {{ margin: 0; color: #fff; font-size: 54px; line-height: 1.08; font-weight: 900; }}
    .ddh-sub, .cli-hero p {{ max-width: 820px; margin: 18px auto 0; color: #b8c4d5; font-size: 17px; line-height: 1.75; }}
    .ddh-endpoint {{ width: min(760px, 100%); margin: 26px auto 0; display: grid; grid-template-columns: 130px 1fr; align-items: center; gap: 10px; border: 1px solid rgba(255,255,255,.12); border-radius: 14px; padding: 10px; background: rgba(255,255,255,.08); box-shadow: 0 24px 70px rgba(0,0,0,.2); backdrop-filter: blur(12px); text-align: left; }}
    .ddh-label {{ color: #cbd5e1; font-weight: 900; text-align: center; }}
    .ddh-url {{ display: block; background: rgba(255,255,255,.12); color: #fff; padding: 12px 14px; border-radius: 10px; overflow-wrap: anywhere; }}
    .ddh-meta-row {{ width: min(820px, 100%); margin: 16px auto 0; display: flex; justify-content: center; flex-wrap: wrap; gap: 8px; }}
    .ddh-meta-row span {{ display: inline-flex; align-items: center; min-height: 30px; border: 1px solid rgba(255,255,255,.14); border-radius: 999px; padding: 0 12px; color: #dbeafe; background: rgba(255,255,255,.07); font-size: 13px; font-weight: 800; }}
    .ddh-actions, .cli-hero-actions, .docs-cta-btns {{ display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-top: 24px; }}
    .ddh-btn-primary {{ background: #2563eb; border-color: #2563eb; color: #fff; box-shadow: 0 14px 34px rgba(37,99,235,.36); }}
    .ddh-btn-ghost {{ background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.18); color: #e2e8f0; }}
    .docs-steps-section, .docs-tools-section, .docs-code-section, .docs-faq-section, .cli-steps-section, .cli-models-section, .cli-faq-section {{ max-width: 1180px; margin: 0 auto; padding: 54px 0 0; }}
    .dts-head, .dcs-head, .css-head {{ margin-bottom: 20px; }}
    .dts-head h2, .dcs-head h2, .css-head h2 {{ font-size: 30px; margin-bottom: 8px; }}
    .dts-head p:not(.eyebrow), .dcs-head p:not(.eyebrow) {{ color: var(--muted); line-height: 1.7; }}
    .doc-steps-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }}
    .doc-step-card, .doc-faq-card {{ border: 1px solid var(--line); border-radius: 16px; background: #fff; padding: 22px; box-shadow: var(--shadow); }}
    .doc-step-card span {{ display: grid; place-items: center; width: 36px; height: 36px; margin-bottom: 16px; border-radius: 50%; background: var(--blue); color: #fff; font-weight: 900; font-size: 13px; }}
    .doc-step-card strong, .doc-faq-card strong {{ display: block; color: var(--ink); font-size: 17px; margin-bottom: 9px; }}
    .doc-step-card p, .doc-faq-card p {{ margin: 0; color: var(--muted); line-height: 1.65; }}
    .doc-tools-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }}
    .doc-tool-card {{ min-height: 210px; display: flex; flex-direction: column; gap: 14px; position: relative; border: 1px solid var(--line); border-radius: 16px; background: #fff; padding: 22px; color: var(--ink); text-decoration: none; box-shadow: var(--shadow); transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease; }}
    .doc-tool-card:hover {{ transform: translateY(-4px); border-color: #bfdbfe; box-shadow: 0 18px 48px rgba(37,99,235,.14); }}
    .dtc-icon {{ width: 46px; height: 46px; display: grid; place-items: center; border-radius: 12px; background: #edf2ff; color: var(--blue-dark); font-size: 13px; font-weight: 900; letter-spacing: 0; }}
    .dtc-body strong {{ display: block; font-size: 19px; margin-bottom: 8px; }}
    .dtc-tag {{ display: inline-flex; width: fit-content; border-radius: 999px; background: #e0f2fe; color: #0369a1; padding: 4px 9px; font-size: 12px; font-weight: 900; }}
    .dtc-body p {{ margin: 12px 0 0; color: var(--muted); line-height: 1.6; }}
    .dtc-arrow {{ margin-top: auto; width: 32px; height: 32px; display: grid; place-items: center; border-radius: 50%; background: #f1f5f9; color: var(--blue); font-weight: 900; }}
    .docs-code-section article {{ min-height: 340px; display: flex; flex-direction: column; gap: 14px; }}
    .docs-code-section article pre {{ flex: 1; min-height: 230px; }}
    .doc-faq-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }}
    .docs-cta-strip {{ max-width: 1180px; margin: 54px auto 0; border-radius: 18px; background: linear-gradient(135deg, #0f172a, #1e3a8a); color: #fff; padding: 26px; box-shadow: 0 28px 70px rgba(15,23,42,.18); }}
    .docs-cta-inner {{ display: flex; align-items: center; justify-content: space-between; gap: 18px; }}
    .docs-cta-inner strong {{ display: block; font-size: 22px; margin-bottom: 6px; }}
    .docs-cta-inner p {{ margin: 0; color: #cbd5e1; }}
    .docs-cta-inner .button:not(.primary) {{ background: rgba(255,255,255,.1); border-color: rgba(255,255,255,.18); color: #fff; }}
    .cli-hero {{ display: grid; grid-template-columns: minmax(0, .95fr) minmax(360px, .75fr); gap: 28px; align-items: center; }}
    .cli-hero > * {{ position: relative; z-index: 1; }}
    .cli-hero-text {{ max-width: 720px; margin-left: auto; }}
    .cli-hero-badge {{ max-width: 520px; margin-right: auto; }}
    .chb-inner {{ border: 1px solid rgba(255,255,255,.14); border-radius: 18px; background: rgba(255,255,255,.08); padding: 18px; box-shadow: 0 24px 70px rgba(0,0,0,.2); backdrop-filter: blur(12px); }}
    .chb-row {{ display: grid; grid-template-columns: 120px 1fr; gap: 12px; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,.12); }}
    .chb-row:last-child {{ border-bottom: 0; }}
    .chb-row span {{ color: #cbd5e1; font-weight: 800; }}
    .chb-row code {{ background: rgba(255,255,255,.12); color: #fff; overflow-wrap: anywhere; }}
    .cli-steps-grid, .cli-faq-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }}
    .cli-step, .cli-faq-card {{ border: 1px solid var(--line); border-radius: 16px; padding: 20px; background: #fff; box-shadow: var(--shadow); }}
    .cli-step-num {{ width: 34px; height: 34px; display: grid; place-items: center; border-radius: 50%; background: var(--blue); color: #fff; font-weight: 900; margin-bottom: 14px; }}
    .cli-step-body strong, .cli-faq-card strong {{ display: block; font-size: 17px; margin-bottom: 8px; }}
    .cli-step-body p, .cli-faq-card p {{ color: var(--muted); line-height: 1.6; margin: 0; }}
    .cli-step-code {{ margin-top: 14px; min-height: 0; padding: 12px; font-size: 12px; }}
    .faq-emoji {{ font-size: 26px; margin-bottom: 12px; }}
    /* ── About page redesign ── */
    .about-dark-hero {{ position: relative; margin: -26px -18px 0; overflow: hidden; background: #07101f; color: #f0f6ff; padding: 80px 18px 64px; }}
    .adh-bg {{ position: absolute; inset: 0; background: radial-gradient(ellipse 70% 60% at 20% 30%, rgba(37,99,235,.28) 0%, transparent 60%), radial-gradient(ellipse 50% 50% at 80% 70%, rgba(16,163,74,.16) 0%, transparent 55%); pointer-events: none; }}
    .adh-bg::after {{ content: ''; position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.04) 1px, transparent 1px); background-size: 44px 44px; }}
    .adh-content {{ position: relative; z-index: 1; max-width: 900px; margin: 0 auto; text-align: center; }}
    .adh-eyebrow {{ display: inline-block; margin: 0 0 16px; padding: 4px 14px; border: 1px solid rgba(147,197,253,.4); border-radius: 999px; background: rgba(37,99,235,.18); color: #93c5fd; font-size: 12px; font-weight: 800; letter-spacing: .05em; text-transform: uppercase; }}
    .about-dark-hero h1 {{ font-size: 54px; line-height: 1.12; font-weight: 900; color: #fff; margin: 0 0 22px; }}
    .adh-sub {{ color: #94a3b8; font-size: 17px; line-height: 1.8; margin: 0 auto 32px; max-width: 780px; }}
    .adh-actions {{ display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }}
    .adh-btn-primary {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); border: none; color: #fff; padding: 12px 26px; border-radius: 10px; font-size: 15px; box-shadow: 0 8px 24px rgba(37,99,235,.4); transition: transform .15s, box-shadow .15s; }}
    .adh-btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 12px 32px rgba(37,99,235,.5); }}
    .adh-btn-ghost {{ background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.2); color: #e2e8f0; padding: 12px 26px; border-radius: 10px; font-size: 15px; transition: background .15s; }}
    .adh-btn-ghost:hover {{ background: rgba(255,255,255,.14); }}
    .about-stats-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 52px; max-width: 760px; margin-left: auto; margin-right: auto; }}
    .about-stat {{ border: 1px solid rgba(255,255,255,.1); border-radius: 14px; background: rgba(255,255,255,.06); backdrop-filter: blur(10px); padding: 18px 12px; }}
    .about-stat strong {{ display: block; font-size: 28px; font-weight: 900; color: #fff; line-height: 1.1; }}
    .about-stat span {{ display: block; margin-top: 4px; color: #94a3b8; font-size: 13px; }}
    /* Features section */
    .about-section, .about-billing-section {{ max-width: 1240px; margin: 0 auto; padding: 64px 18px 32px; }}
    .about-section-head {{ text-align: center; margin-bottom: 40px; }}
    .about-section-head h2 {{ font-size: 32px; margin-bottom: 10px; }}
    .about-section-head p {{ color: var(--muted); font-size: 16px; max-width: 560px; margin: 0 auto; }}
    .af-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
    .af-card {{ border: 1px solid var(--line); border-radius: 16px; background: #fff; padding: 28px; box-shadow: 0 4px 20px rgba(15,23,42,.06); transition: transform .2s, box-shadow .2s; }}
    .af-card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 40px rgba(15,23,42,.12); }}
    .af-icon {{ width: 48px; height: 48px; display: grid; place-items: center; border-radius: 14px; background: #eef2ff; color: var(--blue-dark); font-size: 13px; font-weight: 900; margin-bottom: 16px; letter-spacing: 0; }}
    .af-card h3 {{ font-size: 17px; font-weight: 800; margin: 0 0 10px; color: var(--ink); }}
    .af-card p {{ color: var(--muted); line-height: 1.65; margin: 0; font-size: 14px; }}
    /* Architecture section */
    .about-arch-section {{ background: var(--wash); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); padding: 64px 18px; }}
    .aas-inner {{ max-width: 1240px; margin: 0 auto; display: grid; grid-template-columns: 1.1fr .9fr; gap: 48px; align-items: start; }}
    .aas-left h2, .aas-right h2 {{ font-size: 26px; margin: 6px 0 12px; }}
    .aas-left > p, .aas-right > p {{ color: var(--muted); line-height: 1.7; margin-bottom: 24px; }}
    .arch-diagram {{ display: flex; flex-direction: column; align-items: center; gap: 4px; }}
    .arch-node {{ width: 100%; text-align: center; padding: 12px 16px; border-radius: 10px; font-weight: 700; font-size: 14px; border: 1px solid var(--line); background: #fff; box-shadow: 0 2px 8px rgba(15,23,42,.06); }}
    .arch-node small {{ display: block; font-weight: 400; font-size: 12px; color: var(--muted); margin-top: 3px; }}
    .arch-user {{ background: #1e3a5f; color: #fff; border-color: #1e3a5f; }}
    .arch-nginx {{ background: #0f4c35; color: #fff; border-color: #0f4c35; }}
    .arch-pool {{ background: linear-gradient(135deg, #1e293b, #0f172a); color: #e2e8f0; border-color: #334155; }}
    .arch-pool small {{ color: #94a3b8; }}
    .arch-models {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border-color: #2563eb; font-size: 13px; }}
    .arch-branches {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; width: 100%; }}
    .arch-branch {{ display: flex; }}
    .arch-www {{ background: #edf2ff; color: #1d4ed8; border-color: #bfdbfe; }}
    .arch-api {{ background: #f0fdf4; color: #15803d; border-color: #bbf7d0; }}
    .arch-app {{ background: #fefce8; color: #854d0e; border-color: #fde68a; }}
    .arch-arrow {{ font-size: 18px; color: var(--muted); line-height: 1; }}
    .up-grid {{ display: grid; gap: 14px; }}
    .up-card {{ border: 1px solid var(--line); border-radius: 14px; padding: 20px; background: #fff; box-shadow: 0 2px 10px rgba(15,23,42,.05); display: flex; flex-direction: column; gap: 8px; }}
    .up-icon {{ font-size: 24px; }}
    .up-card strong {{ font-size: 15px; font-weight: 800; color: var(--ink); }}
    .up-card p {{ margin: 0; color: var(--muted); font-size: 13px; line-height: 1.6; }}
    .up-claude {{ border-left: 3px solid #2563eb; }}
    .up-siliconflow {{ border-left: 3px solid #16a34a; }}
    .up-extra {{ border-left: 3px solid #d97706; }}
    .about-billing-section {{ padding-top: 56px; }}
    .billing-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }}
    .billing-card {{ border: 1px solid var(--line); border-radius: 16px; background: linear-gradient(180deg, #fff, #f8fafc); padding: 24px; box-shadow: var(--shadow); }}
    .billing-card span {{ display: inline-flex; align-items: center; justify-content: center; min-width: 36px; height: 30px; margin-bottom: 18px; border-radius: 999px; background: #dbeafe; color: var(--blue-dark); font-weight: 900; font-size: 12px; }}
    .billing-card strong {{ display: block; color: var(--ink); font-size: 18px; margin-bottom: 10px; }}
    .billing-card p {{ margin: 0; color: var(--muted); line-height: 1.7; font-size: 14px; }}
    /* Contact section */
    .about-contact-section {{ max-width: 1240px; margin: 0 auto; padding: 64px 18px 80px; }}
    .acs-head {{ text-align: center; margin-bottom: 36px; }}
    .acs-head h2 {{ font-size: 30px; margin-bottom: 10px; }}
    .acs-head p {{ color: var(--muted); font-size: 16px; }}
    .acs-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }}
    .acs-card {{ border: 1px solid var(--line); border-radius: 16px; padding: 28px; background: #fff; box-shadow: var(--shadow); transition: transform .2s, box-shadow .2s; }}
    .acs-card:hover {{ transform: translateY(-3px); box-shadow: 0 12px 36px rgba(15,23,42,.1); }}
    .acs-icon {{ width: 46px; height: 46px; display: grid; place-items: center; border-radius: 14px; background: #eef2ff; color: var(--blue-dark); font-size: 12px; font-weight: 900; margin-bottom: 14px; letter-spacing: 0; }}
    .acs-card strong {{ display: block; font-size: 16px; font-weight: 800; margin-bottom: 10px; color: var(--ink); }}
    .acs-card p {{ color: var(--muted); font-size: 14px; line-height: 1.65; margin: 0; }}
    .acs-link {{ color: var(--blue); font-weight: 700; text-decoration: none; }}
    .acs-link:hover {{ text-decoration: underline; }}
    .acs-code {{ background: #eef2ff; color: var(--blue-dark); padding: 6px 10px; border-radius: 6px; font-size: 13px; display: inline-block; word-break: break-all; }}
    @media (max-width: 980px) {{
      .about-dark-hero {{ padding: 60px 18px 48px; }}
      .about-dark-hero h1 {{ font-size: 38px; }}
      .about-stats-row {{ grid-template-columns: repeat(2, 1fr); }}
      .af-grid, .aas-inner, .acs-grid, .billing-grid {{ grid-template-columns: 1fr; }}
      .arch-branches {{ grid-template-columns: 1fr; }}
      .docs-dark-hero, .cli-hero {{ padding: 56px 18px 46px; }}
      .docs-dark-hero h1, .cli-hero h1 {{ font-size: 38px; }}
      .doc-steps-grid, .doc-tools-grid, .doc-faq-grid, .cli-hero, .cli-steps-grid, .cli-faq-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .docs-cta-inner {{ align-items: flex-start; flex-direction: column; }}
    }}
    @media (max-width: 560px) {{
      .about-dark-hero h1 {{ font-size: 28px; }}
      .about-stats-row {{ grid-template-columns: repeat(2, 1fr); gap: 10px; }}
      .about-section, .about-arch-section, .about-billing-section, .about-contact-section {{ padding-top: 40px; padding-bottom: 32px; }}
      .docs-dark-hero h1, .cli-hero h1 {{ font-size: 30px; }}
      .ddh-endpoint, .doc-steps-grid, .doc-tools-grid, .doc-faq-grid, .cli-hero, .cli-steps-grid, .cli-faq-grid {{ grid-template-columns: 1fr; }}
      .ddh-label {{ text-align: left; padding-left: 4px; }}
    }}
    @media (max-width: 980px) {{
      header {{ align-items: flex-start; flex-direction: column; }}
      nav {{ justify-content: flex-start; }}
      .landing-hero, .conversion-strip, .conversion-grid, .funnel-panel, .referral-panel, .referral-rules, .plan-grid, .capacity-panel, .capacity-grid, .rate-panel, .model-grid, .quickstart, .docs-grid, .tool-grid, .two, .steps, .feature-grid, .about-stack, .about-features, .contact-grid, .support-card {{ grid-template-columns: 1fr; }}
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
      .support-card {{ padding: 20px; }}
      .support-main strong {{ font-size: 34px; }}
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
