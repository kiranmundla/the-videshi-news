#!/usr/bin/env python3
"""
Fetch market index data and save to public/data/market-indices.json.
Uses yfinance for real-time data.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_PATH = PROJECT_ROOT / "public" / "data" / "market-indices.json"

TICKERS = [
    {"symbol": "^BSESN",   "name": "Sensex",   "display": "SENSEX",  "flag": "🇮🇳"},
    {"symbol": "^NSEI",    "name": "Nifty 50",  "display": "NIFTY",   "flag": "🇮🇳"},
    {"symbol": "^GSPC",    "name": "S&P 500",   "display": "SPX",     "flag": "🇺🇸"},
    {"symbol": "^IXIC",    "name": "Nasdaq",    "display": "NASDAQ",  "flag": "🇺🇸"},
    {"symbol": "USDINR=X", "name": "USD/INR",   "display": "USDINR",  "flag": "💱"},
    {"symbol": "GC=F",     "name": "Gold",      "display": "GOLD",    "flag": "✨"},
    {"symbol": "SI=F",     "name": "Silver",    "display": "SILVER",  "flag": "🪙"},
]


def fetch_index(ticker_info: dict) -> dict | None:
    """Fetch a single index/ticker and return formatted dict, or None on error."""
    sym = ticker_info["symbol"]
    try:
        t = yf.Ticker(sym)
        info = t.fast_info
        price = info.last_price
        prev = info.previous_close
        if price is None or prev is None:
            print(f"  WARN: {sym} — missing price data")
            return None
        change = round(price - prev, 2)
        change_pct = round((change / prev) * 100, 2) if prev else 0.0
        print(f"  OK: {ticker_info['name']:>10} = {price:>12,.2f}  ({change:+.2f}, {change_pct:+.2f}%)")
        return {
            "symbol": ticker_info["display"],
            "name": ticker_info["name"],
            "flag": ticker_info["flag"],
            "value": round(price, 2),
            "change": change,
            "change_pct": change_pct,
        }
    except Exception as e:
        print(f"  ERROR: {sym} — {e}")
        return None


def main():
    print("Fetching market data...")
    indices = []
    for t in TICKERS:
        result = fetch_index(t)
        if result:
            indices.append(result)

    if not indices:
        print("No indices fetched successfully. Keeping existing file.")
        return

    data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "indices": indices,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2))
    print(f"\nSaved {len(indices)} indices to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
