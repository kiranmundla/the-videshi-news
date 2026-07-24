#!/usr/bin/env python3
"""
review-articles.py — Automated editorial QA for published articles.

Catches what Kiran catches manually:
  1. Structural checks (no LLM, fast):
     - Duplicate embeds (inline + social_embeds)
     - Generic hero images (Pexels/Unsplash stock)
     - Embed placement (all clustered at bottom)
     - Missing key takeaways
     - Duplicate pull quotes
     - Irrelevant YouTube embeds (title mismatch)
  2. LLM editorial review (GPT-4o-mini, cheap):
     - Diaspora angle strength
     - Headline quality
     - Content gaps / suggestions
     - Missing obvious embed opportunities

Usage:
  python3 -u review-articles.py --hours 12              # review last 12h
  python3 -u review-articles.py --hours 24 --apply      # review + save report
  python3 -u review-articles.py --article-ids ID1,ID2   # specific articles

Env: ~/workspace/.env.supabase, ~/workspace/.env.openai
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

# ── Env ──
def _load_env(path):
    env = {}
    p = os.path.expanduser(path)
    if not os.path.exists(p):
        return env
    with open(p) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip("\"'")
    return env

_sb = _load_env("~/workspace/.env.supabase")
_oai = _load_env("~/workspace/.env.openai")

SB_URL = _sb.get("SUPABASE_URL", "").rstrip("/").replace("https://", "")
SB_KEY = _sb.get("SUPABASE_SERVICE_ROLE_KEY", "")
OAI_KEY = _oai.get("OPENAI_API_KEY", "")

# ── LLM review dedup (avoid re-reviewing same article) ──
_REVIEWED_STATE_FILE = os.path.expanduser("~/workspace/the-videshi-news/pipeline/.reviewed-articles.json")

def _load_reviewed():
    """Load set of already-LLM-reviewed article IDs."""
    if not os.path.exists(_REVIEWED_STATE_FILE):
        return set()
    try:
        with open(_REVIEWED_STATE_FILE) as f:
            return set(json.load(f))
    except:
        return set()

def _save_reviewed(state):
    """Save reviewed article IDs."""
    with open(_REVIEWED_STATE_FILE, "w") as f:
        json.dump(list(state), f)

def sb_get(endpoint, params=None):
    url = f"https://{SB_URL}/rest/v1/{endpoint}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    r = subprocess.run(
        ["curl", "-s", url,
         "-H", f"apikey: {SB_KEY}",
         "-H", f"Authorization: Bearer {SB_KEY}"],
        capture_output=True, text=True, timeout=30
    )
    return json.loads(r.stdout) if r.stdout.strip() else []


# ── Structural checks (no LLM) ──

def check_duplicate_embeds(article):
    """Check if embeds exist in both inline tags and social_embeds array."""
    issues = []
    body = article.get("body", "") or ""
    embeds = article.get("social_embeds") or []
    if isinstance(embeds, str):
        try:
            embeds = json.loads(embeds)
        except:
            embeds = []
    
    for e in embeds:
        eurl = e.get("url", "") if isinstance(e, dict) else str(e)
        if eurl and eurl in body:
            issues.append(f"Duplicate embed: {eurl[:60]} appears both inline and in social_embeds")
    return issues


def check_hero_image(article):
    """Flag generic stock images."""
    issues = []
    img = article.get("image_url") or article.get("hero_image_url") or ""
    if not img:
        issues.append("No hero image")
    elif any(s in img.lower() for s in ["pexels.com", "unsplash.com", "pixabay.com", "shutterstock.com"]):
        issues.append(f"Generic stock hero image: {img[:80]}")
    return issues


def check_embed_placement(article):
    """Check if all embeds are clustered at the bottom."""
    issues = []
    body = article.get("body", "") or ""
    
    embed_positions = []
    for pattern in [r'<youtube>', r'<twitter>', r'instagram\.com/p/', r'x\.com/\w+/status/']:
        for m in re.finditer(pattern, body, re.IGNORECASE):
            embed_positions.append(m.start())
    
    if not embed_positions:
        return issues
    
    body_len = len(body)
    if body_len == 0:
        return issues
    
    # If all embeds are in the bottom 30% of the article
    all_bottom = all(pos / body_len > 0.7 for pos in embed_positions)
    if all_bottom and len(embed_positions) >= 1:
        issues.append(f"All {len(embed_positions)} embed(s) placed in the bottom 30% — move higher for engagement")
    
    # Check clustering — are any two embeds within 200 chars of each other?
    sorted_pos = sorted(embed_positions)
    for i in range(len(sorted_pos) - 1):
        if sorted_pos[i+1] - sorted_pos[i] < 200:
            issues.append("Two embeds clustered within 200 chars of each other")
            break
    
    return issues


def check_key_takeaways(article):
    """Check if key takeaways are present."""
    body = article.get("body", "") or ""
    if "key-takeaways" not in body and len(body.split()) > 300:
        return ["Missing key takeaways section (article is 300+ words)"]
    return []


def check_duplicate_pull_quotes(article):
    """Check for duplicate pull quotes."""
    body = article.get("body", "") or ""
    quotes = re.findall(r'<blockquote class="pull-quote"><p>"([^"]+)"', body)
    if len(quotes) != len(set(quotes)):
        return ["Duplicate pull quote found"]
    return []


def check_youtube_relevance(article):
    """Basic check: does YouTube title relate to the headline?"""
    issues = []
    body = article.get("body", "") or ""
    headline = (article.get("headline", "") or "").lower()
    
    yt_urls = re.findall(r'<youtube>(https?://[^<]+)</youtube>', body)
    for yt_url in yt_urls:
        vid_id = re.search(r'[?&]v=([a-zA-Z0-9_-]+)', yt_url)
        if not vid_id:
            continue
        try:
            r = subprocess.run(
                ["curl", "-sA", "TheVideshi/1.0",
                 f"https://www.youtube.com/oembed?url={yt_url}&format=json"],
                capture_output=True, text=True, timeout=10
            )
            data = json.loads(r.stdout)
            yt_title = data.get("title", "").lower()
            # Check overlap — at least 2 significant words should match
            hw = {w for w in headline.split() if len(w) > 3}
            yw = {w for w in yt_title.split() if len(w) > 3}
            overlap = hw & yw
            if len(overlap) < 1 and len(hw) > 2:
                issues.append(f"Possibly irrelevant YouTube: \"{data.get('title', '?')[:60]}\" vs headline")
        except:
            pass
    return issues


# ── LLM review ──

def llm_review(article, model="gpt-4o-mini"):
    """GPT-4o-mini editorial review — costs ~$0.001 per article."""
    if not OAI_KEY:
        return None
    
    headline = article.get("headline", "")
    category = article.get("category", "")
    body = article.get("body", "") or ""
    # Truncate body for cost
    body_preview = body[:3000] if len(body) > 3000 else body
    # Strip HTML for cleaner prompt
    body_text = re.sub(r'<[^>]+>', ' ', body_preview)
    body_text = re.sub(r'\s+', ' ', body_text).strip()
    
    has_yt = bool(re.search(r'<youtube>', body))
    has_tw = bool(re.search(r'x\.com/\w+/status/|twitter\.com/\w+/status/', body))
    has_ig = bool(re.search(r'instagram\.com/p/', body))
    embeds_summary = f"YouTube: {'yes' if has_yt else 'no'}, Tweet: {'yes' if has_tw else 'no'}, Instagram: {'yes' if has_ig else 'no'}"
    
    prompt = f"""You are an editorial QA reviewer for The Videshi, an Indian diaspora news site for NRIs.
