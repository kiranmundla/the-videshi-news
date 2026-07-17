#!/usr/bin/env python3
"""
enhance-images.py — GPT-driven image enhancement for articles.

For each article:
1. GPT-4o-mini analyzes headline + body → generates targeted Pexels search queries
2. Pexels API returns candidate images
3. GPT-4o-mini selects best images and writes contextual captions
4. Dry-run prints results; --apply updates DB

Usage:
  python3 -u enhance-images.py --ids ID1,ID2,...
  python3 -u enhance-images.py --latest 5
  python3 -u enhance-images.py --latest 3 --apply
"""

import os, sys, json, subprocess, time, argparse, re, textwrap
from urllib.parse import quote_plus

# ── env ──────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

def curl_json(method, url, headers=None, data=None):
    """HTTP via curl (proxy-safe)."""
    cmd = ["curl", "-s", "-X", method, url]
    for k, v in (headers or {}).items():
        cmd += ["-H", f"{k}: {v}"]
    if data:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if not r.stdout.strip():
        return None
    return json.loads(r.stdout)


# ── Supabase helpers ─────────────────────────────────────────────────
def fetch_articles(ids=None, latest=None):
    """Fetch articles from DB."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?select=id,headline,slug,category,body,image_url,image_caption"
    if ids:
        id_filter = ",".join(f'"{i}"' for i in ids)
        url += f"&id=in.({','.join(ids)})"
    else:
        url += f"&status=eq.published&order=created_at.desc&limit={latest or 5}"
    return curl_json("GET", url, {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }) or []


def update_article(article_id, image_url, image_caption, body=None):
    """Patch article with new hero image + caption, optionally updated body."""
    patch = {"image_url": image_url, "image_caption": image_caption}
    if body:
        patch["body"] = body
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    return curl_json("PATCH", url, {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Prefer": "return=minimal"
    }, patch)


# ── OpenAI helper ────────────────────────────────────────────────────
def gpt_call(system_prompt, user_prompt, temperature=0.3):
    """Call GPT-4o-mini and return parsed JSON."""
    payload = {
        "model": "gpt-4o-mini",
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    result = curl_json("POST", "https://api.openai.com/v1/chat/completions", {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }, payload)
    if not result or "choices" not in result:
        print(f"  ❌ GPT call failed: {result}")
        return None
    content = result["choices"][0]["message"]["content"]
    return json.loads(content)


# ── Pexels helper ────────────────────────────────────────────────────
def pexels_search(query, per_page=6):
    """Search Pexels, return simplified results."""
    url = f"https://api.pexels.com/v1/search?query={quote_plus(query)}&per_page={per_page}&orientation=landscape"
    data = curl_json("GET", url, {"Authorization": PEXELS_API_KEY})
    if not data or "photos" not in data:
        return []
    results = []
    for p in data["photos"]:
        results.append({
            "pexels_id": p["id"],
            "alt": p.get("alt", ""),
            "photographer": p["photographer"],
            "url_large": p["src"]["large2x"],  # 1880px wide, good for hero
            "url_medium": p["src"]["large"],    # 940px, good for inline
            "width": p["width"],
            "height": p["height"],
        })
    return results


# ── Step 1: Generate search queries ─────────────────────────────────
def generate_queries(article):
    """Ask GPT to generate targeted image search queries for this article."""
    body_snippet = (article.get("body") or "")[:1500]
    # Strip markdown images/links for cleaner context
    body_snippet = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', body_snippet)
    body_snippet = re.sub(r'\[([^\]]*)\]\([^)]+\)', r'\1', body_snippet)

    system = """You are an image editor for a news website. Given an article headline, category, and opening text, generate targeted photo search queries for a stock photo site (Pexels).

Return JSON:
{
  "queries": [
    {"query": "search terms", "role": "hero|cuisine|location|context|person|event", "description": "what kind of image this should find"}
  ]
}

