#!/usr/bin/env python3
"""
Videshi News Writer — June 19, 2026 batch
3 articles for the "news" category
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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
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
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
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
                print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def download_and_compress(url, slug):
    """Download image, compress to JPEG, upload to Supabase storage."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed ({r.status_code}): {url[:80]}")
            # curl fallback for Wikimedia 429
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
            print(f"  ⚠ Not an image or too small: {ct}, {len(r_content)} bytes")
            return None

        # Compress with PIL
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
            print(f"  ⚠ Compressed image too small: {len(compressed)} bytes")
            return None

        print(f"  ✓ Compressed: {len(r_content)} → {len(compressed)} bytes")

        # Upload to Supabase storage
        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"

        # Try delete first (ignore errors)
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
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None

    except Exception as e:
        print(f"  ⚠ Download/compress error: {e}")
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
        print(f"  ✓ Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ─── Article 1: Rupee Recovery ────────────────────────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Rupee Recovery — Oil Plunge + RBI Defence")
    print("="*60)

    slug = "indian-rupee-recovery-oil-plunge-rbi-fx-book-94-per-dollar-20260619"
    headline = "The Rupee Clawed Back From 97. Now the RBI's Own $110 Billion Bet Is What Stands Between It and a Real Rally."
    subheadline = "A collapse in oil prices after the US-Iran deal pulled the currency to a six-week high near 94.3. But economists say the central bank's record short-dollar forward book will absorb the inflows before NRIs feel the gain."

    body = """For a month, the Indian rupee looked like a one-way bet on the way down. It struck a record low of nearly 97 to the dollar on May 20, dragged there by a war in West Asia that sent crude oil prices soaring and foreign investors fleeing. This week, the story reversed — and the speed of the turn says as much about the fragility underneath as the relief on top.

The rupee climbed to 94.2925 per dollar this week, its strongest level since May 7 and a six-week high, before settling back near 94.50. The year-to-date decline has narrowed to 5.6 per cent, from a far uglier print just weeks ago. The trigger was simple: Brent crude crashed more than 8 per cent over a few sessions, falling below $80 a barrel, after the United States and Iran reached an interim deal to end their war and reopen the Strait of Hormuz.

For an economy that imports nearly 90 per cent of its oil, cheaper crude is the single most powerful lever on the currency. Every dollar off the barrel eases the import bill, narrows the trade deficit, and cools the imported inflation that has kept wholesale prices running at a six-month high of 9.68 per cent.

## The RBI's Quiet Hand

But the rally is not purely a market story. On June 5, the Reserve Bank of India rolled out a package of measures explicitly designed to pull dollars into the economy — without touching interest rates or abandoning its "neutral" stance. Banks were encouraged to raise foreign-currency deposits, and the central bank offered to absorb the currency risk through swaps.

That is where the catch lies. To defend the rupee on the way down, the RBI built up an enormous position in the forward market. Its short-dollar forward book — essentially a promise to deliver dollars later — is estimated by foreign-bank officials to have ballooned to an all-time high of nearly $110 billion, up from $96 billion in April. India's headline foreign-exchange reserves, meanwhile, have fallen from a peak of $728.5 billion in March to $681.6 billion.

Now, as dollars flow back in on the back of cheaper oil and the central bank's incentives, much of that inflow will not push the rupee higher. It will be soaked up by the RBI as it quietly unwinds that forward book and rebuilds its depleted reserve buffer.

"We do not expect a significant appreciation in the INR," analysts at Goldman Sachs wrote, noting the inflows are "likely to be absorbed by the RBI through rebuilding of its FX buffers, including unwinding a significantly large short dollar forward book."

## A Managed Range, Not a Free Rally

Sakshi Gupta, principal economist at HDFC Bank, said the RBI's drive to rebuild reserves "alongside the sizeable overhang of its forward book are expected to be a drag on the rupee and keep its upside limited." Traders are also bracing for month-end importer payments and maturities in the non-deliverable forwards market that typically pull the currency back down.

Victor Roy, head of treasury at CTBC Bank, sees room for the rupee to firm toward 93.25 in the near term — but warns against expecting "a one-way rally." The strength, in other words, is real but capped: a managed range trade engineered as much in Mumbai's central bank as in the global oil pits.

There is one more variable hanging over everything: the US Federal Reserve. Its policy decision this week — the first under new Chair Kevin Warsh — was watched closely for whether the central bank would drop its last projected 2026 rate cut. A hawkish Warsh puts a floor under the dollar and caps the rupee; a dovish acknowledgment that the oil shock is fading gives the rupee more room to run.

## Why It Matters for the Diaspora

For the millions of non-resident Indians who send money home, the exchange rate is not an abstraction — it is the difference in what their dollars, pounds, and dirhams are worth to family in India. A weaker rupee, paradoxically, stretches every remitted dollar further, which is part of why diaspora inflows surged to a record $135.46 billion in FY25.

For NRIs holding NRE and FCNR deposits, the calculus is sharper still. The RBI's June package was designed to make those very deposits more attractive, with some banks lifting dollar deposit rates toward 7 per cent. The unusual window — a recovering but still cheap rupee, elevated deposit rates, and a central bank actively courting foreign currency — is precisely the kind of moment NRI treasury desks watch for.

The question is how long it lasts. The rupee's fate now rests on three things outside India's control: whether the fragile US-Iran truce holds and keeps oil cheap, whether the Fed signals an end to its easing cycle, and whether foreign investors return to Indian equities in size. Until then, the currency's recovery is less a vote of confidence than a temporary reprieve — one the RBI is carefully rationing."""

    print("  Sourcing image...")
    img_url = None
    img_caption = "The Reserve Bank of India headquarters in Mumbai, where policymakers have rolled out measures to attract dollar inflows"
    img_attribution = "Wikimedia Commons"

    commons = fetch_wikimedia_commons_images("Reserve Bank of India building Mumbai")
    if commons:
        for c in commons:
            tl = c.get("title", "").lower()
            if "reserve bank" in tl or "rbi" in tl:
                img_url = c["url"]
                break
        if not img_url:
            img_url = commons[0]["url"]

    if not img_url:
        commons2 = fetch_wikimedia_commons_images("Indian rupee currency notes")
        if commons2:
            img_url = commons2[0]["url"]
            img_caption = "Indian rupee banknotes; the currency has clawed back from a record low near 97 to the dollar"

    if not img_url:
        px = fetch_pexels_image("Indian rupee currency money")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Indian rupee banknotes"

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
            "Reuters — Rupee Hits Five-Week High After Oil Plunges; Traders Eye Further Rally",
            "Reuters — Rupee Nearly Flat as Oil-Led Rally Faces Off Against Dollar Demand; Fed Verdict Looms",
            "Reuters — Indian Rupee's Oil Relief Capped by RBI's FX Book, Interest Payment Hedges",
            "The Hindu BusinessLine — Weekly Rupee View: Recovery Faces Test",
            "Goldman Sachs / HDFC Bank analyst notes"
        ]),
        "diaspora_angle": "The exchange rate decides what every remitted dollar is worth to family in India, and NRIs weighing FCNR and NRE deposits now face a rare window of high deposit rates and a still-cheap but recovering rupee.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Record Remittances ────────────────────────────────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Record Remittances — $135 Billion Lifeline")
    print("="*60)

    slug = "india-record-remittances-135-billion-diaspora-trade-deficit-cushion-20260619"
    headline = "Indians Abroad Sent Home a Record $135 Billion. It Quietly Covered Nearly Half the Trade Deficit."
    subheadline = "On the UN's International Day of Family Remittances, the numbers tell a story of a diaspora that has become India's most reliable line of external defence — and a center of gravity that has shifted from the Gulf to Silicon Valley."

    body = """India just did something no other country in history has done twice over. In the fiscal year that ended in March, overseas Indians sent home a record $135.46 billion in remittances — a 14 per cent jump on the prior year — cementing India's position not just as the world's largest recipient of diaspora money, but as the only nation ever to cross the $100 billion mark, a threshold it has now blown past for several years running.

The figure landed in the spotlight this week as the world marked the United Nations' International Day of Family Remittances on June 16. And the scale of it is easy to underappreciate: those inflows covered roughly 47 per cent of India's entire merchandise trade deficit. In an economy that imports far more goods than it exports, the money your cousin in New Jersey or your uncle in Dubai wires home is, in aggregate, one of the load-bearing walls of the national balance sheet.

## A Number That Doubled in Eight Years

The trajectory is steep. India received $61 billion in remittances in 2016-17. By FY25 that had more than doubled to $135.46 billion, according to Reserve Bank of India data. The UN's own World Migration Report 2026 put the calendar-2024 figure even higher, at more than $137 billion, with South Asia recording the fastest remittance growth of any region at 11.8 per cent.

For context, the second-largest recipient on earth, Mexico, took in roughly $68 billion — barely half of India's haul. The Philippines, in third, received about $40 billion.

## The Center of Gravity Has Moved

The more revealing shift is not the size but the source. For decades, the archetypal Indian remitter was a construction worker or nurse in the Gulf, wiring a portion of a modest wage back to a village. That story is changing.

Today, the United States, the United Kingdom, and Singapore together account for around 45 per cent of all remittances into India, with the US alone contributing over 23 per cent. The Gulf Cooperation Council countries — long the dominant source — have seen their share steadily slip, buffeted by volatile oil prices and a structural move away from low-skilled labour.

What this reflects is a fundamental change in who the Indian migrant is. The flow has tilted from less-skilled labour migration toward high-skilled migration: the software engineer in Seattle, the physician in Houston, the analyst in London. These are people earning OECD salaries, and the money they send carries the weight of that earning power.

The rise of cheaper digital transfers has amplified the trend. The expansion of India's Unified Payments Interface for cross-border transactions in Singapore, France, and the UAE has cut the cost of sending money home, encouraging more frequent and more formal flows that once might have travelled through informal channels.

## A Cushion That Cannot Be Taken for Granted

The diaspora's dependability is precisely why economists are now warning against complacency. With India's foreign-exchange reserves at around $681 billion and the current account deficit having narrowed sharply — to $15 billion in the first half of FY26 from $25.3 billion a year earlier — much of that resilience traces directly to remittances and other invisible earnings offsetting the goods-trade gap.

But that lifeline runs straight through the immigration policies of other governments. The same US that supplies nearly a quarter of India's remittances has imposed a $100,000 fee on new H-1B petitions and tightened the screws on the very skilled-worker pipeline that generates those high-value transfers. Tighter visa regimes in Canada and the UK threaten the next generation of remitters before they ever arrive. A diaspora that has been treated as a permanent fixture of India's external accounts is, in fact, contingent on doors staying open abroad.

## Why It Matters for the Diaspora

For the NRIs and overseas Indians who make up these flows, the record figure is a reminder that their individual decisions — to send money for a parent's medical bill, a sibling's tuition, a family home — aggregate into something with macroeconomic weight. The Indiaspora forum, marking the remittance day with a panel titled "Roots, Returns and Remittances," framed it as the diaspora "fuelling India's future."

There is also a personal-finance angle worth watching. With the rupee recovering from record lows and Indian banks lifting dollar-deposit rates for NRIs toward 7 per cent, the channels for moving money home are being actively sweetened by Indian policymakers eager to keep the inflows coming.

The deeper truth is that India's relationship with its diaspora has quietly become one of mutual dependence. The migrants rely on the opportunities abroad; the homeland increasingly relies on what they send back. As Prime Minister Narendra Modi made a point of thanking the community first on his recent European tour, the gratitude was not merely ceremonial. At $135 billion a year, it is also arithmetic."""

    print("  Sourcing image...")
    img_url = None
    img_caption = "Indian rupee banknotes alongside US dollars; overseas Indians sent home a record $135.46 billion in FY25"
    img_attribution = "Wikimedia Commons"

    commons = fetch_wikimedia_commons_images("Indian rupee dollar currency exchange money")
    if commons:
        img_url = commons[0]["url"]

    if not img_url:
        commons2 = fetch_wikimedia_commons_images("money transfer remittance currency")
        if commons2:
            img_url = commons2[0]["url"]

    if not img_url:
        px = fetch_pexels_image("money transfer currency exchange dollars")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Currency notes representing global money transfers"

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
            "IBEF — India Remains World's Largest Recipient of Remittances, $135.4 Billion in FY25",
            "Reserve Bank of India / Economic Survey 2025-26 — Remittance Data",
            "IOM UN World Migration Report 2026 — India Top Remittance Recipient",
            "Mint — Diaspora Dollars: Don't Take These Flows for Granted",
            "German Federal Statistical Office (Destatis) — India Largest Recipient of Remittances Globally"
        ]),
        "diaspora_angle": "Overseas Indians are the source of this record $135 billion lifeline, and the same US visa crackdown squeezing the diaspora directly threatens the high-skilled remittance pipeline India now leans on.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 3: Yoga Day at the Lincoln Memorial ──────────────────

