import os, json, time, requests, sys, re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.columns import Columns
from rich import box
from rich.prompt import Prompt, IntPrompt
from rich.align import Align
from rich.rule import Rule

load_dotenv()
CMC_API_KEY = os.getenv("CMC_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
PROXY = os.getenv("PROXY")
proxies = {"http": PROXY, "https": PROXY} if PROXY else None
CMC_BASE = "https://pro-api.coinmarketcap.com"
CMC_HEADERS = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
deepseek = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
console = Console()
LANG = "zh"

T = {
    "zh": {
        "title": "市场裁决系统",
        "subtitle": "P R O T O C O L  —  M A R K E T  C O U R T",
        "select_lang": "选择语言 / Select Language",
        "select_mode": "选择模式",
        "mode1": "单币种裁决",
        "mode2": "多币种对比 (BTC/ETH/BNB/SOL)",
        "mode3": "查看历史准确率",
        "mode4": "退出",
        "enter_symbol": "输入币种 (BTC/ETH/BNB/SOL)",
        "collecting": "正在收集市场数据",
        "connecting": "连接 CoinMarketCap...",
        "fetching_global": "获取全局市场指标...",
        "fetching_sentiment": "获取恐惧贪婪指数...",
        "fetching_coin": "获取实时报价...",
        "fetching_top10": "分析 Top10 市场格局...",
        "fetching_sectors": "扫描板块轮动...",
        "evidence_collected": "证据收集完毕 — 7个维度",
        "regime_detected": "市场状态识别完成",
        "deliberating": "裁决庭审理中",
        "verdict_complete": "裁决完成",
        "saved": "裁决已存档",
        "no_history": "暂无历史裁决记录",
        "accuracy_title": "历史裁决准确率",
        "comparing": "多币种对比裁决进行中",
        "best_opportunity": "最佳机会",
        "highest_risk": "最高风险",
        "evidence_header": "证据审查",
        "regime_header": "市场状态",
        "verdict_header": "最终裁决",
        "claim_header": "庭一：起诉庭",
        "evidence_court": "庭二：证据庭",
        "verdict_court": "庭三：裁决庭",
        "invalidation_header": "失效条件",
        "appeal_header": "上诉机制（24H重审）",
        "bullish": "看多",
        "bearish": "看空",
        "neutral": "中立",
        "confidence": "置信度",
        "target": "目标价",
        "stoploss": "止损价",
        "entry": "入场",
        "valid": "有效至",
        "back": "返回主菜单",
        "press_enter": "按 Enter 继续...",
        "weights_updated": "信号权重已更新",
        "verifying": "验证历史裁决...",
        "verified": "已验证",
        "correct": "正确",
        "incorrect": "错误",
        "inconclusive": "待定",
        "strategy": "策略规格",
        "dim": ["价格动能","市场情绪","市场宽度","衍生品交易量","BTC主导率","板块轮动","稳定币流向"],
        "regime_labels": {
            "PANIC_SELLOFF": "恐慌抛售",
            "BEAR_TREND": "熊市趋势",
            "ACCUMULATION": "底部积累",
            "RECOVERY": "复苏反弹",
            "BULL_TREND": "牛市趋势",
        },
    },
    "en": {
        "title": "Market Verdict System",
        "subtitle": "P R O T O C O L  —  M A R K E T  C O U R T",
        "select_lang": "选择语言 / Select Language",
        "select_mode": "Select Mode",
        "mode1": "Single Asset Verdict",
        "mode2": "Multi-Asset Comparison (BTC/ETH/BNB/SOL)",
        "mode3": "View Historical Accuracy",
        "mode4": "Exit",
        "enter_symbol": "Enter Symbol (BTC/ETH/BNB/SOL)",
        "collecting": "Collecting Market Data",
        "connecting": "Connecting to CoinMarketCap...",
        "fetching_global": "Fetching global metrics...",
        "fetching_sentiment": "Fetching Fear & Greed Index...",
        "fetching_coin": "Fetching live quotes...",
        "fetching_top10": "Analyzing Top10 market structure...",
        "fetching_sectors": "Scanning sector rotation...",
        "evidence_collected": "Evidence collected — 7 dimensions",
        "regime_detected": "Market regime identified",
        "deliberating": "Court deliberating",
        "verdict_complete": "Verdict complete",
        "saved": "Verdict archived",
        "no_history": "No historical verdicts found",
        "accuracy_title": "Historical Verdict Accuracy",
        "comparing": "Multi-asset comparison in progress",
        "best_opportunity": "Best Opportunity",
        "highest_risk": "Highest Risk",
        "evidence_header": "Evidence Review",
        "regime_header": "Market Regime",
        "verdict_header": "Final Verdict",
        "claim_header": "Court I — Claim",
        "evidence_court": "Court II — Evidence",
        "verdict_court": "Court III — Verdict",
        "invalidation_header": "Invalidation Conditions",
        "appeal_header": "Appeal Mechanism (24H Review)",
        "bullish": "BULLISH",
        "bearish": "BEARISH",
        "neutral": "NEUTRAL",
        "confidence": "Confidence",
        "target": "Target",
        "stoploss": "Stop Loss",
        "entry": "Entry",
        "valid": "Valid Until",
        "back": "Back to menu",
        "press_enter": "Press Enter to continue...",
        "weights_updated": "Signal weights updated",
        "verifying": "Verifying historical verdicts...",
        "verified": "Verified",
        "correct": "Correct",
        "incorrect": "Incorrect",
        "inconclusive": "Inconclusive",
        "strategy": "Strategy Spec",
        "dim": ["Price Momentum","Market Sentiment","Market Breadth","Derivatives Volume","BTC Dominance","Sector Rotation","Stablecoin Flow"],
        "regime_labels": {
            "PANIC_SELLOFF": "PANIC SELLOFF",
            "BEAR_TREND": "BEAR TREND",
            "ACCUMULATION": "ACCUMULATION",
            "RECOVERY": "RECOVERY",
            "BULL_TREND": "BULL TREND",
        },
    },
}

def t(key): return T[LANG][key]

SYMBOL_TO_ID = {"BTC": "1", "ETH": "1027", "BNB": "1839", "SOL": "5426"}

BANNER = """
 ████████╗██╗  ██╗███████╗███╗   ███╗██╗███████╗
 ╚══██╔══╝██║  ██║██╔════╝████╗ ████║██║██╔════╝
    ██║   ███████║█████╗  ██╔████╔██║██║███████╗
    ██║   ██╔══██║██╔══╝  ██║╚██╔╝██║██║╚════██║
    ██║   ██║  ██║███████╗██║ ╚═╝ ██║██║███████║
    ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝╚══════╝

         V E R D I C T  —  M A R K E T  C O U R T
"""

def show_banner():
    console.clear()
    console.print(BANNER, style="bold cyan", justify="center")
    console.print(t("subtitle"), style="bold blue", justify="center")
    console.print()

def fetch(endpoint, params=None):
    r = requests.get(f"{CMC_BASE}{endpoint}", headers=CMC_HEADERS, params=params, proxies=proxies, timeout=30)
    return r.json()

def collect_evidence(symbol="BTC"):
    evidence = {}
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    evidence["snapshot_time"] = now
    # 动态解析 coin ID
    coin_id = SYMBOL_TO_ID.get(symbol.upper())
    if not coin_id:
        try:
            map_r = requests.get(
                f"{CMC_BASE}/v1/cryptocurrency/map",
                headers=CMC_HEADERS,
                params={"symbol": symbol.upper(), "limit": 10},
                proxies=proxies,
                timeout=15
            )
            map_data = map_r.json().get("data", [])
            active = [x for x in map_data if x.get("is_active") == 1 and x.get("rank")]
            if active:
                active.sort(key=lambda x: x.get("rank", 9999))
                coin_id = str(active[0]["id"])
                console.print(f"  [dim]→ {symbol.upper()} resolved: {map_data[0]['name']} (rank #{active[0]['rank']})[/]")
            else:
                coin_id = "1"
                console.print(f"  [yellow]⚠ {symbol} not found, defaulting to BTC[/]")
        except:
            coin_id = "1"
    SYMBOL_TO_ID[symbol.upper()] = coin_id

    steps = [
        ("fetching_global", "/v1/global-metrics/quotes/latest", None, "global"),
        ("fetching_sentiment", "/v3/fear-and-greed/latest", None, "sentiment"),
        ("fetching_coin", "/v2/cryptocurrency/quotes/latest", {"id": coin_id, "convert":"USD"}, "coin"),
        ("fetching_top10", "/v1/cryptocurrency/listings/latest", {"limit":10,"convert":"USD"}, "top10"),
        ("fetching_sectors", "/v1/cryptocurrency/categories", {"limit":50}, "sectors"),
    ]
    with Progress(SpinnerColumn(style="cyan"), TextColumn("[cyan]{task.description}"), console=console, transient=True) as progress:
        task = progress.add_task(t("connecting"), total=len(steps))
        for step_key, endpoint, params, key in steps:
            progress.update(task, description=t(step_key))
            time.sleep(0.3)
            try:
                raw = fetch(endpoint, params)
                if key == "global":
                    d = raw["data"]; q = d["quote"]["USD"]
                    evidence["global"] = {
                        "total_market_cap_usd": round(q["total_market_cap"]),
                        "market_cap_24h_change_pct": round(q["total_market_cap_yesterday_percentage_change"],4),
                        "total_volume_24h_usd": round(q["total_volume_24h"]),
                        "volume_24h_change_pct": round(q["total_volume_24h_yesterday_percentage_change"],4),
                        "btc_dominance_pct": round(d["btc_dominance"],4),
                        "btc_dominance_24h_change": round(d["btc_dominance_24h_percentage_change"],4),
                        "eth_dominance_pct": round(d["eth_dominance"],4),
                        "altcoin_market_cap_usd": round(q["altcoin_market_cap"]),
                        "stablecoin_market_cap_usd": round(q["stablecoin_market_cap"]),
                        "stablecoin_volume_24h_usd": round(q["stablecoin_volume_24h"]),
                        "stablecoin_volume_24h_change_pct": round(q["stablecoin_24h_percentage_change"],4),
                        "derivatives_volume_24h_usd": round(q["derivatives_volume_24h"]),
                        "derivatives_volume_24h_change_pct": round(q["derivatives_24h_percentage_change"],4),
                        "defi_volume_24h_usd": round(q["defi_volume_24h"]),
                        "defi_volume_24h_change_pct": round(q["defi_24h_percentage_change"],4),
                        "defi_market_cap_usd": round(q["defi_market_cap"]),
                    }
                elif key == "sentiment":
                    d = raw["data"]; val = d["value"]
                    if val<=20: zone=("极度恐惧，历史上常见于阶段性底部" if LANG=="zh" else "Extreme Fear — historically near stage bottoms")
                    elif val<=40: zone=("恐惧，情绪偏悲观" if LANG=="zh" else "Fear — pessimistic sentiment")
                    elif val<=60: zone=("中性，方向不明" if LANG=="zh" else "Neutral — no clear direction")
                    elif val<=80: zone=("贪婪，注意过热" if LANG=="zh" else "Greed — watch for overheating")
                    else: zone=("极度贪婪，历史上常见于阶段性顶部" if LANG=="zh" else "Extreme Greed — historically near stage tops")
                    evidence["sentiment"] = {"fear_greed_value":val,"fear_greed_label":d["value_classification"],"interpretation":zone,"updated_at":d["update_time"]}
                elif key == "coin":
                    coin_id = SYMBOL_TO_ID.get(symbol,"1")
                    coin = raw["data"][coin_id]; q = coin["quote"]["USD"]
                    evidence["target_coin"] = {
                        "symbol":coin["symbol"],"name":coin["name"],
                        "price_usd":round(q["price"],4),
                        "change_1h_pct":round(q["percent_change_1h"],4),
                        "change_24h_pct":round(q["percent_change_24h"],4),
                        "change_7d_pct":round(q["percent_change_7d"],4),
                        "change_30d_pct":round(q["percent_change_30d"],4),
                        "volume_24h_usd":round(q["volume_24h"]),
                        "volume_change_24h_pct":round(q["volume_change_24h"],4),
                        "market_cap_usd":round(q["market_cap"]),
                        "market_cap_dominance_pct":round(q["market_cap_dominance"],4),
                    }
                elif key == "top10":
                    coins = raw["data"]; top10=[]
                    for c in coins:
                        q=c["quote"]["USD"]
                        top10.append({"rank":c["cmc_rank"],"symbol":c["symbol"],"price_usd":round(q["price"],4),"change_24h_pct":round(q["percent_change_24h"],4),"change_7d_pct":round(q["percent_change_7d"],4),"volume_24h_usd":round(q["volume_24h"]),"market_cap_dominance_pct":round(q["market_cap_dominance"],4)})
                    evidence["top10"]=top10
                    changes=[c["change_24h_pct"] for c in top10]
                    declining=sum(1 for c in changes if c<0)
                    avg=round(sum(changes)/len(changes),4)
                    if LANG=="zh": consensus="全面下跌" if declining>=9 else "多数下跌" if declining>=7 else "分化震荡" if declining>=4 else "多数上涨" if declining>=2 else "全面上涨"
                    else: consensus="Broad Decline" if declining>=9 else "Mostly Declining" if declining>=7 else "Mixed" if declining>=4 else "Mostly Rising" if declining>=2 else "Broad Rally"
                    evidence["market_breadth"]={"top10_declining_count":declining,"top10_advancing_count":10-declining,"top10_avg_24h_change_pct":avg,"market_consensus":consensus}
                elif key == "sectors":
                    sectors=[]
                    for cat in raw["data"]:
                        if cat.get("market_cap",0)>5e8:
                            sectors.append({"name":cat["name"],"market_cap_usd":round(cat.get("market_cap",0)),"market_cap_change_pct":round(cat.get("market_cap_change",0),4),"avg_price_change_pct":round(cat.get("avg_price_change",0),4),"num_tokens":cat.get("num_tokens")})
                    sectors.sort(key=lambda x:x["avg_price_change_pct"],reverse=True)
                    evidence["sectors"]={"top3_gaining":sectors[:3],"top3_losing":sectors[-3:],"total_tracked":len(sectors)}
            except Exception as e:
                evidence[key]={"error":str(e)}
            progress.advance(task)
    console.print(f"  [bold green]✓[/] {t('evidence_collected')}")
    dims = t("dim")
    circles = "①②③④⑤⑥⑦"
    dim_parts = [f"[cyan]{circles[i]}[/] [dim]{d}[/]" for i,d in enumerate(dims)]
    console.print("    " + "  ".join(dim_parts))
    # 宏观事件
    try:
        from datetime import timedelta
        today = datetime.utcnow().strftime("%Y-%m-%d")
        end = (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d")
        r = requests.get(
            f"https://finnhub.io/api/v1/calendar/economic",
            params={"token": FINNHUB_API_KEY},
            proxies=proxies,
            timeout=15
        )
        events = r.json().get("economicCalendar", [])
        high_impact = []
        for ev in events:
            if ev.get("impact") == "high" and ev.get("country") == "US":
                ev_time = ev.get("time", "")
                if today <= ev_time[:10] <= end:
                    high_impact.append({
                        "event": ev.get("event"),
                        "time": ev_time,
                        "country": ev.get("country"),
                        "estimate": ev.get("estimate"),
                        "prev": ev.get("prev"),
                        "impact": ev.get("impact"),
                    })
        high_impact.sort(key=lambda x: x["time"])
        evidence["macro_events"] = high_impact[:5]
    except Exception as e:
        evidence["macro_events"] = []

    return evidence

def load_weights():
    path="weights.json"
    default={"price_momentum":1.0,"sentiment":1.0,"market_breadth":1.0,"derivatives":1.0,"btc_dominance":1.0,"sectors":1.0,"stablecoin":1.0}
    if os.path.exists(path):
        with open(path) as f: saved=json.load(f)
        for k in default:
            if k not in saved: saved[k]=default[k]
        return saved
    return default

def save_weights(weights):
    with open("weights.json","w") as f: json.dump(weights,f,indent=2)

def calc_bull_bear_intensity(evidence):
    """计算多空博弈强度 0-100"""
    score = 50
    fg = evidence.get("sentiment", {}).get("fear_greed_value", 50)
    deriv_change = evidence.get("global", {}).get("derivatives_volume_24h_change_pct", 0)
    stable_change = evidence.get("global", {}).get("stablecoin_volume_24h_change_pct", 0)
    btc_dom_change = evidence.get("global", {}).get("btc_dominance_24h_change", 0)
    breadth = evidence.get("market_breadth", {}).get("top10_declining_count", 5)
    coin_24h = evidence.get("target_coin", {}).get("change_24h_pct", 0)

    # 恐惧贪婪 (越低越偏空)
    score += (fg - 50) * 0.3

    # 衍生品异动 (越高博弈越激烈)
    if deriv_change > 20:
        score -= 15
    elif deriv_change > 10:
        score -= 8
    elif deriv_change < -10:
        score += 8

    # 稳定币流向 (高=资金避险=偏空)
    if stable_change > 15:
        score -= 12
    elif stable_change > 5:
        score -= 5
    elif stable_change < -5:
        score += 8

    # BTC主导率 (上升=避险=偏空)
    score -= btc_dom_change * 10

    # 市场宽度
    score -= (breadth - 5) * 3

    # 24H价格动能
    score += coin_24h * 2

    score = max(0, min(100, score))
    return round(score, 1)

def classify_market_regime(evidence, weights):
    fg=evidence.get("sentiment",{}).get("fear_greed_value",50)
    mc=evidence.get("global",{}).get("market_cap_24h_change_pct",0)
    dc=evidence.get("global",{}).get("derivatives_volume_24h_change_pct",0)
    bc=evidence.get("global",{}).get("btc_dominance_24h_change",0)
    sc=evidence.get("global",{}).get("stablecoin_volume_24h_change_pct",0)
    breadth=evidence.get("market_breadth",{}).get("top10_declining_count",5)
    c7=evidence.get("target_coin",{}).get("change_7d_pct",0)
    c30=evidence.get("target_coin",{}).get("change_30d_pct",0)
    scores={"PANIC_SELLOFF":0,"BEAR_TREND":0,"ACCUMULATION":0,"RECOVERY":0,"BULL_TREND":0}
    w=weights
    if fg<20: scores["PANIC_SELLOFF"]+=3*w["sentiment"]; scores["ACCUMULATION"]+=1*w["sentiment"]
    elif fg<35: scores["BEAR_TREND"]+=2*w["sentiment"]
    elif fg>75: scores["BULL_TREND"]+=2*w["sentiment"]
    elif fg>60: scores["RECOVERY"]+=1*w["sentiment"]
    if mc<-3: scores["PANIC_SELLOFF"]+=2*w["price_momentum"]
    elif mc<-1: scores["BEAR_TREND"]+=2*w["price_momentum"]
    elif mc>2: scores["BULL_TREND"]+=2*w["price_momentum"]
    elif mc>0: scores["RECOVERY"]+=1*w["price_momentum"]
    if dc>20: scores["PANIC_SELLOFF"]+=2*w["derivatives"]
    elif dc>10: scores["BEAR_TREND"]+=1*w["derivatives"]
    elif dc<-10: scores["ACCUMULATION"]+=1*w["derivatives"]
    if sc>15: scores["PANIC_SELLOFF"]+=2*w["stablecoin"]
    elif sc>5: scores["BEAR_TREND"]+=1*w["stablecoin"]
    if bc>0.3: scores["PANIC_SELLOFF"]+=1*w["btc_dominance"]; scores["BEAR_TREND"]+=1*w["btc_dominance"]
    elif bc<-0.3: scores["BULL_TREND"]+=1*w["btc_dominance"]; scores["RECOVERY"]+=1*w["btc_dominance"]
    if breadth>=9: scores["PANIC_SELLOFF"]+=2*w["market_breadth"]
    elif breadth>=7: scores["BEAR_TREND"]+=2*w["market_breadth"]
    elif breadth<=2: scores["BULL_TREND"]+=2*w["market_breadth"]
    elif breadth<=4: scores["RECOVERY"]+=1*w["market_breadth"]
    if c7<-15: scores["PANIC_SELLOFF"]+=1*w["price_momentum"]; scores["ACCUMULATION"]+=1*w["price_momentum"]
    elif c7<-8: scores["BEAR_TREND"]+=2*w["price_momentum"]
    elif c7>10: scores["BULL_TREND"]+=2*w["price_momentum"]
    if c30<-25: scores["ACCUMULATION"]+=2*w["price_momentum"]
    elif c30<-15: scores["BEAR_TREND"]+=1*w["price_momentum"]
    regime=max(scores,key=scores.get)
    total=sum(scores.values())
    confidence=round(scores[regime]/total*100,1) if total>0 else 0
    regime_info={
        "PANIC_SELLOFF":{"zh":{"desc":"市场极度恐惧，集体错误正在发生","bias":"警惕继续下行，关注超卖反弹窗口"},"en":{"desc":"Extreme fear — collective mistakes occurring","bias":"Watch for continued decline, monitor oversold bounce"},"color":"red","icon":"🔴"},
        "BEAR_TREND":{"zh":{"desc":"趋势性下跌，空头占优，反弹均为做空机会","bias":"顺势看空，等待趋势反转确认"},"en":{"desc":"Trending lower — bears dominant","bias":"Trend-following short, wait for reversal confirmation"},"color":"red","icon":"🔻"},
        "ACCUMULATION":{"zh":{"desc":"价格低迷但下跌动能衰竭，聪明资金可能静默建仓","bias":"轻仓试多，严格风控"},"en":{"desc":"Depressed prices, declining momentum","bias":"Light long positions, strict risk control"},"color":"yellow","icon":"🟡"},
        "RECOVERY":{"zh":{"desc":"市场从低位恢复，风险偏好回升","bias":"顺势做多，设好止盈止损"},"en":{"desc":"Recovering from lows, risk appetite returning","bias":"Trend-following long, set take-profit and stop-loss"},"color":"green","icon":"🟢"},
        "BULL_TREND":{"zh":{"desc":"趋势性上涨，多头占优，回调是加仓机会","bias":"顺势做多，回调加仓"},"en":{"desc":"Trending higher — bulls dominant","bias":"Trend-following long, add on dips"},"color":"green","icon":"🚀"},
    }
    info=regime_info[regime]
    intensity = calc_bull_bear_intensity(evidence)
    return {"regime":regime,"label":t("regime_labels")[regime],"confidence_pct":confidence,"description":info[LANG]["desc"],"signal_bias":info[LANG]["bias"],"color":info["color"],"icon":info["icon"],"all_scores":{k:round(v,2) for k,v in scores.items()},"bull_bear_intensity":intensity}

def render_regime_panel(regime):
    bar_filled=int(regime["confidence_pct"]/10)
    bar="█"*bar_filled+"░"*(10-bar_filled)
    color=regime["color"]
    content=(f"{regime['icon']}  [bold {color}]{regime['label']}[/]\n\n"
             f"[white]{regime['description']}[/]\n\n"
             f"[dim]{t('confidence')}:[/]  [{color}]{bar}[/]  [bold]{regime['confidence_pct']}%[/]\n\n"
             f"[dim italic]{regime['signal_bias']}[/]")
    console.print(Panel(content,title=f"[bold cyan]{t('regime_header')}[/]",border_style="cyan",padding=(1,2)))

def render_evidence_table(evidence):
    console.print()
    console.rule(f"[bold cyan]⚖  {t('evidence_court')}[/]")
    console.print()
    coin=evidence.get("target_coin",{})
    global_d=evidence.get("global",{})
    fg=evidence.get("sentiment",{}).get("fear_greed_value",50)
    breadth=evidence.get("market_breadth",{}).get("top10_declining_count",5)
    dc=global_d.get("derivatives_volume_24h_change_pct",0)
    bc=global_d.get("btc_dominance_24h_change",0)
    sc=global_d.get("stablecoin_volume_24h_change_pct",0)
    sectors=evidence.get("sectors",{})
    top_lose=sectors.get("top3_losing",[{}])
    worst=top_lose[0].get("avg_price_change_pct",0) if top_lose else 0

    rows=[
        (t("dim")[0], coin.get("change_24h_pct",0), f"1H:{coin.get('change_1h_pct',0):+.2f}%  24H:{coin.get('change_24h_pct',0):+.2f}%  7D:{coin.get('change_7d_pct',0):+.2f}%  30D:{coin.get('change_30d_pct',0):+.2f}%", "price"),
        (t("dim")[1], fg, f"F&G Index: {fg}  ({evidence.get('sentiment',{}).get('fear_greed_label','')})", "sentiment"),
        (t("dim")[2], breadth, f"{t('market_breadth') if False else breadth}/10 declining  avg: {evidence.get('market_breadth',{}).get('top10_avg_24h_change_pct',0):+.2f}%  [{evidence.get('market_breadth',{}).get('market_consensus','')}]", "breadth"),
        (t("dim")[3], dc, f"Derivatives Vol 24H: {dc:+.2f}%  (${global_d.get('derivatives_volume_24h_usd',0)/1e12:.2f}T)", "deriv"),
        (t("dim")[4], bc, f"BTC Dom: {global_d.get('btc_dominance_pct',0):.2f}%  24H change: {bc:+.4f}%", "btcdom"),
        (t("dim")[5], worst, f"Top losing: {top_lose[0].get('name','') if top_lose else ''}  {worst:+.2f}%", "sector"),
        (t("dim")[6], sc, f"Stablecoin Vol 24H change: {sc:+.2f}%  (${global_d.get('stablecoin_volume_24h_usd',0)/1e9:.1f}B)", "stable"),
    ]

    def get_signal(key, val):
        if key=="price": return ("bearish" if val<-1 else "bullish" if val>1 else "neutral")
        if key=="sentiment": return ("bearish" if val<35 else "bullish" if val>65 else "neutral")
        if key=="breadth": return ("bearish" if val>=7 else "bullish" if val<=3 else "neutral")
        if key=="deriv": return ("bearish" if val>15 else "neutral")
        if key=="btcdom": return ("bearish" if val>0.2 else "bullish" if val<-0.2 else "neutral")
        if key=="sector": return ("bearish" if val<-5 else "bullish" if val>3 else "neutral")
        if key=="stable": return ("bearish" if val>15 else "neutral")
        return "neutral"

    def get_weight(key, signal):
        high_keys={"price","breadth","stable"}
        low_keys={"btcdom","sector"}
        if key in high_keys: return "HIGH"
        if key in low_keys: return "MED"
        return "MED"

    table=Table(box=box.SIMPLE_HEAVY, border_style="cyan", show_header=True, header_style="bold cyan", padding=(0,1))
    table.add_column("#", width=3, style="dim")
    table.add_column(t("evidence_header") if False else "Dimension", width=18)
    table.add_column("Signal", width=12)
    table.add_column("Wt", width=5)
    table.add_column("Key Data", width=55)

    signal_display={
        "bearish": {"zh":"看空 ⬇","en":"BEARISH ⬇","color":"red"},
        "bullish": {"zh":"看多 ⬆","en":"BULLISH ⬆","color":"green"},
        "neutral": {"zh":"中立 ➡","en":"NEUTRAL ➡","color":"yellow"},
    }
    weight_colors={"HIGH":"red","MED":"yellow","LOW":"dim"}

    for i,(dim,val,detail,key) in enumerate(rows,1):
        sig=get_signal(key,val)
        wt=get_weight(key,sig)
        sd=signal_display[sig]
        sig_text=f"[{sd['color']}]{sd[LANG]}[/]"
        wt_text=f"[{weight_colors[wt]}]{wt}[/]"
        table.add_row(str(i), dim, sig_text, wt_text, f"[dim]{detail}[/]")
        time.sleep(0.1)

    console.print(Align.center(table))
    console.print()

def run_verdict_ai(symbol, evidence, regime, accuracy_stats=None):
    now=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    price=evidence.get("target_coin",{}).get("price_usd","N/A")
    lang_note="Output ONLY valid JSON, no markdown, no explanation. Use Chinese for all text fields." if LANG=="zh" else "Output ONLY valid JSON, no markdown, no explanation. Use English for all text fields."
    acc=""
    if accuracy_stats and accuracy_stats.get("accuracy_pct") is not None:
        acc=f"\nSystem historical accuracy: {accuracy_stats['accuracy_pct']}% ({accuracy_stats['correct']} correct / {accuracy_stats['correct']+accuracy_stats['incorrect']} verified)\n"

    prompt=f"""You are the Chief Market Verdict Officer of Verdict Protocol.

STRICT RULES:
- Current time: {now}
- {symbol} current price: ${price} (ONLY valid price)
- All numbers MUST come from the evidence below
- All dates MUST be calculated from {now}
{acc}

MARKET REGIME: {regime['label']} (confidence {regime['confidence_pct']}%)
{regime['description']}

REAL-TIME EVIDENCE:
{json.dumps(evidence, indent=2, ensure_ascii=False)}

UPCOMING MACRO EVENTS (next 48h, high impact only):
{json.dumps(evidence.get("macro_events", []), indent=2, ensure_ascii=False)}

OUTPUT ONLY THIS JSON STRUCTURE (no markdown fences, no extra text):
{{
  "claim": "one sentence directional claim with price target based on ${price}",
  "claim_basis": "2-3 sentences citing specific numbers from evidence",
  "falsification": ["condition 1 with specific value", "condition 2", "condition 3"],
  "evidence_summary": [
    {{"dim": "dimension name", "signal": "bearish|bullish|neutral", "weight": "HIGH|MED|LOW", "detail": "one line with specific data"}},
    {{"dim": "dimension name", "signal": "bearish|bullish|neutral", "weight": "HIGH|MED|LOW", "detail": "one line with specific data"}},
    {{"dim": "dimension name", "signal": "bearish|bullish|neutral", "weight": "HIGH|MED|LOW", "detail": "one line with specific data"}},
    {{"dim": "dimension name", "signal": "bearish|bullish|neutral", "weight": "HIGH|MED|LOW", "detail": "one line with specific data"}},
    {{"dim": "dimension name", "signal": "bearish|bullish|neutral", "weight": "HIGH|MED|LOW", "detail": "one line with specific data"}},
    {{"dim": "dimension name", "signal": "bearish|bullish|neutral", "weight": "HIGH|MED|LOW", "detail": "one line with specific data"}},
    {{"dim": "dimension name", "signal": "bearish|bullish|neutral", "weight": "HIGH|MED|LOW", "detail": "one line with specific data"}}
  ],
  "conclusion": "bearish|bullish|neutral",
  "confidence": 75,
  "entry_price": "{price}",
  "target1": "price as string e.g. $60000",
  "target2": "price as string e.g. $58000",
  "stoploss": "price as string e.g. $65000",
  "valid_until": "datetime string 48h from {now}",
  "invalidation": ["condition 1 with specific value", "condition 2", "condition 3", "condition 4"],
  "appeal_points": ["review point 1", "review point 2", "review point 3"],
  "market_context": "1-2 sentence macro background summary citing specific data",
  "verdict_reasons": ["core reason 1 with specific data", "core reason 2 with specific data", "core reason 3 with specific data"],
  "risk_level": "HIGH|MEDIUM|LOW",
  "risk_reason": "one sentence explaining the risk level",
  "headline": "one punchy telegraph-style summary under 20 words: direction, confidence%, key driver",
  "price_levels": {{
    "current": "{price}",
    "target1": "price string",
    "target2": "price string",
    "stoploss": "price string",
    "key_support": "price string based on data",
    "key_resistance": "price string based on data"
  }},
  "macro_warning": "null or one sentence warning if macro events in next 48h could impact the verdict. IMPORTANT: if macro_warning is not null, reduce confidence by 15% and note recommended position size is halved."
}}

{lang_note}"""

    with console.status(f"[bold cyan]⚖  {t('deliberating')}...[/]", spinner="dots"):
        response=deepseek.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role":"system","content":f"You are a strict market verdict officer. Current time: {now}. Output ONLY valid JSON. No markdown. No extra text."},
                {"role":"user","content":prompt}
            ],
            temperature=0.1,
        )
    raw=response.choices[0].message.content.strip()
    raw=re.sub(r"```json|```","",raw).strip()
    try:
        return json.loads(raw)
    except:
        return {"claim":"—","claim_basis":"—","falsification":[],"evidence_summary":[],"conclusion":"neutral","confidence":50,"entry_price":str(price),"target1":"—","target2":"—","stoploss":"—","valid_until":"—","invalidation":[],"appeal_points":[],"raw":raw}

