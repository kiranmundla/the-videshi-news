#!/usr/bin/env python3
"""
Videshi News Writer — June 23, 2026 (18:30 UTC run)
2 NEW articles, both fresh & distinct from prior runs (which covered SpaceX,
NEET re-exam, Iran sanctions/oil, foreign-investor return, USTR Delhi trade,
China normalisation, PMI, RBI NRI deposits, Jio/NSE IPO, Russian crude, H-1B
$100k fee, student-visa duration, citizenship fee, CUET results, FCRA rules,
July Visa Bulletin EB-2, $750 expedited interview pilot, study-abroad slowdown,
Anil Menon ISS launch):
  1. India's drug regulator flagged 159 medicine samples — including common
     blood-pressure, diabetes, antibiotic and supplement brands — as Not of
     Standard Quality in its latest May alert, one flagged spurious. A
     diaspora-health-safety story about the medicines NRIs carry back and the
     "pharmacy of the world" reputation. (health — drug-safety angle)
  2. Adani's Mundra Airport in Kutch, Gujarat launches its first scheduled
     commercial flights via Star Air, as the group unveils a ~Rs 1 lakh crore,
     five-year airport expansion plan. A diaspora-roots / infrastructure story
     opening Kutch — a heartland for the Gujarati diaspora — to direct air
     travel. (economy — infrastructure / diaspora-roots angle)
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


# \u2500\u2500\u2500 Article 1: CDSCO 159 medicines fail quality test \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: CDSCO drug-quality alert")
    print("="*60)

    slug = "india-drug-regulator-159-medicines-fail-quality-test-may-nsq-alert-spurious-20260623"
    headline = "India's Drug Regulator Just Flagged 159 Medicines as Substandard. Some Are Drugs You Take Every Day."
    subheadline = "In its latest monthly check, the Central Drugs Standard Control Organisation declared 159 samples 'Not of Standard Quality' and one outright spurious \u2014 covering common blood-pressure pills, diabetes tablets, antibiotics and vitamin supplements made by household-name companies. For a diaspora that treats India as its pharmacy, the list is a recurring uncomfortable read."

    body = """India's drug regulator has flagged 159 samples of medicines as "Not of Standard Quality" during its routine surveillance for the month of May, and identified one sample as outright spurious in Assam \u2014 the latest entry in a monthly ritual that keeps turning up familiar, widely-used drugs. Of the 159 failed samples, 46 were declared substandard by central drug laboratories and 113 by state laboratories, according to the Central Drugs Standard Control Organisation (CDSCO).

The regulator was careful to add the caveat it issues every month: the findings apply only to the specific batches tested, and do not mean that other batches of the same products are substandard. But the pattern, repeated alert after alert, is what unsettles patients and pharmacists alike.

## What Failed, and Why

The medicines that turn up on these lists are rarely obscure. Recent CDSCO alerts have flagged batches of telmisartan (a blood-pressure drug), glimepiride and metformin (anti-diabetics), pantoprazole (an acidity medicine), paracetamol, common antibiotics such as amoxicillin-clavulanate and cefixime, and even calcium and vitamin D3 supplements \u2014 the kind of products that sit in tens of millions of Indian medicine cabinets. Manufacturers named across these monthly lists have included well-known firms alongside smaller contract producers clustered in pharmaceutical hubs like Baddi in Himachal Pradesh and the Roorkee belt in Uttarakhand.

The reasons for failure are technical but consequential. The most common is an "assay" failure \u2014 the active ingredient is present in the wrong amount, meaning a patient may be getting too little or too much of the drug. Others fail "dissolution" tests, which measure how the tablet releases its medicine into the body; a pill that does not dissolve properly may not work at all. Injectable products are sometimes flagged for sterility failures, particulate contamination or pH problems \u2014 defects that can be dangerous when a drug goes straight into the bloodstream. A drug declared "spurious," as the single Assam sample was, is a more serious matter still: it suggests deliberate fakery rather than a manufacturing lapse.

## A Pattern, Not a One-Off

