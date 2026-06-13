#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-13 batch
3 articles: El Niño Monsoon, India-Canada Thaw, SpaceX IPO MANGOS
"""

import json, os, subprocess, re, time, datetime, urllib.parse, requests

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                key = key.strip().replace('export ', '')
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- Image sourcing ---
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
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
                width = ii.get("width", 0)
                if url and "image" in mime and width > 300:
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": width,
                        "height": ii.get("height", 0)
                    })
            print(f"  ✓ Wikimedia Commons: {len(results)} results for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for a relevant image. Use curl because Python urllib gets 403."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        for photo in photos:
            url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
            if url:
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def validate_image(url):
    """Validate image URL returns HTTP 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {r.status_code}, {ct}, {cl} bytes")
            return True
        # Try GET for servers that don't support HEAD well
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        # Read a bit to check size
        chunk = r.raw.read(10000)
        if r.status_code == 200 and "image" in ct and len(chunk) > 5000:
            print(f"  ✓ Image validated (GET): {r.status_code}, {ct}, {len(chunk)}+ bytes")
            return True
        print(f"  ✗ Image validation failed: {r.status_code}, {ct}, {len(chunk)} bytes")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=15)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Inserted: {result[0].get('slug', 'unknown')}")
            return True
        print(f"  ✓ Inserted (no body returned)")
        return True
    else:
        print(f"  ✗ Insert failed: {r.status_code} — {r.text[:300]}")
        return False


