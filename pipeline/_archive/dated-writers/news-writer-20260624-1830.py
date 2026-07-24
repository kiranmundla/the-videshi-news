#!/usr/bin/env python3
"""
Videshi News Writer — June 24, 2026 (18:30 UTC run)
2 NEW articles, distinct from all prior runs (dedup-checked against last 45 news):
  1. India-US interim trade deal: USTR Jamieson Greer's two-day Delhi talks with
     Piyush Goyal concluded Wednesday; both sides say they discussed "pathways"
     to an interim deal, made "substantial progress," and are "very, very close."
     This is the OUTCOME of the talks — distinct from the June 23 preview piece
     ("America's Top Trade Envoy Lands in Delhi Tuesday") which was a curtain-raiser.
  2. Navi Mumbai International Airport's first-ever international flight: Air India
     Express launches Navi Mumbai–Abu Dhabi direct service on July 15, the maiden
     overseas route from India's newest greenfield mega-airport. Distinct from the
     June 23 Adani Kutch-airport piece (different airport, different region).
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

UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
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
            return pick["url"], pick.get("title", "")
    return None, ""


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


# \u2500\u2500\u2500 Article 1: India-US interim trade deal nears as Greer talks conclude \u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India-US interim trade deal (Greer talks)")
    print("="*60)

    slug = "india-us-interim-trade-deal-greer-goyal-talks-pathways-very-close-diaspora-20260624"
    headline = "Trump's Trade Envoy Has Left Delhi. India Says the Two Sides Are Now Mapping the Way to a Deal."
    subheadline = "Two days of talks between US Trade Representative Jamieson Greer and Commerce Minister Piyush Goyal ended Wednesday with both governments calling it 'substantial progress' \u2014 and Washington saying the long-promised deal is 'very, very close.' What India wants is a tariff edge over its rivals before a July 24 clock runs out."

    body = """The man Donald Trump sent to close the deal has come and gone. US Trade Representative Jamieson Greer wrapped up two days of talks in New Delhi on Wednesday, and when his delegation pulled out of Vanijya Bhavan, both capitals struck the same careful, optimistic note: the two sides had discussed "pathways" to an interim trade agreement, made "substantial progress," and remained committed to a deal that is, in New Delhi's words, "balanced and commercially meaningful."

Washington went further. Bethany Poulos Morrison, a US deputy assistant secretary for South and Central Asian affairs, told an event in Delhi that the two countries are "very, very close" to concluding what she called a historic agreement. "This is going to open India's market of 1.4 billion to America's goods on terms that are reciprocal and mutually beneficial," she said, invoking "Mission 500" \u2014 the shared target of $500 billion in two-way trade by 2030.

## What Was on the Table

The talks were the most senior in-person push since Prime Minister Narendra Modi and President Trump met on June 17 on the sidelines of the G7 summit \u2014 their first meeting in more than a year. Greer met Goyal, India's commerce secretary Rajesh Agrawal, and Finance Minister Nirmala Sitharaman, who held her own discussions with the delegation. US Ambassador Sergio Gor, posting on X, called the trip a drive "toward finalizing a strong bilateral trade agreement that will unlock new economic opportunities for both countries."

The architecture has been in place since February, when the two sides reached an initial understanding: an 18% US tariff on Indian goods in exchange for New Delhi lowering its own trade barriers and buying more American products. At the time, 18% was a relative win \u2014 lower than the rates facing competitors such as Vietnam and Bangladesh. That edge is exactly what India is fighting to preserve. "We are trying to work out with the US how they will ensure that we will get a comparative advantage, so that our exporters can benefit," Goyal said this week.

## Why the Clock Matters

There is urgency baked into the calendar. Washington's temporary 10% tariff on trading partners expires on July 24, and Goyal has said he would be "the happiest person" if the first tranche of the deal is signed before then. "The faster, the better," he added. India is also seeking assurances that Washington will not slap on fresh tariffs once a deal is inked \u2014 a real worry given how the last agreement unravelled.

Because it did unravel, at least partly. The February understanding was thrown into doubt when the US Supreme Court invalidated Trump's sweeping global tariffs, forcing negotiators to rework the legal foundation. A separate US Section 301 investigation \u2014 probing alleged overcapacity and forced labour in Indian sectors such as textiles and steel \u2014 remains open and unresolved, a thorn that India has pushed back on by citing its vast domestic demand and population.

The negotiations have also unfolded against a darker backdrop. The deaths of three Indian sailors in attacks on commercial ships by the US Navy in the Gulf added a layer of diplomatic friction in recent weeks, a reminder that the trade track does not run in isolation from everything else straining the relationship.

