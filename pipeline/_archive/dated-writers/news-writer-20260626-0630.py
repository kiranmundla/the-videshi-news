#!/usr/bin/env python3
"""
Videshi News Writer — June 26, 2026 (06:30 UTC / June 25 23:30 PDT run)
2 NEW articles, dedup-checked against last ~30 news articles:
  1. India hikes passport fees across all categories from July 1, 2026 —
     first revision in 14 years; 36-page adult passport Rs 1,500 -> Rs 2,500,
     tatkal Rs 3,500 -> Rs 5,000, lost/damaged up to Rs 8,500. Directly hits
     diaspora who renew/replace passports abroad. NOT covered.
  2. Air India 'Easy Connect' hub-and-spoke flights launch from Varanasi
     June 25 — Tier-2/3 city flyers do baggage check-in + international
     immigration at origin airport, transit Delhi as intl pax, no re-check.
     Phased rollout. Big for diaspora flying home from smaller cities. NOT covered.
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
load_env(os.path.expanduser('~/workspace/.env.supabase'))
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


# ─── Article 1: India passport fee hike from July 1 ───

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: India passport fee hike from July 1")
    print("="*60)

    slug = "india-passport-fee-hike-july-1-2026-normal-tatkal-minor-lost-damaged-mea-amendment-rules-20260625"
    headline = "India Just Raised Passport Fees for the First Time in Years. Here's the New Price List."
    subheadline = "From July 1, a basic adult passport jumps from Rs 1,500 to Rs 2,500 and a lost-passport replacement under Tatkal can run to Rs 8,500. The Ministry of External Affairs has revised charges across every category, from minors to police clearance certificates."

    body = """For millions of Indians at home and abroad, the passport is the one document that makes everything else possible \u2014 a job in the Gulf, a degree in Canada, a visa stamp for the United States, a flight home for a parent's funeral. Starting July 1, 2026, getting or renewing one will cost noticeably more. The Ministry of External Affairs has revised passport fees across the board through the Passports (Amendment) Rules, 2026, the first broad fee increase in over a decade.

The headline change is simple: a fresh or reissued 36-page passport for an adult will cost Rs 2,500, up from Rs 1,500. The thicker 60-page booklet, favoured by frequent flyers who burn through visa pages, rises to Rs 3,500 from Rs 2,000. The new rates were notified through a gazette dated June 20 and published by the ministry on June 25, taking effect at the start of next month.

## What the New Fees Look Like

The increases run through every category. Under the expedited Tatkal scheme, an adult 36-page passport will now cost Rs 5,000 instead of Rs 3,500, while a 60-page Tatkal booklet rises to Rs 6,000 from Rs 4,000. Replacing a lost, stolen or damaged passport \u2014 already a stressful and expensive errand \u2014 gets pricier too: Rs 5,000 for a 36-page booklet under normal processing and Rs 6,000 for 60 pages, with the Tatkal route for a lost document climbing as high as Rs 7,500 to Rs 8,500.

Minors are not spared. A fresh or reissued 36-page passport for a child under 18 will now cost Rs 1,750, up from Rs 1,000, with Tatkal charges rising in step. Given that roughly a quarter to a third of the 13 to 14 million passports India issues each year go to minors, that change touches a very large number of families planning their children's first trips abroad.

Several miscellaneous services have also been re-priced. Police Clearance Certificates, surrender certificates and Global Entry Programme verification \u2014 documents that overseas Indians frequently need for jobs, residency and trusted-traveller schemes \u2014 will now cost Rs 750 each, while a Certificate of Identity is fixed at Rs 1,000. Passport validity is unchanged: ten years for adults, five years (or until age 18) for minors.

## A Fee Frozen for Years, Now Catching Up

