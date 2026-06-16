#!/usr/bin/env python3
"""
Sports Writer — June 16, 2026 (07:30 UTC run)
Article: India names its badminton squad for the 20th Asian Games in
Aichi-Nagoya, Japan (Sep 19 - Oct 4, 2026). PV Sindhu, Lakshya Sen and
defending champions Satwik-Chirag headline a side balanced with a wave of
young talent — Ayush Shetty, Unnati Hooda, Tanvi Sharma.
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
            img = data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


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
        r = requests.get(img_url, headers={"User-Agent": UA}, timeout=30)
        content = None
        if r.status_code != 200:
            import subprocess
            tmp = f"/tmp/{filename}"
            subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, img_url], capture_output=True)
            if os.path.exists(tmp) and os.path.getsize(tmp) > 5000:
                content = open(tmp, "rb").read()
            else:
                print(f"  \u2717 Download failed ({r.status_code}) for {img_url[:80]}")
                return None
        else:
            ct = r.headers.get("Content-Type", "")
            if not ct.startswith("image/"):
                print(f"  \u2717 Not an image: {ct}")
                return None
            if len(r.content) < 5000:
                print(f"  \u2717 Image too small: {len(r.content)} bytes")
                return None
            content = r.content

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
            data=compressed,
            timeout=30,
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
print("ARTICLE: India's badminton squad for Asian Games 2026")
print("="*60)

art_slug = "india-badminton-squad-asian-games-2026-aichi-nagoya-sindhu-lakshya-sen-satwik-chirag-young-guard-nri"
art_headline = "Sindhu Is Back for a Fourth Asian Games. This Time She Leads a Team That No Longer Depends on Her."
art_subheadline = "India named its badminton squad for the 20th Asian Games in Aichi-Nagoya. The headline names are familiar \u2014 PV Sindhu, Lakshya Sen, the gold-winning Satwik-Chirag. The story underneath is the depth that has finally arrived behind them."

art_body = """The Badminton Association of India announced its squad for the 20th Asian Games on Saturday, and on paper the marquee names read like a greatest-hits list of the last decade. PV Sindhu, the two-time Asian Games medallist and former world champion. Satwiksairaj Rankireddy and Chirag Shetty, the men's doubles pair who won historic gold in 2022. Lakshya Sen, back inside the world's top 10 and leading the men's singles charge. The continental Games run in Aichi-Nagoya, Japan, from September 19 to October 4.

But for anyone who has watched Indian badminton lurch from one lonely superstar to the next, the more telling part of the team sheet is not the top of it. It is the names underneath \u2014 Ayush Shetty, Unnati Hooda, Tanvi Sharma \u2014 and what their presence says about a sport that, for the first time in a generation, is not resting its entire medal hope on a single pair of shoulders.

## The Selection

The BAI selection committee finalised the squad after weighing recent results across national and international tournaments alongside BWF rankings as of May 26, 2026. India will compete in both the team championship and all five individual disciplines, chasing additions to its tally of 13 Asian Games badminton medals \u2014 a haul built largely in the last two editions.

The men's team retains much of the core that reached the podium at this year's Thomas Cup and won silver in the team event at the 2022 Games: Lakshya Sen, H. S. Prannoy, Kidambi Srikanth, the Satwik-Chirag axis, and a doubles supporting cast of Hariharan Amsakarunan, M. R. Arjun and Dhruv Kapila. The women's team is anchored by Sindhu and the doubles pairing of Treesa Jolly and Gayatri Gopichand.

In the individual events, Sen and the rising Ayush Shetty contest men's singles; Sindhu and Unnati Hooda take women's singles; Satwik-Chirag and Hariharan-Arjun go in men's doubles; Treesa-Gayatri and Kavipriya Selvam-Simran Singhi in women's doubles; and India's top mixed pair, Dhruv Kapila and Tanisha Crasto, in the XD draw.

## A Fourth Games, A Different Role