The May numbers are not an aberration. Data placed before Parliament shows that of roughly 1.16 lakh samples tested in 2024-25, some 3,104 were declared Not of Standard Quality and 245 were found spurious or adulterated \u2014 and over the preceding five years, more than 14,300 samples failed quality tests out of nearly 4.9 lakh examined. The monthly alerts that CDSCO publishes, typically flagging 100 to 160 samples at a time, are the granular face of those aggregate figures.

The backdrop makes the stakes vivid. India is the world's largest supplier of generic medicines, exporting to more than 200 countries and earning the nickname "the pharmacy of the world." But that reputation has been bruised by a string of tragedies \u2014 most recently the deaths of more than 140 children linked to contaminated cough syrups, which pushed the government to reclassify cough syrup as a prescription-only drug. Quality control, long the soft underbelly of a low-cost manufacturing model, is now a matter of national reputation as much as domestic health.

## Why the Diaspora Should Care

For the Indian diaspora, this is not a distant domestic-policy story. Millions of NRIs treat India as their de facto pharmacy: they stock up on blood-pressure pills, diabetes medication, antibiotics and supplements during visits home, or have relatives ship them abroad, drawn by prices a fraction of what they pay in the US, UK or Gulf. A suitcase of Indian-made generics is a quiet diaspora tradition. The monthly NSQ lists are a reminder that the same low cost rests on a quality-control system that still lets substandard batches through with uncomfortable regularity.

The exposure runs the other way too. Some of the very batches flagged by Indian and foreign regulators are made by exporters whose products reach diaspora pharmacies directly \u2014 and recalls of India-made drugs in the United States and elsewhere have become routine news. For NRI families managing the chronic conditions of ageing parents back home, or relying on Indian generics themselves, the practical takeaway is unglamorous but real: check batch numbers against CDSCO alerts, buy from reputable pharmacies, and treat the "pharmacy of the world" with informed eyes rather than blind faith.

## What's Next

