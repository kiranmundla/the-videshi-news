#!/usr/bin/env python3
"""
Videshi News Writer — June 21, 2026 (04:30 UTC run)
2 NEW articles:
  1. Gaganyaan-1 uncrewed test on track for H2 2026; India space economy to hit $45B (tech / space / diaspora-STEM)
  2. Turtlemint IPO — India's first insurtech listing opens; what it signals for NRI investors (markets / finance)
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


# ─── Article 1: Gaganyaan-1 on track for H2 2026 ──────────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Gaganyaan-1 on track for H2 2026 / $45B space economy")
    print("="*60)

    slug = "gaganyaan-1-uncrewed-test-h2-2026-vyommitra-india-space-economy-45-billion-diaspora-20260621"
    headline = "India's First Spacecraft Built for Humans Is Almost Ready to Fly. A Robot Goes First, and the Diaspora Is Watching."
    subheadline = "Union Minister Jitendra Singh says the final uncrewed Gaganyaan test \u2014 carrying the humanoid robot Vyommitra \u2014 is on track before the end of 2026, with an Indian astronaut to follow in 2027, as India bets that a $9-billion space economy can quintuple to $45 billion within a decade."

    body = """India is closing in on one of the most consequential milestones in its history: the first orbital flight of a spacecraft designed to carry its own astronauts. Before any human climbs aboard, a robot will make the journey \u2014 and Union Minister Jitendra Singh has now confirmed that this uncrewed dress rehearsal remains on track for the second half of 2026.

Speaking in an interview with ANI, the minister who oversees the Department of Space said the government is targeting a final uncrewed test flight under the Gaganyaan programme before the end of this year, carrying the half-humanoid robot Vyommitra in the astronaut's seat. "Once our test flights are complete, we will make a big effort to launch one final test rehearsal before the end of this year," Singh said. "I think next year, as part of Gaganyaan, we will also be able to send an Indian human to space."

## The Robot That Goes First

The mission, designated Gaganyaan-1 or simply G1, is the first uncrewed test flight of India's human spaceflight programme. It will lift off on the HLVM3 rocket \u2014 the human-rated version of India's heaviest launcher \u2014 from the Satish Dhawan Space Centre at Sriharikota. Industry reporting has narrowed the likely launch window to between August and September 2026, following clearances from a national review committee.

In the crew module will sit Vyommitra, a half-humanoid robot built to simulate the conditions a human astronaut would experience. It will test the spacecraft's life-support and environmental control systems, monitor cabin conditions, and provide critical data on how the crew and service modules perform in low Earth orbit and during the fiery re-entry back through the atmosphere. The flight is the last major gate before India can credibly strap a person into that seat.

The timeline has moved before. The uncrewed flight was originally pencilled in for early 2026, then pushed to the second half of the year after the Indian Space Research Organisation chose to fold in extra safety checks and lessons learned from anomalies in recent Polar Satellite Launch Vehicle missions. ISRO has been consistent that the slip is about caution, not trouble: the broader programme, it says, remains firmly on track, with the first crewed flight still targeted for 2027.

## A $45-Billion Bet

For Singh, Gaganyaan is the headline act of a far larger ambition. He told ANI that India's space economy, "next to nothing" a decade ago, now stands at roughly $9 billion and is "accelerating at such a rapid pace that it appears we will reach $45 billion in the next eight to ten years." That fivefold leap is being driven by a deliberate policy shift: opening a once-closed government monopoly to private companies and foreign investment.

The numbers behind that opening are striking. India's space budget has roughly tripled, from 5,615 crore rupees in 2013-14 to 13,416 crore in the latest cycle. The number of space startups has grown from barely one to more than 300. ISRO recently marked its 100th satellite launch, and India has lofted hundreds of foreign satellites for paying customers, turning launch capacity into export revenue. Looking further out, Singh has spoken of a Bharat Antariksh Station \u2014 an Indian space station \u2014 by around 2035, and an Indian on the Moon by 2040.

## Why It Matters for the Diaspora

If the abstract ambition feels distant, the human thread runs straight through the global Indian community. Group Captain Shubhanshu Shukla, the Indian Air Force test pilot who flew to the International Space Station on the Axiom-4 mission alongside an international crew, has become a living bridge between the American and Indian space ecosystems. The experience and data from his ISS flight are feeding directly into Gaganyaan's preparations \u2014 a reminder that India's human-spaceflight push is being built partly on collaboration with NASA and US commercial partners.

That ecosystem is thick with Indian-origin talent. The engineers, scientists and mission specialists who populate NASA, SpaceX, Blue Origin and the universities feeding them include a deep bench of the diaspora's STEM professionals. For Indian-American families who measure pride in the achievements of their children in laboratories and launch control rooms, Gaganyaan is not a foreign story \u2014 it is a shared one. India becoming only the fourth nation to independently send humans to orbit, after Russia, the United States and China, would land as a moment of collective arrival.

