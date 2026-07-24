#!/usr/bin/env python3
"""
Videshi News Writer — June 24, 2026 (00:30 UTC run)
2 NEW articles, both fresh & distinct from prior runs (which covered DC Circuit
expedited removal, Sensex 893-pt fall, India skilled-migration #1, UK-India Week
Warwick, CDSCO drug quality, Adani Mundra airport, study-abroad slowdown, Anil
Menon ISS, July visa bulletin, $750 expedited visa, CUET, FCRA, Russian crude,
NSE IPO, India-China normalising, PMI, SpaceX wipeout, NEET re-exam, Iran
sanctions lift, FII return, USTR trade talks, UK PM Starmer resigns, Documented
Dreamers, F-1 duration of status, USCIS citizenship fee, Apache/M777 FMS, RBI
NRI deposits, Tata Electronics breach):
  1. US Senate passes War Powers resolution directing Trump to halt the Iran
     war — first time BOTH chambers have done so since 1973. Symbolic but a
     real rebuke; matters to a diaspora that has watched the Gulf war whipsaw
     oil, flights and the safety of 18,000+ Indians stranded at sea. (politics
     — diaspora-stake angle)
  2. India-Japan summit moves to New Delhi as Japan PM Takaichi's first India
     visit (July 1-3) drops the planned Guwahati venue. 50 Japanese business
     leaders (Suzuki, Itochu, Toyota Tsusho) in tow; semiconductors, critical
     minerals and talent mobility on the table. (diplomacy — diaspora-economy
     angle)
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


# ─── Article 1: Senate passes War Powers resolution on Iran ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Senate passes War Powers resolution rebuking Trump on Iran")
    print("="*60)

    slug = "us-senate-war-powers-resolution-halt-iran-war-rebuke-trump-diaspora-20260624"
    headline = "For the First Time Since 1973, Congress Has Told a President to End a War. The War Is With Iran."
    subheadline = "The US Senate voted 50-48 on Tuesday to direct Donald Trump to pull American forces out of the conflict with Iran \u2014 the first time both chambers have passed such a resolution since the War Powers Act became law. It is likely symbolic. But for a diaspora that watched this war whipsaw oil prices, flights home and the safety of thousands of Indians in the Gulf, the vote is a signal worth reading."

    body = """The United States Senate did something on Tuesday that Congress has not done in more than half a century: it formally told a sitting president to get American forces out of a war. The 50-48 vote directed President Donald Trump to halt US military action against Iran, and because the House of Representatives passed the same measure earlier this month, it marked the first time since the War Powers Resolution became law in 1973 that both chambers have ordered a president to withdraw troops from hostilities.

The resolution is, by most readings, symbolic. But the symbolism is loud. For the better part of a year, Trump enjoyed near-unanimous backing from his own party. On Tuesday, four Republican senators \u2014 Rand Paul, Susan Collins, Lisa Murkowski and Bill Cassidy \u2014 crossed the aisle to vote with Democrats, while Democratic Senator John Fetterman broke the other way. The absences of two Republicans, Mitch McConnell and Dave McCormick, helped tip the count. It was the tenth time the Senate has voted on an Iran war-powers measure this year, and the first to pass.

## What the Vote Does, and Doesn't, Do

Under the 1973 War Powers Act, this kind of concurrent resolution does not go to the White House for the president's signature, and it does not, on its own, carry the force of law. The Trump administration was quick to say so. A White House official dismissed the vote as having "no significance," argued that concurrent resolutions "have no force of law," and noted that, in the administration's telling, hostilities already ended with a ceasefire in April. The White House has also maintained that the measure is unconstitutional.

Legal scholars say it is not so simple. "The executive branch will likely ignore it on constitutional grounds, and it's not clear who might have standing to sue to enforce it," said Scott Anderson of the Brookings Institution. In other words, the resolution's real weight is political, not legal: it is Congress putting on record that the war lacks support, and that the language could bite if fighting resumes.

## A Conflict That Reached Into Diaspora Lives

For Indians abroad, this is not an abstract Washington power struggle. The war that began on February 28 sent a tremor through the entire diaspora ecosystem. Oil spiked above $126 a barrel at its peak before collapsing to around $77 as tensions eased \u2014 a swing that moved everything from airfares on the India routes to the fuel-import bill that shapes the rupee. When the Strait of Hormuz was threatened, shipping through one of the world's most important oil chokepoints was thrown into doubt, and with it the livelihoods of the millions of Indians who live and work across the Gulf.

