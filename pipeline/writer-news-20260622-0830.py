#!/usr/bin/env python3
"""
Videshi News Writer — June 22, 2026 (08:30 UTC run)
2 NEW articles:
  1. BRICS National Security Advisers' Meeting opens in New Delhi, chaired by
     Ajit Doval; Wang Yi & Shoigu attend; theme = non-traditional security
     (cyber, AI, counter-terrorism). Diaspora angle: geopolitics shaping the
     world NRIs live in. (geopolitics)
  2. Iran oil deal cut crude, but airfares — including the India routes the
     diaspora flies — are set to stay high. (economy / travel-cost)
"""

import os, json, requests, urllib.parse, subprocess, io
from datetime import datetime, timezone
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

UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error: {e}")
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
                if ii.get("width", 0) < 300:
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


def pick_commons(queries, min_width=900):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            return pick["url"]
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




# ─── Article 1: BRICS National Security Advisers' Meeting in New Delhi ──────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: BRICS NSA Meeting, New Delhi, Doval chairs")
    print("="*60)

    slug = "brics-national-security-advisers-meeting-new-delhi-doval-wang-yi-shoigu-20260622"
    headline = "India Just Gathered the Security Chiefs of China, Russia and Iran in One Delhi Room. Doval Is in the Chair."
    subheadline = "The BRICS National Security Advisers' Meeting opens in New Delhi on Monday, with Wang Yi and Sergei Shoigu among the delegates. The agenda is cyber, AI and terrorism — but the subtext is India's bid to steer a bloc that now stretches from Beijing to Brasilia."

    body = """For two days starting Monday, New Delhi becomes the meeting point for the security establishments of some of the world's most consequential and most rivalrous powers. India is hosting the BRICS National Security Advisers' Meeting on June 22 and 23, and the man in the chair is Ajit Doval, the country's National Security Adviser and the architect of much of its strategic doctrine over the past decade.

The guest list reads like a map of a shifting world order. China is sending Foreign Minister Wang Yi — his first visit to India since August 2025, a detail that carries weight given the long chill between the two neighbours. Russia is represented by Sergei Shoigu, secretary of its Security Council. Iran is sending Deputy Secretary Nezamipour of its Supreme National Security Council, fresh off a spring of open conflict with the United States and Israel. Brazil, South Africa, Egypt, Ethiopia, Indonesia, Saudi Arabia and the United Arab Emirates round out a bloc that, since its expansion, now counts eleven members and a sizeable share of the planet's population and energy reserves.

## A Deliberately Modern Agenda

The official theme is "Non-traditional security challenges confronting the world today" — diplomatic shorthand for the threats that do not arrive as armies crossing borders. The Ministry of External Affairs says delegates will examine the rapidly evolving nature of national security and, in particular, the role of new technologies in emerging threats: cybersecurity, digital vulnerabilities, and the risks thrown up by artificial intelligence.

The advisers will also review the outcomes of recent BRICS Joint Working Groups on counter-terrorism and on security in the use of information and communication technologies. For India, which has long pressed international forums to take cross-border terrorism seriously, the counter-terror file is not a box-ticking exercise but a core national-security interest, and a recurring source of friction with neighbours.

## Why India Wants This Meeting

The gathering is a rung on a ladder. It is meant to prepare the ground for the BRICS Summit that India will host later this year, in September, as the bloc's chair. New Delhi holds the BRICS presidency for the fourth time — after 2012, 2016 and 2021 — under the theme "Building for Resilience, Innovation, Cooperation and Sustainability," language that reflects Prime Minister Narendra Modi's framing of India as a voice for the developing world.

That framing is doing real work. BRICS has expanded from its original economic remit into a three-pillar agenda spanning political and security cooperation, economy and finance, and people-to-people ties. By chairing the security track, India gets to set the tone — choosing to foreground technology and terrorism rather than the harder, more divisive questions of military alignment that could expose the bloc's internal contradictions. After all, this is a room that contains both India and China, whose troops faced off in the Himalayas not long ago, and a Russia and Iran increasingly cast as adversaries by the West.

## The Diaspora's Stake in the Room

For Indians abroad, a security meeting in Delhi can feel remote. It is not. BRICS is, at heart, an argument about whose rules govern global trade, technology and finance — and the diaspora lives inside the consequences of that argument. NRIs in the United States, Britain and Canada have spent the past months watching tariffs, visa rules and currency swings whipsaw their plans; those are the downstream weather of exactly the geopolitical contest BRICS is trying to reposition.

There is a more direct line, too. The bloc's push to settle more trade outside the dollar, to build alternative payment rails, and to deepen ties among emerging economies bears on everything from how cheaply an NRI can move money home to how India's markets are valued. And India's insistence on keeping terrorism and cyber threats at the centre of the conversation reflects the security of the very country millions of diaspora families still call home, visit each winter, and invest in.

Wang Yi's presence is the headline most analysts will watch. A Chinese foreign minister flying to Delhi to sit at a table India has set is, in itself, a small thawing — and a reminder that for all the rivalry, the giants of Asia keep finding reasons to talk. For a diaspora that straddles both the Western world and its Indian roots, that conversation is worth following closely. The summit in September will tell us how much of it was real."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Ajit Doval")
    img_caption = "National Security Adviser Ajit Doval, who chairs the BRICS NSA Meeting in New Delhi"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        img_url = pick_commons([
            "BRICS summit India",
            "Ministry of External Affairs India building",
            "BRICS leaders meeting"
        ])
        img_caption = "BRICS delegates meet; India chairs the bloc for the fourth time in 2026"

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
            "The Hindu BusinessLine \u2014 India to host BRICS National Security Advisers' Meet from June 22-23: MEA (June 20, 2026): chaired by NSA Ajit Doval; theme 'Non-traditional security challenges confronting the world today'; review of Joint Working Groups on Counter-Terrorism and ICT security; India's fourth BRICS chairship after 2012, 2016, 2021",
            "Madhyamam Online / IANS \u2014 India to host BRICS security advisers' meeting chaired by Ajit Doval on June 22-23: attendees include Chinese FM Wang Yi and Russian Security Council Secretary Sergei Shoigu; Chinese Ambassador Xu Feihong's X post on agenda; meeting as step toward September BRICS Summit",
            "News Dive \u2014 Ajit Doval to Lead BRICS Security Advisors Meeting in India Scheduled for June 22: delegations include Wang Yi, Sergei Shoigu, and Deputy Secretary Nezamipour of Iran's Supreme National Security Council; precursor to September summit in India",
            "New Kerala \u2014 India Hosts BRICS Security Meet: Focus on Cyber, AI Threats: Wang Yi's first visit to India since August 2025; focus on cybersecurity, digital vulnerabilities, AI-driven risks; BRICS now 11 members across political-security, economy-finance, people-to-people pillars"
        ]),
        "diaspora_angle": "BRICS is an argument over whose rules govern global trade, technology, currency and security \u2014 the same forces behind the tariffs, visa rules and rupee swings that buffet NRIs abroad, and the safety of the India their families still call home.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Airfares stay high despite Iran oil relief ──────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Airfares stay high despite Iran oil relief")
    print("="*60)

    slug = "airline-fares-stay-high-despite-iran-oil-deal-india-routes-diaspora-travel-20260622"
    headline = "Oil Is Falling After the Iran Deal. Your Flight to India Is Not Going to Get Cheaper Anytime Soon."
    subheadline = "Airlines are about to save tens of billions on fuel as crude slides on the back of the US-Iran ceasefire. But tight capacity means carriers plan to pocket the relief, not pass it on \u2014 and the diaspora's long-haul routes are squarely in the squeeze."

    body = """The interim peace deal between the United States and Iran has done what months of diplomacy could not: it has pushed oil prices sharply lower. US jet fuel spot prices stood at $2.85 a gallon on June 17, down hard from an early-April high of $4.88. On paper, that is enormous relief for the world's airlines \u2014 a decline of that size would cut the US industry's annual fuel bill by more than $40 billion, by Reuters' calculation. For anyone hoping that cheaper fuel means a cheaper ticket home, the bad news is that it almost certainly does not work that way this time.

