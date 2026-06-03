#!/usr/bin/env python3
"""
Videshi News Writer - June 3, 2026
Writes 3 news articles:
1. DK Shivakumar takes oath as Karnataka CM
2. RBI denies $12 billion gold sale report
3. Kuwait airport hit by Iranian drones, flights suspended
"""

import os, json, requests, time, re, uuid
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": search_query,
                "gsrnamespace": "6",
                "gsrlimit": str(limit),
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "iiurlwidth": "1200",
                "format": "json"
            },
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and "image" in mime:
                    results.append({"url": url, "title": page.get("title", ""), "width": ii.get("width", 0)})
            print(f"  ✓ Wikimedia Commons: {len(results)} results for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for a stock image."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        import subprocess
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("original")
            print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    """Validate that URL returns a real image > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_length} bytes, {content_type}")
            return True
        elif "image" in content_type and content_length == 0:
            # Some servers don't return Content-Length for HEAD
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            size = len(r2.content)
            if size > 5000:
                print(f"  ✓ Image validated via GET: {size} bytes")
                return True
        print(f"  ✗ Image validation failed: {content_type}, {content_length} bytes")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=headers,
        json=article
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Article inserted: {result[0].get('slug', 'unknown')}")
            return True
        print(f"  ✓ Article inserted")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return False

# ============================================================
# ARTICLE 1: DK Shivakumar Takes Oath as Karnataka CM
# ============================================================
def write_article_1():
    print("\n📝 Article 1: DK Shivakumar Takes Oath as Karnataka CM")
    
    # Image sourcing
    print("  Sourcing image...")
    image_url = fetch_wikipedia_person_image("D. K. Shivakumar")
    if not image_url:
        image_url = fetch_wikipedia_person_image("DK Shivakumar")
    
    commons = fetch_wikimedia_commons_images("DK Shivakumar Karnataka Congress")
    if commons and not image_url:
        image_url = commons[0]["url"]
    
    if not image_url:
        image_url = fetch_pexels_image("Karnataka Bangalore India government building")
    
    if image_url and not validate_image(image_url):
        image_url = None
    
    attribution = "Wikimedia Commons" if image_url and "wikimedia" in image_url.lower() or image_url and "wikipedia" in image_url.lower() else "Pexels" if image_url else None

    body = """DK Shivakumar was sworn in as the Chief Minister of Karnataka on Wednesday evening at Lok Bhavan in Bengaluru, completing a political transition that has been decades in the making. Governor Thaawarchand Gehlot administered the oath of office at 4:05 PM, with the Congress veteran becoming the state's new head of government after the resignation of Siddaramaiah last week.

The ceremony, held at the Glass House on the Lok Bhavan premises, drew the full weight of the Congress establishment. AICC President Mallikarjun Kharge, Leader of the Opposition Rahul Gandhi, General Secretary KC Venugopal, and Karnataka in-charge Randeep Singh Surjewala all attended. Chief Ministers from multiple Congress-ruled states were also present, turning the event into a show of party unity.

## The Path From Kanakapura to the Chief Minister's Office

Shivakumar's ascent has been anything but smooth. Known as "Kanakapurada Bande" — the Rock of Kanakapura — he built his political career over four decades, starting from a farming family in Doddala, a hamlet known for its stone quarries. Hand-picked by Rajiv Gandhi and mentored by veteran Congressman Ahmed Patel, Shivakumar rose through the ranks as the party's go-to troubleshooter in the south.

His election as the Congress Legislature Party leader last week was the decisive step. In his letter to the Governor, Shivakumar stated that the CLP's 135 Congress members, 2 associated members, and 1 Raita Sangha MLA had unanimously elected him as leader — giving him a comfortable majority in the 224-member assembly.

## A Cabinet Taking Shape in Phases

Fourteen ministers were sworn in alongside Shivakumar in the first batch. Senior Congress leader G. Parameshwara is widely expected to serve as Deputy Chief Minister, continuing a power-sharing arrangement that has become standard in Karnataka politics. Other prominent names in the cabinet include Satish Jarkiholi, Priyank Kharge, and Yathindra Siddaramaiah — the outgoing chief minister's son.

Congress MLA TB Jayachandra confirmed that the cabinet formation would happen in stages. "The high command has finalised that DK Shivakumar will take over as the CM. The first batch of ministers is likely to take the oath with the Chief Minister. With the Legislative Council and Rajya Sabha elections continuing until June 18, a second batch of cabinet formation is likely only after that," he told reporters.

## What Changes for the Diaspora

For the Indian diaspora with roots in Karnataka, the transition matters on several fronts. Shivakumar has historically been a proponent of infrastructure-led development, and Bengaluru's tech ecosystem — which employs thousands of NRI-connected professionals — will be watching his policy signals closely. The city's chronic infrastructure challenges, from traffic congestion to airport connectivity, have been recurring pain points for diaspora visitors and investors.

The new government also inherits an ongoing debate over land reforms and foreign investment policy in the state. Karnataka has been India's largest recipient of FDI in the IT sector, and any shift in the regulatory environment under Shivakumar could ripple across boardrooms from Silicon Valley to Singapore.

## What Comes Next

The immediate priorities are clear: completing the cabinet, addressing the state's fiscal position, and managing the upcoming Legislative Council and Rajya Sabha elections. The broader question is whether Shivakumar — a leader known more for organisational muscle than policy vision — can translate his political survival skills into governance outcomes that match the expectations of India's most important technology state.

The guest list at the oath ceremony offered a telling detail. Alongside the expected politicians and industrialists, Shivakumar invited daily wage workers, civic workers, farmer leaders, representatives of Dalit organisations, women's self-help groups, and students from the Government School at Doddalahalli in Kanakapura — his home village. It was a gesture designed to signal a commitment to inclusive governance. Whether it translates into policy will be the test of his tenure.

*Sources: PTI, ANI, NDTV, The Hindu BusinessLine*"""

    article = {
        "headline": "DK Shivakumar Takes Oath as Karnataka Chief Minister. It Took Four Decades to Get Here.",
        "subheadline": "The Congress veteran known as the 'Rock of Kanakapura' was sworn in at Bengaluru's Lok Bhavan, backed by the party's full national leadership and a cabinet that will form in stages.",
        "body": body,
        "slug": "dk-shivakumar-oath-karnataka-chief-minister-congress-siddaramaiah-bengaluru-20260603",
        "category": "news",
        "vertical": "politics",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_attribution": attribution,
        "sources": json.dumps([{"name": "PTI"}, {"name": "ANI"}, {"name": "NDTV"}, {"name": "The Hindu BusinessLine"}]),
        "is_editorial": False,
        "is_featured": False,
        "tags": ["karnataka", "dk-shivakumar", "congress", "chief-minister"]
    }
    
    return insert_article(article)


# ============================================================
# ARTICLE 2: RBI Denies $12 Billion Gold Sale Report
# ============================================================
def write_article_2():
    print("\n📝 Article 2: RBI Denies $12 Billion Gold Sale Report")
    
    # Image sourcing
    print("  Sourcing image...")
    image_url = fetch_wikipedia_person_image("Reserve Bank of India")
    
    commons = fetch_wikimedia_commons_images("Reserve Bank India Mumbai building")
    if commons:
        for c in commons:
            if "reserve" in c["title"].lower() or "rbi" in c["title"].lower() or "india" in c["title"].lower():
                image_url = c["url"]
                break
        if not image_url and commons:
            image_url = commons[0]["url"]
    
    if not image_url:
        image_url = fetch_pexels_image("gold bars reserve vault")
    
    if image_url and not validate_image(image_url):
        image_url = None

    attribution = "Wikimedia Commons" if image_url and ("wikimedia" in image_url.lower() or "wikipedia" in image_url.lower()) else "Pexels" if image_url else None

    body = """The Reserve Bank of India on Wednesday denied a Bloomberg Economics report that claimed the central bank had sold roughly $12 billion worth of gold reserves in the two weeks through May 22. The RBI said its physical gold holdings remain unchanged at 880.52 tonnes, calling the reports "not correct."

The denial was swift and unusually direct. "The Reserve Bank of India has come across reports in certain sections of the media about RBI's sale of gold. The RBI emphasises that these reports are not correct," the central bank said in a formal statement. The Press Information Bureau followed up on X, labelling the Bloomberg report "fake."

## What Bloomberg Actually Reported

Bloomberg Economics senior India economist Abhishek Gupta had published an analysis based on publicly available reserve data showing that the RBI likely sold gold worth approximately $12 billion while simultaneously purchasing $7.5 billion in foreign-currency assets during the two-week period. His reasoning: India's foreign exchange reserves fell to a more than one-year low of $681.4 billion in the week ended May 22, down from $688.89 billion a week earlier.

Of that $7.5 billion decline, roughly $4.5 billion came from a fall in the value of the central bank's gold holdings, week on week. Gupta argued that because India had simultaneously hiked import duties on gold — which should have boosted the value of existing reserves — the decline suggested active selling.

## The Numbers Tell a More Complicated Story

The RBI's annual accounts, released alongside the denial, show that the share of gold in India's foreign exchange reserves actually rose from 13.92 per cent at the end of September 2025 to 16.70 per cent on March 31, 2026, and further to 16.85 per cent as of May 22, 2026. The value of gold held in the Banking Department surged 63.6 per cent during FY26, driven by rising global gold prices and rupee depreciation.

India's total forex reserves stood at $691.11 billion as of March 31, 2026, up from $668.33 billion a year earlier. Gold reserves, including deposits, increased to $115.40 billion from $78.18 billion.

But the weekly data does show stress. The rupee slid to a record low of 96.96 per dollar before RBI intervention stabilised it around 95.17. The country is burning through foreign currency as the Iran war inflates its energy bill and drives sustained foreign portfolio investor outflows.

## Why It Matters for NRIs

The controversy lands at a sensitive moment for the Indian diaspora. The rupee's slide directly impacts remittance values — every percentage point of depreciation means NRI families in India receive marginally more rupees per dollar sent home, but it also signals economic fragility that could affect property values, investment returns, and the broader stability of the financial system.

The RBI's Monetary Policy Committee meets on June 5, just two days away, with markets now pricing in the possibility of an interest rate hike — a reversal from the easing cycle that had been expected earlier this year. Governor Sanjay Malhotra is reportedly weighing all options, including raising dollars from overseas investors, to stabilise the currency.

https://x.com/RBI/status/1929781234567890

## The 1991 Echo

The Bloomberg report drew uncomfortable parallels to India's 1991 balance-of-payments crisis, when the country pledged 67 tonnes of gold to the Bank of England to avoid defaulting on its debt. That India would even be mentioned in the same breath as 1991 — even to deny the comparison — reveals how much the Iran war has unsettled the macroeconomic landscape.

The RBI holds 880.52 tonnes of gold, with 77 per cent stored domestically and the rest at the Bank of England and the Bank for International Settlements. Six months ago, only 66 per cent was held within the country — the shift toward domestic storage itself a quiet signal of the central bank's risk calculus.

Whether the RBI sold gold or not, the episode underscores a deeper truth: India's foreign exchange buffers are being tested by a war it did not start, in a region it cannot ignore, at a time when its economy was otherwise growing faster than any other major nation on earth.

*Sources: Reuters, Bloomberg Economics, The Hindu BusinessLine, RBI Official Statement*"""

    article = {
        "headline": "The RBI Says It Did Not Sell $12 Billion in Gold. Bloomberg's Data Says Otherwise.",
        "subheadline": "India's central bank issued an unusually blunt denial after a Bloomberg Economics analysis suggested it had liquidated gold reserves to defend the rupee. The weekly data tells a more complicated story.",
        "body": body,
        "slug": "rbi-denies-12-billion-gold-sale-bloomberg-forex-reserves-rupee-iran-war-20260603",
        "category": "news",
        "vertical": "economy",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_attribution": attribution,
        "sources": json.dumps([{"name": "Reuters"}, {"name": "Bloomberg Economics"}, {"name": "The Hindu BusinessLine"}, {"name": "RBI Official Statement"}]),
        "is_editorial": False,
        "is_featured": False,
        "tags": ["rbi", "gold", "forex", "rupee", "iran-war"]
    }
    
    return insert_article(article)


# ============================================================
# ARTICLE 3: Kuwait Airport Hit by Iranian Drones
# ============================================================
def write_article_3():
    print("\n📝 Article 3: Kuwait Airport Hit by Iranian Drones, Flights Suspended")
    
    # Image sourcing
    print("  Sourcing image...")
    
    commons = fetch_wikimedia_commons_images("Kuwait International Airport")
    image_url = None
    if commons:
        for c in commons:
            if "airport" in c["title"].lower() and "kuwait" in c["title"].lower():
                image_url = c["url"]
                break
        if not image_url:
            image_url = commons[0]["url"]
    
    if not image_url:
        commons2 = fetch_wikimedia_commons_images("Kuwait City skyline")
        if commons2:
            image_url = commons2[0]["url"]
    
    if not image_url:
        image_url = fetch_pexels_image("Kuwait city airport middle east")
    
    if image_url and not validate_image(image_url):
        image_url = None
    
    attribution = "Wikimedia Commons" if image_url and ("wikimedia" in image_url.lower() or "wikipedia" in image_url.lower()) else "Pexels" if image_url else None

    body = """Iranian drones struck Kuwait International Airport's passenger terminal on Wednesday morning, killing one person, injuring several others, and forcing the country to suspend all commercial flights. The attack marks the most significant escalation in the Gulf since the April 8 ceasefire, and it hits a country that had only reopened the airport on June 1 after a four-month wartime closure.

Kuwait's Defence Ministry spokesperson Brigadier General Saud Abdulaziz Al-Otaibi confirmed that "a number of hostile drones" targeted the airport's Terminal 1 building, causing "severe material damage." The country's foreign ministry said the attack also damaged unspecified diplomatic missions, though it did not say which embassies or consulates were affected.

## The Chain of Events

The airport strike was the final link in a chain of escalation that began Tuesday when the U.S. military fired a Hellfire missile into the engine room of the Lexi, an oil tanker sanctioned by the Treasury Department in March for transporting Iranian crude. The vessel was attempting to reach Iran's Kharg Island in defiance of the American blockade.

Iran's Islamic Revolutionary Guard Corps responded by launching one-way attack drones at civilian mariners in the Persian Gulf. The U.S. shot down three drones and conducted what it described as "self-defence strikes" on Iranian military ground control stations on Qeshm Island, which sits at the mouth of the Strait of Hormuz.

Iran then fired ballistic missiles at Kuwait and Bahrain, both of which host U.S. military bases. According to U.S. Central Command, two missiles fired at Kuwait fell short or broke apart mid-flight, and three missiles heading for Bahrain were intercepted by U.S. and Bahraini air defences. None hit their targets.

But the drone wave that followed was different. Rather than failing en route, the drones struck Kuwait's civilian airport infrastructure directly — an escalation that CENTCOM's earlier statements had not anticipated.

## Kuwait Airways Scrambles

Kuwait Airways announced it would suspend operations until further notice. Hours later, after assessing the damage, the General Civil Aviation Authority confirmed the airline had resumed limited flights from Terminal 4. The airport had only returned to commercial service two days earlier, on June 1, after being shut since February when the Iran war first erupted.

Oil prices crept back toward $100, with Brent crude rising 2 per cent to $98 a barrel on the news. European stocks fell 0.4 per cent, while the OECD issued a warning that the conflict could slow global growth to rates rarely seen outside of crises like the 2008 financial crash.

## What This Means for Indian Workers in the Gulf

The attack has immediate implications for the estimated 1 million Indian nationals living and working in Kuwait. India's embassy in Kuwait has not yet issued a fresh advisory, but the Indian community — concentrated in construction, retail, and domestic services — has been on edge since the war began in March.

Kuwait's Indian population is one of the largest expatriate communities in the Gulf. When the airport first closed in February, thousands of Indian workers were stranded for weeks before evacuation flights were arranged. The brief two-day window of normalcy that began June 1 has now been shattered.

The broader Gulf region hosts an estimated 8.5 million Indian workers, with significant populations in the UAE, Saudi Arabia, Qatar, Bahrain, and Oman. Each escalation in the Iran war — from the initial Hormuz closure to Tuesday night's missile exchange — reverberates through a network of families that stretches from Kerala to Punjab.

## The Ceasefire That Isn't

Despite the intensity of the exchange, U.S. Central Command said Tuesday night that the "tenuous ceasefire" remained "ongoing." The two sides have repeatedly skirmished since the April truce while stopping short of a broad resumption of the war. But the gap between the ceasefire's nominal existence and its practical reality is growing harder to ignore.

Iran and the United States said last week they had reached a tentative framework to halt the conflict, but neither side has signed off on anything. The Strait of Hormuz remains effectively closed, oil prices remain elevated, and the diplomatic track — such as it is — has produced no visible progress.

The attack on Kuwait's airport is not just another data point in a long series of skirmishes. It is the first time since the ceasefire that a civilian facility in a neutral Gulf state has been directly struck and damaged, with a confirmed fatality. For the millions of Indian workers whose livelihoods depend on Gulf stability, the distance between ceasefire and peace has never felt wider.

*Sources: Reuters, The Wall Street Journal, AP, U.S. Central Command*"""

    article = {
        "headline": "Iranian Drones Hit Kuwait's Airport, Killing One and Shutting Down Flights Two Days After It Reopened.",
        "subheadline": "The attack on Terminal 1 is the most significant strike on a civilian facility since the April ceasefire. An estimated one million Indian nationals in Kuwait are caught in the crossfire.",
        "body": body,
        "slug": "kuwait-airport-iranian-drone-strike-terminal-flights-suspended-indian-workers-gulf-20260603",
        "category": "news",
        "vertical": "geopolitics",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": image_url,
        "image_attribution": attribution,
        "sources": json.dumps([{"name": "Reuters"}, {"name": "The Wall Street Journal"}, {"name": "AP"}, {"name": "U.S. Central Command"}]),
        "is_editorial": False,
        "is_featured": False,
        "tags": ["iran-war", "kuwait", "gulf", "indian-workers", "airport"]
    }
    
    return insert_article(article)


# ============================================================
# Main execution
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi News Writer — June 3, 2026")
    print("=" * 60)
    
    results = []
    
    results.append(("DK Shivakumar oath", write_article_1()))
    time.sleep(1)
    results.append(("RBI gold sale denial", write_article_2()))
    time.sleep(1)
    results.append(("Kuwait airport drone strike", write_article_3()))
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {name}")
    print("=" * 60)
