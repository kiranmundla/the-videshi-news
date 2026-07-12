#!/usr/bin/env python3
"""
article-cards-ai.py — GPT-generated designed article cards using hero images.
Same approach as reel scene generation but for 4:5 portrait cards.
"""

import os, sys, json, hashlib, subprocess, base64, time
from pathlib import Path

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
load_env("~/workspace/.env.openai")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

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

def download_hero(url, timeout=15):
    """Download hero image and compress for API, return path or None."""
    tmp = f"/tmp/ai_hero_{hashlib.md5(url.encode()).hexdigest()[:12]}.jpg"
    r = subprocess.run(
        ["curl", "-sS", "-L", "-o", tmp, "--max-time", str(timeout),
         "-A", "TheVideshi/1.0", url],
        capture_output=True, timeout=timeout+5
    )
    if r.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 1000:
        # Compress to keep payload small
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

def image_to_b64(path):
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode()

def extract_body_images(body, max_images=2):
    """Extract inline image URLs from article markdown body."""
    import re
    if not body:
        return []
    # Match markdown images: ![alt](url)
    urls = re.findall(r'!\[.*?\]\((https?://[^\)]+)\)', body)
    return urls[:max_images]

def generate_card_ai(article):
    """Use GPT image generation to create a designed card from hero + body images."""
    hero_path = download_hero(article["image_url"])
    if not hero_path:
        return None

    cat = article.get("category", "news")
    color_desc = CATEGORY_COLORS.get(cat, "navy blue")
    headline = article["headline"]
    cat_upper = cat.replace("-", " & ").upper()

    # Build image inputs: hero + any body images
    image_inputs = []
    hero_b64 = image_to_b64(hero_path)
    image_inputs.append({
        "type": "input_image",
        "image_url": f"data:image/jpeg;base64,{hero_b64}"
    })

    body_imgs = extract_body_images(article.get("body", ""))
    for burl in body_imgs:
        bpath = download_hero(burl)
        if bpath:
            bb64 = image_to_b64(bpath)
            image_inputs.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{bb64}"
            })

    img_count = len(image_inputs)
    img_note = f"I'm providing {img_count} image(s) from this article." if img_count > 1 else "I'm providing the article's hero image."

    prompt = f"""Create a professional, visually striking 4:5 portrait news card design.

{img_note} Use the photo(s) prominently in the design — the main image should be clearly visible and take up a significant portion of the card.

Design requirements:
- Category: {cat_upper} (use {color_desc} as the accent/theme color)
- Headline text on the card: "{headline}"
- The headline should be large, bold, white text over a dark gradient at the bottom
- Small "{cat_upper}" category label above the headline
- Small "THEVIDESHI.COM" branding in gold at the bottom
- Clean, modern news media aesthetic — think CNN, Bloomberg, or Moneycontrol social cards
- Professional gradient transitions between the photo and text area
- ONLY use the exact headline text provided — no fake text or placeholders"""

    content_parts = [{"type": "input_text", "text": prompt}] + image_inputs

    # Use Responses API (same as reel pipeline) with image_generation tool
    payload = {
        "model": "gpt-4o",
        "input": [
            {
                "role": "user",
                "content": content_parts
            }
        ],
        "tools": [{"type": "image_generation", "quality": "medium", "size": "1024x1536"}]
    }

    out_path = f"/tmp/ai_card_{article['slug'][:40]}.png"

    # Write payload to temp file (too large for command line)
    payload_path = f"/tmp/ai_card_payload_{hashlib.md5(article['slug'].encode()).hexdigest()[:8]}.json"
    with open(payload_path, "w") as f:
        json.dump(payload, f)

    result = subprocess.run(
        ["curl", "-sS", "-X", "POST", "https://api.openai.com/v1/responses",
         "-H", f"Authorization: Bearer {OPENAI_API_KEY}",
         "-H", "Content-Type: application/json",
         "-d", f"@{payload_path}"],
        capture_output=True, timeout=180
    )

    # Clean up payload file
    try:
        os.remove(payload_path)
    except:
        pass

    try:
        resp = json.loads(result.stdout)
        # Extract generated image from Responses API output
        for item in resp.get("output", []):
            if item.get("type") == "image_generation_call":
                img_b64 = item.get("result", "")
                if img_b64 and len(img_b64) > 100:
                    with open(out_path, "wb") as f:
                        f.write(base64.b64decode(img_b64))
                    return out_path
        # No image found
        print(f"    No image generated. Status: {resp.get('status')}", file=sys.stderr)
        for item in resp.get("output", []):
            if item.get("type") == "message":
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        print(f"    GPT said: {c['text'][:200]}", file=sys.stderr)
    except Exception as e:
        print(f"    Parse error: {e}", file=sys.stderr)
        print(f"    stdout[:300]: {result.stdout.decode() if isinstance(result.stdout, bytes) else result.stdout[:300]}", file=sys.stderr)

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
    print(f"🎨 Generating AI cards for {len(articles)} articles...")

    for i, art in enumerate(articles, 1):
        print(f"  [{i}/{len(articles)}] {art['headline'][:55]}...")
        path = generate_card_ai(art)
        if path:
            print(f"    ✓ {path}")
        else:
            print(f"    ✗ Failed")
        time.sleep(1)  # rate limit spacing

if __name__ == "__main__":
    main()