The human stakes were starkest at sea. In recent weeks, nearly 18,000 Indian seafarers were reported trapped aboard vessels in Gulf waters as the conflict disrupted maritime traffic, and at least three were confirmed dead. India also flew roughly 1,700 of its citizens out of the war zone in an evacuation operation that recalled earlier crisis airlifts. For families in Kerala, Gujarat, Punjab and beyond with relatives in the region, the question of whether this war winds down or flares again is intensely personal.

## Why a Symbolic Vote Still Matters

The diaspora has reason to track the politics closely. A war that drags on keeps oil volatile, keeps the rupee under pressure, and keeps Gulf-based workers exposed. A war that genuinely ends \u2014 which is what the Senate is pushing for \u2014 stabilises all three. The administration says US and Iranian negotiators are meeting in Switzerland to finalise terms under which Tehran would wind down its nuclear programme in exchange for sanctions relief, the unfreezing of assets and a Gulf-financed reconstruction fund. Trump, for his part, has warned there will be "no deal without nuclear inspections," and has threatened to cancel meetings if UN inspectors are denied access.

That is the tension the Senate vote sits inside. Congress is signalling that the appetite for open-ended military action is gone, even within Trump's own party, while the White House negotiates from a position it insists is unconstrained by the resolution. India, which welcomed the earlier US-Iran memorandum of understanding even as its own security establishment warned of "emerging threats," is watching a process on which a great deal of its energy security and the safety of its overseas citizens depends.

## What's Next

