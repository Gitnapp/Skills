---
name: xuang-ai-finance-research
description: Use when producing AI/quant finance investment research,产业链利润迁移分析,公司首次覆盖报告,因子研究,系统化交易策略,AI4Finance 产品设计,or investment memo. Extracted from xuang.xyz blog/research corpus; enforces thesis-first, data-backed, scenario-driven outputs.
version: 1.0.0
author: Hermes Agent, synthesized from Ang XU public site content
license: Research-use-only
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ai-finance, investment-research, factor-research, systematic-trading, valuation, ai4finance]
    related_skills: [polymarket, arxiv]
---

# Xuang AI Finance Research Skill

## Overview

This skill converts Ang XU's public research/blog style into a reusable workflow for AI/quant finance work. Use it to produce investment research, AI 产业链 analysis, systematic trading strategy designs, factor research, valuation one-pagers, and AI4Finance product specs.

Core philosophy:

1. Thesis first, facts second, narrative last.
2. Every claim must map to a measurable KPI, financial line item, valuation multiple, or portfolio action.
3. Always separate fundamentals from market expectations: profit is realization; market cap is expectation.
4. AI is an intelligence layer, not a source of truth. LLM outputs must bind to structured data, reproducible signals, and traceable sources.
5. Do not predict a single future path when the system has multiple regimes. Use scenario + trigger-based decision rules.

## When to Use

Use this skill when the user asks for:

- 首次覆盖报告 / initiating coverage
- AI 产业链研究, AI supply chain, semiconductor/cloud/model/app layer analysis
- 公司估值、目标价、评级、Bull/Base/Bear 模型
- 产业链利润迁移、跨产业类比、卖铲人 vs 应用层判断
- 因子研究、Alpha101/191、IC/ICIR、因子合成、分组回测
- Crypto CTA, systematic trading, strategy backtest design
- AI manager / Conviction Atlas style investment agent
- Stock OnePager, Coverage Model, AI4Finance dashboard/product spec
- LLM + finance product design where output must be verifiable

Do not use this skill for:

- Pure news summary with no investment conclusion
- Unverified stock tips
- Financial advice phrased as certainty
- High-frequency execution details without market microstructure data
- Legal/tax/accounting advice

## Mandatory Output Standard

Every serious output must contain these blocks unless the user explicitly asks for a short answer:

1. Direct conclusion: rating/action/decision in 1-3 lines.
2. Core thesis: 3-5 numbered points, each with data or KPI.
3. Evidence table: source, metric, current value, interpretation.
4. Scenario table: Bull/Base/Bear with assumptions, probability, valuation/action.
5. Risks: probability, impact, early warning signal.
6. Catalysts: time, event, positive/negative trigger.
7. Caveats: data limitations, uncertainty, what would change the view.

Avoid:

- “长期看好” without numbers.
- “护城河强” without mechanism.
- “估值合理” without multiple/peer/history.
- “AI 会增长” as an investment thesis.
- LLM-only investment decisions.

## Research Mode 1: Initiating Coverage Report

### Standard Structure

Use this structure for a full company report:

```markdown
# {Company} 首次覆盖报告（{Ticker / Market / Private}）

# {One-line title: positioning + key number + judgment}

> **评级：{BUY/HOLD/SELL}** | **目标价/公允估值：{value}** | **空间：{+/-xx%}** | **时间窗口：12 个月**

## 投资摘要

项目 | 数据
---|---
评级 | BUY/HOLD/SELL
当前股价/估值 | value + date
12 个月目标价/公允估值 | value
隐含空间 | +/-xx%
市值 / EV | value
财年截止 | month
核心估值方法 | PE / EV Revenue / EV EBITDA / DCF / SOTP / ARR multiple

## 财务速览

Metric | FY-2A | FY-1A | FYE | FY+1E | FY+2E
---|---:|---:|---:|---:|---:
Revenue |  |  |  |  |  |
YoY |  |  |  |  |  |
Gross Margin |  |  |  |  |  |
EBITDA / Op Income |  |  |  |  |  |
Net Income / EPS |  |  |  |  |  |
Capex |  |  |  |  |  |
FCF |  |  |  |  |  |
Main Multiple |  |  |  |  |  |

## 投资论点与风险
### 论点一：{moat / bottleneck}
### 论点二：{growth engine}
### 论点三：{competition / customer lock-in / supply constraint}
### 论点四：{financial translation}
### 论点五：{valuation mismatch}

## 风险评估（12 项分 4 类）
- 公司特定风险 4 项
- 行业 / 市场风险 3 项
- 财务风险 2 项
- 宏观风险 3 项

## 公司基础
## 财务预测
## 估值分析
## 主要催化剂
## 主要下行风险
## 附录：数据来源、图表索引、模型假设
```