def render_verdict(vdata, symbol):
    # 电报式摘要
    headline = vdata.get("headline", "")
    if headline:
        console.print()
        console.print(Panel(
            f"[bold yellow]⚡  {headline}[/]",
            border_style="yellow", padding=(0,2)
        ))

    conclusion=vdata.get("conclusion","neutral")
    confidence=vdata.get("confidence",50)
    if conclusion=="bearish": color="red"; icon="📉"; label=t("bearish")
    elif conclusion=="bullish": color="green"; icon="📈"; label=t("bullish")
    else: color="yellow"; icon="⚖"; label=t("neutral")

    bar_filled=int(confidence/10)
    bar="█"*bar_filled+"░"*(10-bar_filled)

    # Court I
    console.print()
    console.print(Panel(
        f"[bold white]{vdata.get('claim','—')}[/]\n\n"
        f"[dim]{vdata.get('claim_basis','—')}[/]\n\n"
        f"[cyan]{'证伪条件' if LANG=='zh' else 'Falsification'}:[/]\n"
        +"\n".join(f"  [dim]• {c}[/]" for c in vdata.get("falsification",[])),
        title=f"[bold cyan]{t('claim_header')}[/]",
        border_style="blue", padding=(1,2)
    ))

    # Court II — structured table
    console.print()
    console.rule(f"[bold cyan]{t('evidence_court')}[/]")
    console.print()
    ev_table=Table(box=box.SIMPLE_HEAVY, border_style="cyan", show_header=True, header_style="bold cyan", padding=(0,1))
    ev_table.add_column("#", width=3, style="dim")
    ev_table.add_column("Dimension", width=20)
    ev_table.add_column("Signal", width=12)
    ev_table.add_column("Wt", width=5)
    ev_table.add_column("Analysis", width=52)
    signal_display={"bearish":{"zh":"看空 ⬇","en":"BEARISH ⬇","color":"red"},"bullish":{"zh":"看多 ⬆","en":"BULLISH ⬆","color":"green"},"neutral":{"zh":"中立 ➡","en":"NEUTRAL ➡","color":"yellow"}}
    weight_colors={"HIGH":"red","MED":"yellow","LOW":"dim"}
    for i,ev in enumerate(vdata.get("evidence_summary",[]),1):
        sig=ev.get("signal","neutral")
        wt=ev.get("weight","MED")
        sd=signal_display.get(sig,signal_display["neutral"])
        ev_table.add_row(
            str(i), ev.get("dim","—"),
            f"[{sd['color']}]{sd[LANG]}[/]",
            f"[{weight_colors.get(wt,'dim')}]{wt}[/]",
            f"[dim]{ev.get('detail','—')}[/]"
        )
    console.print(Align.center(ev_table))

    # Court III — verdict
    console.print()
    console.rule(f"[bold {color}]⚖  {t('verdict_court')}[/]")
    console.print()

    # 市场背景
    market_context = vdata.get("market_context","")
    if market_context:
        console.print(Panel(
            f"[dim]{market_context}[/]",
            title="[bold cyan]市场背景 / Market Context[/]",
            border_style="dim", padding=(0,2)
        ))
        console.print()

    # 裁决理由
    reasons = vdata.get("verdict_reasons",[])
    if reasons:
        console.print(f"  [bold cyan]{'裁决理由' if LANG=='zh' else 'Verdict Rationale'}[/]")
        for i,r in enumerate(reasons,1):
            console.print(f"  [{'red' if conclusion=='bearish' else 'green' if conclusion=='bullish' else 'yellow'}]{i}.[/] {r}")
        console.print()

    # 风险等级
    risk_level = vdata.get("risk_level","MEDIUM")
    risk_reason = vdata.get("risk_reason","")
    risk_colors = {"HIGH":"red","MEDIUM":"yellow","LOW":"green"}
    risk_icons = {"HIGH":"🔴","MEDIUM":"🟡","LOW":"🟢"}
    rc = risk_colors.get(risk_level,"yellow")
    ri = risk_icons.get(risk_level,"🟡")
    risk_label = {"HIGH":("高风险" if LANG=="zh" else "HIGH RISK"),"MEDIUM":("中等风险" if LANG=="zh" else "MEDIUM RISK"),"LOW":("低风险" if LANG=="zh" else "LOW RISK")}.get(risk_level,"MEDIUM")

    # Main verdict panel
    verdict_main=(
        f"{icon}  [bold {color}]{label}[/]   "
        f"[dim]{t('confidence')}:[/] [{color}]{bar}[/] [bold]{confidence}%[/]   "
        f"{ri} [bold {rc}]{risk_label}[/]"
    )
    console.print(Panel(verdict_main, border_style=color, padding=(1,2)))
    if risk_reason:
        console.print(f"  [dim]{risk_reason}[/]")
        console.print()

    # Strategy row
    entry=vdata.get("entry_price","—")
    t1=vdata.get("target1","—")
    t2=vdata.get("target2","—")
    sl=vdata.get("stoploss","—")
    valid=vdata.get("valid_until","—")

    strat_table=Table(box=box.SIMPLE, show_header=False, padding=(0,2), border_style="dim")
    strat_table.add_column("Label", style="dim", width=12)
    strat_table.add_column("Value", style="bold white", width=18)
    strat_table.add_column("Label2", style="dim", width=12)
    strat_table.add_column("Value2", style="bold white", width=18)
    strat_table.add_row(t("entry"), f"[cyan]{entry}[/]", t("target")+" 1", f"[{color}]{t1}[/]")
    strat_table.add_row(t("stoploss"), f"[red]{sl}[/]", t("target")+" 2", f"[{color}]{t2}[/]")
    strat_table.add_row(t("valid"), f"[dim]{valid}[/]", "", "")
    console.print(Align.center(strat_table))

    # 关键价格警戒线
    price_levels = vdata.get("price_levels", {})
    if price_levels:
        console.print()
        console.print(f"  [bold cyan]{'关键价格区间' if LANG=='zh' else 'Key Price Levels'}[/]")
        try:
            cur = float(str(price_levels.get("current","0")).replace("$","").replace(",",""))
            levels = [
                ("key_resistance", "resistance" if LANG=="en" else "关键阻力", "red", "▲"),
                ("stoploss", "stop loss" if LANG=="en" else "止损位", "red", "✕"),
                ("current", "current" if LANG=="en" else "当前价", "white", "●"),
                ("target1", "target 1" if LANG=="en" else "目标1", "green", "✓"),
                ("target2", "target 2" if LANG=="en" else "目标2", "green", "✓"),
                ("key_support", "support" if LANG=="en" else "关键支撑", "green", "▼"),
            ]
            for key, label, lcolor, sym in levels:
                val_str = str(price_levels.get(key, "—")).replace("$","").replace(",","")
                try:
                    val = float(val_str)
                    pct = (val - cur) / cur * 100
                    pct_str = f"[dim]({pct:+.2f}%)[/]"
                except:
                    pct_str = ""
                console.print(f"  [{lcolor}]{sym}[/] [dim]{label}:[/] [bold {lcolor}]${val_str}[/]  {pct_str}")
        except:
            pass

    # 宏观警告
    macro_warning = vdata.get("macro_warning")
    if macro_warning and macro_warning.lower() != "null":
        macro_warn_label = "宏观事件警告" if LANG=="zh" else "Macro Event Warning"
        console.print()
        console.print(Panel(
            f"[bold yellow]⚠  {macro_warn_label}[/]\n{macro_warning}",
            border_style="yellow", padding=(0,2)
        ))
    # 历史相似案例
    similar = find_similar_verdicts(symbol, vdata.get("conclusion","neutral"))
    if similar:
        console.print()
        console.print(f"  [bold cyan]{'历史相似案例' if LANG=='zh' else 'Similar Historical Cases'}[/]")
        for s in similar:
            rc = "green" if s["result"]=="correct" else "red" if s["result"]=="incorrect" else "yellow"
            console.print(
                f"  [dim]{s['verdict_id']}[/]  [{s['regime_color']}]{s['regime']}[/]  "
                f"[dim]→[/] [{rc}]{t(s['result'])}[/]  "
                f"[dim]{s['price_change']:+.2f}%  ({s['hours_ago']:.0f}h ago)[/]"
            )

    # Invalidation
    console.print()
    console.print(f"  [bold cyan]{t('invalidation_header')}[/]")
    for i,cond in enumerate(vdata.get("invalidation",[]),1):
        console.print(f"  [dim]{i}.[/] {cond}")

    # Appeal
    console.print()
    console.print(f"  [bold cyan]{t('appeal_header')}[/]")
    for i,pt in enumerate(vdata.get("appeal_points",[]),1):
        console.print(f"  [dim]{i}.[/] [dim]{pt}[/]")
    console.print()