For Sindhu, this is a fourth Asian Games, and the framing has quietly shifted. At Incheon in 2014 and through the years that followed, she was the safety net \u2014 the one name India could pencil in for a deep run. Now 30, with an Olympic silver and bronze and a world title behind her, she arrives less as the sole hope and more as the senior figure in a deeper room. "Indian badminton today is in a position where success is being shaped not just by individual excellence, but by the growing depth of talent across categories," the BAI noted in its announcement, pointing to Satwik-Chirag's return to form, Sen's climb back into the top 10, and the men's team's repeat Thomas Cup podium.

## The Young Guard

The clearest signal is the youth. Ayush Shetty earned his place on the back of a silver medal at the Badminton Asia Championships, a result that announced him as more than a prospect. Unnati Hooda, a teenager who has already won team-championship hardware, slots into women's singles behind Sindhu \u2014 the exact succession plan Indian women's badminton has lacked since Saina Nehwal and Sindhu themselves. And Tanvi Sharma, a silver medallist at the BWF World Junior Championships individual event, completes a trio of selections that reflect performance, not reputation.

This is the part that should interest the diaspora most. For years, the worry around Indian badminton has been the cliff edge behind the stars \u2014 the sense that when Sindhu or Sen stepped away, there was nothing underneath. Aichi-Nagoya is the first major Games where that fear looks misplaced.

## What the Diaspora Is Watching

For Indian sports fans abroad, the Asian Games occupy a particular place: a multi-sport stage where badminton is one of the surest sources of national pride, and where the time difference with Japan makes for watchable evenings in much of Asia and manageable mornings on the US East Coast. The 2022 gold from Satwik-Chirag was a watershed moment streamed and re-shared across diaspora WhatsApp groups; a repeat, or a Sindhu medal in what may be one of her final Games, would land the same way.

But the deeper draw this time is the changing of the guard playing out in real time. Watching Sindhu lead rather than carry, and watching a 17-year-old line up in the same singles draw she once owned alone, is the kind of generational handover that diaspora families \u2014 many raising their own children on weekend badminton in suburban gyms from New Jersey to Surrey \u2014 recognise instantly. The medals will matter. The succession may matter more."""

print("\nSourcing image...")
# Hero: PV Sindhu — verified Wikipedia/Commons photo of the squad's marquee name
img_candidate = fetch_wikipedia_person_image("P. V. Sindhu")
img_caption = "PV Sindhu, who will lead India's women's singles challenge at the 2026 Asian Games"
img_attribution = "Wikimedia Commons"

img_final = None
if img_candidate:
    img_final = upload_to_supabase(img_candidate, f"{art_slug}.jpg")

if not img_final:
    # Fallback: Satwik-Chirag's Satwiksairaj
    alt = fetch_wikipedia_person_image("Lakshya Sen")
    if alt:
        img_final = upload_to_supabase(alt, f"{art_slug}-lsen.jpg")
        if img_final:
            img_caption = "Lakshya Sen, who leads India's men's singles contingent at the 2026 Asian Games"

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "badminton",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "The Bridge \u2014 PV Sindhu, Satwik-Chirag to headline India's squad for the 2026 Asian Games", "url": "https://thebridge.in"},
        {"name": "Khel Now \u2014 Asian Games 2026: India's badminton contingent for Aichi-Nagoya", "url": "https://khelnow.com"},
        {"name": "myKhel \u2014 Asian Games 2026: PV Sindhu, Satwik-Chirag to lead a young Indian badminton squad in Japan", "url": "https://www.mykhel.com"},
        {"name": "IANS \u2014 Two-time medalist Sindhu, 2022 champs Satwik-Chirag headline India's Asian Games squad", "url": "https://ianslive.in"},
    ]),
    "diaspora_angle": "The Asian Games is one of the surest sources of badminton pride for Indian sports fans abroad, and this squad marks a generational handover \u2014 with PV Sindhu now leading rather than carrying a team finally deep in young talent.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "="*60)
print("DONE")
print("="*60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print("Set to status='review'")