### One-line Title Formula

`{产业链位置/稀缺性} + {核心量化证据} + {估值/风险判断} + {评级}`

Good title patterns:

- “全球 AI 算力的物理中枢，但估值已计入完美执行 —— 持有”
- “$99B RPO 锁定 + NVIDIA 持股 + 高杠杆三连击 —— 买入”
- “汽车业务结构性下滑，AI 期权充分定价 —— 持有”

Rules:

- Include one identity claim: bottleneck, toll-booth, platform, AI option, seller-of-picks, workflow owner.
- Include at least one number: RPO, ARR, backlog, market share, revenue growth, capex, valuation.
- If BUY: emphasize underpriced visibility or mispriced growth.
- If HOLD: emphasize “direction right, but price-in / wait for proof”.
- If SELL/avoid: emphasize narrative-fundamental mismatch.

### Five-Thesis Framework

Each report should use five thesis pillars:

1. Why this company matters.
   - bottleneck, single point of failure, monopoly, toll-booth, platform entrance
2. Why now.
   - product cycle, capex cycle, adoption S-curve, backlog/RPO/order inflection
3. Why competitors cannot easily catch up.
   - technology lead, customer qualification, supply lock, data flywheel, ecosystem lock-in
4. How it appears in financials.
   - revenue growth, margin expansion, operating leverage, FCF, ROIC, EPS CAGR
5. Where the market is wrong.
   - old-business multiple, over-discounted risk, price-in perfect execution, wrong peer set

Single thesis template:

```markdown
### 论点{n}：{conclusion with mechanism or number}

Definition/background: {what this product/business is}

Key data:
- Metric 1: {value, YoY/QoQ, source}
- Metric 2: {peer comparison}
- Metric 3: {forecast or capacity/order figure}

Mechanism chain:
{technology / supply / customer / distribution} → {pricing power / volume} → {margin / cash flow} → {valuation}

Financial mapping:
- Revenue: {how it contributes}
- Margin: {gross/EBITDA impact}
- Capex / FCF: {cash-flow impact}
- Valuation: {multiple or DCF implication}

Verifiable KPIs:
- {KPI 1 threshold}
- {KPI 2 threshold}
- {KPI 3 threshold}

Bull case: {what upside requires}
Bear case: {what breaks the thesis}
```

### Thesis Archetypes

Use the right archetype before writing.

| Archetype | Use for | Core question | Typical valuation anchor |
|---|---|---|---|
| Bottleneck / 卡口 | ASML, TSMC, HBM, 光模块, 液冷 | Is this the binding constraint? | PE, EV/EBITDA, DCF, backlog multiple |
| Seller-of-picks / 卖铲人 | GPU cloud, ODM, equipment, infra | Does all AI capex flow through it? | EV/Revenue, EV/EBITDA, RPO/backlog |
| Platform / 平台层 | Microsoft, OpenAI, Anthropic | Does it own workflow/distribution/API? | EV/Revenue, ARR multiple, SOTP |
| Cycle-to-structure | HBM, optical, AI server | Is cyclical business becoming secular? | PE, PEG, historical multiple |
| Price-in / 估值透支 | Tesla, high-multiple AI names | Is direction right but upside gone? | implied assumptions, reverse DCF |

## Research Mode 2: Risk Assessment

