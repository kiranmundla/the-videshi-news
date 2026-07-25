#!/usr/bin/env python3
"""Estimate daily Hatch token usage per cron based on frequency and context size."""
import re, os, glob

# Base context loaded on every agent turn (system prompt + injected files)
# Measured: ~140K tokens for a full session. Cron turns are lighter (no chat history)
# but still load system prompt + all injected files + goals + alignment synthesis
BASE_CONTEXT_TOKENS = 45_000  # conservative estimate for a cron turn

# Heavier crons that do substantial LLM work (writing articles, browsing, reviewing)
HEAVY_CRONS = {
    "videshi-v2-writer": 80_000,      # writes full articles
    "videshi-site-monitor": 60_000,    # browses pages, analyzes
    "videshi-article-reviewer": 40_000, # reviews articles with LLM
    "videshi-enricher": 35_000,        # enriches articles
    "videshi-content-gap-audit": 50_000,
    "videshi-newsletter-daily": 40_000,
    "videshi-newsletter": 50_000,
    "videshi-whos-x-weekly": 60_000,
    "videshi-key-updates-sync": 40_000,
    "videshi-daily-happenings": 40_000,
}

# Light crons that mostly run scripts
LIGHT_CRONS_OVERHEAD = 5_000  # minimal work beyond base context

def parse_interval(s):
    """Parse interval string like '20m', '4h', '96h' to hours."""
    m = re.match(r'(\d+)\s*([smh])', s)
    if not m: return None
    val, unit = int(m.group(1)), m.group(2)
    if unit == 's': return val / 3600
    if unit == 'm': return val / 60
    return val

def get_daily_runs(schedule_key):
    """Estimate runs per day from schedule_key."""
    if schedule_key.startswith('interval@'):
        interval = schedule_key.split('@')[1]
        hours = parse_interval(interval)
        if hours and hours > 0:
            return min(24 / hours, 144)  # cap at 144 (10min interval)
        return 1
    elif schedule_key.startswith('daily@'):
        return 1
    elif schedule_key.startswith('weekly@'):
        # count days
        parts = schedule_key.split('@')[1] if '@' in schedule_key else ''
        days = parts.split('-')[0] if '-' in parts else ''
        day_count = len([d for d in days.split(',') if d.strip()]) if days else 1
        return day_count / 7
    elif schedule_key.startswith('monthly@'):
        return 1 / 30
    return 1

def main():
    import json
    
    # Read cron list from the cron.d directories
    cron_dirs = [
        os.path.expanduser("~/workspace/cron.d"),
        os.path.expanduser("~/workspace/goals/*/crons"),
    ]
    
    crons = []
    for pattern in cron_dirs:
        for path in glob.glob(os.path.join(pattern, "**", "*.md"), recursive=True):
            if "/_archive/" in path:
                continue
            basename = os.path.basename(path)
            # Extract cron id and schedule from filename: id__schedule.md
            if "__" not in basename:
                continue
            parts = basename.replace(".md", "").split("__", 1)
            cron_id = parts[0]
            schedule_key = parts[1] if len(parts) > 1 else ""
            
            # Skip system crons
            if cron_id in ("heartbeat", "doctor", "deterministic-doctor"):
                continue
            
            daily_runs = get_daily_runs(schedule_key)
            work_tokens = HEAVY_CRONS.get(cron_id, LIGHT_CRONS_OVERHEAD)
            per_run = BASE_CONTEXT_TOKENS + work_tokens
            daily_tokens = daily_runs * per_run
            
            crons.append({
                "id": cron_id,
                "schedule": schedule_key,
                "daily_runs": daily_runs,
                "per_run": per_run,
                "daily_tokens": daily_tokens,
            })
    
    # Sort by daily tokens desc
    crons.sort(key=lambda x: -x["daily_tokens"])
    
    total_daily = sum(c["daily_tokens"] for c in crons)
    total_runs = sum(c["daily_runs"] for c in crons)
    
    print(f"═══ Estimated Daily Hatch Token Usage ═══")
    print(f"Total: ~{total_daily/1_000_000:.1f}M tokens/day across ~{total_runs:.0f} runs")
    print(f"Monthly: ~{total_daily * 30 / 1_000_000:.0f}M tokens")
    print()
    print(f"{'Cron':<40} {'Freq':>8} {'Runs/d':>7} {'Per Run':>8} {'Daily':>10}")
    print("─" * 78)
    
    for c in crons:
        freq = c["schedule"].replace("interval@", "").replace("daily@", "daily").replace("weekly@", "weekly")
        per_run_k = f"{c['per_run']//1000}K"
        daily_k = f"{c['daily_tokens']/1000:.0f}K"
        runs = f"{c['daily_runs']:.1f}" if c['daily_runs'] < 1 else f"{c['daily_runs']:.0f}"
        pct = c['daily_tokens'] / total_daily * 100 if total_daily else 0
        bar = "█" * int(pct / 2)
        print(f"{c['id']:<40} {freq:>8} {runs:>7} {per_run_k:>8} {daily_k:>10} {bar}")
    
    print()
    print(f"{'TOTAL':<40} {'':>8} {total_runs:>7.0f} {'':>8} {total_daily/1000:>10.0f}K")
    
    # Top 5
    print(f"\n═══ Top 5 Token Consumers ═══")
    for c in crons[:5]:
        pct = c["daily_tokens"] / total_daily * 100
        print(f"  {c['id']}: ~{c['daily_tokens']/1000:.0f}K/day ({pct:.0f}%)")

if __name__ == "__main__":
    main()
