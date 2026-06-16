#!/usr/bin/env python3
"""
Sports Writer — June 16, 2026 (01:30 UTC run)
Article: India's Sports Ministry has sent a "Sports Passport" proposal to the
PMO and Home Ministry that could let PIO/OCI athletes represent India without
surrendering their foreign passports — a story aimed squarely at the diaspora,
pegged to Indian-origin players (Sarpreet Singh, Tahsin Jamshid, Samuel
Moutoussamy) appearing at the FIFA World Cup 2026 for other nations.
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
print("ARTICLE: India's Sports Passport proposal reaches the PMO")
print("="*60)

art_slug = "india-sports-passport-proposal-pmo-pio-oci-athletes-football-fifa-world-cup-2026-diaspora-nri"
art_headline = "India Won't Let Them Play Without Surrendering Their Passports. A New Proposal on Modi's Desk Could Change That."
art_subheadline = "The Sports Ministry has sent the PMO and Home Ministry a \u201cSports Passport\u201d framework that would let PIO and OCI athletes represent India \u2014 a question made unavoidable as players of Indian origin light up the FIFA World Cup for other countries."

art_body = """As the FIFA World Cup 2026 plays out across North America with a record 48 nations, India is once again on the outside looking in \u2014 absent from the field, but unmistakably present in the bloodlines of the men competing. Sarpreet Singh, the son of Punjabi immigrants, is in New Zealand's squad. Tahsin Jamshid, a 19-year-old born in Doha to Keralite parents, is representing Qatar. Samuel Moutoussamy, whose father traces back to a Tamil family in Guadeloupe, anchors DR Congo's midfield. Each carries Indian heritage onto sport's biggest stage \u2014 for someone else.

That uncomfortable arithmetic is now driving a policy debate that has reached the highest levels of the Indian government. According to a Khel Now exclusive, the Ministry of Youth Affairs and Sports has submitted a detailed proposal to the Prime Minister's Office and the Ministry of Home Affairs seeking consideration of a "Sports Passport" framework \u2014 a mechanism that would allow eligible Persons of Indian Origin (PIO) and Overseas Citizens of India (OCI) to represent India in international competition without first renouncing their foreign citizenship.

## The Wall That Indian Athletes Hit

India does not permit dual citizenship. The Constitution forbids it, and successive governments have interpreted that to mean a person cannot hold an Indian passport alongside another country's. Layered on top is a Ministry of Youth Affairs and Sports policy, dating to 2008, that restricts government-supported national-team representation to Indian citizens alone. Courts have repeatedly upheld it: in litigation involving the All India Chess Federation, the judiciary affirmed that as long as the Centre does not recognise dual citizenship, PIO and OCI cardholders cannot turn out for India at international events.

The practical effect is a wall. An athlete of Indian origin who has trained in an elite system abroad \u2014 a swimmer in Australia, a sprinter in Britain, a basketball player in the American college pipeline \u2014 cannot simply pull on India's colours. They must surrender their existing passport and naturalise, a process that is lengthy, irreversible, and professionally costly.

A few have done it. Bengaluru FC forward Ryan Williams renounced his Australian citizenship earlier this year, acquired an Indian passport, and made his debut for the Blue Tigers under Khalid Jamil, scoring against Hong Kong. Before him, Japan-born Arata Izumi took the same route back in 2012. But such cases are rare precisely because the demand \u2014 give up your other life \u2014 is so steep.

## What a Sports Passport Would Actually Do

A Sports Passport is a fast-track or special-eligibility pathway that lets a country field athletes who can strengthen its national teams without necessarily extending the full bundle of citizenship rights. Some nations grant accelerated full citizenship; others build narrower sporting-eligibility frameworks. The aim is uniform: deepen the talent pool and lift competitiveness.

The world is full of working examples. Qatar leaned on sports naturalisation across football, athletics and handball, a strategy that underpinned its AFC Asian Cup triumph in 2019 and its squads at the 2022 World Cup. Bahrain recruited East African distance runners. Turkey has naturalised wrestlers, throwers and weightlifters; Spain used exceptional citizenship provisions to bolster its basketball roster; Hungary and Austria maintain legal carve-outs for individuals deemed to serve the national interest, athletes included.

