#!/usr/bin/env python3
"""
News writer for The Videshi — June 11, 2026 evening run.
Writes 3 articles on breaking stories with diaspora angle.
"""

import json, os, sys, time, re, uuid
from datetime import datetime, timezone
import requests
from urllib.parse import quote

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img, "Wikimedia Commons"
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None, None

def search_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons for topic-specific images."""
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": query,
                "gsrnamespace": 6,
                "gsrlimit": limit,
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "iiurlwidth": 1200,
                "format": "json"
            },
            headers={"User-Agent": UA},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                width = ii.get("width", 0)
                height = ii.get("height", 0)
                if url and "image" in mime and width >= 400:
                    results.append({
                        "url": url,
                        "width": width,
                        "height": height,
                        "title": page.get("title", "")
                    })
            if results:
                results.sort(key=lambda x: x["width"], reverse=True)
                print(f"  ✓ Wikimedia Commons found {len(results)} results for '{query}'")
                return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{query}': {e}")
    return []

def search_pexels(query):
    """Search Pexels for topic images (NOT for named people)."""
    if not PEXELS_KEY:
        return None, None
    try:
        import subprocess
        result = subprocess.run([
            'curl', '-sS',
            f'https://api.pexels.com/v1/search?query={quote(query)}&per_page=5&orientation=landscape',
            '-H', f'Authorization: {PEXELS_KEY}'
        ], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                src = photo.get("src", {})
                url = src.get("large2x") or src.get("large") or src.get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:60]}...")
                    return url, "Pexels"
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None, None

def validate_image(url):
    """Validate image URL returns HTTP 200 with image content > 5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Try GET if HEAD didn't return Content-Length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            chunk = r2.raw.read(10000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: >{len(chunk)} bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Article inserted: {result[0].get('id', 'unknown')}")
            return result[0]
        print(f"  ✓ Article inserted (raw response)")
        return result
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None

# ─────────────────────────────────────────────
# ARTICLE 1: Trump Cancels Iran Strikes
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("ARTICLE 1: Trump Cancels Iran Strikes, Oil Crashes")
print("="*60)

# Image sourcing: Trump from Wikipedia
img1_url, img1_attr = fetch_wikipedia_person_image("Donald Trump")

# Also try Wikimedia Commons for Iran strikes
commons_results = search_wikimedia_commons("US military strikes Iran 2026")
if not commons_results:
    commons_results = search_wikimedia_commons("Persian Gulf US Navy")

# If Wikipedia Trump image not validated, try Pexels for oil/crude
if img1_url and not validate_image(img1_url):
    img1_url = None

if not img1_url:
    # Fallback to commons
    for cr in commons_results:
        if validate_image(cr["url"]):
            img1_url = cr["url"]
            img1_attr = "Wikimedia Commons"
            break

if not img1_url:
    img1_url, img1_attr = search_pexels("crude oil barrel price global")
    if img1_url:
        validate_image(img1_url)

