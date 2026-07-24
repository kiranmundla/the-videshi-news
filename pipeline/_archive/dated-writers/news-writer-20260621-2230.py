#!/usr/bin/env python3
"""
Videshi News Writer — June 21, 2026 (22:30 UTC run)
2 NEW articles:
  1. India-US ministerial trade talks open in Delhi this week; July 24 tariff cliff (news / trade)
  2. Indian consular services in UAE pause June 26-30 ahead of provider switch (nri-world / diaspora-services)
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


# ─── Article 1: India-US ministerial trade talks ───────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India-US ministerial trade talks")
    print("="*60)

    slug = "india-us-ministerial-trade-talks-delhi-goyal-greer-july-24-tariff-deadline-bta-20260621"
    headline = "India's Trade Minister Just Summoned Washington's Negotiator to Delhi. The Clock Runs Out July 24."
    subheadline = "Commerce Minister Piyush Goyal says US Trade Representative Jamieson Greer arrives this week to put 'final touches' on the first phase of a bilateral trade deal — one both sides want signed before a temporary tariff regime expires and a new, harsher one could snap into place."

    body = """India and the United States are racing a calendar. Commerce and Industry Minister Piyush Goyal told reporters in Mumbai that his American counterpart, US Trade Representative Jamieson Greer, would arrive in Delhi this week for two days of ministerial-level talks aimed at finishing the first phase of a long-negotiated bilateral trade agreement. "For the US trade deal talks, tomorrow my counterpart is coming to Delhi," Goyal said. The meeting follows chief-negotiator-level discussions held in the capital from June 2 to 4, and India's Commerce Secretary Rajesh Agrawal has signalled the ministers will focus on giving "final touches" to the framework.

The deadline that gives the talks their urgency is July 24. On February 24, the US imposed a temporary 10% tariff on goods from all its trading partners, a stopgap meant to last 150 days. When that window closes next month, Washington must put a new tariff regime in place — and for India, what replaces the placeholder could be considerably steeper. Goyal said on June 5 that both sides were moving to close "all the open ends" of the interim deal and expected to execute a "very, very vibrant" first phase by the middle of July.

For the Indian diaspora, this is not abstract trade-ministry choreography. The United States was India's second-largest trading partner in 2025-26, with Indian exports to America worth $87.3 billion and a trade surplus of $34.4 billion. Behind those numbers sit the pharmaceutical firms, textile exporters, gems-and-jewellery houses and IT services companies whose fortunes shape jobs on both sides of the ocean — and whose pricing in American stores depends directly on the tariff line the two ministers settle on. NRI-owned import businesses, retailers and the families who send goods and money home all feel the pass-through when duties move.

The backdrop is a tariff landscape repeatedly upended by American courts. On February 20, the US Supreme Court ruled against President Donald Trump's sweeping "reciprocal" tariffs, which had been imposed under the 1977 International Emergency Economic Powers Act and had left India facing a 50% levy. That ruling forced Washington to replace the reciprocal tariffs with the temporary 10% duty — and forced both governments back to the drawing board on a framework they had announced with fanfare on February 7. Under that original framework, the US had agreed to cut tariffs on Indian goods to 18% from 50%, and India had offered to lower or eliminate duties on a wide range of American industrial and farm goods, from tree nuts and soybean oil to wine and spirits. New Delhi also signalled intent to buy some $500 billion of US energy, aircraft, precious metals and technology products over five years.

What India wants now is an edge. When the framework was first struck, an 18% US tariff on Indian goods gave New Delhi a comparative advantage over competitors such as Vietnam and the ASEAN bloc, which faced 19 to 20%. But the flat 10% placeholder erased that gap — every country now carries the same additional levy. Indian officials say it is essential the final pact restores a margin over rival exporters. The logic is simple: if an Indian shirt lands in America at $118 after duty while a Vietnamese one costs $120, US importers lean toward the cheaper Indian product, and Indian factories keep their orders.

Complicating the endgame are two separate US Section 301 investigations launched in March, including one targeting India over alleged failures to bar goods made with forced labour. On June 2, the USTR proposed 12.5% tariffs on 54 countries, India among them, under that probe; the measure is still only a proposal, with hearings scheduled for July 7 and a comment deadline of June 22. A second investigation's report is still awaited. Those parallel tracks mean a headline trade deal could be undercut by sector-specific duties arriving through a different legal door.