def find_similar_verdicts(symbol, current_conclusion, max_results=3):
    """找历史相似案例"""
    verdicts_dir = "verdicts"
    if not os.path.exists(verdicts_dir):
        return []
    results = []
    for filename in sorted(os.listdir(verdicts_dir), reverse=True):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(verdicts_dir, filename)
        try:
            with open(path) as f:
                record = json.load(f)
        except:
            continue
        if record.get("symbol") != symbol:
            continue
        outcome = record.get("outcome")
        if not outcome:
            continue
        vdata = record.get("verdict_data", {})
        if not isinstance(vdata, dict):
            continue
        conclusion = vdata.get("conclusion", "")
        if conclusion != current_conclusion:
            continue
        regime = record.get("market_regime", {})
        regime_color = regime.get("color", "white") if isinstance(regime, dict) else "white"
        regime_label = regime.get("label", "—") if isinstance(regime, dict) else "—"
        results.append({
            "verdict_id": record.get("verdict_id", "—"),
            "regime": regime_label,
            "regime_color": regime_color,
            "result": outcome.get("result", "inconclusive"),
            "price_change": outcome.get("price_change_pct", 0),
            "hours_ago": outcome.get("hours_elapsed", 0),
        })
        if len(results) >= max_results:
            break
    return results

def verify_past_verdicts(symbol="BTC"):
    verdicts_dir="verdicts"
    if not os.path.exists(verdicts_dir): return []
    results=[]; now=datetime.utcnow()
    for filename in sorted(os.listdir(verdicts_dir)):
        if not filename.endswith(".json"): continue
        path=os.path.join(verdicts_dir,filename)
        with open(path) as f: record=json.load(f)
        if record.get("symbol")!=symbol or record.get("outcome") is not None: continue
        verdict_time=datetime.fromisoformat(record["timestamp"].replace("Z",""))
        hours=(now-verdict_time).total_seconds()/3600
        if hours<24: continue
        try:
            coin_id=SYMBOL_TO_ID.get(symbol,"1")
            d=fetch("/v2/cryptocurrency/quotes/latest",{"id":coin_id,"convert":"USD"})
            current_price=round(d["data"][coin_id]["quote"]["USD"]["price"],4)
        except: continue
        entry_price=record.get("evidence",{}).get("target_coin",{}).get("price_usd")
        if not entry_price: continue
        change_pct=round((current_price-entry_price)/entry_price*100,4)
        vdata=record.get("verdict_data",{})
        conclusion=vdata.get("conclusion","") if isinstance(vdata,dict) else ""
        if not conclusion:
            vtext=record.get("verdict","")
            if any(w in vtext for w in ["看空","BEARISH","bearish"]): conclusion="bearish"
            elif any(w in vtext for w in ["看多","BULLISH","bullish"]): conclusion="bullish"
            else: conclusion="neutral"
        if conclusion=="bearish": result="correct" if change_pct<-2 else "incorrect" if change_pct>2 else "inconclusive"
        elif conclusion=="bullish": result="correct" if change_pct>2 else "incorrect" if change_pct<-2 else "inconclusive"
        else: result="inconclusive"
        weights=load_weights(); delta=0.05
        # Get contributing dimensions from evidence summary
        evidence_summary = record.get("verdict_data", {})
        if isinstance(evidence_summary, dict):
            ev_list = evidence_summary.get("evidence_summary", [])
        else:
            ev_list = []
        verdict_conclusion = conclusion
        # Map dimension names to weight keys
        dim_key_map = {
            "price momentum": "price_momentum",
            "market sentiment": "sentiment",
            "market breadth": "market_breadth",
            "derivatives": "derivatives",
            "btc dominance": "btc_dominance",
            "sector rotation": "sectors",
            "stablecoin": "stablecoin",
        }
        contributing_keys = set()
        for ev in ev_list:
            sig = ev.get("signal", "").lower()
            dim = ev.get("dim", "").lower()
            if sig == verdict_conclusion:
                for keyword, key in dim_key_map.items():
                    if keyword in dim:
                        contributing_keys.add(key)
        # If we can't determine contributing dims, fall back to all
        if not contributing_keys:
            contributing_keys = set(weights.keys())
        for k in weights:
            if k not in contributing_keys:
                continue
            if result=="correct": weights[k]=round(min(2.0,weights[k]+delta),3)
            elif result=="incorrect": weights[k]=round(max(0.1,weights[k]-delta),3)
        save_weights(weights)
        record["outcome"]={"verified_at":now.isoformat()+"Z","entry_price":entry_price,"current_price":current_price,"price_change_pct":change_pct,"verdict_direction":conclusion,"result":result,"hours_elapsed":round(hours,1)}
        with open(path,"w") as f: json.dump(record,f,ensure_ascii=False,indent=2)
        results.append(record["outcome"])
        rc="green" if result=="correct" else "red" if result=="incorrect" else "yellow"
        console.print(f"  [cyan]{t('verified')}[/] {record['verdict_id']} → [{rc}]{t(result)}[/]  ({change_pct:+.2f}%)")
    return results