Use 12 risks across four buckets.

```markdown
## 风险评估（12 项分 4 类）

### 公司特定风险（4 项）
**1. {risk name} —— 概率 ~{x%}，影响 {valuation/price/revenue -x%}**
Mechanism: {how the risk transmits into financials}
Early warning: {observable signal + threshold}
Mitigation: {if any}

### 行业 / 市场风险（3 项）
...

### 财务风险（2 项）
...

### 宏观风险（3 项）
...
```

Each risk must have five fields:

| Field | Requirement |
|---|---|
| Name | Specific, not “competition risk” |
| Probability | ~5%, ~20%, ~30%/year, or long-term |
| Impact | valuation/price/revenue/margin/EPS impact |
| Mechanism | event → operating metric → financials → valuation |
| Early warning | observable threshold |

Good early warning examples:

- Copilot seat QoQ growth <20% for two quarters.
- Gross margin down >300 bps QoQ.
- Hyperscaler capex guidance cut >5%.
- RPO growth below revenue growth.
- Key product delayed >2 quarters.
- Benchmark rank falls by 2+ positions.
- Debt/EBITDA breaches covenant threshold.
- Large customer revenue share falls from 60% to below 40%.

## Research Mode 3: Valuation

### Pick the Right Valuation Anchor

| Company type | Primary anchor | Cross-check |
|---|---|---|
| Mature mega-cap | PE / EV EBITDA / DCF | SOTP, historical PE |
| High-growth SaaS / AI lab | EV/Forward Revenue, EV/ARR | DCF sanity check, private rounds |
| GPU cloud / heavy infra | EV/Revenue, EV/EBITDA, RPO | debt capacity, FCF path |
| Semiconductor equipment | PE, EV/EBITDA, backlog | DCF, history |
| Foundry / manufacturing | PE, EV/EBITDA, ROIC | capex cycle, DCF |
| Cyclical growth | PE, PEG, PB/ROE | cycle percentile |
| Private company | latest round, forward ARR | tender/secondary, IPO peers |
| Multi-business platform | SOTP | PE/DCF cross-check |

### Valuation Chapter Template

```markdown
# 估值分析

## Why this method
We use {method} rather than {alternative}, because:
1. {matches business model}
2. {matches market trading convention}
3. {avoids accounting/capex/noise problem}

## Key assumptions
Parameter | Value | Why
---|---:|---
Risk-free rate |  | 
Beta |  | 
ERP |  | 
WACC |  | 
Terminal growth |  | 
Terminal margin |  | 
Exit multiple |  | 

## Comparable companies
Company | Ticker | Growth | Margin | Multiple | Why comparable
---|---|---:|---:|---:|---

## Premium / discount rationale
- Growth: company {x%} vs peers {y%}
- Margin: company {x%} vs peers {y%}
- Visibility: backlog/RPO covers {x} years revenue
- Risk: customer concentration / leverage / regulation warrants {x%} discount

## Valuation summary
Method | Weight | Implied value
---|---:|---:
Comps |  | 
DCF |  | 
SOTP |  | 
Historical multiple |  | 
Weighted average |  | 
Final target |  | 
```

Important: if terminal value contributes >80% of EV, DCF is only a sanity check. Cross-check with comps, SOTP, historical multiple, or private-market valuation.

## Research Mode 4: Catalysts

Catalysts must be time-bound and directional.

```markdown
## 主要催化剂

# | Time | Event | Positive trigger | Negative trigger | Expected impact
---|---|---|---|---|---
1 | 2026-Q2 | Earnings + guidance | revenue > consensus by 5%, margin +200 bps | guidance cut | +12% / -10%
2 | 2026-H2 | Product/customer certification | share >70% | delayed 2 quarters | +15% / -12%
```

Do not write vague catalysts like “AI demand growth”. Write observable events.

Catalyst library:

- Earnings beat, guide-up, FCF margin repair
- Backlog/RPO acceleration, book-to-bill >1, long-term customer contract
- New product ramp, benchmark lead, customer qualification
- IPO, tender, buyback, spin-off, index inclusion
- Export license, tariff exemption, antitrust resolution, rate cut