## Why It Matters for the Diaspora

For the roughly 5.4 million people of Indian origin in the United States \u2014 and the businesses they run on both sides of the ocean \u2014 the shape of this deal is not abstract. A favourable tariff line keeps Indian-made goods competitive on American shelves, protecting the importers, distributors and retailers, many of them diaspora-owned, who move textiles, food, pharmaceuticals and engineering products into the US market. A bad outcome, or no deal at all before July 24, risks higher costs landing precisely on those small and mid-sized firms.

There is a larger stake, too. The deal's chapters on technology, digital trade and talent mobility touch the professional spine of the Indian-American story \u2014 the engineers, founders and IT workers whose careers straddle Silicon Valley and Bengaluru. The US embassy framed it plainly this week, calling the partnership a "win-win" that creates American manufacturing jobs while supporting "tech talent exchanges." After Delhi, Greer flew on to Uzbekistan. The signatures are not yet on paper, and Indian officials remain wary of stalled talks inviting fresh tariff threats. But for a diaspora that has watched the US-India relationship lurch between warmth and friction, "very, very close" is, for now, the most hopeful phrase on offer.
"""

    img_url = fetch_wikipedia_person_image("Piyush Goyal")
    img_attribution = "Wikimedia Commons"
    img_caption = "Commerce and Industry Minister Piyush Goyal, who led India's side of the two-day trade talks with US Trade Representative Jamieson Greer in New Delhi"

    if not img_url:
        img_url, _ = pick_commons([
            "Piyush Goyal minister",
            "Vanijya Bhavan New Delhi commerce ministry",
            "India United States trade meeting",
            "shipping container port India export"
        ])
        img_caption = "India and the United States are pushing to finalise an interim trade deal that would set tariffs on Indian exports"

    if not img_url:
        px = fetch_pexels_image("shipping container port trade")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "India is seeking a tariff edge over regional rivals as it races to conclude a trade deal with the US before a July deadline"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "trade-policy",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters (reuters.com, June 24 2026) \u2014 'India says it discussed pathways to interim trade deal with US': India and the United States have discussed pathways to conclude an interim trade deal, the Indian government said in a statement on Wednesday after talks between trade minister Piyush Goyal and USTR Jamieson Greer; Greer was in India for two-day talks seen as crucial to mending bilateral ties; the trip followed the first Modi-Trump meeting in over a year on June 17 at the G7 summit; both sides made 'substantial progress' and are committed to an agreement that is 'balanced and commercially meaningful'; an initial understanding was reached in February but uncertainty persists over a continuing US Section 301 probe; in February the two sides agreed to 18% tariffs on Indian goods in exchange for New Delhi lowering trade barriers and buying more American goods; after India, Greer travels to Uzbekistan.",
            "Reuters (reuters.com, June 22 2026) \u2014 'India seeks tariff advantage over peers in push to finalise US trade deal': New Delhi is pushing for a trade pact on terms better than those for other Asian economies; the death of three Indian sailors in attacks on commercial ships by the US Navy in the Gulf added to diplomatic tensions; New Delhi is seeking a competitive tariff edge over regional peers including ASEAN nations like Vietnam; Goyal said he would be 'happy' if a deal is finalised before July 24, when Washington's temporary 10% tariff on trading partners expires, adding 'the faster, the better'; India also seeks assurances that Washington won't levy new tariffs after the deal.",
            "The Indian EYE (theindianeye.com, June 24 2026) \u2014 'US expects to close trade deal with India': US Deputy Assistant Secretary in the Bureau of South and Central Asian Affairs Bethany Poulos Morrison said Washington is 'very, very close' to concluding the trade agreement with India; a delegation led by USTR Jamieson Greer left Vanijya Bhawan in New Delhi on Wednesday after meeting Indian negotiators; Finance Minister Nirmala Sitharaman held discussions with the delegation; Morrison said the agreement would open India's market of 1.4 billion to American goods on 'reciprocal and mutually beneficial' terms, referencing 'Mission 500' \u2014 $500 billion in trade by 2030.",
            "The Indian EYE (theindianeye.com, June 24 2026) \u2014 'India welcomes US Trade Representative Greer': US Ambassador to India Sergio Gor said ongoing discussions will pave the path toward finalisation of the trade deal; Gor posted on X that finalising the bilateral trade agreement will 'unlock new economic opportunities for both countries and significantly deepen the US-India economic partnership'; Greer met Goyal at Vanijay Bhavan to discuss an interim deal and the broader Bilateral Trade Agreement (BTA), accompanied by Ambassador Gor and a US trade delegation.",
            "Bloomberg Law (news.bloomberglaw.com, June 24 2026) \u2014 'US Trade Chief Greer in India to Resolve Trade Pact Hurdles': USTR Jamieson Greer and Indian officials stepped up efforts to resolve remaining differences holding up an interim trade agreement, with talks extending into Wednesday; the US is India's largest trading partner and export market, while Washington sees deeper economic engagement with New Delhi as strategically important.",
            "Livemint (livemint.com, June 22 2026) \u2014 'US trade chief to visit India for interim deal discussions': discussions focus on implementing the US-India joint statement and an interim trade agreement within the broader BTA framework; Goyal said he would be 'the happiest person' if the first tranche is signed before July 24; the proposed deal is likely to cover preferential tariffs, rules of origin and investment provisions, with both countries also engaged on defence, critical minerals and investment."
        ]),
        "diaspora_angle": "For the millions of Indian-Americans and the diaspora-run importers, distributors and tech firms that straddle both economies, the tariff line in this deal decides whether Indian-made goods stay competitive on US shelves and whether the talent-mobility and digital-trade chapters ease the careers of engineers and founders working across Silicon Valley and India \u2014 with a July 24 deadline raising the stakes of getting it done.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: Navi Mumbai airport's first international flight (Abu Dhabi) \u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Navi Mumbai airport first international flight")
    print("="*60)

    slug = "navi-mumbai-airport-first-international-flight-abu-dhabi-air-india-express-july-15-diaspora-20260624"
    headline = "India's Newest Mega-Airport Is About to Send Its First Plane Abroad. The Destination Is Abu Dhabi."
    subheadline = "On July 15, Air India Express will fly Navi Mumbai International Airport's maiden international service to Abu Dhabi \u2014 the moment a greenfield giant meant to relieve Mumbai's choked skies joins the global map, and a new door home for the Gulf's vast Indian workforce."

    body = """India's newest mega-airport is about to grow up. On July 15, Air India Express will operate the first-ever international passenger flight out of Navi Mumbai International Airport (NMIA), a direct service to Abu Dhabi's Zayed International Airport. It is a milestone moment for a greenfield project built to ease the strain on Mumbai's saturated aviation system \u2014 and the day NMIA stops being a domestic-only airport and joins the global map.

