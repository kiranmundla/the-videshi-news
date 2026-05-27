#!/usr/bin/env python3
"""
The Videshi Daily Briefing
Sends a short daily news digest to all newsletter subscribers via Resend.
Skips Sundays — the weekly edition covers that day.

Usage:
  python3 send-newsletter-daily.py              # Send to all subscribers
  python3 send-newsletter-daily.py --test       # Send only to editor@thevideshi.com
  python3 send-newsletter-daily.py --dry-run    # Build HTML and save locally, don't send
"""

import argparse
import hashlib
import hmac
import json
import os
import re
import sys
import time
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

import requests

# ── Config ──────────────────────────────────────────────────────────────────

SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
FROM_ADDRESS = "The Videshi <noreply@thevideshi.com>"
SITE_URL = "https://thevideshi.com"
UNSUB_SECRET = "videshi-unsub-2026"

CATEGORY_EMOJI = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "travel": "✈️",
    "lifestyle-health": "🧘",
    "markets-finance": "📈",
    "technology": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

CATEGORY_LABEL = {
    "news": "NEWS",
    "immigration": "IMMIGRATION",
    "nri-world": "NRI WORLD",
    "travel": "TRAVEL",
    "lifestyle-health": "LIFESTYLE",
    "markets-finance": "MARKETS",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

# Preferred order for picking stories across categories
CATEGORY_ORDER = [
    "news", "sports", "entertainment", "immigration",
    "nri-world", "markets-finance", "technology",
    "lifestyle-health", "travel", "food",
]


# ── Helpers ─────────────────────────────────────────────────────────────────

def load_env(path):
    """Load a .env file into a dict."""
    env = {}
    p = Path(path).expanduser()
    if not p.exists():
        return env
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def supabase_get(path, params=None):
    """GET from Supabase REST API."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def make_unsub_token(email):
    """HMAC-SHA256 token for unsubscribe verification."""
    return hmac.new(
        UNSUB_SECRET.encode(), email.lower().encode(), hashlib.sha256
    ).hexdigest()[:16]


def summarise(body_md, max_sentences=2):
    """Extract first N sentences from markdown body as plain text."""
    if not body_md:
        return ""
    # Strip markdown images, links, headers, bold/italic
    text = re.sub(r"!\[.*?\]\(.*?\)", "", body_md)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
    text = re.sub(r"\n{2,}", "\n", text).strip()
    # Get sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)
    # Filter out very short fragments
    sentences = [s for s in sentences if len(s) > 30]
    return " ".join(sentences[:max_sentences]).strip()


# ── Data fetching ───────────────────────────────────────────────────────────

def fetch_subscribers():
    """Get all newsletter subscribers."""
    return supabase_get("newsletter_subscribers", {"select": "id,email,subscribed_at"})


def fetch_daily_articles(since_iso):
    """Fetch published articles from the last 24 hours."""
    params = {
        "select": "id,slug,headline,subheadline,category,image_url,body,published_at",
        "status": "eq.published",
        "published_at": f"gte.{since_iso}",
        "order": "published_at.desc",
        "limit": "30",
    }
    return supabase_get("p2_articles", params)


def score_article(a):
    """Score an article by quality signals (higher = better pick for newsletter).
    No viewer data yet, so we use editorial quality heuristics."""
    score = 0
    body = a.get("body", "") or ""
    headline = a.get("headline", "") or ""
    subheadline = a.get("subheadline", "") or ""

    # Body length — meatier articles score higher
    word_count = len(body.split())
    if word_count >= 700:
        score += 3
    elif word_count >= 500:
        score += 2
    elif word_count >= 300:
        score += 1

    # Has image — polished article
    if a.get("image_url"):
        score += 2

    # Has subheadline — editorial effort
    if subheadline and len(subheadline) > 20:
        score += 1

    # Headline quality — specifics (numbers, names, quotes) signal strong writing
    if re.search(r'\d', headline):
        score += 1  # contains a number
    if len(headline) >= 40 and len(headline) <= 160:
        score += 1  # good headline length

    # Source count — more sources = better researched
    source_mentions = body.lower().count("according to") + body.lower().count("reported") + body.lower().count("sources say")
    if source_mentions >= 2:
        score += 1

    return score


def pick_daily_stories(articles):
    """Pick a hero + 5 stories across categories, ranked by quality score."""
    # Sort by score (desc), then recency as tiebreaker
    scored = sorted(articles, key=lambda a: (score_article(a), a.get("published_at", "")), reverse=True)

    # Hero: best-scoring article with an image
    hero = None
    for a in scored:
        if a.get("image_url") and a.get("slug"):
            hero = a
            break

    hero_id = hero["id"] if hero else None
    hero_cat = hero.get("category") if hero else None

    by_cat = {}
    for a in scored:
        if not a.get("slug") or a["id"] == hero_id:
            continue
        cat = a.get("category", "news")
        if cat not in by_cat:
            by_cat[cat] = a  # best-scoring article per category

    stories = []
    for cat in CATEGORY_ORDER:
        if cat == hero_cat:
            continue
        if cat in by_cat:
            stories.append(by_cat[cat])
        if len(stories) >= 5:
            break

    return hero, stories


# ── HTML email builder ──────────────────────────────────────────────────────

def build_daily_html(hero, stories, date_label, unsub_url):
    """Build the daily briefing HTML email."""

    # Hero section
    hero_html = ""
    if hero:
        hero_summary = summarise(hero.get("body", ""), 2) or hero.get("subheadline", "")
        hero_cat = hero.get("category", "news")
        hero_emoji = CATEGORY_EMOJI.get(hero_cat, "📰")
        hero_label = CATEGORY_LABEL.get(hero_cat, hero_cat.upper())
        hero_url = f"{SITE_URL}/articles/{hero['slug']}"
        hero_img = hero.get("image_url", "")

        hero_html = f"""
        <tr>
          <td style="padding: 0 24px 24px 24px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="padding-bottom: 12px;">
                  <span style="font-size: 11px; font-weight: 700; color: #c9a84c; letter-spacing: 1.5px; text-transform: uppercase;">
                    {hero_emoji} {hero_label} &mdash; TOP STORY
                  </span>
                </td>
              </tr>
              {"<tr><td style='padding-bottom: 16px;'><a href='" + hero_url + "' target='_blank'><img src='" + hero_img + "' alt='' width='100%' style='display: block; border-radius: 8px; max-width: 100%; height: auto;' /></a></td></tr>" if hero_img else ""}
              <tr>
                <td>
                  <a href="{hero_url}" target="_blank" style="font-size: 20px; font-weight: 700; color: #1a1a2e; text-decoration: none; line-height: 1.3;">
                    {hero['headline']}
                  </a>
                </td>
              </tr>
              <tr>
                <td style="padding-top: 10px; font-size: 14px; color: #444; line-height: 1.6;">
                  {hero_summary}
                </td>
              </tr>
              <tr>
                <td style="padding-top: 14px;">
                  <a href="{hero_url}" target="_blank" style="display: inline-block; padding: 10px 24px; background-color: #c9a84c; color: #ffffff; font-size: 14px; font-weight: 600; text-decoration: none; border-radius: 6px;">
                    Read more &rarr;
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        """

    # Group stories by category (preserving order)
    grouped = OrderedDict()
    for s in stories:
        cat = s.get("category", "news")
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(s)

    # Build category blocks
    category_blocks = ""
    for cat, cat_stories in grouped.items():
        emoji = CATEGORY_EMOJI.get(cat, "📰")
        label = CATEGORY_LABEL.get(cat, cat.upper())

        article_rows = ""
        for s in cat_stories:
            url = f"{SITE_URL}/articles/{s['slug']}"
            body_summary = summarise(s.get("body", ""), 2) or s.get("subheadline", "")
            if len(body_summary) > 180:
                body_summary = body_summary[:177].rsplit(" ", 1)[0] + "…"
            img_url = s.get("image_url", "")

            # Thumbnail + text layout if image exists, text-only otherwise
            if img_url:
                article_rows += f"""
              <tr>
                <td style="padding: 6px 0 12px 0;">
                  <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td width="80" style="vertical-align: top; padding-right: 12px;">
                        <a href="{url}" target="_blank">
                          <img src="{img_url}" alt="" width="80" height="80" style="display: block; border-radius: 6px; width: 80px; height: 80px; object-fit: cover;" />
                        </a>
                      </td>
                      <td style="vertical-align: top;">
                        <a href="{url}" target="_blank" style="font-size: 15px; font-weight: 600; color: #1a1a2e; text-decoration: none; line-height: 1.3;">
                          {s['headline']}
                        </a>
                        <br />
                        <span style="font-size: 13px; color: #666; line-height: 1.4;">
                          {body_summary}
                        </span>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
                """
            else:
                article_rows += f"""
              <tr>
                <td style="padding: 6px 0 12px 0;">
                  <a href="{url}" target="_blank" style="font-size: 15px; font-weight: 600; color: #1a1a2e; text-decoration: none; line-height: 1.3;">
                    {s['headline']}
                  </a>
                  <br />
                  <span style="font-size: 13px; color: #666; line-height: 1.4;">
                    {body_summary}
                  </span>
                </td>
              </tr>
                """

        category_blocks += f"""
          <tr>
            <td style="padding: 14px 0 4px 0;">
              <span style="font-size: 12px; font-weight: 700; color: #c9a84c; letter-spacing: 1.5px; text-transform: uppercase;">
                {emoji} {label}
              </span>
            </td>
          </tr>
          {article_rows}
          <tr><td style="border-bottom: 1px solid #eee;"></td></tr>
        """

    # Stories section
    stories_html = ""
    if category_blocks:
        stories_html = f"""
          <!-- TOP STORIES -->
          <tr>
            <td style="padding: 0 24px 16px 24px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                {category_blocks}
              </table>
            </td>
          </tr>
        """

    # Quick links row (compact text links)
    quick_links_html = f"""
          <!-- QUICK LINKS -->
          <tr>
            <td style="padding: 4px 24px 24px 24px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-top: 1px solid #eee;">
                <tr>
                  <td style="padding-top: 16px; text-align: center; font-size: 13px; color: #999;">
                    <a href="{SITE_URL}/travel" target="_blank" style="color: #c9a84c; text-decoration: none; font-weight: 600;">✈️ Travel</a>
                    &nbsp;&nbsp;·&nbsp;&nbsp;
                    <a href="{SITE_URL}/cars" target="_blank" style="color: #c9a84c; text-decoration: none; font-weight: 600;">🚗 Cars</a>
                    &nbsp;&nbsp;·&nbsp;&nbsp;
                    <a href="{SITE_URL}/immigration" target="_blank" style="color: #c9a84c; text-decoration: none; font-weight: 600;">🛂 Immigration</a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
    """

    # Full email
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>The Videshi Daily</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f7; font-family: Arial, Helvetica, sans-serif; -webkit-font-smoothing: antialiased;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f4f4f7;">
    <tr>
      <td align="center" style="padding: 24px 12px;">
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; width: 100%; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">

          <!-- HEADER -->
          <tr>
            <td style="background-color: #1a1a2e; padding: 22px 24px; text-align: center;">
              <div style="font-size: 26px; font-weight: 700; color: #ffffff; letter-spacing: 1px;">
                The Videshi
              </div>
              <div style="font-size: 12px; color: #c9a84c; margin-top: 5px; letter-spacing: 0.5px;">
                Your daily Indian diaspora briefing
              </div>
              <div style="font-size: 11px; color: #aaa; margin-top: 6px;">
                {date_label}
              </div>
            </td>
          </tr>

          <!-- SPACER -->
          <tr><td style="height: 16px;"></td></tr>

          <!-- HERO -->
          {hero_html}

          {stories_html}

          {quick_links_html}

          <!-- FOOTER -->
          <tr>
            <td style="background-color: #1a1a2e; padding: 20px 24px; text-align: center;">
              <div style="font-size: 14px; font-weight: 700; color: #ffffff; margin-bottom: 6px;">
                The Videshi
              </div>
              <div style="font-size: 11px; color: #aaa; margin-bottom: 10px;">
                Your daily source for Indian diaspora news
              </div>
              <div style="margin-bottom: 12px;">
                <table cellpadding="0" cellspacing="0" border="0" align="center">
                  <tr>
                    <td style="padding: 0 8px;"><a href="https://x.com/thevideshi" target="_blank"><img src="https://cdn.simpleicons.org/x/c9a84c" alt="X" width="20" height="20" style="display: block;" /></a></td>
                    <td style="padding: 0 8px;"><a href="https://www.threads.net/@the.videshi" target="_blank"><img src="https://cdn.simpleicons.org/threads/c9a84c" alt="Threads" width="20" height="20" style="display: block;" /></a></td>
                    <td style="padding: 0 8px;"><a href="https://www.instagram.com/the.videshi" target="_blank"><img src="https://cdn.simpleicons.org/instagram/c9a84c" alt="Instagram" width="20" height="20" style="display: block;" /></a></td>
                    <td style="padding: 0 8px;"><a href="https://www.youtube.com/@TheVideshi" target="_blank"><img src="https://cdn.simpleicons.org/youtube/c9a84c" alt="YouTube" width="20" height="20" style="display: block;" /></a></td>
                  </tr>
                </table>
              </div>
              <div style="border-top: 1px solid #333; padding-top: 10px;">
                <a href="{SITE_URL}" target="_blank" style="color: #c9a84c; text-decoration: none; font-size: 11px;">thevideshi.com</a>
              </div>
              <div style="margin-top: 10px;">
                <a href="{unsub_url}" target="_blank" style="color: #777; text-decoration: underline; font-size: 10px;">
                  Unsubscribe
                </a>
              </div>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    return html


# ── Send via Resend ─────────────────────────────────────────────────────────

def send_email(to_email, subject, html_body, resend_key, unsub_url):
    """Send one email via Resend API."""
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
            "html": html_body,
            "headers": {
                "List-Unsubscribe": f"<{unsub_url}>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            },
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="The Videshi Daily Briefing")
    parser.add_argument("--test", action="store_true", help="Send only to editor@thevideshi.com")
    parser.add_argument("--dry-run", action="store_true", help="Build HTML and save locally, don't send")
    args = parser.parse_args()

    # Sunday check — weekly edition runs on Sundays instead
    now = datetime.now(timezone.utc)
    # Use PT for day-of-week check
    from zoneinfo import ZoneInfo
    now_pt = now.astimezone(ZoneInfo("America/Los_Angeles"))
    if now_pt.weekday() == 6 and not args.test and not args.dry_run:
        print("☀️ Sunday — skipping daily (weekly edition runs today)")
        sys.exit(0)

    # Load env
    supabase_env = load_env("~/workspace/.env.supabase")
    resend_env = load_env("~/workspace/.env.resend")

    global SUPABASE_KEY
    SUPABASE_KEY = supabase_env.get("SUPABASE_SERVICE_ROLE_KEY", "")
    resend_key = resend_env.get("RESEND_API_KEY", "")

    if not SUPABASE_KEY:
        print("❌ SUPABASE_SERVICE_ROLE_KEY not found in .env.supabase")
        sys.exit(1)
    if not resend_key and not args.dry_run:
        print("❌ RESEND_API_KEY not found in .env.resend")
        sys.exit(1)

    # Date range: past 24 hours
    since = now - timedelta(hours=24)
    since_iso = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    date_label = now_pt.strftime("%A, %B %d, %Y")  # e.g. "Wednesday, May 27, 2026"

    print(f"📰 The Videshi Daily Briefing")
    print(f"   Date: {date_label}")
    print()

    # Fetch articles
    print("📥 Fetching articles…")
    articles = fetch_daily_articles(since_iso)
    print(f"   Found {len(articles)} published articles in the past 24h")

    if not articles:
        print("⚠ No articles in the past 24h — skipping daily briefing.")
        sys.exit(0)

    # Pick hero + stories
    hero, stories = pick_daily_stories(articles)
    if hero:
        print(f"   Hero: [{hero.get('category', '?')}] {hero['headline'][:65]}…")
    print(f"   Selected {len(stories)} stories across {len(set(s.get('category') for s in stories))} categories")
    for s in stories:
        cat = s.get("category", "?")
        print(f"     [{cat}] {s['headline'][:65]}…")

    # Build subject
    subject = f"The Videshi Daily — {now_pt.strftime('%B %d, %Y')}"

    # Get subscribers
    if args.test:
        subscribers = [{"email": "editor@thevideshi.com"}]
        print(f"\n🧪 TEST MODE — sending only to editor@thevideshi.com")
    elif args.dry_run:
        subscribers = []
        print(f"\n🔍 DRY RUN — building HTML only")
    else:
        print("📥 Fetching subscribers…")
        subscribers = fetch_subscribers()
        print(f"   {len(subscribers)} subscriber(s)")

    if not subscribers and not args.dry_run:
        print("⚠ No subscribers — nothing to send.")
        sys.exit(0)

    # Build preview HTML
    preview_unsub = f"{SITE_URL}/unsubscribe?email=preview@example.com&token=preview"
    preview_html = build_daily_html(hero, stories, date_label, preview_unsub)

    if args.dry_run:
        out_dir = Path(__file__).parent / "newsletter-previews"
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / f"daily-{now.strftime('%Y-%m-%d')}.html"
        out_path.write_text(preview_html)
        print(f"\n✅ HTML saved to {out_path}")
        print(f"   Subject: {subject}")
        return

    # Send to each subscriber
    sent = 0
    errors = []
    for sub in subscribers:
        email = sub["email"]
        token = make_unsub_token(email)
        unsub_url = f"{SITE_URL}/unsubscribe?email={quote(email)}&token={token}"
        html = build_daily_html(hero, stories, date_label, unsub_url)

        try:
            result = send_email(email, subject, html, resend_key, unsub_url)
            sent += 1
            print(f"   ✅ Sent to {email} (id: {result.get('id', '?')})")
        except Exception as e:
            errors.append((email, str(e)))
            print(f"   ❌ Failed for {email}: {e}")

        # Rate limit between sends
        if len(subscribers) > 1:
            time.sleep(1)

    # Log results
    log_path = Path(__file__).parent / "newsletter-log.json"
    try:
        log = json.loads(log_path.read_text()) if log_path.exists() else []
    except:
        log = []
    log.append({
        "type": "daily",
        "sent_at": now.isoformat() + "Z",
        "subject": subject,
        "subscribers": len(subscribers),
        "sent": sent,
        "errors": len(errors),
        "hero_slug": hero["slug"] if hero else None,
        "story_count": len(stories),
    })
    log_path.write_text(json.dumps(log, indent=2))

    # Archive the newsletter HTML
    archive_dir = Path(__file__).parent / "newsletter-archive"
    archive_dir.mkdir(exist_ok=True)
    archive_path = archive_dir / f"daily-{now.strftime('%Y-%m-%d')}.html"
    archive_html = build_daily_html(hero, stories, date_label, "#")
    archive_path.write_text(archive_html)
    print(f"   Archived: {archive_path}")

    print(f"\n{'='*50}")
    print(f"📬 Daily briefing sent!")
    print(f"   Delivered: {sent}/{len(subscribers)}")
    if errors:
        print(f"   Errors: {len(errors)}")
        for email, err in errors:
            print(f"     - {email}: {err}")
    print(f"   Subject: {subject}")


if __name__ == "__main__":
    main()