def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: Yoga Day at the Lincoln Memorial")
    print("="*60)

    slug = "international-yoga-day-2026-lincoln-memorial-washington-diaspora-healthy-aging-20260619"
    headline = "For the First Time, the Diaspora Unrolls Its Mats at the Lincoln Memorial for Yoga Day"
    subheadline = "The Indian Embassy chose one of America's most sacred civic spaces for the 12th International Day of Yoga, anchoring a global campaign built this year around 'Yoga for Healthy Aging.'"

    body = """On Friday morning, the steps where Martin Luther King Jr. told America about his dream and where Lincoln's marble gaze has watched over the nation for a century became something else: an open-air yoga studio for the Indian diaspora. The Indian Embassy in the United States chose the Lincoln Memorial as the venue for the 12th International Day of Yoga, an unusually symbolic setting for a celebration that has grown, in just over a decade, from a UN resolution into a global movement.

"We're celebrating #InternationalDayOfYoga2026 at the iconic Lincoln Memorial on Friday, June 19, 2026," the embassy announced on X, inviting practitioners across the Washington region to gather at the monument. The choice of venue was deliberate. Few American landmarks carry the civic weight of the Lincoln Memorial, and staging a quintessentially Indian practice there is a statement about how deeply the diaspora has woven itself into the fabric of its adopted home.

## A Theme Built for an Ageing Diaspora

The official International Day of Yoga falls on June 21 — the summer solstice, the longest day of the year in the Northern Hemisphere, chosen when India first proposed the observance to the United Nations in 2014. This year's global theme is "Yoga for Healthy Aging," an initiative framing the ancient discipline as a tool for extending life expectancy, preserving flexibility, and supporting proactive wellness into later years.

That theme lands with particular force for the Indian American community, one of the country's fastest-growing and now visibly maturing immigrant populations. The first large waves of Indian professionals who arrived in the 1960s, 70s, and 80s are now entering their seventies and eighties — a generation for whom "healthy aging" is not a slogan but a daily concern, often navigated far from the extended-family support structures of India.

"Yoga is the pause button that humanity needs to breathe, balance, and become whole again," Prime Minister Narendra Modi said in a message marking the celebrations.

## From New Delhi to Times Square

The Washington gathering is one node in a sprawling global campaign. In New York, the festivities will center on Times Square — one of the most photographed public spaces on earth — and be headlined by Padma Shri H.R. Nagendra, the yoga scholar who guides Modi's personal practice and serves as president of Bengaluru's S-VYASA University. Nagendra is travelling to New York as chief guest for the June 21 event, which is expected to draw thousands.

The spread of these events across iconic American venues reflects how thoroughly yoga has crossed over from a diaspora practice into the American mainstream. Tens of millions of Americans now practise some form of yoga, and the discipline has become one of India's most successful cultural exports — a point of soft power that Indian diplomacy has been keen to amplify since the UN first declared the day in 2014.

## More Than a Photo Opportunity

For the Indian Embassy, the choreography of these events serves a dual purpose. There is the cultural diplomacy — projecting India's heritage onto the world's most recognisable stages. But there is also a community-building function that matters quietly and locally: bringing together first-generation immigrants, their American-born children, and the growing cohort of Indian-origin seniors in a shared ritual that needs no translation.

That intergenerational dimension is where this year's "Healthy Aging" theme connects most directly to diaspora life. For families spread across continents — a parent in Bengaluru, a child in Boston — practices that support physical and mental well-being into old age address one of the diaspora's most persistent anxieties: how to care for ageing relatives, and eventually themselves, across distance and time zones.

## Why It Matters for the Diaspora

For the Indian community in America, gatherings like Friday's are about more than downward dogs on the National Mall. They are public assertions of belonging at a moment when the broader US-India relationship and the diaspora's place in American life are under unusual strain — from visa crackdowns to isolated incidents of anti-India hostility that have rattled the community in recent months.

Choosing the Lincoln Memorial, a monument to unity and to the idea that the nation belongs to all who call it home, sends its own message. The diaspora is not asking for permission to practise its heritage in the heart of American democracy. It is simply unrolling its mat — and inviting everyone else to join.

As the sun climbs over the Reflecting Pool and a few thousand people move through their sun salutations in the shadow of Lincoln, the scene captures something true about the Indian American story in 2026: increasingly confident, visibly rooted, and determined to age — as a community — with grace."""

    print("  Sourcing image...")
    img_url = None
    img_caption = "The Lincoln Memorial in Washington, D.C., the venue for the Indian Embassy's International Day of Yoga 2026 celebration"
    img_attribution = "Wikimedia Commons"

    commons = fetch_wikimedia_commons_images("Lincoln Memorial Washington DC")
    if commons:
        for c in commons:
            tl = c.get("title", "").lower()
            if "lincoln memorial" in tl:
                img_url = c["url"]
                break
        if not img_url:
            img_url = commons[0]["url"]

    if not img_url:
        commons2 = fetch_wikimedia_commons_images("International Day of Yoga")
        if commons2:
            img_url = commons2[0]["url"]
            img_caption = "Participants at an International Day of Yoga gathering"

    if not img_url:
        px = fetch_pexels_image("yoga group outdoor sunrise")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A group yoga session at sunrise"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-culture",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Indian Eye — Indian Embassy to Celebrate International Day of Yoga 2026 at Lincoln Memorial",
            "Indian Embassy Washington DC (@IndianEmbassyUS) — Official X Announcement",
            "Ministry of AYUSH / UN — International Day of Yoga 2026 Theme: Yoga for Healthy Aging"
        ]),
        "diaspora_angle": "An ageing first generation of Indian Americans makes this year's 'Healthy Aging' theme deeply personal, while the Lincoln Memorial venue stakes the diaspora's claim to belonging at a tense moment in US-India ties.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Main ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Videshi News Writer — June 19, 2026")
    print("=" * 60)

    results = []

    art1 = write_article_1()
    results.append(("Rupee Recovery", art1))

    art2 = write_article_2()
    results.append(("Record Remittances", art2))

    art3 = write_article_3()
    results.append(("Yoga Day Lincoln Memorial", art3))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, art_id in results:
        status = "✓ OK" if art_id else "✗ FAILED"
        print(f"  {status} — {name}: {art_id}")

    failed = sum(1 for _, aid in results if not aid)
    print(f"\nTotal: {len(results)} articles, {len(results)-failed} succeeded, {failed} failed")