The revision is striking partly because it follows such a long pause. Passport fees in India had stayed largely flat for years even as the cost of producing the documents \u2014 now chip-enabled e-passports with embedded biometric data \u2014 climbed. The government has been rolling out e-passports that speed up border crossings and harden security, and the fee increase lands as that upgrade scales nationwide. Officials frame the higher charges as bringing fees in line with the real cost of issuing a modern travel document.

The timing is also politically delicate. The hike was notified just as the ministry was fielding criticism over a separate statement that "a passport is a travel document and not proof of citizenship" \u2014 a remark that unsettled some applicants. For ordinary citizens, the practical upshot is simpler: the document is about to cost more, so the calendar matters.

## Why It Matters for the Diaspora

For non-resident Indians, the change is more than a domestic line item. Indian missions abroad set their consular fees in local currency benchmarked to the rupee schedule, so a fee revision in New Delhi typically ripples out to embassies and consulates worldwide in the following weeks. An NRI renewing a passport in Dubai, London or New Jersey can expect the local fee to track the new structure once missions update their schedules.

The lost-and-damaged category is where the diaspora feels it most. Passports get lost, soaked or run out of pages far from home, and the replacement charges \u2014 now up to Rs 8,500 under Tatkal \u2014 are the steepest of the lot. The practical advice writes itself: if you or your children have a renewal coming up and the booklet is eligible now, filing before July 1 locks in the old rate. Anyone applying after that date simply pays the new schedule. And with India simultaneously pushing e-passports and digital application tools like DigiLocker integration, the process itself is getting faster even as it gets dearer \u2014 a trade most travellers will accept, as long as they know the new numbers before they reach the counter."""

    img_url, ititle = pick_commons([
        "Indian passport booklet",
        "Indian passport",
        "Passport of India",
        "Bharat passport",
        "Republic of India passport"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "An Indian passport. The Ministry of External Affairs has raised passport fees across all categories effective July 1, 2026"

    if not img_url:
        px = fetch_pexels_image("passport travel document")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "India is raising passport fees across all categories from July 1, 2026"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-services",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Hindu BusinessLine (thehindubusinessline.com, 25 June 2026) \u2014 'Govt increases passport fees across categories from July 1': under the Passports (Amendment) Rules, 2026 notified by the MEA, a fresh/reissued 36-page adult passport will cost Rs 2,500 (up from Rs 1,500) and a 60-page Rs 3,500 (up from Rs 2,000); lost/damaged replacement Rs 5,000 (36-page) and Rs 6,000 (60-page); minors 36-page Rs 1,750 (up from Rs 1,000); Tatkal 36-page Rs 5,000 (up from Rs 3,500), 60-page Rs 6,000 (up from Rs 4,000); Tatkal lost/damaged Rs 7,500 (36-page) and Rs 8,500 (60-page); PCC/surrender certificate/Global Entry verification now Rs 750; Certificate of Identity Rs 1,000; adult passports valid 10 years, minors 5 years or until 18.",
            "Online Maharashtra / PTI (onlinemaharashtra.com, 25 June 2026) \u2014 'Passport Charges Hiked To Rs 2,500 From July 1': MEA amended the Passports Rules, 1980 via the Passports (Amendment) Rules, 2026; notification dated June 20, published June 25, in force from July 1, 2026; cites section 24 of the Passports Act, 1967; revised Schedule IV distinguishes applicants 18+ (and minors 15-18 applied under that class) from minors under 18.",
            "Dainik Bhaskar English (bhaskarenglish.in, 25 June 2026) \u2014 'Passport Fees Hike India July 1 | Tatkaal Rs 5,000; Lost Rs 8,500': MEA gazette notification revising passport fees across categories; standard 36-page Rs 1,500 -> Rs 2,500, Tatkal Rs 3,500 -> Rs 5,000, 60-page normal Rs 2,000 -> Rs 3,500 and Tatkal to Rs 6,000; lost/damaged documents up to Rs 8,500.",
            "Travelobiz (travelobiz.com, 25 June 2026) \u2014 'Indian Passport Fees to Increase From July 1: Check New Charges for Fresh, Tatkal & PCC Services': summary of revised MEA fee structure effective July 1, 2026 covering fresh passports, Tatkal applications, Police Clearance Certificates and lost passport replacements."
        ]),
        "diaspora_angle": "India is raising passport fees across every category from July 1, 2026 \u2014 a basic adult passport rises to Rs 2,500 and a lost-passport Tatkal replacement to as much as Rs 8,500 \u2014 and because Indian missions abroad benchmark consular fees to the domestic schedule, NRIs renewing or replacing passports overseas should expect higher charges and can lock in the old rate by filing before July 1.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Air India 'Easy Connect' hub-and-spoke flights ───

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Air India 'Easy Connect' hub-and-spoke flights")
    print("="*60)

    slug = "air-india-easy-connect-hub-spoke-flights-varanasi-tier-2-3-immigration-origin-airport-baggage-checkin-20260625"
    headline = "You Can Now Clear Immigration in Varanasi and Fly to the World Through Delhi Without Touching Your Bags"
    subheadline = "Air India's new 'Easy Connect' flights, launching from Varanasi on June 25, let travellers from smaller Indian cities check baggage through to their final destination and complete international immigration at their home airport. A phased rollout to more Tier-2 and Tier-3 cities is planned."

    body = """For a family flying from Varanasi to visit relatives in New Jersey, the journey has long had an awkward seam in the middle. Fly to Delhi, collect your checked bags, exit, re-check them for the international leg, then join the immigration queue at one of the country's busiest airports \u2014 all while watching the connection clock. From June 25, Air India says it has stitched that seam shut.

