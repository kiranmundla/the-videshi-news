#!/usr/bin/env python3
"""Fetch historical price data for market indices and save as JSON for chart rendering."""

import json
import os
import sys
from datetime import datetime, timezone

try:
    import yfinance as yf
except ImportError:
    print("Installing yfinance...")
    os.system(f"{sys.executable} -m pip install -q yfinance")
    import yfinance as yf

SYMBOLS = {
    "SENSEX": "^BSESN",
    "NIFTY": "^NSEI",
    "SPX": "^GSPC",
    "NASDAQ": "^IXIC",
    "USDINR": "USDINR=X",
    "GOLD": "GC=F",
    "SILVER": "SI=F",
}

TIMEFRAMES = {
    "1D": {"period": "1d", "interval": "5m"},
    "1W": {"period": "5d", "interval": "1h"},
    "1M": {"period": "1mo", "interval": "1d"},
    "1Y": {"period": "1y", "interval": "1wk"},
}

MAX_POINTS = 100

def fetch_chart_data(symbol_key, yf_symbol):
    result = {}
    for tf_name, params in TIMEFRAMES.items():
        try:
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period=params["period"], interval=params["interval"])
            if hist.empty:
                result[tf_name] = []
                continue

            points = []
            for ts, row in hist.iterrows():
                close = row.get("Close")
                if close is None or (hasattr(close, '__iter__') and len(close) == 0):
                    continue
                val = float(close) if not hasattr(close, 'item') else close.item()
                if val <= 0:
                    continue
                t_str = ts.strftime("%Y-%m-%dT%H:%M")
                points.append({"t": t_str, "v": round(val, 2)})

            # Downsample if too many points
            if len(points) > MAX_POINTS:
                step = len(points) / MAX_POINTS
                sampled = []
                for i in range(MAX_POINTS):
                    idx = int(i * step)
                    sampled.append(points[idx])
                # Always include the last point
                if sampled[-1] != points[-1]:
                    sampled[-1] = points[-1]
                points = sampled

            result[tf_name] = points
            print(f"  {symbol_key} {tf_name}: {len(points)} points")
        except Exception as e:
            print(f"  {symbol_key} {tf_name}: ERROR - {e}")
            result[tf_name] = []
    return result


def main():
    output_path = os.path.join(os.path.dirname(__file__), "..", "public", "data", "market-charts.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    charts = {}
    for key, yf_sym in SYMBOLS.items():
        print(f"Fetching {key} ({yf_sym})...")
        charts[key] = fetch_chart_data(key, yf_sym)

    data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "charts": charts,
    }

    with open(output_path, "w") as f:
        json.dump(data, f)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"\nSaved to {output_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
