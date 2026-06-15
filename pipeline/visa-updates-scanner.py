#!/usr/bin/env python3
"""
Visa Updates Scanner
- Searches for new US visa/consulate announcements affecting India
- Checks State Dept wait time changes
- Updates visa-updates.json
- Pushes to git if changes detected
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

REPO = os.path.expanduser("~/workspace/the-videshi-news")
UPDATES_FILE = os.path.join(REPO, "public/data/visa-updates.json")
ENV_FILE = os.path.expanduser("~/workspace/.env.github")

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

def load_existing():
    if os.path.exists(UPDATES_FILE):
        with open(UPDATES_FILE) as f:
            return json.load(f)
    return []

def save_updates(updates):
    with open(UPDATES_FILE, "w") as f:
        json.dump(updates, f, indent=2)
        f.write("\n")

def git_push_if_changed():
    load_env(ENV_FILE)
    os.chdir(REPO)
    # Check if file changed
    result = subprocess.run(["git", "diff", "--name-only", "public/data/visa-updates.json"],
                          capture_output=True, text=True)
    if "visa-updates.json" not in result.stdout:
        print("No changes to visa-updates.json")
        return False
    subprocess.run(["git", "add", "public/data/visa-updates.json"], check=True)
    subprocess.run(["git", "commit", "-m", f"update visa updates {datetime.now().strftime('%Y-%m-%d')}"],
                  check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("Pushed visa-updates.json changes")
    return True

def main():
    """
    This script is called by the Hatch cron. The cron worker (the AI agent)
    will do the actual web searching and analysis. This script handles:
    1. Loading existing updates
    2. Accepting new updates via stdin (JSON array)
    3. Merging, deduplicating, sorting
    4. Saving and pushing
    """
    existing = load_existing()
    existing_ids = {u["id"] for u in existing}
    
    # Read new updates from stdin if piped
    if not sys.stdin.isatty():
        try:
            new_updates = json.load(sys.stdin)
            for u in new_updates:
                if u["id"] not in existing_ids:
                    existing.append(u)
                    existing_ids.add(u["id"])
                    print(f"Added: {u['headline']}")
        except Exception as e:
            print(f"Error reading stdin: {e}")
    
    # Sort by date descending
    existing.sort(key=lambda u: u.get("date", ""), reverse=True)

    # Still-active policies are never trimmed out by age, even if they fall
    # outside the latest-20 window (e.g. interview waiver elimination).
    STICKY_IDS = {"interview-waiver-eliminated"}

    # Keep latest 20, but always preserve sticky still-active policies.
    kept = existing[:20]
    kept_ids = {u["id"] for u in kept}
    for u in existing:
        if u["id"] in STICKY_IDS and u["id"] not in kept_ids:
            # Drop the oldest non-sticky entry to make room.
            for i in range(len(kept) - 1, -1, -1):
                if kept[i]["id"] not in STICKY_IDS:
                    kept.pop(i)
                    break
            kept.append(u)
    kept.sort(key=lambda u: u.get("date", ""), reverse=True)
    existing = kept[:20]
    
    save_updates(existing)
    git_push_if_changed()

if __name__ == "__main__":
    main()
