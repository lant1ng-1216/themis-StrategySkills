# Themis-Verdict

> *Themis — the Greek goddess of justice, law, and order.*

A judicial-framework strategy skill for AI agents, built on CoinMarketCap real-time data.

Built for the **BNB Hack: AI Trading Agent Edition** hackathon (Track 2 — Strategy Skills).

Powered by [Verdict Protocol](https://verdictprotocol.online).

---

## The Core Idea

Most strategy tools ask: *"What will the market do next?"*

Themis-Verdict asks: *"Who is making a collective mistake right now — and what is the evidence?"*

---

## Three-Court Verdict Framework

- COURT I — Claim Court: State a falsifiable hypothesis before seeing all data
- COURT II — Evidence Court: Examine 7 dimensions, both supporting and opposing  
- COURT III — Verdict Court: Synthesize evidence into a structured strategy spec

Every verdict includes explicit invalidation conditions, a 24-hour appeal mechanism, a self-calibrating confidence score, and macro event warnings.

---

## 7-Dimension Evidence System

1. Price Momentum — get_crypto_quotes_latest
2. Market Sentiment — get_global_metrics_latest (Fear and Greed Index)
3. Market Breadth — get_crypto_listings_latest (Top 10 assets)
4. Derivatives Activity — get_global_metrics_latest (derivatives volume change)
5. BTC Dominance Flow — get_global_metrics_latest (btc_dominance_24h_change)
6. Sector Rotation — get_crypto_categories
7. Stablecoin Flow — get_global_metrics_latest (stablecoin volume change)

---

## 5 Market Regimes

- PANIC SELLOFF: Collective mistakes occurring, contrarian opportunity building
- BEAR TREND: Trending lower, bears dominant, bounces are sell opportunities
- ACCUMULATION: Depressed prices, declining momentum, smart money may be accumulating
- RECOVERY: Recovering from lows, risk appetite returning
- BULL TREND: Trending higher, bulls dominant, dips are buy opportunities

---

## Self-Calibrating Signal Weights

Bayesian weight updates improve accuracy over time. Each verdict is verified 24 hours after issuance. Correct verdicts increase signal weights (+0.05), incorrect verdicts decrease them (-0.05). Weights are bounded between 0.1 and 2.0.

---

## Quick Start

```bash
git clone https://github.com/lant1ng-1216/themis-verdict
cd themis-verdict
pip install requests python-dotenv openai rich
cp .env.example .env
python demo/main.py
```

Required API keys:
- CoinMarketCap API: https://pro.coinmarketcap.com/signup
- DeepSeek or any OpenAI-compatible LLM
- Finnhub API: https://finnhub.io/register

---

## Files

- THEMIS_VERDICT_SKILL.md — The core Skill file for DoraHacks submission
- demo/main.py — Runnable terminal demo system
- .env.example — Environment variable template

---

## Built With

- CoinMarketCap AI Agent Hub — real-time market data
- Finnhub Economic Calendar — macro event data
- DeepSeek / OpenAI-compatible LLM — verdict reasoning engine
- Verdict Protocol (https://verdictprotocol.online) — the on-chain verdict layer

---

*Themis-Verdict is a Track 2 submission for BNB Hack: AI Trading Agent Edition.*
*Built by @lant1ng-1216 — https://github.com/lant1ng-1216*
