#!/usr/bin/env python3
"""
proofread-article.py — Pre-publish proofreader and image QA.

Runs after enrichment, before feed rebuild. Uses GPT-4o-mini to:
  1. Check every inline image for relevance to the article
  2. Fix grammar, awkward phrasing, broken HTML
  3. Catch duplicate/repeated paragraphs
  4. Verify pull quotes exist in article text
  5. Flag duplicate embeds

Automatically removes irrelevant images and applies text fixes.
Runs as Step 4.5 in the V3 writer pipeline.

Usage:
  python3 -u proofread-article.py --hours 3              # dry run
  python3 -u proofread-article.py --hours 3 --apply      # apply fixes
  python3 -u proofread-article.py --article-ids ID1,ID2 --apply

Cost: ~$0.001-0.003 per article (GPT-4o-mini)

Env: ~/workspace/.env.supabase, ~/workspace/.env.openai
"""

import os
import sys
import json
import re
import time
import subprocess
import argparse
from datetime import datetime, timezone, timedelta

_dir = os.path.dirname(os.path.abspath(__file__))

# ─── Env ──────────────────────────────────────────────────────────────────────

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.openai"))

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

# ─── Supabase helpers ─────────────────────────────────────────────────────────

def sb_get(endpoint, params=None):
    url = f"{SB_URL}/rest/v1/{endpoint}"
    cmd = ["curl", "-sS", url,
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}"]
    if params:
        for k, v in params.items():
            cmd += ["-G", "--data-urlencode", f"{k}={v}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return json.loads(r.stdout)
    except Exception as e:
        print(f"  ⚠ Supabase GET error: {e}")
        return []


def sb_patch(article_id, updates):
    url = f"{SB_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    payload = json.dumps(updates)
    try:
        r = subprocess.run(
            ["curl", "-sS", "-X", "PATCH", url,
             "-H", f"apikey: {SB_KEY}",
             "-H", f"Authorization: Bearer {SB_KEY}",
             "-H", "Content-Type: application/json",
             "-H", "Prefer: return=minimal",
             "-d", payload],
            capture_output=True, text=True, timeout=15,
        )
        return r.returncode == 0
    except Exception as e:
        print(f"  ⚠ Supabase PATCH error: {e}")
        return False

# ─── Image extraction ─────────────────────────────────────────────────────────

def extract_inline_images(body):
    """Extract all inline images from the article body.
    Returns list of {tag, src, alt, caption, line_idx}."""
    images = []

    # HTML <figure> or <img> tags
    for m in re.finditer(
        r'<figure[^>]*>.*?<img\s+[^>]*src="([^"]+)"[^>]*alt="([^"]*)"[^>]*>.*?'
        r'(?:<figcaption[^>]*>(.*?)</figcaption>)?.*?</figure>',
        body, re.DOTALL
    ):
        images.append({
            "tag": m.group(0),
            "src": m.group(1),
            "alt": m.group(2),
            "caption": m.group(3) or m.group(2),
        })

    # Standalone <img> not inside <figure>
    for m in re.finditer(r'<img\s+[^>]*src="([^"]+)"[^>]*alt="([^"]*)"[^>]*>', body):
        full = m.group(0)
        # Skip if already captured inside a figure
        if any(full in img["tag"] for img in images):
            continue
        images.append({
            "tag": full,
            "src": m.group(1),
            "alt": m.group(2),
            "caption": m.group(2),
        })

    # Markdown images ![alt](src)
    for m in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', body):
        images.append({
            "tag": m.group(0),
            "src": m.group(2),
            "alt": m.group(1),
            "caption": m.group(1),
        })

    return images


def extract_pull_quotes(body):
    """Extract pull quotes from article body."""
    quotes = []
    for m in re.finditer(
        r'<blockquote\s+class="pull-quote"[^>]*>\s*<p>"?(.*?)"?</p>',
        body, re.DOTALL
    ):
        quotes.append(m.group(1).strip())
    return quotes

# ─── GPT-4o-mini proofreader ─────────────────────────────────────────────────

def call_gpt(headline, category, body_text, images_desc, pull_quotes):
    """Send article to GPT-4o-mini for proofreading. Returns structured JSON."""

    images_block = ""
    if images_desc:
        img_lines = []
        for i, img in enumerate(images_desc):
            img_lines.append(f"  Image {i+1}: alt=\"{img['alt']}\", caption=\"{img['caption']}\", src_domain={img.get('domain','unknown')}")
        images_block = "INLINE IMAGES:\n" + "\n".join(img_lines)
    else:
        images_block = "INLINE IMAGES: none"

    quotes_block = ""
    if pull_quotes:
        quotes_block = "PULL QUOTES:\n" + "\n".join(f"  - \"{q[:100]}...\"" if len(q) > 100 else f"  - \"{q}\"" for q in pull_quotes)

    # Truncate body to ~4000 chars for cost efficiency (enough for proofreading)
    body_truncated = body_text[:5000]

    prompt = f"""You are a professional news editor proofreading an article before publication on The Videshi, an Indian diaspora news site.

HEADLINE: {headline}
CATEGORY: {category}
{images_block}
{quotes_block}

ARTICLE BODY (may be truncated):
{body_truncated}

Review the article and return a JSON object with these fields:

1. "images_to_remove": array of image indices (1-based) that are IRRELEVANT to this specific article.
   An image is irrelevant if:
   - It shows something unrelated to the article's topic (e.g., an airplane photo on a flood story, a band photo on a business story)
   - It's a generic stock photo that doesn't add value (e.g., generic laptop photo on a specific company story)
   - Its alt/caption references something not discussed in the article
   Be CONSERVATIVE — only flag images that are clearly wrong or irrelevant. A topically related image is fine even if generic.

2. "text_fixes": array of objects with "old" (exact text to find) and "new" (replacement text) for:
   - Grammar errors
   - Awkward phrasing that reads poorly
   - Broken/malformed HTML tags
   - Repeated words or stuttering
   Keep fixes minimal and precise. Do NOT rewrite style or voice. Only fix clear errors.
   Each "old" string must be an EXACT substring from the article body.

3. "pull_quote_issues": array of strings describing any pull quote problems (quote not in article, misattributed, etc.)

4. "other_issues": array of strings for anything else notable (duplicate paragraphs, broken formatting, etc.)

5. "verdict": "clean" if no issues found, "minor" if only small fixes, "major" if significant problems

Return ONLY valid JSON, no markdown formatting."""

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 1000,
        "response_format": {"type": "json_object"},
    })

    try:
        r = subprocess.run(
            ["curl", "-sS", "--max-time", "30",
             "https://api.openai.com/v1/chat/completions",
             "-H", f"Authorization: Bearer {OPENAI_KEY}",
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True, text=True, timeout=35,
        )
        if r.returncode != 0:
            print(f"     ⚠ GPT call failed (curl error)")
            return None

        resp = json.loads(r.stdout)
        if "error" in resp:
            print(f"     ⚠ GPT error: {resp['error'].get('message','unknown')[:80]}")
            return None

        content = resp["choices"][0]["message"]["content"]
        return json.loads(content)

    except Exception as e:
        print(f"     ⚠ GPT proofreader error: {e}")
        return None

# ─── Apply fixes ──────────────────────────────────────────────────────────────

def apply_proofread(article, review, dry_run=True):
    """Apply proofread fixes to an article. Returns (changes_desc, updates_dict) or (None, None)."""
    body = article.get("body") or ""
    new_body = body
    changes = []

    images = extract_inline_images(body)

    # 1. Remove irrelevant images
    images_to_remove = review.get("images_to_remove", [])
    removed_count = 0
    for idx in sorted(images_to_remove, reverse=True):  # reverse so indices stay valid
        if 1 <= idx <= len(images):
            img = images[idx - 1]
            tag = img["tag"]
            # Remove the figure/img tag and clean up surrounding whitespace
            if tag in new_body:
                new_body = new_body.replace(tag, "")
                removed_count += 1
                changes.append(f"removed image: {img['alt'][:50]}")
                print(f"     🗑 Remove image {idx}: \"{img['alt'][:60]}\"")

    # 2. Apply text fixes
    text_fixes = review.get("text_fixes", [])
    fix_count = 0
    for fix in text_fixes[:10]:  # cap at 10 fixes per article
        old = fix.get("old", "")
        new = fix.get("new", "")
        if old and old in new_body and old != new:
            new_body = new_body.replace(old, new, 1)  # replace first occurrence only
            fix_count += 1
            # Show a short preview of the fix
            old_preview = old[:40].replace('\n', ' ')
            new_preview = new[:40].replace('\n', ' ')
            print(f"     ✏️  Fix: \"{old_preview}\" → \"{new_preview}\"")

    if fix_count:
        changes.append(f"{fix_count} text fix{'es' if fix_count > 1 else ''}")

    # 3. Log other issues (informational only)
    for issue in review.get("pull_quote_issues", []):
        print(f"     ⚠ Pull quote: {issue[:80]}")
    for issue in review.get("other_issues", []):
        print(f"     ⚠ Other: {issue[:80]}")

    # Clean up triple+ blank lines
    new_body = re.sub(r'\n{3,}', '\n\n', new_body)

    if new_body == body:
        return None, None

    updates = {"body": new_body}
    change_desc = " + ".join(changes)
    return change_desc, updates


# ─── Main ─────────────────────────────────────────────────────────────────────

def fetch_articles(article_ids=None, hours=3):
    if article_ids:
        params = {
            "select": "id,headline,slug,category,body,image_url,published_at",
            "id": f"in.({','.join(article_ids)})",
            "status": "eq.published",
        }
    else:
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
        params = {
            "select": "id,headline,slug,category,body,image_url,published_at",
            "status": "eq.published",
            "published_at": f"gte.{since}",
            "order": "published_at.desc",
            "limit": "50",
        }
    return sb_get("p2_articles", params)


def main():
    parser = argparse.ArgumentParser(description="Proofread articles before final publish")
    parser.add_argument("--article-ids", type=str, help="Comma-separated article UUIDs")
    parser.add_argument("--hours", type=int, default=3, help="Look back N hours (default 3)")
    parser.add_argument("--apply", action="store_true", help="Apply fixes to Supabase")
    parser.add_argument("--max", type=int, default=20, help="Max articles to proofread")
    args = parser.parse_args()

    print("═══ Article Proofreader ═══")
    start = time.time()

    if not OPENAI_KEY:
        print("  ❌ No OPENAI_API_KEY — cannot proofread")
        sys.exit(1)

    article_ids = args.article_ids.split(",") if args.article_ids else None
    articles = fetch_articles(article_ids, args.hours)
    print(f"Articles: {len(articles)} found\n")

    report = {"proofread": 0, "fixed": 0, "clean": 0, "errors": 0,
              "images_removed": 0, "text_fixes": 0}

    for article in articles[:args.max]:
        headline = article["headline"]
        body = article.get("body") or ""
        category = article.get("category", "")

        print(f"  📝 {headline[:75]}")
        print(f"     [{category}]")

        # Extract images and pull quotes for the LLM
        images = extract_inline_images(body)
        pull_quotes = extract_pull_quotes(body)

        # Build image descriptions for LLM
        images_desc = []
        for img in images:
            src = img["src"]
            # Extract domain for context
            domain_match = re.search(r'https?://([^/]+)', src)
            domain = domain_match.group(1) if domain_match else "unknown"
            images_desc.append({
                "alt": img["alt"],
                "caption": img["caption"],
                "domain": domain,
            })

        if not images and not pull_quotes:
            # Strip HTML for basic text-only body
            body_text = re.sub(r'<[^>]+>', ' ', body)
            body_text = re.sub(r'\s+', ' ', body_text).strip()
        else:
            body_text = re.sub(r'<[^>]+>', ' ', body)
            body_text = re.sub(r'\s+', ' ', body_text).strip()

        # Call GPT-4o-mini
        review = call_gpt(headline, category, body_text, images_desc, pull_quotes)
        if not review:
            report["errors"] += 1
            continue

        verdict = review.get("verdict", "unknown")
        n_img_remove = len(review.get("images_to_remove", []))
        n_text_fix = len(review.get("text_fixes", []))

        if verdict == "clean" and n_img_remove == 0 and n_text_fix == 0:
            print(f"     ✅ Clean")
            report["clean"] += 1
            report["proofread"] += 1
            continue

        print(f"     Verdict: {verdict} | {n_img_remove} images to remove | {n_text_fix} text fixes")

        # Apply fixes
        change_desc, updates = apply_proofread(article, review, dry_run=not args.apply)

        if change_desc and updates:
            if args.apply:
                if sb_patch(article["id"], updates):
                    print(f"     ✅ Applied: {change_desc}")
                    report["fixed"] += 1
                else:
                    print(f"     ❌ Patch failed")
                    report["errors"] += 1
            else:
                print(f"     [DRY RUN] Would apply: {change_desc}")
                report["fixed"] += 1

            report["images_removed"] += n_img_remove
            report["text_fixes"] += n_text_fix
        else:
            print(f"     ✅ No actionable fixes (issues are informational)")
            report["clean"] += 1

        report["proofread"] += 1

    elapsed = time.time() - start
    print(f"\n═══ Done in {elapsed:.1f}s ═══")
    print(f"Proofread: {report['proofread']}, Clean: {report['clean']}, Fixed: {report['fixed']}, Errors: {report['errors']}")
    print(f"Images removed: {report['images_removed']}, Text fixes: {report['text_fixes']}")


if __name__ == "__main__":
    main()
