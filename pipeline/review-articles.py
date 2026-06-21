#!/usr/bin/env python3
"""
Article Quality Reviewer for The Videshi.
Dual-LLM review + auto-revision pipeline.

Usage:
  python3 review-articles.py                    # Review last 3 hours of published articles
  python3 review-articles.py --hours 6          # Review last 6 hours
  python3 review-articles.py --id <article-id>  # Review a specific article
  python3 review-articles.py --fix              # Auto-revise flagged articles + remove bad embeds
  python3 review-articles.py --pre-publish      # Review articles in 'review' status before publishing

Pipeline:
  1. Pre-checks (no LLM): duplicate embeds, duplicate images
  2. LLM Review (GPT-4o-mini primary, Gemini 2.5 Flash fallback): score + feedback
  3. Auto-revision (--fix mode):
     - Score 7+  (pass)  → no changes
     - Score 4-6 (flag)  → send article + feedback to Gemini for revision, patch in Supabase
     - Score 1-3 (fail)  → unpublish (status → 'archived') if BOTH reviewers agree; else revise
     - Irrelevant embeds → auto-removed
     - Duplicate embeds  → auto-deduped
"""

import json, os, sys, subprocess, time, re
from datetime import datetime, timedelta, timezone
from collections import Counter

# ── Load env ──
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip().lstrip("export ").strip()
                    v = v.strip().strip("'\"")
                    if k and not os.environ.get(k):
                        os.environ[k] = v

for envfile in [".env.supabase", ".env.openai", ".env.google-ai", ".env.pexels"]:
    load_env(os.path.expanduser(f"~/workspace/{envfile}"))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_KEY = os.environ.get("GOOGLE_AI_API_KEY", "")

# ── Supabase helpers ──
def sb_get(path):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    r = subprocess.run(
        ["curl", "-s", url, "-H", f"apikey: {SUPABASE_KEY}", "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True, timeout=30
    )
    data = json.loads(r.stdout)
    return data if isinstance(data, list) else []

def sb_patch(article_id, data):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    body = json.dumps(data)
    r = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-X", "PATCH", url,
         "-H", f"apikey: {SUPABASE_KEY}", "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json", "-d", body],
        capture_output=True, text=True, timeout=30
    )
    return int(r.stdout.strip())

# ── LLM helpers ──
def call_openai(prompt, article_text, model="gpt-4o-mini", max_tokens=800):
    if not OPENAI_KEY:
        return None
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": article_text}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    r = subprocess.run(
        ["curl", "-s", "https://api.openai.com/v1/chat/completions",
         "-H", f"Authorization: Bearer {OPENAI_KEY}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=90
    )
    try:
        data = json.loads(r.stdout)
        if "error" in data:
            print(f"  ⚠️  OpenAI error: {data['error']['message'][:80]}")
            return None
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print(f"  ⚠️  OpenAI parse error: {e}")
        return None

# ── Vision image-match check (looks at the actual photo pixels) ──
VISION_JUDGE_PROMPT = """You are a photo desk editor for an Indian-diaspora news site. \
You are shown ONE photo and the headline/subject it was attached to. Decide ONLY whether \
the photo's SUBJECT plausibly belongs to this story.

Headline: {headline}
Subheadline: {subheadline}
Vertical: {vertical}
Caption/entities on the photo: {caption}

Judge ONLY the photo's subject vs the story topic — NOT whether the headline or caption \
claims are factually true. Rules:
- If the photo shows the correct named person, it is a MATCH even if the caption gets a \
detail wrong (job title, jersey number, "resigning", team, etc.). Do not second-guess facts.
- A generic but on-topic photo (a graduation scene for a student-visa story, a stock oil \
tanker for a shipping story, a city skyline for a city story) is a MATCH.
- MISMATCH only when the subject is clearly WRONG: a different named person, a music \
album cover / band on a non-music story, an unrelated company logo, a meme, or a photo \
whose subject plainly contradicts the story topic (e.g. a wrong country/landmark).
- When unsure, answer MATCH. Bias strongly toward MATCH; flag only gross mismatches.

Reply with strict JSON only:
{{"verdict":"MATCH"|"MISMATCH","what_photo_shows":"<5-12 words>","reason":"<one short sentence>"}}"""