## Research Mode 5: 产业链利润迁移 / Cross-Industry Analogy

Use this for AI supply chain or any industry chain study.

### Core Question

Do not ask “which segment is better?” Ask:

1. Where is profit now?
2. Where is market cap / expectation now?
3. Does profit lead market cap or market cap lead profit?
4. What is the dominant barrier: resource, technology, network effect, or compute/ecosystem?
5. What trigger changes the regime?

### Segment Definition

| Segment | Definition | Business model | Key metrics |
|---|---|---|---|
| Upstream | scarce resource, equipment, compute, raw material | sell resources/equipment/chips/infra | ASP, capex, backlog, inventory, margin |
| Midstream | transforms inputs into scalable product/distribution | manufacturing, cloud, platform distribution | share, utilization, cost curve, customer lock-in |
| Downstream | monetizes users or enterprise workflows | apps, ads, subscription, agents | ARR, users, ARPU, retention, network effect |

For big tech, split by segment. Do not classify the whole company as one layer if cloud, search, ads, office, or commerce have different economics.

### Required Charts / Tables

Produce four core charts or equivalent tables:

1. Absolute net profit by upstream/midstream/downstream.
2. Absolute market cap by segment.
3. Profit-share stacked view.
4. Market-cap-share stacked view.

Then produce pairwise spread tables:

- Upstream vs Midstream
- Midstream vs Downstream
- Upstream vs Downstream

Spread formula:

- profit spread = segment A profit - segment B profit
- market cap spread = segment A market cap - segment B market cap
- crossing zero = regime event

Interpretation:

| Observation | Meaning |
|---|---|
| Profit crosses zero first, market cap lags | market stuck in old narrative |
| Market cap crosses first, profit lags | market pricing future endgame |
| Both cross together | transition confirmed |
| Long divergence | structural narrative premium |
| Profit rebounds but market cap does not | cyclical bounce, not structural return |

### Dominant Barrier Framework

| Barrier | Pattern | Investment meaning |
|---|---|---|
| Resource monopoly | upstream earns first; demand peak can kill whole chain | do not mistake commodity peak for permanent moat |
| Technology monopoly | midstream can win structurally | watch cost curve, share, customer certification |
| Network effect | downstream can dominate market cap before profit | use basket; winners may rotate |
| Compute/ecosystem monopoly | mixed; must monitor signals | do not static-compare to Cisco or say “this time different” |

### Four Patterns

1. Gradual decline / co-death: resource chain earns until demand peaks, then all segments suffer.
2. Synchronous reversal: market cap and profit both migrate around the same period.
3. Delayed reaction: profit collapses before market cap accepts it; seller-of-picks narrative inertia.
4. Structural divergence: downstream market cap dominates despite midstream profit strength, often due to network effect.

### AI Supply Chain Specific Scenario Set

| Scenario | Story | Trigger | Action |
|---|---|---|---|
| Internet pattern | Upstream peaks; downstream apps/platforms capture largest value | downstream gross margin >60%, profitable ARR-scale apps | reduce upstream, build downstream basket |
| EV battery pattern | Cloud/midstream becomes CATL-like winner | self-developed chip share >50%, AI cloud segment high growth and profitable | add MSFT/GOOGL/AMZN-like midstream |
| New AI species | Agent economy and inference cost collapse rewire workflow value | inference cost down 10x, agent ARR >$10B with small headcount | lower old-chain weight, diversify into new apps |

Monitoring thresholds:

| Signal | Threshold | Action |
|---|---:|---|
| Hyperscaler capex YoY | < +30% for 2 quarters | reduce upstream 25% |
| Hyperscaler capex YoY | < +10% for 2 quarters | reduce upstream 50% |
| Any hyperscaler capex guidance cut | triggered | immediate upstream risk review |
| NVIDIA / upstream data-center revenue growth | < +30% for 2 quarters | reduce upstream 50% |
| GPU rental/secondary price | -30% | upstream risk rising |
| AI app ARR | >$5B and GM >50% | downstream basket candidate |
| Foundation model GM | >60% | software-like economics emerging |

