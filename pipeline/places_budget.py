"""
Google Places API daily budget guard.
All directory scripts should call check_budget() before making a Places API call.

State file: pipeline/places-usage.json
Resets daily at midnight UTC.

Per-consumer allocations (added 2026-10-14, Kiran's directive): the shared
90-call daily total is split so Learn/kids expansion is guaranteed a slice.
expand-directory.py ran first and consumed all 90, starving
expand-kids-places.py (0 calls/day for days). Now each expander registers
itself via set_consumer() and gets a hard per-consumer cap inside the shared
total: kids 20, directory 70. The guarantee is order-independent — directory
can never touch the kids reserve. Once kids has had its turn for the day
(mark_consumer_done), the directory cap is released to the full shared total
so an unused kids allocation is not stranded when main runs after kids.
Scripts that never call set_consumer() are bound only by the shared total,
as before.

A third consumer, "photo_refresh" (cap 30), was added 2026-10-14 for the
Sunday directory-photo refresh that gradually restores covers nulled in
the directory-photo repair; see CONSUMER_CAPS below.
"""

import json, os, time
from datetime import datetime, timezone

STATE_FILE = os.path.join(os.path.dirname(__file__), "places-usage.json")
DAILY_LIMIT = 90  # max Places API calls per day (across all scripts)
# Recalibrated 2026-10-08: the field mask requests Enterprise-tier fields
# (photos, rating, userRatingCount), so Text Search bills ~$32-35/1000.
# 90 calls/day -> ~2,700/month -> ~$86-95/month, stays under the $100/mo
# auto-cap on GCP project 22758573703 all month. At the old 200/day
# (~$192-210/mo) the expansion silently stalls around day 14-15 when the
# cap throttles the API. Conservative per Kiran's 2026-10-07 directive;
# raise only if he approves higher spend.

# Per-consumer daily caps within the shared DAILY_LIMIT total.
# photo_refresh (added 2026-10-14): the Sunday directory-photo refresh
# restores covers nulled in the Oct-14 repair (~2 calls per cover: place
# details + photo media). Cap 30 = at most ~15 covers per run, and because
# it registers as a consumer it can never push the shared total past 90 or
# eat the kids/directory allocations — it runs Sun 04:00, after the daily
# 02:00 expansion, and simply spends whatever budget is left that day.
CONSUMER_CAPS = {"kids": 20, "directory": 70, "photo_refresh": 30}
# The consumer whose finished turn releases its unused reserve to "directory".
RESERVE_OWNER = "kids"

_CONSUMER = None  # set per-process via set_consumer()

def set_consumer(name):
    """Register this process as a budget consumer (e.g. "kids", "directory").

    Consumers named in CONSUMER_CAPS get a hard per-consumer daily cap on top
    of the shared total. Unregistered processes keep the old behavior
    (shared total only).
    """
    global _CONSUMER
    _CONSUMER = name

def _load():
    if not os.path.exists(STATE_FILE):
        return {"date": "", "count": 0, "consumers": {}, "done": {}}
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except Exception:
        return {"date": "", "count": 0, "consumers": {}, "done": {}}
    state.setdefault("consumers", {})
    state.setdefault("done", {})
    return state

def _save(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def _current_state():
    """Today's state; a stale date means a fresh day (nothing carries over)."""
    state = _load()
    if state["date"] != _today():
        return {"date": _today(), "count": 0, "consumers": {}, "done": {}}
    return state

def get_usage():
    """Return (count_today, daily_limit)."""
    state = _load()
    if state["date"] != _today():
        return 0, DAILY_LIMIT
    return state["count"], DAILY_LIMIT

def get_consumer_usage(name):
    """Calls recorded today for one consumer."""
    return _current_state()["consumers"].get(name, 0)

def consumer_done(name):
    """True if the consumer has marked its turn complete today."""
    return bool(_current_state()["done"].get(name))

def mark_consumer_done(name):
    """Mark a consumer's daily turn complete (releases its reserve)."""
    state = _current_state()
    state["done"][name] = True
    _save(state)

def _effective_cap(name, state):
    """Hard daily cap for a consumer, or None if it has no allocation."""
    cap = CONSUMER_CAPS.get(name)
    if cap is None:
        return None
    if name == "directory" and state["done"].get(RESERVE_OWNER):
        # Kids has had its turn: release any unused reserve to the main
        # expander (the shared-total check in check_budget still binds).
        return DAILY_LIMIT
    return cap

def check_budget(calls_needed=1):
    """
    Check if we have budget for `calls_needed` Places API calls today.
    Returns True if allowed, False if over budget.
    Does NOT increment the counter — call record_call() after a successful API call.
    Enforces the shared daily total and, for registered consumers, their
    per-consumer allocation cap.
    """
    state = _load()
    today = _today()
    if state["date"] != today:
        state = {"date": today, "count": 0, "consumers": {}, "done": {}}
        _save(state)
    if (state["count"] + calls_needed) > DAILY_LIMIT:
        return False
    if _CONSUMER is not None:
        cap = _effective_cap(_CONSUMER, state)
        if cap is not None and \
                (state["consumers"].get(_CONSUMER, 0) + calls_needed) > cap:
            return False
    return True

def record_call(n=1):
    """Record n Places API calls made (shared total + this process's consumer)."""
    state = _current_state()
    state["count"] += n
    if _CONSUMER is not None:
        state["consumers"][_CONSUMER] = state["consumers"].get(_CONSUMER, 0) + n
    state["date"] = _today()
    _save(state)
    return state["count"]

def budget_remaining():
    """How many calls left today."""
    used, limit = get_usage()
    return max(0, limit - used)

def guarded_places_call(call_fn, *args, **kwargs):
    """
    Wrapper: checks budget, makes the call, records it.
    Raises RuntimeError if over budget.
    """
    if not check_budget():
        used, limit = get_usage()
        raise RuntimeError(
            f"Places API daily budget exhausted: {used}/{limit} calls used today. "
            f"Skipping to avoid cost overrun."
        )
    result = call_fn(*args, **kwargs)
    record_call()
    return result
