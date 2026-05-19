#!/usr/bin/env python3
"""Refresh markets data for The Videshi."""
import json, requests, datetime, os
from pathlib import Path

DATA_DIR = Path.home() / "workspace" / "the-videshi-news" / "public" / "data"

def fetch_markets():
    """Fetch 7 major market indices."""
    indices = [
        {"symbol": "^BSESN", "name": "BSE Sensex", "key": "sensex"},
        {"symbol": "^NSEI", "name": "Nifty 50", "key": "nifty"},
        {"symbol": "^DJI", "name": "Dow Jones", "key": "dow"},
        {"symbol": "^GSPC", "name": "S&P 500", "key": "sp500"},
        {"symbol": "^IXIC", "name": "Nasdaq", "key": "nasdaq"},
        {"symbol": "^FTSE", "name": "FTSE 100", "key": "ftse"},
        {"symbol": "USDINR=X", "name": "USD/INR", "key": "usdinr"},
    ]
    
    results = []
    for idx in indices:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{idx['symbol']}?range=5d&interval=1d"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            data = r.json()
            
            meta = data["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice", 0)
            prev = meta.get("chartPreviousClose", meta.get("previousClose", 0))
            
            change = price - prev if prev else 0
            change_pct = (change / prev * 100) if prev else 0
            
            # Get historical for sparkline
            timestamps = data["chart"]["result"][0].get("timestamp", [])
            closes = data["chart"]["result"][0]["indicators"]["quote"][0].get("close", [])
            sparkline = [c for c in closes if c is not None]
            
            results.append({
                "key": idx["key"],
                "name": idx["name"],
                "symbol": idx["symbol"],
                "price": round(price, 2),
                "change": round(change, 2),
                "changePct": round(change_pct, 2),
                "sparkline": [round(s, 2) for s in sparkline[-5:]],
                "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
            print(f"  ✅ {idx['name']}: {price:,.2f} ({change_pct:+.2f}%)")
        except Exception as e:
            print(f"  ❌ {idx['name']}: {e}")
    
    return results

print("📊 Fetching market data...")
markets = fetch_markets()

if markets:
    markets_file = DATA_DIR / "markets.json"
    with open(markets_file, "w") as f:
        json.dump({"indices": markets, "lastUpdated": datetime.datetime.now(datetime.timezone.utc).isoformat()}, f, indent=2)
    print(f"\n✅ Wrote {len(markets)} indices to {markets_file}")
else:
    print("⚠️ No market data fetched")
