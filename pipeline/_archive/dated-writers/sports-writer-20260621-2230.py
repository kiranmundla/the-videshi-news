#!/usr/bin/env python3
"""
Sports Writer — June 21, 2026 (22:30 UTC slot)

Article: The European T20 Premier League (ETPL) — Europe's first ICC-sanctioned
franchise T20 league — opened Player Draft Registration on June 18-19, 2026.
Six city franchises: Glasgow, Edinburgh (Scotland), Dublin, Belfast (Ireland),
Amsterdam, Rotterdam (Netherlands). Backed jointly by Cricket Ireland, Cricket
Scotland and the KNCB (Royal Dutch Cricket Association) — an unprecedented
three-nation collaboration. 32 matches, Aug 26 - Sep 20, 2026. Each franchise
fields eight home players plus a European development player. Registration open
to men affiliated with the three boards via etplofficial.com.

DEDUP: Checked last 3 days of sports. Covered already: Glasgow CWG contingent,
women's hockey Nations Cup, women's T20 WC v SA, post-Kohli ODIs/Test day one,
MLC, FIFA WC recaps, Neeraj Doha, Kohli England recall, Sooryavanshi, Anahat
Singh, Esha Singh, Sonia Raman. The ETPL launch / draft-registration story is
FRESH and uncovered, with a strong UK/Ireland/Netherlands diaspora hook.

Hero: Commons cricket imagery (Ireland/associate cricket, stadium). No single
named protagonist, so an on-topic event/ground photo is correct.
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
print("ARTICLE: Europe's first ICC franchise T20 league opens draft")
print("="*60)

art_slug = "european-t20-premier-league-etpl-icc-sanctioned-draft-registration-2026-glasgow-edinburgh-dublin-belfast-amsterdam-rotterdam-ireland-scotland-netherlands-diaspora-nri"
art_headline = "Europe Just Launched Its First Big-League T20 — and the Diaspora Built Half the Talent Pool"
art_subheadline = "The ICC-sanctioned European T20 Premier League opened its player draft this week, with six city franchises across Ireland, Scotland and the Netherlands — cricketing nations whose teams the South Asian diaspora has quietly powered for years."

art_body = """Europe is finally getting a franchise T20 league worthy of the name. The European T20 Premier League (ETPL) — billed as the continent's first ICC-sanctioned franchise tournament — opened Player Draft Registration this week, the first concrete step toward an inaugural season that will run from August 26 to September 20. Six city-based teams will represent Glasgow, Edinburgh, Dublin, Belfast, Amsterdam and Rotterdam across a 32-match season, and registration is now open to cricketers affiliated with Cricket Ireland, Cricket Scotland or the Royal Dutch Cricket Association through the league's official website, etplofficial.com.

What makes the ETPL unusual is not the format — draft, franchises, overseas stars, the familiar furniture of every T20 league since the IPL — but its ownership. This is not the project of a single national board chasing a quick payday. It is a joint venture of three boards at once: Ireland, Scotland and the Netherlands, each fielding two teams, pooling their resources to build something none could sustain alone.

## A League Three Countries Built Together

"Unlike other leagues typically supported by a single national board, the ETPL boasts the unified backing of Cricket Ireland, Cricket Scotland, and Cricket Netherlands, demonstrating an unprecedented level of collaboration," the organisers said. It is the first competition of its kind to be built across three nations rather than within one, and that cooperative model is the point. For associate cricket — the rung below the Test-playing elite — money and meaningful match exposure have always been the twin bottlenecks. A shared league spreads the cost and triples the talent base.

Each franchise will field eight home players alongside a development player drawn from a European country, a deliberate design choice meant to keep the league a pipeline for local talent rather than a retirement home for fading internationals. The draft, once registration closes, will let franchises assemble local rosters before adding the marquee overseas names that draw crowds and broadcasters. The league is promising its participants international broadcast coverage, professional franchise environments and, crucially, regular high-pressure cricket against quality opposition — the kind associate players almost never get between World Cups.

## Why the Diaspora Should Care

Here is the part that lands close to home for Indians settled across Britain, Ireland and the Low Countries: the national teams the ETPL is built to strengthen have, for years, been substantially powered by the South Asian diaspora. Ireland's recent sides have featured players of Indian and Pakistani heritage; the Netherlands has long leaned on cricketers with roots in the subcontinent and the Caribbean-Indian community; Scotland's set-up is dotted with names that trace back to Punjab and beyond. These are teams that exist, in large part, because immigrant families kept playing the game in cities where it was a minority pursuit.

A professional, well-broadcast home league changes the calculus for those communities. It gives a young British-Indian or Dutch-Indian cricketer a visible, local route to a paid playing career without having to uproot to county cricket or gamble on an IPL contract that will never come. It gives diaspora families in Glasgow, Dublin and Amsterdam — cities with sizeable and growing South Asian populations — a top-tier team to actually go and watch, in their own time zone, in grounds they can reach on a weekend. And it gives the wider game a new audience precisely where the diaspora is densest.

## The Bigger Picture

The ETPL also slots into a crowded and fast-growing landscape of European franchise cricket, alongside ventures like the EUT20 in Belgium, as the sport pushes hard to establish itself beyond its traditional strongholds. Cricket's return to the Olympic programme at Los Angeles 2028 has sharpened every associate board's incentive to develop depth, and a sustained domestic league is the surest way to build it.

For a community that has spent decades being the quiet engine of associate cricket in Europe — coaching juniors in church-hall nets, ferrying kids to weekend fixtures, keeping clubs alive — the arrival of a serious, ICC-backed league feels less like a novelty and more like overdue recognition. When the first ball is bowled in late August, in Dublin or Rotterdam or Glasgow, a good share of the players running in will carry surnames the diaspora knows well. That is the story worth following."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "A cricket match in Europe's associate game"
img_attribution = "Wikimedia Commons"
img_final = None

# On-topic Commons imagery — associate / Ireland / Netherlands cricket, grounds
for q in ["Ireland cricket team T20", "Netherlands cricket team",
          "Clontarf Cricket Club Ground Dublin", "Malahide Cricket Club Ground",
          "VRA Cricket Ground Amstelveen", "Scotland cricket team"]:
    cands = fetch_wikimedia_commons_images(q)
    for c in cands:
        low = c["title"].lower()
        print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
        if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                       "letters", "diagram", "chart", "flag", "icon"]):
            continue
        got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
        if got:
            img_final = got
            img_caption = "Associate-nation cricket in Europe, the talent base the new ETPL is built to develop"
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
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Cricbuzz \u2014 ETPL opens player draft registration (News Digest, June 2026)", "url": "https://m.cricbuzz.com/cricket-news"},
        {"name": "LatestLY/ANI \u2014 European T20 Premier League Opens Player Draft Registration Ahead of Historic Inaugural Season", "url": "https://www.latestly.com/agency-news/"},
        {"name": "Devdiscourse \u2014 European T20 Premier League opens player draft registration ahead of historic inaugural season", "url": "https://www.devdiscourse.com/news"},
        {"name": "Cricbuzz \u2014 European T20 Premier League to begin (ICC-sanctioned, three-nation league)", "url": "https://www.cricbuzz.com/cricket-news"},
    ]),
    "diaspora_angle": "The Irish, Scottish and Dutch national teams the ETPL is built to strengthen have for years been substantially powered by South Asian immigrant communities, and a serious, well-broadcast home league gives diaspora families across Britain, Ireland and the Netherlands a top-tier local team to watch and a real professional pathway for their children.",
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
