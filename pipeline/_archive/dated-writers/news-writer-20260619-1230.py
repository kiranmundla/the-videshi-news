#!/usr/bin/env python3
"""
Videshi News Writer — June 19, 2026 (12:30 UTC run)
2 NEW articles for the "news" category:
  1. India overhauls UAE passport/visa/consular services — Al Hind Tours takes over July 1 (diaspora-safety)
  2. India's state fuel retailers hit borrowing limits — Rs 1 trillion Q1 losses under Modi's price freeze (economy)
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


# ─── Article 1: India overhauls UAE consular services ────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India overhauls UAE passport/visa services")
    print("="*60)

    slug = "india-uae-passport-visa-consular-services-new-provider-al-hind-july-2026-20260619"
    headline = "India Is Handing Its UAE Passport and Visa Counters to a New Operator on July 1. Millions of NRIs Need to Pay Attention."
    subheadline = "From July 1, Al Hind Tours and Travels takes over passport, visa, OCI and attestation services across the Emirates — replacing BLS International and SGIVS Global. For the 3.5 million Indians in the UAE, every consular errand is about to run through a different door."

    body = """For the largest community of overseas Indians anywhere in the world, the most mundane bureaucratic act — renewing a passport, getting a document attested, applying for an OCI card — is about to change hands. The Indian Embassy in Abu Dhabi has confirmed that from July 1, 2026, a new provider, Al Hind Tours and Travels LLC, will take over passport, visa and consular services across the United Arab Emirates, replacing the long-standing operators BLS International Services and SGIVS Global.

It is the kind of administrative change that rarely makes front pages, yet touches almost every Indian family in the Gulf. The UAE is home to roughly 3.5 million Indians — the single largest expatriate population in the country and one of the biggest concentrations of the diaspora on earth. Between passport renewals, visa applications, police clearance certificates and the endless document attestations that expatriate life demands, the consular counter is a recurring fixture of life abroad. Changing who runs it is no small thing.

## What Is Actually Changing

The Embassy has been precise about the timeline. Until June 30, 2026, applications will continue to be processed by the existing operators, BLS International and SGIVS Global, under the current system. Anything submitted before July 1 will be handled by those incumbents under the existing arrangement, so applications already in the pipeline will not be orphaned by the switch.

From July 1, every fresh application flows through centres run by Al Hind Tours and Travels. The new provider will manage the full range of consular work: passport issuance and renewals, visa applications, Overseas Citizen of India (OCI) services, Police Clearance Certificates and document attestation. The Embassy says 16 service centres will operate across the Emirates, with locations, operating hours and applicable fees to be announced ahead of the transition.

Officials have stressed that steps are being taken to minimise disruption during the handover, and that detailed instructions will follow as the date approaches. Applicants have been urged to rely only on official updates from the Embassy of India in Abu Dhabi and the Consulate General of India in Dubai, rather than on second-hand information.

## Why a Quiet Switch Carries Real Risk

Transitions like this are where things go wrong for ordinary people. Service-provider handovers can mean new websites, new appointment systems, new fee structures and a learning curve for staff — exactly the friction that turns a routine passport renewal into a missed flight or a lapsed visa. Expatriates in the UAE live by hard residency deadlines; a delayed passport or a stalled attestation is not an inconvenience but a status problem that can affect employment and the right to stay.

The practical advice writes itself. Anyone with a consular task that can be completed before June 30 has reason to act now, while the familiar BLS and SGIVS systems are still running. Those who must apply after July 1 will want to wait for the Embassy to publish the new centre locations and fee schedule before paying anyone or booking an appointment — a window scammers and unofficial agents typically exploit during exactly this kind of changeover.

## Why It Matters for the Diaspora

This is the diaspora's daily reality in microcosm. For all the headlines about trade deals and remittance records, the lived experience of being an NRI is built from these small, high-stakes errands — the renewal that has to clear before a residency visa expires, the attestation a new employer demands, the OCI card a child needs. When the machinery behind those errands changes, millions of households feel it directly, even if the wider world does not notice.

