"""
Google Places API daily budget guard.
All directory scripts should call check_budget() before making a Places API call.

State file: pipeline/places-usage.json
Resets daily at midnight UTC.
"""

import json, os, time
from datetime import datetime, timezone

STATE_FILE = os.path.join(os.path.dirname(__file__), "places-usage.json")
DAILY_LIMIT = 100  # max Places API calls per day (across all scripts)

def _load():
    if not os.path.exists(STATE_FILE):
        return {"date": "", "count": 0}
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"date": "", "count": 0}

def _save(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def get_usage():
    """Return (count_today, daily_limit)."""
    state = _load()
    if state["date"] != _today():
        return 0, DAILY_LIMIT
    return state["count"], DAILY_LIMIT

def check_budget(calls_needed=1):
    """
    Check if we have budget for `calls_needed` Places API calls today.
    Returns True if allowed, False if over budget.
    Does NOT increment the counter — call record_call() after a successful API call.
    """
    state = _load()
    today = _today()
    if state["date"] != today:
        state = {"date": today, "count": 0}
        _save(state)
    return (state["count"] + calls_needed) <= DAILY_LIMIT

def record_call(n=1):
    """Record n Places API calls made."""
    state = _load()
    today = _today()
    if state["date"] != today:
        state = {"date": today, "count": 0}
    state["count"] += n
    state["date"] = today
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
