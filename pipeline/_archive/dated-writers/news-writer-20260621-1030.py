#!/usr/bin/env python3
"""
Videshi News Writer — June 21, 2026 (10:30 UTC run)
2 NEW articles:
  1. Bangladesh PM Tarique Rahman skips India for first foreign trip (Malaysia + China); Hasina, Teesta, Mongla port (news / geopolitics)
  2. International Day of Yoga 2026 — Modi leads 12th IDY from Kolkata's Red Road, diaspora celebrations worldwide (news / culture-diaspora)
"""

import os, json, requests, urllib.parse, subprocess, io
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"


# ─── Image sourcing functions ────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
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
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 600:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  \u2713 Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def download_and_compress(url, slug):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  \u26a0 Download failed ({r.status_code}): {url[:80]}")
            try:
                tmp = f"/tmp/{slug}_src"
                subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=30, check=True)
                with open(tmp, "rb") as f:
                    content = f.read()
                if len(content) < 5000:
                    return None
                r_content = content
            except Exception:
                return None
        else:
            r_content = r.content
        ct = r.headers.get("Content-Type", "") if r.status_code == 200 else "image/jpeg"
        if "image" not in ct and len(r_content) < 5000:
            print(f"  \u26a0 Not an image or too small: {ct}, {len(r_content)} bytes")
            return None

        from PIL import Image
        img = Image.open(io.BytesIO(r_content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()

        if len(compressed) < 5000:
            print(f"  \u26a0 Compressed image too small: {len(compressed)} bytes")
            return None

        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"

        requests.delete(upload_url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY
        })

        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }, timeout=30)

        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None

    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ─── Article 1: Bangladesh PM skips India for first foreign trip ──

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Bangladesh PM Tarique Rahman skips India")
    print("="*60)

    slug = "bangladesh-pm-tarique-rahman-first-foreign-trip-malaysia-china-skips-india-hasina-teesta-20260621"
    headline = "Bangladesh's New Prime Minister Picked His First Trip Abroad. He Did Not Pick India."
    subheadline = "Tarique Rahman flew to Malaysia on Sunday and heads to Beijing on Monday for a deal-laden state visit \u2014 bypassing the neighbour that hosts the leader he wants extradited, and signalling to three South Asian capitals that Dhaka intends to keep its options wide open."

    body = """When a new prime minister chooses where to make his first foreign trip, the choice is rarely an accident. So when Bangladesh's foreign ministry announced on Saturday that Tarique Rahman would fly to Malaysia on Sunday and on to China the next day \u2014 with no stop in New Delhi \u2014 the message landed clearly in three South Asian capitals at once. For the millions of Bangladeshi-origin and Indian-origin families whose lives straddle the region, from Kolkata to Kuala Lumpur, the itinerary is a map of where the subcontinent's balance of power may be heading.

Rahman, who took office in February after his Bangladesh Nationalist Party won elections that ended an 18-month interim administration, had a standing invitation to India. Prime Minister Narendra Modi was among the first world leaders to congratulate him, and Lok Sabha Speaker Om Birla attended his swearing-in in Dhaka. There had even been speculation Rahman might first visit a smaller neighbour such as Bhutan or the Maldives. Instead he chose Malaysia and China \u2014 a decision that, by its own logic, was as much economic as it was diplomatic.

## What He Is Going For

The substance of the trip is heavily tilted toward Beijing. Dhaka's foreign secretary told reporters that Bangladesh and China are expected to sign 17 bilateral instruments, including 13 memorandums of understanding and a joint action plan, during a state visit that runs from June 23 to 25. Rahman is scheduled to meet Premier Li Qiang and to sit down with President Xi Jinping on June 26. Among the headline items: Chinese support for the long-delayed Teesta River restoration project \u2014 a plan to dredge, embank and manage a key river through dredging and irrigation \u2014 and Chinese participation in modernising Mongla Port, Bangladesh's second-largest. The two sides may also issue a joint communiqu\u00e9 for the first time in nearly two decades, and Dhaka is expected to sign on to Beijing's Global Development Initiative.

The Malaysia leg is built around people. Malaysia is home to an estimated 800,000 Bangladeshi workers \u2014 more than a third of its foreign workforce \u2014 and talks there are expected to focus on labour migration, recruitment and broader trade. Remittances from those workers are a crucial source of foreign exchange for a country of 170 million, which gives the Kuala Lumpur stop a domestic urgency that goes well beyond protocol.

## The Shadow of Sheikh Hasina

What India watches most closely is the gap the itinerary leaves behind. Relations between Dhaka and New Delhi have been strained since the 2024 uprising that toppled former prime minister Sheikh Hasina, a long-standing ally of India who fled across the border and has lived in India ever since. Bangladesh has repeatedly demanded her extradition; India said in late 2025 it was examining the request. As long as Hasina remains on Indian soil, the single most sensitive issue between the two governments stays unresolved \u2014 and a first prime ministerial visit to Delhi would have been freighted with it.

Ties have improved since Rahman took over, but frictions persist. The two countries have clashed over border tensions and over Indian "push-ins" \u2014 Bangladesh's allegation that Indian authorities have pushed people they deem illegal migrants across the frontier without following agreed repatriation procedures. Border guards from both sides met in New Delhi last week and agreed to strengthen intelligence-sharing and coordinate patrols, but the migrant dispute remains a running sore. Against that backdrop, the choice of Beijing and Kuala Lumpur reads less as a snub than as a hedge: Dhaka widening its options while keeping India and China in careful balance.

## Why It Matters for the Diaspora

For the Indian diaspora, and especially for the millions of Bengali-origin families in West Bengal, the Northeast and abroad, the India-Bangladesh relationship is never purely foreign policy \u2014 it is rivers, borders, trade routes and kinship that cut across the line drawn in 1947. A Bangladesh tilting toward China complicates everything from the management of shared rivers like the Teesta, on which farmers on both sides depend, to the security calculus along a 4,000-kilometre frontier that India has long worried about. New Delhi has watched China's expanding footprint in South Asia \u2014 in Sri Lanka, the Maldives, Nepal and now potentially at Mongla, uncomfortably close to Indian waters \u2014 with steady unease.

There is also the human layer. Bangladeshi migrant workers in Malaysia and the Gulf occupy the same labour corridors as Indian workers, and the remittance economies of both nations rise and fall together. A prime minister who builds his foreign policy around jobs abroad and infrastructure at home is responding to the same pressures \u2014 employment, foreign exchange, development \u2014 that shape the lives of South Asians everywhere they have settled. Rahman's first trip abroad, in the end, is a statement about which doors Dhaka intends to keep open. For now, the one to New Delhi is being left, pointedly, for later."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "Mongla Port in southern Bangladesh; Chinese participation in modernising the port is on the agenda for PM Tarique Rahman's Beijing visit"
    img_attribution = "Wikimedia Commons"

    # Try Tarique Rahman's actual photo first
    person_img = fetch_wikipedia_person_image("Tarique Rahman")
    if person_img:
        img_url = person_img
        img_caption = "Bangladesh Prime Minister Tarique Rahman, who chose Malaysia and China over India for his first foreign trip since taking office in February"
        img_attribution = "Wikimedia Commons"

    if not img_url:
        for q in ["Mongla Port Bangladesh", "Bangladesh China flags diplomacy", "Teesta River Bangladesh", "Dhaka Bangladesh government building"]:
            commons = fetch_wikimedia_commons_images(q)
            if commons:
                img_url = commons[0]["url"]
                t = commons[0]["title"].lower()
                if "teesta" in t:
                    img_caption = "The Teesta River; Chinese support for a long-delayed Teesta restoration project is on the agenda for Bangladesh PM Tarique Rahman's China visit"
                elif "dhaka" in t:
                    img_caption = "A government building in Dhaka, Bangladesh, whose new prime minister bypassed India for his first foreign trip"
                break

    if not img_url:
        px = fetch_pexels_image("Dhaka Bangladesh city")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Dhaka, Bangladesh, whose new prime minister chose Malaysia and China over neighbouring India for his first trip abroad"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters \u2014 Bangladesh's premier looks to China, Malaysia for investment, jobs in first trip (Tarique Rahman bypasses India; Hasina in India; border tensions and push-ins; ~800,000 Bangladeshi workers in Malaysia; Teesta project)",
            "AFP / Malay Mail \u2014 Bangladesh PM Tarique Rahman picks Malaysia, China for first overseas trips, skips India (Sunday Malaysia, Monday China; Teesta dredging/embankment; Modi invitation via Om Birla; Hasina extradition; China's regional influence)",
            "The Business Standard (tbsnews.net) \u2014 PM's China visit: Dhaka, Beijing likely to sign 15-17 bilateral instruments (June 23-25; Xi Jinping June 26; Premier Li Qiang)",
            "News Ei Samay \u2014 Bangladesh-China to sign 17 instruments including 13 MoUs; Mongla Port modernisation; joint communiqu\u00e9 after ~two decades; Global Development Initiative; Modi's February invitation"
        ]),
        "diaspora_angle": "The India-Bangladesh relationship is rivers, borders, trade and kinship for millions of Bengali-origin families in West Bengal, the Northeast and abroad, so a new Dhaka government tilting toward China \u2014 on shared rivers like the Teesta and on a port near Indian waters \u2014 reshapes the security and economic landscape of the eastern subcontinent the diaspora is tied to.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: International Day of Yoga 2026 ────────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: International Day of Yoga 2026")
    print("="*60)

    slug = "international-day-of-yoga-2026-modi-kolkata-red-road-healthy-ageing-diaspora-worldwide-20260621"
    headline = "On the Longest Day, India's Quietest Export Filled Parks From Kolkata to Birmingham"
    subheadline = "Narendra Modi led the 12th International Day of Yoga from Kolkata's Red Road on Sunday under the theme 'Yoga for Healthy Ageing,' as Indian consulates from Birmingham to Shanghai turned town squares into mass mat sessions \u2014 the diaspora's softest and most durable form of soft power."

    body = """On the longest day of the year in the Northern Hemisphere, millions of people in India and across its diaspora unrolled a mat. Sunday marked the 12th International Day of Yoga, and Prime Minister Narendra Modi led the national observance from Kolkata's iconic Red Road, while President Droupadi Murmu joined a state-level event in Jabalpur, Madhya Pradesh, moving through asanas alongside ordinary participants. The theme this year \u2014 "Yoga for Healthy Ageing" \u2014 framed the practice less as exercise and more as a quiet strategy for living well into old age, a message aimed squarely at a graying world.

