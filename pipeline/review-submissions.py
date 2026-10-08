#!/usr/bin/env python3 -u
"""Moderate community submissions for The Videshi.

The web forms write to community_submissions with status='pending'.
NOTHING goes live without approval here.

Usage:
  python3 -u pipeline/review-submissions.py --list        # show pending queue
  python3 -u pipeline/review-submissions.py --stats       # queue counts
  python3 -u pipeline/review-submissions.py              # interactive review

On approve:
  event    -> inserted into `events` (source='community'), geocoded via
              zippopotam when a zip is present; picked up by prebuild-feeds.
  business -> inserted into `directory_listings` (source='community',
              verified=true); picked up by prebuild-feeds.

Supabase access is via curl (urllib/requests fail through the proxy).
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
HOST = SUPABASE_URL.replace("https://", "")


def sb(method: str, path: str, data: dict | None = None, params: str = ""):
    """Supabase REST via curl."""
    url = f"https://{HOST}/rest/v1/{path}{params}"
    cmd = [
        "curl", "-sS", "-X", method, url,
        "-H", f"apikey: {SERVICE_KEY}",
        "-H", f"Authorization: Bearer {SERVICE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
    ]
    if data is not None:
        cmd += ["-d", json.dumps(data)]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise RuntimeError(f"curl failed: {out.stderr[:200]}")
    try:
        return json.loads(out.stdout) if out.stdout.strip() else []
    except json.JSONDecodeError:
        raise RuntimeError(f"bad JSON: {out.stdout[:200]}")


def get_pending() -> list[dict]:
    return sb("GET", "community_submissions",
              params="?status=eq.pending&order=submitted_at.asc")


def get_stats() -> dict:
    rows = sb("GET", "community_submissions", params="?select=status,type")
    from collections import Counter
    return dict(Counter((r["type"], r["status"]) for r in rows))


def geocode_zip(zip_code: str) -> tuple[float | None, float | None]:
    try:
        out = subprocess.run(
            ["curl", "-sS", "--max-time", "10",
             f"https://api.zippopotam.us/us/{zip_code}"],
            capture_output=True, text=True, timeout=15)
        d = json.loads(out.stdout)
        p = d["places"][0]
        return float(p["latitude"]), float(p["longitude"])
    except Exception:
        return None, None


def slugify(*parts: str) -> str:
    s = "-".join(parts)
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:80] or "submission"


def approve_event(sub: dict) -> str:
    lat, lon = (geocode_zip(sub["zip"]) if sub.get("zip") else (None, None))
    row = {
        "title": sub["name"],
        "date": sub.get("event_date"),
        "time": sub.get("event_time"),
        "venue_name": sub.get("venue"),
        "street_address": sub.get("address"),
        "city": sub.get("city"),
        "state": sub.get("state"),
        "zip_code": sub.get("zip"),
        "latitude": lat,
        "longitude": lon,
        "category": sub.get("category") or "Community",
        "description": (sub.get("description") or "")[:500],
        "long_description": sub.get("description"),
        "ticket_url": sub.get("ticket_url"),
        "image_url": sub.get("image_url"),
        "organizer": sub.get("submitter_email"),
        "source": "community",
        "slug": slugify(sub["name"], sub.get("event_date") or ""),
    }
    row = {k: v for k, v in row.items() if v is not None}
    created = sb("POST", "events", data=row)
    return created[0]["id"] if created else ""


def approve_business(sub: dict) -> str:
    lat, lon = (geocode_zip(sub["zip"]) if sub.get("zip") else (None, None))
    row = {
        "name": sub["name"],
        "category": (sub.get("category") or "").split(" / ")[0] or "Community",
        "subcategory": (sub.get("category") or "").split(" / ")[1]
        if " / " in (sub.get("category") or "") else None,
        "description": sub.get("description"),
        "phone": sub.get("phone"),
        "website": sub.get("website"),
        "address": sub.get("address"),
        "city": sub.get("city"),
        "state": sub.get("state"),
        "zip": sub.get("zip"),
        "latitude": lat,
        "longitude": lon,
        "hours": sub.get("hours"),
        "image_url": sub.get("image_url"),
        "source": "community",
        "verified": True,
        "slug": slugify(sub["name"], sub.get("city") or ""),
    }
    row = {k: v for k, v in row.items() if v is not None}
    created = sb("POST", "directory_listings", data=row)
    return created[0]["id"] if created else ""


def set_status(sub_id: str, status: str, notes: str = "",
               live_id: str = "", live_table: str = ""):
    patch = {"status": status, "review_notes": notes or None,
             "reviewed_at": "now()"}
    if live_id:
        patch["live_id"] = live_id
        patch["live_table"] = live_table
    sb("PATCH", "community_submissions",
       data=patch, params=f"?id=eq.{sub_id}")


def show(sub: dict):
    print(f"\n{'='*60}")
    print(f"[{sub['type'].upper()}] {sub['name']}")
    print(f"  id: {sub['id']}  submitted: {sub['submitted_at'][:10]}")
    if sub.get("description"):
        print(f"  desc: {sub['description'][:220]}")
    loc = ", ".join(x for x in
                    [sub.get("venue"), sub.get("address"),
                     sub.get("city"), sub.get("state"), sub.get("zip")] if x)
    if loc:
        print(f"  where: {loc}")
    if sub["type"] == "event":
        print(f"  when: {sub.get('event_date')} {sub.get('event_time') or ''}")
        if sub.get("ticket_url"):
            print(f"  tickets: {sub['ticket_url']}")
    else:
        for k in ("phone", "website", "hours"):
            if sub.get(k):
                print(f"  {k}: {sub[k]}")
    print(f"  category: {sub.get('category')}")
    print(f"  submitter: {sub.get('submitter_name') or '-'} "
          f"<{sub.get('submitter_email') or '-'}>")
    if sub.get("image_url"):
        print(f"  image: {sub['image_url']}")


def interactive():
    pending = get_pending()
    if not pending:
        print("Queue is empty — nothing pending.")
        return
    print(f"{len(pending)} submission(s) pending review.")
    for sub in pending:
        show(sub)
        while True:
            try:
                c = input("  [a]pprove  [r]eject  [s]pam  s[k]ip  [q]uit > "
                          ).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nBye.")
                return
            if c == "q":
                return
            if c == "k":
                break
            if c in ("a", "r", "s"):
                notes = ""
                if c != "a":
                    notes = input("  review note (optional): ").strip()
                if c == "a":
                    try:
                        live_table = ("events" if sub["type"] == "event"
                                      else "directory_listings")
                        live_id = (approve_event(sub) if sub["type"] == "event"
                                   else approve_business(sub))
                        set_status(sub["id"], "approved", notes,
                                   live_id, live_table)
                        print(f"  ✓ approved -> {live_table} {live_id[:8]}")
                    except Exception as e:
                        print(f"  ✗ approve failed: {e}")
                else:
                    status = "rejected" if c == "r" else "spam"
                    set_status(sub["id"], status, notes)
                    print(f"  ✓ marked {status}")
                break
            print("  huh? a/r/s/k/q")


def main():
    if not SUPABASE_URL or not SERVICE_KEY:
        print("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY "
              "(source ~/workspace/.env.supabase)", file=sys.stderr)
        sys.exit(1)
    if "--stats" in sys.argv:
        for (t, s), n in sorted(get_stats().items()):
            print(f"{t:10} {s:10} {n}")
        return
    if "--list" in sys.argv:
        pending = get_pending()
        if not pending:
            print("Queue is empty.")
            return
        for sub in pending:
            print(f"{sub['submitted_at'][:10]} [{sub['type']}] "
                  f"{sub['name'][:60]} ({sub.get('city')}, {sub.get('state')})")
        return
    interactive()


if __name__ == "__main__":
    main()
