#!/usr/bin/env python3
"""
Shared delayed-publish queue for The Videshi social channels.

Kiran's delayed-publish model (2026-10-24): cron jobs do ALL the work
on schedule — article selection, exact post-text composition, reel
prep (final MP4, cover, caption, alt text) — but make ZERO connector
calls, because every facebook-cli / threads-cli / instagram-cli
publish needs Kiran's fresh approval at call time and unattended runs
kept dying on approval-card timeouts. Producers STAGE fully-ready
entries here; social-publish-flush.py publishes them later, in
created order, while Kiran is present to approve each one.

Queue file: pipeline/.state/social-publish-queue.json
  {"entries": [ {id, channel, kind, slug|reel_id, headline, text,
                 link, image_url, media_file, cover_file, alt_text,
                 reel_row_id, with_link, created_at, source}, ... ]}

channel: facebook | threads | instagram
kind:    article_post | reel_draft | reel_post

All read-modify-write goes through an flock-guarded update so the
FB / Threads / reel producers and the flush never race. Dedup rule:
the same (channel, kind, slug-or-reel-id) is never staged twice;
callers additionally filter against their published ledgers
(fb-posted.json / threads-posted.json / reel-distribution.json).
"""
import fcntl
import json
import os
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

BASE = os.path.expanduser("~/workspace/the-videshi-news/pipeline/.state")
QUEUE_FILE = os.path.join(BASE, "social-publish-queue.json")
LOCK_FILE = QUEUE_FILE + ".lock"
PACIFIC = ZoneInfo("America/Los_Angeles")

STALE_AFTER_HOURS = 48


def now_pacific_iso():
    return datetime.now(PACIFIC).isoformat(timespec="seconds")


def entry_ref(entry):
    # Reel entries carry BOTH reel_id (identity) and slug (the source
    # article, informational); dedup must key on the reel. Article
    # entries have no reel_id and key on the slug.
    return entry.get("reel_id") or entry.get("slug")


def entry_key(entry):
    return (entry.get("channel"), entry.get("kind"), entry_ref(entry))


def _read_unlocked():
    try:
        with open(QUEUE_FILE) as f:
            data = json.load(f)
        entries = data.get("entries", [])
        return entries if isinstance(entries, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _write_unlocked(entries):
    os.makedirs(BASE, exist_ok=True)
    tmp = QUEUE_FILE + f".tmp{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump({"entries": entries}, f, indent=1)
    os.replace(tmp, QUEUE_FILE)


class _LockedQueue:
    """flock-guarded read-modify-write over the queue file."""

    def __enter__(self):
        os.makedirs(BASE, exist_ok=True)
        self._fd = open(LOCK_FILE, "a+")
        fcntl.flock(self._fd, fcntl.LOCK_EX)
        self.entries = _read_unlocked()
        return self.entries

    def __exit__(self, *exc):
        try:
            if exc[0] is None:
                _write_unlocked(self.entries)
        finally:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
            self._fd.close()
        return False


def locked_queue():
    return _LockedQueue()


def load_entries():
    """Snapshot read (no lock held afterwards)."""
    with locked_queue() as entries:
        return list(entries)


def add_entry(entry):
    """Append entry unless (channel, kind, ref) is already queued.
    Assigns id/created_at when missing. Returns True if staged."""
    if not entry.get("id"):
        entry["id"] = "q-" + uuid.uuid4().hex[:12]
    if not entry.get("created_at"):
        entry["created_at"] = now_pacific_iso()
    with locked_queue() as entries:
        if any(entry_key(e) == entry_key(entry) for e in entries):
            return False
        entries.append(entry)
        return True


def remove_entry(entry_id):
    with locked_queue() as entries:
        before = len(entries)
        entries[:] = [e for e in entries if e.get("id") != entry_id]
        return len(entries) != before


def queued_refs(channel=None, kind=None):
    """Refs (slugs / reel ids) currently staged, optionally filtered."""
    return {entry_ref(e) for e in load_entries()
            if (channel is None or e.get("channel") == channel)
            and (kind is None or e.get("kind") == kind)}


def queued_slugs(channel, kind="article_post"):
    return queued_refs(channel, kind)


def age_hours(entry, now=None):
    try:
        created = datetime.fromisoformat(entry.get("created_at") or "")
        if created.tzinfo is None:
            created = created.replace(tzinfo=PACIFIC)
        now = now or datetime.now(PACIFIC)
        return (now - created).total_seconds() / 3600.0
    except Exception:
        return None


def is_stale(entry, now=None):
    age = age_hours(entry, now=now)
    return age is not None and age > STALE_AFTER_HOURS
