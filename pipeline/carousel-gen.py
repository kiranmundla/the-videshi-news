#!/usr/bin/env python3
"""
Instagram Carousel Generator for The Videshi.

Takes an article and generates a set of clean, swipeable infographic slides
(1080×1350 portrait) for manual Instagram carousel posting.

Usage:
    python3 carousel-gen.py <article_id>
    python3 carousel-gen.py <article_id> --slides 8
    python3 carousel-gen.py <article_id> --output-dir /tmp/carousel

Output: numbered PNG slides in the output directory, ready to post.
"""
import argparse
import base64
import json
import os
import sys
import time
import requests

# ── Load env ──
def _load_env(path):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("\"'"))

_load_env(os.path.expanduser("~/workspace/.env.supabase"))
_load_env(os.path.expanduser("~/workspace/.env.openai"))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

RESP_URL = "https://api.openai.com/v1/responses"
RESP_HEADERS = {
    "Authorization": f"Bearer {OPENAI_KEY}",
    "Content-Type": "application/json",
}

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ── Fetch article ──
def fetch_article(article_id):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}&select=*"
    r = requests.get(url, headers=SB_HEADERS, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        print(f"❌ Article not found: {article_id}")
        sys.exit(1)
    return rows[0]


# ── Plan carousel slides ──
def plan_carousel(article, num_slides):
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    body = article.get("body", "")[:4000]
    category = article.get("category", "news")

    prompt = f"""You are designing an Instagram CAROUSEL (swipeable image slides) for The Videshi — news for the Indian diaspora.

ARTICLE:
Headline: {headline}
Subheadline: {subheadline}
Category: {category}
Body: {body}

Create exactly {num_slides} carousel slides. Each slide is a SINGLE, clean infographic card.

SLIDE RULES:
1. Slide 1 = HOOK. The "stop scrolling" slide. Bold headline, one dramatic number or claim.
   Should make the viewer NEED to swipe. Use the article's most dramatic fact.
2. Slides 2-{num_slides - 1} = STORY BEATS. Each slide covers ONE key point from the article.
   - ONE big number or fact per slide
   - A short headline (4-8 words) and a one-line context sentence (10-20 words)
   - Think: Bloomberg TV data callout, not a magazine infographic
   - Include specific numbers, names, dates from the article
   - Build a narrative arc — each slide should make you want to see the next
3. Slide {num_slides} = CLOSER. Wrap up with the forward-looking takeaway or "what's next" angle.
   Include "Full story at TheVideshi.com" as a subtle footer.

VISUAL STYLE:
- Clean, modern, bold. Lots of negative space.
- Dark navy (#0B1D3A) or deep charcoal backgrounds with white/gold text
- ONE visual idea per slide — a number, a chart, a simple icon
- NO human faces or portraits
- NO busy infographic posters with 10 data points
- NO stock photo backgrounds
- Minimal — if you can remove something and the slide still works, remove it
- Professional news graphics aesthetic (Bloomberg, Reuters, The Economist)
- Consistent style across all slides — they should feel like a unified set

Return JSON only:
{{"slides": [
  {{"slide": 1, "headline": "hook headline", "body_text": "supporting context line", "visual_description": "detailed description of what to generate (150-250 chars, including text placement and data viz if any)"}},
  {{"slide": 2, "headline": "...", "body_text": "...", "visual_description": "..."}},
  ...
]}}"""

    print(f"📝 Planning {num_slides} carousel slides...", flush=True)
    r = requests.post(RESP_URL, headers=RESP_HEADERS, json={
        "model": "gpt-4o",
        "input": prompt,
    }, timeout=120)
    r.raise_for_status()
    resp = r.json()

    # Extract text output
    text = ""
    for item in resp.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    text = c["text"]

    # Parse JSON
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]

    plan = json.loads(text)
    prev_id = resp.get("id")
    return plan, prev_id


# ── Generate each slide image ──
def generate_slides(plan, prev_id, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    slides = plan.get("slides", [])
    generated = []

    for i, slide in enumerate(slides):
        num = slide.get("slide", i + 1)
        desc = slide.get("visual_description", "")
        headline = slide.get("headline", "")
        body_text = slide.get("body_text", "")

        print(f"\n🖼️  Generating slide {num}/{len(slides)}: {headline}", flush=True)

        gen_prompt = (
            f"Generate slide {num} for the Instagram carousel. "
            f"Headline on slide: \"{headline}\". "
            f"Supporting text: \"{body_text}\". "
            f"Visual direction: {desc}. "
            f"STYLE: Clean, modern news infographic on dark navy (#0B1D3A) background. "
            f"White and gold (#C9A84C) text. ONE key visual idea. Lots of breathing room. "
            f"1080×1350 portrait format. NO human faces. NO busy layouts. "
            f"Text must be large, bold, and fully readable — never cut off at edges. "
            f"Keep 80px safe margins on all sides."
        )

        try:
            r = requests.post(RESP_URL, headers=RESP_HEADERS, json={
                "model": "gpt-4o",
                "input": gen_prompt,
                "previous_response_id": prev_id,
                "tools": [{"type": "image_generation", "size": "1024x1536",
                            "quality": "high"}],
                "tool_choice": {"type": "image_generation"},
            }, timeout=300)
            r.raise_for_status()
            resp = r.json()
            prev_id = resp.get("id", prev_id)

            # Extract image
            img_b64 = None
            for item in resp.get("output", []):
                if item.get("type") == "message":
                    for c in item.get("content", []):
                        if c.get("type") == "image" and c.get("image_base64"):
                            img_b64 = c["image_base64"]

            if not img_b64:
                print(f"  ⚠️ No image returned for slide {num}", flush=True)
                continue

            # Save
            out_path = os.path.join(output_dir, f"slide-{num:02d}.png")
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(img_b64))

            fsize = os.path.getsize(out_path) / 1024
            print(f"  ✅ Saved: {out_path} ({fsize:.0f} KB)", flush=True)
            generated.append(out_path)

        except Exception as e:
            print(f"  ❌ Failed slide {num}: {e}", flush=True)

    return generated


def main():
    parser = argparse.ArgumentParser(description="Generate Instagram carousel slides")
    parser.add_argument("article_id", help="Article UUID")
    parser.add_argument("--slides", type=int, default=7, help="Number of slides (default: 7)")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    args = parser.parse_args()

    if not OPENAI_KEY:
        print("❌ OPENAI_API_KEY not set"); sys.exit(1)
    if not SUPABASE_URL:
        print("❌ SUPABASE_URL not set"); sys.exit(1)

    # Fetch article
    article = fetch_article(args.article_id)
    headline = article.get("headline", "untitled")
    slug = article.get("slug", article.get("id", "carousel"))
    print(f"📰 Article: {headline}")

    # Output dir
    out_dir = args.output_dir or f"/tmp/carousel-{slug[:60]}"

    # Plan
    plan, prev_id = plan_carousel(article, args.slides)
    slides = plan.get("slides", [])
    print(f"📋 Planned {len(slides)} slides")
    for s in slides:
        print(f"   Slide {s.get('slide')}: {s.get('headline')}")

    # Generate
    t0 = time.time()
    generated = generate_slides(plan, prev_id, out_dir)
    elapsed = time.time() - t0

    print(f"\n{'='*50}")
    print(f"✅ Generated {len(generated)}/{len(slides)} slides in {elapsed:.0f}s")
    print(f"📁 Output: {out_dir}/")
    for p in generated:
        print(f"   {os.path.basename(p)}")


if __name__ == "__main__":
    main()
