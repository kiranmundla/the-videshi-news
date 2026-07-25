#!/usr/bin/env python3
"""Lightweight cron token usage logger. Each cron can call this at the end of a run."""
import json, os, sys, time
from datetime import datetime, timezone

LOG_PATH = os.path.expanduser("~/workspace/cron-usage-log.json")

def log_run(cron_id, context_chars=0, note=""):
    """Append a run entry to the usage log."""
    entry = {
        "cron_id": cron_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "context_chars": context_chars,
        "est_tokens": context_chars // 4,  # rough 4 chars/token estimate
        "note": note
    }
    
    data = []
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH) as f:
                data = json.load(f)
        except:
            data = []
    
    data.append(entry)
    
    # Keep last 7 days only
    cutoff = time.time() - 7 * 86400
    data = [e for e in data if datetime.fromisoformat(e["ts"]).timestamp() > cutoff]
    
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=1)

def summary():
    """Print usage summary."""
    if not os.path.exists(LOG_PATH):
        print("No usage data yet.")
        return
    
    with open(LOG_PATH) as f:
        data = json.load(f)
    
    if not data:
        print("No usage data yet.")
        return
    
    # Group by cron_id
    by_cron = {}
    for e in data:
        cid = e["cron_id"]
        if cid not in by_cron:
            by_cron[cid] = {"runs": 0, "total_tokens": 0}
        by_cron[cid]["runs"] += 1
        by_cron[cid]["total_tokens"] += e.get("est_tokens", 0)
    
    # Sort by total tokens desc
    ranked = sorted(by_cron.items(), key=lambda x: -x[1]["total_tokens"])
    
    total_runs = sum(v["runs"] for v in by_cron.values())
    total_tokens = sum(v["total_tokens"] for v in by_cron.values())
    
    print(f"Last 7 days: {total_runs} runs, ~{total_tokens:,} est tokens\n")
    print(f"{'Cron':<35} {'Runs':>5} {'Est Tokens':>12} {'Avg/Run':>10}")
    print("-" * 65)
    for cid, v in ranked:
        avg = v["total_tokens"] // v["runs"] if v["runs"] else 0
        print(f"{cid:<35} {v['runs']:>5} {v['total_tokens']:>12,} {avg:>10,}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        summary()
    elif len(sys.argv) > 1:
        log_run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 0)
    else:
        print("Usage: cron-usage-log.py <cron_id> [context_chars]")
        print("       cron-usage-log.py --summary")
