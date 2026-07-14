#!/usr/bin/env python3
"""
recommendation-thanker.py — Send thank-you emails for new directory recommendations.

Queries directory_recommendations for pending rows with an email but no thanked_at,
sends a branded thank-you email via Resend, and marks them thanked.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
if SUPABASE_URL and not SUPABASE_URL.startswith("http"):
    SUPABASE_URL = "https://" + SUPABASE_URL
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")

if not all([SUPABASE_URL, SUPABASE_KEY, RESEND_API_KEY]):
    print("❌ Missing env vars (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, RESEND_API_KEY)")
    sys.exit(1)

FROM_EMAIL = "The Videshi <hello@thevideshi.com>"
SUBJECT = "Thanks for your recommendation! 🙏"


def supabase_get(path: str) -> list:
    """GET from Supabase REST API."""
    cmd = [
        "curl", "-s",
        f"{SUPABASE_URL}/rest/v1/{path}",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  ⚠️  Bad response from Supabase GET: {result.stdout[:200]}")
        return []


def supabase_patch(table: str, row_id: str, data: dict) -> bool:
    """PATCH a row in Supabase."""
    cmd = [
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-X", "PATCH",
        f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{row_id}",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal",
        "-d", json.dumps(data),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() == "204"


def send_email(to: str, business_name: str, city: str, state: str, recommender_name: str | None) -> bool:
    """Send thank-you email via Resend."""
    greeting = f"Hi {recommender_name}" if recommender_name else "Hi there"
    location = f"{city}, {state}" if city and state else city or state or ""

    html = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <div style="max-width:520px;margin:0 auto;padding:32px 16px;">
    <!-- Header -->
    <div style="background:#0B1D3A;border-radius:12px 12px 0 0;padding:28px 24px;text-align:center;">
      <h1 style="margin:0;color:#D4A843;font-size:22px;font-weight:700;letter-spacing:0.5px;">
        The Videshi
      </h1>
      <p style="margin:6px 0 0;color:rgba(255,255,255,0.6);font-size:12px;letter-spacing:1.5px;text-transform:uppercase;">
        Your Indian-American Community Hub
      </p>
    </div>

    <!-- Body -->
    <div style="background:#ffffff;padding:28px 24px;border-radius:0 0 12px 12px;">
      <p style="margin:0 0 16px;color:#333;font-size:15px;line-height:1.6;">
        {greeting},
      </p>

      <p style="margin:0 0 16px;color:#333;font-size:15px;line-height:1.6;">
        Thank you for recommending <strong style="color:#0B1D3A;">{business_name}</strong>{f' in <strong style="color:#0B1D3A;">{location}</strong>' if location else ''}!
        Community recommendations like yours are what make The Videshi Directory truly valuable.
      </p>

      <p style="margin:0 0 16px;color:#333;font-size:15px;line-height:1.6;">
        Our team will review your submission and add it to the directory shortly.
        Together, we're building the most comprehensive guide to Indian-owned
        businesses across America. 🇮🇳
      </p>

      <!-- CTA -->
      <div style="text-align:center;margin:24px 0;">
        <a href="https://www.thevideshi.com/directory"
           style="display:inline-block;background:#0B1D3A;color:#D4A843;text-decoration:none;padding:12px 28px;border-radius:8px;font-size:14px;font-weight:600;">
          Browse the Directory →
        </a>
      </div>

      <p style="margin:0;color:#666;font-size:14px;line-height:1.6;">
        Warm regards,<br>
        <strong style="color:#0B1D3A;">The Videshi Team</strong>
      </p>
    </div>

    <!-- Footer -->
    <div style="text-align:center;padding:16px 0;color:#999;font-size:11px;">
      <p style="margin:0;">© {datetime.now().year} The Videshi · <a href="https://www.thevideshi.com" style="color:#999;text-decoration:underline;">thevideshi.com</a></p>
    </div>
  </div>
</body>
</html>"""

    payload = json.dumps({
        "from": FROM_EMAIL,
        "to": [to],
        "subject": SUBJECT,
        "html": html,
    })

    cmd = [
        "curl", "-s",
        "-X", "POST",
        "https://api.resend.com/emails",
        "-H", f"Authorization: Bearer {RESEND_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", payload,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        resp = json.loads(result.stdout)
        if "id" in resp:
            return True
        print(f"  ⚠️  Resend error for {to}: {resp}")
        return False
    except json.JSONDecodeError:
        print(f"  ⚠️  Bad Resend response for {to}: {result.stdout[:200]}")
        return False


def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Recommendation thanker starting...")

    # Fetch unthanked recommendations with an email
    rows = supabase_get(
        "directory_recommendations"
        "?thanked_at=is.null"
        "&recommender_email=not.is.null"
        "&select=id,business_name,city,state,recommender_name,recommender_email"
        "&order=created_at.asc"
        "&limit=50"
    )

    if not rows:
        print("  No pending recommendations to thank.")
        return

    print(f"  Found {len(rows)} recommendation(s) to thank.")

    sent = 0
    for row in rows:
        email = row["recommender_email"]
        name = row.get("recommender_name")
        biz = row["business_name"]
        city = row.get("city", "")
        state = row.get("state", "")
        row_id = row["id"]

        print(f"  → Emailing {email} (recommended: {biz})...")

        if send_email(email, biz, city, state, name):
            now = datetime.now(timezone.utc).isoformat()
            if supabase_patch("directory_recommendations", row_id, {"thanked_at": now}):
                sent += 1
                print(f"    ✅ Sent & marked thanked")
            else:
                print(f"    ⚠️  Email sent but failed to mark thanked_at")
        else:
            print(f"    ❌ Failed to send email")

    print(f"\n  Done: {sent}/{len(rows)} thank-you emails sent.")


if __name__ == "__main__":
    main()
