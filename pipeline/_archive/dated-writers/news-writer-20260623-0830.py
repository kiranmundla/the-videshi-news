#!/usr/bin/env python3
"""
Videshi News Writer — June 23, 2026 (08:30 UTC run)
2 NEW articles (both fresh, distinct from prior runs which covered SpaceX,
NEET re-exam, Iran sanctions/oil, foreign-investor return, USTR Delhi trade,
China normalisation, PMI/business confidence, RBI NRI deposits, Jio IPO):
  1. India pivots hard to Russian crude and coal to cushion the Iran-war
     energy shock — Russian oil set for a record ~2.55m bpd in June, nearly
     half of all imports, even after the US let its Russia waiver lapse.
     (economy/energy — diaspora fuel-cost, remittance and geopolitics angle)
  2. India's NSE files for a ~Rs 30,000-crore IPO — set to be the largest in
     the country's history, valuing the world's busiest derivatives exchange
     near $57bn; a pure offer-for-sale letting global funds (Temasek, CPPIB)
     and Indian institutions cash out. (markets — NRI investor angle)
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


# ─── Article 1: India pivots to Russian crude and coal after Iran war ───────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India pivots to Russian crude and coal")
    print("="*60)

    slug = "india-pivots-russian-crude-coal-record-imports-iran-war-hormuz-energy-diaspora-20260623"
    headline = "India Is Buying More Russian Oil Than Ever Before \u2014 Even After Washington Pulled the Permission Slip"
    subheadline = "Russian crude is set to hit a record of around 2.55 million barrels a day in June, close to half of everything India imports, as the Iran war and the scramble around the Strait of Hormuz push the world's third-largest oil buyer back to Moscow's discounted barrels \u2014 with consequences that reach the diaspora's fuel bills, flight fares and remittances."

    body = """India has swung hard back toward Russian crude oil and coal to cushion the energy shock from the Iran war, with imports of Moscow's oil now set to reach the highest monthly level the country has ever recorded. According to vessel-tracking data compiled by the commodity-analytics firm Kpler, India's arrivals of Russian crude are on course for roughly 2.55 million barrels per day in June \u2014 up from 2.13 million bpd in May and above the previous record of about 2.2 million bpd set in May 2023. By some preliminary counts, Russian barrels have accounted for as much as 53% of all Indian oil imports this month.

That is a dramatic reordering of where India gets its energy. Russia's share of India's total crude imports \u2014 running at about 5.29 million bpd in June \u2014 has climbed to just under half, from an average of around 23% in the three months before the war began on February 28, when the United States and Israel launched their aerial campaign against Iran. Saudi Arabia, by contrast, has been squeezed to the margins: Kpler pegs Indian imports from the kingdom at around 349,000 bpd in June, down sharply from roughly 832,000 bpd before the conflict.

## How the War Rewired India's Oil Map

The pivot was set in motion when Iran effectively closed the Strait of Hormuz \u2014 the narrow waterway that normally carries about a fifth of the world's oil and gas \u2014 in response to the U.S. and Israeli strikes. With Gulf flows disrupted and prices spiking, Washington quietly waived sanctions on buying Russian crude to keep global supply flowing. India's refiners, long comfortable with discounted Russian grades, seized the opening. They also widened the net beyond Russia: imports from the UAE ran near a record at around 636,000 bpd, Venezuela climbed to become India's fourth-largest supplier at roughly 209,000 bpd, and refiners pulled extra cargoes from Brazil, Nigeria and Angola.

Here is the twist that makes this more than a wartime blip: the U.S. let its waiver on Russian oil lapse on June 17 without renewing it, even as it announced its memorandum of understanding with Iran. In theory, that should nudge India back toward Middle Eastern crude now that Hormuz is reopening and tankers are moving again. In practice, analysts expect Russian oil to stay a "cornerstone" of India's import basket. "Regardless of whether the US waiver is extended, we expect India's imports of Russian crude to remain robust," Sumit Ritolia of Kpler said, citing the persistent discounts and steady refinery demand that first drew India to Moscow's barrels in 2022.

## Why the Diaspora Should Care