The reason is capacity. After a brutal year, airlines are not racing to add seats and fight for passengers with lower fares. They are doing the opposite \u2014 holding the line on price to rebuild margins battered by the spring's fuel spike. US domestic airline seats are scheduled to grow just 0.4% year-on-year in the third quarter, down from the 4.6% expected before the latest Middle East tensions. Aircraft delivery delays, tight airport slots and weakened low-cost carriers have removed the usual pressure that drags fares down when oil falls.

## Fares Rose Less Than Fuel \u2014 and Won't Fall Back

Through the fuel spike, carriers raised ticket prices and bag fees but recovered only part of their costs. Industry data show jet fuel prices rose more than three times as fast as airfares from January through May, and Deutsche Bank estimated US carriers recouped only about 60 cents of every extra dollar spent on fuel. United's chief executive told Reuters his airline is "on a path to recovering 100% by the end of the year" \u2014 a frank admission that lower fuel costs will go toward repairing the books, not lowering fares. Average US domestic fares booked a week before travel were still up 34% year-on-year as of early June.

Outside the United States, the picture is uneven, and not in the diaspora's favour. Lower crude takes time to feed through to jet fuel, and analysts say that unless jet fuel falls back toward the start of the year, airlines will keep fares firm or push them higher wherever demand allows. Long-haul fares may ease somewhat in Europe, where carriers passed fuel costs through more aggressively. But the Middle East \u2014 the very airspace most India-bound flights cross \u2014 is described as the clearest exception, with fuel still too expensive for widespread discounting.

