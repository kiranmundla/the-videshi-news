#!/usr/bin/env python3
"""
Sports Writer — June 18, 2026 (16:30 UTC run)
Article: Sonia Raman — the first person of Indian origin to be a WNBA head
coach — is navigating a brutal debut season in Seattle (3-12). A lawyer-turned
-MIT-coach-turned-NBA-assistant whose unconventional path is its own story.

Distinct from recent sports coverage on the dashboard (cricket ODIs/WC, women's
T20 WC, India A tri-series, chess, junior tennis, golf, hockey, football,
athletics). This is WNBA / basketball / diaspora-representation — untouched.

Hero image: no Commons photo of Raman exists; use a current-season (2026)
Seattle Storm player photo from Wikimedia Commons (the team she coaches) with an
honest caption. No generic stock.
"""

import os, sys, json, io
from datetime import datetime, timezone

import requests
from PIL import Image

# ── ENV ──
env_supa = os.path.expanduser("~/.env.supabase")
for line in open(env_supa):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
UA = "TheVideshi/1.0 (thevideshi.com)"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(" ", "_")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    out = []
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers={"User-Agent": UA}, timeout=15,
        )
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for p in pages.values():
                ii = (p.get("imageinfo") or [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and mime.startswith("image/") and ii.get("width", 0) >= 800:
                    out.append({"url": url, "title": p.get("title", ""),
                                "w": ii.get("width"), "h": ii.get("height")})
    except Exception as e:
        print(f"  \u26a0 Commons error for '{search_query}': {e}")
    return out


def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    try:
        import subprocess
        tmp = f"/tmp/{filename}"
        subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, img_url], capture_output=True)
        if not (os.path.exists(tmp) and os.path.getsize(tmp) > 5000):
            print(f"  \u2717 Download failed for {img_url[:80]}")
            return None
        content = open(tmp, "rb").read()
        compressed = compress_image(content)
        print(f"  \U0001f4e6 Compressed to {len(compressed)/1024:.0f} KB")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=compressed, timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url}")
            return public_url
        else:
            print(f"  \u2717 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  \u2717 Upload error: {e}")
        return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  \u2713 Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


print("\n" + "="*60)
print("ARTICLE: Sonia Raman — first Indian-origin WNBA head coach")
print("="*60)

art_slug = "sonia-raman-first-indian-origin-wnba-head-coach-seattle-storm-debut-season-mit-grizzlies-2026-nri"
art_headline = "She Coached at MIT, Then the Grizzlies. Now Sonia Raman Is the First Indian-Origin Head Coach in the WNBA \u2014 and the Hardest Part Has Only Just Begun."
art_subheadline = "A walk-on guard who became a lawyer, then the winningest coach in MIT history, then the first Indian-American woman on an NBA bench, Raman took over the Seattle Storm this season. At 3-12, the rebuild is brutal \u2014 but the barrier she broke is permanent."