There is a broader signal too. India has been steadily reorganising how it serves its overseas citizens, from new service providers in the Gulf to expanded online systems back home. The UAE switch is one piece of that churn, and it lands in the corridor that matters most: the Gulf still accounts for a large share of India's remittances and hosts nearly half its migrants. Getting consular service right in Abu Dhabi and Dubai is, for India, not a clerical detail but a test of whether it can keep faith with the diaspora that keeps so much money and goodwill flowing home.

For now, the message to every Indian family in the Emirates is simple: note the date, finish what you can before June 30, and trust only the Embassy's official channels for what comes next."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "The Consulate General of India in Dubai, which oversees consular services for the UAE's Indian community"
    img_attribution = "Wikimedia Commons"

    for q in ["Consulate General of India Dubai", "Embassy of India Abu Dhabi", "Indian passport document", "Dubai skyline UAE"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            t = commons[0]["title"].lower()
            if "passport" in t:
                img_caption = "An Indian passport, among the consular services moving to a new provider in the UAE on July 1"
            elif "dubai" in t and "consulate" not in t:
                img_caption = "The Dubai skyline; the UAE hosts roughly 3.5 million Indians, the world's largest expatriate Indian community"
            break

    if not img_url:
        px = fetch_pexels_image("passport documents application")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Passport and travel documents"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Outlook Traveller \u2014 India Announces New Visa and Passport Service Provider in UAE; Key Changes Explained",
            "Embassy of India, Abu Dhabi \u2014 official notice on appointment of Al Hind Tours and Travels LLC from July 1, 2026",
            "Consulate General of India, Dubai \u2014 transition guidance for passport, visa and consular applicants"
        ]),
        "diaspora_angle": "Every passport renewal, OCI application and attestation for the 3.5 million Indians in the UAE \u2014 the world's largest expatriate Indian community \u2014 moves to a new operator on July 1, so families should finish what they can before June 30 and trust only official Embassy channels for what comes next.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: State fuel retailers hit borrowing limits ────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India's fuel retailers hit borrowing limits")
    print("="*60)

    slug = "india-state-fuel-retailers-borrowing-limits-one-trillion-rupee-losses-price-freeze-20260619"
    headline = "India's Fuel Retailers Have Hit Their Borrowing Limit Absorbing Rs 1 Trillion in Losses to Keep Pump Prices Frozen"
    subheadline = "Oil secretary Neeraj Mittal says state-run IOC, BPCL and HPCL can barely borrow more after eating Rs 1 lakh crore of first-quarter losses to shield Indian consumers from the Iran war's oil shock. The freeze cannot hold forever — and the diaspora's families pay either way."

    body = """India's strategy for surviving the oil shock of the Iran war has been deceptively simple: make the country's three state-owned fuel retailers swallow the pain so ordinary Indians do not feel it at the pump. On Thursday, the man who oversees them admitted how close that strategy is to its limit. Oil secretary Neeraj Mittal told an industry event that Indian Oil Corporation, Bharat Petroleum and Hindustan Petroleum are now hitting their borrowing limits, having absorbed roughly Rs 1 trillion — about $10.6 billion — in revenue losses in just the first quarter of this year.

The figure is staggering, and it is the cost of a deliberate political choice. While many countries raised retail prices of petrol and diesel by 40 to 50 per cent after the war drove crude higher, India has lifted them by less than 10 per cent. The gap between what these companies pay for crude, gas and LPG and what they are allowed to charge for the finished fuel is being financed, quarter after quarter, by borrowing.

## A Freeze Built on Debt

The mechanics are unforgiving. India imports more than 80 per cent of its crude, so when the Strait of Hormuz seized up and global prices spiked, the cost of every barrel landing in India rose with it. But the government, anxious to keep inflation and public anger in check, held the line on pump prices. The three state retailers — which between them control roughly 90 per cent of India's more than 100,000 fuel stations — were left to bridge the difference out of their own balance sheets.

For a while, borrowing did the job. Now Mittal says that runway is running out. When companies of this size hit their borrowing ceilings, the options narrow fast: raise pump prices, secure direct government support, or curtail the very imports that keep the country supplied. The government has so far insisted it has no proposal to compensate the retailers for these losses, even as the oil minister himself has acknowledged that India will eventually have to assess how long the firms can sustain the bleeding.

Prime Minister Narendra Modi has leaned into conservation as a stopgap, urging citizens to travel less and save fuel, and casting India as one of the few nations that has held energy prices steady through the crisis. That message buys time and political goodwill. It does not refill the retailers' coffers.

## The Reckoning That Keeps Getting Postponed

Economists have been blunt about where this ends. With neither the government's fiscal buffers nor the oil companies' balance sheets able to withstand a prolonged shock, analysts have warned for weeks that retail fuel prices will have to rise — the only question is when. Every quarter the freeze holds is another quarter of losses piled onto state companies that also fund refinery expansion, pipelines and the clean-energy transition out of the same strained cash flows.

There is a small mercy in the timing. The recent US-Iran peace framework has pushed Brent crude back down toward $79 a barrel and eased the rupee off its lows, taking some pressure off the import bill. If that de-escalation holds, the retailers' losses could narrow and the day of reckoning could slip further into the future. But the structural problem is unchanged: India has been subsidising calm at the pump with corporate debt, and that debt has nearly run its course.

## Why It Matters for the Diaspora

For the diaspora, this is not an abstract balance-sheet story — it is about the households back home. Fuel prices in India are the master switch for inflation: they feed into the cost of food, transport and nearly everything a family buys. As long as the freeze holds, the relatives that NRIs support feel less squeeze, and the remittances sent home stretch further. The moment it breaks and pump prices jump, that cushion thins, and the monthly transfers from Dubai, London and New Jersey have to work harder.

There is a market dimension too. NRI investors hold positions in IOC, BPCL and HPCL, and in the broader Indian equity story that the diaspora has been courted to buy into. State retailers borrowing to the hilt to fund a political price freeze is precisely the kind of hidden liability that can surface in earnings, dividends and credit ratings. And the rupee — the number every remitter watches — is tied directly to the oil import bill these companies carry.

India has bought its consumers months of calm at the petrol pump. The bill for that calm is now sitting on three state balance sheets that say they can borrow little more. Whether it is paid through higher prices, government cash or a lucky break in global crude, someone pays — and for the diaspora, the someone is often family."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = None
    img_caption = "An Indian Oil fuel station; state retailers have absorbed about Rs 1 trillion in losses to keep pump prices frozen"
    img_attribution = "Wikimedia Commons"

    for q in ["Indian Oil petrol pump station", "Bharat Petroleum fuel station India", "Hindustan Petroleum filling station", "petrol pump India"]:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            img_url = commons[0]["url"]
            break

    if not img_url:
        px = fetch_pexels_image("gas station fuel pump")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A fuel station forecourt"

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
            "Reuters \u2014 Indian state fuel retailers hitting borrowing limits, says official (oil secretary Neeraj Mittal, June 18, 2026)",
            "OilPrice.com \u2014 Modi's Fuel Price Freeze Is Costing State Retailers Billions",
            "The Hindu BusinessLine \u2014 State-owned fuel retailers losing nearly Rs 600 crore daily despite price hikes"
        ]),
        "diaspora_angle": "India has frozen pump prices through the oil shock by making state retailers borrow against Rs 1 trillion in losses \u2014 a cushion that keeps inflation and the relatives NRIs support protected for now, but whose eventual breaking point will hit household budgets, the rupee and diaspora-held energy stocks alike.",
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