The regulator says routine testing across central and state laboratories will continue, and the monthly alerts will keep coming. The harder questions are structural: whether India can tighten enforcement against repeat-offender manufacturers, close the gap between the handful of states that report diligently and the many that submit no data at all, and invest in the testing infrastructure needed to police an industry of its size. Until then, each monthly list will land the same way \u2014 a routine bureaucratic release that nonetheless asks every Indian household, at home and abroad, a quietly alarming question about the pills in the cabinet."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: pills / medicines / pharmacy. No single named person.
    img_url, ctitle = pick_commons([
        "assorted pills tablets medicine",
        "pharmaceutical tablets blister pack",
        "medicines pharmacy shelf India",
        "prescription drugs pills",
        "tablets capsules medication"
    ])
    img_caption = "Assorted medicine tablets; India's drug regulator flagged 159 samples as Not of Standard Quality in its latest monthly alert"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("pills medicine tablets pharmacy")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Medicine tablets and capsules; CDSCO's latest alert declared 159 drug samples substandard"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "health",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "IndiaMedToday (indiamedtoday.com, June 2026) \u2014 '159 Drug Samples Fail CDSCO Quality Test in May, One Flagged Spurious': India's drug regulator flagged 159 drug samples as Not of Standard Quality during routine surveillance in May, while one sample was identified as spurious in Assam; of the total, 46 samples declared NSQ by central drug laboratories and 113 by state drug laboratories; CDSCO said findings apply only to specific batches and do not mean other batches of the same products are substandard.",
            "Medical Dialogues (medicaldialogues.in) \u2014 monthly CDSCO NSQ alert coverage: recent alerts flagged batches of telmisartan (BP), glimepiride and metformin (anti-diabetics), pantoprazole, paracetamol, amoxicillin-clavulanate, cefixime, and calcium + Vitamin D3 supplements; manufacturers include Karnataka Antibiotics & Pharmaceuticals, Hindustan Antibiotics, Zydus Healthcare, Hetero Labs, Macleods and smaller producers in Baddi (HP) and Roorkee (Uttarakhand); failure reasons include assay failure (incorrect active ingredient content), dissolution failure (drug-release problems), sterility failures and particulate matter in injectables, and description/labelling defects; 'Not of Standard Quality' is defined under Section 16(1)(a) of the Drugs and Cosmetics Act, 1940.",
            "Medical Dialogues / Parliament data \u2014 'Over 14,300 Drug Samples Fail Quality Tests in Five Years': Union Health Minister J.P. Nadda told Parliament that of ~1.16 lakh samples tested in 2024-25, 3,104 were declared NSQ and 245 found spurious or adulterated; over five years more than 14,300 of nearly 4.9 lakh samples tested were flagged NSQ and nearly 1,600 found spurious or adulterated.",
            "Background: India is the world's largest supplier of generic medicines ('pharmacy of the world'); the government recently reclassified cough syrup as a prescription-only drug following the deaths of more than 140 children linked to contaminated cough syrups."
        ]),
        "diaspora_angle": "Millions of NRIs treat India as their pharmacy \u2014 stocking up on blood-pressure pills, diabetes drugs, antibiotics and supplements on visits home or having relatives ship them abroad for a fraction of Western prices \u2014 so a monthly list of substandard and spurious medicines is a direct, practical health-safety concern for diaspora families and the ageing parents they manage from afar.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# \u2500\u2500\u2500 Article 2: Adani Mundra Airport launches scheduled flights \u2500\u2500\u2500\u2500\u2500

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Adani Mundra Airport")
    print("="*60)

    slug = "adani-mundra-airport-first-scheduled-flights-star-air-kutch-gujarat-airport-expansion-20260623"
    headline = "Adani Just Opened an Airport in the Heart of Kutch. For the Gujarati Diaspora, It's a New Door Home."
    subheadline = "The Mundra Airport in Gujarat began scheduled passenger flights on Tuesday via regional carrier Star Air \u2014 connecting the remote Kutch region directly to Mumbai, Goa and six other cities \u2014 as the Adani Group unveiled plans to invest about Rs 1 lakh crore across its airports over the next five years."

    body = """For decades, getting from Kutch \u2014 the vast, arid district in Gujarat's far west \u2014 to a city like Mumbai meant a long road trip or a multi-stop journey via Bhuj's skeletal airstrip. On Tuesday that changed. Adani Mundra Airport, built next to India's largest private port, launched its first scheduled commercial passenger flights, with regional carrier Star Air opening direct air links to Mumbai and Goa and additional routes to Hindon (near Delhi), Surat, Belagavi, Bengaluru, Kolhapur and Nanded.

"Just keep in mind that today for someone from Mundra to even go to Mumbai was like a two-stop journey, and having a direct flight now is going to be extremely easy for them," said Jeet Adani, who oversees the group's airports business. The launch of eight new Star Air services from the new terminal is designed to create what the company calls an "express corridor" for trade, logistics and tourism around Mundra.

## An Airport Bolted to a Port

What makes Mundra unusual is its setting. The airport sits adjacent to Mundra Port \u2014 India's largest private port \u2014 and the Mundra Special Economic Zone, the country's largest operational multi-product SEZ and a nerve centre of India's import-export activity. Adani is explicitly positioning the airport not as a standalone passenger terminal but as the missing piece of a "fully integrated, multi-modal logistics and business hub," giving the cargo that flows through the port a fast last-mile air link to national and global supply chains.

The terminal, which the company says was completed in record time, has a 1,900-metre runway capable of handling a range of passenger and cargo aircraft, multiple check-in counters, lounges and a food court. Operations will begin with smaller regional aircraft, but Jeet Adani said larger narrow-body jets such as the Airbus A320 and Boeing 737 could be deployed later as demand grows, with land available to extend the runway further.

## Part of a Bigger Bet on the Skies

The Mundra launch came bundled with a far larger announcement: the Adani Group plans to invest roughly Rs 1 lakh crore across its airport portfolio over the next five years, and is eyeing fresh airport bids as it pushes for a bigger role in India's fast-growing aviation economy. The group already runs a clutch of major airports including Mumbai and the new greenfield Navi Mumbai International Airport, and Ahmedabad is expected to be added to the Mundra network soon.

For the Kutch region itself, the promise is concrete: easier business travel tied to the port and its industrial ecosystem, and a tourism boost for destinations such as Mandvi Beach and the cultural sites scattered across the district. Where Bhuj's airport has long offered only thin connectivity, a direct metro-to-metro link reshapes what is possible for residents and visitors alike.

## Why the Diaspora Should Care

Kutch and the wider Gujarat region are the ancestral home of one of the largest and most prosperous slices of the Indian diaspora \u2014 the Gujarati communities that built lives in East Africa, the United Kingdom, the United States and the Gulf, and that retain deep family, property and business ties to towns across the district. For these families, the friction of reaching the homeland has always included that final, awkward leg: land in Mumbai or Ahmedabad, then face a long road journey or a connecting hop to reach the family town. A functioning airport at Mundra, with the prospect of A320s and wider connectivity to come, chips away at exactly that friction.

There is a business dimension too. The Gujarati diaspora is heavily represented in trade and logistics, and Mundra \u2014 port, SEZ and now airport \u2014 is one of the engines of India's export economy. An integrated hub that shortens the distance between cargo, capital and the people who move both is the kind of infrastructure NRI entrepreneurs and investors watch closely. As Jeet Adani framed it, the goal is to connect "our Karmabhoomi" \u2014 the land of one's work \u2014 to the rest of India, and by extension to the diaspora that still calls Kutch home.

## What's Next

Star Air's regional turboprops will run the initial schedule, with Ahmedabad expected to join the network soon and larger aircraft a possibility as passenger numbers build. The broader story is Adani's Rs 1 lakh crore aviation push, which would deepen the group's already dominant footprint in Indian airports \u2014 a concentration that draws both investor interest and scrutiny. For Kutch, though, the immediate change is simpler and long-awaited: a direct flight out, and a faster way back in."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    # Topic imagery: Mundra port / Kutch / airport. No single named person as hero.
    img_url, ctitle = pick_commons([
        "Mundra Port Gujarat",
        "Mundra Adani port",
        "Bhuj Kutch Gujarat airport",
        "Kutch Gujarat landscape",
        "regional airport terminal India"
    ])
    img_caption = "Mundra in Gujarat's Kutch region, home to India's largest private port, where Adani launched scheduled passenger flights"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("airport terminal regional aircraft")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "A regional airport terminal; Adani's Mundra Airport in Kutch launched its first scheduled commercial flights"

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
            "The Hindu Business Line (thehindubusinessline.com, June 23, 2026) \u2014 'Adani Group to invest about Rs 1 lakh crore across airports in next 5 years; Mundra commercial operations take off': Mundra Airport began commercial passenger operations; Jeet Adani said operations will start with regional transport flights, with narrow-body A320/737 operations possible later as demand grows; runway can already handle A320/737 with extension land available; key growth drivers cited as internal/business travel and tourism linked to cultural sites and Mandvi beach; goal to connect 'our Karmabhoomi' to the rest of India.",
            "Devdiscourse / ANI (devdiscourse.com, June 23, 2026, 14:18 IST) and New Kerala \u2014 'Adani Mundra Airport emerges as fully integrated multi-modal logistics, business hub with launch of inaugural scheduled flights': Star Air launched eight new air services from the new terminal beginning Tuesday June 23, connecting Mundra to Mumbai and Goa plus Hindon, Surat, Belagavi, Bengaluru, Kolhapur and Nanded; airport sits adjacent to Mundra Port (India's largest private port) and the Mundra SEZ (largest operational multi-product SEZ); 1,900-metre runway, modern terminal with multiple check-in counters, lounges and food court; positioned as a fully integrated multi-modal logistics and business hub.",
            "Outlook Business (outlookbusiness.com, June 23, 2026) \u2014 'Adani Eyes New Airport Bids as It Unveils Rs 1 Lakh Cr Expansion Plan': Adani Group to invest ~Rs 1 lakh crore across airports over five years and is eyeing new airport bids; Mundra inaugural operations connect Mumbai and Goa with additional routes via Star Air; Ahmedabad expected to be added soon; Jeet Adani said the services will improve connectivity for Kutch residents, businesses and tourists and boost tourism to attractions such as Mandvi Beach."
        ]),
        "diaspora_angle": "Kutch and Gujarat are the ancestral home of one of the largest, most prosperous Indian diasporas \u2014 communities in East Africa, the UK, US and Gulf with deep family, property and trade ties to the district \u2014 so a direct-flight airport at Mundra removes the awkward final leg of every trip home and strengthens the port-SEZ-airport logistics hub that NRI entrepreneurs watch closely.",
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