Principle: position limits are more reliable than top-calling.

## Research Mode 6: Factor Research

### Mandatory Factor Workflow

Never approve a factor based only on recent returns. Use:

1. Factor definition and economic meaning.
2. Data coverage and sample days.
3. IC mean.
4. ICIR.
5. IC > 0 ratio.
6. abs(IC).
7. IC time series.
8. Cumulative IC.
9. IC decay across horizons.
10. Factor correlation matrix.
11. Group backtest.
12. Long-short spread.
13. Composite vs single factor comparison.

### Factor Screening Rules

| Metric | Meaning | Rule |
|---|---|---|
| IC mean | average predictive correlation | must have economic meaning |
| ICIR | IC mean / IC std | prefer stability over one-off strength |
| IC > 0 ratio | directional consistency | should be meaningfully above random |
| abs(IC) | strength ignoring sign | high abs but unstable sign is risky |
| days | sample length | reject small-sample factors |

### IC Decay Rules

- 1D IC high but 5D decays: short-horizon factor.
- 5D/10D IC stable: medium-horizon rebalance possible.
- IC turns negative: may be reversal/crowding.
- Rebalance frequency must follow IC decay, not preference.

### Group Backtest Rules

- Sort universe by factor value into 5 or 10 groups.
- Check monotonicity across groups.
- Compute long-short spread, e.g. G5 - G1.
- Verify results are not driven by a few extreme days.
- Consider industry/size neutralization.

### Factor Combination Rules

Before factor synthesis:

1. Build correlation matrix.
2. Remove highly correlated duplicate logic.
3. Choose weight method: equal weight, IC weighted, ICIR weighted.
4. Show weight allocation.
5. Compare composite IC/ICIR against single factors.
6. Composite should improve stability, not just backtest return.

Anti-patterns:

- Combining many similar price-volume factors without correlation check.
- Using 1D factor for monthly rebalance.
- High IC mean with low ICIR.
- Top group return without monotonicity.
- Ignoring survivorship bias, trading cost, limit-up/down, suspension.

## Research Mode 7: Systematic Trading / Crypto CTA

### Strategy Design Checklist

Every strategy spec must define:

- Universe: assets/stocks/markets.
- Data source and frequency.
- Signal formulas.
- Signal normalization.
- Portfolio construction.
- Position sizing.
- Rebalance frequency.
- Trading cost and slippage.
- Risk control.
- Backtest metrics.
- Deployment/monitoring.

### Multi-Signal Score

Process:

1. Calculate signals: momentum, trend, volume, volatility, sentiment, on-chain, valuation.
2. Standardize each signal: z-score, rank percentile, or [-1, 1].
3. Check signal correlation.
4. Combine via equal weight, IC weight, ICIR weight, or custom risk-adjusted weight.
5. Map score to action: long / flat / short / reduce / rebalance.
6. Explain contribution: which signal helped, which hurt.

Anti-pattern:

- Add RSI + MACD + sentiment without standardization.
- Multiple correlated trend indicators counted as independent alpha.
- “看多 BTC” without signal breakdown.

### Crypto CTA Baseline

Prefer daily trend-following over default high-frequency.

Core pieces:

- Trend filter: moving-average regime, breakout, ADX-like strength.
- Momentum signal: price return / rank / acceleration.
- Volume confirmation.
- Volatility filter and volatility targeting.
- Position cap per asset.
- Cash reserve / max exposure.
- Max drawdown control.
- Stop loss / trailing stop.
- Rolling backtest.

Output metrics:

- cumulative return
- annualized return
- Sharpe
- Sortino if possible
- max drawdown
- volatility
- win rate
- profit/loss ratio
- turnover
- benchmark excess return
- number of trades
- average holding period
- transaction cost impact

## Research Mode 8: AI4Finance Product Design

### System Architecture

Use a layered architecture:

1. Data Ingestion Layer
   - market data, GitHub, on-chain, financial statements, news, prediction markets
2. Processing Layer
   - cleaning, feature engineering, signal calculation, anomaly detection
3. Intelligence Layer
   - LLM strategy parser, AI manager reasoning, memo/report generation
4. Modeling Layer
   - backtest, factor evaluation, valuation model, scenario analysis
5. Product Layer
   - dashboard, leaderboard, one-pager, API, export, paid unlock
6. Monitoring Layer
   - data freshness, strategy drift, signal failures, alert precision

Rule: LLM belongs in Intelligence Layer. It cannot replace data, backtest, or valuation truth.

### Natural Language Strategy → Backtest

Pipeline:

1. Parse market, universe, buy/sell conditions, frequency, constraints.
2. Convert to structured DSL:
   - universe
   - filters
   - signals
   - entry rules
   - exit rules
   - rebalance rules
   - cost model
3. Run backtest with trading cost, slippage, suspension/limit handling where relevant.
4. Output annual return, Sharpe, max drawdown, win rate, turnover, benchmark excess.
5. Save strategy config for reproducibility.

Anti-pattern:

- LLM says “strategy is good” without backtest.
- Natural language not converted to deterministic rules.
- No cost, slippage, or survivorship-bias control.

### AI Manager

An AI investment manager must include:

- Persona / style: momentum, value, macro, risk parity, event-driven, on-chain.
- Risk preference: conservative, balanced, aggressive.
- Signal engine: list, weight, score, explanation.
- Portfolio state: holdings, cash, weights, turnover.
- Performance: NAV, Sharpe, drawdown, hit rate, ranking.
- Memo: conclusion, evidence, signal breakdown, action, risks.

Do not create a “manager” with only a persona prompt. It must have portfolio state and track record.

### Productization Checklist

A finance strategy product is not a notebook. Include:

- Dashboard
- Current holdings
- NAV curve
- Signal explanation
- Risk warnings
- Leaderboard
- Memo generation
- API/export
- Data freshness checks
- Monitoring alerts
- Permission/payment if paid
- Disclaimer: not investment advice

Leaderboard must not rank only by return. Include Sharpe, max drawdown, hit rate, sample size, and period.

## Research Mode 9: Web3 / On-Chain / Atomic Arbitrage

### Atomic Arbitrage

Rules:

- Execute all legs in one transaction; fail atomically.
- Include gas, slippage, DEX fee, flash-loan fee in net profit.
- Set minimum profit threshold.
- Use minimum output protection.
- Simulate before execution.
- Protect against MEV/front-running where possible.
- Audit smart contract permissions.

Do not treat raw DEX price spread as profit.

### On-Chain Monitor

Alert must include:

- chain
- tx hash
- token
- amount
- from/to address
- label: exchange, fund, bridge, contract, unknown
- risk reason
- confidence
- actionability

Avoid alert spam. Define whale threshold, filter exchange wallets, and distinguish bridge/internal transfers from true whale activity.

## Research Mode 10: OnePager / Coverage Model

### Coverage Model

Every valuation model must include:

- TAM top-down estimate.
- Bull/Base/Bear scenarios.
- Assumptions for market size, market share, revenue, margin, multiple, discount rate.
- Sensitivity analysis.
- Separate model output from investment conclusion.

No single-point valuation without assumptions.

### Stock OnePager

A one-pager should include:

- ticker and market
- company overview
- price chart
- volume chart
- financial metrics
- valuation metrics
- key risks
- investment summary
- printable/shareable output
- data source

Prefer visual clarity over long prose.

## Data Source and Chart Discipline

Every important chart/table needs:

```markdown
> 📊 看图要点：{what this proves: mismatch, inflection, trend, sensitivity, comparison}
> 📂 数据来源：{specific source}
```

Data source hierarchy:

1. Company first-party: annual/quarterly report, earnings call, investor day, press release.
2. Regulatory: 10-K, 10-Q, 20-F, S-1/F-1, proxy, exchange filings.
3. Consensus / market: Bloomberg, FactSet, Visible Alpha, Yahoo Finance, Stockanalysis.
4. Industry: Gartner, IDC, TrendForce, SEMI, Omdia, Synergy Research, Dell’Oro, SemiAnalysis.
5. News: Reuters, Bloomberg, CNBC, The Information, TechCrunch.
6. Alternative: GitHub, on-chain, benchmark, LinkedIn, patent, app/user data.

Always specify:

- currency and unit
- fiscal year end
- actual vs estimate
- GAAP vs Non-GAAP
- reported vs constant currency
- diluted vs basic shares
- EV definition
- ARR/RPO/backlog definitions
- capex and FCF definitions
- pre-money vs post-money for private companies

## Writing Style

Use conclusion-first paragraphs.

Good sentence patterns:

- “核心不是 A，而是 B。”
- “市场错在……”
- “看似贵，但……”
- “方向正确，但估值已 price-in。”
- “这不是周期反弹，而是结构迁移。”
- “杠杆是 feature 不是 bug, if backed by contract visibility.”
- “Capex 不是黑洞，而是锁定未来 revenue 的 prepayment — only if RPO/backlog supports it.”

Replace adjectives with mechanism chains:

Bad:
“公司竞争力强，增长空间大。”

Good:
“公司通过 {technology lead} → {customer qualification} → {capacity lock} → {ASP stability} → {margin expansion} 形成闭环，最终体现为 FY2026-2028 EBITDA CAGR {x%}。”

## Anti-Pattern Library

Research anti-patterns:

- Story without data.
- Data without investment conclusion.
- Upside without downside.
- Risk list without probability/impact.
- Catalyst without time.
- Chart without interpretation.
- DCF terminal value drives everything but no cross-check.

Factor anti-patterns:

- Recent return only.
- Small sample.
- High IC but low ICIR.
- No IC decay.
- Highly correlated factors blindly combined.
- Group returns not monotonic.

Backtest anti-patterns:

- Look-ahead bias.
- Survivorship bias.
- No trading cost/slippage.
- No suspension/limit handling for A-shares.
- Overfit parameters.
- No out-of-sample / rolling validation.

AI anti-patterns:

- LLM directly issues trade action without structured inputs.
- Memo has no signal values.
- Manager has persona but no portfolio or track record.
- Hallucinated data source.
- “Strategy generated” treated as “strategy validated”.

Product anti-patterns:

- Notebook-only strategy.
- No API/export.
- Leaderboard ranked only by return.
- No risk warning.
- Paid content sells unverifiable “inside view”.

## Verification Checklist

Before delivering output using this skill:

- [ ] Did I state a clear action/rating/conclusion?
- [ ] Does every thesis have at least one measurable KPI?
- [ ] Did I separate fundamentals from market expectations?
- [ ] Did I include Bull/Base/Bear or explain why not?
- [ ] Did I quantify risks with probability/impact/early warning?
- [ ] Did I use the correct valuation anchor for company type?
- [ ] Did I include catalysts with time and event?
- [ ] Did I state data source and data caveats?
- [ ] For factors: IC, ICIR, IC decay, correlation, group backtest checked?
- [ ] For strategies: trading cost, slippage, drawdown, turnover, benchmark included?
- [ ] For AI outputs: are LLM conclusions grounded in structured data?
- [ ] Did I avoid certainty language and investment-advice framing?

## Source Corpus

Synthesized from `/Users/admin/Desktop/爬虫` crawl of `https://xuang.xyz`, especially:

- AI产业链-综合研究-产业链利润迁移与类比研究.md
- AI产业链-公司研究-*首次覆盖报告.md
- FactorLab因子研究.md
- Atlas策略图鉴.md
- 项目-ConvictionAtlas.md
- 项目-StrategyLab.md
- 项目-CoverageModel.md
- 项目-StockOnePager.md
- 项目-FintechRadar.md
- 项目-AtomicArbitrage.md
- 项目-OnChainMonitor.md

See `references/source-map.md` for the detailed extraction map.
