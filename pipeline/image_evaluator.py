#!/usr/bin/env python3
"""
Evaluate article images (hero + body) for reel inclusion.

Quality tiers:
  - DIRECT:  High-res, clear subject, usable as a full reel scene
  - BLEND:   Decent but not great — pass as reference to AI generator
  - SKIP:    Too low quality, broken, or generic to use

Returns a list of scored images with tier, resolution, and description.
"""

import os, sys, re, json, base64, requests
from io import BytesIO
from urllib.parse import urlparse

# Supabase env
SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SB_HEADERS = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}

# OpenAI
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

# Minimum dimensions for each tier
MIN_WIDTH_DIRECT = 800   # Full scene use
MIN_WIDTH_BLEND = 400    # Reference for AI blending
MIN_HEIGHT_DIRECT = 600
MIN_HEIGHT_BLEND = 300


def _download_image(url, timeout=15):
    """Download image, return (bytes, width, height) or None."""
    try:
        r = requests.get(url, timeout=timeout, headers={
            "User-Agent": "TheVideshi/1.0 (thevideshi.com)"
        })
        if r.status_code != 200:
            return None
        img_bytes = r.content
        if len(img_bytes) < 5000:  # too small, likely broken
            return None
        
        # Get dimensions via PIL
        from PIL import Image
        img = Image.open(BytesIO(img_bytes))
        w, h = img.size
        return img_bytes, w, h
    except Exception as e:
        print(f"  ⚠️ Download failed for {url[:60]}: {e}")
        return None


def _vision_evaluate(img_b64, article_headline, img_source="hero"):
    """Ask GPT-4o to evaluate image quality and relevance for reel use.
    
    Returns dict: {tier: DIRECT|BLEND|SKIP, description: str, reason: str}
    """
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "max_tokens": 200,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": (
                        "You evaluate photos for use in news video reels (vertical, 9:16). "
                        "Judge the image on: (1) visual clarity and sharpness, "
                        "(2) whether it shows a real person, place, or event (not a logo/icon/illustration), "
                        "(3) topical connection to the headline — a photo of a KEY PERSON mentioned or implied in the headline counts as highly relevant (e.g. a CEO portrait for a company story, a politician for a policy story), "
                        "(4) visual interest (would it grab attention in a vertical video). "
                        "Return JSON: {\"tier\": \"DIRECT\"|\"BLEND\"|\"SKIP\", \"description\": \"<what the image shows in 10 words>\", \"reason\": \"<why this tier>\"}\n"
                        "DIRECT = sharp, real photo with clear subject that connects to the story — use as-is in a reel scene. Portraits of key figures ARE direct.\n"
                        "BLEND = decent real photo but not perfect (slightly low-res, busy composition, loosely connected) — can be enhanced/composited by AI.\n"
                        "SKIP = generic stock, logo, illustration, icon, completely unrelated, or too low quality to salvage."
                    )},
                    {"role": "user", "content": [
                        {"type": "text", "text": f"Headline: {article_headline}\nImage source: {img_source}\nEvaluate this image:"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}", "detail": "low"}}
                    ]}
                ]
            },
            timeout=30
        )
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            return json.loads(content)
    except Exception as e:
        print(f"  ⚠️ Vision eval failed: {e}")
    
    return {"tier": "SKIP", "description": "evaluation failed", "reason": "API error"}


def _extract_body_image_urls(body_markdown):
    """Extract image URLs from article body markdown."""
    if not body_markdown:
        return []
    # Match markdown images: ![alt](url)
    pattern = r'!\[[^\]]*\]\(([^)]+)\)'
    urls = re.findall(pattern, body_markdown)
    # Filter out non-image URLs
    return [u for u in urls if any(u.lower().endswith(ext) or ext in u.lower() 
            for ext in ['.jpg', '.jpeg', '.png', '.webp', 'image'])]


