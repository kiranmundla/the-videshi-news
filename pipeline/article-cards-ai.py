#!/usr/bin/env python3
"""
article-cards-ai.py — Gemini-generated designed article cards using hero + body images.
Same engine as reel scene generation (gemini-2.5-flash-image).
"""

import os, sys, json, hashlib, subprocess, base64, time, re
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent

def load_env(path):
    p = os.path.expanduser(path)
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env("~/workspace/.env.supabase")
load_env("~/workspace/.env.google-ai")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
GEMINI_KEY = os.environ.get("GOOGLE_AI_API_KEY", "")

# Style reference storyboards (same as reel pipeline)
GEMINI_REF_1 = PIPELINE_DIR / "assets" / "gemini-ref-storyboard-1.jpg"
GEMINI_REF_2 = PIPELINE_DIR / "assets" / "gemini-ref-storyboard-2.jpg"

CATEGORY_COLORS = {
    "immigration": "deep crimson red",
    "technology": "electric blue",
    "entertainment": "rich purple",
    "sports": "vibrant green",
    "news": "bold red",
    "markets-finance": "warm amber/gold",
    "nri-world": "teal/cyan",
    "travel": "ocean teal",
    "lifestyle-health": "magenta pink",
    "food": "warm orange",
}

def download_image(url, timeout=15):
    """Download and compress image for API."""
    tmp = f"/tmp/ai_hero_{hashlib.md5(url.encode()).hexdigest()[:12]}.jpg"
    r = subprocess.run(
        ["curl", "-sS", "-L", "-o", tmp, "--max-time", str(timeout),
         "-A", "TheVideshi/1.0", url],
        capture_output=True, timeout=timeout+5
    )
    if r.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 1000:
        try:
            from PIL import Image
            im = Image.open(tmp).convert("RGB")
            im.thumbnail((900, 900))
            compressed = tmp.replace(".jpg", "_sm.jpg")
            im.save(compressed, quality=75)
            return compressed
        except:
            return tmp
    return None

def img_to_b64(path):
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode()

def extract_body_images(body, max_images=2):
    if not body:
        return []
    return re.findall(r'!\[.*?\]\((https?://[^\)]+)\)', body)[:max_images]

