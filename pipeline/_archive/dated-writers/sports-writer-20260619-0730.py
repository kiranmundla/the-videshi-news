#!/usr/bin/env python3
"""
Sports Writer — June 19, 2026 (07:30 UTC run)
Article: India men's hockey beat world champions Germany 3-1 in Rotterdam
(Wed June 17), ending a NINE-match winless run in the FIH Pro League 2025-26.
Mandeep Singh (7'), Shilanand Lakra (13') and Nilakanta Sharma (35') scored;
Hardik Singh Player of the Match; Manpreet Singh broke Dilip Tirkey's 412-cap
record to become India's most-capped player (413). Germany took the reverse
fixture 2-1 the next day.

ANGLE: This is the REDEMPTION follow-up to the June 17 Videshi article
"Nine Games, Zero Wins: India's Hockey Team Is Having Its Worst Pro League
Ever — at the Worst Possible Time." That winless streak is now broken, and
broken against the WORLD CHAMPIONS, on the eve of an Olympic-cycle that runs
through the World Cup and Asian Games. Manpreet's record adds a generational,
legacy hook. Diaspora angle: hockey is India's most decorated Olympic sport
(8 golds), Manpreet led the Tokyo bronze that ended a 41-year medal drought,
and for the diaspora this is the sport that carries the deepest national
memory.

Hero: Manpreet Singh has a Wikipedia portrait (most-capped milestone makes
him the natural face). Fall back to Hardik Singh, then on-topic Commons.
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
print("ARTICLE: India break winless run — beat world champs Germany 3-1")
print("="*60)

art_slug = "india-men-hockey-beat-world-champions-germany-3-1-fih-pro-league-2025-26-rotterdam-end-nine-match-winless-run-manpreet-singh-most-capped-nri"
art_headline = "Nine Games, Zero Wins — Then They Beat the World Champions. India's Hockey Team Just Ended Its Misery in Rotterdam."
art_subheadline = "Two days after their worst Pro League campaign hit rock bottom, India dismantled reigning world champions Germany 3-1 \u2014 on the same night Manpreet Singh became the most-capped player in Indian hockey history."

art_body = """ROTTERDAM \u2014 For four months, the most decorated team in India's Olympic history had been losing in a way that felt almost unfamiliar. Nine matches into the FIH Pro League 2025-26, the men in blue had not won once: four home defeats in Bhubaneswar in February, three draws and a shootout in Hobart, and a narrow 2-3 loss to the Netherlands to open the European leg. It was, by some distance, the worst Pro League campaign India had ever run.

On Wednesday, in the Dutch port city of Rotterdam, it ended \u2014 and it ended against the best team on the planet. India beat reigning world champions Germany 3-1, a controlled, front-running performance that snapped the nine-match winless streak and reminded everyone watching that this team, for all its recent struggles, can still beat anybody.

## A First Half That Settled It

India did not wait. Mandeep Singh opened the scoring in the 7th minute with a sharp turn in front of goal, and before the first quarter was out Shilanand Lakra had beaten German goalkeeper Alexander Stadler with a fine strike to make it 2-0 in the 13th. Germany \u2014 World No. 5, and holders of the world title \u2014 changed their press and pushed hard through the second quarter, winning penalty corners in the 24th and 27th minutes. India's defence held: Amit Rohidas blocked the first dragflick, goalkeeper Mohith saved the second, and the 2-0 lead survived to halftime.

The decisive blow came in the 35th minute, when Nilakanta Sharma carried the ball through the German defenders on a brilliant solo run and slotted home for 3-0. Germany pulled one back through Raphael Hartkopf with 20 seconds left in the third quarter, and threw everything forward in the last 90 seconds, earning a penalty corner in the 59th minute. The Indian backline stood firm. Midfielder Hardik Singh, who shepherded play from the centre all evening, was named Player of the Match.

## Manpreet Singh Walks Into History

The win carried a milestone that will outlast the scoreline. In earning his cap that night, Manpreet Singh \u2014 the 33-year-old midfielder who captained India to its Tokyo 2020 Olympic bronze, the medal that ended a 41-year drought \u2014 broke Dilip Tirkey's record of 412 international appearances to become the most-capped player in the history of Indian men's hockey. With 413 caps, Manpreet now sits fifth on the all-time global list, behind only Belgium's John-John Dohmen, the Netherlands' Teun de Nooijer, Australia's Eddie Ockenden, and Great Britain's Barry Middleton.

For a player whose career has spanned India's climb from also-rans to an Olympic medal-winning side, the record landed on a fitting night: a statement win against the world champions, secured by the kind of defensive discipline that has defined his era in the team.

## Why It Matters Now

Coach Craig Fulton's side remains eighth in the standings, with seven points from ten games, and there is no pretending one result erases a difficult season. Germany, in fact, answered the very next day, taking the reverse fixture 2-1 in the final quarter to share the spoils of the Rotterdam double-header. But the difference between a winless campaign and a campaign with a marquee scalp is enormous, both for confidence and for momentum heading into a loaded Olympic cycle \u2014 a World Cup and the Asian Games loom, and the road to the 2028 Los Angeles Games has already begun.

India's hockey men have spent this season being defined by their failures. For one night in Rotterdam, they were defined by a win over the best team in the world.

## Why the Diaspora Is Watching

Hockey is not just another sport in the Indian sporting imagination \u2014 it is the one that carries the deepest national memory. India won eight Olympic gold medals in field hockey, more than any nation, in an era when the game was the country's pride. For the diaspora, that history is inherited: the grandparents who watched Dhyan Chand's successors dominate, the long medal drought that followed, and the catharsis of the Tokyo bronze that Manpreet Singh led. A win over the reigning world champions, on a European pitch, by a captain-class generation that refused to let a bad season define it, is the kind of result that travels \u2014 a reminder to Indians in New Jersey, London, and Sydney that their oldest sporting love is still capable of moments like this."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Manpreet Singh, who became the most-capped player in Indian hockey history during India's 3-1 win over Germany"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Manpreet Singh (most-capped milestone) then Hardik Singh (POTM)
for person, cap in [
    ("Manpreet Singh (field hockey)", "Manpreet Singh, who became the most-capped player in Indian hockey history during India's 3-1 win over Germany"),
    ("Hardik Singh", "Hardik Singh, named Player of the Match in India's 3-1 FIH Pro League win over world champions Germany"),
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
    for q in ["Manpreet Singh field hockey", "India men hockey team", "Indian field hockey", "field hockey India"]:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            if not any(g in low for g in ["manpreet", "hockey", "india"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                img_caption = "Indian men's field hockey, India's most decorated Olympic sport"
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
        {"name": "Khel Now \u2014 Men's FIH Pro League 2025-26: India defeat world champions Germany for maiden win", "url": "https://www.khelnow.com/hockey/2026-06-fih-pro-league-india-germany-result"},
        {"name": "RevSportz \u2014 India produce strong defensive display in their 3-1 win over World Champions Germany", "url": "https://revsportz.in/"},
        {"name": "IANS Live \u2014 India beat world champions Germany 3-1 in FIH Pro League", "url": "https://ianslive.in/"},
        {"name": "Yardbarker \u2014 India Beat World Champions Germany 3-1 In FIH Pro League", "url": "https://www.yardbarker.com/"},
    ]),
    "diaspora_angle": "Hockey is India's most decorated Olympic sport \u2014 eight golds and the deepest national sporting memory \u2014 and this win over the reigning world champions, on the night captain-class veteran Manpreet Singh became India's most-capped player ever, is the kind of redemption story that resonates with NRIs who inherited that history from grandparents who watched India dominate the game.",
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
