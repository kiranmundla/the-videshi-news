"""Keepers for the product-gallery rung (2026-11-15).

The Gemini eyewear case: the article's own primary source
(blog.google announcement) carried a dozen official product
images; the article shipped with a publisher hotlink and no
gallery. Extraction must collapse srcset size variants, skip
logos, take the maker's alt text as caption ground truth
(minus layout boilerplate), and the trigger/hero rules must
stay conservative.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def load(name):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PG = load("product_gallery")

total = fails = 0


def check(label, cond):
    global total, fails
    total += 1
    if cond:
        print(f"  ok {total}: {label}")
    else:
        fails += 1
        print(f"  FAIL {total}: {label}")


B = "https://storage.googleapis.com/gweb-uniblog-publish-prod/images"
HTML = f"""
<html><head>
<meta property="og:image" content="{B}/Blog1_Banner.width-1300.png" />
</head><body>
<img src="{B}/google-logo.png" alt="Google logo" />
<img src="{B}/WP_Alden.width-500.format-webp.webp"
     srcset="{B}/WP_Alden.width-500.format-webp.webp 500w,
             {B}/WP_Alden.width-2000.format-webp.webp 2000w"
     alt="Dark green glasses with clear lenses floating on a grey background. Along the top are Warby Parker, Google, and Samsung logos." />
<img src="{B}/WP_Alden.width-800.format-webp.webp" alt="dupe variant" />
<img srcset="{B}/GM_GGS001.width-1600.format-webp.webp 1600w"
     alt="" />
</body></html>"""

cands = PG.extract_candidates(HTML, "https://blog.google/x/post/")
urls = [c["url"] for c in cands]
check("og:image extracted first", urls[0].endswith("Blog1_Banner.width-1300.png"))
check("logo skipped", not any("logo" in u for u in urls))
check("srcset largest variant chosen", any("WP_Alden.width-2000" in u for u in urls))
check("size variants deduped by stem", len([u for u in urls if "WP_Alden" in u]) == 1)
check("srcset-only img extracted", any("GM_GGS001" in u for u in urls))

cap = PG.caption_for(
    "Dark green glasses with clear lenses floating on a grey "
    "background. Along the top are Warby Parker, Google, and "
    "Samsung logos.", "Google")
check("caption cuts layout boilerplate + credits",
      cap == "Dark green glasses with clear lenses floating on "
             "a grey background. Official Google product image.")
check("empty alt → honest generic",
      PG.caption_for("", "Apple") == "Official Apple product image.")

art = {"category": "technology", "is_visual_story": False,
       "gallery_images": None,
       "sources": [{"label": "Google Blog",
                    "url": "https://blog.google/x/post/"},
                   {"label": "Android Police",
                    "url": "https://www.androidpolice.com/y/"}]}
src = PG.official_source(art)
check("official source found in article sources",
      src is not None and src[1] == "Google")
check("qualifies: technology + official + no gallery",
      PG.qualifies(art))
check("no qualify when gallery already present",
      not PG.qualifies({**art, "gallery_images": [{"url": "x"}]}))
check("no qualify for plain news story",
      not PG.qualifies({**art, "category": "news"}))
check("visual story qualifies outside technology",
      PG.qualifies({**art, "category": "entertainment",
                    "is_visual_story": True}))
check("news-only sources → no official source",
      PG.official_source({"sources": [
          {"url": "https://www.androidpolice.com/y/"}]}) is None)

check("hero replaceable: third-party hotlink",
      PG._hero_is_replaceable(
          {"image_url": "https://static0.anpoimages.com/x.jpg"}))
check("hero NOT replaceable: our storage",
      not PG._hero_is_replaceable(
          {"image_url": "https://lboecaekpynbpyijrbfz.supabase.co/x.jpg"}))
check("hero NOT replaceable: wikimedia",
      not PG._hero_is_replaceable(
          {"image_url": "https://upload.wikimedia.org/x.jpg"}))
check("hero replaceable: missing",
      PG._hero_is_replaceable({"image_url": None}))

# ── Hybrid placement (Kiran's call, 2026-11-15): section-
# matching shots inline, the rest in one in-body strip.
BODY = ('<div class="key-takeaways">x</div><p>Intro about the '
        'launch.</p><h2>What the glasses do</h2><p>Voice help '
        'and a camera.</p><h2>Hardware, price and availability'
        '</h2><p>Warby Parker styles start at $395. Warby '
        'Parker offers three frames.</p><p>Gentle Monster '
        'styles start at $449.</p><h2>Compatibility</h2>'
        '<p>Pixel and Galaxy phones.</p>')
pool = [
    ("https://x/wp.jpg", "Warby Parker lifestyle.",
     PG._match_tokens("Models wearing Warby Parker frames",
                      "wp_carousel_lifestyle")),
    ("https://x/gm.jpg", "Gentle Monster studio.",
     PG._match_tokens("Black sunglasses floating",
                      "gm_ggs001")),
    ("https://x/range.jpg", "The full range.",
     PG._match_tokens("Two women wearing wide black sunglasses",
                      "gm_lifestyle")),
]
new_body = PG.place_in_body(BODY, pool, "Official Google product images.")
check("hybrid: body produced", bool(new_body))
wp_at = new_body.find("https://x/wp.jpg")
hw_at = new_body.find("Hardware, price")
gm_at = new_body.find("Gentle Monster styles start")
check("hybrid: section-matched shot inline in its section",
      hw_at != -1 and wp_at > hw_at)
check("hybrid: strip block present for the rest",
      "<!-- photo-strip" in new_body)
import json as _json
blk = new_body.split("<!-- photo-strip")[1].split("-->")[0]
data = _json.loads(blk)
check("hybrid: strip JSON parses with images + credit",
      len(data["images"]) >= 1
      and data["credit"] == "Official Google product images.")
check("hybrid: no top-gallery semantics (no gallery_images)",
      "gallery_images" not in new_body)

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
