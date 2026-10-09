#!/usr/bin/env python3
"""
The Videshi WhatsApp Digest — ready-to-paste morning brief for Kiran.

Builds a compact WhatsApp-formatted digest (top story + quick hits +
deadlines) reusing the daily newsletter's picking logic, then emails it
to editor@thevideshi.com so Kiran can paste it into the WhatsApp channel.

WhatsApp has no posting API, so this is manual paste by design.

Runs AFTER the daily newsletter (7:15am vs 7:00am) and picks from articles
the newsletter didn't use (newslettered_at is null filter).

Usage:
  python3 send-whatsapp-digest.py              # Email digest to Kiran
  python3 send-whatsapp-digest.py --test       # Same (only recipient is Kiran anyway)
  python3 send-whatsapp-digest.py --dry-run    # Print to stdout, don't send
"""

import argparse
import importlib.util
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

# ── Import shared logic from the newsletter script ──────────────────────────

_NEWSLETTER_PATH = Path(__file__).resolve().parent / "send-newsletter-daily.py"
_spec = importlib.util.spec_from_file_location("newsletter_daily", _NEWSLETTER_PATH)
_news = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_news)

# Reused functions (single source of truth — no duplicated picking logic)
load_env = _news.load_env
summarise = _news.summarise
write_why_it_matters = _news.write_why_it_matters
parse_deadlines = _news.parse_deadlines
format_deadline_when = _news.format_deadline_when
score_article = _news.score_article
pick_stories = _news.pick_stories
mark_newslettered = _news.mark_newslettered
supabase_get = _news.supabase_get

SUPABASE_URL = _news.SUPABASE_URL
FROM_ADDRESS = _news.FROM_ADDRESS
SITE_URL = "https://www.thevideshi.com"  # full www URL for pasted links
EDITOR_EMAIL = "editor@thevideshi.com"


# ── WhatsApp digest builder ─────────────────────────────────────────────────

def article_url(slug):
    return f"{SITE_URL}/articles/{slug}"