def generate_card_gemini(article):
    """Use Gemini 2.5 Flash Image to create a data-rich card (same engine as reels)."""
    hero_path = download_image(article["image_url"])
    if not hero_path:
        print("    ✗ Hero download failed", file=sys.stderr)
        return None

    cat = article.get("category", "news")
    color_desc = CATEGORY_COLORS.get(cat, "navy blue")
    headline = article["headline"]
    cat_upper = cat.replace("-", " & ").upper()
    body_text = (article.get("body") or "")[:2500]

    # Build multimodal parts
    parts = []

    # Style reference storyboards (same as reel pipeline)
    has_refs = False
    if GEMINI_REF_1.exists() and GEMINI_REF_2.exists():
        for ref_path in [GEMINI_REF_1, GEMINI_REF_2]:
            parts.append({
                "inlineData": {
                    "mimeType": "image/jpeg",
                    "data": img_to_b64(str(ref_path))
                }
            })
        has_refs = True

    # Hero image
    parts.append({
        "inlineData": {
            "mimeType": "image/jpeg",
            "data": img_to_b64(hero_path)
        }
    })

    # Body images
    body_imgs = extract_body_images(article.get("body", ""))
    body_img_count = 0
    for burl in body_imgs:
        bpath = download_image(burl)
        if bpath:
            parts.append({
                "inlineData": {
                    "mimeType": "image/jpeg",
                    "data": img_to_b64(bpath)
                }
            })
            body_img_count += 1

    total_imgs = 1 + body_img_count

    # Build the prompt
    ref_intro = (
        "The first two images are STYLE REFERENCES showing the visual quality I want — "
        "notice the bright colors, vivid photographic style, dramatic data callouts with "
        "big bold numbers, cinematic lighting, strong composition. "
        "Match this energy and richness.\n\n"
    ) if has_refs else ""

    photo_intro = (
        f"The next {total_imgs} image(s) are from this article (hero photo + inline images). "
        f"Use them creatively — as background, inset, or composed into the design.\n\n"
    )

    prompt = (
        f"{ref_intro}"
        f"{photo_intro}"
        f"Now create a SINGLE 4:5 PORTRAIT NEWS CARD IMAGE (like an Instagram news card or "
        f"YouTube community post card).\n\n"
        f"Category: {cat_upper} (use {color_desc} as accent color)\n"
        f"Headline: \"{headline}\"\n\n"
        f"ARTICLE CONTENT (extract the most impactful stat or data point):\n"
        f"{body_text}\n\n"
        f"DESIGN GOALS:\n"
        f"- Extract the BIGGEST stat/number from the article and make it HUGE and bold "
        f"(like \"$42 BILLION\" or \"4.93M BARRELS\" or \"+26.5%\" or \"5-4 MAJORITY\")\n"
        f"- Dark, dramatic, cinematic background using the article photo(s)\n"
        f"- Bold headline text, large enough to read at thumbnail size\n"
        f"- Small \"{cat_upper}\" category label\n"
        f"- Small \"THEVIDESHI.COM\" branding in gold at the bottom\n"
        f"- Information-dense — key takeaway visible at a glance\n"
        f"- Think CNN breaking news graphics or Bloomberg data visualization cards\n"
        f"- The card should GRAB ATTENTION when scrolling on a phone\n\n"
        f"RULES:\n"
        f"- Use ONLY real data from the article — no placeholder or made-up numbers\n"
        f"- The headline text must be the EXACT headline provided\n"
        f"- Make it visually rich and dramatic, NOT plain or corporate"
    )

    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}
    }

    # Write payload to file (too large for -d inline)
    slug_hash = hashlib.md5(article["slug"].encode()).hexdigest()[:8]
    payload_path = f"/tmp/ai_card_payload_{slug_hash}.json"
    with open(payload_path, "w") as f:
        json.dump(payload, f)

    out_path = f"/tmp/ai_card_{article['slug'][:40]}.png"

    gem_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={GEMINI_KEY}"
    result = subprocess.run(
        ["curl", "-sS", "-X", "POST", gem_url,
         "-H", "Content-Type: application/json",
         "-d", f"@{payload_path}", "--max-time", "120"],
        capture_output=True, timeout=150
    )

    # Cleanup payload
    try:
        os.remove(payload_path)
    except:
        pass

    try:
        resp = json.loads(result.stdout)
        # Extract image from Gemini response
        for candidate in resp.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if "inlineData" in part:
                    img_b64 = part["inlineData"].get("data", "")
                    if img_b64:
                        with open(out_path, "wb") as f:
                            f.write(base64.b64decode(img_b64))
                        return out_path
        # No image
        err = resp.get("error")
        if err:
            print(f"    Gemini error: {json.dumps(err)[:200]}", file=sys.stderr)
        else:
            # Print text parts for debugging
            for candidate in resp.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "text" in part:
                        print(f"    Gemini text: {part['text'][:200]}", file=sys.stderr)
    except Exception as e:
        print(f"    Parse error: {e}", file=sys.stderr)
        raw = result.stdout.decode() if isinstance(result.stdout, bytes) else str(result.stdout)
        print(f"    raw[:300]: {raw[:300]}", file=sys.stderr)

    return None


def fetch_articles(category=None, limit=5):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&image_url=not.is.null&order=published_at.desc&limit={limit}&select=slug,headline,image_url,category,body"
    if category:
        url += f"&category=eq.{category}"
    r = subprocess.run(
        ["curl", "-sS", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, timeout=15
    )
    return json.loads(r.stdout)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", default=None)
    parser.add_argument("--limit", type=int, default=4)
    args = parser.parse_args()

    articles = fetch_articles(category=args.category, limit=args.limit)
    print(f"🎨 Generating AI cards (Gemini) for {len(articles)} articles...")

    for i, art in enumerate(articles, 1):
        print(f"  [{i}/{len(articles)}] {art['headline'][:55]}...")
        path = generate_card_gemini(art)
        if path:
            print(f"    ✓ {path}")
        else:
            print(f"    ✗ Failed")
        time.sleep(2)  # rate limit

if __name__ == "__main__":
    main()
