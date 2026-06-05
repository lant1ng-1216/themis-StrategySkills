# Themis-Verdict

> *Themis — the Greek goddess of justice, law, and order. She holds the scales of balance and the sword of truth.*

A judicial-framework strategy skill for AI agents, built on CoinMarketCap real-time data. Instead of predicting markets, Themis-Verdict acts as a **Chief Market Verdict Officer** — examining evidence across 7 dimensions, classifying market regimes, and delivering structured, falsifiable verdicts.

Built for the **BNB Hack: AI Trading Agent Edition** hackathon (Track 2 — Strategy Skills).

Powered by [Verdict Protocol](https://verdictprotocol.online) — a universal on-chain verdict layer.

---

## The Core Idea

Most strategy tools ask: *"What will the market do next?"*

Themis-Verdict asks: *"Who is making a collective mistake right now — and what is the evidence?"*

Markets transfer wealth from wrong judgments to correct ones. This skill detects collective errors — overleveraged longs, panic-driven selling, ignored accumulation signals — and constructs a falsifiable verdict around them.

---

## Three-Court Verdict Framework

- **COURT I — Claim Court**: State a falsifiable hypothesis before seeing all data
- **COURT II — Evidence Court**: Examine 7 dimensions, both supporting and opposing
- **COURT III — Verdict Court**: Synthesize evidence into a structured strategy spec

Every verdict includes:
- Explicit invalidation conditions (minimum 4)
- A 24-hour appeal mechanism
- A self-calibrating confidence score
- A macro event warning if high-impact events fall within the 48-hour window

---

## 7-Dimension Evidence System

1. Price Momentum — `get_crypto_quotes_latest`
2. Market Sentiment — `get_global_metrics_latest` (Fear and Greed Index)
3. Market Breadth — `get_crypto_listings_latest` (Top 10 assets)
4. Derivatives Activity — `get_global_metrics_latest` (derivatives volume change)
5. BTC Dominance Flow — `get_global_metrics_latest` (btc_dominance_24h_change)
6. Sector Rotation — `get_crypto_categories`
7. Stablecoin Flow — `get_global_metrics_latest` (stablecoin volume change)

---

## 5 Market Regimes

- **PANIC SELLOFF**: Collective mistakes occurring, contrarian opportunity building
- **BEAR TREND**: Trending lower, bears dominant, bounces are sell opportunities
- **ACCUMULATION**: Depressed prices, declining momentum, smart money may be accumulating
- **RECOVERY**: Recovering from lows, risk appetite returning
- **BULL TREND**: Trending higher, bulls dominant, dips are buy opportunities

---

## Self-Calibrating Signal Weights

Bayesian weight updates improve accuracy over time. Each verdict is verified 24 hours after issuance. Correct verdicts increase signal weights (+0.05), incorrect verdicts decrease them (-0.05). Weights are bounded between 0.1 and 2.0.

---

## CoinMarketCap AI Agent Hub — Deep Integration

This project uses the CoinMarketCap AI Agent Hub as its exclusive real-time data layer across 5 endpoints and 7 analytical dimensions.

### 5 CMC Endpoints Used

| Endpoint | Dimensions Powered |
|----------|--------------------|
| `get_global_metrics_latest` | Sentiment, Derivatives, BTC Dominance, Stablecoin Flow |
| `get_crypto_quotes_latest` | Price Momentum, Asset Resolution |
| `get_crypto_listings_latest` | Market Breadth (Top 10) |
| `get_crypto_categories` | Sector Rotation (20+ sectors) |
| `search_cryptos` | Dynamic ID resolution for any token |

### What Makes This Integration Deep

Most CMC integrations pull a price and display it. Themis-Verdict uses CMC data to power a multi-layer reasoning system:

1. **Regime Classification** — 5 market states scored using weighted signals from 4 different CMC endpoints simultaneously
2. **Bull/Bear Intensity Score** — a composite 0-100 score computed from 6 CMC data fields in real time
3. **Evidence Weighting** — each of the 7 dimensions has a dynamic weight that updates based on historical verdict accuracy
4. **Falsification Logic** — invalidation conditions are derived from live CMC thresholds, not static rules
5. **Cross-Asset Synthesis** — 4 assets analyzed in parallel, with correlation observations powered by CMC data

### Key CMC Data Fields and How They Are Used

- `derivatives_24h_percentage_change` — detects panic deleveraging vs. stabilization (volume change, not price)
- `stablecoin_24h_percentage_change` — measures safe-haven capital flow intensity (volume change, not market cap)
- `btc_dominance_24h_percentage_change` — tracks directional capital rotation between BTC and altcoins
- `fear_greed_value` — weighted into regime classification with contextual interpretation rules
- `avg_price_change` per category — powers sector rotation analysis across 20+ market sectors

---

## Quick Start

```bash
git clone https://github.com/lant1ng-1216/themis-verdict
cd themis-verdict
pip install requests python-dotenv openai rich
cp .env.example .env
# Edit .env with your API keys
python demo/main.py
```

**Required API keys:**
- [CoinMarketCap API](https://pro.coinmarketcap.com/signup) — free Basic plan
- Any OpenAI-compatible LLM (DeepSeek, OpenAI, Groq, etc.)
- [Finnhub API](https://finnhub.io/register) — free plan for macro events

---

## Files

| File | Description |
|------|-------------|
| `THEMIS_VERDICT_SKILL.md` | The core Skill file — DoraHacks submission |
| `demo/main.py` | Runnable terminal demo system |
| `.env.example` | Environment variable template |

---

## Built With

- [CoinMarketCap AI Agent Hub](https://coinmarketcap.com/api/agent) — exclusive real-time data layer
- [Finnhub Economic Calendar](https://finnhub.io) — macro event data
- DeepSeek / any OpenAI-compatible LLM — verdict reasoning engine
- [Verdict Protocol](https://verdictprotocol.online) — the on-chain verdict layer this skill extends

---

*Themis-Verdict is a Track 2 submission for BNB Hack: AI Trading Agent Edition.*
*Built by [@lant1ng-1216](https://github.com/lant1ng-1216)*