The airline has launched what it calls 'Easy Connect' flights, the first operational rollout of the Government of India's hub-and-spoke aviation model. Under the new system, a passenger departing Varanasi can check in once, all the way through to their final international destination, and clear international immigration formalities right there at the origin airport. They then transit Delhi as an international passenger \u2014 no collecting bags, no re-checking, no second immigration line at the hub.

## How the Hub-and-Spoke Model Works

The idea borrows from how global carriers already route traffic. Smaller "spoke" cities such as Varanasi feed into a major "hub" airport like Delhi, from which Air India's wider international network fans out. The coordination happens behind the scenes: baggage is tagged through to the destination, immigration is handled at the start of the trip, and schedules are aligned so the domestic and international legs connect smoothly.

For the traveller, the experience is meant to feel like a single trip rather than two stitched-together flights. "Through check-in to final destination" means the bag dropped in Varanasi is not seen again until the final city. "Immigration at origin" means the exit formalities happen before the first takeoff, sparing passengers the crush at Delhi's international terminal during peak hours.

Air India, the Tata Group-owned flag carrier, has been designated the lead airline for implementing the model. Chief Executive Campbell Wilson framed it as a way to make foreign travel more accessible to "Bharat" \u2014 the smaller cities and towns beyond the big metros \u2014 and to reduce Indian travellers' dependence on overseas transit hubs like Dubai, Doha and Singapore for international connections.

## A Phased Rollout Beyond Varanasi

Varanasi is the starting point, not the destination. Air India says it plans a phased expansion of Easy Connect operations to multiple Tier-2 and Tier-3 cities in the coming months, aiming to operationalise seamless international connectivity from non-metro India at scale. The ambition is to let a flyer from a smaller city reach a long list of global destinations through a single domestic connection, with the friction of the hub airport largely engineered away.

The launch fits a broader government push to spread aviation beyond the handful of metro gateways that have historically handled most of India's international traffic. By letting smaller airports handle through check-in and origin immigration, the model effectively upgrades them into international departure points without each needing its own roster of long-haul flights.

## Why It Matters for the Diaspora

For the Indian diaspora, this is a quietly significant change in how the trip home actually works. A huge share of overseas Indians trace their roots not to Delhi or Mumbai but to the towns and smaller cities of Uttar Pradesh, Bihar, Punjab, Gujarat, Kerala and beyond \u2014 places like Varanasi that sit at the spoke end of the network. For them, the old routine of collecting and re-checking bags at Delhi, often with elderly parents or young children in tow, was the most tiring part of the journey.