Rules:
- Generate 3-4 queries, each targeting a DIFFERENT visual aspect of the story
- First query should be the best hero image candidate (wide, editorial, establishing shot)
- Be specific: "downtown Juneau Alaska waterfront" not just "Alaska"
- For food articles: include a cuisine-specific query (e.g. "Indian thali curry naan" not just "food")
- For people: search for the role/context, not the person's name (stock sites won't have them)
- For finance/markets: search for relevant imagery (trading floor, stock chart, company HQ)
- For tech: search for the product/concept visually
- Keep queries to 3-6 words for best results"""

    user = f"""Headline: {article['headline']}
Category: {article.get('category', 'news')}

Article opening:
{body_snippet}"""

    return gpt_call(system, user)


# ── Step 2: Select images and write captions ─────────────────────────
def select_and_caption(article, all_candidates):
    """Ask GPT to pick the best images and write contextual captions."""
    # Build candidates summary
    candidates_text = ""
    for group in all_candidates:
        candidates_text += f"\n--- Query: \"{group['query']}\" (role: {group['role']}) ---\n"
        for i, img in enumerate(group["results"]):
            candidates_text += f"  [{group['query_idx']}-{i}] alt=\"{img['alt']}\" by {img['photographer']} ({img['width']}x{img['height']})\n"

    system = """You are a photo editor for TheVideshi.com, an Indian diaspora news site. Select the best images for an article and write contextual captions.

Return JSON:
{
  "hero": {
    "pick": "query_idx-result_idx",
    "caption": "Two sentences. First: what the image shows. Second: the article context."
  },
  "body_images": [
    {
      "pick": "query_idx-result_idx",
      "caption": "Two sentences. First: what the image shows. Second: the article context.",
      "placement_hint": "after which topic/paragraph this image fits best"
    }
  ]
}

Rules:
- Pick 1 hero image (wide, editorial, landscape orientation preferred)
- Pick 1-2 body images (different from hero, different visual aspects)
- NEVER claim a stock photo is the actual person, restaurant, or place in the story
- Caption format: Two short factual sentences. Sentence 1 = what the image shows. Sentence 2 = the relevant news context from the article. Just state the facts plainly.
- Do NOT use words like "symbolizing", "representing", "reflecting", "embodying", "illustrating", "showcasing". Just say what it is, then say what's happening in the news.
- Example: "A close-up of a microchip on a printed circuit board. The semiconductor industry is experiencing significant stock declines as investors pivot to software giants."
- Example: "The Federal Reserve building in Washington, D.C. Treasury yields are signaling potential interest rate hikes ahead."
- Prefer images with relevant, specific alt text over generic ones
- Credit line is automatic — don't include photographer name in the caption"""

    body_snippet = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', (article.get("body") or ""))[:1000]

    user = f"""Article: {article['headline']}
Category: {article.get('category', 'news')}
Opening: {body_snippet[:500]}

Available images:
{candidates_text}"""

    return gpt_call(system, user)


