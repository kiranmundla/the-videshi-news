#!/usr/bin/env python3
"""
Videshi News Writer — June 21, 2026 (12:30 UTC run)
2 NEW articles:
  1. USTR Jamieson Greer arrives India June 22 eve for June 23-24 talks to finalise interim trade deal; record May exports; Section 301 (news / trade)
  2. India W vs South Africa W — Women's T20 World Cup PREVIEW at Old Trafford, June 21 (news / cricket)
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


# ─── Article 1: USTR Greer arrives to finalise India-US trade deal ─

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: USTR Greer arrives India for trade deal talks")
    print("="*60)

    slug = "ustr-jamieson-greer-india-visit-june-23-interim-trade-deal-record-exports-section-301-diaspora-20260621"
    headline = "America's Top Trade Negotiator Lands in Delhi This Week. A Long-Awaited Deal May Be Within Reach."
    subheadline = "US Trade Representative Jamieson Greer arrives on Monday evening for two days of talks to put the final touches on an interim India-US trade pact \u2014 a deal that would settle tariff questions hanging over Indian exporters and, indirectly, the diaspora economy that depends on them."

    body = """The week that could decide the shape of India's trade relationship with the United States for years to come begins on Monday evening, when US Trade Representative Jamieson Greer steps off a plane in New Delhi. Over June 23 and 24, Greer will sit down with India's Minister for Commerce and Industry to give what officials are calling the "final touches" to an interim bilateral trade agreement \u2014 the closest the two sides have come to a signed deal since they announced a framework, but did not sign it, in February.

For the Indian diaspora in the United States, Britain, Canada and the Gulf, this is not an abstract diplomatic exercise. The terms negotiated in those two days will help set the price of the textiles, pharmaceuticals, jewellery and processed foods that flow between the two economies, the visa-adjacent rules that shape how Indian IT services are sold into America, and the broader confidence that underpins one of the most consequential economic partnerships in the world.

## What Greer Is Coming to Finalise

Commerce Secretary Rajesh Agrawal laid out the schedule plainly this week. "USTR is coming on the evening of June 22nd. On 23-24 June, he will be engaging with our Minister for Commerce and Industry," he told reporters. "We expect that discussions will be centred around giving final touches to the framework deal and also on the larger BTA that has been under discussion between the two sides."

The interim deal traces back to a framework announced on February 6 but never signed, under which the United States agreed to cut tariffs on Indian goods to 18 per cent from a punishing 50 per cent, in exchange for India lowering barriers across industrial and some agricultural products and reducing its purchases of Russian oil. Exporters have said the cut to 18 per cent would put Indian textiles, apparel, pharmaceuticals, chemicals, footwear, jewellery and shrimp roughly on par with Asian competitors such as Vietnam and Bangladesh \u2014 a difference that, for whole industries, is the gap between winning and losing orders.

A central irritant on the agenda is the Section 301 probe. New Delhi wants clear answers on Washington's proposed new tariffs under that investigation, which targets alleged overcapacity in sectors such as textiles and steel, before it puts its name to anything. "Whenever we finalise and sign the deal," Agrawal said, negotiators want clarity on the 301 proceedings folded in. India is also holding firm on its sensitive sectors \u2014 dairy, farmers and fishermen \u2014 which it has kept off the table in every recent agreement.

## A Deal Negotiated From Strength

Greer arrives at a moment when India can negotiate from a position of unusual confidence. Agrawal said merchandise exports rose 18 per cent year-on-year in May to $45.2 billion, up from $38.3 billion a year earlier \u2014 "amongst one of the highest monthly exports in merchandise that we have achieved thus far." India's trade deficit narrowed even as imports climbed, a sign that the export engine is running hot despite volatile energy prices and Middle East disruptions.

The longer arc is more striking still. India's overall exports have nearly doubled in 12 years, from $446 billion to $863 billion, while services exports \u2014 the software, back-office and consulting work that employs millions and underwrites much of the diaspora's prosperity \u2014 have tripled, from $142 billion to $420 billion. India has concluded nine trade agreements with 38 countries in the past five years, including recent deals with Britain and the European Union, giving its negotiators both leverage and a template.

## Why the Diaspora Is Watching

The visit also unfolds against real diplomatic friction. Ties have been strained by US tariffs, by President Trump's repeated and Indian-denied claims that he helped end last year's India-Pakistan conflict, and most recently by anger in India over the killing of three Indian civilian mariners by US forces in the Gulf of Oman. That a trade visit of this importance is proceeding regardless underscores how much both governments want the economic relationship to hold.

