#!/usr/bin/env python3
"""Weekly entertainment feed refresh for The Videshi.

Regenerates streaming-picks.json (self-updating week label), enriches
now-in-theaters.json trailers/cast, and rolls its week_of label to the
current Mon–Sun week. Created 2026-10-02 after the site audit found
"What to Watch" showing Aug 31 – Sep 06 and "Now in Theaters" showing
Sep 21 – Sep 27 on Oct 2.
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path("/home/hatch/workspace/the-videshi-news")
PIPE = REPO / "pipeline"
DATA = REPO / "public" / "data"


def run(cmd):
    print(f"$ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=PIPE, capture_output=True, text=True, timeout=600)
    print(r.stdout[-1500:] if r.stdout else "")
    if r.returncode != 0:
        print(f"!! exit={r.returncode}\n{r.stderr[-1500:]}", file=sys.stderr)
    return r.returncode == 0


def current_week_label(now=None):
    now = now or datetime.now(timezone.utc)
    # Week runs Mon–Sun; display in PT like the rest of the site
    monday = now - timedelta(days=now.weekday())
    sunday = monday + timedelta(days=6)
    fmt = lambda d: f"{d.strftime('%b')} {d.strftime('%d')}"
    label = f"{fmt(monday)} – {fmt(sunday)}, {sunday.year}"
    return label.replace(" – ", " – ")  # en dash


def main():
    ok = True
    ok &= run([sys.executable, "-u", "streaming-picks.py"])
    ok &= run([sys.executable, "-u", "fetch-theaters.py"])

    # Roll the theaters week label (movie list itself is editorially curated;
    # fetch-theaters.py only enriches trailers/cast).
    week = current_week_label()
    tp = DATA / "now-in-theaters.json"
    d = json.loads(tp.read_text())
    d["week_of"] = week
    d["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tp.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print(f"Theaters week_of -> {week}")

    # Commit + push
    r = subprocess.run(
        ["git", "add", "-A", "public/data/streaming-picks.json", "public/data/now-in-theaters.json"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["git", "commit", "-m", f"chore: weekly entertainment refresh ({week})"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    print(r.stdout.strip() or r.stderr.strip())
    r = subprocess.run(["git", "push", "origin", "main"], cwd=REPO, capture_output=True, text=True, timeout=120)
    print(r.stdout.strip()[-500:] or r.stderr.strip()[-500:])
    print("OK" if ok else "DONE WITH WARNINGS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
