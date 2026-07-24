#!/usr/bin/env python3
"""
Videshi News Writer — June 19, 2026 (Batch 2)
3 NEW articles for the "news" category:
  1. US Domestic H-1B Visa Renewal Pilot
  2. Mumbai Water Crisis / Delayed Monsoon
  3. India's Record Defence Production
Reuses helper functions from news-writer-20260619.py
"""

import os, json, requests, urllib.parse, uuid, subprocess, time, re
from datetime import datetime, timezone

# Load env
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


def fetch_wikimedia_commons_images(search_query, limit=5):
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
    """Download image, compress to JPEG, upload to Supabase storage."""
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
        import io
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
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ─── Article 1: India's OCI Program Digital Overhaul ─────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India's OCI Program Digital Overhaul")
    print("="*60)

    slug = "india-oci-rules-overhaul-2026-digital-portal-passport-update-mandate-dual-citizenship-20260619"
    headline = "India Just Rewrote the Rulebook for 4.5 Million OCI Holders. The Fine Print Forces a Hard Choice on Dual-Passport Families."
    subheadline = "A sweeping overhaul moves Overseas Citizen of India casework fully online and promises 15-day approvals, but a mandatory passport-update rule with fines, colliding with new US disclosure demands, leaves diaspora families caught between two governments."

    body = """For the roughly 4.5 million people who hold an Overseas Citizen of India card — the document that lets the global Indian diaspora live, work, and own property in India without a visa — the rules have just changed in ways both welcome and unnerving. India's Ministry of Home Affairs has overhauled the OCI program, digitising it end to end while quietly tightening obligations that could trip up families who treat the card as a set-it-and-forget-it lifetime privilege.

The headline change is convenience. OCI casework — first-time applications, renewals, and renunciations — is moving onto a single online portal, ending the duplicate-paperwork era. Indian authorities expect the digital shift to slash approval times to roughly 15 working days, down from the six to eight weeks that applicants in cities like New York, London, and Dubai have long endured. The e-OCI credential becomes the core record; the physical card, once mandatory, is now optional.

But the same overhaul carries a sting in the tail. OCI holders who fail to update their new passport details on the portal within three months of getting a new passport will face a fine of about $25, or the local equivalent. For a diaspora accustomed to renewing passports every decade and forgetting about the OCI link entirely, the new compliance clock is easy to miss — and now carries a penalty.

## A Lifetime Card With New Strings

The OCI card has always occupied an unusual middle ground. It is not citizenship — India does not permit dual nationality — but it grants most of the practical rights short of voting and government employment. For millions in the diaspora, it has been the thread keeping them legally tethered to the homeland: the document that lets them inherit family property, run businesses, and return without the indignity of a tourist visa.

The MHA's revisions expand who can hold it even as they tighten how it must be maintained. Foreign nationals can now apply for an OCI card without first completing six months of residence in India, provided they hold a valid long-term visa and their documents are in order — a meaningful easing for spouses and recent arrivals. And in a gesture echoing earlier outreach, fifth- and sixth-generation Indian-origin Tamils in Sri Lanka have been made newly eligible, broadening the card's reach to diaspora communities with thin historical paper trails.

The digital system is also being wired into India's Fast-Track Immigration Programme, linking OCI biometric data to real-time processing at major airports including Delhi and Bengaluru — a convenience for frequent flyers, and a sign of how thoroughly the credential is being folded into a single identity backbone.

## Caught Between Two Governments

The most fraught consequence has nothing to do with India alone. The tightening of OCI compliance is colliding head-on with a parallel tightening in the United States — and Indian-origin families with feet in both countries are caught in the squeeze.

Recent US guidance requires fuller disclosure of foreign allegiances and travel documents, including OCI status, on naturalisation and green-card forms such as the N-400 and I-485. Failures to disclose can be treated as misrepresentation, a serious immigration offence. At the same time, India's rules are unforgiving about dual passports: a US-born child of Indian parents who holds both an American and an Indian passport is, under Indian law, in violation — and the new digital system can flag exactly that kind of mismatch in real time.

The practical upshot is a hard choice many families have deferred for years. To stay within Indian law, US-born children of Indian parents must effectively choose between a US passport and an Indian one once they come of age; holding both, long an informal grey-zone habit, is now a flaggable violation on one side and a disclosable fact on the other. Immigration lawyers describe a sharpening compliance burden for precisely the cross-border families the OCI was meant to serve.

## What Holders Should Do Now

For the diaspora, the overhaul demands a few concrete habits. Anyone who has renewed a passport recently should log in and update the details before the three-month window lapses. Families with US-born children approaching adulthood should take advice on the passport question rather than drift. And PIO card holders, a now-defunct category folded into OCI, should confirm their status, as the older cards have ceased to be valid travel documents.

## Why It Matters for the Diaspora

This is not an abstract policy tweak — it touches the single document that most directly defines the legal relationship between overseas Indians and their homeland. For the diaspora, the OCI card is how a family keeps a grandmother's flat in Pune, how a second-generation engineer in California holds onto the option of returning, how belonging is made bureaucratically real across an ocean.

The digital overhaul makes that relationship faster and, in theory, easier to manage. But it also makes it less forgiving of inattention, and it forces into the open a dual-passport ambiguity that millions of families have quietly lived with for decades. As two governments simultaneously tighten their record-keeping, the comfortable in-between that the diaspora once occupied is narrowing. The card that was meant to simplify belonging now comes with a checklist — and a deadline."""

    print("  Sourcing image...")
    img_url = None
    img_caption = "An Indian passport and travel documents; India has overhauled the OCI program for its global diaspora"
    img_attribution = "Wikimedia Commons"

    commons = fetch_wikimedia_commons_images("Indian passport document")
    if commons:
        for c in commons:
            tl = c.get("title", "").lower()
            if "passport" in tl and "india" in tl:
                img_url = c["url"]
                break
        if not img_url:
            img_url = commons[0]["url"]

    if not img_url:
        commons2 = fetch_wikimedia_commons_images("passport immigration airport")
        if commons2:
            img_url = commons2[0]["url"]
            img_caption = "Passport and immigration documents"

    if not img_url:
        px = fetch_pexels_image("passport travel documents immigration")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A passport and travel documents"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Clark Hill PLC (via JD Supra) \u2014 May 2026 Outbound Immigration and Global Mobility Recap: India OCI Program Changes",
            "VisaVerge \u2014 India OCI Rules 2026: Digital Shift & Minor Passport Ban",
            "Ministry of Home Affairs (India) \u2014 Revised OCI Program Rules",
            "India Abroad \u2014 OCI Rules Changed 2026: New Fees, Deadlines & Update Explained"
        ]),
        "diaspora_angle": "OCI holders ARE the diaspora \u2014 4.5 million of them \u2014 and this overhaul both speeds up their casework and, colliding with new US disclosure rules, forces dual-passport families into a long-deferred choice between an American and an Indian passport.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Mumbai Water Crisis / Delayed Monsoon ────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Mumbai Water Crisis / Delayed Monsoon")
    print("="*60)

    slug = "mumbai-water-crisis-delayed-monsoon-2026-reservoirs-40-days-supply-20260619"
    headline = "Mumbai Has 40 Days of Drinking Water Left, and the Monsoon Is Running on Empty"
    subheadline = "The city is enduring its driest June in over a decade as reservoirs sink to roughly 10 per cent of capacity, forcing water cuts on construction and industry while Maharashtra waits on a monsoon that may be the weakest in 11 years."

    body = """Mumbai is a city defined by its rains. The monsoon that sweeps in off the Arabian Sea each June is woven into the rhythm of life here — the relief after a punishing summer, the flooded local-train tracks, the first cup of chai watching the deluge. This year, the rain has not come, and the silence from the sky has turned into one of the most acute water emergencies the metropolis has faced in years.

The seven lakes that supply drinking water to Mumbai's more than 20 million people have fallen to roughly 10.35 per cent of their total usable capacity — a level that, by the civic body's own reckoning, leaves the city with about 40 days of drinking water before reserves run critically dry. It is a sobering figure for a megacity in mid-June, the very month its reservoirs are supposed to begin refilling.

The cause is a monsoon that has stalled. Mumbai and the wider Maharashtra region are enduring their driest June in more than a decade, with the state receiving an estimated 75 per cent less rainfall than average across the first 16 days of the month. The India Meteorological Department now expects the monsoon to reach the region only in the last week of June, around June 22 to 25 — and forecasters warn this year's monsoon could prove the weakest in 11 years.

## The Cuts Begin

The Brihanmumbai Municipal Corporation has already moved to ration. Water supply to construction sites across the city has been suspended outright, halting a sector that is one of Mumbai's largest consumers of the resource. Industrial and commercial users have been hit with a 20 per cent cut. The measures are designed to stretch the dwindling reserves through to whenever the rains finally arrive — but they come with an economic bite, freezing building activity in one of the world's most expensive property markets.

The crisis has reignited a long-running argument about whether India's financial capital has planned adequately for a future of erratic rainfall. "Where is the long-term thinking?" asked Niranjan Hiranandani, the prominent real-estate developer and chairman of the Hiranandani Group, in remarks that captured the frustration of a business community watching the city lurch from shortage to shortage. Critics point to chronic under-investment in water recycling, rainwater harvesting, and storage even as the city's population and construction footprint swell.

## The Science of a Stalled Monsoon

Behind the dry skies lies a familiar culprit. Meteorologists point to weakening monsoon winds, with developing conditions in the Pacific dampening the systems that normally drive rain onto India's west coast.

"The monsoon circulation has been notably weak this year," said Akshay Deoras, a meteorologist at the University of Reading, attributing the sluggish advance to atmospheric patterns suppressing the winds that carry moisture inland. The monsoon delivers roughly 70 per cent of India's annual rainfall and is the lifeblood of an agricultural economy that still employs nearly half the country's workforce. A weak or late monsoon does not just mean dry taps in Mumbai; it ripples outward into the price of food on tables across the country — and, by extension, into the remittances and grocery bills of families connected to India from abroad.

## A Pattern, Not an Anomaly

For climate scientists, Mumbai's predicament fits an increasingly familiar template: monsoons that arrive late, behave erratically, and swing between extremes of drought and deluge. The same systems that leave reservoirs parched in June have, in recent years, dumped record single-day rainfall that floods the city within hours. The infrastructure built for a predictable 20th-century monsoon is straining against a 21st-century climate that no longer follows the old calendar.

## Why It Matters for the Diaspora

For the vast Mumbai and Maharashtra diaspora — among the largest contributors to the NRI communities of the Gulf, the US, and the UK — the water crisis is intensely personal. It is parents and grandparents rationing supply in family flats, relatives navigating cuts that disrupt daily life, and the anxious phone calls that follow every report of a city under strain.

There is a broader economic thread too. A weak monsoon stokes food inflation, which feeds into the cost-of-living pressures that shape how far remitted money stretches back home. For NRIs who send funds to support family in India, a bad monsoon year can quietly raise the real cost of that support — even as it raises worries about the well-being of those they left behind.

And for a diaspora that often dreams of return — of retirement homes in Pune, second properties in Mumbai's suburbs, a place to spend the monsoon months — the spectacle of India's richest city counting down its remaining days of water is a reminder that the climate of the homeland they imagine returning to is changing faster than the plans being made for it.

The rains will come, as they always do. The question Mumbai is being forced to ask, a little more urgently each year, is what happens in the lengthening gap before they do."""

    print("  Sourcing image...")
    img_url = None
    img_caption = "The Mumbai skyline; the city is enduring its driest June in over a decade as reservoirs run low"
    img_attribution = "Wikimedia Commons"

    commons = fetch_wikimedia_commons_images("Mumbai skyline monsoon rain")
    if commons:
        img_url = commons[0]["url"]

    if not img_url:
        commons2 = fetch_wikimedia_commons_images("Mumbai cityscape skyline")
        if commons2:
            img_url = commons2[0]["url"]

    if not img_url:
        px = fetch_pexels_image("Mumbai skyline city India")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The Mumbai skyline"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "climate",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "Reuters \u2014 Mumbai Faces Water Crisis as Monsoon Delays, Reservoirs Run Low",
            "DevDiscourse \u2014 Mumbai's Water Reserves Dwindle Amid Delayed Monsoon",
            "The Prevalent India \u2014 Mumbai Water Cuts: BMC Restricts Supply to Construction, Industry",
            "CurlyTales \u2014 Mumbai Has Just 40 Days of Water Left as Monsoon Stalls",
            "India Meteorological Department / University of Reading (Akshay Deoras) commentary"
        ]),
        "diaspora_angle": "The huge Mumbai and Maharashtra diaspora has family weathering the cuts firsthand, while a weak monsoon stokes food inflation that quietly raises the real cost of the money NRIs send home.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 3: India's Record Defence Production ────────────────

