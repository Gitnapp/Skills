---
name: paid-service-request
description: Generate paid service request documents for manager approval. Use when the user needs to write a subscription/service approval request, asks to "write a paid service request", mentions "付费服务申请", or needs to justify API/SaaS costs to a manager. Outputs markdown + PDF.
---

# Paid Service Request Generator

Generate a concise, data-driven paid service request document (markdown + PDF) for manager approval.

## Workflow

### 1. Collect Information

Gather from user (skip what's already known, ask one question at a time):

- **Project name** and one-line description
- **Project status**: in development / ready to launch / running
- **Services to subscribe**, each needs:
  - Service name
  - Pricing page URL
  - Desired tier (e.g. Pro, Ultra)
  - Purpose (one sentence)
- **Usage estimate basis** (daily calls × 30 days)

### 2. Fetch Pricing

For each pricing URL, open it with Playwright browser tools:

```
browser_navigate → URL
browser_wait_for → tier name text (e.g. "Pro"), up to 5 seconds
browser_snapshot → extract from snapshot: tier name, price, request quota, hard/soft limit, overage cost, rate limit
```

If browser extraction fails, ask user for the numbers directly.

### 3. Generate Markdown

Save to `{project_dir}/paid_service_request.md` using this template:

```markdown
# 付费服务申请

## 项目背景

**项目名称**：{name}

**目标**：{description}

**当前状态**：{status}

## 需要订阅的服务

### {N}. {service} — {tier} 套餐

| 项目 | 详情 |
|------|------|
| 平台 | {platform} |
| 用途 | {purpose} |
| 套餐 | {tier} |
| 费用 | **${price}/月** |
| 配额 | {quota} |
| 速率 | {rate_limit} |
| 链接 | {pricing_url} |

**实际用量估算**：{formula} = **约 {number} 次/月**，占配额 {percent}%。

## 费用汇总

| 服务 | 月费 |
|------|------|
| {service1} | ${price1} |
| **合计** | **${total}/月** |

## 产出价值

- {value_point_1}
- {value_point_2}
- {value_point_3}
```

**Style rules**: no filler text, prices must come from actual pricing pages, usage estimates must show calculation formula, value points in plain language (2-3 items).

### 4. Render PDF

Run `{baseDir}/scripts/render_pdf.sh {markdown_path} {pdf_path}`:

1. Converts markdown → styled HTML (Chinese fonts, clean tables)
2. Serves HTML on a temp local port
3. Uses Playwright `page.pdf()` to export A4 PDF
4. Cleans up temp server

If the script fails, fall back to manual steps:
1. Convert markdown to HTML with inline CSS from `{baseDir}/assets/style.css`
2. Start `python3 -m http.server` on a free port
3. `browser_navigate` → `http://localhost:{port}/file.html`
4. `browser_run_code` → `page.pdf({ path, format: 'A4', margin: { top: '20mm', bottom: '20mm', left: '15mm', right: '15mm' }, printBackground: true })`
5. Kill the server

### 5. Deliver

Report both file paths to user:
- `paid_service_request.md` — editable source
- `paid_service_request.pdf` — ready to send
