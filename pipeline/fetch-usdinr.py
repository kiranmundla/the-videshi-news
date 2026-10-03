#!/usr/bin/env python3
"""
Fetch USD/INR rate daily and maintain history for the remittance tracker.
Uses the free open.er-api.com (no key needed). Run via daily cron.

Outputs:
  public/data/usdinr.json         — current rate + 30d sparkline + day change
  public/data/usdinr-history.json — full 90d history
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO, "public", "data")
CURRENT_FILE = os.path.join(DATA_DIR, "usdinr.json")
HISTORY_FILE = os.path.join(DATA_DIR, "usdinr-history.json")
HISTORY_DAYS = 90


def fetch_rate():
    cmd = ["curl", "-sS", "--max-time", "20",
           "https://open.er-api.com/v6/latest/USD"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"curl failed: {r.stderr[:100]}")
    d = json.loads(r.stdout)
    if d.get("result") != "success":
        raise RuntimeError(f"API error: {d.get('error-type', 'unknown')}")
    return float(d["rates"]["INR"]), d.get("time_last_update_utc", "")


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            return json.load(open(HISTORY_FILE))
        except Exception:
            pass
    return []


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        rate, updated = fetch_rate()
    except Exception as e:
        print(f"FAILED to fetch rate: {e}", file=sys.stderr)
        sys.exit(1)

    history = load_history()
    # Replace today's entry if re-run, else append
    history = [h for h in history if h.get("date") != today]
    history.append({"date": today, "rate": round(rate, 4)})
    history = sorted(history, key=lambda h: h["date"])[-HISTORY_DAYS:]

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

    # Build current snapshot: rate, day change, 30d sparkline
    spark = history[-30:]
    prev = history[-2]["rate"] if len(history) >= 2 else rate
    day_change = rate - prev
    day_change_pct = (day_change / prev * 100) if prev else 0
    hi_30 = max(h["rate"] for h in spark) if spark else rate
    lo_30 = min(h["rate"] for h in spark) if spark else rate

    snapshot = {
        "pair": "USD/INR",
        "rate": round(rate, 2),
        "date": today,
        "updated_utc": updated,
        "source": "open.er-api.com (mid-market)",
        "day_change": round(day_change, 2),
        "day_change_pct": round(day_change_pct, 2),
        "high_30d": round(hi_30, 2),
        "low_30d": round(lo_30, 2),
        "sparkline": [{"d": h["date"], "r": h["rate"]} for h in spark],
    }
    with open(CURRENT_FILE, "w") as f:
        json.dump(snapshot, f, separators=(",", ":"))

    print(f"USD/INR: {rate:.2f} ({day_change:+.2f}, {day_change_pct:+.2f}%) — {len(history)}d history")


if __name__ == "__main__":
    main()
