#!/usr/bin/env python3
"""Sports writer — 2026-05-22 night run (23:00 PDT): data refresh only.
No new articles needed — section well stocked from today's runs (8 articles).
Focus: fix IPL standings for Match 67, score decay, markets refresh, git push.
"""

import json, os, re, subprocess, sys, requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Supabase config ──
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

now = datetime.now(timezone.utc).isoformat()

print(f"=== Sports Writer — 2026-05-22 Night (23:00 PDT) ===\n")
print("No new articles this run — sports section well stocked (8 articles today).\n")


# ══════════════════════════════════════════════════════════════
# FIX IPL STANDINGS — Update for Match 67 (SRH 255/4 beat RCB 200/4)
# ══════════════════════════════════════════════════════════════

print("── IPL Standings Fix (Match 67 update) ──")
try:
    ipl_path = PROJECT_ROOT / "public" / "data" / "ipl-standings.json"
    ipl_data = json.loads(ipl_path.read_text())

    # Updated standings after Match 67 (SRH beat RCB by 55 runs)
    # Source: mykhel.com official points table, May 22 2026
    updated_standings = [
        {"team": "Royal Challengers Bengaluru", "short": "RCB", "played": 14, "won": 9, "lost": 5, "nr": 0, "nrr": "+0.783", "points": 18, "position": 1},
        {"team": "Gujarat Titans", "short": "GT", "played": 14, "won": 9, "lost": 5, "nr": 0, "nrr": "+0.695", "points": 18, "position": 2},
        {"team": "Sunrisers Hyderabad", "short": "SRH", "played": 14, "won": 9, "lost": 5, "nr": 0, "nrr": "+0.524", "points": 18, "position": 3},
        {"team": "Rajasthan Royals", "short": "RR", "played": 13, "won": 7, "lost": 6, "nr": 0, "nrr": "+0.083", "points": 14, "position": 4},
        {"team": "Punjab Kings", "short": "PBKS", "played": 13, "won": 6, "lost": 6, "nr": 1, "nrr": "+0.227", "points": 13, "position": 5},
        {"team": "Kolkata Knight Riders", "short": "KKR", "played": 13, "won": 6, "lost": 6, "nr": 1, "nrr": "+0.011", "points": 13, "position": 6},
        {"team": "Chennai Super Kings", "short": "CSK", "played": 14, "won": 6, "lost": 8, "nr": 0, "nrr": "-0.345", "points": 12, "position": 7},
        {"team": "Delhi Capitals", "short": "DC", "played": 13, "won": 6, "lost": 7, "nr": 0, "nrr": "-0.871", "points": 12, "position": 8},
        {"team": "Mumbai Indians", "short": "MI", "played": 13, "won": 4, "lost": 9, "nr": 0, "nrr": "-0.510", "points": 8, "position": 9},
        {"team": "Lucknow Super Giants", "short": "LSG", "played": 13, "won": 4, "lost": 9, "nr": 0, "nrr": "-0.702", "points": 8, "position": 10},
    ]

    ipl_data["standings"] = updated_standings
    ipl_data["last_updated"] = now
    ipl_data["stage"] = "Top 3 qualified (RCB, GT, SRH — all 18 pts). 3 matches remain for 4th playoff spot. RCB vs GT in Qualifier 1."

    ipl_data["recent_results"] = [
        {"match": "Match 67", "date": "May 22", "teams": "SRH vs RCB", "result": "SRH won by 55 runs (SRH 255/4, RCB 200/4)", "venue": "Hyderabad"},
        {"match": "Match 66", "date": "May 21", "teams": "GT vs CSK", "result": "GT won by 89 runs (GT 229/4, CSK 140)", "venue": "Ahmedabad"},
        {"match": "Match 65", "date": "May 20", "teams": "KKR vs MI", "result": "KKR won by 4 wickets", "venue": "Kolkata"},
        {"match": "Match 64", "date": "May 19", "teams": "RR vs LSG", "result": "RR won by 5 wickets", "venue": "Jaipur"},
        {"match": "Match 63", "date": "May 18", "teams": "CSK vs SRH", "result": "SRH won by 5 wickets", "venue": "Chennai"},
    ]

    ipl_data["upcoming"] = [
        {"match": "Match 68", "date": "May 23", "teams": "LSG vs PBKS", "time": "7:30 PM IST", "venue": "Lucknow", "note": "PBKS must win to stay alive"},
        {"match": "Match 69", "date": "May 24", "teams": "MI vs RR", "time": "3:30 PM IST", "venue": "Mumbai"},
        {"match": "Match 70", "date": "May 24", "teams": "KKR vs DC", "time": "7:30 PM IST", "venue": "Kolkata"},
    ]

    ipl_data["playoffs"] = {
        "qualifier_1": {"teams": "RCB vs GT", "status": "confirmed"},
        "eliminator": {"teams": "SRH vs TBD (4th place)", "status": "SRH confirmed, opponent TBD after 3 remaining matches"},
        "fourth_spot_race": "RR (14 pts, 1 match left) vs PBKS (13 pts, 1 match left) vs KKR (13 pts, 1 match left) vs DC (12 pts, 1 match left)"
    }

    ipl_data["orange_cap"] = [
        {"player": "Sai Sudharsan", "team": "GT", "runs": 638},
        {"player": "Shubman Gill", "team": "GT", "runs": 616},
        {"player": "Vaibhav Sooryavanshi", "team": "RR", "runs": 579},
        {"player": "Mitchell Marsh", "team": "LSG", "runs": 563},
        {"player": "Heinrich Klaasen", "team": "SRH", "runs": 555},
    ]

    ipl_data["purple_cap"] = [
        {"player": "Bhuvneshwar Kumar", "team": "RCB", "wickets": 24},
        {"player": "Kagiso Rabada", "team": "GT", "wickets": 24},
        {"player": "Anshul Kamboj", "team": "CSK", "wickets": 21},
        {"player": "Rashid Khan", "team": "GT", "wickets": 19},
        {"player": "Jofra Archer", "team": "RR", "wickets": 18},
    ]

    ipl_path.write_text(json.dumps(ipl_data, indent=2))
    print("  ✅ IPL standings updated for Match 67")
    print(f"     RCB P14 W9 L5 NRR+0.783 | GT P14 W9 L5 NRR+0.695 | SRH P14 W9 L5 NRR+0.524")
    print(f"     3 matches remain: LSG-PBKS (May 23), MI-RR + KKR-DC (May 24)")
    print(f"     Added: playoffs, orange_cap, purple_cap sections")