article1_body = """Trump called off planned military strikes against Iran on Thursday evening, declaring that negotiations had been "approved" at the highest levels of Iranian leadership and by a broad coalition including Israel, Saudi Arabia, the UAE, Qatar, Turkey, Pakistan and Egypt.

"Based on the fact that discussions with the Islamic Republic of Iran have been brought to the highest level of Iranian leadership and approved, I have, as President of the United States of America, cancelled the scheduled strikes and bombings against Iran this evening," Trump wrote on Truth Social.

The dramatic reversal came just hours after Trump had threatened to hit Iran "very hard tonight" and floated the idea of seizing Kharg Island, the hub through which 90 per cent of Iran's crude oil exports flow. He compared the plan to the American takeover of Venezuela's oil sector, saying it was "working out brilliantly for both countries."

Oil prices fell sharply on the announcement. Brent crude dropped 3.7 per cent to $89.65 a barrel, while West Texas Intermediate fell 3.6 per cent to $86.75 — the steepest single-session decline since the April ceasefire. Earlier in the day, prices had been rising, with Brent touching $94.83 after Iran's Revolutionary Guard declared the Strait of Hormuz "closed to all vessels."

## What a Deal Would Mean for India

For India, the world's third-largest oil importer, any sustained easing of Gulf tensions would be transformative. The country imports 85 per cent of its crude, and roughly 1.5 million barrels per day normally transit the Strait of Hormuz. Since the war began on 28 February, India's fuel subsidy bill has doubled, foreign portfolio investors have pulled $30.4 billion from Indian markets, and the rupee has weakened to 95.35 against the dollar.

A return of Brent to the mid-$80s — if it holds — would ease pressure on the Reserve Bank of India, which cut rates in June but faces an inflation rate that just crossed 4 per cent after 15 months below target. It would also offer relief to Indian Oil Corporation and other state refiners that have been absorbing losses rather than passing through the full cost of crude above $90.

"Any progress on diplomacy is a positive signal for the Indian economy," said G Chokkalingam of Equinomics Research. "But the naval blockade staying in place means we are not out of the woods."

## The Fine Print

Trump emphasised that the US naval blockade of Iranian ports would "remain in full force and effect until this transaction is finalised." He promised that the time and place of a signing would be "announced shortly." There was no immediate comment from Tehran, and analysts noted that Trump has claimed imminent deals with Iran multiple times since April, only for them to collapse.

The ceasefire, in place since 8 April, has been described by Trump himself as "the most violated ceasefire in the history of the world." US and Iranian forces exchanged strikes on both Tuesday and Wednesday, with the US firing 49 Tomahawk missiles at Iranian air defences and radar installations. Iran retaliated with missiles and drones targeting US bases in Jordan, Kuwait and Bahrain.

## Diaspora on Edge

For the estimated 8 million Indians working in Gulf states — the UAE, Saudi Arabia, Qatar, Kuwait, Bahrain and Oman — any escalation directly threatens livelihoods and safety. India has had to deploy naval vessels to escort merchant shipping through the Persian Gulf, and three Indian seafarers were killed this week when US forces struck tankers with Indian crews aboard.

The Indian government has summoned the American envoy over the strikes on ships carrying Indian nationals and is expected to raise the issue during Modi's meeting with Trump at the G7 summit in Evian next week. Remittances from the Gulf — worth $32 billion annually to India — have already begun to slow as employers in construction, hospitality and logistics scale back amid the instability.

If the deal materialises, it would be the first concrete diplomatic breakthrough since the war began more than three months ago. If it does not, the pattern of threats, strikes and hollow truces will continue — and India will keep paying the price at the pump."""

article1 = {
    "headline": "Trump Cancels Iran Strikes at the Last Minute. Oil Crashed. India Is Watching the Fine Print.",
    "subheadline": "Brent crude dropped 3.7 per cent to $89 after Trump said a deal had been approved by Iran, Israel, Saudi Arabia and a dozen other nations. But the naval blockade stays — and India still imports 85 per cent of its oil.",
    "body": article1_body.strip(),
    "slug": "trump-cancels-iran-strikes-oil-crashes-india-watching-deal-fine-print-20260611",
    "category": "news",
    "vertical": "geopolitics",
    "status": "review",
    "is_editorial": False,
    "image_url": img1_url or "",
    "image_caption": "Donald Trump announced the cancellation of strikes on Iran via Truth Social on Thursday evening",
    "image_attribution": img1_attr or "Wikimedia Commons",
    "sources": json.dumps(["Reuters", "Wall Street Journal", "Barron's", "USA Today"]),
    "diaspora_angle": "Gulf-based Indian workers face direct safety risks, and any deal would ease India's $30B+ oil import pressure and stabilise remittances worth $32 billion annually.",
    "published_at": datetime.now(timezone.utc).isoformat()
}

result1 = insert_article(article1)
print(f"  Article 1 result: {'SUCCESS' if result1 else 'FAILED'}")

time.sleep(1)