def get_accuracy_stats(symbol="BTC"):
    verdicts_dir="verdicts"
    if not os.path.exists(verdicts_dir): return None
    total=correct=incorrect=inconclusive=0
    for filename in os.listdir(verdicts_dir):
        if not filename.endswith(".json"): continue
        with open(os.path.join(verdicts_dir,filename)) as f: record=json.load(f)
        if record.get("symbol")!=symbol or not record.get("outcome"): continue
        total+=1; r=record["outcome"].get("result")
        if r=="correct": correct+=1
        elif r=="incorrect": incorrect+=1
        else: inconclusive+=1
    if total==0: return None
    return {"total_verdicts":total,"correct":correct,"incorrect":incorrect,"inconclusive":inconclusive,"accuracy_pct":round(correct/(correct+incorrect)*100,1) if (correct+incorrect)>0 else None}

def save_verdict_record(verdict_id, symbol, evidence, regime, vdata):
    os.makedirs("verdicts",exist_ok=True)
    record={"verdict_id":verdict_id,"symbol":symbol,"language":LANG,"timestamp":datetime.utcnow().isoformat()+"Z","market_regime":regime,"evidence":evidence,"verdict_data":vdata,"outcome":None}
    path=f"verdicts/{verdict_id}.json"
    with open(path,"w") as f: json.dump(record,f,ensure_ascii=False,indent=2)
    console.print(f"\n  [dim]📁 {t('saved')}: {path}[/]")