art_body = """SEATTLE \u2014 On a June night at the Moda Center in Portland, the Seattle Storm lost again, 94-89, a one-possession game that slipped away in a fourth quarter they could not control. It dropped their record to 3-12, among the worst in the WNBA, and deepened the most difficult stretch of a difficult first season. On the away bench, charting it all, was a 52-year-old former lawyer from Framingham, Massachusetts \u2014 a woman whose name most American sports fans are only now learning, and one that millions in the Indian diaspora have quietly adopted as their own.

Sonia Raman is the head coach of the Seattle Storm. She is also, since her hiring last October, the first person of Indian origin to be a head coach in the history of the Women's National Basketball Association. The losses are piling up. The milestone is not going anywhere.

## A Path That Made No Sense \u2014 Until It Did

Raman did not arrive in professional basketball by the usual route. She walked on to the Tufts University team as a guard in the early 1990s, had her playing career interrupted when she was struck by a car and broke her leg in her junior year, and finished as a team co-captain who had learned more from the sideline than the court. She graduated in 1996 with a degree in international relations, then did something almost no future NBA coach has done: she went to law school, earning a Juris Doctor from Boston College in 2001.

For a time she practiced law. But the game kept pulling her back. She took an assistant's job at Wellesley College, and in 2008 became head coach of the women's team at the Massachusetts Institute of Technology \u2014 not a basketball factory, but a place where she built something lasting. Over twelve seasons she became the winningest coach in program history, with more than 150 victories and back-to-back conference Coach of the Year honors in 2016 and 2017.

## From MIT to the NBA Bench

In 2020 the Memphis Grizzlies hired her as an assistant coach, making her the first Indian-American woman to hold such a role in the NBA. She spent four seasons in Memphis working on player development and analytics \u2014 the unglamorous, detail-obsessed craft that modern coaching is built on \u2014 before moving to the New York Liberty's staff in 2025. When the Storm parted ways with Noelle Quinn after a first-round playoff exit, they turned to Raman.

"Sonia is a trailblazer, an innovator and a leader in basketball analytics and strategy," Storm general manager Talisa Rhea said on announcing the hire. The team handed her a multi-year deal and a franchise with serious history: four WNBA championships, the most recent in 2020, and a city that takes its women's basketball seriously.

## The Rebuild Nobody Romanticizes

What Raman inherited, though, is a roster in transition. The Storm used a top-three pick on Spanish-Senegalese center Awa Fam and drafted Duke guard Taina Mair, betting on youth alongside veterans like Ezi Magbegor and Gabby Williams. The results have been painful: at 3-12, Seattle sits near the bottom of the Western Conference, and the patience of a championship-pedigree fan base will be tested all summer. Rebuilds are romantic only in retrospect. In the present, they are a string of close losses and hard postgame questions.

None of that erases what her appointment represents. For a generation of South Asian families in the United States \u2014 many of whom pushed their children toward medicine, engineering or law rather than the gym \u2014 Raman's career is a quiet rebuttal to the idea that sport is not a serious path. She did the safe thing, became a lawyer, and then chose the court anyway. That she now stands on an WNBA sideline, the first of her heritage to do so, is the kind of representation that does not depend on the scoreboard.

## Why It Matters Beyond the Standings

Raman's wife, Milena Flores, is herself a former Stanford and WNBA player with Seattle roots, and the couple's return to the Pacific Northwest has the feel of a homecoming. The wins will have to come later; first seasons of rebuilds rarely produce them. But the barrier she broke \u2014 like the one she broke in Memphis four years earlier \u2014 is the sort that stays broken. The next Indian-origin coach to reach a major American professional bench will not be the first. Sonia Raman already took care of that."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "A Seattle Storm player in action during the 2026 WNBA season, Sonia Raman's first as head coach"
img_attribution = "Wikimedia Commons"
img_final = None

# No Commons photo of Raman exists. Use a current-season (2026) Seattle Storm
# player photo (the team she coaches) — on-topic Commons imagery, not stock.
commons_queries = [
    "Sonia Raman",
    "Flaujae Johnson Storm",
    "Awa Fam Storm",
    "Seattle Storm 2026",
    "Seattle Storm basketball",
]
for q in commons_queries:
    cands = fetch_wikimedia_commons_images(q)
    for c in cands:
        low = c["title"].lower()
        print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
        # skip non-photos / off-topic documents / logos / maps
        if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                       "letters", "bandiera", "monitorul",
                                       "sandspur", "evening post", "nostra"]):
            continue
        # require a Storm/basketball-relevant photo
        if not any(g in low for g in ["storm", "raman", "wnba", "basketball", "arena"]):
            continue
        got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
        if got:
            img_final = got
            if "raman" in low:
                img_caption = "Seattle Storm head coach Sonia Raman, the first person of Indian origin to lead a WNBA team"
            elif "flaujae" in low:
                img_caption = "Seattle Storm guard Flau'jae Johnson during the 2026 WNBA season, Sonia Raman's first as head coach"
            elif "awa fam" in low or "fam" in low:
                img_caption = "Seattle Storm center Awa Fam, a 2026 draft pick, in Sonia Raman's first season as head coach"
            break
    if img_final:
        break

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "diaspora-sport",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Reuters \u2014 Storm officially tab Sonia Raman as head coach", "url": "https://www.reuters.com/sports/basketball/"},
        {"name": "Wikipedia \u2014 Sonia Raman", "url": "https://en.wikipedia.org/wiki/Sonia_Raman"},
        {"name": "Wikipedia \u2014 2026 Seattle Storm season", "url": "https://en.wikipedia.org/wiki/2026_Seattle_Storm_season"},
        {"name": "Wikipedia \u2014 Seattle Storm", "url": "https://en.wikipedia.org/wiki/Seattle_Storm"},
    ]),
    "diaspora_angle": "Sonia Raman is the first person of Indian origin to be a head coach in the WNBA \u2014 and earlier was the first Indian-American woman to coach in the NBA \u2014 a barrier-breaking career that offers South Asian families in America a powerful counter-example to the idea that professional sport is not a serious path.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "="*60)
print("DONE")
print("="*60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print(f"Image: {img_final or '(none)'}")
print("Set to status='review'")