# ── Main pipeline ────────────────────────────────────────────────────
def enhance_article(article, apply=False):
    """Full enhancement pipeline for one article."""
    print(f"\n{'='*70}")
    print(f"📰 {article['headline']}")
    print(f"   Category: {article.get('category')}  |  ID: {article['id'][:8]}")

    # Current state
    hero = article.get("image_url", "")
    hero_source = "wikimedia" if "wikimedia" in hero else "pexels" if "pexels" in hero else "other"
    print(f"   Current hero: [{hero_source}] {hero[:80]}...")
    print(f"   Current caption: {article.get('image_caption') or 'NONE'}")

    # Step 1: Generate queries
    print(f"\n   🔍 Step 1: Generating search queries...")
    queries_result = generate_queries(article)
    if not queries_result or "queries" not in queries_result:
        print("   ❌ Failed to generate queries")
        return None

    queries = queries_result["queries"]
    for q in queries:
        print(f"      → [{q['role']}] \"{q['query']}\"")

    # Step 2: Search Pexels
    print(f"\n   📷 Step 2: Searching Pexels...")
    all_candidates = []
    for idx, q in enumerate(queries):
        results = pexels_search(q["query"])
        print(f"      [{q['role']}] \"{q['query']}\" → {len(results)} results")
        all_candidates.append({
            "query": q["query"],
            "role": q["role"],
            "query_idx": idx,
            "results": results
        })
        time.sleep(0.2)  # polite rate limiting

    # Step 3: Select and caption
    print(f"\n   ✍️  Step 3: Selecting images and writing captions...")
    selection = select_and_caption(article, all_candidates)
    if not selection:
        print("   ❌ Failed to select/caption")
        return None

    # Resolve picks to actual image data
    def resolve_pick(pick_str):
        parts = pick_str.split("-")
        q_idx, r_idx = int(parts[0]), int(parts[1])
        if q_idx < len(all_candidates) and r_idx < len(all_candidates[q_idx]["results"]):
            return all_candidates[q_idx]["results"][r_idx]
        return None

    hero_pick = resolve_pick(selection["hero"]["pick"])
    body_picks = []
    for bp in selection.get("body_images", []):
        img = resolve_pick(bp["pick"])
        if img:
            body_picks.append({"image": img, "caption": bp["caption"], "hint": bp.get("placement_hint", "")})

    # Display results
    print(f"\n   ✅ RESULTS:")
    if hero_pick:
        print(f"\n   🖼️  HERO IMAGE:")
        print(f"      Photo: {hero_pick['alt'][:70]}")
        print(f"      Credit: {hero_pick['photographer']} / Pexels")
        print(f"      Caption: {selection['hero']['caption']}")
        print(f"      URL: {hero_pick['url_large'][:80]}...")

    for i, bp in enumerate(body_picks):
        print(f"\n   🖼️  BODY IMAGE {i+1}:")
        print(f"      Photo: {bp['image']['alt'][:70]}")
        print(f"      Credit: {bp['image']['photographer']} / Pexels")
        print(f"      Caption: {bp['caption']}")
        print(f"      Placement: {bp['hint']}")
        print(f"      URL: {bp['image']['url_medium'][:80]}...")

    result = {
        "article_id": article["id"],
        "headline": article["headline"],
        "hero": {
            "url": hero_pick["url_large"] if hero_pick else None,
            "caption": selection["hero"]["caption"],
            "credit": f"Photo: {hero_pick['photographer']} / Pexels" if hero_pick else None,
            "alt": hero_pick["alt"] if hero_pick else None,
        },
        "body_images": [{
            "url": bp["image"]["url_medium"],
            "caption": bp["caption"],
            "credit": f"Photo: {bp['image']['photographer']} / Pexels",
            "alt": bp["image"]["alt"],
            "placement_hint": bp["hint"]
        } for bp in body_picks]
    }

    # Apply to DB if requested
    if apply and hero_pick:
        print(f"\n   💾 Applying to DB...")
        full_caption = f"{selection['hero']['caption']} (Photo: {hero_pick['photographer']} / Pexels)"
        update_article(article["id"], hero_pick["url_large"], full_caption)
        print(f"   ✅ Hero image + caption updated")

    return result


def main():
    parser = argparse.ArgumentParser(description="Enhance article images with GPT + Pexels")
    parser.add_argument("--ids", help="Comma-separated article IDs")
    parser.add_argument("--latest", type=int, help="Enhance N latest published articles")
    parser.add_argument("--apply", action="store_true", help="Actually update DB (default: dry-run)")
    args = parser.parse_args()

    if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY, PEXELS_API_KEY]):
        print("❌ Missing env vars. Source .env.supabase, .env.openai, .env.pexels")
        sys.exit(1)

    # Fetch articles
    ids = args.ids.split(",") if args.ids else None
    articles = fetch_articles(ids=ids, latest=args.latest or 5)
    print(f"📋 Found {len(articles)} articles to enhance")

    results = []
    for art in articles:
        r = enhance_article(art, apply=args.apply)
        if r:
            results.append(r)

    # Summary
    print(f"\n{'='*70}")
    print(f"📊 SUMMARY: Enhanced {len(results)}/{len(articles)} articles")
    if not args.apply:
        print(f"   (dry-run — use --apply to update DB)")

    # Save results to file for review
    out_path = "/tmp/enhance-images-results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"   Results saved to {out_path}")


if __name__ == "__main__":
    main()