def single_verdict(symbol):
    verdict_id=f"VP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{symbol}"
    console.print(); console.rule(f"[bold cyan]Case ID: {verdict_id}[/]")
    console.print(f"  [dim]{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}[/]\n")
    with console.status(f"[cyan]{t('verifying')}[/]",spinner="dots"): verified=verify_past_verdicts(symbol)
    if not verified: console.print(f"  [dim]{t('no_history')}[/]")
    accuracy_stats=get_accuracy_stats(symbol)
    if accuracy_stats and accuracy_stats.get("accuracy_pct") is not None:
        ac=accuracy_stats["accuracy_pct"]
        ac_color="green" if ac>=60 else "yellow" if ac>=40 else "red"
        console.print(f"\n  [dim]{t('accuracy_title')}:[/] [{ac_color}]{ac}%[/] ([green]{accuracy_stats['correct']}✓[/] [red]{accuracy_stats['incorrect']}✗[/] [yellow]{accuracy_stats['inconclusive']}?[/])")
    console.print()
    weights=load_weights()
    evidence=collect_evidence(symbol)
    regime=classify_market_regime(evidence,weights)
    render_regime_panel(regime)
    vdata=run_verdict_ai(symbol,evidence,regime,accuracy_stats)
    render_verdict(vdata,symbol)
    save_verdict_record(verdict_id,symbol,evidence,regime,vdata)

