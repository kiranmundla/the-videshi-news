#!/usr/bin/env python3
"""
Sports Writer — June 20, 2026 (04:30 UTC slot)
Article: India have handed a maiden T20I call-up to 15-year-old Vaibhav
Sooryavanshi for the white-ball leg of the UK tour (two T20Is in Ireland from
June 26, then five against England). Shreyas Iyer named T20I captain, replacing
World Cup-winning skipper Suryakumar Yadav; Tilak Varma his deputy. BCCI is
sending the teenager's parents on tour to ease his transition into a senior
dressing room.

ANGLE: A 15-year-old being picked for India's senior side is a once-in-a-
generation story — the youngest path into international cricket, the IPL record
breaker, and a deliberate, caretaking BCCI. Diaspora angle: British-Indian fans
in Belfast/England get to witness the debut of the most-hyped teenager in world
cricket in person. Recent sports coverage was the men's Test preview (Gill),
women's T20 WC, Neeraj, hockey, MLC — nothing on the white-ball squad/
Sooryavanshi. Fresh.

Hero: Wikipedia portrait of Vaibhav Sooryavanshi (upload.wikimedia.org),
then Commons.
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


def fetch_wikimedia_commons_images(search_query, limit=8):
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
print("ARTICLE: India women thrash Chile 6-0, into Nations Cup final")
print("="*60)

art_slug = "india-women-hockey-beat-chile-6-0-fih-nations-cup-2026-final-auckland-pro-league-promotion-salima-tete-navneet-deepika-nri"
art_headline = "Six Goals, Zero Conceded: India's Women Storm Into the Nations Cup Final \u2014 and to the Brink of the Pro League"
art_subheadline = "A 6-0 demolition of Chile in Auckland puts the Indian women's hockey team one win from the trophy and, more importantly, from a return to the elite FIH Pro League they were relegated from last year."

art_body = """When India's women walked off the turf in Auckland on Saturday, the scoreline read 6-0, but the number that actually mattered was the one still to come. A semi-final this emphatic was never really about Chile. It was about the door to the FIH Pro League swinging back open \u2014 and India kicking it down.

The Indian women's hockey team produced its most complete performance of the FIH Hockey Women's Nations Cup 2025-26, routing Chile 6-0 to march into Sunday's final. It was a result built on relentless attacking intent and a defence that, for the fourth time in five matches, simply refused to be breached.

## A Blitz Inside the First Quarter

Chile barely had time to settle. Navneet Kaur opened the scoring in the sixth minute from a penalty corner and added a field goal in the 13th, and by the time the first quarter closed India were already three up, drag-flicker Deepika having converted in the 14th. Deepika struck again from another penalty corner in the 18th minute to make it 4-0, turning a contest into a procession.

Neha extended the lead with a penalty-corner goal in the 32nd minute, and Rutuja Pisal completed the rout with a field goal in the 39th. Six different moments, four of them from set pieces, underlining how dangerous this Indian side has become whenever it wins a penalty corner. The shut-out also handed the defence and goalkeeper a near-untroubled evening before the biggest game of the week.

## The Run That Got Them Here

The semi-final was no aberration. India topped Pool A with a perfect record, beating the United States 3-2, Japan, and Uruguay 3-2 in a run that mixed flair with the kind of nerve that had deserted them in tighter tournaments. The Uruguay win doubled as a personal milestone for midfielder Neha, who brought up her 200th senior international appearance.

Through it all, Deepika has been the tournament's defining figure with the drag-flick, and captain Salima Tete has marshalled a young group that looks increasingly comfortable on the big stage. India arrived in New Zealand ranked ninth in the world; they will leave it having looked a clear cut above most of the field.

## Why the Final Is About More Than a Trophy

The stakes on Sunday stretch well beyond silverware. The winner of the FIH Hockey Women's Nations Cup earns promotion to the 2026-27 FIH Pro League \u2014 hockey's top-tier annual competition, where India would face the world's best sides home and away across a full season. That regular diet of elite matches is precisely what a developing team needs, and precisely what India lost when they were relegated from the Pro League last year.

For a side rebuilding after the disappointment of missing out on the Paris Olympics, getting back among the elite is the whole point of this trip. A title would be welcome; the Pro League place is essential to the long-term project of turning India back into a podium contender by the time the Los Angeles Olympics come around in 2028.

India will meet the winner of the other semi-final between hosts New Zealand and the United States in Sunday's final in Auckland. Whoever emerges, India will start as one of the form teams of the tournament \u2014 and with the memory of a 6-0 statement still fresh.

## Why the Diaspora Will Be Watching

For Indian sports fans in the United States, the United Kingdom and Australia, the women's hockey team has quietly become one of the most compelling watches in the calendar \u2014 a young, attacking side playing without fear in time zones that, for once, suit the Western diaspora better than the cricket. Several of these matches have been streamed free on Watch.Hockey, making it easy for NRI families to follow along.

There is a deeper resonance, too. The earlier 3-2 win over the USA was a reminder that American field hockey is itself increasingly powered by talent the diaspora recognises, and India's bid to climb back into the Pro League is a story of a women's programme refusing to slide. Sunday's final is a chance for that programme to announce, on a global stage and at a friendly hour, that it is back among the best."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "India women's hockey captain Salima Tete, who led the side to the Nations Cup final"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Subject athlete / captain (Wikipedia portrait)
for person, cap in [
    ("Salima Tete", "India women's hockey captain Salima Tete, who led the side to the Nations Cup final"),
    ("Navneet Kaur (field hockey)", "India forward Navneet Kaur, who scored twice in the 6-0 semi-final win over Chile"),
]:
    wiki_img = fetch_wikipedia_person_image(person)
    if wiki_img:
        got = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
        if got:
            img_final = got
            img_caption = cap
            break

# 2) Fallback: on-topic Commons imagery
if not img_final:
    for q in ["Indian women's hockey team", "India women field hockey", "India women hockey team"]:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            if not any(g in low for g in ["india", "hockey"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                img_caption = "The Indian women's hockey team"
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
    "vertical": "hockey",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Wikipedia \u2014 2025\u201326 Women's FIH Hockey Nations Cup", "url": "https://en.wikipedia.org/wiki/2025%E2%80%9326_Women%27s_FIH_Hockey_Nations_Cup"},
        {"name": "RevSportz \u2014 India top Pool A unbeaten at FIH Hockey Women's Nations Cup", "url": "https://revsportz.in/"},
        {"name": "The Bridge \u2014 India beat Uruguay 3-2 to finish unbeaten in Nations Cup pool stage", "url": "https://thebridge.in/"},
        {"name": "USA Field Hockey \u2014 2026 FIH Hockey Nations Cup Auckland Squad", "url": "https://www.usafieldhockey.com/"},
    ]),
    "diaspora_angle": "Played in a New Zealand time zone that suits NRI viewers and streamed free online, India's women are one win from a return to hockey's elite Pro League \u2014 a milestone the diaspora can watch live as the programme rebuilds toward the 2028 LA Olympics.",
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