def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: India's Record Defence Production")
    print("="*60)

    slug = "india-record-defence-production-178-lakh-crore-fy26-exports-aatmanirbhar-20260619"
    headline = "India's Arms Factories Just Hit a Record, and the Private Sector Is Finally Getting a Real Cut"
    subheadline = "Defence production touched an all-time high of \u20b91.78 lakh crore in FY26 as exports surged past \u20b938,000 crore \u2014 the clearest sign yet that India's bid to turn from the world's biggest arms importer into a maker and seller is gaining traction."

    body = """For most of its independent history, India has been defined in the global arms trade by a single, uncomfortable label: the world's largest importer of weapons. A new set of production figures suggests that story, while far from over, is finally beginning to change — and that the change is being driven not only by sprawling state-owned giants but, increasingly, by private industry.

India's defence production reached an all-time high of ₹1.78 lakh crore in the 2025-26 financial year, Defence Minister Rajnath Singh announced — a 15.6 per cent jump over the previous year and a remarkable 110 per cent increase since FY21, when production stood at roughly ₹85,000 crore. In just five years, the value of what India's defence sector builds has more than doubled.

The export numbers are even more striking. Defence exports hit a record ₹38,424 crore, surging 62.66 per cent year-on-year — a category that barely registered a decade ago and now sees Indian-made equipment reaching dozens of countries. A nation long dependent on Russian, French, and American hardware is steadily becoming a supplier in its own right.

## The Private Sector Breaks Through

Perhaps the most consequential shift lies beneath the headline figure. The private sector's share of defence production has climbed to a record 24 per cent — roughly ₹42,000 crore — a meaningful crack in what was for decades the near-monopoly of state-owned Defence Public Sector Undertakings and ordnance factories.

The DPSUs still dominate, contributing about 76 per cent of total production. But the direction of travel is unmistakable. And in exports, the private sector's dynamism is even clearer: while DPSU exports themselves surged an extraordinary 151 per cent, the opening of the sector has drawn in private manufacturers, start-ups, and a wave of micro, small and medium enterprises into the defence supply chain. The government has set a target of ₹3 lakh crore in production and ₹50,000 crore in exports by 2029, goals that now look less aspirational than they did a few years ago.

## Aatmanirbhar Bharat, in Hardware

The numbers are the most tangible expression yet of "Aatmanirbhar Bharat" — the self-reliance drive that has become a centrepiece of government policy — translated from slogan into steel. A series of measures has underpinned the climb: successive "positive indigenisation lists" that bar the import of specified items to force domestic development, a higher share of the capital procurement budget reserved for domestic industry, and liberalised foreign direct investment rules to pull in technology and capital.

"This reflects the growing self-reliance and capability of our defence industry," Rajnath Singh said, crediting both public and private players. The strategic logic runs deeper than economics. Every artillery gun, drone, or radar built at home is one less dependency on a foreign supplier whose politics might, in a crisis, dictate whether spare parts arrive. For a country that watched sanctions and supply disruptions complicate defence ties in the past, indigenisation is as much about strategic autonomy as about industrial pride.

## From Importer to Exporter

The transformation is far from complete. India remains heavily dependent on imports for cutting-edge systems — fighter-jet engines, advanced submarines, and high-end electronics among them — and the gap between assembling foreign-designed equipment under licence and genuinely indigenous design remains wide. Critics note that a portion of "domestic" production still rests on imported components and technology transfers.

But the trajectory matters. Indian-made coastal patrol vessels, helicopters, missiles, and increasingly drones are finding buyers across Southeast Asia, Africa, the Middle East, and beyond. The country's defence-tech start-up ecosystem — much of it powered by engineers and entrepreneurs with deep ties to the global Indian diaspora — is beginning to feed into this pipeline, particularly in software, surveillance, and unmanned systems.

## Why It Matters for the Diaspora

For the Indian diaspora, the rise of a domestic defence-industrial base resonates on several frequencies. There is the straightforward pride of watching the homeland shed a dependency that has long sat awkwardly with its great-power ambitions. There is the strategic reassurance, for a community that follows India's security tensions with Pakistan and China closely, of a country better able to equip itself.

And there is opportunity. The defence-tech boom is drawing in exactly the kind of high-skilled, globally networked talent the diaspora is full of — engineers in aerospace, AI, and advanced manufacturing who increasingly see India's defence sector as a place to build rather than merely a market to sell into. Indian-origin founders and investors in the US and Europe are eyeing a sector that, until recently, was effectively closed to private and foreign participation.

The label of "world's largest arms importer" will not disappear overnight. But for the first time in a generation, the numbers are pointing the other way — and a diaspora accustomed to watching India buy its security from others is beginning to watch it build, and sell, that security itself."""

    print("  Sourcing image...")
    img_url = None
    img_caption = "Defence Minister Rajnath Singh, who announced India's record defence production for FY26"
    img_attribution = "Wikimedia Commons"

    img_url = fetch_wikipedia_person_image("Rajnath Singh")

    if not img_url:
        commons = fetch_wikimedia_commons_images("Indian Army defence equipment parade")
        if commons:
            img_url = commons[0]["url"]
            img_caption = "Indian defence equipment on display; production hit a record \u20b91.78 lakh crore in FY26"

    if not img_url:
        px = fetch_pexels_image("military defence equipment soldiers")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Military defence equipment"

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
            "Ministry of Defence / PIB \u2014 India's Defence Production Hits Record \u20b91.78 Lakh Crore in FY26",
            "The Hindu BusinessLine \u2014 Defence Production at All-Time High; Private Sector Share Climbs",
            "Outlook Business \u2014 India Defence Exports Surge 62% to Record \u20b938,424 Crore",
            "Defence Minister Rajnath Singh \u2014 Official Statement on FY26 Production Figures"
        ]),
        "diaspora_angle": "A diaspora that has long watched India rank as the world's biggest arms importer now sees it building and exporting its own security, with the defence-tech boom drawing in exactly the high-skilled, globally networked talent the diaspora is full of.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Main ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Videshi News Writer \u2014 June 19, 2026 (Batch 2)")
    print("=" * 60)

    results = []

    art1 = write_article_1()
    results.append(("OCI Program Digital Overhaul", art1))

    art2 = write_article_2()
    results.append(("Mumbai Water Crisis", art2))

    art3 = write_article_3()
    results.append(("Record Defence Production", art3))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, art_id in results:
        status = "\u2713 OK" if art_id else "\u2717 FAILED"
        print(f"  {status} \u2014 {name}: {art_id}")

    failed = sum(1 for _, aid in results if not aid)
    print(f"\nTotal: {len(results)} articles, {len(results)-failed} succeeded, {failed} failed")