def multi_verdict():
    symbols=["BTC","ETH","BNB","SOL"]
    console.print(); console.rule(f"[bold cyan]{t('comparing')}[/]")
    results=[]; weights=load_weights()
    for sym in symbols:
        console.print(f"\n  [cyan]▶ {sym}...[/]")
        evidence=collect_evidence(sym)
        regime=classify_market_regime(evidence,weights)
        results.append({"symbol":sym,"price":evidence.get("target_coin",{}).get("price_usd","—"),"change_7d":evidence.get("target_coin",{}).get("change_7d_pct",0),"change_30d":evidence.get("target_coin",{}).get("change_30d_pct",0),"regime":regime,"evidence":evidence})
    console.print(); console.rule("[bold cyan]MULTI-ASSET VERDICT COMPARISON[/]"); console.print()
    table=Table(box=box.DOUBLE_EDGE,border_style="cyan",show_header=True,header_style="bold cyan")
    table.add_column("Asset",style="bold white",width=8)
    table.add_column("Price",width=12)
    table.add_column("7D",width=8)
    table.add_column("30D",width=8)
    table.add_column("Regime",width=20)
    table.add_column("Conf",width=8)
    for r in results:
        reg=r["regime"]; c=reg["color"]
        c7=r["change_7d"]; c30=r["change_30d"]
        table.add_row(f"[bold]{r['symbol']}[/]",f"${r['price']:,}" if isinstance(r['price'],(int,float)) else str(r['price']),f"[{'red' if c7<0 else 'green'}]{c7:+.1f}%[/]",f"[{'red' if c30<0 else 'green'}]{c30:+.1f}%[/]",f"[{c}]{reg['icon']} {reg['label']}[/]",f"[{c}]{reg['confidence_pct']}%[/]")
    console.print(Align.center(table))
    best=sorted(results,key=lambda x:x["regime"]["all_scores"].get("ACCUMULATION",0)+x["regime"]["all_scores"].get("RECOVERY",0),reverse=True)[0]
    worst=sorted(results,key=lambda x:x["regime"]["all_scores"].get("PANIC_SELLOFF",0)+x["regime"]["all_scores"].get("BEAR_TREND",0),reverse=True)[0]
    console.print(f"\n  [bold green]▲ {t('best_opportunity')}:[/] [bold]{best['symbol']}[/] — {best['regime']['label']}")
    console.print(f"  [bold red]▼ {t('highest_risk')}:[/] [bold]{worst['symbol']}[/] — {worst['regime']['label']}\n")
    lang_str = 'Chinese' if LANG=='zh' else 'English'
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    summary_data = [{'symbol':r['symbol'],'regime':r['regime']['label'],'regime_confidence':r['regime']['confidence_pct'],'bull_bear_intensity':r['regime'].get('bull_bear_intensity',50),'price':r['evidence'].get('target_coin',{}).get('price_usd'),'change_24h':r['evidence'].get('target_coin',{}).get('change_24h_pct',0),'change_7d':r['change_7d'],'change_30d':r['change_30d'],'fear_greed':r['evidence'].get('sentiment',{}).get('fear_greed_value',50),'derivatives_change':r['evidence'].get('global',{}).get('derivatives_volume_24h_change_pct',0)} for r in results]
    macro_events = results[0]['evidence'].get('macro_events', []) if results else []
    schema = """{"market_environment": "2-3 sentences with specific data","asset_ranking": [{"symbol": "BTC","rank": 1,"label": "best|good|risky|worst","reason": "one sentence with data","opportunity_score": 75},{"symbol": "ETH","rank": 2,"label": "best|good|risky|worst","reason": "one sentence with data","opportunity_score": 60},{"symbol": "BNB","rank": 3,"label": "best|good|risky|worst","reason": "one sentence with data","opportunity_score": 45},{"symbol": "SOL","rank": 4,"label": "best|good|risky|worst","reason": "one sentence with data","opportunity_score": 30}],"key_focus": {"symbol": "BTC","reason": "2 sentences"},"correlation_note": "one sentence on asset correlations","strategy_48h": "2-3 sentences with specific price levels","trigger_to_watch": ["signal 1 with threshold","signal 2 with threshold"]}"""
    summary_prompt = (
        "You are the Chief Market Verdict Officer of Verdict Protocol. Current time: " + now_str + "\n\n"
        + "Multi-asset real-time data:\n" + json.dumps(summary_data, indent=2) + "\n\n"
        + "Upcoming macro events (next 48h):\n" + json.dumps(macro_events, indent=2) + "\n\n"
        + "Output ONLY this JSON structure, no markdown, no extra text:\n" + schema
        + "\n\nWrite all text fields in " + lang_str + ". Use plain text only, no markdown, no ** symbols."
    )
    with console.status(f"[bold cyan]⚖  {t('deliberating')} (multi-asset)...[/]", spinner="bouncingBall"):
        resp = deepseek.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role":"system","content":"Output ONLY valid JSON. No markdown. No ** symbols. No extra text."},
                {"role":"user","content":summary_prompt}
            ],
            temperature=0.1
        )
    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"```json|```","",raw).strip()
    try:
        synthesis = json.loads(raw)
    except:
        synthesis = None

    console.print()
    console.rule("[bold cyan]⚖  Cross-Asset Synthesis[/]")
    console.print()

    if synthesis:
        with console.status(f"[dim]{'解析市场环境...' if LANG=='zh' else 'Parsing market environment...'}", spinner="dots"):
            time.sleep(0.5)
        env_label = "市场环境" if LANG=="zh" else "Market Environment"
        console.print(Panel(f"[white]{synthesis.get('market_environment','—')}[/]",
            title=f"[bold cyan]🌐  {env_label}[/]", border_style="cyan", padding=(0,2)))
        time.sleep(0.4)

        console.print()
        rank_label = "资产排名（机会/风险比）" if LANG=="zh" else "Asset Ranking (Opportunity/Risk)"
        console.print(f"  [bold cyan]📊  {rank_label}[/]")
        console.print()
        label_colors = {"best":"green","good":"cyan","risky":"yellow","worst":"red"}
        label_icons = {"best":"▲","good":"△","risky":"▽","worst":"▼"}
        label_zh = {"best":"最佳","good":"较好","risky":"风险","worst":"最险"}
        label_en = {"best":"BEST","good":"GOOD","risky":"RISKY","worst":"WORST"}
        circles = "①②③④"
        for item in synthesis.get("asset_ranking",[]):
            time.sleep(0.25)
            sym = item.get("symbol","—")
            rank = item.get("rank",1)
            lbl = item.get("label","risky")
            reason = item.get("reason","—")
            score = item.get("opportunity_score",50)
            lcolor = label_colors.get(lbl,"yellow")
            licon = label_icons.get(lbl,"△")
            ltext = label_zh.get(lbl,lbl) if LANG=="zh" else label_en.get(lbl,lbl)
            score_bar = "█"*int(score/10)+"░"*(10-int(score/10))
            console.print(f"  [dim]{circles[rank-1] if rank<=4 else str(rank)}[/] [bold white]{sym.ljust(5)}[/] [{lcolor}]{licon} {ltext}[/]  [{lcolor}]{score_bar}[/] [dim]{score}[/]")
            console.print(f"       [dim]{reason}[/]")
        time.sleep(0.3)

        console.print()
        corr_label = "联动性观察" if LANG=="zh" else "Correlation Note"
        console.print(f"  [bold cyan]🔗  {corr_label}[/]")
        console.print(f"  [dim]{synthesis.get('correlation_note','—')}[/]")
        time.sleep(0.3)

        console.print()
        focus = synthesis.get("key_focus",{})
        focus_label = "重点关注" if LANG=="zh" else "Key Focus"
        console.print(f"  [bold cyan]🎯  {focus_label}: [bold white]{focus.get('symbol','—')}[/][/]")
        console.print(f"  [dim]{focus.get('reason','—')}[/]")
        time.sleep(0.3)

        console.print()
        strat_label = "48H策略建议" if LANG=="zh" else "48H Strategy"
        with console.status(f"[dim]{'生成策略建议...' if LANG=='zh' else 'Generating strategy...'}", spinner="dots"):
            time.sleep(0.6)
        console.print(Panel(f"[bold white]{synthesis.get('strategy_48h','—')}[/]",
            title=f"[bold cyan]⚡  {strat_label}[/]", border_style="yellow", padding=(0,2)))
        time.sleep(0.3)

        console.print()
        trigger_label = "关键信号监控" if LANG=="zh" else "Triggers to Watch"
        console.print(f"  [bold cyan]⚠  {trigger_label}[/]")
        for i,trig in enumerate(synthesis.get("trigger_to_watch",[]),1):
            time.sleep(0.2)
            console.print(f"  [yellow]{i}.[/] {trig}")
    else:
        console.print(Panel(raw, title="[bold cyan]⚖  Cross-Asset Synthesis[/]", border_style="cyan", padding=(1,2)))