# ─────────────────────────────────────────────
# ARTICLE 2: Ebola Outbreak WHO Emergency
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("ARTICLE 2: Ebola Outbreak — NRI Travel Alert")
print("="*60)

# Image: try Wikimedia Commons for Ebola/WHO
commons_ebola = search_wikimedia_commons("Ebola response WHO protective equipment")
if not commons_ebola:
    commons_ebola = search_wikimedia_commons("Ebola virus disease response Africa")

img2_url, img2_attr = None, None
for cr in commons_ebola:
    if validate_image(cr["url"]):
        img2_url = cr["url"]
        img2_attr = "Wikimedia Commons"
        break

if not img2_url:
    # Try Wikipedia for WHO
    img2_url, img2_attr = fetch_wikipedia_person_image("Tedros Adhanom Ghebreyesus")
    if img2_url and not validate_image(img2_url):
        img2_url = None

if not img2_url:
    img2_url, img2_attr = search_pexels("medical health workers protective equipment")
    if img2_url and not validate_image(img2_url):
        img2_url = None

article2_body = """The World Health Organisation has declared the Ebola outbreak in the Democratic Republic of Congo a Public Health Emergency of International Concern — the highest alarm the agency can sound. With suspected cases now topping 900 and the death toll climbing past 220, WHO Director-General Tedros Adhanom Ghebreyesus is travelling to Congo personally, warning that the epidemic is "outpacing us."

For NRIs planning summer travel to the United States, Canada or Mexico — especially those attending the FIFA World Cup that kicked off this week — the outbreak has triggered a cascade of new border controls that could affect journey plans.

## What Has Changed

The US Department of Health and Human Services has expanded travel restrictions under Title 42. Lawful permanent residents — green card holders — who have been in the DRC, Uganda or South Sudan within the last 21 days may face temporary entry limits. US citizens can still enter but will undergo enhanced health screening at major airports including Atlanta, Washington-Dulles and John F. Kennedy.

Canada and Mexico, co-hosting the World Cup, have announced coordinated screening measures for travellers arriving from Central and East Africa. All three nations stress that the vast majority of international visitors are unaffected, but the rules add friction for anyone with recent travel to the affected region.

The Centers for Disease Control and Prevention has modelled worst-case scenarios. If only 20 per cent of patients in Congo are isolated, there is a 65 per cent chance of case numbers exceeding 20,000 within three months — which would put it on track to rival the 2014-16 West Africa epidemic that killed 11,300 people.

## The Outbreak So Far

The Bundibugyo strain driving this outbreak has no approved vaccine or specific treatment. It was first identified in Mongbwalu, a gold-mining town in Congo's Ituri province, where a funeral in early February is believed to have been a super-spreader event. More than 80 mourners attended the burial of a 44-year-old pastor; within weeks, dozens of deaths followed.

The virus has crossed into Uganda, which has recorded 19 confirmed cases. Congo has reimposed flight restrictions to and from Ituri's capital, Bunia. On the ground, medics lack basic protective equipment — boots, thermometers, water basins — and health workers have been attacked by communities that blame them for spreading the disease.

"We are dying like flies," said Denis Urwothun Rwothng'a, a medic in Bunia who has lost three colleagues to the virus.

## Why NRIs Should Pay Attention

India has a significant diaspora across Central and East Africa, including construction workers, traders and IT professionals in Uganda, Kenya, Tanzania and the DRC. The Indian embassy in Kinshasa has not yet issued a formal travel advisory, but diplomatic sources say one is being drafted.

For Indian students, workers and families in neighbouring countries, the risk is proximity. Uganda shares a long land border with Ituri province, and confirmed cases there have prompted alarm. India's own experience with viral outbreaks — from Nipah to COVID — means public health authorities are alert, but the Bundibugyo strain is particularly dangerous because it lacks the medical countermeasures that eventually tamed the 2014 outbreak.

The dismantling of USAID — which previously could deploy protective equipment within 48 hours of an outbreak declaration — has left a logistics gap that international agencies are struggling to fill. "USAID had these systems. They weren't perfect but they were pretty damn good," said a US official. "Now we are literally building the plane as we fly it."

## What to Do

NRIs travelling to the US, Canada or Mexico this summer should check CDC travel advisories before departure. Those with recent travel to the DRC, Uganda or South Sudan should expect enhanced screening and carry documentation of their travel history. Anyone who develops symptoms — fever, vomiting, unexplained bleeding — within 21 days of leaving an affected area should isolate immediately and contact public health authorities.

For diaspora families in East Africa, the advice is simpler: avoid travel to Ituri province, follow local health authority guidance, and monitor WHO situation reports. The next few weeks will determine whether this outbreak is contained — or becomes Africa's worst health crisis in a decade."""