def clean_for_whatsapp(text):
    """Strip any residual markup; collapse whitespace. WhatsApp is plain text."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_whatsapp_digest(top, why_it_matters, quick_hits, deadlines, date_label):
    """Build the plain-text WhatsApp message."""
    lines = []
    lines.append("🇮🇳 *THE VIDESHI — Morning Brief*")
    lines.append(f"_{date_label}_")
    lines.append("")

    # Top story
    if top:
        lines.append("🔥 *TOP STORY*")
        lines.append(clean_for_whatsapp(top.get("headline", "")))
        take = clean_for_whatsapp(why_it_matters)
        if take:
            lines.append(take)
        if top.get("slug"):
            lines.append(f"👉 {article_url(top['slug'])}")
        lines.append("")

    # Quick hits
    if quick_hits:
        lines.append("⚡ *QUICK HITS*")
        for i, s in enumerate(quick_hits, 1):
            headline = clean_for_whatsapp(s.get("headline", ""))
            one_liner = summarise(s.get("body", ""), 1) or s.get("subheadline", "")
            one_liner = clean_for_whatsapp(one_liner)
            if len(one_liner) > 160:
                one_liner = one_liner[:157].rsplit(" ", 1)[0] + "…"
            lines.append(f"{i}. {headline} — {one_liner}")
            if s.get("slug"):
                lines.append(f"   👉 {article_url(s['slug'])}")
        lines.append("")

    # Deadlines
    if deadlines:
        lines.append("⏰ *DEADLINES*")
        for d in deadlines:
            when = format_deadline_when(d["_days_until"])
            lines.append(f"• {d['title']} — {d['date']} ({when})")
        lines.append("")

    lines.append("_thevideshi.com_")

    return "\n".join(lines)


def send_email(to_email, subject, text_body, resend_key):
    """Send a plain-text email via Resend."""
    resp = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {resend_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": FROM_ADDRESS,
            "to": [to_email],
            "subject": subject,
            "text": text_body,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_digest_articles(since_iso):
    """Fetch published articles from the last 24h, excluding already-used ones.

    The newsletter runs at 7:00am and marks its picks with newslettered_at.
    This digest runs at 7:15am and picks from what's left.
    """
    params = {
        "select": "id,slug,headline,subheadline,category,image_url,body,published_at,is_editorial,is_featured",
        "status": "eq.published",
        "published_at": f"gte.{since_iso}",
        "newslettered_at": "is.null",
        "order": "published_at.desc",
        "limit": "30",
    }
    result = supabase_get("p2_articles", params)
    if isinstance(result, dict) and result.get("code") == "42703":
        print("  ⚠ newslettered_at column not found — fetching without dedup filter")
        params.pop("newslettered_at", None)
        result = supabase_get("p2_articles", params)
    return result


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="The Videshi WhatsApp Digest")
    parser.add_argument("--test", action="store_true",
                        help="Send to editor@thevideshi.com (same as normal)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print digest to stdout, don't send")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    now_pt = now.astimezone(ZoneInfo("America/Los_Angeles"))

    # Load env
    supabase_env = load_env("~/workspace/.env.supabase")
    resend_env = load_env("~/workspace/.env.resend")
    openai_env = load_env("~/workspace/.env.openai")

    # Wire the imported module's globals (it reads these at call time)
    _news.SUPABASE_KEY = supabase_env.get("SUPABASE_SERVICE_ROLE_KEY", "")
    _news.OPENAI_API_KEY = openai_env.get("OPENAI_API_KEY", "")
    resend_key = resend_env.get("RESEND_API_KEY", "")

    if not _news.SUPABASE_KEY:
        print("❌ SUPABASE_SERVICE_ROLE_KEY not found in .env.supabase")
        sys.exit(1)
    if not resend_key and not args.dry_run:
        print("❌ RESEND_API_KEY not found in .env.resend")
        sys.exit(1)

    since = now - timedelta(hours=24)
    since_iso = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    date_label = now_pt.strftime("%B %d, %Y")  # e.g. "October 9, 2026"

    print("📱 The Videshi WhatsApp Digest")
    print(f"   Date: {date_label}")
    print()

    # Fetch articles (excluding ones the newsletter already used)
    print("📥 Fetching articles…")
    articles = fetch_digest_articles(since_iso)
    print(f"   Found {len(articles)} unused articles in the past 24h")

    if not articles:
        print("⚠ No unused articles in the past 24h — nothing to digest.")
        sys.exit(0)

    # Pick stories (same logic as newsletter)
    top, quick_hits = pick_stories(articles)
    if top:
        print(f"   Top story: [{top.get('category', '?')}] {top['headline'][:65]}…")
    print(f"   Quick hits: {len(quick_hits)}")

    # Why-it-matters take for the top story
    why_it_matters = ""
    if top:
        print("✍️  Writing 'why it matters' take…")
        why_it_matters = write_why_it_matters(top)

    # Deadlines
    deadlines = parse_deadlines(days_ahead=14)
    print(f"⏰ {len(deadlines)} deadline(s) in the next 14 days")

    # Build the WhatsApp message
    digest = build_whatsapp_digest(top, why_it_matters, quick_hits, deadlines, date_label)

    # Length check — WhatsApp messages cap at 65,536 chars; keep it comfortable
    if len(digest) > 4000:
        print(f"  ⚠ Digest is {len(digest)} chars — long for a single WhatsApp message")

    subject = f"WhatsApp digest — {now_pt.strftime('%b %d')} (ready to paste)"

    if args.dry_run:
        print(f"\n{'='*50}")
        print(digest)
        print(f"{'='*50}")
        print(f"\n✅ DRY RUN — {len(digest)} chars, not sent")
        print(f"   Subject would be: {subject}")
        return

    # Email body: paste instruction + the digest in a copy-friendly block
    email_body = (
        "Paste the below into the WhatsApp channel:\n"
        "----------------------------------------\n\n"
        f"{digest}"
    )

    try:
        result = send_email(EDITOR_EMAIL, subject, email_body, resend_key)
        print(f"   ✅ Sent to {EDITOR_EMAIL} (id: {result.get('id', '?')})")
    except Exception as e:
        print(f"   ❌ Send failed: {e}")
        sys.exit(1)

    # Mark articles as used so tomorrow's newsletter doesn't repeat them
    sent_ids = [top["id"]] if top else []
    sent_ids.extend(s["id"] for s in quick_hits)
    if sent_ids:
        mark_newslettered(sent_ids)
        print(f"   📌 Marked {len(sent_ids)} articles as used")

    # Log
    log_path = Path(__file__).parent / "whatsapp-digest-log.json"
    try:
        log = json.loads(log_path.read_text()) if log_path.exists() else []
    except Exception:
        log = []
    log.append({
        "type": "whatsapp-digest",
        "sent_at": now.isoformat() + "Z",
        "subject": subject,
        "sent_to": EDITOR_EMAIL,
        "top_story_slug": top["slug"] if top else None,
        "quick_hit_count": len(quick_hits),
        "deadline_count": len(deadlines),
        "chars": len(digest),
    })
    log_path.write_text(json.dumps(log, indent=2))

    print(f"\n{'='*50}")
    print("📬 WhatsApp digest emailed to Kiran!")
    print(f"   Subject: {subject}")


if __name__ == "__main__":
    main()