def show_accuracy():
    import os as _os

    # 读取所有裁决记录
    verdicts_dir = "verdicts"
    all_records = []
    if _os.path.exists(verdicts_dir):
        for filename in sorted(_os.listdir(verdicts_dir), reverse=True):
            if not filename.endswith(".json"): continue
            try:
                with open(_os.path.join(verdicts_dir, filename)) as f:
                    all_records.append(json.load(f))
            except: continue

    # 计算总体战绩
    total_v = correct_v = incorrect_v = inconclusive_v = 0
    max_streak = cur_streak = 0
    streak_list = []
    per_symbol = {}
    recent = []

    for r in reversed(all_records):
        sym = r.get("symbol","—")
        outcome = r.get("outcome")
        if sym not in per_symbol:
            per_symbol[sym] = {"total":0,"correct":0,"incorrect":0,"inconclusive":0,"changes":[]}
        per_symbol[sym]["total"] += 1
        total_v += 1
        if outcome:
            result = outcome.get("result","inconclusive")
            chg = outcome.get("price_change_pct",0)
            per_symbol[sym]["changes"].append(chg)
            if result == "correct":
                correct_v += 1
                per_symbol[sym]["correct"] += 1
                cur_streak += 1
                max_streak = max(max_streak, cur_streak)
                streak_list.append("correct")
            elif result == "incorrect":
                incorrect_v += 1
                per_symbol[sym]["incorrect"] += 1
                cur_streak = 0
                streak_list.append("incorrect")
            else:
                inconclusive_v += 1
                per_symbol[sym]["inconclusive"] += 1
                streak_list.append("inconclusive")
            recent.append({
                "id": r.get("verdict_id","—"),
                "symbol": sym,
                "result": result,
                "change": chg,
                "hours": outcome.get("hours_elapsed",0),
                "direction": outcome.get("verdict_direction","—"),
            })
        else:
            per_symbol[sym]["total"] = per_symbol[sym].get("total",0)

    recent = list(reversed(recent))[:5]
    win_rate = round(correct_v/(correct_v+incorrect_v)*100,1) if (correct_v+incorrect_v)>0 else 0
    cur_streak_final = 0
    for s in reversed(streak_list):
        if s == "correct": cur_streak_final += 1
        else: break

    # ── BOOT SEQUENCE ──
    console.clear()
    console.print(BANNER, style="bold cyan", justify="center")
    boot_lines = [
        f"VERDICT PROTOCOL — PERFORMANCE ANALYTICS",
        f"LOADING VERDICT DATABASE...  {'█'*min(total_v,20)}{'░'*(20-min(total_v,20))}  {total_v} RECORDS",
        f"COMPUTING ACCURACY METRICS... {'[green]DONE[/]' if total_v>0 else '[yellow]NO DATA[/]'}",
        f"CALIBRATING SIGNAL WEIGHTS... [green]DONE[/]",
        f"RENDERING DASHBOARD...",
    ]
    for line in boot_lines:
        console.print(f"  [dim cyan]{line}[/]")
        time.sleep(0.3)
    console.print()
    time.sleep(0.4)

    # ── 总体战绩 ──
    wr_color = "green" if win_rate>=70 else "yellow" if win_rate>=50 else "red"
    wr_bar_filled = int(win_rate/10)
    wr_bar = f"[{wr_color}]{'█'*wr_bar_filled}[/][dim]{'░'*(10-wr_bar_filled)}[/]"

    overall_label = "总体战绩" if LANG=="zh" else "Overall Performance"
    winrate_label = "胜率" if LANG=="zh" else "WIN RATE"
    total_label = "总裁决" if LANG=="zh" else "TOTAL"
    correct_label = "正确" if LANG=="zh" else "CORRECT"
    incorrect_label = "错误" if LANG=="zh" else "INCORRECT"
    streak_label = "当前连胜" if LANG=="zh" else "CUR STREAK"
    best_streak_label = "最长连胜" if LANG=="zh" else "BEST STREAK"

    pending_zh = "待定" if LANG=="zh" else "PENDING"
    streak_color = "green" if cur_streak_final>0 else "white"
    overall_content = (
        f"  {wr_bar}  [{wr_color}][bold]{win_rate}%[/][/]  [dim]{winrate_label}[/]\n\n"
        f"  [dim]{total_label}:[/] [bold white]{total_v}[/]    "
        f"[dim]{correct_label}:[/] [bold green]{correct_v}[/]    "
        f"[dim]{incorrect_label}:[/] [bold red]{incorrect_v}[/]    "
        f"[dim]{pending_zh}:[/] [bold yellow]{inconclusive_v}[/]\n\n"
        f"  [dim]{streak_label}:[/] [bold {streak_color}]{cur_streak_final}[/]    "
        f"[dim]{best_streak_label}:[/] [bold cyan]{max_streak}[/]"
    )
    with console.status(f"[dim]{'计算战绩...' if LANG=='zh' else 'Computing stats...'}", spinner="dots"):
        time.sleep(0.6)
    console.print(Panel(overall_content, title=f"[bold cyan]🏆  {overall_label}[/]", border_style="cyan", padding=(1,2)))
    time.sleep(0.4)

    # ── 各币种横向条形图 ──
    console.print()
    rank_label = "各币种战绩" if LANG=="zh" else "Per-Asset Performance"
    console.print(f"  [bold cyan]📊  {rank_label}[/]")
    console.print()
    for sym in ["BTC","ETH","BNB","SOL"]:
        time.sleep(0.2)
        sd = per_symbol.get(sym, {"total":0,"correct":0,"incorrect":0,"inconclusive":0,"changes":[]})
        c = sd["correct"]; inc = sd["incorrect"]; tot = sd["total"]
        wr = round(c/(c+inc)*100,1) if (c+inc)>0 else 0
        bar_w = int(wr/5)
        bar = f"[{'green' if wr>=70 else 'yellow' if wr>=50 else 'red'}]{'█'*bar_w}[/][dim]{'░'*(20-bar_w)}[/]"
        changes = sd["changes"]
        avg_chg = round(sum(changes)/len(changes),2) if changes else 0
        best = round(max(changes),1) if changes else 0
        worst = round(min(changes),1) if changes else 0
        wr_color = "green" if wr>=70 else "yellow" if wr>=50 else "red"
        console.print(
            f"  [bold white]{sym.ljust(5)}[/] {bar}  [{wr_color}]{wr}%[/]  "
            f"[green]{c}W[/]-[red]{inc}L[/]  "
            f"[dim]avg:[/][{'green' if avg_chg>=0 else 'red'}]{avg_chg:+.1f}%[/]  "
            f"[dim]best:[/][green]{best:+.1f}%[/]  "
            f"[dim]worst:[/][red]{worst:+.1f}%[/]"
        )
    time.sleep(0.3)

    # ── 最近裁决时间线 ──
    if recent:
        console.print()
        timeline_label = "最近裁决记录" if LANG=="zh" else "Recent Verdicts"
        console.print(f"  [bold cyan]📋  {timeline_label}[/]")
        console.print()
        result_icons = {"correct":"[bold green]✓[/]","incorrect":"[bold red]✗[/]","inconclusive":"[bold yellow]?[/]"}
        dir_labels = {"bearish":("看空" if LANG=="zh" else "BEARISH"),"bullish":("看多" if LANG=="zh" else "BULLISH"),"neutral":("中立" if LANG=="zh" else "NEUTRAL")}
        for rec in recent:
            time.sleep(0.2)
            icon = result_icons.get(rec["result"],"[dim]?[/]")
            rc = "green" if rec["result"]=="correct" else "red" if rec["result"]=="incorrect" else "yellow"
            direction = dir_labels.get(rec["direction"], rec["direction"])
            chg = rec["change"]
            chg_str = f"[{'green' if chg>=0 else 'red'}]{chg:+.2f}%[/]"
            hours_str = f"{rec['hours']:.0f}h ago" if rec['hours']>0 else "pending"
            console.print(
                f"  {icon} [dim]{rec['id'][-20:]}[/]  "
                f"[bold white]{rec['symbol']}[/]  "
                f"[dim]{direction}[/]  "
                f"{chg_str}  "
                f"[{rc}]{t(rec['result'])}[/]  "
                f"[dim]{hours_str}[/]"
            )
    time.sleep(0.3)

    # ── 信号权重热力图 ──
    console.print()
    weight_label = "信号权重热力图（自动校准）" if LANG=="zh" else "Signal Weight Heatmap (Auto-calibrating)"
    console.print(f"  [bold cyan]🧠  {weight_label}[/]")
    console.print()
    weights = load_weights()
    max_w = max(weights.values()) if weights else 1.0
    min_w = min(weights.values()) if weights else 1.0
    dim_names = t("dim")
    dim_map = {
        "price_momentum": dim_names[0],
        "sentiment": dim_names[1],
        "market_breadth": dim_names[2],
        "derivatives": dim_names[3],
        "btc_dominance": dim_names[4],
        "sectors": dim_names[5],
        "stablecoin": dim_names[6],
    }
    for i,(k,v) in enumerate(weights.items()):
        time.sleep(0.15)
        intensity = int((v/2.0)*10)
        if v > 1.05:
            color="green"; trend="▲"; status=("上升" if LANG=="zh" else "UP")
        elif v < 0.95:
            color="red"; trend="▼"; status=("下降" if LANG=="zh" else "DOWN")
        else:
            color="white"; trend="═"; status=("基准" if LANG=="zh" else "BASE")
        heat_bar = f"[{color}]{'█'*intensity}[/][dim]{'░'*(10-intensity)}[/]"
        dim_name = dim_map.get(k, k)
        delta = v - 1.0
        delta_str = f"[{color}]{delta:+.2f}[/]"
        console.print(
            f"  [{color}]{trend}[/] [white]{dim_name.ljust(12)}[/] "
            f"{heat_bar}  [{color}]{v:.2f}[/]  {delta_str}  [dim]{status}[/]"
        )
    console.print()