The robot flies first. But the seat it occupies is, before long, meant for a human \u2014 and for a diaspora that has spent decades helping build the world's space programmes, watching India build its own carries a particular weight."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "An ISRO rocket on the launch pad at Satish Dhawan Space Centre; Gaganyaan-1 will fly on the human-rated HLVM3 from Sriharikota"
    img_attribution = "Wikimedia Commons"

    for q in ["Gaganyaan crew module ISRO", "LVM3 rocket launch Satish Dhawan", "ISRO LVM3 launch pad Sriharikota", "GSLV Mark III launch"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "gaganyaan" in t or "crew module" in t:
                img_caption = "Gaganyaan crew module hardware; the uncrewed G1 test carrying the robot Vyommitra is on track for the second half of 2026"
            elif "lvm" in t or "gslv" in t:
                img_caption = "An ISRO LVM3 heavy-lift rocket; the human-rated HLVM3 will carry Gaganyaan-1 from Satish Dhawan Space Centre"
            else:
                img_caption = "An ISRO launch from Satish Dhawan Space Centre, Sriharikota, the spaceport for India's Gaganyaan human spaceflight programme"
            break

    if not img_url:
        px = fetch_pexels_image("rocket launch space")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A rocket lifting off"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Devdiscourse / ANI \u2014 India's space economy to grow five-fold to USD 45 billion; Gaganyaan human mission likely next year: Jitendra Singh (June 20, 2026)",
            "Devdiscourse \u2014 Union Minister Jitendra Singh hails space, nuclear energy reforms; final Vyommitra test before end of year",
            "India Strategic \u2014 First Gaganyaan uncrewed G-1 gears up for launch (August\u2013September 2026, Satish Dhawan Space Centre)",
            "Wikipedia \u2014 Gaganyaan-1 (uncrewed flight test, H2 2026 planned, HLVM3, Vyommitra)",
            "Aviation Week \u2014 India's first crewed Gaganyaan launch and ISRO astronaut training (Shubhanshu Shukla, Axiom-4)"
        ]),
        "diaspora_angle": "India's first human-rated spacecraft is nearing its uncrewed Vyommitra test flight, with data from diaspora astronaut Shubhanshu Shukla's ISS mission feeding the effort \u2014 a milestone that resonates across the Indian-origin STEM community powering NASA, SpaceX and the world's space programmes.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Turtlemint IPO — India's first insurtech listing ───────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Turtlemint IPO \u2014 India's first insurtech listing")
    print("="*60)

    slug = "turtlemint-ipo-india-first-insurtech-listing-price-band-nri-investors-policybazaar-20260621"
    headline = "India's First Insurtech IPO Is Live. The Muted Grey Market Says the Easy-Money Era of Desi Startups Is Over."
    subheadline = "Turtlemint's \u20b9883-crore offering \u2014 the first time an Indian insurance-distribution startup has gone public \u2014 closes June 23 and lists June 29, but a thin grey-market premium and persistent losses are forcing NRI investors to weigh a new kind of question about India's IPO boom."

    body = """For years, the story of investing in young Indian companies was told in superlatives: record fundraising, blockbuster listing-day pops, valuations that seemed to defy gravity. The initial public offering of Turtlemint Fintech Solutions, open for subscription now and the first insurtech listing in Indian history, is telling a more sober story \u2014 and that shift matters as much to the diaspora as the deal itself.

Turtlemint's \u20b9882.67-crore issue opened on June 19 at a price band of \u20b9144 to \u20b9152 a share, valuing the Mumbai-based company at about \u20b94,513 crore, or roughly $475 million, at the top of the range. The subscription window closes on June 23, with allotment expected June 24 and a market debut on both the BSE and NSE tentatively set for June 29. The offering combines a fresh issue of \u20b9660.7 crore \u2014 new money for the company \u2014 with an offer for sale of about \u20b9222 crore by existing shareholders cashing out a slice of their stake.

## What Turtlemint Actually Does

Turtlemint is not an insurer. It is a technology-enabled distributor of financial products, with insurance \u2014 both life and non-life \u2014 accounting for about 98 percent of its revenue, alongside mutual funds, loans and deposits. Its model rests on a network of PoSP agents (point-of-sale persons): the company arms tens of thousands of small advisors and agents with software to sell and service policies, particularly in smaller towns and underserved markets where insurance penetration remains low. The pitch to investors is that India's vast, under-insured population plus AI-led distribution equals a long growth runway.

The numbers show that growth, and its cost. Revenue jumped about 80 percent year-on-year to \u20b9741 crore in the first nine months of FY26. But the company remains firmly loss-making, with a net loss of roughly \u20b9187 crore over the same period, up about 20 percent from a year earlier, and continued cash burn from operations. The only listed peer the prospectus identifies is PB Fintech, the parent of Policybazaar, which has been profitable for three straight years and trades at a far richer multiple.

## A Muted Reception

The market's response has been notably restrained. Ahead of the opening, the grey-market premium \u2014 the unofficial price at which shares change hands before listing \u2014 hovered at just \u20b92 to \u20b93 over the issue price, signalling that investors expect a flat-to-modest debut rather than the explosive first-day gains that defined recent years. On day one, the issue was subscribed only about 45 percent, with non-institutional investors particularly cautious.

There was a firmer vote of confidence from the institutional side. Turtlemint raised \u20b9397.2 crore from anchor investors before the issue opened, allotting shares to a roster that included domestic mutual funds such as ICICI Prudential, Bank of India and Bandhan, alongside global names like Societe Generale, BNP Paribas, Citi and Amansa Holdings. Analysts noted a telling alignment: some of the life insurers buying in are also Turtlemint's distribution customers, meaning the platform's growth directly benefits its own anchor backers. Brokerage SMIFS recommended subscribing for the long term, citing the large agent network and India's rising insurance penetration.

## Why It Matters for the Diaspora

For non-resident Indians who follow \u2014 or fund \u2014 India's startup economy, Turtlemint is a useful weathervane. NRIs and overseas citizens can participate in Indian IPOs through their NRE or NRO portfolio accounts, and many have ridden the country's listing boom from afar. This deal arrives amid a crowded pipeline that also includes the long-awaited NSE listing and Reliance's Jio Platforms filing, and its lukewarm reception suggests the market is starting to discriminate: profitability and reasonable pricing now matter more than a compelling narrative alone.

That recalibration cuts both ways. For diaspora investors who have watched loss-making consumer-tech listings swing wildly, a more disciplined market is arguably healthier \u2014 a sign that India's capital markets are maturing past the froth. For founders and early backers, including the global Indian venture investors who seeded a generation of these companies, it is a reminder that the exit no longer prices itself.

Turtlemint will list either way on June 29, and its first trading days will be read closely as a referendum on whether India's insurtech promise can translate into public-market value. For an NRI deciding whether to put capital to work back home, the lesson of this IPO may be less about one company than about a new rule of the road: in 2026, the Indian market is asking harder questions, and expecting better answers."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "The Bombay Stock Exchange in Mumbai; Turtlemint, India's first insurtech IPO, is set to list on the BSE and NSE on June 29"
    img_attribution = "Wikimedia Commons"

    for q in ["Bombay Stock Exchange building Mumbai", "BSE building Dalal Street", "National Stock Exchange India building", "Mumbai financial district BKC"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "national stock" in t or "nse" in t:
                img_caption = "The National Stock Exchange in Mumbai; Turtlemint's insurtech IPO is slated to debut on the NSE and BSE on June 29"
            elif "bombay" in t or "bse" in t or "dalal" in t:
                img_caption = "The Bombay Stock Exchange on Dalal Street, Mumbai, where Turtlemint \u2014 India's first insurtech IPO \u2014 will list on June 29"
            else:
                img_caption = "Mumbai's financial district; Turtlemint's \u20b9883-crore insurtech IPO closes June 23 and lists on the BSE and NSE on June 29"
            break

    if not img_url:
        px = fetch_pexels_image("stock exchange financial district")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A stock exchange trading environment"

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
            "Inc42 \u2014 [Update] Turtlemint IPO: Issue Subscribed 45% On Day 1 (price band \u20b9144-152; valuation \u20b94,513 Cr; listing June 29)",
            "Inc42 \u2014 Turtlemint IPO: Cash Burn In Focus After \u20b9397 Cr Anchor Round (net loss \u20b9187.3 Cr in 9M FY26)",
            "Outlook Business \u2014 Turtlemint IPO Opens Today: GMP, Risks, Financials And Key Things To Know (fresh issue \u20b9660.72 Cr, OFS \u20b9221.95 Cr)",
            "The Hindu BusinessLine \u2014 Turtlemint Fintech Solutions IPO: Should You Subscribe? (PoSP model; PB Fintech / Policybazaar as only listed peer)",
            "Outlook Money \u2014 Turtlemint Fintech Solutions IPO: modest demand on first day of bidding; muted grey-market premium"
        ]),
        "diaspora_angle": "Turtlemint's debut \u2014 India's first insurtech IPO \u2014 lands amid a crowded listing pipeline, and its muted grey-market reception signals to NRI investors, who can subscribe through NRE/NRO portfolio accounts, that India's IPO boom is now rewarding profitability and pricing discipline over narrative alone.",
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