article2 = {
    "headline": "The Ebola Outbreak Just Got the Highest WHO Alarm. Here Is What Every NRI Travelling This Summer Needs to Know.",
    "subheadline": "Suspected cases have topped 900 in Congo. The US has restricted green card holders from three African countries. And the World Cup has just begun.",
    "body": article2_body.strip(),
    "slug": "ebola-who-emergency-nri-travel-restrictions-world-cup-green-card-20260611",
    "category": "news",
    "vertical": "global-health",
    "status": "review",
    "is_editorial": False,
    "image_url": img2_url or "",
    "image_caption": "Health workers in protective equipment respond to the Ebola outbreak in the Democratic Republic of Congo",
    "image_attribution": img2_attr or "Wikimedia Commons",
    "sources": json.dumps(["WHO", "Reuters", "CDC", "NPR", "Travel and Tour World"]),
    "diaspora_angle": "NRIs face new US entry screening rules, green card holders from affected African countries risk temporary entry limits, and Indian diaspora workers across East Africa are in proximity to the spreading outbreak.",
    "published_at": datetime.now(timezone.utc).isoformat()
}

result2 = insert_article(article2)
print(f"  Article 2 result: {'SUCCESS' if result2 else 'FAILED'}")

time.sleep(1)

# ─────────────────────────────────────────────
# ARTICLE 3: Indian Refiners Secure Crude
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("ARTICLE 3: Indian Refiners Secure Crude Through August")
print("="*60)

# Image: Oil refinery from Pexels (generic scene, not a named person)
img3_url, img3_attr = None, None
commons_oil = search_wikimedia_commons("Indian oil refinery petroleum")
if not commons_oil:
    commons_oil = search_wikimedia_commons("oil refinery crude petroleum India")

for cr in commons_oil:
    if validate_image(cr["url"]):
        img3_url = cr["url"]
        img3_attr = "Wikimedia Commons"
        break

if not img3_url:
    img3_url, img3_attr = search_pexels("oil refinery industrial petrochemical plant")
    if img3_url and not validate_image(img3_url):
        img3_url = None