def _download_image_b64(url):
    """Download an image, return (b64, mime) or (None, None). curl for proxy + 429 resistance."""
    import base64
    ext = (url.rsplit(".", 1)[-1].split("?")[0].lower() if "." in url else "jpg")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
            "webp": "image/webp", "gif": "image/gif"}.get(ext, "image/jpeg")
    try:
        r = subprocess.run(
            ["curl", "-sS", "-L", "-A", "TheVideshi/1.0 (thevideshi.com)", "-o", "-", url],
            capture_output=True, timeout=45)
        if r.returncode == 0 and r.stdout and len(r.stdout) > 500:
            return base64.b64encode(r.stdout).decode("ascii"), mime
    except Exception:
        pass
    return None, None

def vision_image_match(article):
    """Look at the actual hero image and decide if its subject fits the story.
    Returns dict {verdict, what_photo_shows, reason} or None if unavailable/skipped."""
    if not OPENAI_KEY:
        return None
    url = (article.get("image_url") or "").strip()
    if not url:
        return None
    b64, mime = _download_image_b64(url)
    if not b64:
        return None
    prompt = VISION_JUDGE_PROMPT.format(
        headline=article.get("headline", "") or "",
        subheadline=article.get("subheadline", "") or "",
        vertical=article.get("vertical", "") or article.get("category", "") or "",
        caption=(article.get("image_caption") or article.get("image_entities") or "(none)"),
    )
    payload = {
        "model": "gpt-4o",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "low"}},
            ],
        }],
        "max_tokens": 150,
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    for attempt in range(3):
        try:
            r = subprocess.run(
                ["curl", "-s", "https://api.openai.com/v1/chat/completions",
                 "-H", f"Authorization: Bearer {OPENAI_KEY}",
                 "-H", "Content-Type: application/json",
                 "-d", json.dumps(payload)],
                capture_output=True, text=True, timeout=90)
            data = json.loads(r.stdout)
            if "error" in data:
                msg = data["error"].get("message", "")[:80]
                if any(s in msg.lower() for s in ("rate", "overload", "timeout", "try again")):
                    time.sleep(2 * (attempt + 1)); continue
                print(f"  ⚠️  Vision error: {msg}")
                return None
            return json.loads(data["choices"][0]["message"]["content"])
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return None