A source close to the developments told Khel Now the government is likely to take six to eight months to reach a decision, and that the framework is being examined with football, basketball and tennis specifically in mind \u2014 disciplines where naturalisation pathways have moved the needle elsewhere.

## Football Lit the Fuse, But the Stakes Are Bigger

The immediate trigger is football's malaise. India's men's team has slipped down the FIFA rankings and failed to qualify for the AFC Asian Cup for the first time in nearly a decade. AIFF President Kalyan Chaubey has emerged as one of the loudest advocates for a diaspora pathway, raising it again during a recent meeting with Sports Minister Mansukh Mandaviya and Indian Super League club representatives, and urging clubs to sign PIO and OCI players. The federation has reportedly already identified a pool of 28 players who could fit India's long-term plans if the rules change.

But the proposal's reach extends well past the pitch. India is preparing a bid to host the 2036 Olympic Games and faces mounting pressure to convert its vast population into medals. The Khelo Bharat policy framework explicitly frames sport as a vehicle for strengthening ties with overseas Indians. For the first time, a framework that could touch multiple sports at once has formally landed on the desks of the PMO and Home Ministry \u2014 moving the conversation beyond individual federations.

Critics will ask the obvious question: should national teams lean on athletes developed outside India's own system, and might a Sports Passport become an alibi for neglecting grassroots development? Supporters counter that the evidence from Morocco's 2022 run, built substantially on European-trained players, to Ireland, Jamaica and the Philippines shows diaspora talent complements domestic pipelines rather than replacing them.

## Why It Matters to the Diaspora

For NRIs and people of Indian origin in the United States, Britain, Canada and Australia, this is personal in a way few sports-policy debates ever are. It speaks directly to the children and grandchildren of the diaspora \u2014 the ones raised in foreign academies, fluent in another nation's sporting culture, yet still tied to India by name, family and identity. A Sports Passport would tell them they no longer have to choose between the country that shaped their game and the country that shaped their roots. When SAI media was contacted, officials declined to comment, and the final eligibility criteria remain undecided. But the question the proposal forces \u2014 who gets to represent India \u2014 is one the global Indian family has been waiting a long time to have answered.
"""

print("\nSourcing image...")
# Topic/event image: India's national football team. Use Wikimedia Commons
# (actual national-team photo) — far more relevant than a generic Pexels shot.
img_candidate = "https://upload.wikimedia.org/wikipedia/commons/c/c0/India_starting_XI_vs_Puerto_Rico_2016.jpg"
img_caption = "India's national football team lines up before an international match"
img_attribution = "Wikimedia Commons"

img_final = upload_to_supabase(img_candidate, f"{art_slug}.jpg")

if not img_final:
    # Fallback: try the Blue Pilgrims supporters image
    img_final = upload_to_supabase(
        "https://upload.wikimedia.org/wikipedia/commons/5/56/Blue_Pilgrims_at_Mumbai_2018_to_support_India_national_football_team.jpg",
        f"{art_slug}-fans.jpg")
    if img_final:
        img_caption = "Blue Pilgrims supporters rally behind the India national football team"

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "football",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Khel Now", "url": "https://khelnow.com/football/sports-passport-pio-oci-athletes-india"},
        {"name": "RevSportz", "url": "https://revsportz.in/will-the-sports-passport-transform-indian-sports/"},
        {"name": "Mondaq (Legal analysis: PIO/OCI sports eligibility)", "url": "https://www.mondaq.com"},
        {"name": "Jagran Josh", "url": "https://www.jagranjosh.com"},
    ]),
    "diaspora_angle": "A Sports Passport would let PIO and OCI athletes raised abroad represent India without surrendering their foreign citizenship \u2014 directly affecting the children of the diaspora in the US, UK, Canada and Australia who are tied to India by heritage but barred by its citizenship rules.",
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
