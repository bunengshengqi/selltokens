#!/usr/bin/env python3
"""Apply 996 Tokens branding options to the application SQLite database."""

from __future__ import annotations

import os
import sqlite3


DB_PATH = os.environ.get("NEWAPI_DB", "/opt/selltokens/data/new-api/one-api.db")
DOCS_LINK = "https://app.996tokens.com/about#docs"

ABOUT_HTML = r"""
<style>
  .nt-about {
    --nt-ink: #0f172a;
    --nt-muted: #64748b;
    --nt-line: #e2e8f0;
    --nt-blue: #2563eb;
    --nt-cyan: #06b6d4;
    --nt-green: #16a34a;
    --nt-violet: #7c3aed;
    --nt-amber: #d97706;
    font-size: 16px;
    color: var(--nt-ink);
    max-width: 1240px;
    margin: 0 auto;
    padding: 6px 18px 56px;
  }
  .nt-about * { box-sizing: border-box; }
  .nt-about a { text-decoration: none; }
  .nt-hero {
    position: relative;
    overflow: hidden;
    min-height: 420px;
    border: 1px solid rgba(148, 163, 184, .28);
    border-radius: 26px;
    background:
      radial-gradient(circle at 12% 18%, rgba(37, 99, 235, .45), transparent 32%),
      radial-gradient(circle at 78% 18%, rgba(6, 182, 212, .30), transparent 30%),
      linear-gradient(135deg, #07111f 0%, #0f1d35 48%, #111827 100%);
    color: white;
    box-shadow: 0 28px 80px rgba(15, 23, 42, .18);
  }
  .nt-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(255,255,255,.065) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,.065) 1px, transparent 1px);
    background-size: 48px 48px;
    mask-image: linear-gradient(to bottom, rgba(0,0,0,.9), transparent 86%);
  }
  .nt-hero-inner {
    position: relative;
    z-index: 1;
    display: grid;
    grid-template-columns: minmax(0, 1.1fr) 390px;
    gap: 42px;
    align-items: center;
    min-height: 420px;
    padding: 52px;
  }
  .nt-kicker {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    width: fit-content;
    margin: 0 0 18px;
    padding: 7px 12px;
    border: 1px solid rgba(147, 197, 253, .35);
    border-radius: 999px;
    background: rgba(37, 99, 235, .16);
    color: #bfdbfe;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: .08em;
  }
  .nt-hero h1 {
    max-width: 760px;
    margin: 0;
    color: #fff;
    font-size: 52px;
    line-height: 1.08;
    font-weight: 900;
    letter-spacing: 0;
  }
  .nt-hero p {
    max-width: 720px;
    margin: 20px 0 0;
    color: #cbd5e1;
    font-size: 17px;
    line-height: 1.85;
  }
  .nt-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 28px;
  }
  .nt-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 44px;
    padding: 0 18px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,.18);
    font-weight: 800;
    color: #e2e8f0;
    background: rgba(255,255,255,.08);
  }
  .nt-btn.primary {
    border-color: #3b82f6;
    background: #2563eb;
    color: #fff;
    box-shadow: 0 18px 42px rgba(37, 99, 235, .34);
  }
  .nt-panel {
    border: 1px solid rgba(255,255,255,.14);
    border-radius: 22px;
    padding: 18px;
    background: rgba(255,255,255,.08);
    backdrop-filter: blur(14px);
  }
  .nt-panel-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 14px;
  }
  .nt-panel-head strong { font-size: 16px; color: #fff; }
  .nt-live {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    color: #bbf7d0;
    font-size: 12px;
    font-weight: 800;
  }
  .nt-live::before {
    content: "";
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 0 6px rgba(34, 197, 94, .15);
  }
  .nt-route {
    display: grid;
    grid-template-columns: 34px 1fr;
    gap: 12px;
    align-items: center;
    padding: 12px;
    border-radius: 14px;
    background: rgba(15, 23, 42, .42);
    border: 1px solid rgba(255,255,255,.1);
  }
  .nt-route + .nt-route { margin-top: 10px; }
  .nt-dot {
    width: 34px;
    height: 34px;
    display: grid;
    place-items: center;
    border-radius: 11px;
    background: rgba(59, 130, 246, .18);
    color: #93c5fd;
    font-weight: 900;
  }
  .nt-route strong { display: block; color: #fff; font-size: 14px; }
  .nt-route span { display: block; margin-top: 3px; color: #94a3b8; font-size: 12px; line-height: 1.5; }
  .nt-metrics {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin: 18px 0 0;
  }
  .nt-metric {
    border: 1px solid var(--nt-line);
    border-radius: 18px;
    background: #fff;
    padding: 22px;
    box-shadow: 0 16px 44px rgba(15, 23, 42, .07);
  }
  .nt-metric strong { display: block; font-size: 30px; line-height: 1; color: var(--nt-ink); }
  .nt-metric span { display: block; margin-top: 8px; color: var(--nt-muted); font-weight: 700; }
  .nt-section { margin-top: 28px; }
  .nt-section-head {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 18px;
    margin-bottom: 16px;
  }
  .nt-section-head h2 {
    margin: 0;
    color: var(--nt-ink);
    font-size: 28px;
    line-height: 1.2;
    font-weight: 900;
  }
  .nt-section-head p {
    max-width: 560px;
    margin: 8px 0 0;
    color: var(--nt-muted);
    line-height: 1.7;
  }
  .nt-chip {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    min-height: 30px;
    padding: 0 11px;
    border-radius: 999px;
    background: #eff6ff;
    color: #1d4ed8;
    font-size: 12px;
    font-weight: 900;
  }
  .nt-card-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
  }
  .nt-card {
    min-height: 210px;
    border: 1px solid var(--nt-line);
    border-radius: 20px;
    background: #fff;
    padding: 24px;
    box-shadow: 0 14px 40px rgba(15, 23, 42, .06);
  }
  .nt-card-mark {
    width: 42px;
    height: 42px;
    display: grid;
    place-items: center;
    border-radius: 13px;
    margin-bottom: 18px;
    color: #fff;
    font-weight: 900;
  }
  .nt-card:nth-child(1) .nt-card-mark { background: var(--nt-blue); }
  .nt-card:nth-child(2) .nt-card-mark { background: var(--nt-green); }
  .nt-card:nth-child(3) .nt-card-mark { background: var(--nt-violet); }
  .nt-card:nth-child(4) .nt-card-mark { background: var(--nt-cyan); }
  .nt-card:nth-child(5) .nt-card-mark { background: var(--nt-amber); }
  .nt-card:nth-child(6) .nt-card-mark { background: #475569; }
  .nt-card h3 { margin: 0 0 10px; color: var(--nt-ink); font-size: 18px; font-weight: 900; }
  .nt-card p { margin: 0; color: var(--nt-muted); line-height: 1.7; }
  .nt-docs {
    display: grid;
    grid-template-columns: minmax(0, .92fr) minmax(0, 1.08fr);
    gap: 18px;
    align-items: stretch;
  }
  .nt-doc-main,
  .nt-doc-card {
    border: 1px solid var(--nt-line);
    border-radius: 20px;
    background: #fff;
    box-shadow: 0 14px 40px rgba(15, 23, 42, .06);
  }
  .nt-doc-main {
    min-height: 320px;
    padding: 26px;
    background:
      radial-gradient(circle at 16% 10%, rgba(37, 99, 235, .12), transparent 34%),
      linear-gradient(180deg, #ffffff, #f8fafc);
  }
  .nt-doc-main h3 {
    margin: 0 0 12px;
    font-size: 24px;
    color: var(--nt-ink);
    font-weight: 900;
  }
  .nt-doc-main p { margin: 0; color: var(--nt-muted); line-height: 1.75; }
  .nt-endpoint {
    display: grid;
    gap: 8px;
    margin: 22px 0;
    padding: 16px;
    border-radius: 16px;
    border: 1px solid #dbeafe;
    background: #eff6ff;
  }
  .nt-endpoint span {
    color: #1d4ed8;
    font-size: 12px;
    font-weight: 900;
  }
  .nt-endpoint code {
    display: block;
    width: 100%;
    padding: 12px 13px;
    border-radius: 12px;
    background: #0f172a;
    color: #dbeafe;
    overflow-wrap: anywhere;
  }
  .nt-mini-steps {
    display: grid;
    gap: 10px;
    margin-top: 18px;
  }
  .nt-mini-steps div {
    display: grid;
    grid-template-columns: 30px 1fr;
    gap: 10px;
    align-items: start;
    color: var(--nt-muted);
    line-height: 1.6;
  }
  .nt-mini-steps b {
    width: 30px;
    height: 30px;
    display: grid;
    place-items: center;
    border-radius: 10px;
    background: #0f172a;
    color: #fff;
    font-size: 12px;
  }
  .nt-doc-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
  }
  .nt-doc-card {
    min-height: 150px;
    padding: 20px;
    color: var(--nt-ink);
  }
  .nt-doc-icon {
    width: 38px;
    height: 38px;
    display: grid;
    place-items: center;
    border-radius: 12px;
    margin-bottom: 14px;
    background: #eef2ff;
    color: var(--nt-blue);
    font-weight: 900;
  }
  .nt-doc-card strong { display: block; margin-bottom: 8px; font-size: 16px; }
  .nt-doc-card span { color: var(--nt-muted); line-height: 1.6; font-size: 14px; }
  .nt-flow {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    border: 1px solid var(--nt-line);
    border-radius: 22px;
    background: linear-gradient(180deg, #ffffff, #f8fafc);
    padding: 16px;
    box-shadow: 0 16px 42px rgba(15, 23, 42, .06);
  }
  .nt-flow-step {
    position: relative;
    min-height: 148px;
    border-radius: 16px;
    padding: 18px;
    background: #fff;
    border: 1px solid #e5e7eb;
  }
  .nt-flow-step:not(:last-child)::after {
    content: "→";
    position: absolute;
    right: -15px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 2;
    width: 28px;
    height: 28px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: #eff6ff;
    color: var(--nt-blue);
    font-weight: 900;
    border: 1px solid #bfdbfe;
  }
  .nt-flow-step b {
    display: inline-flex;
    width: 28px;
    height: 28px;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: #0f172a;
    color: #fff;
    font-size: 12px;
    margin-bottom: 12px;
  }
  .nt-flow-step strong { display: block; font-size: 16px; margin-bottom: 8px; }
  .nt-flow-step span { color: var(--nt-muted); line-height: 1.65; font-size: 14px; }
  .nt-band {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 300px;
    gap: 20px;
    align-items: center;
    border-radius: 22px;
    padding: 26px;
    background: #0f172a;
    color: #fff;
    box-shadow: 0 22px 60px rgba(15, 23, 42, .14);
  }
  .nt-band h2 { margin: 0 0 10px; color: #fff; font-size: 26px; }
  .nt-band p { margin: 0; color: #cbd5e1; line-height: 1.75; }
  .nt-band-list {
    display: grid;
    gap: 10px;
  }
  .nt-band-list span {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 12px;
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 12px;
    background: rgba(255,255,255,.06);
    color: #e2e8f0;
    font-weight: 800;
  }
  @media (max-width: 960px) {
    .nt-hero-inner, .nt-band { grid-template-columns: 1fr; padding: 32px; }
    .nt-hero h1 { font-size: 40px; }
    .nt-metrics, .nt-card-grid, .nt-flow, .nt-docs { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .nt-flow-step:not(:last-child)::after { display: none; }
  }
  @media (max-width: 620px) {
    .nt-about { padding: 0 10px 42px; }
    .nt-hero-inner { padding: 24px; }
    .nt-hero h1 { font-size: 32px; }
    .nt-metrics, .nt-card-grid, .nt-flow, .nt-docs, .nt-doc-grid { grid-template-columns: 1fr; }
    .nt-section-head { align-items: flex-start; flex-direction: column; }
  }
</style>

<div class="nt-about">
  <section class="nt-hero">
    <div class="nt-hero-inner">
      <div>
        <div class="nt-kicker">ABOUT 996 TOKENS</div>
        <h1>为 AI 编程和 Agent 调用而设计的多模型 API 平台</h1>
        <p>996 Tokens 第一版只开放 Claude、GPT、Gemini 七个核心模型。用户只需要一个 API Key，就能在 Cursor、Claude Code、Cline、脚本和业务系统里切换模型。</p>
        <div class="nt-actions">
          <a class="nt-btn primary" href="/console">返回控制台</a>
          <a class="nt-btn" href="/console/topup">账户充值</a>
          <a class="nt-btn" href="#support">联系客服</a>
        </div>
      </div>
      <div class="nt-panel">
        <div class="nt-panel-head">
          <strong>使用流程</strong>
          <span class="nt-live">ONLINE</span>
        </div>
        <div class="nt-route">
          <div class="nt-dot">1</div>
          <div><strong>用户请求</strong><span>Cursor / Claude Code / OpenAI SDK 统一接入</span></div>
        </div>
        <div class="nt-route">
          <div class="nt-dot">2</div>
          <div><strong>用户控制台</strong><span>余额、API Key、用量、充值和模型列表集中管理</span></div>
        </div>
        <div class="nt-route">
          <div class="nt-dot">3</div>
          <div><strong>模型服务</strong><span>Claude、GPT、Gemini 系列模型统一接入</span></div>
        </div>
      </div>
    </div>
  </section>

  <div class="nt-metrics">
    <div class="nt-metric"><strong>7</strong><span>首发核心模型</span></div>
    <div class="nt-metric"><strong>CNY</strong><span>人民币余额展示</span></div>
    <div class="nt-metric"><strong>¥10</strong><span>最低充值门槛</span></div>
    <div class="nt-metric"><strong>100</strong><span>第一版并发目标</span></div>
  </div>

  <section class="nt-section">
    <div class="nt-section-head">
      <div>
        <span class="nt-chip">核心能力</span>
        <h2>一个账户，接入常用大模型</h2>
        <p>页面、计费、充值、文档和客服都围绕开发者日常使用体验来设计。</p>
      </div>
    </div>
    <div class="nt-card-grid">
      <div class="nt-card"><div class="nt-card-mark">A</div><h3>统一接入</h3><p>一个 API Key 调用 Claude、GPT、Gemini 首发模型，兼容 OpenAI Chat Completions。</p></div>
      <div class="nt-card"><div class="nt-card-mark">B</div><h3>余额清晰</h3><p>账户以人民币展示，充值、扣费和用量记录清晰可查。</p></div>
      <div class="nt-card"><div class="nt-card-mark">C</div><h3>体验稳定</h3><p>面向高频开发和自动化调用场景，持续优化响应体验。</p></div>
      <div class="nt-card"><div class="nt-card-mark">D</div><h3>充值方便</h3><p>保留微信支付、兑换码和人工处理入口，方便处理异常订单。</p></div>
      <div class="nt-card"><div class="nt-card-mark">E</div><h3>开发者友好</h3><p>重点适配 Cursor、Claude Code、Cline、Cherry Studio 和常见 SDK。</p></div>
      <div class="nt-card"><div class="nt-card-mark">F</div><h3>客服支持</h3><p>充值、API Key、扣费和接入问题都可以联系 QQ 客服协助处理。</p></div>
    </div>
  </section>

  <section class="nt-section" id="docs">
    <div class="nt-section-head">
      <div>
        <span class="nt-chip">接入文档</span>
        <h2>在后台里完成第一步，不用跳出控制台</h2>
        <p>这里保留最常用的接入信息。完整公开文档仍在官网，适合发给用户或写教程。</p>
      </div>
      <a class="nt-btn primary" href="https://www.996tokens.com/docs" target="_blank" rel="noopener noreferrer">公开文档 ↗</a>
    </div>
    <div class="nt-docs">
      <div class="nt-doc-main">
        <h3>OpenAI 兼容入口</h3>
        <p>绝大多数客户端只需要替换 Base URL，然后填入后台创建的 API Key。</p>
        <div class="nt-endpoint">
          <span>BASE URL</span>
          <code>https://api.996tokens.com/v1</code>
        </div>
        <div class="nt-mini-steps">
          <div><b>1</b><span>进入控制台，创建或复制你的 API Key。</span></div>
          <div><b>2</b><span>在 Cursor、Cline、Cherry Studio 或 SDK 中填写 Base URL。</span></div>
          <div><b>3</b><span>选择模型后发起测试请求，后台可查看日志和扣费。</span></div>
        </div>
      </div>
      <div class="nt-doc-grid">
        <a class="nt-doc-card" href="https://www.996tokens.com/docs/cursor" target="_blank" rel="noopener noreferrer">
          <div class="nt-doc-icon">C</div><strong>Cursor / Cline</strong><span>图形界面接入，适合 AI 编程日常使用。</span>
        </a>
        <a class="nt-doc-card" href="https://www.996tokens.com/docs/claude-code-cli" target="_blank" rel="noopener noreferrer">
          <div class="nt-doc-icon">CC</div><strong>Claude Code CLI</strong><span>命令行 Agent 编码，配置环境变量后启动。</span>
        </a>
        <a class="nt-doc-card" href="https://www.996tokens.com/docs#sdk" target="_blank" rel="noopener noreferrer">
          <div class="nt-doc-icon">SDK</div><strong>OpenAI SDK</strong><span>Python / Node.js 只改 base_url，其余代码基本不变。</span>
        </a>
        <a class="nt-doc-card" href="/pricing">
          <div class="nt-doc-icon">¥</div><strong>模型价格</strong><span>在模型广场查看可用模型和人民币计价。</span>
        </a>
      </div>
    </div>
  </section>

  <section class="nt-section">
    <div class="nt-section-head">
      <div>
        <span class="nt-chip">系统分工</span>
        <h2>三套视角，各司其职</h2>
      </div>
    </div>
    <div class="nt-flow">
      <div class="nt-flow-step"><b>01</b><strong>公开官网</strong><span>展示品牌、价格、模型、Claude Code 教程和注册入口。</span></div>
      <div class="nt-flow-step"><b>02</b><strong>用户后台</strong><span>管理余额、充值、API Key、调用日志、用量统计和模型权限。</span></div>
      <div class="nt-flow-step"><b>03</b><strong>服务支持</strong><span>处理充值异常、接入问题和账户使用问题。</span></div>
      <div class="nt-flow-step"><b>04</b><strong>API 网关</strong><span>通过 api.996tokens.com 对外提供 OpenAI 兼容调用入口。</span></div>
    </div>
  </section>

  <section class="nt-section" id="support">
    <div class="nt-section-head">
      <div>
        <span class="nt-chip">客服支持</span>
        <h2>遇到问题，添加 QQ 客服</h2>
        <p>充值不到账、Key 无法使用、扣费疑问或接入失败，请打开 QQ 搜索客服号并添加好友。</p>
      </div>
      <span class="nt-btn primary">QQ 61943181</span>
    </div>
    <div class="nt-card-grid">
      <div class="nt-card"><div class="nt-card-mark">QQ</div><h3>客服 QQ</h3><p>61943181</p></div>
      <div class="nt-card"><div class="nt-card-mark">1</div><h3>充值问题</h3><p>支付成功但余额未到账，请带上注册邮箱、订单金额和截图。</p></div>
      <div class="nt-card"><div class="nt-card-mark">2</div><h3>接入问题</h3><p>Cursor、Claude Code、Cline 或 SDK 报错时，请附上错误提示。</p></div>
      <div class="nt-card"><div class="nt-card-mark">3</div><h3>账户问题</h3><p>API Key、余额、用量记录等问题可联系人工确认。</p></div>
    </div>
  </section>

  <section class="nt-section">
    <div class="nt-band">
      <div>
        <h2>服务声明</h2>
        <p>996 Tokens 当前只向海外用户开放。企业合作、兑换码或异常订单请联系 QQ 客服 61943181 确认。</p>
      </div>
      <div class="nt-band-list">
        <span>官网 <b>996tokens.com</b></span>
        <span>控制台 <b>app.996tokens.com</b></span>
        <span>API <b>api.996tokens.com</b></span>
      </div>
    </div>
  </section>
</div>
"""