Trade and defence sit inside a wider architecture: the India-US COMPACT \u2014 Catalyzing Opportunities for Military Partnership, Accelerated Commerce and Technology \u2014 which Modi and Trump reviewed on the sidelines of the G7 summit in France, welcoming progress across defence, strategic technology, energy and trade. For the diaspora, the stakes are layered. A signed interim deal would lower costs for the Indian goods that fill desi grocery aisles and jewellery counters abroad, steady the IT-services relationship that employs so many Indian-origin professionals, and signal that the two largest democracies intend to keep building together. Greer's two days in Delhi will not settle everything. But for millions whose livelihoods straddle both countries, they are two days worth watching closely."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "Shipping containers at an Indian port; US Trade Representative Jamieson Greer arrives in New Delhi on June 22 to finalise an interim India-US trade deal"
    img_attribution = "Wikimedia Commons"

    # Prefer Greer's own photo
    person_img = fetch_wikipedia_person_image("Jamieson Greer")
    if person_img:
        img_url = person_img
        img_caption = "US Trade Representative Jamieson Greer, who arrives in New Delhi on June 22 for two days of talks to finalise an interim India-US trade agreement"
        img_attribution = "Wikimedia Commons"

    if not img_url:
        for q in ["India United States flags", "container ship port India export", "Nhava Sheva port India", "India US trade diplomacy"]:
            commons = fetch_wikimedia_commons_images(q)
            if commons:
                img_url = commons[0]["url"]
                t = commons[0]["title"].lower()
                if "flag" in t:
                    img_caption = "The flags of India and the United States; USTR Jamieson Greer arrives in New Delhi on June 22 to finalise an interim bilateral trade deal"
                elif "port" in t or "ship" in t or "container" in t:
                    img_caption = "Containers at an Indian port; India's merchandise exports rose 18% in May as it works to finalise an interim trade deal with the United States"
                break

    if not img_url:
        px = fetch_pexels_image("cargo container ship port export")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A container ship at port; India's exports rose 18% in May as USTR Greer arrives to finalise an interim India-US trade agreement"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "trade",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Hindu BusinessLine \u2014 India-US trade deal nears completion ahead of Jamieson Greer's India visit (USTR arrives evening June 22; engages Minister for Commerce and Industry June 23-24; Section 301; final touches to framework + larger BTA; India-US COMPACT review)",
            "The Indian Eye \u2014 USTR Jamieson Greer to visit India for trade talks on June 23-24 (Agrawal: May merchandise exports up 18% YoY to $45.2B vs $38.3B; overall exports doubled $446B\u2192$863B over 12 years; services tripled $142B\u2192$420B; nine FTAs with 38 countries in five years)",
            "Reuters \u2014 India's May trade gap narrows as exports rise; U.S. trade talks in focus (deficit narrowed to $28.21B; exports $45.2B; Greer June 23-24; India seeks clear answers on Section 301 tariffs; preferential tariff access sought; textiles/steel overcapacity probes)",
            "Reuters \u2014 India-US trade deal slashes tariffs, lifts exports and markets (Feb 6 framework: US tariffs on Indian goods cut to 18% from 50%; exporters say textiles, pharma, chemicals, footwear, jewellery, shrimp put on par with Vietnam/Bangladesh)",
            "Tripura Star News / PIB \u2014 PM Modi meets President Trump on margins of G7 Summit (COMPACT progress across defence, tech, energy, trade; instructed officials toward interim BTA; Greer visiting India next week)"
        ]),
        "diaspora_angle": "The interim India-US trade deal Greer is in Delhi to finalise would set the tariffs on the textiles, pharmaceuticals, jewellery and processed foods that fill desi shops abroad, steady the IT-services relationship that employs millions of Indian-origin professionals, and signal continued confidence in a partnership central to the diaspora's economic life.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India W vs South Africa W — T20 World Cup preview ──

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India W vs South Africa W — T20 WC preview")
    print("="*60)

    slug = "india-women-south-africa-t20-world-cup-old-trafford-preview-harmanpreet-wolvaardt-revenge-20260621"
    headline = "India's Women Have Won Everything So Far. South Africa Are the Test That Tells Us If It's Real."
    subheadline = "Unbeaten and top of their group, Harmanpreet Kaur's side meet South Africa at Old Trafford on Sunday \u2014 the same opponent that beat them 4-1 in a bruising bilateral series in April, and the first real measure of whether this World Cup run is built to last."

    body = """There is a difference between winning and being tested, and so far at this T20 World Cup, India's women have only done the first. On Sunday afternoon at Old Trafford in Manchester, that changes. Harmanpreet Kaur's side, unbeaten and sitting top of Group 1, face a South Africa team that knows exactly how to beat them \u2014 because it did so, repeatedly, only two months ago. For the thousands of Indian-origin fans who will fill the stands of one of cricket's most storied grounds, this is the match that turns a promising campaign into a serious one, or exposes its limits.

India arrive in ominous form. They opened with a 64-run dismantling of Pakistan at Edgbaston, then crushed the Netherlands by 95 runs at Headingley, a result that left them on top of the table with a net run rate of plus 3.975 \u2014 the kind of cushion that matters when semi-final places are decided on fractions. South Africa, by contrast, have split their two matches and sit at minus 1.097, which sharpens the stakes: a win on Sunday would all but secure India's place in the last four, while a defeat would throw the group wide open.

## The Ghost of April

What gives this fixture its edge is recent history. In April, India toured South Africa for a five-match T20 series and lost it 4-1. It was not a fluke. South Africa's batting, marshalled by the elegant Laura Wolvaardt, repeatedly outpaced India's, and their captain was named player of the series after a run of commanding innings. India won only the dead-rubber consolation. That tour is the uncomfortable subtext to everything on Sunday: India may be the form team of the tournament, but against this specific opponent, in the recent past, they were comprehensively second best.

The personnel carry the storyline. Wolvaardt is the leading run-scorer of this World Cup so far, with 438 runs at an average just shy of 49 \u2014 a player capable of batting India out of the contest on her own. India's answer is a top order in rhythm: captain Harmanpreet Kaur, with 301 tournament runs at 43, and the explosive opener Shafali Verma, whose 264 runs have come at a strike rate above 143. The contest within the contest may be India's young spinner Shree Charani, the tournament's joint-leading wicket-taker with 15, against a South African middle order that has the depth to punish anything loose.

## Old Trafford, and the Crowd That Comes With It

The setting matters too. Old Trafford has hosted some of the most emotionally charged India matches in England's cricketing memory, and a World Cup fixture on a Sunday afternoon will draw heavily from the enormous British-Indian community across Manchester, Leicester, Birmingham and London. England remains, after India itself, perhaps the most reliable away crowd women's cricket from the subcontinent can summon. For a sport still fighting for the attention and investment its men's game commands, a packed, partisan Old Trafford is its own kind of statement.

That backdrop has weight beyond the result. The women's game in India has been transformed in recent years by the Women's Premier League, by genuine television money and by the breakthrough of last year's 50-over World Cup triumph on home soil \u2014 a victory that turned players like Harmanpreet, Verma and Deepti Sharma into household names. A deep run at this tournament, in front of diaspora crowds, compounds that momentum. Defeat to a familiar nemesis would not undo it, but it would be a reminder of how thin the margins still are at the very top.

## What's at Stake

The tournament's shape is coming into focus. The semi-finals are scheduled for July 2 and 3, with the final at Lord's on July 5 \u2014 the home of cricket, and a stage that would lend any title an extra resonance. India's path there runs, in large part, through Sunday. Win, and they travel toward the knockouts as the team to beat, their one psychological question mark \u2014 South Africa \u2014 answered. Lose, and the April series suddenly looks less like an aberration and more like a pattern, with the pressure of expectation, always heavy on an Indian side, pressing harder.

For the diaspora watching from England, from living rooms in New Jersey and Toronto, and from a subcontinent where women's cricket has finally been given room to matter, the appeal is simple. This is the game where we find out what India's women are actually made of this summer. The toss is set for early afternoon UK time. By evening, the group will look very different \u2014 and so, perhaps, will the conversation about who wins this World Cup."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "Old Trafford Cricket Ground in Manchester, where India's women face South Africa in a Women's T20 World Cup group match on June 21, 2026"
    img_attribution = "Wikimedia Commons"

    for q in ["Old Trafford Cricket Ground Manchester", "Harmanpreet Kaur cricket", "India women cricket team", "women cricket match England"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "harmanpreet" in t:
                img_caption = "India captain Harmanpreet Kaur, whose side faces South Africa at Old Trafford in a Women's T20 World Cup group match on June 21, 2026"
            elif "old trafford" in t:
                img_caption = "Old Trafford Cricket Ground in Manchester, host of India's Women's T20 World Cup clash with South Africa on June 21, 2026"
            break

    if not img_url:
        px = fetch_pexels_image("cricket stadium match")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A cricket ground; India's women face South Africa in a Women's T20 World Cup group match at Old Trafford on June 21, 2026"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Sportradar (ICC T20 World Cup, Women 2026) \u2014 South Africa vs India, Old Trafford Cricket Ground, Manchester; Sunday June 21, 06:30 PDT / 13:30 UTC start; group round, status not_started at preview time",
            "Cricket World / Proteas Women \u2014 South Africa Women beat India Women by 23 runs to seal 4-1 T20I series victory (April 2026 bilateral series; Laura Wolvaardt Player of Match and Player of Series)",
            "ICC / tournament records \u2014 India W beat Pakistan by 64 runs at Edgbaston and Netherlands by 95 runs at Headingley; top of Group 1 (NRR +3.975); SA W 1-1 (NRR -1.097)",
            "Tournament statistics \u2014 Laura Wolvaardt leading run-scorer (438 at ~48.7); Harmanpreet Kaur 301 at 43; Shafali Verma 264 at SR 143+; Shree Charani joint-leading wicket-taker (15); semi-finals July 2-3, final at Lord's July 5"
        ]),
        "diaspora_angle": "A Sunday-afternoon World Cup fixture at Old Trafford will draw heavily on Britain's large Indian-origin community across Manchester, Leicester, Birmingham and London \u2014 and for diaspora fans from England to New Jersey to Toronto, India women's run, powered by the WPL and last year's home World Cup title, is a marker of how far the subcontinent's women's game has finally been allowed to rise.",
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
