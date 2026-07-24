#!/usr/bin/env python3
"""
article-polish.py — Single LLM call per article combining:
  1. Key takeaways (structured JSON for key_takeaways column)
  2. Data cards (stat grids, comparisons, timelines for data_cards column)
  3. Proofread (grammar fixes, irrelevant image detection)

GPT-4o-mini primary, Gemini 2.5 Flash fallback.
Called by the writer at insert time. review-articles.py remains as safety net.

Usage:
  python3 -u article-polish.py --article-id <uuid>
  python3 -u article-polish.py --article-id <uuid> --dry-run
  python3 -u article-polish.py --hours 3 --max 20       # Batch catchup
"""

import argparse, json, os, re, subprocess, sys, tempfile
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

# ── Env ──
def _load_env(path):
    p = os.path.expanduser(path)
    if not os.path.exists(p):
        return
    with open(p) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("\"'"))

_load_env("~/workspace/.env.supabase")
_load_env("~/workspace/.env.openai")
_load_env("~/workspace/.env.google-ai")

SB_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
OAI_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_KEY = os.environ.get("GOOGLE_AI_API_KEY", "")
SB_HOST = SB_URL.replace("https://", "")


def sb_get(endpoint, params=None):
    url = f"https://{SB_HOST}/rest/v1/{endpoint}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    r = subprocess.run(
        ["curl", "-s", url,
         "-H", f"apikey: {SB_KEY}",
         "-H", f"Authorization: Bearer {SB_KEY}"],
        capture_output=True, text=True, timeout=30
    )
    return json.loads(r.stdout) if r.stdout.strip() else []


def sb_patch(article_id, data):
    url = f"https://{SB_HOST}/rest/v1/p2_articles?id=eq.{article_id}"
    payload = json.dumps(data)
    r = subprocess.run(
        ["curl", "-s", "-X", "PATCH", url,
         "-H", f"apikey: {SB_KEY}",
         "-H", f"Authorization: Bearer {SB_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal",
         "-d", payload],
        capture_output=True, text=True, timeout=30
    )
    return r.returncode == 0


def extract_images(body):
    images = []
    for m in re.finditer(r'<img[^>]*?(?:alt=["\']([^"\']*)["\'])?[^>]*?(?:src=["\']([^"\']*)["\'])?[^>]*/?>',
                         body, re.IGNORECASE):
        alt = m.group(1) or ""
        src = m.group(2) or ""
        domain = src.split("/")[2] if src.count("/") >= 2 else "unknown"
        images.append({"alt": alt, "src_domain": domain})
    for m in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', body):
        src = m.group(2)
        domain = src.split("/")[2] if src.count("/") >= 2 else "unknown"
        images.append({"alt": m.group(1), "src_domain": domain})
    return images


PROMPT = """You are a senior news editor and data journalist at The Videshi, an Indian diaspora news site. Do THREE things in ONE response:

## 1. KEY TAKEAWAYS
3-5 concise bullet points summarizing the article in 10 seconds. Each under 20 words, standalone insight.

## 2. DATA CARDS
0-3 structured data cards from the article's facts/numbers. Each card is a rich visual summary. Types:
- "stat_grid": hero_stat (value, label, optional trend "↑ 317%") + 2-4 items (value, label)
- "comparison": 3-6 items (name, value, numeric_value) sorted desc
- "timeline": 3-6 items (date, event) chronological
- "highlights": 3-5 items (text, optional stat)
Each card: card_title (punchy, NOT the headline), card_type, items, placement_hint ("after_lead"/"mid_article"/"before_conclusion"), optional source_note.
Every number MUST come from the article. If no meaningful stats exist, return empty array.

## 3. PROOFREAD
- Grammar errors only: subject-verb, tense, missing articles, repeated words, broken HTML
- Flag irrelevant inline images (by 1-based index) — CONSERVATIVE, only clearly wrong ones
- Do NOT change factual content (names, numbers, dates, quotes)
- Do NOT rewrite style or structure

Headline: {headline}
Category: {category}
{images_block}
Body: {body_text}

Return ONLY valid JSON:
{{
  "key_takeaways": ["...", "..."],
  "data_cards": [...],
  "proofread": {{
    "images_to_remove": [],
    "text_fixes": [{{"old": "exact text", "new": "fixed text"}}],
    "verdict": "clean|minor|major"
  }}
}}"""


# ── LLM Calls ──

def _call_openai(prompt):
    """GPT-4o-mini primary."""
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "max_tokens": 2000,
        "temperature": 0.1,
    })
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        tmp.write(payload)
        tmp_path = tmp.name
    try:
        r = subprocess.run(
            ["curl", "-sS", "--max-time", "45",
             "https://api.openai.com/v1/chat/completions",
             "-H", f"Authorization: Bearer {OAI_KEY}",
             "-H", "Content-Type: application/json",
             "-d", f"@{tmp_path}"],
            capture_output=True, text=True, timeout=50
        )
        os.unlink(tmp_path)
        if r.returncode != 0:
            return None
        data = json.loads(r.stdout)
        if "error" in data:
            print(f"     ⚠ GPT error: {data['error'].get('message', '')[:80]}")
            return None
        content = data["choices"][0]["message"]["content"]
        result = json.loads(content)
        usage = data.get("usage", {})
        if usage:
            cost = usage.get("prompt_tokens", 0) * 0.15 / 1e6 + usage.get("completion_tokens", 0) * 0.60 / 1e6
            print(f"     Tokens: {usage.get('prompt_tokens',0)} in + {usage.get('completion_tokens',0)} out = ${cost:.4f}")
        return result
    except Exception as e:
        print(f"     ⚠ GPT error: {e}")
        try:
            os.unlink(tmp_path)
        except:
            pass
        return None