The choice of Abu Dhabi as the inaugural overseas destination is no accident. The United Arab Emirates is consistently one of the single largest international destinations for Indian travellers, a corridor thickened by decades of employment, tourism, education and family ties. Western India, in particular, sends an enormous volume of outbound traffic toward the Gulf, and Abu Dhabi functions as a global transit hub, linking onward to Europe, North America and Africa.

## A Phased, Demand-Driven Start

Air India Express is opening the route cautiously. The Navi Mumbai\u2013Abu Dhabi service will begin with two flights a week, on Wednesdays and Fridays, before stepping up to three weekly flights from July 29, with a Sunday frequency planned for a later phase. The schedule has been built around early-morning departures designed to feed Abu Dhabi's international transit network and keep aircraft efficiently utilised.

The international launch is only one piece of a broader build-out. Air India Express plans to operate roughly 30 weekly flights from Navi Mumbai, connecting it not just to Abu Dhabi but to major Indian cities including Bengaluru and Delhi. That blend of international and domestic growth, scaled simultaneously, signals a phased network strategy rather than a single showpiece route.

## The Airport Behind the Headline

Navi Mumbai International Airport has been a long time coming. Operated under Adani Group stewardship with a minority stake held by the state planning body CIDCO, the airport was inaugurated in October 2024 and began domestic passenger operations in December 2025. In the months since, it has ramped quickly \u2014 already handling around 20,000 passengers a day, with projections targeting some 50,000 daily movements by year-end.

Its strategic purpose is structural. Mumbai's existing Chhatrapati Shivaji Maharaj International Airport has long run up against capacity limits, and NMIA is designed less as a competitor than as a pressure valve, redistributing the Mumbai Metropolitan Region's aviation demand across a two-airport system. For residents of Navi Mumbai, Thane and Raigad, the new international service also means shorter drives and easier access to overseas travel than the trek to the older airport across the bay.

The launch lands amid a wider surge in India-UAE air links. Just days after the Navi Mumbai announcement, Air India unveiled first-ever direct flights from Guwahati in the northeast to Abu Dhabi and Dubai, part of a steady thickening of one of the world's busiest international travel corridors.

## Why It Matters for the Diaspora

For the millions of Indians living and working across the Gulf \u2014 the UAE alone is home to one of the largest Indian expatriate communities anywhere \u2014 a new direct route is far more than a line on a timetable. It is another way home. Gulf-based workers, who send back a substantial share of India's record remittance inflows, now gain an additional gateway into the Mumbai region without funnelling through the older, congested airport, cutting transfer hassle for families travelling with children, elderly parents or heavy luggage on the annual journey back.

