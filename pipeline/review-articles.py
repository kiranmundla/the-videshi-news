#!/usr/bin/env python3
"""
Article Quality Reviewer for The Videshi.
Dual-LLM review: GPT-4o-mini + Gemini 2.0 Flash.

Usage:
  python3 review-articles.py                    # Review last 3 hours of published articles
  python3 review-articles.py --hours 6          # Review last 6 hours
  python3 review-articles.py --id <article-id>  # Review a specific article
  python3 review-articles.py --fix              # Auto-fix flagged issues (remove bad embeds, etc.)
  python3 review-articles.py --pre-publish      # Review articles in 'review' status before publishing

Checks:
  1. Social embed relevance (IG/X embeds match article topic)
  2. Image-headline match (hero image fits the article subject)
  3. Duplicate image detection (same image used on recent articles)
  4. Editorial quality (diaspora angle, sources, structure)
  5. Duplicate embed detection (same URL embedded twice)
  6. Factual consistency (internal contradictions)

Output: JSON report per article with pass/flag/fail per check.
"""

import json, os, sys, subprocess, time, re
from datetime import datetime, timedelta, timezone
from collections import defaultdict

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
def call_openai(prompt, article_text, model="gpt-4o-mini"):
    if not OPENAI_KEY:
        return None
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": article_text}
        ],
        "max_tokens": 800,
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    r = subprocess.run(
        ["curl", "-s", "https://api.openai.com/v1/chat/completions",
         "-H", f"Authorization: Bearer {OPENAI_KEY}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=60
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

def call_gemini(prompt, article_text, model="gemini-2.5-flash"):
    if not GEMINI_KEY:
        return None
    payload = {
        "contents": [{"parts": [{"text": f"{prompt}\n\n---\n\n{article_text}"}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 800,
            "responseMimeType": "application/json"
        }
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
    r = subprocess.run(
        ["curl", "-s", url, "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=60
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

# ── Review prompt ──
REVIEW_PROMPT = """You are an editorial quality reviewer for The Videshi, an Indian diaspora news platform.

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


# ── Pre-checks (no LLM needed) ──
def check_duplicate_embeds(body):
    """Find duplicate social media URLs in the article body."""
    ig_urls = re.findall(r'https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/[A-Za-z0-9_-]+/?', body)
    x_urls = re.findall(r'https?://(?:www\.)?(?:twitter|x)\.com/\w+/status/\d+', body)
    all_urls = ig_urls + x_urls
    from collections import Counter
    dupes = [url for url, count in Counter(all_urls).items() if count > 1]
    return dupes

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

# ── Main review function ──
def review_article(article, recent_articles, fix_mode=False):
    """Review a single article with pre-checks + LLM review."""
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
    }
    
    # Pre-check 1: Duplicate embeds
    dup_embeds = check_duplicate_embeds(body)
    result["pre_checks"]["duplicate_embeds"] = dup_embeds
    if dup_embeds:
        print(f"  🔁 Duplicate embeds: {dup_embeds}")
        if fix_mode:
            fixed_body = body
            for url in dup_embeds:
                # Remove duplicate (keep first occurrence)
                parts = fixed_body.split(url)
                if len(parts) > 2:
                    fixed_body = parts[0] + url + url.join(parts[2:])  # keep first, remove second
            if fixed_body != body:
                status = sb_patch(article["id"], {"body": fixed_body})
                if status in (200, 204):
                    result["actions_taken"].append(f"Removed duplicate embed(s): {dup_embeds}")
                    print(f"  ✅ Fixed duplicate embeds")
    
    # Pre-check 2: Duplicate images
    dup_images = check_duplicate_images(article, recent_articles)
    result["pre_checks"]["duplicate_images"] = dup_images
    if dup_images:
        print(f"  🖼️  Same image used on: {[d['headline'] for d in dup_images]}")
    
    # Build article text for LLM review
    article_text = f"""HEADLINE: {headline}
VERTICAL: {vertical}
IMAGE URL: {image_url}
IMAGE ENTITIES: {image_entities}

BODY:
{body[:4000]}"""
    
    # LLM Review (try OpenAI first, then Gemini)
    llm_result = call_openai(REVIEW_PROMPT, article_text)
    llm_source = "gpt-4o-mini"
    
    if not llm_result:
        llm_result = call_gemini(REVIEW_PROMPT, article_text)
        llm_source = "gemini-2.0-flash"
    
    if llm_result:
        result["llm_review"] = llm_result
        result["llm_source"] = llm_source
        score = llm_result.get("overall_score", "?")
        verdict = llm_result.get("verdict", "?")
        print(f"  📊 Score: {score}/10 | Verdict: {verdict} ({llm_source})")
        
        # Handle embed issues in fix mode
        if fix_mode and llm_result.get("embed_issues"):
            for issue in llm_result["embed_issues"]:
                if issue.get("problem") == "irrelevant" and issue.get("url"):
                    url = issue["url"]
                    # Remove irrelevant embed from body
                    fixed = body.replace(f"\n\n{url}\n\n", "\n\n")
                    if fixed == body:
                        fixed = body.replace(url, "")
                    if fixed != body:
                        status = sb_patch(article["id"], {"body": fixed})
                        if status in (200, 204):
                            result["actions_taken"].append(f"Removed irrelevant embed: {url}")
                            print(f"  ✅ Removed irrelevant embed: {url[:60]}")
                            body = fixed  # update for subsequent fixes
        
        # Print issues
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
    
    print(f"Found {len(articles)} articles to review")
    
    # Also fetch recent articles for image dedup check
    recent_cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    recent_articles = sb_get(
        f"p2_articles?select=id,headline,image_url&status=eq.published&published_at=gte.{recent_cutoff}&limit=500"
    )
    
    # Review each article
    results = []
    stats = {"pass": 0, "flag": 0, "fail": 0, "error": 0}
    
    for article in articles:
        result = review_article(article, recent_articles, fix_mode)
        results.append(result)
        
        verdict = "error"
        if result.get("llm_review"):
            verdict = result["llm_review"].get("verdict", "error")
        stats[verdict] = stats.get(verdict, 0) + 1
        
        time.sleep(0.5)  # rate limit
    
    # Summary
    print(f"\n{'='*60}")
    print(f"REVIEW SUMMARY: {len(articles)} articles")
    print(f"  ✅ Pass: {stats['pass']}")
    print(f"  ⚠️  Flag: {stats['flag']}")
    print(f"  ❌ Fail: {stats['fail']}")
    print(f"  💀 Error: {stats['error']}")
    
    if fix_mode:
        total_fixes = sum(len(r.get("actions_taken", [])) for r in results)
        print(f"  🔧 Auto-fixes applied: {total_fixes}")
    
    # Save report
    report_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/review-report.json")
    with open(report_path, "w") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stats": stats,
            "articles": results,
        }, f, indent=2, default=str)
    print(f"\nFull report: {report_path}")


if __name__ == "__main__":
    main()
