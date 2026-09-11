#!/usr/bin/env python3
"""Refresh market-indices.json for The Videshi's MarketTicker component.

Reads Yahoo Finance free chart API (no key needed) and writes the file the
frontend actually reads: public/data/market-indices.json with schema
{last_updated, indices: [{symbol, name, flag, value, change, change_pct}]}.
"""
import json, requests, datetime
from pathlib import Path

DATA_DIR = Path.home() / "workspace" / "the-videshi-news" / "public" / "data"

# (yahoo symbol, display symbol, display name, flag emoji)
INDICES = [
    ("^GSPC",  "SPX",    "S&P 500",  "\U0001F1FA\U0001F1F8"),
    ("^IXIC",  "NASDAQ", "Nasdaq",   "\U0001F1FA\U0001F1F8"),
    ("^DJI",   "DJI",    "Dow Jones","\U0001F1FA\U0001F1F8"),
    ("^BSESN", "SENSEX", "Sensex",   "\U0001F1EE\U0001F1F3"),
    ("^NSEI",  "NIFTY",  "Nifty 50", "\U0001F1EE\U0001F1F3"),
    ("^FTSE",  "FTSE",   "FTSE 100", "\U0001F1EC\U0001F1E7"),
    ("USDINR=X", "USDINR", "USD/INR","\U0001F4B1"),
    ("GC=F",   "GOLD",   "Gold",     "✨"),
    ("SI=F",   "SILVER", "Silver",   "\U0001FA99"),
]

def fetch_markets():
    results = []
    for yahoo_sym, symbol, name, flag in INDICES:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_sym}?range=5d&interval=1d"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            data = r.json()
            meta = data["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice", 0)
            prev = meta.get("chartPreviousClose", meta.get("previousClose", 0))
            change = price - prev if prev else 0
            change_pct = (change / prev * 100) if prev else 0
            results.append({
                "symbol": symbol,
                "name": name,
                "flag": flag,
                "value": round(price, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
            })
            print(f"  ✅ {name}: {price:,.2f} ({change_pct:+.2f}%)")
        except Exception as e:
            print(f"  ❌ {name}: {e}")
    return results

print("📊 Fetching market data...")
markets = fetch_markets()

if markets:
    out_file = DATA_DIR / "market-indices.json"
    with open(out_file, "w") as f:
        json.dump({
            "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "indices": markets,
        }, f, indent=2)
    print(f"\n✅ Wrote {len(markets)} indices to {out_file}")
else:
    print("⚠️ No market data fetched")