# ========================================================================
# ARTICLE 1: El Niño and India's Monsoon
# ========================================================================
def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: El Niño and India's Monsoon Crisis")
    print("="*60)

    # Image sourcing: Wikimedia Commons for monsoon/drought imagery
    image_url = None
    image_caption = ""
    image_attribution = ""

    # Try Wikimedia Commons first
    commons = fetch_wikimedia_commons_images("India monsoon rain agriculture", 5)
    for img in commons:
        title_lower = img["title"].lower()
        if any(kw in title_lower for kw in ["monsoon", "rain", "india", "farm", "paddy", "rice", "drought"]):
            if validate_image(img["url"]):
                image_url = img["url"]
                image_caption = "Monsoon rains over Indian farmland"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        # Try different search
        commons2 = fetch_wikimedia_commons_images("Indian monsoon farmer field", 5)
        for img in commons2:
            if validate_image(img["url"]):
                image_url = img["url"]
                image_caption = "Agricultural fields during India's monsoon season"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        # Fall back to Pexels
        pexels_url = fetch_pexels_image("India monsoon rain farming")
        if pexels_url and validate_image(pexels_url):
            image_url = pexels_url
            image_caption = "Monsoon rain over farmland in India"
            image_attribution = "Pexels"

    if not image_url:
        pexels_url = fetch_pexels_image("rice paddy field rain")
        if pexels_url and validate_image(pexels_url):
            image_url = pexels_url
            image_caption = "Rice paddy fields awaiting monsoon rains"
            image_attribution = "Pexels"

    slug = "el-nino-india-monsoon-26-percent-deficit-food-inflation-risk-20260613"

    body = """El Niño is back. The U.S. Climate Prediction Center confirmed this week that El Niño conditions have officially developed in the tropical Pacific, and forecasters expect the event to strengthen into a moderate-to-strong episode by the northern hemisphere winter of 2026–27. For India, the timing could not be worse. The southwest monsoon, which delivers nearly 70 per cent of the country's annual rainfall, is already running 26.5 per cent below normal through the first 12 days of June.

The India Meteorological Department's latest bulletin projects below-normal rainfall for the entire June–September season, forecasting just 90 per cent of the long-period average. Pune has not recorded a single millimetre of rain in 21 days — a dry streak not seen since at least 2014. Across Maharashtra, rainfall deficits range from 43 per cent in Marathwada to 73 per cent in Vidarbha. The monsoon, which made landfall in Kerala on 4 June — a few days behind schedule — has all but stalled.

## Why This El Niño Could Be Historic

Climate scientists are warning this could be the costliest El Niño on record. Forecasts suggest sea surface temperature anomalies could exceed 2°C, rivalling the intensity of the infamous 1997–98 and 2015–16 events. But unlike those years, this episode is unfolding against a backdrop of 1.42°C of global warming above pre-industrial levels, a pre-monsoon heatwave that pushed temperatures above 46°C across northern India and Pakistan, and drastically reduced winter snowpack in the Hindu Kush–Himalayan range.

"The outlook points to a drier monsoon overall, but that does not mean lower risk," said Manish Shrestha, a hydrologist at ICIMOD in Kathmandu. "Short, intense rainfall events can still trigger serious hazards." The pattern experts fear most is the compound scenario: prolonged dry spells followed by sudden intense downpours that trigger flash floods and landslides, all against a backdrop of depleted water reserves.

## The Food Price Equation

For India's 1.4 billion people, the monsoon is not just weather — it is the economy. Agriculture accounts for 18 per cent of India's nearly $4 trillion GDP, and roughly half the country's farmland remains rain-fed. Rice, cotton, and soybeans are the crops most vulnerable to deficit rainfall.

India's rice stocks remain healthy, providing a buffer against moderate shortfalls. But the comfort zone ends with pulses and oilseeds. India imported over $23 billion worth of these commodities in FY26, and El Niño-driven droughts in Southeast Asian palm oil producers like Indonesia and Malaysia could push both international prices and India's import bill sharply higher.

Farmers are already adjusting. In Madhya Pradesh, Abhishek Raghuvanshi, a farmer from Vidisha district, told Mint he has abandoned plans to plant rice in favour of soybean, which requires less water. "Farmers in my neighbourhood are likely to plant less maize and rice this year," he said. "We are also opting for shorter-duration varieties, which are better suited for dry conditions."

Vegetable prices, historically the most volatile component of India's food inflation basket, could spike if the monsoon remains weak through July and August — precisely when most kharif crops enter critical grain formation stages.

## What the Diaspora Should Watch

For NRIs with families in rural and semi-urban India, the trajectory of this monsoon is worth monitoring closely. A moderate deficit — between 5 and 10 per cent below normal — is manageable. A severe shortfall could trigger a food inflation cycle that erodes purchasing power for middle-class households across the country.

The Reserve Bank of India, which cut its benchmark rate by 25 basis points in April, may find its room for further easing constrained if food prices surge. Investors in Indian equities should watch FMCG and agricultural stocks for early signals. And the global rice market, where India remains the world's largest exporter, could tighten if New Delhi reimpose export restrictions to protect domestic supply — as it did during the 2023 El Niño.

The monsoon has four months to play out, and reservoir levels remain 19 per cent above normal, providing some insurance. But the opening act has been troubling. Whether this El Niño delivers a manageable shortfall or a full-blown agricultural crisis will depend on what happens in July, when the season's heaviest rainfall is expected — and when the El Niño's grip on the jet stream typically tightens.

**Sources:** India Meteorological Department, U.S. Climate Prediction Center (NOAA), ICIMOD Hindu Kush–Himalayan Monsoon Outlook 2026, Livemint, Reuters, Outlook Business"""

    article = {
        "headline": "El Niño Has Arrived. India's Monsoon Is Already 26 Per Cent Below Normal.",
        "subheadline": "Forecasters say this could be the strongest El Niño since 1997. Farmers are switching crops. Food prices may follow.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "climate",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "diaspora_angle": "A weak monsoon could trigger food inflation that hits NRI families in rural India and tighten global rice markets where India is the largest exporter.",
        "sources": ["India Meteorological Department", "U.S. Climate Prediction Center (NOAA)", "ICIMOD Monsoon Outlook 2026", "Livemint", "Reuters", "Outlook Business"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

    if not image_url:
        print("  ⚠ No valid image found — inserting without image")
        article.pop("image_url", None)
        article.pop("image_caption", None)
        article.pop("image_attribution", None)

    return insert_article(article)


# ========================================================================
# ARTICLE 2: India-Canada Diplomatic Thaw
# ========================================================================
def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: India-Canada Diplomatic Thaw")
    print("="*60)

    # Image: Try Jaishankar on Wikipedia
    image_url = fetch_wikipedia_person_image("S. Jaishankar")
    image_caption = "External Affairs Minister S. Jaishankar"
    image_attribution = "Wikimedia Commons"

    if image_url and not validate_image(image_url):
        image_url = None

    if not image_url:
        image_url = fetch_wikipedia_person_image("Subrahmanyam Jaishankar")
        if image_url and not validate_image(image_url):
            image_url = None

    if not image_url:
        # Try Mark Carney
        image_url = fetch_wikipedia_person_image("Mark Carney")
        image_caption = "Canadian Prime Minister Mark Carney"
        if image_url and not validate_image(image_url):
            image_url = None

    if not image_url:
        # Try Commons
        commons = fetch_wikimedia_commons_images("Jaishankar India foreign minister", 5)
        for img in commons:
            if validate_image(img["url"]):
                image_url = img["url"]
                image_caption = "India's External Affairs Minister S. Jaishankar"
                break

    slug = "jaishankar-canada-visit-carney-india-diplomatic-thaw-20260613"

    body = """External Affairs Minister S. Jaishankar is likely to travel to Canada next week, sources told Indian media on Saturday — a visit that would mark the most significant high-level diplomatic engagement between the two countries since relations cratered in 2023 over the killing of Khalistani separatist leader Hardeep Singh Nijjar on Canadian soil.

The exact date has not been confirmed, but the timing aligns with a broader recalibration underway in Ottawa. Canadian Prime Minister Mark Carney, speaking to reporters in Gyeongju on Saturday, pointedly highlighted the "progress" his government has made in strengthening ties with India as part of Canada's strategy to reduce its dependence on trade with the United States.

## A Relationship Rebuilt From the Wreckage

The India–Canada relationship hit its nadir under Justin Trudeau, whose public accusation that the Indian government was involved in Nijjar's assassination triggered a diplomatic spiral: India expelled Canadian diplomats, suspended visa services, and issued a safety advisory warning Indians against travel to Canada. Ottawa withdrew 41 diplomats from India after New Delhi threatened to revoke their immunity.

Carney, who replaced Trudeau as Liberal leader earlier this year, has moved quickly to reset the tone. "What Canada will be looking to do is to diversify our trading relationships with like-minded countries," he said at the APEC summit. "There are opportunities to rebuild the relationship with India — there needs to be a shared sense of values around that commercial relationship."

The pivot is not merely rhetorical. Canadian Foreign Minister Anita Anand and other cabinet members have been engaging with their Indian counterparts behind the scenes, according to Carney's office. And in a striking signal of intent, India's High Commissioner Dinesh Patnaik told the Global Energy Show in Calgary this week that India is now considering Canada as a potential crude oil supplier — a prospect that would have been unthinkable a year ago.

## Why Carney Needs India

The urgency on the Canadian side is strategic. With the United States imposing escalating tariffs and Trump openly musing about absorbing Canada, Ottawa is scrambling to build trade relationships that reduce its vulnerability to American pressure. The Prime Minister's Office has announced an "ambitious new mission to double non-US exports in the next decade," with the Indo-Pacific at the centre of that strategy.

India, for its part, is open to the rapprochement but is proceeding with characteristic caution. New Delhi has not publicly acknowledged the planned Jaishankar visit, and Indian officials are expected to demand tangible action on the Khalistan issue — specifically, a crackdown on extremist activities on Canadian soil — before fully normalising relations.

"India has always maintained that the Khalistan extremist elements are a small minority and do not represent the Sikh community," Jaishankar said at a press conference in Washington earlier this year. "The Modi government has paid a great deal of attention to the issues of the Sikh community in the last ten years."

## What This Means for 1.8 Million Indian Canadians

For the estimated 1.8 million people of Indian origin living in Canada, the diplomatic freeze has been more than an abstraction. Visa processing delays, halted consular services, and a general atmosphere of suspicion have affected students, workers, and families on both sides.

Canada remains one of the top destinations for Indian students, with over 320,000 Indian nationals enrolled in Canadian institutions as of 2025. A thaw in relations could ease visa backlogs and restore the kind of people-to-people connectivity that both governments say they value.

The energy dimension is equally significant for the diaspora. If India begins importing Canadian crude — its newer refineries are designed to handle heavy grades — it would create a new economic corridor between the two countries, with potential downstream benefits for Indian-Canadian businesses in the energy sector.

The coming weeks will test whether Carney's rhetoric translates into the kind of concrete action that New Delhi demands. But the trajectory is clear: after two years of diplomatic winter, India and Canada appear to be testing the ice.

**Sources:** Reuters, The Indian Eye, Canadian Prime Minister's Office, Global Energy Show (Calgary)"""

    article = {
        "headline": "Jaishankar May Visit Canada Next Week. It Would Be the First High-Level Trip Since the Diplomatic Freeze.",
        "subheadline": "Mark Carney is pivoting away from Washington and toward New Delhi. India is listening — but wants action on Khalistan first.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diplomacy",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "diaspora_angle": "1.8 million Indian Canadians have endured visa delays and consular shutdowns during the diplomatic freeze — a thaw could restore services and open new trade corridors.",
        "sources": ["Reuters", "The Indian Eye", "Canadian Prime Minister's Office", "Global Energy Show Calgary"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

    if not image_url:
        print("  ⚠ No valid image found — inserting without image")
        article.pop("image_url", None)
        article.pop("image_caption", None)
        article.pop("image_attribution", None)

    return insert_article(article)


# ========================================================================
# ARTICLE 3: SpaceX IPO / MANGOS
# ========================================================================
def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: SpaceX IPO Reshapes Wall Street's Power Index")
    print("="*60)

    # Image: SpaceX or Elon Musk from Wikipedia
    image_url = None
    image_caption = ""
    image_attribution = ""

    # Try Wikimedia Commons for SpaceX
    commons = fetch_wikimedia_commons_images("SpaceX Falcon rocket launch", 5)
    for img in commons:
        title_lower = img["title"].lower()
        if any(kw in title_lower for kw in ["spacex", "falcon", "starship", "rocket"]):
            if validate_image(img["url"]):
                image_url = img["url"]
                image_caption = "A SpaceX rocket launch from Cape Canaveral"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        # Try Elon Musk Wikipedia
        image_url = fetch_wikipedia_person_image("Elon Musk")
        if image_url and validate_image(image_url):
            image_caption = "SpaceX CEO Elon Musk"
            image_attribution = "Wikimedia Commons"
        else:
            image_url = None

    if not image_url:
        commons2 = fetch_wikimedia_commons_images("SpaceX launch", 5)
        for img in commons2:
            if validate_image(img["url"]):
                image_url = img["url"]
                image_caption = "A SpaceX launch"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        pexels_url = fetch_pexels_image("rocket launch space")
        if pexels_url and validate_image(pexels_url):
            image_url = pexels_url
            image_caption = "A rocket launch at sunset"
            image_attribution = "Pexels"

    slug = "spacex-2-trillion-ipo-mangos-magnificent-seven-wall-street-20260613"

    body = """SpaceX went public this past week and immediately became one of the most valuable companies on Earth. The IPO — the largest in United States history — valued Elon Musk's rocket and satellite company at more than $2 trillion, vaulting it above both Tesla and Meta Platforms. Wall Street's decade-old shorthand for market dominance is already crumbling.

The "Magnificent Seven" — the label coined by Bank of America in 2023 for the seven heavyweight tech stocks that drove American markets to record highs — suddenly has an identity crisis. SpaceX, now the ninth or tenth most valuable company in the world depending on the day, is not in the group. Neither are Anthropic or OpenAI, both of which are preparing their own trillion-dollar IPOs.

## Enter the MANGOS

The race to devise a replacement acronym is well underway. The frontrunner gaining traction on X and among institutional investors is **MANGOS** — Meta, Anthropic, Nvidia, Google (Alphabet), OpenAI, and SpaceX. The label is not standardised; some interpreters swap Anthropic for Apple. But the direction is clear.

"We are already referring to it internally, and the industry is picking up on it as well," said Aga Kuplinska, senior vice president of product development at Tidal Financial Group, which helps asset managers roll out ETFs.

Others are taking a more expansive approach. Dan Boardman-Weston, CEO of BRI Wealth Management, has proposed "Magna Atoms" — the Magnificent Seven plus SpaceX, OpenAI, and Anthropic. Bank of America itself quietly pivoted in a May research note to the "AI Big 10," adding Broadcom, Micron, and AMD to the original seven. That expanded group now accounts for more than 40 per cent of the S&P 500's total weight.

## The Indian Connection

What is striking about the reshuffled power index is how many of its constituent companies are led or shaped by Indian-origin executives. Sundar Pichai runs Alphabet. Satya Nadella runs Microsoft. Arvind Krishna leads IBM. Shantanu Narayen heads Adobe. These are not peripheral figures — they are the architects of the AI infrastructure buildout that is driving the current market mania.

India's own ecosystem is plugging in at the infrastructure level. The Indian Space Research Organisation has launched over 430 foreign satellites commercially, and NewSpace India is aggressively courting Western contracts. SpaceX's Starlink, meanwhile, is negotiating with Indian regulators for a satellite broadband licence that could transform rural connectivity across the subcontinent — a market of 600 million potential users that no terrestrial provider has been able to reach.

## What It Means for Markets

The concentration risk is hard to overstate. Whether you call them the Magnificent Seven, the MANGOS, or the Magna Atoms, the handful of companies at the top of the S&P 500 now wield an outsized influence on index returns. A bad quarter from Nvidia or a regulatory crackdown on AI companies could ripple through pension funds and 401(k) accounts that millions of NRI investors hold.

SpaceX's entry into public markets also introduces a new variable: space. The company's Starlink satellite internet business generates billions in recurring revenue and is growing rapidly across emerging markets. Its government contracts — including classified defence work — add another layer of strategic value that traditional tech companies do not carry.

"The Magnificent Seven label is not going away," said Dave Mazza, CEO of Roundhill Investments. "It is too embedded in how investors and the media view large-cap tech leadership. What you will likely see is additive terminology rather than replacement."

Perhaps. But the speed with which SpaceX breached the $2 trillion mark suggests the taxonomy of power in American markets is shifting faster than the labels can keep up. For Indian investors and NRI professionals embedded in Silicon Valley and Wall Street, the reshuffling is more than academic. The companies that define this era are being built — and increasingly led — by people from their own community.

**Sources:** Reuters, Bank of America Global Research, Futurum Equities, Tidal Financial Group, BRI Wealth Management, Roundhill Investments"""

    article = {
        "headline": "SpaceX Just Became a $2 Trillion Company. Wall Street Is Already Renaming Its Power Index.",
        "subheadline": "The biggest IPO in American history has killed the Magnificent Seven. The leading replacement — MANGOS — features companies run by Indian-origin CEOs.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "markets",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "diaspora_angle": "Indian-origin CEOs run multiple companies in the new market power index, and SpaceX's Starlink is negotiating an India broadband licence that could reach 600 million users.",
        "sources": ["Reuters", "Bank of America Global Research", "Futurum Equities", "Tidal Financial Group", "BRI Wealth Management", "Roundhill Investments"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

    if not image_url:
        print("  ⚠ No valid image found — inserting without image")
        article.pop("image_url", None)
        article.pop("image_caption", None)
        article.pop("image_attribution", None)

    return insert_article(article)


# ========================================================================
# MAIN
# ========================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"VIDESHI NEWS WRITER — {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    results = []
    results.append(("El Niño Monsoon", write_article_1()))
    results.append(("India-Canada Thaw", write_article_2()))
    results.append(("SpaceX MANGOS", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  {status}: {name}")
    print(f"{'='*60}\n")
