#!/usr/bin/env python3
"""
article-cards-hatch.py — Generate article cards using Hatch image generator.
Called from cron task body (agent context required for generate_media).

This script builds the prompt and metadata; the actual generation
happens via the agent's generate_media tool, so this is a helper
for the cron task logic, not a standalone runner.

Logo overlay is done programmatically with Pillow for consistent sizing.
"""

import os, sys, json, subprocess, hashlib
from pathlib import Path
from PIL import Image

PIPELINE_DIR = Path(__file__).resolve().parent
LOGO_PATH = PIPELINE_DIR / "assets" / "logo-transparent.png"

CATEGORY_THEMES = {
    "immigration": {"color": "deep crimson red", "label": "IMMIGRATION"},
    "technology": {"color": "electric blue", "label": "TECHNOLOGY"},
    "entertainment": {"color": "rich purple", "label": "ENTERTAINMENT"},
    "sports": {"color": "vibrant green", "label": "SPORTS"},
    "news": {"color": "bold red", "label": "NEWS"},
    "markets-finance": {"color": "warm amber/gold", "label": "MARKETS & FINANCE"},
    "nri-world": {"color": "teal/cyan", "label": "NRI WORLD"},
    "travel": {"color": "ocean teal", "label": "TRAVEL"},
    "lifestyle-health": {"color": "magenta pink", "label": "LIFESTYLE & HEALTH"},
    "food": {"color": "warm orange", "label": "FOOD"},
}


def build_card_prompt(article):
    """Build the generate_media prompt for an article card."""
    cat = article.get("category", "news")
    theme = CATEGORY_THEMES.get(cat, {"color": "navy blue", "label": cat.upper()})
    headline = article["headline"]
    body = (article.get("body") or "")[:2000]

    prompt = (
        f'A dramatic, data-rich news card for "The Videshi" Indian diaspora news outlet. '
        f'Dark cinematic background using the provided photo. '
        f'The second provided image is the outlet\'s logo — place it VERY SMALL in the '
        f'top left corner, about the size of a favicon/app icon, subtle and unobtrusive. '
        f'Bold headline: "{headline}". '
        f'Category "{theme["label"]}" in {theme["color"]}. '
        f'Extract the MOST IMPACTFUL stat or number from this article content and make it '
        f'HUGE and bold (like "$42 BILLION" or "6-3 RULING" or "+26.5%"): {body[:800]} '
        f'Small "THEVIDESHI.COM" branding in gold at bottom. '
        f'CNN/Bloomberg breaking news infographic style. '
        f'Rich, dramatic, information-dense portrait card.'
    )
    return prompt


def overlay_logo(card_path, output_path, logo_size=48, margin=20):
    """Overlay the Videshi logo on the top-left of the card at a fixed small size."""
    if not LOGO_PATH.exists():
        # No logo file, just copy
        import shutil
        shutil.copy2(card_path, output_path)
        return output_path

    card = Image.open(card_path).convert("RGBA")
    logo = Image.open(str(LOGO_PATH)).convert("RGBA")
    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

    # Paste logo with alpha composite
    card.paste(logo, (margin, margin), logo)
    card.convert("RGB").save(output_path, quality=90)
    return output_path


def download_hero(url, timeout=15):
    """Download hero image for use as source."""
    tmp = f"/tmp/card_hero_{hashlib.md5(url.encode()).hexdigest()[:12]}.jpg"
    r = subprocess.run(
        ["curl", "-sS", "-L", "-o", tmp, "--max-time", str(timeout),
         "-A", "TheVideshi/1.0", url],
        capture_output=True, timeout=timeout+5
    )
    if r.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 1000:
        return tmp
    return None


if __name__ == "__main__":
    # Test: print prompt for latest article
    from dotenv import load_dotenv
    load_dotenv(os.path.expanduser("~/workspace/.env.supabase"))

    url = f"{os.environ['SUPABASE_URL']}/rest/v1/p2_articles?status=eq.published&image_url=not.is.null&order=published_at.desc&limit=1&select=slug,headline,image_url,category,body"
    r = subprocess.run(
        ["curl", "-sS", url,
         "-H", f"apikey: {os.environ['SUPABASE_SERVICE_ROLE_KEY']}",
         "-H", f"Authorization: Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}"],
        capture_output=True, timeout=15
    )
    articles = json.loads(r.stdout)
    if articles:
        print(build_card_prompt(articles[0]))