def select_language():
    global LANG
    show_banner()
    console.print(Panel("[bold]1[/]  中文\n[bold]2[/]  English",title="[bold cyan]选择语言 / Select Language[/]",border_style="blue",padding=(1,4)))
    choice=IntPrompt.ask("  ›",choices=["1","2"])
    LANG="zh" if choice==1 else "en"

def main_menu():
    while True:
        show_banner()
        console.print(Panel(f"[bold]1[/]  {t('mode1')}\n[bold]2[/]  {t('mode2')}\n[bold]3[/]  {t('mode3')}\n[bold]4[/]  {t('mode4')}",title=f"[bold cyan]{t('select_mode')}[/]",border_style="blue",padding=(1,4)))
        choice=IntPrompt.ask("  ›",choices=["1","2","3","4"])
        if choice==1:
            symbol=Prompt.ask(f"\n  {'输入币种符号 (如 BTC/ETH/PEPE/DOGE)' if LANG=='zh' else 'Enter symbol (e.g. BTC/ETH/PEPE/DOGE)'}").upper()
            single_verdict(symbol)
            Prompt.ask(f"\n  [dim]{t('press_enter')}[/]")
        elif choice==2:
            multi_verdict()
            Prompt.ask(f"\n  [dim]{t('press_enter')}[/]")
        elif choice==3:
            show_accuracy()
            Prompt.ask(f"\n  [dim]{t('press_enter')}[/]")
        elif choice==4:
            console.print("\n[bold cyan]Verdict Protocol — Terminated.[/]\n")
            break

if __name__=="__main__":
    select_language()
    main_menu()