"Yoga brings people together. I extend my greetings to people across the world on this occasion," Modi told the gathering in Kolkata. He stressed that yoga is far more than physical movement: "Yoga is not restricted to any age group or community. It is an expression of the human spirit and a pathway to harmony between the body, mind and soul." Across the country, sessions filled parks, schools, government offices and village squares, with Union Ministers, Governors and Chief Ministers folding into the crowds.

## A Date India Wrote Into the Calendar

There is a reason June 21 carries this particular weight. The United Nations General Assembly declared it the International Day of Yoga in 2014, after a campaign led by Modi, choosing the summer solstice \u2014 the longest day \u2014 as a date of symbolic significance across many cultures. In the decade since, the observance has grown from a novelty into one of the largest community celebrations on the global calendar, a rare instance of a single country successfully exporting a piece of its civilisational heritage as a shared international ritual.

For India, the day has become a deliberate instrument of soft power, and the diaspora is its most effective delivery system. Where a trade deal is negotiated behind closed doors and a defence pact reaches only governments, a yoga session in a public square reaches families, neighbours and the merely curious. It is diplomacy conducted in tracksuits, and it works precisely because it asks for nothing in return.

## The Diaspora Turns Out

That was visible this weekend in the global program of events organised by Indian missions abroad. In Britain, the Consulate General of India in Birmingham hosted the 12th International Day of Yoga at Victoria Square under the banner "Yoga for Wellness, Wisdom and World Peace," capping weeks of lead-up sessions \u2014 from "Saree Yoga" to fun yoga for kids \u2014 run with community groups including the Isha Foundation, the Brahma Kumaris, Heartfulness and the Art of Living. In China, the Indian consulate in Shanghai held curtain-raiser events that drew nearly 500 participants of diverse nationalities, with the main-day celebrations expected to bring together the Indian diaspora, Chinese practitioners and wellness enthusiasts across Eastern China.

