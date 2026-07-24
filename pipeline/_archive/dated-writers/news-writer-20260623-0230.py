#!/usr/bin/env python3
"""
Videshi News Writer — June 23, 2026 (02:30 UTC run)
2 NEW articles (both fresh, distinct from the most recent news pieces):
  1. US waives Iran sanctions for 60 days after the first peace talks in
     Switzerland; oil resumes its slide, Hormuz tanker traffic picks up, and a
     roadmap to a permanent deal is set within 60 days. (geopolitics / energy)
  2. Foreign investors stage their biggest single-day buy of Indian stocks
     since February after a record $30.6bn exodus this year, as Mideast calm,
     cheaper oil and RBI rupee support revive overseas appetite. (economy /
     markets — strong NRI investment angle)
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


# ─── Article 1: US waives Iran sanctions / oil slides / Hormuz reopens ──────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: US waives Iran sanctions after first peace talks")
    print("="*60)

    slug = "us-waives-iran-sanctions-60-days-buergenstock-peace-talks-hormuz-tankers-oil-falls-india-20260623"
    headline = "America Just Lifted Iran's Oil Sanctions for 60 Days. For India, the Relief Is Already Floating Through Hormuz."
    subheadline = "After the first round of talks under a fragile peace deal, the US Treasury waived sanctions on Iran from Monday, oil resumed its slide below $80, and tankers began moving again through the world's most important oil chokepoint \u2014 the one through which two-thirds of India's crude flows."

    body = """The United States waived sanctions on Iran for 60 days from Monday, the first concrete step in a nascent peace deal, after negotiators meeting at a Swiss mountain resort agreed on a roadmap toward a permanent agreement within 60 days. For a few tense days over the weekend the week-old accord had looked like it might collapse, with Tehran declaring the Strait of Hormuz closed and President Donald Trump threatening to restart the war. By Monday the mood had flipped: tanker traffic through the strait picked up, and oil prices resumed their slide.

The US Treasury announced a waiver, running until August 21, that allows Tehran to sell oil and related products and to receive payment for them \u2014 the first of several steps envisaged under the agreement to give Iran economic relief. US Vice President JD Vance, who took part in the talks at the Qatari-owned Buergenstock resort, struck an upbeat tone, saying the two sides had "laid a very good foundation for a successful final deal." Iran's foreign ministry was more cautious, with a spokesman insisting Tehran had not yet discussed nuclear issues or made new commitments. Brent crude settled around 3% lower, slipping below $80 a barrel.

## Why This Lands So Squarely on India

For India, the world's third-largest oil importer, this is not a distant diplomatic story \u2014 it is the price of nearly everything. India buys close to 90% of the crude it burns from abroad, and roughly two-thirds of those imports sail through the Strait of Hormuz, the narrow waterway between Iran and Oman that the war had turned into a flashpoint. When Tehran declared the strait closed, every shipping calculation in New Delhi tightened; when traffic resumed and prices eased, the relief was immediate and concrete.

The mediators \u2014 Pakistan and Qatar \u2014 said the two sides also agreed to open a communications line to help ensure safe passage for commercial ships through Hormuz, precisely to avoid the kind of confrontation that has cost lives at sea. That matters intensely to India, whose sailors crew vessels on virtually every major route: Indian nationals make up about 12% of the global merchant-shipping workforce, roughly 300,000 people. Three Indian seafarers were killed in US strikes on tankers in the Gulf this month, and a separate fleet of India-bound ships \u2014 including vessels carrying fertiliser for the summer crop season \u2014 had been stranded in or near the strait. New Delhi confirmed on Monday that four cargo ships carrying urea, di-ammonium phosphate and sulphur had crossed Hormuz and were headed to Indian ports.

## A Deal That Is Still Fragile

The relief comes with heavy caveats. Vance said Tehran had agreed to allow nuclear inspectors back in and to set up mechanisms to handle frozen assets and manage ceasefires, and Trump posted that Iran would accept weapons inspections to ensure "nuclear honesty." But Iran's foreign ministry said no nuclear commitments had been made, and the two sides offered conflicting accounts of how Iran's unfrozen funds could be spent \u2014 Washington suggesting the money would flow to US farm goods, Tehran's central bank governor disputing any such obligation. Technical talks were due to continue through the week, and Trump warned that if Iran "doesn't live up to their agreement... I will do what I have to do."

The accord also reaches beyond Iran. It includes a mechanism to wind down fighting in Lebanon between Israel and Hezbollah, where officials reported the longest lull since the war began. Israel, which was not party to the deal and has refused to withdraw from Lebanon, agreed to a separate ceasefire on Friday.

## What It Means for the Diaspora

For the Indian diaspora, the chain of consequences is direct. Cheaper oil eases the import bill that drives India's inflation and the rupee, the currency in which millions of NRIs send remittances home and hold property and deposits. A calmer Gulf means safer waters for the hundreds of thousands of Indian seafarers \u2014 and for the families who have spent weeks watching strikes on commercial shipping. And the resumption of fertiliser and fuel cargoes through Hormuz protects the summer farming season that underpins food prices across the country the diaspora stays tethered to.