Easy Connect targets exactly that pain point. A grandparent flying out to spend the summer with grandchildren abroad, or a worker returning to a Gulf posting after a visit home, can now begin and end the bureaucratic part of the trip at a familiar local airport rather than navigating a giant transit hub mid-journey. It also makes smaller home cities more viable as genuine international starting points, which over time can mean more route options and less reliance on a long domestic hop to a metro before any overseas flight even begins. As the rollout widens city by city, the practical promise is a simpler door-to-door journey between the diaspora's adopted homes and the towns they still call home."""

    img_url, ititle = pick_commons([
        "Air India Boeing 787 Dreamliner",
        "Air India aircraft Tata",
        "Lal Bahadur Shastri Airport Varanasi",
        "Air India airplane",
        "Varanasi airport terminal"
    ])
    img_attribution = "Wikimedia Commons"
    img_caption = "An Air India aircraft. The airline's new 'Easy Connect' flights launch from Varanasi under the government's hub-and-spoke model"

    if not img_url:
        px = fetch_pexels_image("airport terminal airplane travel")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Air India's 'Easy Connect' flights let travellers from smaller cities clear immigration at their home airport"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "travel",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Hindu BusinessLine (thehindubusinessline.com, 25 June 2026) \u2014 'Air India to make foreign travel more accessible to Bharat: AI CEO': Air India CEO and MD Campbell Wilson says the newly launched 'Easy Connect' initiative seeks to make international travel more accessible to passengers from smaller Indian cities and reduce dependence on overseas transit hubs; service lets Tier-2/Tier-3 city passengers connect to international destinations via India-based hubs; commences from Varanasi on June 25 with Air India as lead carrier; phased rollout planned; under the hub-and-spoke model 'spoke' cities like Varanasi connect to 'hub' airports like Delhi; features through check-in to final destination and immigration clearance at point of origin.",
            "Air India Newsroom (airindia.com press release) \u2014 'From your home city to the world: Air India introduces Easy Connect flights, leads rollout from Varanasi on 25 June': Air India opened bookings for first flights under the Government of India's hub-and-spoke model branded 'Easy Connect'; travellers from Tier-2/Tier-3 cities such as Varanasi can drop baggage and complete immigration at origin airport and travel seamlessly worldwide; through check-in to final destination with no need to collect or re-check baggage at the hub (Delhi); immigration at origin avoids queues at the hub; phased rollout across multiple cities planned.",
            "The Hindu BusinessLine (thehindubusinessline.com) \u2014 'Air India to launch hub-and-spoke international connectivity flights from June 25': Air India commences operations under the Centre's hub-and-spoke aviation model from June 25, Varanasi the first spoke city connected to the airline's international network through Delhi; passengers complete baggage check-in and international immigration formalities at origin before connecting overseas via Delhi; first operational rollout of the hub-and-spoke framework; travellers transit Delhi as international passengers."
        ]),
        "diaspora_angle": "Air India's new 'Easy Connect' hub-and-spoke flights, launching from Varanasi on June 25 with a phased rollout to more Tier-2 and Tier-3 cities, let travellers check baggage through to their final destination and clear international immigration at their home airport \u2014 a direct win for the large share of the diaspora whose roots are in smaller Indian cities and who have long endured collecting and re-checking bags and a second immigration queue at Delhi mid-journey.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    print("Videshi News Writer \u2014 2026-06-26 06:30 UTC run")
    id1 = write_article_1()
    id2 = write_article_2()
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Article 1 (India passport fee hike July 1): {'OK id=' + str(id1) if id1 else 'FAILED'}")
    print(f"Article 2 (Air India Easy Connect flights): {'OK id=' + str(id2) if id2 else 'FAILED'}")