except Exception as e:
    print(f"  ❌ IPL standings error: {e}")


# ══════════════════════════════════════════════════════════════
# SCORE DECAY — age-based decay for older articles
# ══════════════════════════════════════════════════════════════

print("\n── Score Decay ──")
try:
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?status=eq.published&select=id,score_total,published_at&order=published_at.desc",
        headers={**HEADERS, "Prefer": ""},
        timeout=30
    )
    r.raise_for_status()
    all_articles = r.json()
    now_dt = datetime.now(timezone.utc)
    decayed = 0
    for art in all_articles:
        if not art.get("published_at") or not art.get("score_total"):
            continue
        pub = datetime.fromisoformat(art["published_at"].replace("Z", "+00:00"))
        age_hours = (now_dt - pub).total_seconds() / 3600
        if age_hours < 6:
            continue
        decay_amount = int(age_hours / 6) * 2
        new_score = max(10, art["score_total"] - decay_amount)
        if new_score < art["score_total"]:
            requests.patch(
                f"{SB_URL}/rest/v1/p2_articles?id=eq.{art['id']}",
                headers={**HEADERS, "Prefer": "return=minimal"},
                json={"score_total": new_score},
                timeout=10
            )
            decayed += 1
    print(f"  ✅ {decayed} articles decayed (of {len(all_articles)} total published)")
except Exception as e:
    print(f"  ❌ Score decay error: {e}")


# ══════════════════════════════════════════════════════════════
# REFRESH MARKET DATA
# ══════════════════════════════════════════════════════════════

print("\n── Markets Refresh ──")
try:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "videshi-markets.py")],
        capture_output=True, text=True, timeout=60,
        cwd=str(PROJECT_ROOT)
    )
    if result.returncode == 0:
        print(f"  ✅ Markets refreshed")
        for line in result.stdout.strip().split("\n")[-4:]:
            print(f"     {line}")
    else:
        print(f"  ❌ Markets failed: {result.stderr[:200]}")
except Exception as e:
    print(f"  ❌ Markets error: {e}")


# ══════════════════════════════════════════════════════════════
# REFRESH MARKET CHARTS
# ══════════════════════════════════════════════════════════════

print("\n── Market Charts Refresh ──")
try:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "videshi-market-charts.py")],
        capture_output=True, text=True, timeout=120,
        cwd=str(PROJECT_ROOT)
    )
    if result.returncode == 0:
        print(f"  ✅ Market charts refreshed")
    else:
        print(f"  ❌ Market charts failed: {result.stderr[:200]}")
except Exception as e:
    print(f"  ❌ Market charts error: {e}")


# ══════════════════════════════════════════════════════════════
# REFRESH SNAPSHOTS
# ══════════════════════════════════════════════════════════════

print("\n── Snapshots Refresh ──")
try:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "videshi-snapshots.py")],
        capture_output=True, text=True, timeout=60,
        cwd=str(PROJECT_ROOT)
    )
    if result.returncode == 0:
        print(f"  ✅ Snapshots refreshed")
    else:
        print(f"  ❌ Snapshots failed: {result.stderr[:200]}")
except Exception as e:
    print(f"  ❌ Snapshots error: {e}")


# ══════════════════════════════════════════════════════════════
# GIT PUSH
# ══════════════════════════════════════════════════════════════

print("\n── Git Push ──")
try:
    os.chdir(str(PROJECT_ROOT))
    subprocess.run(["git", "add", "public/data/"], capture_output=True, timeout=15)
    commit_result = subprocess.run(
        ["git", "commit", "-m", "data: IPL standings fix (Match 67) + markets + score decay (May 22 night)"],
        capture_output=True, text=True, timeout=15
    )
    if "nothing to commit" in commit_result.stdout + commit_result.stderr:
        print("  ℹ️  No data changes to push")
    else:
        push_result = subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True, text=True, timeout=30
        )
        if push_result.returncode == 0:
            log = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True, text=True, timeout=5)
            print(f"  ✅ Pushed: {log.stdout.strip()}")
        else:
            print(f"  ❌ Push failed: {push_result.stderr[:200]}")
except Exception as e:
    print(f"  ❌ Git error: {e}")


print("\n✅ Sports writer night run complete.")