But the operative word is fragile. Sixty days is a clock, not a guarantee, and the relationship India is trying to navigate \u2014 deepening trade with Washington while protesting the deaths of its citizens at American hands \u2014 remains unsettled. For now, the tankers are moving and the price at the pump is falling. Whether that holds will be decided over the next two months, far from the ports of Mundra and Paradeep, but felt acutely there all the same."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "Strait of Hormuz tanker",
        "oil tanker Persian Gulf",
        "crude oil tanker ship sea",
        "Buergenstock resort Switzerland"
    ])
    img_caption = "An oil tanker in the Gulf; tanker traffic through the Strait of Hormuz resumed on June 22, 2026"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("oil tanker ship ocean")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "An oil tanker at sea; oil prices slid below $80 as the Strait of Hormuz reopened to shipping"

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
            "Reuters \u2014 US waives Iran sanctions after talks; Lebanon fighting abates (June 22, 2026): the United States waived sanctions on Iran for 60 days from Monday after the first talks under a nascent peace deal; the US Treasury announced a waiver until August 21 allowing Tehran to sell oil and receive payment; the two sides agreed a roadmap toward a permanent agreement within 60 days at the Qatari-owned Buergenstock resort, with mediators Pakistan and Qatar; tanker traffic through the Strait of Hormuz picked up and oil prices resumed their slide; VP JD Vance said they 'laid a very good foundation'; Iran's foreign ministry said no nuclear issues had yet been discussed; a mechanism to end fighting in Lebanon and a communications line for safe passage through Hormuz were agreed; oil settled 3% lower",
            "Reuters \u2014 Indian shares rise on Reliance, IT rebound; Mideast hopes lift sentiment (June 22, 2026): the first round of US-Iran talks ended with progress on a roadmap for a final deal within 60 days; Brent crude fell 1.9% to trade below $80 a barrel after Tehran's announcement it had closed the Strait of Hormuz and Trump's threats to resume attacks",
            "Reuters \u2014 India-bound fertilizer ships cross Hormuz, government says (June 22, 2026): four cargo ships carrying urea, di-ammonium phosphate and sulphur crossed the Strait of Hormuz last week headed to Krishnapatnam, Kakinada, Paradeep and Mundra ports; last week India said 16 India-bound ships carrying about 700,000 tons of fertiliser were stranded near the strait; India is one of the world's largest fertiliser importers and cumulative stock stands at 19.60 million metric tons",
            "The Indian EYE \u2014 Strait of Hormuz Crisis Poses New Test for India-US Ties: India confirmed three Indian seafarers died after a US strike on a commercial vessel in the Gulf of Oman; India supplies about 12% of the global merchant-shipping workforce, roughly 300,000 people"
        ]),
        "diaspora_angle": "India imports about 90% of its crude and routes two-thirds of it through the Strait of Hormuz, so a sanctions waiver that calms the Gulf, reopens tanker traffic and pushes oil below $80 directly eases the import bill, the rupee and inflation that shape NRI remittances and investments \u2014 while a safer strait protects the roughly 300,000 Indian seafarers who crew the world's shipping.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Foreign investors return to Indian equities ────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Foreign investors return to Indian stocks")
    print("="*60)

    slug = "foreign-investors-return-indian-equities-biggest-daily-buy-since-february-record-30-billion-exodus-nri-20260623"
    headline = "After Pulling a Record $30 Billion Out of India, Foreign Investors Just Made Their Biggest Bet Back in Months"
    subheadline = "Overseas funds bought more Indian stocks in a single session on Friday than on any day since early February, and the Sensex and Nifty logged a sixth gain in seven sessions \u2014 a turn that matters to every NRI with money in Indian markets."

    body = """For most of this year, the story of foreign money in India has been one long withdrawal. Overseas investors have yanked a record $30.6 billion out of Indian stocks since January, a steady drain that helped knock the market off its highs, pressured the rupee and rattled the diaspora's growing pile of India-linked savings. On Monday, for the first time in months, the tide looked like it might be turning.

Foreign portfolio investors bought $515.2 million of Indian equities on Friday \u2014 their largest single-day purchase since early February \u2014 and the buying carried sentiment into Monday's session. India's benchmark Nifty 50 rose 0.37% to 24,102.90 and the Sensex added 0.38% to 77,094.07, both logging their sixth gain in seven sessions. Thirteen of the 16 major sectors advanced, and the broader small-cap and mid-cap indices climbed alongside the blue chips.

## What Turned the Mood

Three things lined up. The first is the Middle East: the opening round of US-Iran peace talks ended with progress toward a roadmap for a final deal within 60 days, calming nerves after a weekend in which Tehran had declared the Strait of Hormuz closed and Washington threatened to resume strikes. With the immediate war risk easing, Brent crude fell back below $80 a barrel \u2014 a crucial relief for a country that imports almost all of its oil.

"If crude stays below $80 and the peace process holds, it improves earnings visibility and can help bring foreign investors back to Indian equities," said Rajesh Kothari, chief investment officer of AlfAccurate Advisors. The second driver was Reliance Industries, which rose 1.3% after its annual general meeting, with brokerages pointing to the IPO-bound Jio Platforms and the conglomerate's AI and new-energy bets as growth engines. The third was a rebound in IT stocks, which had tumbled 3.7% on Friday after a weak demand forecast from Accenture; the sector clawed back about 0.75%.

Helping the broader picture, government and central-bank steps to support the rupee have moderated the foreign outflows that defined the first half of the year. After months of selling, even one outsized day of buying is enough to shift the narrative on Dalal Street.

## A Story the Diaspora Owns a Piece Of

For non-resident Indians, this is not a spectator sport. The diaspora is an increasingly direct stakeholder in Indian equities. This year's Union Budget doubled the individual investment limit under the Portfolio Investment Scheme \u2014 the main route through which NRIs buy Indian shares \u2014 from 5% to 10%, and lifted the aggregate cap to 24%, an explicit bid to pull more overseas Indian savings into the market rather than leaving them as consumption-led remittances. India received about $135 billion in remittances in the last fiscal year, the most of any country, and policymakers want a larger slice of that channelled into capital formation.

That makes the foreign-flow story personal. When global funds flee, NRI portfolios and the rupee value of dollar investments both take the hit; when they return, the same holdings recover. The record $30.6 billion exodus has been a drag on returns all year, so any sign that the world's big investors are circling back is welcome news for diaspora investors watching their India allocations.

## What's Next

The caveats are the same ones hanging over the oil market. The US-Iran truce is fragile, technical talks are still under way, and a single strong day of foreign buying is not a trend. India's IT sector, the diaspora's bellwether, is still nursing the wounds of Accenture's warning and a three-year low hit last week. And the broader macro backdrop \u2014 a US trade deal still unsigned ahead of a July 24 tariff deadline, a hawkish Federal Reserve, an uneven monsoon \u2014 leaves plenty of room for the mood to sour again.

But for now the arrows are pointing up: oil down, the rupee steadier, the indices grinding higher and foreign money testing the water again. For the millions of NRIs who have quietly built a stake in India's stock market, Friday's buying was the first concrete hint in a long while that the smart money may be coming home too."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "Bombay Stock Exchange building Mumbai",
        "BSE building Dalal Street Mumbai",
        "National Stock Exchange India",
        "Mumbai financial district skyline"
    ])
    img_caption = "The Bombay Stock Exchange in Mumbai; foreign investors made their biggest single-day purchase of Indian stocks since February"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("stock market trading screen india")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A stock market display; the Sensex and Nifty logged a sixth gain in seven sessions as foreign buying returned"

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
            "Reuters \u2014 Indian shares rise on Reliance, IT rebound; Mideast hopes lift sentiment (June 22, 2026): Nifty 50 rose 0.37% to 24,102.90 and Sensex added 0.38% to 77,094.07, the sixth gain in seven sessions; foreign portfolio investors, who have offloaded a record $30.6 billion of Indian stocks year-to-date, bought $515.2 million of equities on Friday, their biggest daily purchase since early February; Brent crude fell 1.9% below $80; Reliance Industries rose 1.3% after its AGM; the IT index, which fell 3.7% on Friday after Accenture's weak forecast, rose about 0.75%; 13 of 16 major sectors gained; Rajesh Kothari of AlfAccurate Advisors quoted",
            "Reuters \u2014 US waives Iran sanctions after talks; Lebanon fighting abates (June 22, 2026): the first round of US-Iran talks ended with a roadmap toward a final deal within 60 days; oil prices resumed their slide and settled about 3% lower",
            "Mint \u2014 Budget 2026 positions diaspora capital as a growth lever, not just a remittance stream: the budget doubled the individual investment limit under the Portfolio Investment Scheme from 5% to 10% and raised the aggregate cap to 24% to deepen diaspora participation in equity markets; India received about $135 billion in remittances in FY25, the world's largest recipient, nearly 3.5% of GDP",
            "YourStory / CREDX startup roundup (June 22, 2026): Jio Platforms filed its DRHP ahead of Reliance's AGM as an IPO-bound business; Reliance brokerages cite Jio, AI and new-energy units as growth drivers"
        ]),
        "diaspora_angle": "NRIs are direct stakeholders in Indian equities \u2014 the 2026 budget doubled their Portfolio Investment Scheme limit to 10% and raised the aggregate cap to 24% \u2014 so a turn in foreign flows after a record $30.6 billion exodus directly affects the value of diaspora portfolios and the rupee in which they invest and remit.",
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