## What This Means for the India Routes

For the millions of NRIs who fly between India and the United States, Britain, Canada and the Gulf, the calculus is unforgiving. These are long-haul, fuel-intensive routes, and many of them transit or connect through Gulf hubs \u2014 Dubai, Doha, Abu Dhabi \u2014 that sit in the region analysts single out as least likely to see fare cuts. Carriers on these routes spent the spring contending with rerouting and disruption from the Gulf conflict; now they have every incentive to use the fuel windfall to recover, not to discount.

Gulf carriers could prove an exception within the exception. Analysts note UAE airlines may be more aggressive on promotions and enjoy stronger government backing, which could mean occasional deals for travellers willing to route through Dubai or Abu Dhabi. But that is a narrow opening, not a trend.

The structural point holds: a 5% drop in fuel costs lifts airline earnings by 10% to 15% for the big US carriers, by one estimate \u2014 powerful motivation to bank the savings. As one airline executive bluntly summarised the industry's mood when asked about a return to fatter margins: it depends entirely on "when's fuel going to go down," and whether they can hold price once it does.

## The Practical Takeaway

For diaspora travellers planning the annual trip home, the winter holidays, or a family wedding, the message from the data is to book early and not to wait for a fuel-driven price collapse that the industry has no intention of delivering. Demand, not crude, is now the variable that matters most \u2014 and as long as planes keep filling, fares will stay firm. The Iran deal may have spared the global economy a far worse oil shock, sparing diaspora households the much higher fares a prolonged war would have brought. But the relief is showing up on airline balance sheets, not on the booking page. For the family flight to India, the cheapest seat is still the one bought soonest."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = pick_commons([
        "airport departure board terminal",
        "airliner aircraft airport India",
        "commercial airplane airport terminal",
        "aircraft jet airport runway"
    ])
    img_caption = "Long-haul carriers are set to keep fares high despite falling fuel costs"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("airport terminal airplane departure")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Travellers at an airport terminal"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters \u2014 Analysis: Airline ticket prices may stay high as carriers bank fuel relief from Iran deal (June 22, 2026): US jet fuel $2.85/gal June 17 vs $4.88 early-April high; $40bn+ potential annual fuel-bill cut; US Q3 domestic seats +0.4% YoY (down from 4.6% pre-tension); fares up 34.1% YoY as of June 8; United CEO Scott Kirby targets 100% cost recovery by year-end",
            "Reuters (same analysis) \u2014 jet fuel rose 3x faster than airfares Jan-May; Deutsche Bank estimate of 60c recovery per extra fuel dollar ($14.4bn revenue vs $24.1bn costs); Middle East called clearest exception to fare relief; UAE carriers may be more aggressive with government backing; Jefferies: 5% fuel-cost drop lifts EPS 10-15% for Delta/Southwest/United",
            "Reuters \u2014 Asian stocks gain, oil slips as Iran talks progress (June 22, 2026): Brent ~$81/barrel, far below May peak of $126.41; oil decline driven by US-Iran interim peace deal and Strait of Hormuz developments"
        ]),
        "diaspora_angle": "NRIs fly some of the most fuel-intensive long-haul routes in the world, many transiting the Gulf hubs analysts say are least likely to see fare cuts \u2014 so the oil windfall from the Iran deal will pad airline margins rather than lower the price of the family flight home.",
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
