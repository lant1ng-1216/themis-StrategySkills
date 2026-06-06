# Themis-Verdict — Market Verdict Skill

*Built on [Verdict Protocol](https://verdictprotocol.online) — a universal on-chain verdict layer.*

A judicial-framework strategy skill that transforms raw CoinMarketCap data into structured, falsifiable trading verdicts. The agent acts as a **Chief Market Verdict Officer** — examining evidence across 7 dimensions, classifying the market regime, and delivering a formal verdict with explicit invalidation conditions and an appeal mechanism.

Submitted for **BNB Hack: AI Trading Agent Edition — Track 2: Strategy Skills**.

---

## Prerequisites

```json
{
  "mcpServers": {
    "cmc-mcp": {
      "url": "https://mcp.coinmarketcap.com/mcp",
      "headers": {
        "X-CMC-MCP-API-KEY": "your-api-key"
      }
    }
  }
}
```

Get your API key from https://pro.coinmarketcap.com/login

---

## Core Philosophy

Most strategy tools ask: **"What will the market do next?"**

Themis-Verdict asks: **"Who is making a collective mistake right now, and what is the evidence?"**

Markets transfer wealth from wrong judgments to correct ones. This skill detects collective errors — overleveraged longs, panic-driven selling, ignored accumulation signals — and constructs a falsifiable verdict around them.

Every verdict must:
1. State a specific, falsifiable claim **before** examining data
2. Present both supporting AND opposing evidence
3. Define explicit conditions under which the verdict is invalid
4. Include a 24-hour appeal mechanism for re-examination

---

## Step 1: Resolve Target Asset

Call `get_crypto_quotes_latest` or `search_cryptos` to identify the target asset.

Required output:
- Asset symbol, name, CMC rank
- Current price in USD
- CMC ID for subsequent calls

The skill supports any asset with CMC data coverage — not limited to major coins.

---

## Step 2: Collect 7-Dimension Evidence

Call the following tools in sequence to build the complete evidence fingerprint.

### Dimension 1 — Price Momentum

Call `get_crypto_quotes_latest` for the target asset.

Extract:
- `percent_change_1h` — short-term direction
- `percent_change_24h` — daily momentum
- `percent_change_7d` — weekly trend
- `percent_change_30d` — monthly structure
- `volume_change_24h` — volume confirmation

Signal rules:
- **BEARISH**: All timeframes negative and accelerating downward
- **BULLISH**: Multiple timeframes positive with volume confirmation
- **NEUTRAL**: Mixed signals across timeframes

Weight: **HIGH**

---

### Dimension 2 — Market Sentiment

Call `get_global_metrics_latest` and extract the Fear & Greed index.

| Value | Label | Implication |
|-------|-------|-------------|
| 0–20 | Extreme Fear | Historically near stage bottoms — NOT an automatic buy |
| 21–40 | Fear | Pessimistic sentiment |
| 41–60 | Neutral | No directional bias |
| 61–80 | Greed | Watch for overheating |
| 81–100 | Extreme Greed | Historically near stage tops |

**Critical rule**: Extreme Fear alone is NOT a buy signal. Combine with decelerating momentum and declining derivatives volume.

Weight: **MEDIUM**

---

### Dimension 3 — Market Breadth

Call `get_crypto_listings_latest` with `limit=10`.

Calculate:
- Number of Top 10 assets declining in 24h
- Average 24h change across Top 10

Classification:
- 9–10 declining → Broad Decline
- 7–8 declining → Mostly Declining
- 4–6 declining → Mixed
- 2–3 declining → Mostly Rising
- 0–1 declining → Broad Rally

Signal rules:
- **BEARISH**: 7+ of Top 10 declining, only stablecoins advancing
- **BULLISH**: 7+ of Top 10 advancing with volume
- **NEUTRAL**: Mixed 4–6 split

Weight: **HIGH**

---

### Dimension 4 — Derivatives Activity

Call `get_global_metrics_latest`. Extract `derivatives_volume_24h` and `derivatives_24h_percentage_change`.

**Note**: This field measures **volume change**, not market cap change.

| Change | Condition | Implication |
|--------|-----------|-------------|
| > +20% | During price decline | Panic deleveraging, bearish acceleration |
| > +10% | During price decline | Elevated bearish activity |
| < -10% | During price decline | Deleveraging complete, potential stabilization |
| > +20% | During price rise | Leveraged long accumulation, watch for squeeze |

Weight: **MEDIUM**

---

### Dimension 5 — BTC Dominance Flow

Call `get_global_metrics_latest`. Extract `btc_dominance` and `btc_dominance_24h_percentage_change`.

| Change | Implication |
|--------|-------------|
| Rising > +0.3% | Capital fleeing altcoins to BTC safety. Bearish for non-BTC |
| Falling < -0.3% | Risk appetite returning. Bullish for altcoins |
| Within ±0.3% | No strong directional capital flow |

Weight: **MEDIUM**

---

### Dimension 6 — Sector Rotation

Call `get_crypto_categories` with `limit=20`. Filter for market cap > $500M. Sort by `avg_price_change`.

Identify top 3 gaining and bottom 3 losing sectors.

Signal rules:
- **BEARISH**: AI, NFT, DeFi, high-beta sectors all in bottom 3
- **BULLISH**: High-beta sectors leading, stablecoins not in top 3
- **NEUTRAL**: Mixed rotation without clear theme

Weight: **LOW** (unless extreme, e.g. leading sector > +5% or < -8%)

---

### Dimension 7 — Stablecoin Flow

Call `get_global_metrics_latest`. Extract `stablecoin_volume_24h` and `stablecoin_24h_percentage_change`.

**Note**: This is **volume** change, not market cap change.

| Volume Change | Implication |
|---------------|-------------|
| > +15% | Heavy safe-haven demand, capital fleeing risk. **Bearish** |
| +5% to +15% | Moderate defensive positioning. Mild bearish |
| < -5% | Capital deploying from stablecoins into risk. **Bullish** |
| Stable | No significant capital repositioning |

Weight: **HIGH** (when > ±15%), **MEDIUM** otherwise

---

## Step 3: Classify Market Regime

Using the 7-dimension evidence, score each of the 5 regimes:

### PANIC SELLOFF
- Fear & Greed < 20: **+3 pts**
- Market cap 24h change < -3%: **+2 pts**
- Derivatives volume change > +20%: **+2 pts**
- Stablecoin volume change > +15%: **+2 pts**
- 9+ of Top 10 declining: **+2 pts**
- BTC dominance rising > +0.3%: **+1 pt**
- Target 7d change < -15%: **+1 pt**

### BEAR TREND
- Fear & Greed 21–35: **+2 pts**
- Market cap 24h change -1% to -3%: **+2 pts**
- 7–8 of Top 10 declining: **+2 pts**
- Target 7d change -8% to -15%: **+2 pts**
- BTC dominance rising: **+1 pt**

### ACCUMULATION
- Fear & Greed < 20 with decelerating decline: **+1 pt**
- Target 30d change < -25%: **+2 pts**
- Derivatives volume change < -10%: **+1 pt**
- Target 7d change < -15%: **+1 pt**

### RECOVERY
- Fear & Greed 61–80: **+1 pt**
- Market cap 24h change > 0%: **+1 pt**
- BTC dominance falling < -0.3%: **+1 pt**
- 3 or fewer of Top 10 declining: **+1 pt**

### BULL TREND
- Fear & Greed > 75: **+2 pts**
- Market cap 24h change > +2%: **+2 pts**
- 2 or fewer of Top 10 declining: **+2 pts**
- Target 7d change > +10%: **+2 pts**
- BTC dominance falling: **+1 pt**

**Select the regime with the highest score.**
**Confidence = (regime score / total score) × 100%**

**Tie-break rule**: When two regimes share the highest score, select the one that aligns with the primary price momentum direction (bearish momentum → prefer BEAR_TREND or PANIC_SELLOFF; bullish momentum → prefer RECOVERY or BULL_TREND).

### Regime Signal Bias

| Regime | Signal Bias | Key Watchpoints |
|--------|-------------|----------------|
| PANIC SELLOFF | Watch for reversal while protecting against continuation | Fear index bottom, derivatives deceleration |
| BEAR TREND | Follow trend short, wait for reversal confirmation | BTC dominance peak, volume exhaustion |
| ACCUMULATION | Light long positions with strict risk control | Volume contraction, higher lows |
| RECOVERY | Trend-following long, take profits at resistance | Volume expansion, sector broadening |
| BULL TREND | Trend-following long, add on dips | Extreme Greed warning, BTC dominance collapse |

---

## Step 4: Three-Court Verdict Process

### COURT I — Claim Court

Before examining all data, state a specific falsifiable claim:

```
Claim: [Asset] will [direction] to [specific price target] within 48 hours
Initial basis: [1-2 observations from preliminary scan]
Falsification conditions:
- [Specific price threshold that invalidates this claim]
- [Specific indicator threshold that invalidates this claim]
- [Specific market condition that invalidates this claim]
```

**Rules:**
- State the claim BEFORE reviewing all 7 dimensions — this prevents post-hoc rationalization
- Must include a specific price target, not just "go up" or "go down"
- The claim is a hypothesis — the final verdict may differ if evidence contradicts it

---

### COURT II — Evidence Court

Review each of the 7 dimensions in sequence. For each dimension:

```
[Dimension Name]
Data: [specific numbers from CMC tools]
Signal: BEARISH / BULLISH / NEUTRAL
Weight: HIGH / MEDIUM / LOW
Reasoning: [one sentence explaining the signal direction]
```

**Required rule**: At least one BULLISH or NEUTRAL item must be presented even in strongly bearish environments. A verdict with 7/7 bearish signals should **reduce** confidence by 10–15% — it suggests a crowded trade.

---

### COURT III — Verdict Court

```
VERDICT: [BEARISH / BULLISH / NEUTRAL]
Confidence: [0–100%]

Market Context:
[1-2 sentences on macro background with specific data points]

Verdict Rationale:
1. [Core reason with specific data]
2. [Core reason with specific data]
3. [Core reason with specific data]

Risk Level: HIGH / MEDIUM / LOW
Risk Reason: [One sentence]

Strategy Specification:
- Entry: [specific price]
- Target 1: [price] ([% from entry])
- Target 2: [price] ([% from entry])
- Stop Loss: [price] ([% from entry])
- Key Support: [price based on data]
- Key Resistance: [price based on data]
- Valid window: 48 hours from [timestamp]

Invalidation Conditions (minimum 4):
1. [Condition with specific threshold]
2. [Condition with specific threshold]
3. [Condition with specific threshold]
4. [Condition with specific threshold]

Appeal Mechanism (24-hour re-review):
Review at [timestamp + 24h]:
1. [Specific data point to check]
2. [Specific data point to check]
3. [Specific data point to check]
```

---

## Step 5: Bull/Bear Intensity Score

After completing the verdict, compute a composite market intensity score (0–100):

```
Base score: 50

Adjustments:
+ (Fear & Greed - 50) × 0.3
- 15 if derivatives_volume_change > 20%
- 8  if derivatives_volume_change > 10%
+ 8  if derivatives_volume_change < -10%
- 12 if stablecoin_volume_change > 15%
- 5  if stablecoin_volume_change > 5%
+ 8  if stablecoin_volume_change < -5%
- (btc_dominance_24h_change × 10)
- (declining_top10_count - 5) × 3
+ target_24h_change × 2

Clamp to [0, 100]
```

Score interpretation:
- 0–40: Bears dominant
- 41–59: Balanced / contested
- 60–100: Bulls dominant

---

## Step 6: Check Macro Events

Query an economic calendar for high-impact US events within the 48-hour verdict window.

Filter for:
- `impact = "high"`
- `country = "US"`
- Event types: FOMC decisions, Non-Farm Payrolls, CPI, GDP

If high-impact events exist within 48 hours:
- Add a macro warning to the verdict output
- Note that the event may override technical signals
- Consider reducing recommended position size in the strategy specification

---

## Step 7: Archive and Verify

Store each verdict for future accuracy tracking:

```json
{
  "verdict_id": "VP-[YYYYMMDDHHMMSS]-[SYMBOL]",
  "symbol": "[ASSET]",
  "timestamp": "[ISO 8601]",
  "market_regime": {
    "regime": "[REGIME_CODE]",
    "confidence_pct": 0,
    "bull_bear_intensity": 0
  },
  "evidence": {},
  "verdict_data": {
    "conclusion": "bearish|bullish|neutral",
    "confidence": 0,
    "entry_price": "",
    "target1": "",
    "target2": "",
    "stoploss": "",
    "valid_until": "",
    "invalidation": [],
    "appeal_points": []
  },
  "outcome": null
}
```

Verification (after 24+ hours):
- **correct**: price moved > 2% in predicted direction
- **incorrect**: price moved > 2% against prediction
- **inconclusive**: price within ±2%

Weight update rule: +0.05 if correct, -0.05 if incorrect (bounded 0.1 to 2.0)

---

## Multi-Asset Comparison Workflow

To compare multiple assets simultaneously:

1. Run Steps 1–5 independently for each asset
2. Rank by opportunity score: `(ACCUMULATION score + RECOVERY score) / total score`
3. Rank by risk score: `(PANIC_SELLOFF score + BEAR_TREND score) / total score`
4. Generate cross-asset synthesis:
   - Overall market environment with specific data points
   - Asset ranking with reasoning for each position
   - Most important asset to watch and why
   - Correlation observations (e.g., if SOL drops more than BTC proportionally, what does that imply?)
   - 48-hour strategic recommendation with specific price levels
   - 2 key triggers to monitor across all assets

---

## Self-Calibrating Signal Weights

Initial weights (all signals start at 1.0):

| Signal | Initial Weight | Range |
|--------|---------------|-------|
| price_momentum | 1.0 | 0.1 – 2.0 |
| sentiment | 1.0 | 0.1 – 2.0 |
| market_breadth | 1.0 | 0.1 – 2.0 |
| derivatives | 1.0 | 0.1 – 2.0 |
| btc_dominance | 1.0 | 0.1 – 2.0 |
| sectors | 1.0 | 0.1 – 2.0 |
| stablecoin | 1.0 | 0.1 – 2.0 |

After each verified verdict, update weights for the **dimensions that contributed to the verdict direction**:
- `outcome = correct` → contributing dimension weights += 0.05 (max 2.0)
- `outcome = incorrect` → contributing dimension weights -= 0.05 (min 0.1)
- Non-contributing dimensions: no change

A dimension "contributes" when its signal aligned with the final verdict conclusion (e.g., if verdict = bearish and dimension signal = bearish, it contributed).

This ensures weights accurately reflect each dimension's individual predictive value over time.

---

## Required CMC Tools

| Tool | Dimensions Served |
|------|------------------|
| `get_crypto_quotes_latest` | Price Momentum, Asset Resolution |
| `get_global_metrics_latest` | Sentiment, Derivatives, BTC Dominance, Stablecoin Flow |
| `get_crypto_listings_latest` | Market Breadth (Top 10) |
| `get_crypto_categories` | Sector Rotation |
| `search_cryptos` | Dynamic asset ID resolution for any token |

---

## Critical Rules

1. **Never use training data prices.** All price references must come from live CMC tool calls. State the data retrieval timestamp explicitly in the verdict.

2. **Falsification before analysis.** The claim in Court I must be stated before reviewing all 7 dimensions.

3. **Require opposing evidence.** Reduce confidence by 10–15% when all 7 dimensions align in the same direction — it suggests a crowded trade.

4. **Volume vs. market cap distinction.** `stablecoin_24h_percentage_change` and `derivatives_24h_percentage_change` measure **volume** change, not market cap or price change. Misinterpreting these fields is the most common error.

5. **Regime before strategy.** Always classify the market regime before constructing strategy specifications.

6. **48-hour validity only.** This skill produces short-term tactical verdicts. Re-run the full workflow for longer timeframes.

7. **Appeal is mandatory.** Every verdict must include a 24-hour appeal mechanism.

8. **Macro events reduce confidence.** When `macro_warning` is present, automatically reduce verdict confidence by 15% and recommend halving the suggested position size. State this explicitly in the verdict output.

9. **Tie-break by momentum.** When regime scores are tied, defer to the primary price momentum direction as the deciding factor.

---

## Example Output

```
VERDICT PROTOCOL — MARKET VERDICT
Asset: BTC  |  2026-06-05 01:15:00 UTC
Market Regime: PANIC SELLOFF (confidence 53.8%)
Bull/Bear Intensity: 28/100 — Bears Dominant

HEADLINE: BTC bearish 75% — extreme fear + derivatives surge signal continuation

COURT I — CLAIM
Claim: BTC will decline to $60,000 within 48 hours from current $63,400
Initial basis: 7-day decline -14.1%, Fear & Greed at 19
Falsification: Price breaks $65,500 / Fear index rises above 30 / Derivatives volume contracts

COURT II — EVIDENCE
[1/7] Price Momentum     BEARISH   HIGH   1H:-0.9%  24H:-3.2%  7D:-14.1%  30D:-22.4%
[2/7] Market Sentiment   BEARISH   MED    Fear & Greed: 19 (Extreme Fear — near stage bottoms)
[3/7] Market Breadth     BEARISH   HIGH   9/10 Top assets declining, avg -2.8%
[4/7] Derivatives        BEARISH   MED    Volume +22.6% — panic deleveraging signal
[5/7] BTC Dominance      BEARISH   MED    Dominance +0.25% — capital fleeing altcoins
[6/7] Sector Rotation    BEARISH   MED    AI -8.7%, NFT -8.0%, Perpetuals -12.3%
[7/7] Stablecoin Flow    NEUTRAL   HIGH   Volume +12.5% — moderate safe-haven demand

Note: 6/7 bearish signals — confidence reduced by 10% to account for crowded trade risk

COURT III — VERDICT
VERDICT: BEARISH  |  Confidence: 75%  |  Risk Level: HIGH

Market Context:
Total crypto market cap $2.19T, down -3.1% in 24H. BTC dominance rising to 57.9%,
indicating systematic capital flight from risk assets.

Verdict Rationale:
1. Price momentum negative across all 4 timeframes — no timeframe showing recovery
2. Derivatives volume surge +22.6% confirms active deleveraging, not stabilization
3. 9/10 Top assets declining — systemic selling, not BTC-specific weakness

Strategy Specification:
Entry: $63,400  |  Target 1: $60,500 (-4.6%)  |  Target 2: $58,500 (-7.7%)
Stop Loss: $65,800 (+3.8%)  |  Valid until: 2026-06-07 01:15:00 UTC

Invalidation Conditions:
1. BTC price breaks above $65,800
2. Fear & Greed rises above 30
3. Derivatives volume 24H change turns negative
4. Stablecoin volume 24H change drops below +5%

Appeal Mechanism (review at 2026-06-06 01:15 UTC):
1. Fear & Greed — if risen to 25+, reduce bearish confidence by 15%
2. Derivatives volume — if declining, potential stabilization signal
3. Stablecoin flow — if decelerating, defensive positioning may be ending
```

---

## Signal-to-Action Protocol

When an AI agent or automated system consumes a Themis verdict, the following execution rules apply:

### Interpreting the Signal

| Field | Value | Recommended Action |
|-------|-------|-------------------|
| `conclusion` | bearish | Consider short position or reduce long exposure |
| `conclusion` | bullish | Consider long position or increase exposure |
| `conclusion` | neutral | Hold current position, await next verdict |
| `confidence` | < 50% | Observe only, no position recommended |
| `confidence` | 50–70% | Standard position (50% of allocated capital) |
| `confidence` | > 70% | Full position (up to 75% of allocated capital) |
| `macro_warning` | present | Halve position size, wait for event resolution |
| `regime` | PANIC_SELLOFF | Widen stop loss, avoid chasing short entries |

### Invalidation Handling

When any `invalidation_condition` threshold is triggered:
1. Exit the position immediately
2. Log the triggered condition and the verdict ID
3. Do NOT re-enter until a new verdict is issued
4. Do NOT override the invalidation condition based on personal judgment

### Risk Parameters

- Maximum loss per verdict: 2% of total portfolio
- Maximum simultaneous open verdicts: 3
- Stop loss price: use `stoploss` field — do not modify
- Position validity: use `valid_until` field — close position if verdict expires without target hit
- When `macro_warning` is present: reduce position to 50% of normal size

### Appeal Mechanism

At `timestamp + 24 hours`, re-evaluate using `appeal_points`. If 2 or more appeal points indicate weakening verdict:
- Reduce position by 50%
- Tighten stop loss to 50% of original range
- If all 3 appeal points indicate reversal: exit fully and await new verdict

---

## Adapting This Skill

**For single-asset deep analysis**: Run the full 7-dimension workflow with 5 appeal points instead of 3.

**For portfolio-level view**: Run multi-asset comparison on any 4 assets of interest.

**For any tradeable asset**: Use `search_cryptos` to resolve the CMC ID dynamically. The skill automatically selects the highest-ranked active asset when multiple tokens share the same symbol.

**For longer timeframes**: Extend the valid window to 96 hours and use 7D/30D momentum as primary signals instead of 1H/24H.

---

*Themis-Verdict implements the Verdict Protocol judicial framework for market analysis.*
*This skill produces structured, falsifiable strategy specifications — not investment advice.*
*All verdicts carry explicit invalidation conditions and must be reviewed through the appeal mechanism.*
*Source: https://github.com/lant1ng-1216/themis-verdict*
