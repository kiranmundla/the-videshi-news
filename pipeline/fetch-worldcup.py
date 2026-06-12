#!/usr/bin/env python3
"""
fetch-worldcup.py — Update World Cup 2026 data (scores, standings, highlights)

Fetches latest match results and updates worldcup.json.
Run as a cron job during the tournament (June 11 – July 19, 2026).

Sources:
  - Web search for live scores/results
  - Social media for highlight videos (@fifaworldcup on IG/Threads/YouTube)

Output: public/data/worldcup.json (updated in place)
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone

REPO = os.path.expanduser("~/workspace/the-videshi-news")
DATA_FILE = os.path.join(REPO, "public/data/worldcup.json")


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    data["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[worldcup] Saved {DATA_FILE}")


def update_standings(data):
    """Recalculate group standings from match results."""
    # Reset all standings
    for group_teams in data["groups"].values():
        for t in group_teams:
            t["p"] = 0; t["w"] = 0; t["d"] = 0; t["l"] = 0
            t["gf"] = 0; t["ga"] = 0; t["pts"] = 0

    # Build code→team lookup
    code_to_team = {}
    for group_teams in data["groups"].values():
        for t in group_teams:
            code_to_team[t["code"]] = t

    # Tally from completed matches
    for m in data["matches"]:
        if m["status"] != "FT" or not m.get("score"):
            continue
        parts = m["score"].split("-")
        if len(parts) != 2:
            continue
        hg, ag = int(parts[0].strip()), int(parts[1].strip())
        ht = code_to_team.get(m["home_code"])
        at = code_to_team.get(m["away_code"])
        if not ht or not at:
            continue
        ht["p"] += 1; at["p"] += 1
        ht["gf"] += hg; ht["ga"] += ag
        at["gf"] += ag; at["ga"] += hg
        if hg > ag:
            ht["w"] += 1; ht["pts"] += 3
            at["l"] += 1
        elif ag > hg:
            at["w"] += 1; at["pts"] += 3
            ht["l"] += 1
        else:
            ht["d"] += 1; at["d"] += 1
            ht["pts"] += 1; at["pts"] += 1

    # Sort each group
    for g in data["groups"]:
        data["groups"][g].sort(key=lambda t: (t["pts"], t["gf"] - t["ga"], t["gf"]), reverse=True)

    # Update stage description
    total_played = sum(1 for m in data["matches"] if m["status"] == "FT")
    total_group = len([m for m in data["matches"] if m.get("group")])
    if total_played == 0:
        data["stage"] = "Group Stage — Kicks off June 11"
    elif total_played < total_group:
        matchdays = set()
        for m in data["matches"]:
            if m["status"] == "FT":
                matchdays.add(m["date"])
        data["stage"] = f"Group Stage — {total_played} of {total_group} matches played"
    else:
        data["stage"] = "Knockout Stage"


def git_push(message):
    """Commit and push updates."""
    try:
        subprocess.run(["git", "add", "public/data/worldcup.json"], cwd=REPO, check=True)
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO)
        if result.returncode == 0:
            print("[worldcup] No changes to push")
            return
        subprocess.run(["git", "commit", "-m", message], cwd=REPO, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO, check=True)
        print(f"[worldcup] Pushed: {message}")
    except subprocess.CalledProcessError as e:
        print(f"[worldcup] Git error: {e}")


def main():
    data = load_data()
    
    # Recalculate standings from current data
    update_standings(data)
    save_data(data)
    
    # Push if there are changes
    git_push(f"data: update World Cup standings ({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')})")
    
    print("[worldcup] Done")


if __name__ == "__main__":
    main()