article3_body = """Three and a half months into the Iran war, India's oil supply chain is holding — but only because state refiners have been quietly scrambling behind the scenes, cutting deals in corners of the global crude market they would normally ignore.

Indian refiners have secured enough crude to meet their needs through at least August, according to industry sources cited by Reuters. The lifeline is coming not from India's traditional Gulf suppliers, but from a patchwork of workarounds: ship-to-ship transfers off Fujairah, spot purchases from Brazil and West Africa, and carefully negotiated cargoes from Abu Dhabi National Oil Company loaded at ports outside the Strait of Hormuz.

## The Deals Being Done

Hindustan Petroleum Corporation Limited (HPCL) has purchased 4 million barrels of Murban crude from the UAE for August delivery, sourced through Totsa (TotalEnergies' trading arm) and Mercuria. The crude was priced at a premium of about 40 cents per barrel over the July Dated Brent benchmark — expensive, but available.

Last week, HPCL also bought 2 million barrels from Brazil and West Africa for its 180,000-barrel-per-day Rajasthan refinery. Indian Oil Corporation and Mangalore Refinery and Petrochemicals have made similar spot purchases in recent weeks.

ADNOC is offering crude from Fujairah storage, Zirku or Das Island, and via ship-to-ship transfer in the Fujairah-to-Sohar corridor and in Malaysian waters. Liquefied petroleum gas — critical for Indian households — is mostly being sourced from Sohar in Oman, bypassing the contested strait entirely.

"We are well covered on LPG at least till mid-July, and crude is not a problem," an Indian refinery source told Reuters. "The concern is not supply but price."

## The Price India Is Paying

That distinction — supply secure, price painful — captures India's predicament. Brent crude has averaged above $90 since the war began, compared with $75-80 in the months before. Even with Trump's dramatic cancellation of strikes on Thursday evening sending prices briefly to $89, the baseline remains far above what India's fiscal math assumes.

The cost shows up everywhere. India's fertiliser subsidy bill has doubled in three months as feedstock prices have soared. Foreign portfolio investors have yanked a record $30.4 billion from Indian equities since February, partly because high oil prices widen the current account deficit and weaken the rupee. The currency itself has slid to 95.35 per dollar, with the Reserve Bank of India burning through reserves to prevent a steeper fall.

Oil Minister Hardeep Singh Puri has insisted India has "enough diversified supplies" and is not "unduly worried." But behind the reassurance, the government is stress-testing scenarios where the Strait of Hormuz remains contested for months, not weeks.

## What Diversification Looks Like

India's emergency playbook has three layers. The first is geographic diversification — buying from Latin America, West Africa and the US, routes that bypass the Persian Gulf entirely. The second is creative logistics: the ship-to-ship transfers off Fujairah and Malaysia allow cargoes to be loaded outside the conflict zone, even when the strait is notionally "closed." The third is drawing down strategic petroleum reserves, though India's current stockpile of about 39 million barrels provides only around 9.5 days of import cover.

Saudi Arabia, which has its own Red Sea export terminals that bypass Hormuz, has emerged as a crucial swing supplier. India imported 890,000 barrels per day from Saudi Arabia in April, up 19 per cent from pre-war levels.

## The NRI Angle

For NRIs who own property in India, hold rupee-denominated investments, or send remittances home, the oil-price dynamic matters more than any single headline. A sustained Brent above $90 means a weaker rupee, higher inflation, and slower GDP growth — all of which erode the value of Indian assets in dollar terms. If Trump's cancelled strikes lead to a real deal and oil settles below $85, the arithmetic reverses: the rupee stabilises, the RBI gets room to cut rates further, and equity markets could stage a recovery.

For now, India's refiners have bought themselves time. The question is whether diplomacy can buy the rest."""

article3 = {
    "headline": "India's Refiners Have Quietly Secured Oil Through August. Here Is How They Did It.",
    "subheadline": "Ship-to-ship transfers off Fujairah, spot cargoes from Brazil and West Africa, and 4 million barrels of UAE crude. India's supply chain is holding — but the price is steep.",
    "body": article3_body.strip(),
    "slug": "india-refiners-secure-crude-oil-august-iran-war-hpcl-adnoc-diversification-20260611",
    "category": "news",
    "vertical": "economy",
    "status": "review",
    "is_editorial": False,
    "image_url": img3_url or "",
    "image_caption": "An oil refinery complex processing crude petroleum for domestic fuel supply",
    "image_attribution": img3_attr or "Pexels",
    "sources": json.dumps(["Reuters", "The Hindu BusinessLine", "The Indian Eye"]),
    "diaspora_angle": "NRIs with rupee investments, Indian property or remittance flows are directly affected — sustained high oil prices weaken the rupee, inflate costs, and erode the dollar value of Indian assets.",
    "published_at": datetime.now(timezone.utc).isoformat()
}

result3 = insert_article(article3)
print(f"  Article 3 result: {'SUCCESS' if result3 else 'FAILED'}")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
results = [
    ("Trump Cancels Iran Strikes", result1),
    ("Ebola WHO Emergency NRI Travel", result2),
    ("Indian Refiners Secure Crude", result3)
]
for title, r in results:
    status = "✓ INSERTED" if r else "✗ FAILED"
    print(f"  {status}: {title}")