These are not isolated set-pieces. Across the United States, Canada, the Gulf, Australia and Europe, Indian associations and consulates have spent June staging mass yoga events in parks, on beaches and in convention halls \u2014 the kind of gathering that lets a second-generation child see a few thousand people, many of them not Indian at all, practising something their grandparents did. For a community that often measures its presence abroad in CEOs and spelling-bee champions, this is a different and gentler register of belonging: cultural rather than competitive, open rather than exclusive.

## Why It Matters

The "Healthy Ageing" theme has a particular resonance for the diaspora. First-generation immigrants who arrived decades ago are now entering their sixties and seventies far from the joint-family structures that once cushioned old age in India. Yoga \u2014 low-cost, low-impact, requiring nothing but a mat and a patch of floor \u2014 has quietly become part of how many of them manage blood pressure, joint mobility, stress and the loneliness that can shadow ageing abroad. The Ministry of Ayush framed the year's theme around extending not just lifespan but "healthspan," the years lived in good health, and that is a goal that translates cleanly across every time zone the diaspora occupies.

There is a strategic dividend too. Every park session abroad strengthens the association between India and wellness, a brand that feeds tourism, the global market for Indian wellness products and services, and the country's wider cultural standing. But the deeper point is simpler and more human. On a single day, in dozens of countries, people of Indian origin and their friends and neighbours did the same thing at roughly the same time, for no reason other than that it felt good and connected them to something older than any of them. In an anxious and polarised year, that quiet synchrony \u2014 a few million people breathing in unison from Kolkata to Birmingham \u2014 may be the most reassuring thing the diaspora exported all summer."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "A mass yoga session marking the International Day of Yoga; the 12th edition was led by PM Modi from Kolkata on June 21, 2026"
    img_attribution = "Wikimedia Commons"

    for q in ["International Day of Yoga India", "International Yoga Day mass session", "yoga day India Modi", "yoga asana group outdoor India"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            break

    if not img_url:
        px = fetch_pexels_image("group yoga outdoor sunrise")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A group yoga session at sunrise; the 12th International Day of Yoga was observed worldwide on June 21, 2026"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "culture",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Impressive Times \u2014 International Yoga Day 2026: PM Modi Leads Nationwide Celebrations from Kolkata; Yoga for Healthy Ageing (Modi at Red Road, President Murmu in Jabalpur, 12th IDY, June 21 longest day, Modi quotes)",
            "Medical Dialogues \u2014 International Yoga Day 2026: NMC organises special event; Ministry of Ayush nationwide observance; theme 'Yoga for Healthy Ageing'; main event led by Modi from Kolkata",
            "PIB (Ministry of Ayush) \u2014 Main IDY 2026 celebration in Kolkata June 21; theme 'Yoga for Healthy Ageing'; healthspan vs lifespan framing; UNGA 2014 declaration",
            "Eventbrite / Consulate General of India, Birmingham \u2014 12th International Day of Yoga at Victoria Square, 'Yoga for Wellness, Wisdom and World Peace'; lead-up sessions with Isha, Brahma Kumaris, Heartfulness, Art of Living",
            "LatestLY / ANI \u2014 Indian Consulate in Shanghai hosts curtain-raiser ahead of IDY 2026; ~500 participants; June 21 UN declaration credited to Modi"
        ]),
        "diaspora_angle": "International Day of Yoga is India's most effective form of soft power and the diaspora is its delivery system \u2014 consulates from Birmingham to Shanghai turned public squares into mass sessions, while the 'Healthy Ageing' theme speaks directly to first-generation immigrants now growing old far from the joint families that once cushioned old age in India.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    print("\n" + "="*60)
    print(f"DONE. Inserted IDs: {[i for i in ids if i]}")
    print("="*60)
