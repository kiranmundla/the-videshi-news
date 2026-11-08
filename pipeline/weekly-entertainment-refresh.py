#!/usr/bin/env python3
"""Weekly entertainment feed refresh for The Videshi.

Regenerates streaming-picks.json (self-updating week label), enriches
now-in-theaters.json trailers/cast, and rolls its week_of label to the
current Mon–Sun week. Created 2026-10-02 after the site audit found
"What to Watch" showing Aug 31 – Sep 06 and "Now in Theaters" showing
Sep 21 – Sep 27 on Oct 2.

Box-office guard (added 2026-11-07, Kiran's go): boxoffice.json slipped
stale three times (Oct 5, Oct 12, Oct 26) because nothing in this script
touched it — the builder only ran when someone hand-researched a figures
file. This script now (a) rebuilds boxoffice.json from the current week's
figures file (pipeline/boxoffice-figures-<date>.json) when one exists, and
(b) FAILS LOUD (exit 1, run reports failure naming box office) when no
current-week figures file exists or the resulting boxoffice.json is not
fresh for the current Mon–Sun week. Reporting success on stale box-office
data is the failure this guard exists to prevent.
"""
import json
import re
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


def current_monday(now=None):
    now = now or datetime.now(timezone.utc)
    return (now - timedelta(days=now.weekday())).date()


FIGURES_RE = re.compile(r"^boxoffice-figures-(\d{4}-\d{2}-\d{2})\.json$")


def find_current_week_figures(pipe_dir, monday):
    """Newest pipeline/boxoffice-figures-<date>.json dated within the
    current Mon–Sun week, or None. Figures files are hand-researched by the
    cron worker per the coverage rule; this only locates them."""
    sunday = monday + timedelta(days=6)
    best = None
    for p in Path(pipe_dir).glob("boxoffice-figures-*.json"):
        m = FIGURES_RE.match(p.name)
        if not m:
            continue
        try:
            d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        except ValueError:
            continue
        if monday <= d <= sunday and (best is None or d > best[0]):
            best = (d, p)
    return best[1] if best else None


def boxoffice_freshness_problem(data, week_label, monday):
    """None if boxoffice.json is fresh for the current week, else a string
    naming the problem. Fresh = week_of is the current Mon–Sun label AND
    as_of falls inside the current week (a previous week's file verified
    'fresh' under the old 8-day window three times — that window is gone)."""
    if not isinstance(data, dict) or not data.get("films"):
        return "boxoffice.json missing or has no films"
    if data.get("week_of") != week_label:
        return (f"boxoffice.json week_of is {data.get('week_of')!r}, "
                f"expected current week {week_label!r}")
    as_of = str(data.get("as_of") or "")
    sunday = monday + timedelta(days=6)
    if not (monday.isoformat() <= as_of <= sunday.isoformat()):
        return (f"boxoffice.json as_of is {as_of!r}, outside the current "
                f"week ({monday.isoformat()} – {sunday.isoformat()})")
    return None


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

    # Box office: rebuild from this week's researched figures file, then
    # verify freshness. Runs AFTER the theaters week roll because
    # build-boxoffice.py takes week_of from now-in-theaters.json.
    monday = current_monday()
    figures = find_current_week_figures(PIPE, monday)
    if figures is not None:
        print(f"Box office figures file: {figures.name}")
        ok &= run([sys.executable, "-u", "build-boxoffice.py", "--figures", str(figures)])
    else:
        print(f"!! BOX OFFICE: no figures file for the current week "
              f"(expected pipeline/boxoffice-figures-<date>.json dated "
              f"{monday.isoformat()} – {(monday + timedelta(days=6)).isoformat()})",
              file=sys.stderr)
        ok = False
    try:
        bo = json.loads((DATA / "boxoffice.json").read_text())
    except Exception as e:
        bo, problem = None, f"boxoffice.json unreadable: {e}"
    else:
        problem = boxoffice_freshness_problem(bo, week, monday)
    if problem:
        print(f"!! BOX OFFICE STALE: {problem} — the run FAILS so stale "
              f"box-office data is never reported as a successful refresh.",
              file=sys.stderr)
        ok = False
    else:
        print(f"Box office fresh: week_of={bo['week_of']}, as_of={bo['as_of']}, "
              f"{len(bo['films'])} films")

    # Commit + push
    r = subprocess.run(
        ["git", "add", "-A", "public/data/streaming-picks.json", "public/data/now-in-theaters.json", "public/data/boxoffice.json"],
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