There is an economic dimension, too. NRIs in the Gulf are among the most important investors in western India's property and business markets, and easier, faster connectivity tends to deepen those ties \u2014 more frequent visits, more in-person deal-making, more movement of people and money along the Mumbai-to-Abu Dhabi axis. As NMIA scales toward its 50,000-passenger-a-day ambition and adds destinations, the airport is positioning itself as a new hub for exactly the kind of cross-border, two-homes life that defines the modern Indian diaspora. The first flight to Abu Dhabi is just the opening gate.
"""

    img_url, _ = pick_commons([
        "Navi Mumbai International Airport",
        "Air India Express aircraft Boeing 737",
        "Air India Express airplane",
        "Zayed International Airport Abu Dhabi terminal"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "An Air India Express aircraft; the airline will operate Navi Mumbai International Airport's first international flight, to Abu Dhabi, on July 15"

    if not img_url:
        px = fetch_pexels_image("airport terminal airplane departure")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Navi Mumbai International Airport launches its first overseas route, to Abu Dhabi, on July 15"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-travel",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Inshorts (inshorts.com, June 23 2026) \u2014 'Air India Express to launch 1st foreign flight from Navi Mumbai': Air India Express will launch Navi Mumbai International Airport's first international passenger flight on July 15 with a direct service to Abu Dhabi; the route marks the beginning of overseas operations from the airport, which opened in December 2025; the launch is expected to boost international connectivity and ease pressure on Mumbai's existing airport.",
            "Travel And Leisure Asia (travelandleisureasia.com, June 22 2026) \u2014 'Air India Express To Start Direct Flights From Navi Mumbai To Abu Dhabi': the new direct flights will operate twice a week on Wednesdays and Fridays from July 15, increasing to three weekly flights from July 29; these will be the first international passenger flights from Navi Mumbai International Airport; the route will reduce travel time and benefit the Indian diaspora residing in the Gulf region.",
            "Travel And Tour World (travelandtourworld.com, June 22 2026) \u2014 'Navi Mumbai Sees 20,000 Daily Passengers Shift as Air India Express Launches Abu Dhabi Flights on July 15': the airport, operated under Adani Group stewardship with a minority stake held by CIDCO, was opened in October 2024 and began domestic operations in December 2025; it is already handling around 20,000 passengers daily, with projections targeting 50,000 daily movements by year-end; from Abu Dhabi, passengers gain access to Europe, North America and Africa through onward networks; NMIA serves as a pressure valve for Mumbai's saturated airspace.",
            "Travel And Tour World (travelandtourworld.com, June 2026) \u2014 'Air India Express ... Abu Dhabi\u2013Navi Mumbai Direct Flights': the service begins mid-July 2026 with two weekly flights, rising to three from end-July; Navi Mumbai to Abu Dhabi operates as an early-morning departure on Wednesday and Friday, with Sunday added in a later phase; Abu Dhabi functions as a major global transit hub linking Asia, Europe, Africa and the Americas; the route reinforces strengthening India-UAE air connectivity.",
            "Curly Tales (curlytales.com, June 22 2026) \u2014 'Come July, Air India Express To Launch Direct Abu Dhabi Flights From Navi Mumbai International Airport': from July 15, Air India Express will launch direct flights between Navi Mumbai International Airport and Abu Dhabi's Zayed International Airport, giving Mumbai Metropolitan region passengers an additional gateway to the UAE capital and Indian expats another route home; the service starts twice weekly (Wed and Fri), rising to three from July 29, with Sunday flights to be added later; Air India Express will operate around 30 weekly flights from NMIA, also serving Bengaluru and Delhi.",
            "Curly Tales (curlytales.com, June 23 2026) \u2014 'Air India To Launch First-Ever Direct Flights From Guwahati To Abu Dhabi And Dubai': days after the Navi Mumbai announcement, Air India unveiled first-ever direct routes from Guwahati to Abu Dhabi and Dubai, part of steadily expanding India-UAE air links; the Navi Mumbai\u2013Abu Dhabi service from July 15 made Abu Dhabi the first international destination linked to Mumbai's newest airport."
        ]),
        "diaspora_angle": "For the Gulf's vast Indian workforce \u2014 the UAE hosts one of the world's largest Indian expatriate communities and a major source of India's record remittances \u2014 Navi Mumbai's first international flight opens another, less-congested gateway home and is set to deepen the Mumbai-to-Abu Dhabi ties of investment, family travel and business that define modern diaspora life.",
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