def evaluate_article_images(article, max_body_images=3):
    """Evaluate all images for an article. Returns list of scored image dicts.
    
    Each dict: {
        url: str,
        source: 'hero' | 'body',
        tier: 'DIRECT' | 'BLEND' | 'SKIP',
        width: int, height: int,
        description: str,
        reason: str,
        img_bytes: bytes (for DIRECT/BLEND only),
        img_b64: str (for DIRECT/BLEND only)
    }
    """
    headline = article.get("headline", "")
    results = []
    
    # 1. Evaluate hero image
    hero_url = article.get("image_url", "")
    if hero_url:
        print(f"  📸 Evaluating hero image...")
        dl = _download_image(hero_url)
        if dl:
            img_bytes, w, h = dl
            
            # Resolution gate
            if w < MIN_WIDTH_BLEND or h < MIN_HEIGHT_BLEND:
                print(f"    ❌ Too small ({w}×{h}), skipping")
                results.append({
                    "url": hero_url, "source": "hero", "tier": "SKIP",
                    "width": w, "height": h,
                    "description": "too small", "reason": f"Resolution {w}×{h} below minimum"
                })
            else:
                # Vision evaluation
                img_b64 = base64.b64encode(img_bytes).decode()
                eval_result = _vision_evaluate(img_b64, headline, "hero")
                
                # Override tier if resolution is too low for DIRECT
                tier = eval_result.get("tier", "SKIP")
                if tier == "DIRECT" and (w < MIN_WIDTH_DIRECT or h < MIN_HEIGHT_DIRECT):
                    tier = "BLEND"
                    eval_result["reason"] += f" (downgraded: {w}×{h} too small for DIRECT)"
                
                results.append({
                    "url": hero_url, "source": "hero", "tier": tier,
                    "width": w, "height": h,
                    "description": eval_result.get("description", ""),
                    "reason": eval_result.get("reason", ""),
                    "img_bytes": img_bytes,
                    "img_b64": img_b64
                })
                print(f"    {tier}: {eval_result.get('description', '')} ({w}×{h})")
        else:
            print(f"    ❌ Hero image download failed")
    
    # 2. Evaluate body images (up to max_body_images)
    body = article.get("body", "") or article.get("content", "")
    body_urls = _extract_body_image_urls(body)
    
    for i, url in enumerate(body_urls[:max_body_images]):
        print(f"  📸 Evaluating body image {i+1}/{min(len(body_urls), max_body_images)}...")
        dl = _download_image(url)
        if not dl:
            print(f"    ❌ Download failed")
            continue
        
        img_bytes, w, h = dl
        if w < MIN_WIDTH_BLEND or h < MIN_HEIGHT_BLEND:
            print(f"    ❌ Too small ({w}×{h}), skipping")
            continue
        
        img_b64 = base64.b64encode(img_bytes).decode()
        eval_result = _vision_evaluate(img_b64, headline, f"body image {i+1}")
        
        tier = eval_result.get("tier", "SKIP")
        if tier == "DIRECT" and (w < MIN_WIDTH_DIRECT or h < MIN_HEIGHT_DIRECT):
            tier = "BLEND"
        
        results.append({
            "url": url, "source": "body", "tier": tier,
            "width": w, "height": h,
            "description": eval_result.get("description", ""),
            "reason": eval_result.get("reason", ""),
            "img_bytes": img_bytes,
            "img_b64": img_b64
        })
        print(f"    {tier}: {eval_result.get('description', '')} ({w}×{h})")
    
    # Summary
    direct = [r for r in results if r["tier"] == "DIRECT"]
    blend = [r for r in results if r["tier"] == "BLEND"]
    skip = [r for r in results if r["tier"] == "SKIP"]
    print(f"  📊 Image evaluation: {len(direct)} DIRECT, {len(blend)} BLEND, {len(skip)} SKIP")
    
    return results


def get_usable_images(article, max_body_images=3):
    """Convenience: returns only DIRECT and BLEND images, sorted by quality."""
    all_imgs = evaluate_article_images(article, max_body_images)
    usable = [r for r in all_imgs if r["tier"] in ("DIRECT", "BLEND")]
    # DIRECT first, then BLEND; hero before body within each tier
    usable.sort(key=lambda x: (0 if x["tier"] == "DIRECT" else 1, 0 if x["source"] == "hero" else 1))
    return usable


if __name__ == "__main__":
    # Test with an article ID
    import subprocess
    
    # Load env
    for env_file in [".env.supabase", ".env.openai"]:
        env_path = os.path.expanduser(f"~/workspace/{env_file}")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip().strip('"').strip("'")
    
    # Re-read after env load
    globals()["SB_URL"] = os.environ.get("SUPABASE_URL", "")
    globals()["SB_KEY"] = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    globals()["SB_HEADERS"] = {"apikey": os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""), 
                                "Authorization": f"Bearer {os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')}"}
    globals()["OPENAI_KEY"] = os.environ.get("OPENAI_API_KEY", "")
    
    if len(sys.argv) > 1:
        article_id = sys.argv[1]
        # Fetch article
        r = requests.get(
            f"{os.environ['SUPABASE_URL']}/rest/v1/p2_articles?id=eq.{article_id}&select=headline,image_url,body",
            headers={"apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"],
                     "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}"},
            timeout=10
        )
        if r.status_code == 200 and r.json():
            article = r.json()[0]
            print(f"Article: {article['headline'][:60]}")
            print()
            results = evaluate_article_images(article)
            print(f"\nResults: {json.dumps([{k:v for k,v in r.items() if k not in ('img_bytes','img_b64')} for r in results], indent=2)}")
        else:
            print(f"Article not found: {article_id}")
    else:
        print("Usage: python3 image_evaluator.py <article_id>")