For the diaspora, this is not an abstract commodities story \u2014 it sits underneath several things they feel directly. Cheaper crude, whether discounted Russian oil or the broad slide in prices after the Iran de-escalation, is what keeps a lid on India's fuel costs, its import bill and ultimately the rupee that so many NRIs send money into. A steadier import bill helps cushion the currency that determines how far a remittance stretches when it lands in a parent's account in Kochi or Ludhiana.

It cuts the other way too. India's deepening reliance on Russian energy is precisely the kind of friction that hangs over the India\u2013U.S. trade talks underway in Delhi this week, and over the diaspora's hopes that a tariff deal lands before Washington's July 24 deadline. Every record month of Russian crude is a reminder that India will guard its energy security fiercely, even when it complicates the Washington relationship that shapes H-1B visas, student flows and the broader climate for Indian-Americans. And for the millions of Indians working in the Gulf's oil and gas economy, the shifting map of who sells India its oil is a live signal about where the jobs and the contracts will be once the dust settles.

## What's Next

The near-term question is how quickly Gulf producers claw back the market share the war cost them. Saudi Arabia and other OPEC suppliers have already asked Indian refiners to lift their full committed contract volumes as Hormuz traffic normalises, and some spot buying from Latin America is expected to taper. But the structural lesson of the past four months is unlikely to be unlearned: India has built a far broader, more opportunistic sourcing base than it had before February, and Russian crude \u2014 sanctioned by the West, discounted to India \u2014 remains the anchor. For a country that imports more than 85% of the oil it burns, energy security will keep trumping everyone else's preferences, and the diaspora will keep watching the price at the pump and the value of the rupee for the real-world echo of it."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # No single named person -> topic imagery from Commons (oil tanker / refinery)
    img_url, ctitle = pick_commons([
        "crude oil tanker ship sea",
        "oil tanker",
        "Jamnagar refinery",
        "oil refinery India",
        "petroleum refinery"
    ])
    img_caption = "An oil tanker at sea; India's Russian crude imports are set for a record ~2.55 million barrels a day in June, nearly half of all its oil imports"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("oil tanker ship ocean")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "An oil tanker at sea; India turned record volumes of Russian crude to cushion the Iran-war energy shock"

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
            "Reuters \u2014 India pivots to Russian crude and coal to mitigate Iran war fallout (June 23, 2026): India has swung to buying Russian crude oil and coal after flows were disrupted and prices rose during the Iran conflict; arrivals of Russian crude expected to surge to a record ~2.55 million bpd in June (Kpler), up from 2.13 million bpd in May and above the prior record 2.16 million bpd of May 2023; Russia's share of India's total crude imports of 5.29 million bpd in June will be just under 50%, up from ~23% in the three months before the war began Feb 28; the US waived Russia sanctions to boost supply after Iran effectively closed the Strait of Hormuz, then let the waiver expire June 17 without extending it; India still holding off some Middle East producers, with Saudi imports ~349,000 bpd in June vs ~832,000 bpd before the conflict",
            "OilPrice.com / Financial Express \u2014 India's Imports of Russian Oil Set for New Record High (June 22, 2026): India imported ~2.6 million bpd of Russian crude so far in June (Kpler preliminary vessel-tracking), with Russian crude as much as 53.5% of all Indian oil imports; full-month Russian crude set for a record ~2.35 million bpd, exceeding the prior record of 2.2 million bpd from May 2023; the US let the waiver on Russian oil sales expire without renewal as it announced the Iran MoU; Kpler's Sumit Ritolia: 'Regardless of whether the US waiver is extended, we expect India's imports of Russian crude to remain robust, even if not at record-high levels'; India also buying more from Nigeria, Angola, Brazil and Venezuela",
            "The Hindu BusinessLine / Outlook Business (PTI) \u2014 India boosts Russian, UAE oil purchases in June ahead of full Hormuz recovery (June 21, 2026): Russian crude described as a 'cornerstone' of India's import strategy expected to remain so even after Hormuz normalises given favourable economics and supply security; UAE imports near-record ~636,000 bpd, Venezuela India's fourth-largest supplier at ~209,000 bpd behind Saudi Arabia's ~384,000 bpd, US imports fell sharply to ~91,000 bpd; three Indian-flagged tankers carrying 860,000+ tonnes of crude plus an LNG carrier resumed Hormuz transit after the US-Iran agreement; Gulf suppliers expected to gradually regain share but India's sourcing base likely to remain broader than before the crisis"
        ]),
        "diaspora_angle": "Cheaper crude keeps a lid on India's fuel costs, import bill and the rupee that NRIs remit into, while India's deepening reliance on Russian oil is exactly the friction hanging over the India\u2013U.S. trade talks that shape H-1B visas and student flows \u2014 and a live signal for the millions of Indians working the Gulf's energy economy.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: NSE files for India's largest-ever IPO ──────────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: NSE files for India's largest-ever IPO")
    print("="*60)

    slug = "nse-files-drhp-largest-india-ipo-30000-crore-derivatives-exchange-diaspora-investors-20260623"
    headline = "India's Biggest Stock Exchange Is Finally Going Public \u2014 in What Would Be the Country's Largest IPO Ever"
    subheadline = "After nearly a decade of delays, the National Stock Exchange has filed papers for a roughly Rs 30,000-crore listing that could value the world's busiest derivatives bourse near $57 billion. It is a pure cash-out for global funds and Indian institutions \u2014 and a long-awaited window for the diaspora investors who power so much of India's market."

    body = """The National Stock Exchange of India \u2014 the engine room of the country's stock market and the busiest derivatives exchange on the planet \u2014 has finally filed to go public. NSE submitted its Draft Red Herring Prospectus to the Securities and Exchange Board of India, setting up an initial public offering that industry estimates put at around Rs 30,000 crore. If it prices at the top of expectations, it would become the largest IPO in India's history, surpassing the record set by Hyundai Motor India's 2024 listing.

The structure is unusual but telling. The offering is a pure Offer for Sale: NSE itself will raise no fresh capital. Instead, existing shareholders will sell roughly 148.9 million equity shares \u2014 about 6% of the exchange \u2014 and pocket the proceeds. NSE does not need the money. It is debt-free, cash-rich and highly profitable, reporting total income of about Rs 18,713 crore and net profit of around Rs 10,302 crore for the year ended March 2026. The listing is less about funding growth than about finally giving long-trapped shareholders an exit and bringing transparent price discovery to a stock that has traded actively in the unlisted "grey" market for years.

## A Listing a Decade in the Making

NSE first tried to list back in 2016, only to see its plans stall amid a regulatory enquiry \u2014 most notably the long-running "co-location" controversy over unfair access to its trading systems. While NSE waited, its smaller rival BSE listed in 2017. The path cleared this year: the board approved the IPO in February after a no-objection certificate from SEBI, and the government halved the minimum public float for the very largest companies, letting firms valued above Rs 5 trillion sell as little as 2.5% of their capital. A high-powered SEBI committee also recommended settlements exceeding Rs 1,800 crore to close out the co-location and dark-fibre cases that had dogged the exchange.

The scale is hard to overstate. Founded in 1992 to replace a scandal-prone patchwork of regional exchanges, NSE today commands roughly 95% of India's cash-equity market and about 75% of equity derivatives, and accounts for close to 89% of global stock-index options volume \u2014 the product of an extraordinary boom in options trading among Indian retail investors. At its unlisted-market price of nearly Rs 2,000 a share, the exchange is valued at around $57 billion, which would rank it among the world's five most valuable bourses, comparable to the London Stock Exchange Group.

## Why the Diaspora Should Care

For diaspora investors, NSE is not just another IPO \u2014 it is the marketplace itself. Nearly every India-focused equity fund, GIFT City vehicle and direct trade an NRI makes ultimately runs across NSE's rails. Owning a slice of the exchange is a way to bet on the structural growth of Indian capital markets as a whole rather than on any single company: the more Indians trade, the more the exchange earns. With around 257 million investor accounts and 130 million unique investors, NSE has a far larger retail base than Nasdaq or the New York Stock Exchange, which lean on institutions.

The IPO also lands at a moment thick with signals for the diaspora. It is one of two mega-listings expected this year, alongside Mukesh Ambani's Reliance Jio \u2014 the phone carrier in millions of NRI families' pockets \u2014 in an offering that could top $4 billion. Among the sellers cashing out of NSE are exactly the kind of global institutions the diaspora invests beside: Singapore's Temasek, the Canada Pension Plan Investment Board, and Indian heavyweights such as State Bank of India, Bank of Baroda and LIC. Their willingness to sell at a discount of 5% to 10% to private-market valuations sets a price marker that retail and NRI buyers will study closely when the shares finally open.

## What's Next

Nothing about an NSE listing is fast. SEBI's review of the draft prospectus will set the timeline, and a public offer typically takes at least three to four months to clear after approvals, with investor roadshows determining final pricing \u2014 sources point to a band around Rs 1,900 a share and a debut likely in late 2026 on rival exchange BSE, since NSE cannot list on itself. The risks are real too: revenue heavily skewed toward derivatives transactions, ongoing regulatory scrutiny, and a profit that actually slipped about 15% last year. But for a diaspora that has spent years watching India's market boom from the outside, the chance to own the exchange at the centre of it is the kind of milestone worth marking \u2014 carefully, and with eyes open to the price."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url, ctitle = pick_commons([
        "National Stock Exchange of India building Mumbai",
        "Bombay Stock Exchange building Mumbai",
        "Bandra Kurla Complex Mumbai",
        "Mumbai financial district skyline",
        "Nariman Point Mumbai"
    ])
    img_caption = "Mumbai's financial district; the National Stock Exchange has filed for a ~Rs 30,000-crore IPO that would be India's largest-ever"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("Mumbai skyline business district")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A city financial district; NSE's filing sets up what could be India's largest-ever public offering"

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
            "Reuters \u2014 India's largest bourse NSE files for IPO after years of regulatory delays (June 18, 2026): NSE filed draft papers for an IPO, one of two mega IPOs this year alongside Reliance Jio; trying to list since 2016 when first papers were stalled by a regulatory enquiry; estimated valuation ~$55 billion based on unlisted-market shares, comparable to the London Stock Exchange Group ($58bn); founded 1992, India's most widely held unlisted firm with 200,909 shareholders; proposed IPO sees shareholders offer 148.9 million equity shares (6% of total); government halved minimum IPO float for companies valued above Rs 5 trillion to 2.5%; sellers include SBI, Bank of Baroda, state insurers, Singapore's Temasek and the Canada Pension Plan Investment Board; ~257 million investor accounts and 130 million unique investors",
            "Reuters \u2014 India's long-delayed NSE IPO sets up $2.6 billion windfall for top investors / India's NSE set to list (June 18-19, 2026): pure offer-for-sale of ~6% of equity, no fresh capital raised; shares trade near Rs 2,000 in the unlisted market implying a valuation around $57 billion, the world's fifth most valuable exchange; shares may be offered at a 5-10% discount to private valuations, with the figure under discussion around Rs 1,900/share, implying a ~$3.3 billion issue alongside Reliance Jio's ~$4 billion; NSE reported FY ending March 2026 profit of Rs 103 billion ($1.09bn), down 15% year-on-year; ~95% cash-equity share, ~75% equity-derivatives share, ~89% of global stock-index options volume in 2025; transaction revenue >80% of income",
            "The Indian Eye / LiveMint \u2014 NSE Files for IPO worth Rs 30,000-Crore, set to become India's Largest Public Issue (June 23, 2026): DRHP filed with SEBI for a ~Rs 30,000-crore IPO expected to be the largest in India's history; pure Offer for Sale of ~148.9 million shares (~6% of equity); FY March 2026 total income Rs 18,713 crore and net profit Rs 10,302 crore; co-location controversy and regulatory hurdles delayed listing for nearly a decade; board approved IPO Feb 6, 2026 after SEBI no-objection; valuation estimated at Rs 5-5.5 trillion; would surpass the record set by Hyundai Motor India; listing to be on BSE (NSE cannot list on itself), timeline subject to SEBI review, likely late 2026"
        ]),
        "diaspora_angle": "NSE is the marketplace nearly every India-focused fund, GIFT City vehicle and NRI trade runs across, so owning a slice is a bet on Indian capital markets themselves \u2014 and the global funds cashing out (Temasek, CPPIB) and the discount they accept set a price marker diaspora investors will study when one of India's two mega-IPOs of the year finally opens.",
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