The resolution's immediate practical effect is uncertain, given that the administration says the fighting has already paused. Its lasting significance may be as a marker: the moment a restive Congress, ahead of November's midterm elections, drew a line under an unpopular war. A Reuters/Ipsos poll released on Tuesday found just one in four Americans believe the war was worth its costs, and a majority doubt any truce will hold. For the diaspora, the takeaway is less about the legal mechanics than the direction of travel \u2014 toward a settlement that, if it sticks, would steady the oil prices, the currency and the Gulf jobs on which so many Indian families quietly depend."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: US Capitol / Senate chamber. Institution, not a single named person.
    img_url, ctitle = pick_commons([
        "United States Senate chamber",
        "United States Capitol building Washington",
        "United States Senate floor",
        "US Capitol dome",
        "United States Congress building"
    ])
    img_caption = "The US Senate; lawmakers voted 50-48 to direct President Trump to halt military action against Iran"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("united states capitol building washington")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The US Capitol; the Senate passed a resolution directing Trump to end the war with Iran"

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
            "Reuters (reuters.com, June 23-24, 2026) \u2014 'US Senate joins House in voting to halt Iran war, rebuking Trump': the Senate voted 50-48 in favour of a war powers resolution that passed the House early this month; first time since the 1973 War Powers Act that both chambers have directed a president to remove forces from hostilities; the conflict began February 28; four Republicans (Rand Paul, Susan Collins, Lisa Murkowski, Bill Cassidy) joined all but one Democrat, while Sen. John Fetterman voted against; two Republicans (Mitch McConnell, Dave McCormick) did not vote; Reuters/Ipsos poll found one in four Americans believe the war was worth its costs; quote from Scott Anderson of the Brookings Institution that the executive branch will likely ignore it on constitutional grounds.",
            "CNN (cnn.com, June 23, 2026) \u2014 'Senate votes to limit Trump's Iran war powers in rare rebuke': final tally 50-48; the measure is a concurrent resolution that does not require the president's signature and does not carry the force of law; a White House official said it 'has no significance' and that hostilities terminated with a ceasefire on April 7; tenth time the Senate has voted on an Iran war-powers measure this year.",
            "New York Post (nypost.com, June 23, 2026) \u2014 'Senate passes anti-Iran war resolution with 4 Republican votes': first time Congress has passed a resolution directing a president to end an undeclared war since the 1973 War Powers Resolution; US and Iranian negotiators meeting in Switzerland to finalise Tehran's abandonment of its nuclear program in exchange for sanctions relief, unfreezing of assets and a $300 billion Gulf Arab-financed reconstruction fund; House tally was 215-208.",
            "Background \u2014 India/diaspora exposure (June 2026): the Iran war sent Brent crude above $126 a barrel before it fell ~39% to around $77 as tensions eased and the Strait of Hormuz reopened; nearly 18,000 Indian seafarers were reported trapped aboard vessels in the Gulf with at least three confirmed dead; India evacuated roughly 1,700 citizens from the war zone; India welcomed the US-Iran MoU while NSA Ajit Doval warned of 'emerging threats'; Trump warned of 'no deal without nuclear inspections.'"
        ]),
        "diaspora_angle": "The war this resolution targets reached deep into diaspora life \u2014 whipsawing oil prices and the rupee, threatening shipping through the Strait of Hormuz, leaving nearly 18,000 Indian seafarers trapped in Gulf waters and forcing the evacuation of 1,700 citizens \u2014 so a bipartisan Senate signal that Washington wants the conflict to end speaks directly to the energy security, currency stability and Gulf livelihoods that millions of Indian families abroad depend on.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: India-Japan summit moves to Delhi for Takaichi's first visit ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India-Japan summit moves to Delhi; Takaichi's first visit")
    print("="*60)

    slug = "india-japan-summit-delhi-takaichi-first-visit-guwahati-dropped-semiconductors-20260624"
    headline = "Japan's New PM Makes Her First India Trip Next Week \u2014 With 50 Company Bosses and a Shopping List of Chips"
    subheadline = "Sanae Takaichi's debut visit to India from July 1-3 will now be held in New Delhi after a planned summit in Guwahati was shelved over a tight schedule. Behind the venue shuffle sits a far bigger story: a Japanese business armada and an India-Japan agenda built around semiconductors, critical minerals and the movement of skilled people \u2014 all of which run straight through the diaspora."

    body = """Japanese Prime Minister Sanae Takaichi will make her first official visit to India next week, from July 1 to 3, in a trip that has quietly become one of the more consequential diplomatic engagements of the summer. The headline change is logistical: the annual India-Japan summit, which Assam had hoped to host in Guwahati, will now be held in New Delhi. The substance, however, is anything but a footnote.

For days, Assam Chief Minister Himanta Biswa Sarma had teased the arrival of a "powerful global leader" and spoke of the "possibility" of Takaichi holding summit-level talks with Prime Minister Narendra Modi in Guwahati on July 1. Sources now say the visit will take place in the capital instead. "Given PM Takaichi's domestic commitments, the window between her proposed arrival in India and her departure is quite tight," officials said, citing the "additional logistical issues connected to a visit outside the capital." Guwahati had been offered to the Japanese side, but the calendar won.

## A Business Delegation, Not Just a State Visit

What makes this trip unusual is who is coming with her. Takaichi will be accompanied by leaders from more than 50 Japanese companies and organisations \u2014 a roster that, according to a Nikkei report, includes Suzuki Motor President Toshihiro Suzuki and senior executives from the trading houses Itochu and Toyota Tsusho, Toyota's trading arm. Japanese small and medium enterprises and startups are expected to join an Indo-Japanese business forum running alongside the summit. The delegation's focus, by all accounts, is squarely on investment opportunities, industrial cooperation and the kind of supply-chain partnerships that survive geopolitical weather.

This is Takaichi's first trip to India since she took office in October 2025, and it follows a period of unusually warm contact at the top. Modi met her in France last week on the sidelines of the G7, where he described a "great interaction," and the two have now met several times in eight months, including at the G20 in South Africa. The summit builds on the 10-year roadmap and defence framework signed during Modi's visit to Japan in August 2025.

## Chips, Minerals and the Northeast Tilt

The economic core of the relationship is what the two governments call "economic security" \u2014 a basket that spans semiconductors, critical minerals, artificial intelligence, emerging technologies and telecommunications. Even with the summit moving to Delhi, the symbolism of the originally proposed Guwahati venue tells you where the partnership is heading. Assam is fast emerging as a hub for semiconductor production, and Japan has long been a key partner in India's "Act East" push to deepen ties across the northeast and into Southeast Asia. Part of Japan's "Free and Open Indo-Pacific" vision involves an industrial corridor linking the Bay of Bengal to northeastern India, a project both governments are now trying to accelerate.

The two sides are also expected to launch joint efforts to secure supply chains for critical goods \u2014 telecommunications equipment, pharmaceuticals, critical minerals, semiconductors and clean energy \u2014 and to expand defence cooperation, including joint military exercises and collaboration on naval technology. In a world of fragmenting supply chains and a rising China, a democratic India and a democratic Japan pooling industrial muscle is a strategic statement as much as a commercial one.

## Why the Diaspora Should Care

For the Indian diaspora, the most direct thread is talent mobility, which has featured prominently in recent Modi-Takaichi conversations. As Japan races to build out its semiconductor and advanced-manufacturing base while contending with a shrinking, ageing workforce, it has been steadily opening doors to skilled Indian engineers, technicians and care workers. A summit that deepens the India-Japan technology partnership tends to widen those doors further \u2014 creating a new destination for diaspora professionals beyond the well-trodden US, UK, Canada and Gulf routes.

There is a second, subtler stake. Japanese investment flowing into Indian semiconductor and clean-energy projects \u2014 much of it likely to land in states with large emigrant populations \u2014 strengthens the home-country economy that the diaspora remains tethered to through remittances, family ties and, increasingly, return migration. When Suzuki, Itochu and Toyota Tsusho executives sit down in New Delhi next week, the deals they sketch out will, over time, shape where the next generation of Indian engineers chooses to build a career.

## What's Next

The summit is scheduled for July 1-3, with the Indo-Japanese business forum and a slate of agreements on economic security, defence and connectivity expected to follow. For Modi, it is a chance to lock in continuity with a new Japanese leadership; for Takaichi, an early test of a relationship her predecessors invested in heavily. And for a diaspora that has spent the last decade watching India court the West, it is a reminder that some of the most important doors \u2014 for jobs, for investment, for the future \u2014 are opening to the east."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Person article: Takaichi. Wikipedia FIRST per rules.
    img_url = fetch_wikipedia_person_image("Sanae Takaichi")
    img_caption = "Japanese Prime Minister Sanae Takaichi, who makes her first official visit to India from July 1-3"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        img_url, ctitle = pick_commons([
            "Sanae Takaichi", "Narendra Modi Japan", "India Japan flags summit"
        ])

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diplomacy",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "IndiaPost / PTI (indiapost.com, June 23-24, 2026) \u2014 'Japan PM Takaichi Visit likely To Be Held In New Delhi In July': Takaichi expected to make her first official India visit July 1-3; due to 'logistical issues' the visit likely to be held in New Delhi rather than Guwahati, which had been offered to the Japanese side; sources cited PM Takaichi's domestic commitments and a tight window; Assam CM Himanta Biswa Sarma had posted on X about the 'possibility' of a Guwahati summit on July 1; she will be accompanied by leaders of over 50 Japanese companies per a June 18 Nikkei report; NHK reported the leaders will discuss security and economy cooperation under the Japan-India joint vision.",
            "The Economic Times / Europe Says wire (June 2026) \u2014 'Japan Inc follows PM Takaichi to India, with chips and investments on the agenda': summit between Modi and Takaichi scheduled July 1-3; delegation of ~50 business leaders including executives from Suzuki, Itochu and Toyota Tsusho; Japanese SMEs and startups to join an Indo-Japanese business forum; Ahmedabad had been the only Indian city outside New Delhi to host the summit; Assam emerging as a semiconductor hub; 59 Japanese business establishments operated in Assam as of 2024.",
            "SME Times / IANS (smetimes.in, June 22, 2026) \u2014 'Japan PM Sanae Takaichi, 50 top business leaders to visit India next month': first India visit since Takaichi took office October 2025; focus on investment, industrial cooperation and supply-chain partnerships; economic security covering semiconductors, critical minerals, AI, emerging technologies and ICT a key element of the partnership; joint initiative to secure supply chains for telecom, pharmaceuticals, critical minerals, semiconductors and clean energy; expanded joint military exercises and naval-technology collaboration.",
            "Background \u2014 India-Japan ties (2025-26): builds on a 10-year economic roadmap and defence framework signed during Modi's August 2025 Japan visit; Modi met Takaichi in France on the G7 sidelines last week ('great interaction') and previously at the G20 in South Africa; Japan's 'Free and Open Indo-Pacific' includes an industrial corridor linking the Bay of Bengal to northeastern India under India's 'Act East' policy."
        ]),
        "diaspora_angle": "Japan, racing to build out semiconductors and advanced manufacturing while its own workforce shrinks, has been opening doors to skilled Indian engineers, technicians and care workers \u2014 so a summit that deepens India-Japan tech, talent-mobility and supply-chain ties opens a fresh destination for diaspora professionals beyond the usual US/UK/Canada/Gulf routes, while Japanese investment into Indian chip and clean-energy projects strengthens the home economy that NRIs stay tethered to through remittances and return migration.",
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
