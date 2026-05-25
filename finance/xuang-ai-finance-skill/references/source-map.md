# Source Map: xuang.xyz → xuang-ai-finance-research skill

Generated from local crawl folder: `/Users/admin/Desktop/爬虫`.

## Corpus Coverage

| Source file | Extracted skill area | Notes |
|---|---|---|
| `AI产业链-综合研究-产业链利润迁移与类比研究.md` | 产业链利润迁移、跨产业类比、主导壁垒、价利关系、AI scenario | Core source for industry-chain method |
| `AI产业链-公司研究-*.md` | 首次覆盖报告、5-thesis structure、risk/valuation/catalyst/data discipline | 12 company reports across AI chain |
| `FactorLab因子研究.md` | IC/ICIR、IC decay、分组回测、因子合成、相关性矩阵 | Page is UI-like but workflow is clear |
| `Atlas策略图鉴.md` and `Atlas-*` | AI manager、leaderboard、portfolio/NAV/memo productization | Some SPA pages had limited static content |
| `项目-ConvictionAtlas.md` | AI investment manager architecture | Data → signals → decisions → memo |
| `项目-StrategyLab.md` | Natural language strategy → structured backtest | LLM parses, backtest validates |
| `项目-CoverageModel.md` | TAM top-down valuation, three-scenario modeling | Bull/Base/Bear required |
| `项目-StockOnePager.md` | One-page equity research output | Ticker → visual report |
| `项目-FintechRadar.md` | AI4Finance open-source radar | GitHub activity, classification, export |
| `项目-AtomicArbitrage.md` | EVM atomic arbitrage rules | Gas/slippage/flash-loan fees, all-or-revert |
| `项目-OnChainMonitor.md` | On-chain alert design | Whale threshold, address labels, tx hash |

## Extracted Core Principles

### 1. Thesis-first research

The reports start with rating, target price/fair value, upside/downside, and a title that combines identity + key number + judgment. Company background comes after the investment thesis.

Reusable rule:

- Start with conclusion.
- Explain what would make the conclusion wrong.
- Quantify thesis, risk, and catalyst.

### 2. Five-thesis report structure

Across company reports, the recurring pattern is:

1. Moat / bottleneck / why important.
2. Growth engine / why now.
3. Competitive insulation / why others cannot catch up.
4. Financial translation / how it appears in revenue, margin, FCF, EPS.
5. Valuation mismatch / what the market misprices.

### 3. Risk discipline

Risks are not listed generically. They are grouped into 12 items across:

- Company-specific
- Industry / market
- Financial
- Macro

Each risk should include probability, impact, mechanism, early warning, and mitigation.

### 4. Valuation triangulation

Valuation is not single-method. Use the company type to choose the anchor:

- PE/EV EBITDA for mature or manufacturing companies.
- EV/Revenue or ARR multiple for high-growth SaaS/AI labs.
- RPO/backlog and debt capacity for GPU cloud or heavy infra.
- SOTP for multi-business platforms.
- DCF mostly as sanity check when terminal value dominates.

### 5. Profit vs market-cap industry-chain analysis

The comprehensive AI chain research uses a dual-line framework:

- Profit = realized fundamentals.
- Market cap = expectations.

The key is not simply upstream vs midstream vs downstream, but whether profit and market cap cross, diverge, or lag.

### 6. Dominant barrier determines the pattern

| Barrier | Pattern |
|---|---|
| Resource monopoly | Upstream earns first; demand peak can kill the chain |
| Technology monopoly | Midstream can structurally win |
| Network effect | Downstream can dominate market cap before profit |
| Compute/ecosystem monopoly | Mixed; monitor signals, avoid static analogy |

### 7. Factor research discipline

Factor research must include:

- IC mean
- ICIR
- IC > 0 ratio
- abs(IC)
- sample days
- IC time series
- cumulative IC
- IC decay
- correlation matrix
- group backtest
- long-short spread

### 8. AI4Finance architecture

Layered design:

1. Data ingestion
2. Processing / feature engineering
3. Intelligence layer (LLM)
4. Backtesting/modeling
5. Product layer
6. Monitoring layer

LLM is not truth. It translates, explains, summarizes, and generates memos grounded in structured data.

### 9. Strategy productization

A strategy is not complete until it has:

- Dashboard
- Signals
- Holdings
- NAV
- Risk metrics
- Memo
- Leaderboard
- API/export
- Monitoring

### 10. Anti-patterns

Avoid:

- Story without data.
- Single-point valuation.
- No downside case.
- LLM-generated investment conclusion without signal values.
- Backtest without trading cost/slippage.
- Factor combination without correlation check.
- Leaderboard ranked only by return.

## Known Crawl Limitations

- Several Atlas pages were SPA/client-rendered, so Markdown content is thin.
- `Atlas策略图鉴.md` contains some mojibake from static HTML encoding.
- `Atlas-API文档.md` only captured “Swagger UI”.
- The research reports and comprehensive AI chain article were captured well and form the main knowledge base.

## Recommended Future Enhancement

If a browser-rendered crawl is needed later, re-capture SPA pages with Playwright/browser snapshot and merge dynamic text into this skill. The current skill intentionally prioritizes the high-signal research reports over thin SPA pages.
