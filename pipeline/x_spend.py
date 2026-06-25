#!/usr/bin/env python3
"""
x_spend.py — The Videshi X-API spend meter + hard budget guard.

Single source of truth for how much we've spent on the X API this calendar
month, and a kill-switch so no job can push us past MONTHLY_BUDGET.

Rates (X pay-per-use, verified 2026-06):
  read  (post returned by search/timeline) : $0.005
  user  (user lookup / by-username)         : $0.010
  write (post created, link-free)           : $0.015
  write (post created, contains a link)     : $0.200   <- avoid! we de-link.

Usage in a job:
    import x_spend
    if x_spend.over_budget():        # guard at top of run
        print("X-BUDGET: ceiling reached, skipping run"); sys.exit(0)
    ...
    x_spend.add(reads=len(results))  # whenever the API returns posts
    x_spend.add(users=1)             # on a real (uncached) user lookup
    x_spend.add(writes=1)            # on a successful (de-linked) post

State persists to x-usage.json, keyed by YYYY-MM (auto-rolls each month).
Concurrency-safe via an flock on the state file.
"""
import json, os, sys, time, fcntl, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "x-usage.json")

# ---- rates ----
R_READ        = 0.005
R_USER        = 0.010
R_WRITE       = 0.015
R_WRITE_LINK  = 0.200

# ---- budget ----
MONTHLY_BUDGET = float(os.environ.get("X_MONTHLY_BUDGET", "25.0"))
# Soft guard fires a bit early so an in-flight run can't overshoot the hard cap.
SOFT_STOP = MONTHLY_BUDGET * 0.97


def _month():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m")


def _blank(m):
    return {"month": m, "reads": 0, "users": 0, "writes": 0,
            "writes_link": 0, "cost": 0.0}


def _load_locked(fh):
    fh.seek(0)
    raw = fh.read()
    try:
        d = json.loads(raw) if raw.strip() else {}
    except Exception:
        d = {}
    m = _month()
    if d.get("month") != m:          # new month -> reset
        d = _blank(m)
    # ensure keys
    for k, v in _blank(m).items():
        d.setdefault(k, v)
    return d


def _cost(d):
    return round(d["reads"] * R_READ
                 + d["users"] * R_USER
                 + d["writes"] * R_WRITE
                 + d["writes_link"] * R_WRITE_LINK, 4)


def add(reads=0, users=0, writes=0, writes_link=0):
    """Record real API consumption. Atomic read-modify-write under flock."""
    if not (reads or users or writes or writes_link):
        return
    fd = os.open(STATE, os.O_RDWR | os.O_CREAT, 0o644)
    with os.fdopen(fd, "r+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        d = _load_locked(fh)
        d["reads"] += int(reads)
        d["users"] += int(users)
        d["writes"] += int(writes)
        d["writes_link"] += int(writes_link)
        d["cost"] = _cost(d)
        fh.seek(0); fh.truncate()
        json.dump(d, fh, indent=2)
        fh.flush(); os.fsync(fh.fileno())
        fcntl.flock(fh, fcntl.LOCK_UN)
        return d


def month_total():
    """Current month-to-date dollars spent."""
    try:
        fd = os.open(STATE, os.O_RDONLY)
        with os.fdopen(fd, "r") as fh:
            d = _load_locked(fh)
            return _cost(d)
    except FileNotFoundError:
        return 0.0


def remaining():
    return round(MONTHLY_BUDGET - month_total(), 4)


def over_budget(headroom=0.0):
    """True if month-to-date (plus optional reserve) has hit the soft stop.
    Jobs call this at startup and bail out quietly if True."""
    return (month_total() + headroom) >= SOFT_STOP


def status_line():
    d_cost = month_total()
    return (f"X-SPEND {_month()}: ${d_cost:.2f} / ${MONTHLY_BUDGET:.2f} "
            f"({100*d_cost/MONTHLY_BUDGET:.0f}%), ${remaining():.2f} left")


if __name__ == "__main__":
    # CLI: show status, or `--reset` to clear this month (manual override).
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        with open(STATE, "w") as fh:
            json.dump(_blank(_month()), fh, indent=2)
        print("reset:", status_line())
    else:
        print(status_line())