def call_gemini(prompt, article_text, model="gemini-2.5-flash", max_tokens=800):
    if not GEMINI_KEY:
        return None
    payload = {
        "contents": [{"parts": [{"text": f"{prompt}\n\n---\n\n{article_text}"}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": max_tokens,
            "responseMimeType": "application/json",
            "thinkingConfig": {"thinkingBudget": 0}
        }
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
    r = subprocess.run(
        ["curl", "-s", url, "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=90
    )
    try:
        data = json.loads(r.stdout)
        if "error" in data:
            print(f"  ⚠️  Gemini error: {data['error']['message'][:80]}")
            return None
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)
    except Exception as e:
        print(f"  ⚠️  Gemini parse error: {e}")
        return None

def call_openai_text(prompt, article_text, model="gpt-4o-mini", max_tokens=2000):
    """Call OpenAI without JSON mode — returns raw text (for article rewrites)."""
    if not OPENAI_KEY:
        return None
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": article_text}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }
    r = subprocess.run(
        ["curl", "-s", "https://api.openai.com/v1/chat/completions",
         "-H", f"Authorization: Bearer {OPENAI_KEY}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=120
    )
    try:
        data = json.loads(r.stdout)
        if "error" in data:
            print(f"  ⚠️  OpenAI rewrite error: {data['error']['message'][:80]}")
            return None
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  ⚠️  OpenAI rewrite parse error: {e}")
        return None

def call_gemini_text(prompt, article_text, model="gemini-2.5-flash", max_tokens=2000):
    """Call Gemini without JSON mode — returns raw text (for article rewrites)."""
    if not GEMINI_KEY:
        return None
    payload = {
        "contents": [{"parts": [{"text": f"{prompt}\n\n---\n\n{article_text}"}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": max_tokens,
            "thinkingConfig": {"thinkingBudget": 0},
        }
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
    r = subprocess.run(
        ["curl", "-s", url, "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=120
    )
    try:
        data = json.loads(r.stdout)
        if "error" in data:
            print(f"  ⚠️  Gemini rewrite error: {data['error']['message'][:80]}")
            return None
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"  ⚠️  Gemini rewrite parse error: {e}")
        return None

# ── Prompts ──
REVIEW_PROMPT = """You are an editorial quality reviewer for The Videshi, an Indian diaspora news platform for NRIs.

Review the article below and return a JSON object with these fields:

{
  "overall_score": <1-10>,
  "embed_issues": [
    {"url": "...", "problem": "irrelevant|broken|duplicate", "explanation": "..."}
  ],
  "image_match": {"score": <1-10>, "issue": "..." or null},
  "diaspora_angle": {"present": true/false, "quality": <1-10>, "note": "..."},
  "factual_flags": ["any internal contradictions or suspicious claims"],
  "duplicate_embeds": ["URLs that appear more than once"],
  "suggestions": ["1-2 actionable improvements"],
  "verdict": "pass" | "flag" | "fail"
}

Rules:
- "pass" = publishable as-is (score 7+)
- "flag" = minor issues, could improve (score 4-6)  
- "fail" = should not publish without fixes (score 1-3)
- For embed_issues: check if each social media URL (instagram.com/reel/..., twitter.com/..., x.com/...) is topically relevant to the article's subject. A Sachin Tendulkar cricket post in a sprinting article = "irrelevant". 
- For image_match: does the hero image description/entities match the article headline and topic?
- Diaspora angle: does the article connect to NRI/diaspora readers? Is it forced or natural?
- Be strict but fair. This is a real newsroom quality gate."""

REVISE_PROMPT = """You are a senior editor at The Videshi, an Indian diaspora news platform for NRIs in the US, UK, and Canada.

You are given an article and reviewer feedback. Your job is to REVISE the article to fix the flagged issues.

RULES:
- Keep the same headline, structure, and markdown format
- Keep ALL social media embed URLs (lines starting with https://instagram.com or https://x.com) exactly as they are — do not remove, move, or modify them
- Preserve the article's voice and factual content
- Fix ONLY what the feedback asks for:
  * If diaspora angle is weak → add 1-2 natural NRI-relevant sentences (how this affects Indians abroad, remittances, dual citizenship, travel, family ties, professional impact)
  * If sources are thin → add context or attribution where possible
  * If structure is weak → improve flow between sections
  * If tone is off → adjust to professional but accessible news tone
- Keep the article between 600-900 words
- Output ONLY the revised article body in markdown. No preamble, no explanation, no "Here's the revised article" — just the article text.
- Do NOT add fictional quotes or fabricated statistics"""

SECOND_REVIEW_PROMPT = """You are an editorial quality reviewer for The Videshi, an Indian diaspora news platform.

This article was flagged as "fail" by a first reviewer. Give your independent assessment.
Return a JSON object with these fields:

{
  "overall_score": <1-10>,
  "verdict": "pass" | "flag" | "fail",
  "should_unpublish": true/false,
  "reason": "brief explanation"
}

Only set should_unpublish to true if the article is genuinely harmful, completely off-topic, factually wrong in a dangerous way, or nonsensical. Most articles should be revised, not unpublished."""


# ── Pre-checks (no LLM needed) ──
def check_duplicate_embeds(body):
    """Find duplicate social media URLs in the article body."""
    ig_urls = re.findall(r'https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/[A-Za-z0-9_-]+/?', body)
    x_urls = re.findall(r'https?://(?:www\.)?(?:twitter|x)\.com/\w+/status/\d+', body)
    all_urls = ig_urls + x_urls
    dupes = [url for url, count in Counter(all_urls).items() if count > 1]
    return dupes


def verify_embed_urls(body, published_at=None):
    """Verify that social media embed URLs are actually live and not hallucinated.
    
    Checks:
    1. X/Twitter: react-tweet API returns data (not null)
    2. X/Twitter: tweet timestamp is within 60 days of article publish date (catches hallucinated old IDs)
    3. Instagram: oEmbed API returns valid response
    
    Returns list of {"url": ..., "problem": "broken"|"hallucinated_old", "detail": ...}
    """
    issues = []
    
    # ── Check X/Twitter embeds ──
    x_urls = re.findall(r'https?://(?:www\.)?(?:twitter|x)\.com/\w+/status/(\d+)', body)
    for tweet_id in x_urls:
        url = f"https://x.com/status/{tweet_id}"
        # Find full URL in body for removal
        full_url_match = re.search(r'https?://(?:www\.)?(?:twitter|x)\.com/\w+/status/' + tweet_id, body)
        full_url = full_url_match.group(0) if full_url_match else url
        
        try:
            r = subprocess.run(
                ["curl", "-s", "--connect-timeout", "5", "--max-time", "10",
                 f"https://react-tweet.vercel.app/api/tweet/{tweet_id}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(r.stdout)
            
            if data.get("data") is None:
                issues.append({"url": full_url, "problem": "broken", "detail": "react-tweet returned null (deleted/protected/nonexistent)"})
                continue
            
            # Check tweet age — hallucinated tweets often have IDs from years ago
            if published_at:
                try:
                    # Twitter snowflake → timestamp
                    tweet_epoch_ms = (int(tweet_id) >> 22) + 1288834974657
                    tweet_date = datetime.fromtimestamp(tweet_epoch_ms / 1000, tz=timezone.utc)
                    
                    if isinstance(published_at, str):
                        pub_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    else:
                        pub_date = published_at
                    
                    age_days = (pub_date - tweet_date).days
                    if age_days > 60:
                        issues.append({
                            "url": full_url,
                            "problem": "hallucinated_old",
                            "detail": f"Tweet is from {tweet_date.strftime('%Y-%m-%d')} — {age_days} days before article. Likely hallucinated."
                        })
                except Exception:
                    pass  # Can't parse date, skip age check
                    
        except Exception as e:
            # Network error — don't flag, just skip
            print(f"  ⚠️  Could not verify tweet {tweet_id}: {e}")
    
    # ── Check Instagram embeds ──
    ig_urls = re.findall(r'https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)', body)
    for shortcode in ig_urls:
        full_url_match = re.search(r'https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/' + re.escape(shortcode) + r'[^\s]*', body)
        full_url = full_url_match.group(0) if full_url_match else f"https://instagram.com/p/{shortcode}"
        
        try:
            r = subprocess.run(
                ["curl", "-s", "--connect-timeout", "5", "--max-time", "10", "-o", "/dev/null", "-w", "%{http_code}",
                 f"https://www.instagram.com/p/{shortcode}/embed/"],
                capture_output=True, text=True, timeout=15
            )
            status_code = r.stdout.strip()
            if status_code in ("404", "410"):
                issues.append({"url": full_url, "problem": "broken", "detail": f"Instagram embed returned {status_code}"})
        except Exception as e:
            print(f"  ⚠️  Could not verify IG {shortcode}: {e}")
    
    return issues

def check_duplicate_images(article, recent_articles):
    """Check if this article's image is used by another recent article."""
    img = article.get("image_url", "")
    if not img:
        return []
    dupes = []
    for other in recent_articles:
        if other["id"] != article["id"] and other.get("image_url") == img:
            dupes.append({"article_id": other["id"], "headline": other["headline"][:60]})
    return dupes


# ── Revision engine ──
def revise_article(article, review_result, fix_mode=False):
    """Send article + feedback to LLM for revision. Returns revised body or None."""
    if not fix_mode:
        return None

    headline = article["headline"]
    body = article.get("body", "") or ""
    vertical = article.get("vertical", "") or ""
    
    # Build feedback summary from review
    feedback_parts = []
    review = review_result.get("llm_review", {})
    
    if review.get("diaspora_angle", {}).get("quality", 10) < 7:
        note = review["diaspora_angle"].get("note", "")
        feedback_parts.append(f"DIASPORA ANGLE: Weak (score {review['diaspora_angle'].get('quality', '?')}/10). {note}")
    
    if review.get("image_match", {}).get("score", 10) < 6:
        issue = review["image_match"].get("issue", "")
        feedback_parts.append(f"IMAGE MATCH: Poor. {issue}")
    
    if review.get("factual_flags"):
        feedback_parts.append(f"FACTUAL FLAGS: {'; '.join(review['factual_flags'][:3])}")
    
    if review.get("suggestions"):
        feedback_parts.append(f"SUGGESTIONS: {'; '.join(review['suggestions'][:3])}")
    
    score = review.get("overall_score", 10)
    feedback_parts.append(f"OVERALL SCORE: {score}/10")
    
    if not feedback_parts:
        return None
    
    feedback = "\n".join(feedback_parts)
    
    article_text = f"""HEADLINE: {headline}
VERTICAL: {vertical}

REVIEWER FEEDBACK:
{feedback}

CURRENT ARTICLE BODY:
{body}"""
    
    print(f"  🔄 Revising with Gemini 2.5 Flash...")
    
    # Use Gemini for revision (free tier), fall back to OpenAI
    revised = call_gemini_text(REVISE_PROMPT, article_text, max_tokens=2500)
    reviser = "gemini-2.5-flash"
    
    if not revised:
        print(f"  🔄 Gemini unavailable, revising with GPT-4o-mini...")
        revised = call_openai_text(REVISE_PROMPT, article_text, max_tokens=2500)
        reviser = "gpt-4o-mini"
    
    if not revised:
        print(f"  ❌ Revision failed — no LLM available")
        return None
    
    # Basic sanity checks on the revised article
    revised = revised.strip()
    
    # Remove any preamble the LLM might add
    for prefix in ["Here's the revised article:", "Here is the revised article:", "Revised article:", "---"]:
        if revised.lower().startswith(prefix.lower()):
            revised = revised[len(prefix):].strip()
    
    # Check it's not drastically shorter (LLM sometimes truncates)
    orig_words = len(body.split())
    revised_words = len(revised.split())
    if revised_words < orig_words * 0.5:
        print(f"  ⚠️  Revision too short ({revised_words} words vs original {orig_words}).")
        # Fallback to the other LLM
        if reviser == "gemini-2.5-flash":
            print(f"  🔄 Falling back to GPT-4o-mini for revision...")
            revised = call_openai_text(REVISE_PROMPT, article_text, max_tokens=2500)
            reviser = "gpt-4o-mini"
        elif reviser == "gpt-4o-mini":
            print(f"  🔄 Falling back to Gemini 2.5 Flash for revision...")
            revised = call_gemini_text(REVISE_PROMPT, article_text, max_tokens=2500)
            reviser = "gemini-2.5-flash"
        if not revised:
            print(f"  ❌ Fallback revision also failed. Skipping.")
            return None
        revised = revised.strip()
        for prefix in ["Here's the revised article:", "Here is the revised article:", "Revised article:", "---"]:
            if revised.lower().startswith(prefix.lower()):
                revised = revised[len(prefix):].strip()
        revised_words = len(revised.split())
        if revised_words < orig_words * 0.5:
            print(f"  ❌ Fallback also too short ({revised_words} words). Skipping.")
            return None
    
    # Check embeds are preserved
    orig_embeds = set(re.findall(r'https?://(?:www\.)?(?:instagram\.com|x\.com|twitter\.com)/\S+', body))
    revised_embeds = set(re.findall(r'https?://(?:www\.)?(?:instagram\.com|x\.com|twitter\.com)/\S+', revised))
    lost_embeds = orig_embeds - revised_embeds
    if lost_embeds:
        print(f"  ⚠️  Revision dropped embeds: {lost_embeds}. Re-appending them.")
        for embed in lost_embeds:
            revised += f"\n\n{embed}"
    
    # Patch in Supabase
    status = sb_patch(article["id"], {"body": revised})
    if status in (200, 204):
        print(f"  ✅ Article revised by {reviser} ({revised_words} words)")
        return {"reviser": reviser, "word_count": revised_words, "original_word_count": orig_words}
    else:
        print(f"  ❌ Supabase patch failed (HTTP {status})")
        return None


def handle_fail(article, review_openai, fix_mode=False):
    """Handle a 'fail' verdict — get second opinion, revise or unpublish."""
    if not fix_mode:
        return "fail_no_action"
    
    headline = article["headline"]
    body = article.get("body", "") or ""
    
    article_text = f"""HEADLINE: {headline}
BODY:
{body[:4000]}"""
    
    # Get second opinion from the OTHER model
    print(f"  🔍 Getting second opinion for fail verdict...")
    second = call_gemini(SECOND_REVIEW_PROMPT, article_text)
    second_source = "gemini-2.5-flash"
    if not second:
        second = call_openai(SECOND_REVIEW_PROMPT, article_text)
        second_source = "gpt-4o-mini"
    
    if second and second.get("should_unpublish") == True:
        # Both agree: unpublish
        status = sb_patch(article["id"], {"status": "archived"})
        if status in (200, 204):
            reason = second.get("reason", "consensus fail")
            print(f"  🗑️  UNPUBLISHED (consensus: {reason})")
            return f"unpublished: {reason}"
        else:
            print(f"  ❌ Failed to unpublish (HTTP {status})")
            return "unpublish_failed"
    else:
        # Second reviewer disagrees — revise instead
        if second:
            print(f"  ↩️  Second reviewer says: {second.get('verdict','?')} (score {second.get('overall_score','?')}). Revising instead.")
        return "revise"


# ── Main review function ──
def review_article(article, recent_articles, fix_mode=False, pre_publish=False):
    """Review a single article with pre-checks + LLM review + auto-revision."""
    headline = article["headline"]
    body = article.get("body", "") or ""
    image_url = article.get("image_url", "") or ""
    image_entities = article.get("image_entities", "") or ""
    vertical = article.get("vertical", "") or ""
    
    print(f"\n📝 Reviewing: {headline[:70]}...")
    
    result = {
        "id": article["id"],
        "headline": headline,
        "slug": article.get("slug", ""),
        "pre_checks": {},
        "llm_review": None,
        "actions_taken": [],
        "revised": False,
        "unpublished": False,
    }
    
    # ── Pre-check 1: Duplicate embeds ──
    dup_embeds = check_duplicate_embeds(body)
    result["pre_checks"]["duplicate_embeds"] = dup_embeds
    if dup_embeds:
        print(f"  🔁 Duplicate embeds: {dup_embeds}")
        if fix_mode:
            fixed_body = body
            for url in dup_embeds:
                parts = fixed_body.split(url)
                if len(parts) > 2:
                    fixed_body = parts[0] + url + url.join(parts[2:])
            if fixed_body != body:
                status = sb_patch(article["id"], {"body": fixed_body})
                if status in (200, 204):
                    result["actions_taken"].append(f"Removed duplicate embed(s)")
                    print(f"  ✅ Fixed duplicate embeds")
                    body = fixed_body
                    article["body"] = body
    
    # ── Pre-check 2: Duplicate images ──
    dup_images = check_duplicate_images(article, recent_articles)
    result["pre_checks"]["duplicate_images"] = dup_images
    if dup_images:
        print(f"  🖼️  Same image used on: {[d['headline'] for d in dup_images]}")
    
    # ── Pre-check 3: Verify embed URLs are live ──
    broken_embeds = verify_embed_urls(body, article.get("published_at"))
    result["pre_checks"]["broken_embeds"] = broken_embeds
    if broken_embeds:
        for be in broken_embeds:
            print(f"  💀 Embed {be['problem']}: {be['url'][:60]} — {be['detail'][:60]}")
        if fix_mode:
            fixed_body = body
            for be in broken_embeds:
                url = be["url"]
                # Remove the URL line and surrounding blank lines
                fixed_body = re.sub(r'\n?\n?' + re.escape(url) + r'\n?\n?', '\n\n', fixed_body)
            fixed_body = re.sub(r'\n{3,}', '\n\n', fixed_body)
            if fixed_body != body:
                status = sb_patch(article["id"], {"body": fixed_body})
                if status in (200, 204):
                    count = len(broken_embeds)
                    result["actions_taken"].append(f"Removed {count} broken/hallucinated embed(s)")
                    print(f"  ✅ Removed {count} broken/hallucinated embed(s)")
                    body = fixed_body
                    article["body"] = body

    # ── Pre-check 4: Vision image match (looks at the actual photo) ──
    # Only run when there's an image and we're gating publication, to keep cost down.
    if image_url and (pre_publish or fix_mode):
        vmatch = vision_image_match(article)
        result["pre_checks"]["vision_image_match"] = vmatch
        if vmatch and (vmatch.get("verdict") or "").upper() == "MISMATCH":
            shows = vmatch.get("what_photo_shows", "?")
            print(f"  🖼️❌ Image MISMATCH — photo shows: {shows} | {vmatch.get('reason','')[:70]}")
            result["image_mismatch"] = True
            if fix_mode:
                # Clear the bad image so the article can't publish with a wrong photo.
                # A null image_url sends it back for re-sourcing on the next writer pass.
                status = sb_patch(article["id"], {"image_url": ""})
                if status in (200, 204):
                    result["actions_taken"].append(f"Cleared mismatched image ({shows})")
                    print(f"  ✅ Cleared mismatched image")
                    image_url = ""
                    article["image_url"] = ""
        elif vmatch:
            print(f"  🖼️✅ Image OK — {vmatch.get('what_photo_shows','')}")

    # ── Build article text for LLM review ──
    article_text = f"""HEADLINE: {headline}
VERTICAL: {vertical}
IMAGE URL: {image_url}
IMAGE ENTITIES: {image_entities}

BODY:
{body[:4000]}"""
    
    # ── LLM Review (GPT-4o-mini primary) ──
    llm_result = call_openai(REVIEW_PROMPT, article_text)
    llm_source = "gpt-4o-mini"
    
    if not llm_result:
        llm_result = call_gemini(REVIEW_PROMPT, article_text)
        llm_source = "gemini-2.5-flash"
    
    if llm_result:
        result["llm_review"] = llm_result
        result["llm_source"] = llm_source
        score = llm_result.get("overall_score", "?")
        llm_verdict = llm_result.get("verdict", "?")
        # Derive verdict from score — LLM sometimes returns wrong verdict for the score
        if isinstance(score, (int, float)):
            if score >= 7:
                verdict = "pass"
            elif score >= 4:
                verdict = "flag"
            else:
                verdict = "fail"
            if verdict != llm_verdict:
                print(f"  ⚠️ LLM verdict '{llm_verdict}' overridden to '{verdict}' (score {score})")
        else:
            verdict = llm_verdict
        print(f"  📊 Score: {score}/10 | Verdict: {verdict} ({llm_source})")
        
        # ── Handle embed issues (remove irrelevant embeds) ──
        if fix_mode and llm_result.get("embed_issues"):
            for issue in llm_result["embed_issues"]:
                if issue.get("problem") == "irrelevant" and issue.get("url"):
                    url = issue["url"]
                    fixed = body.replace(f"\n\n{url}\n\n", "\n\n")
                    if fixed == body:
                        fixed = body.replace(f"\n{url}\n", "\n")
                    if fixed == body:
                        fixed = body.replace(url, "")
                    if fixed != body:
                        status = sb_patch(article["id"], {"body": fixed})
                        if status in (200, 204):
                            result["actions_taken"].append(f"Removed irrelevant embed: {url[:60]}")
                            print(f"  ✅ Removed irrelevant embed: {url[:60]}")
                            body = fixed
                            article["body"] = body
        
        # ── Handle verdict ──
        if fix_mode and verdict == "pass":
            # Pre-publish gate: promote passing articles to published
            if pre_publish and article.get("status") == "review":
                if result.get("image_mismatch"):
                    # Vision check cleared a wrong photo; hold for re-sourcing, don't publish image-less.
                    print(f"  🔒 Held in review — image was mismatched, awaiting re-source")
                    result["actions_taken"].append("held: image mismatch")
                else:
                    now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    status = sb_patch(article["id"], {"status": "published", "published_at": now_ts})
                    if status in (200, 204):
                        result["actions_taken"].append("promoted to published")
                        print(f"  ✅ Promoted to published (score {score})")
                    else:
                        print(f"  ⚠️ Failed to promote (HTTP {status})")

        elif fix_mode and verdict == "fail":
            fail_result = handle_fail(article, llm_result, fix_mode)
            if fail_result.startswith("unpublished"):
                result["unpublished"] = True
                result["actions_taken"].append(fail_result)
            elif fail_result == "revise":
                # Revise instead of unpublish
                rev = revise_article(article, result, fix_mode)
                if rev:
                    result["revised"] = True
                    result["actions_taken"].append(f"Revised by {rev['reviser']} ({rev['original_word_count']}→{rev['word_count']} words)")
        
        elif fix_mode and verdict == "flag":
            # Flagged articles get revised
            rev = revise_article(article, result, fix_mode)
            if rev:
                result["revised"] = True
                result["actions_taken"].append(f"Revised by {rev['reviser']} ({rev['original_word_count']}→{rev['word_count']} words)")
                # In pre-publish mode, revised flagged articles stay in 'review' for re-check next cycle
                if pre_publish and article.get("status") == "review":
                    print(f"  🔄 Stays in review — will be re-checked next cycle")
        
        # ── Print issues ──
        if llm_result.get("embed_issues"):
            for iss in llm_result["embed_issues"]:
                print(f"  ⚠️  Embed: {iss.get('url','?')[:50]} — {iss.get('problem','?')}: {iss.get('explanation','')[:60]}")
        if llm_result.get("factual_flags"):
            for flag in llm_result["factual_flags"]:
                print(f"  🚩 Factual: {flag[:80]}")
        if llm_result.get("suggestions"):
            for sug in llm_result["suggestions"]:
                print(f"  💡 {sug[:80]}")
    else:
        print(f"  ❌ No LLM review available")
    
    return result


def main():
    fix_mode = "--fix" in sys.argv
    pre_publish = "--pre-publish" in sys.argv
    hours = 3
    article_id = None
    
    for i, arg in enumerate(sys.argv):
        if arg == "--hours" and i + 1 < len(sys.argv):
            hours = int(sys.argv[i + 1])
        if arg == "--id" and i + 1 < len(sys.argv):
            article_id = sys.argv[i + 1]
    
    # Fetch articles
    select = "id,headline,slug,body,image_url,image_entities,vertical,published_at,status"
    
    if article_id:
        articles = sb_get(f"p2_articles?select={select}&id=eq.{article_id}")
    elif pre_publish:
        articles = sb_get(f"p2_articles?select={select}&status=eq.review&order=created_at.desc&limit=20")
    else:
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
        articles = sb_get(f"p2_articles?select={select}&status=eq.published&published_at=gte.{cutoff}&order=published_at.desc&limit=50")
    
    if not articles:
        print("No articles found to review.")
        return
    
    print(f"{'🔧 FIX MODE' if fix_mode else '👀 REVIEW ONLY'} — Found {len(articles)} articles")
    
    # Also fetch recent articles for image dedup check
    recent_cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    recent_articles = sb_get(
        f"p2_articles?select=id,headline,image_url&status=eq.published&published_at=gte.{recent_cutoff}&limit=500"
    )
    
    # Review each article
    results = []
    stats = {"pass": 0, "flag": 0, "fail": 0, "error": 0}
    revision_count = 0
    unpublish_count = 0
    
    for article in articles:
        result = review_article(article, recent_articles, fix_mode, pre_publish=pre_publish)
        results.append(result)
        
        verdict = "error"
        if result.get("llm_review"):
            verdict = result["llm_review"].get("verdict", "error")
        stats[verdict] = stats.get(verdict, 0) + 1
        
        if result.get("revised"):
            revision_count += 1
        if result.get("unpublished"):
            unpublish_count += 1
        
        time.sleep(0.5)  # rate limit between articles
    
    # Summary
    print(f"\n{'='*60}")
    print(f"REVIEW SUMMARY: {len(articles)} articles")
    print(f"  ✅ Pass: {stats['pass']}")
    print(f"  ⚠️  Flag: {stats['flag']}")
    print(f"  ❌ Fail: {stats['fail']}")
    print(f"  💀 Error: {stats['error']}")
    
    if fix_mode:
        total_mechanical = sum(
            len([a for a in r.get("actions_taken", []) if "Removed" in a])
            for r in results
        )
        total_broken_embeds = sum(
            len(r.get("pre_checks", {}).get("broken_embeds", []))
            for r in results
        )
        print(f"  🔧 Mechanical fixes (embeds): {total_mechanical}")
        print(f"  💀 Broken/hallucinated embeds found: {total_broken_embeds}")
        print(f"  📝 Articles revised: {revision_count}")
        print(f"  🗑️  Articles unpublished: {unpublish_count}")
    
    # Save report
    report_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/review-report.json")
    with open(report_path, "w") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "fix" if fix_mode else "review",
            "stats": stats,
            "revisions": revision_count,
            "unpublished": unpublish_count,
            "articles": results,
        }, f, indent=2, default=str)
    print(f"\nFull report: {report_path}")


if __name__ == "__main__":
    main()