def _call_gemini(prompt):
    """Gemini 2.5 Flash fallback — free tier, thinkingBudget:0 for clean JSON."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "maxOutputTokens": 2000,
            "temperature": 0.1,
            "thinkingConfig": {"thinkingBudget": 0}
        }
    })
    try:
        r = subprocess.run(
            ["curl", "-sS", "--max-time", "45", "-X", "POST", url,
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True, text=True, timeout=50
        )
        if r.returncode != 0:
            return None
        data = json.loads(r.stdout)
        if "error" in data:
            print(f"     ⚠ Gemini error: {data['error'].get('message', '')[:80]}")
            return None
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)
    except Exception as e:
        print(f"     ⚠ Gemini error: {e}")
        return None


# ── Main Logic ──

def polish_article(article):
    """Single LLM call for takeaways + data cards + proofread. GPT primary, Gemini fallback."""
    headline = article.get("headline", "")
    category = article.get("category", "")
    body = article.get("body", "") or ""

    body_text = re.sub(r'<[^>]+>', ' ', body)
    body_text = re.sub(r'\s+', ' ', body_text).strip()[:5000]

    images = extract_images(body)
    if images:
        img_lines = [f"  Image {i+1}: alt=\"{img['alt']}\", domain={img['src_domain']}"
                     for i, img in enumerate(images)]
        images_block = "INLINE IMAGES:\n" + "\n".join(img_lines)
    else:
        images_block = "INLINE IMAGES: none"

    prompt = PROMPT.format(
        headline=headline, category=category,
        images_block=images_block, body_text=body_text
    )

    # Try GPT-4o-mini first
    if OAI_KEY:
        result = _call_openai(prompt)
        if result:
            return result
        print("     ↳ GPT failed, trying Gemini...")

    # Gemini 2.5 Flash fallback
    if GEMINI_KEY:
        result = _call_gemini(prompt)
        if result:
            print("     (via Gemini)")
            return result

    if not OAI_KEY and not GEMINI_KEY:
        print("     ⚠ No LLM keys available")
    return None


def apply_polish(article, result, dry_run=False):
    """Apply all results to the article in DB."""
    aid = article["id"]
    updates = {}
    changes = []

    # Key takeaways
    takeaways = result.get("key_takeaways", [])
    if takeaways and isinstance(takeaways, list):
        updates["key_takeaways"] = takeaways
        changes.append(f"{len(takeaways)} takeaways")

    # Data cards
    cards = result.get("data_cards", [])
    if cards and isinstance(cards, list):
        valid = [c for c in cards
                 if isinstance(c, dict) and c.get("card_title") and c.get("card_type") and c.get("items")]
        if valid:
            updates["data_cards"] = valid
            changes.append(f"{len(valid)} cards ({', '.join(c['card_type'] for c in valid)})")

    # Proofread — apply to body
    proofread = result.get("proofread", {})
    body = article.get("body", "") or ""
    body_changed = False

    to_remove = proofread.get("images_to_remove", [])
    if to_remove:
        img_matches = list(re.finditer(
            r'<figure[^>]*>.*?</figure>|<img[^>]*/?>|!\[[^\]]*\]\([^)]+\)',
            body, re.DOTALL))
        for idx in sorted(to_remove, reverse=True):
            if 1 <= idx <= len(img_matches):
                m = img_matches[idx - 1]
                body = body[:m.start()] + body[m.end():]
                body_changed = True
                changes.append(f"removed image {idx}")

    fixes = proofread.get("text_fixes", [])
    n_fixed = 0
    for fix in fixes[:10]:
        old, new = fix.get("old", ""), fix.get("new", "")
        if old and old in body:
            body = body.replace(old, new, 1)
            body_changed = True
            n_fixed += 1
    if n_fixed:
        changes.append(f"{n_fixed} text fixes")

    if body_changed:
        updates["body"] = body

    updates["enriched_at"] = datetime.now(timezone.utc).isoformat()

    verdict = proofread.get("verdict", "clean")
    if changes:
        print(f"     ✅ {', '.join(changes)} | {verdict}")
    else:
        print(f"     ✅ clean | {verdict}")

    if not dry_run and updates:
        if not sb_patch(aid, updates):
            print(f"     ⚠ DB patch failed")
            return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--article-id", type=str, help="Single article ID")
    parser.add_argument("--hours", type=int, default=3, help="Look back N hours")
    parser.add_argument("--max", type=int, default=20, help="Max articles")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"═══ Article Polish ═══")
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    if args.article_id:
        articles = sb_get("p2_articles", {
            "id": f"eq.{args.article_id}",
            "select": "id,headline,slug,category,body,published_at"
        })
    else:
        cutoff = quote((datetime.now(timezone.utc) - timedelta(hours=args.hours)).isoformat(), safe='')
        articles = sb_get("p2_articles", {
            "status": "eq.published",
            "published_at": f"gte.{cutoff}",
            "enriched_at": "is.null",
            "select": "id,headline,slug,category,body,published_at",
            "order": "published_at.desc",
            "limit": str(args.max)
        })

    print(f"Found {len(articles)} articles\n")

    polished = errors = 0
    for article in articles:
        print(f"  📰 {article.get('headline', '')[:75]}")
        result = polish_article(article)
        if not result:
            errors += 1
            continue
        if apply_polish(article, result, dry_run=args.dry_run):
            polished += 1
        else:
            errors += 1
        print()

    print(f"═══ Done: {polished} polished, {errors} errors ═══")


if __name__ == "__main__":
    main()