Review this article critically and give 2-4 specific, actionable suggestions to improve it.

Focus on:
1. Is the diaspora/NRI angle strong enough? (This is the site's USP)
2. Would a specific social embed make this better? (e.g. "embed the official USCIS tweet about this policy")
3. Is the headline compelling and specific?
4. Any factual gaps or missing context that a reader would want?
5. Is the content structure good? (progression, depth)

Do NOT suggest generic improvements like "add more sources" or "make it more engaging."
Only suggest things that would concretely improve THIS specific article.

If the article is good, say so — don't force suggestions.

Article:
Headline: {headline}
Category: {category}
Current embeds: {embeds_summary}
Body (first 3000 chars): {body_text[:2000]}

Respond as JSON: {{"quality_score": 1-10, "suggestions": ["specific suggestion 1", ...], "embed_opportunities": ["specific embed idea if any"]}}"""

    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 500,
        "response_format": {"type": "json_object"}
    })
    
    try:
        r = subprocess.run(
            ["curl", "-s", "https://api.openai.com/v1/chat/completions",
             "-H", f"Authorization: Bearer {OAI_KEY}",
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(r.stdout)
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print(f"     LLM error: {e}")
        return None


# ── Main ──

def review_article(article, run_llm=True):
    """Run all checks on one article. Returns dict of issues and suggestions."""
    result = {
        "id": article["id"],
        "headline": article.get("headline", "")[:80],
        "slug": article.get("slug", ""),
        "category": article.get("category", ""),
        "structural_issues": [],
        "llm_review": None,
    }
    
    # Structural checks
    result["structural_issues"].extend(check_duplicate_embeds(article))
    result["structural_issues"].extend(check_hero_image(article))
    result["structural_issues"].extend(check_embed_placement(article))
    result["structural_issues"].extend(check_key_takeaways(article))
    result["structural_issues"].extend(check_duplicate_pull_quotes(article))
    result["structural_issues"].extend(check_youtube_relevance(article))
    
    # LLM review
    if run_llm:
        result["llm_review"] = llm_review(article)
    
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=int, default=12, help="Review articles from last N hours")
    parser.add_argument("--max", type=int, default=10, help="Max articles to review")
    parser.add_argument("--article-ids", type=str, help="Comma-separated article IDs")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM review (structural only)")
    parser.add_argument("--apply", action="store_true", help="Save report to file")
    args = parser.parse_args()
    
    print(f"═══ Article Quality Review ═══")
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    
    # Fetch articles
    if args.article_ids:
        ids = [i.strip() for i in args.article_ids.split(",")]
        articles = []
        for aid in ids:
            a = sb_get("p2_articles", {
                "id": f"eq.{aid}",
                "select": "id,headline,slug,category,body,social_embeds,image_url,published_at"
            })
            articles.extend(a)
    else:
        cutoff = quote((datetime.now(timezone.utc) - timedelta(hours=args.hours)).isoformat(), safe='')
        articles = sb_get("p2_articles", {
            "status": "eq.published",
            "published_at": f"gte.{cutoff}",
            "select": "id,headline,slug,category,body,social_embeds,image_url,published_at",
            "order": "published_at.desc",
            "limit": str(args.max)
        })
    
    print(f"Found {len(articles)} articles to review\n")
    
    # Load reviewed state to skip redundant LLM calls
    reviewed_state = _load_reviewed()
    
    results = []
    llm_skipped = 0
    for article in articles:
        headline = article.get("headline", "")[:75]
        aid = article.get("id", "")
        
        # Decide whether to run LLM: skip if already reviewed (unless --article-ids forces it)
        skip_llm = args.no_llm
        if not skip_llm and not args.article_ids and aid in reviewed_state:
            skip_llm = True
            llm_skipped += 1
        
        print(f"  📰 {headline}" + (" (LLM cached)" if skip_llm and not args.no_llm else ""))
        
        result = review_article(article, run_llm=not skip_llm)
        results.append(result)
        
        # Mark as reviewed if LLM ran successfully
        if not skip_llm and result.get("llm_review"):
            reviewed_state.add(aid)
        
        # Print structural issues
        if result["structural_issues"]:
            for issue in result["structural_issues"]:
                print(f"     ⚠️  {issue}")
        
        # Print LLM review
        llm = result.get("llm_review")
        if llm:
            score = llm.get("quality_score", "?")
            print(f"     Score: {score}/10")
            for s in llm.get("suggestions", []):
                print(f"     💡 {s}")
            for e in llm.get("embed_opportunities", []):
                if e:
                    print(f"     🔗 {e}")
        
        print()
    
    # Summary
    total_issues = sum(len(r["structural_issues"]) for r in results)
    avg_score = 0
    scored = [r for r in results if r.get("llm_review") and r["llm_review"].get("quality_score")]
    if scored:
        avg_score = sum(r["llm_review"]["quality_score"] for r in scored) / len(scored)
    
    print(f"═══ Summary ═══")
    print(f"Articles reviewed: {len(results)}")
    if llm_skipped:
        print(f"LLM reviews skipped (already reviewed): {llm_skipped}")
    print(f"Structural issues found: {total_issues}")
    if scored:
        print(f"Average quality score: {avg_score:.1f}/10")
    
    # Articles needing attention (score < 7 or structural issues)
    attention = [r for r in results if 
                 (r.get("llm_review") and r["llm_review"].get("quality_score", 10) < 7) or
                 len(r["structural_issues"]) > 0]
    if attention:
        print(f"Articles needing attention: {len(attention)}")
        for r in attention:
            print(f"  • {r['headline']}")
    
    # Save report
    if args.apply:
        report_dir = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reports")
        os.makedirs(report_dir, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
        report_path = os.path.join(report_dir, f"review-{ts}.json")
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nReport saved: {report_path}")
    
    # Persist reviewed state
    _save_reviewed(reviewed_state)
    
    return results


if __name__ == "__main__":
    main()