The week ahead, then, is a test of whether two governments can convert a battered framework into a signed first phase before the temporary regime lapses. For overseas Indians watching from Edison, Houston or Silicon Valley, the stakes are concrete: the price of Indian goods on American shelves, the health of the export industries that employ relatives back home, and whether the world's largest democracy and its largest economy can still strike a deal when the courts and the clock keep moving the goalposts. The answer should arrive within days."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    person_img = fetch_wikipedia_person_image("Piyush Goyal")
    if person_img:
        img_url = person_img
        img_caption = "India's Commerce and Industry Minister Piyush Goyal, who is hosting US Trade Representative Jamieson Greer in Delhi this week"
        img_attribution = "Wikimedia Commons"

    if not img_url:
        for q in ["Piyush Goyal Minister Commerce", "India United States trade", "Narendra Modi United States President"]:
            commons = fetch_wikimedia_commons_images(q)
            if commons:
                img_url = commons[0]["url"]
                img_caption = "India-US trade negotiations resume at ministerial level in Delhi"
                img_attribution = "Wikimedia Commons"
                break

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
            "The Hindu BusinessLine — 'India, US to hold ministerial-level trade pact talks this week' (June 21, 2026): USTR Jamieson Greer and Minister Piyush Goyal to hold two-day talks in Delhi; follows June 2-4 chief-negotiator discussions; temporary 10% US tariff (imposed Feb 24 for 150 days) expires July 24; USTR's two Section 301 probes; June 2 proposal of 12.5% tariffs on 54 countries including India, hearings July 7, comment deadline June 22",
            "The Hindu BusinessLine (same report): Feb 7 joint statement framework — US to cut Indian tariffs to 18% from 50%; India to reduce/eliminate duties on US industrial and farm goods (DDGs, sorghum, tree nuts, fruit, soybean oil, wine, spirits); India to buy ~$500 billion of US energy, aircraft, precious metals, technology and coking coal over five years; US was India's 2nd-largest trading partner in 2025-26 with $87.3 billion in Indian exports and a $34.4 billion surplus",
            "The Hindu BusinessLine (same report): Feb 20 US Supreme Court ruling against Trump's IEEPA-based reciprocal tariffs (India had faced 50%), forcing the temporary 10% duty; India seeking a comparative tariff advantage over ASEAN, Vietnam, Sri Lanka, Pakistan and Bangladesh competitors"
        ]),
        "diaspora_angle": "The tariff line these two ministers settle on directly sets the shelf price of Indian goods in America and the health of the pharma, textile, gems and IT export industries that employ millions of the diaspora's relatives back home — making a deal before the July 24 cliff a pocketbook issue for NRIs, not just a diplomatic one.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: UAE consular services pause ─────────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India consular services pause in UAE")
    print("="*60)

    slug = "india-uae-passport-visa-consular-services-pause-june-26-30-al-hind-bls-sgivs-handover-20260621"
    headline = "India Is Switching Who Handles Passports in the UAE. For Five Days, the Window Closes Entirely."
    subheadline = "The Indian Embassy in Abu Dhabi says passport, visa and attestation services across the Emirates will halt from June 26 to 30 as a new outsourced provider takes over — a quiet handover that touches one of the world's largest diaspora communities."

    body = """For one of the largest concentrations of Indians anywhere outside India, a routine bureaucratic handover is about to mean a closed door. The Indian Embassy in Abu Dhabi has announced that passport, visa and attestation services across the United Arab Emirates will be suspended for five days, from June 26 to June 30, as the mission transitions from its current outsourced operators to a new one. Regular appointments will not be available during that window, and applicants have been urged to plan their submissions around it.

The mechanics are straightforward but the timing matters. The existing providers — BLS International, which has handled passport and visa services, and SGIVS Global, which managed attestation — will stop accepting new applications after June 25. On July 1, Al Hind Tours and Travel LLC, selected after a tendering and evaluation process, formally takes over all passport, visa and consular service applications and launches a new online appointment portal. Applications lodged before the cut-off will continue to be processed through the existing centres, so the disruption falls on anyone who has not yet filed.

For the roughly 3.5 million Indians who live and work in the UAE — the single largest expatriate group in the country and a cornerstone of the global diaspora — consular paperwork is not a once-a-decade chore. It is the machinery of daily life abroad: renewing a passport before it lapses, getting educational and commercial documents attested for jobs and family sponsorship, securing the papers that keep a residency visa valid. A five-day blackout, landing just before a provider many applicants have never dealt with takes the reins, is the kind of administrative speed bump that can cascade into missed deadlines for those who leave things late.

The embassy has stressed that emergency services will not stop. Urgent cases during the June 26-30 window will be handled directly by the Embassy of India in Abu Dhabi and the Consulate General of India in Dubai. Applicants needing immediate help have been pointed to a toll-free number, 800 46342 (spelling "800 INDIA"), a WhatsApp line at +971 54 309 0571, and an email channel at pbsk.dubai@mea.gov.in. The mission has repeatedly asked the community to rely only on official communication channels for updates rather than secondhand claims during the changeover.

The practical advice writes itself. Anyone in the UAE whose passport is nearing expiry, who needs documents attested for a job offer, school admission or family visa, or who has a residency renewal that hinges on fresh paperwork would be wise to file before June 25 rather than risk the gap. Those who cannot beat the deadline should know that nothing is lost — services resume on July 1 through Al Hind's centres — but the new portal and operator will be unfamiliar, and the first days of any handover tend to carry teething troubles.

The change also sits within a broader pattern of churn in how India delivers consular services to its enormous Gulf diaspora, where outsourced operators periodically rotate as contracts are re-tendered. For the workers who form the backbone of that community — construction crews, healthcare staff, hospitality workers, engineers and the professionals who anchor the Emirates' Indian business class — the identity of the company processing their paperwork is less important than continuity and reliability. The test of this handover will be whether Al Hind's online portal and centres open smoothly on July 1, or whether the five-day pause stretches, in practice, into a longer backlog.

For now, the message from Abu Dhabi is a calendar entry every Indian in the UAE should mark: file before June 25 if you can, keep the emergency contact lines handy if you cannot, and trust only official embassy and consulate channels for what comes next. In a community where so much of life runs through a passport and a stack of attested documents, even a planned five-day pause is worth planning around."""

    img_url = None
    img_caption = ""
    img_attribution = ""

    for q in ["Indian passport", "Embassy of India building", "Dubai skyline Burj Khalifa", "Indian passport document"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            if "passport" in q.lower():
                img_caption = "An Indian passport; consular services in the UAE pause June 26-30 during a provider handover"
            else:
                img_caption = "Dubai, where Indian consular services pause for five days during a provider transition"
            img_attribution = "Wikimedia Commons"
            break

    if not img_url:
        px = fetch_pexels_image("passport documents application")
        if px:
            img_url = px
            img_caption = "Passport and consular paperwork; India's UAE services pause June 26-30"
            img_attribution = "Pexels"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "diaspora-services",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Ainvest — 'Indian Passport, Visa Services in UAE to Pause for 5 Days from June 26' (June 20, 2026): Indian Embassy in Abu Dhabi suspending passport, visa and attestation services June 26-30 due to transition to new outsourced provider Al Hind Tours and Travel LLC; BLS International and SGIVS Global stop accepting new applications after June 25; emergency services continue; Al Hind launches new online appointment portal July 1; emergency contacts toll-free 800 46342 (800 INDIA), WhatsApp +971 54 309 0571, email pbsk.dubai@mea.gov.in",
            "News7tv — 'Indian Embassy in UAE to pause passport, visa services from June 26-30 ahead of Al Hind Tours takeover' (June 20, 2026): Al Hind Tours and Travel LLC to take over passport, visa and attestation services from July 1; no regular appointments June 26-30; applications submitted before the transition continue through existing centres; emergency services handled by Embassy of India Abu Dhabi and Consulate General of India Dubai; Al Hind selected after tendering and evaluation process"
        ]),
        "diaspora_angle": "The UAE is home to roughly 3.5 million Indians — the largest expatriate group in the country — for whom passport renewals, document attestation and visa paperwork are the machinery of daily life abroad, so a planned five-day service blackout just before an unfamiliar new provider takes over is a deadline every Indian in the Emirates needs to plan around.",
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