FOOTER_HTML = r"""
<style>
footer .text-sm.flex-shrink-0 { display: none !important; }
footer > div { justify-content: center !important; }
.custom-footer { width: 100%; text-align: center; }
.custom-footer .footer-note {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  line-height: 1.7;
}
.custom-footer .footer-copy { color: var(--semi-color-text-1); }
.custom-footer .footer-disclaimer { color: var(--semi-color-text-2); font-size: 13px; }
a[href*="newapi.pro"], a[href*="github.com/QuantumNous"] { display: none !important; }
</style>
<div class="custom-footer">
  <div class="footer-note">
    <div class="footer-copy">© 2026 996 Tokens. 版权所有</div>
    <div class="footer-disclaimer">只向海外用户开放</div>
  </div>
</div>
"""


def upsert_option(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "insert or replace into options (`key`, value) values (?, ?)",
        (key, value),
    )


def main() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        upsert_option(conn, "About", ABOUT_HTML.strip())
        upsert_option(conn, "Footer", FOOTER_HTML.strip())
        upsert_option(conn, "DocsLink", DOCS_LINK)
        upsert_option(conn, "general_setting.docs_link", DOCS_LINK)
        conn.commit()
    print(f"Updated 996 Tokens branding options in {DB_PATH}")


if __name__ == "__main__":
    main()
