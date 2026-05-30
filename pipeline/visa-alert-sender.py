#!/usr/bin/env python3
"""
Visa Alert Sender
- Checks for new visa sightings since last run
- Emails matching subscribers via Resend
- Tracks last-sent timestamp to avoid duplicates
"""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta

REPO = os.path.expanduser("~/workspace/the-videshi-news")
STATE_FILE = os.path.join(REPO, "pipeline/visa-alert-state.json")

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

def supabase_get(table, params=""):
    url = f"{os.environ['SUPABASE_URL']}/rest/v1/{table}?{params}"
    req = urllib.request.Request(url, headers={
        "apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}",
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_sent_at": "2026-01-01T00:00:00Z", "total_sent": 0}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")

def send_email(to, subject, html_body):
    resend_key = os.environ.get("RESEND_API_KEY", "")
    if not resend_key:
        print(f"  SKIP (no RESEND_API_KEY): {to}")
        return False
    payload = json.dumps({
        "from": "The Videshi Visa Alerts <alerts@thevideshi.com>",
        "to": [to],
        "subject": subject,
        "html": html_body,
    }).encode()
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {resend_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"  SENT to {to}: {result.get('id', 'ok')}")
            return True
    except Exception as e:
        print(f"  FAIL to {to}: {e}")
        return False

def build_sighting_email(sightings):
    """Build HTML email for new sighting alerts."""
    cards = ""
    for s in sightings:
        consulate = s.get("consulate", "Unknown")
        visa_type = s.get("visa_type", "")
        desc = s.get("description", "")
        date_start = s.get("slot_date_start", "")
        date_end = s.get("slot_date_end", "")
        reporter = s.get("reporter_name", "Community member")
        date_range = ""
        if date_start:
            date_range = f"Slots seen: {date_start}"
            if date_end and date_end != date_start:
                date_range += f" – {date_end}"

        cards += f"""
        <div style="border:1px solid #e5e5e5;border-radius:8px;padding:16px;margin-bottom:12px;background:#fafaf9;">
          <div style="margin-bottom:8px;">
            <span style="background:#1a1a2e;color:white;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600;">{consulate}</span>
            <span style="background:#f3f4f6;padding:2px 8px;border-radius:12px;font-size:11px;margin-left:4px;">{visa_type}</span>
          </div>
          {f'<p style="color:#b45309;font-size:12px;font-weight:600;margin:0 0 6px;">📅 {date_range}</p>' if date_range else ''}
          <p style="color:#374151;font-size:13px;line-height:1.5;margin:0 0 6px;">{desc}</p>
          <p style="color:#9ca3af;font-size:11px;margin:0;">Reported by {reporter}</p>
        </div>
        """

    return f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:560px;margin:0 auto;padding:20px;">
      <div style="text-align:center;margin-bottom:24px;">
        <h1 style="font-family:Georgia,serif;font-size:22px;color:#1a1a2e;margin:0;">🛂 New Visa Slot Sightings</h1>
        <p style="color:#6b7280;font-size:13px;margin:6px 0 0;">from The Videshi Visa Tracker</p>
      </div>

      <p style="color:#374151;font-size:13px;line-height:1.5;">
        New appointment slot sightings have been reported by the community. Act fast — slots disappear quickly.
      </p>

      {cards}

      <div style="text-align:center;margin:24px 0;">
        <a href="https://www.thevideshi.com/immigration/visas" style="display:inline-block;background:#16a34a;color:white;padding:10px 24px;border-radius:8px;font-size:13px;font-weight:600;text-decoration:none;">
          View All Sightings →
        </a>
      </div>

      <div style="border-top:1px solid #e5e5e5;padding-top:16px;margin-top:24px;">
        <p style="color:#9ca3af;font-size:10px;text-align:center;margin:0;">
          You're receiving this because you signed up for Visa Slot Alerts on The Videshi.<br>
          This is a premium service offered free during our launch period.<br>
          Always verify availability on <a href="https://www.ustraveldocs.com/" style="color:#6b7280;">ustraveldocs.com</a> before booking.
        </p>
      </div>
    </div>
    """

def build_update_email(updates):
    """Build HTML email for policy/news updates."""
    items = ""
    for u in updates:
        severity_color = "#dc2626" if u.get("severity") == "high" else "#d97706" if u.get("severity") == "medium" else "#6b7280"
        items += f"""
        <div style="border-left:3px solid {severity_color};padding:8px 12px;margin-bottom:12px;background:#fafaf9;">
          <p style="font-size:11px;color:#6b7280;margin:0 0 2px;text-transform:uppercase;letter-spacing:0.5px;">{u.get('label','')}</p>
          <p style="font-size:14px;font-weight:600;color:#1a1a2e;margin:0 0 4px;font-family:Georgia,serif;">{u.get('headline','')}</p>
          <p style="font-size:12px;color:#374151;line-height:1.4;margin:0;">{u.get('summary','')}</p>
        </div>
        """

    return f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:560px;margin:0 auto;padding:20px;">
      <div style="text-align:center;margin-bottom:24px;">
        <h1 style="font-family:Georgia,serif;font-size:22px;color:#1a1a2e;margin:0;">📰 Visa Policy Update</h1>
        <p style="color:#6b7280;font-size:13px;margin:6px 0 0;">from The Videshi Immigration Hub</p>
      </div>

      {items}

      <div style="text-align:center;margin:24px 0;">
        <a href="https://www.thevideshi.com/immigration/visas" style="display:inline-block;background:#1a1a2e;color:white;padding:10px 24px;border-radius:8px;font-size:13px;font-weight:600;text-decoration:none;">
          View Full Tracker →
        </a>
      </div>

      <div style="border-top:1px solid #e5e5e5;padding-top:16px;margin-top:24px;">
        <p style="color:#9ca3af;font-size:10px;text-align:center;margin:0;">
          You're receiving this because you signed up for Visa Slot Alerts on The Videshi.<br>
          This is a premium service offered free during our launch period.
        </p>
      </div>
    </div>
    """

def main():
    load_env(os.path.expanduser("~/workspace/.env.supabase"))
    load_env(os.path.expanduser("~/workspace/.env.resend"))
    
    state = load_state()
    last_sent = state["last_sent_at"]
    now = datetime.now(timezone.utc).isoformat()
    
    print(f"Checking for new sightings since {last_sent}...")
    
    # Get new sightings
    new_sightings = supabase_get(
        "visa_sightings",
        f"created_at=gt.{last_sent}&order=created_at.desc&limit=20"
    )
    
    if not new_sightings:
        print("No new sightings. Done.")
        state["last_sent_at"] = now
        save_state(state)
        return
    
    print(f"Found {len(new_sightings)} new sighting(s)")
    
    # Get active subscribers
    subscribers = supabase_get(
        "visa_alert_subscribers",
        "active=eq.true&select=email,visa_type,channel"
    )
    
    if not subscribers:
        print("No active subscribers. Done.")
        state["last_sent_at"] = now
        save_state(state)
        return
    
    print(f"Found {len(subscribers)} active subscriber(s)")
    
    # Build email
    html = build_sighting_email(new_sightings)
    subject = f"🛂 {len(new_sightings)} New Visa Slot Sighting{'s' if len(new_sightings) > 1 else ''} — The Videshi"
    
    sent_count = 0
    for sub in subscribers:
        email = sub.get("email", "")
        if not email or email.endswith("@placeholder.local"):
            continue
        sub_type = sub.get("visa_type", "all")
        
        # Filter: if subscriber wants a specific type, only send if matching sighting exists
        if sub_type != "all":
            matching = [s for s in new_sightings if s.get("visa_type") == sub_type]
            if not matching:
                continue
            html = build_sighting_email(matching)
            subject = f"🛂 {len(matching)} New {sub_type} Slot Sighting{'s' if len(matching) > 1 else ''} — The Videshi"
        
        if send_email(email, subject, html):
            sent_count += 1
        
        # Rate limit: 2 per second (Resend free tier)
        time.sleep(0.5)
    
    print(f"Sent {sent_count} alert email(s)")
    state["last_sent_at"] = now
    state["total_sent"] = state.get("total_sent", 0) + sent_count
    save_state(state)

if __name__ == "__main__":
    main()
