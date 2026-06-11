#!/usr/bin/env python3
"""News writer for The Videshi — June 11, 2026 afternoon batch."""

import json, os, sys, time, uuid, hashlib
import requests
from datetime import datetime, timezone
from io import BytesIO

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = "TheVideshi/1.0 (thevideshi.com)"
HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- Image sourcing functions ---

def fetch_wikipedia_person_image(person_name):
    import urllib.parse
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
                print(f"  OK Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  WARN Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=5):
    import urllib.parse
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200", "format": "json"
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
                    "width": ii.get("width", 0), "height": ii.get("height", 0)
                })
            if results:
                print(f"  OK Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  WARN Wikimedia error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        import subprocess
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3&orientation=landscape'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0].get("src", {}).get("landscape", "")
            if url:
                print(f"  OK Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  WARN Pexels error: {e}")
    return None


def compress_and_upload(img_url, slug):
    try:
        from PIL import Image
    except ImportError:
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow', '-q'], check=True)
        from PIL import Image

    print(f"  Downloading: {img_url[:80]}...")
    r = requests.get(img_url, headers={"User-Agent": UA}, timeout=20)
    if r.status_code != 200 or len(r.content) < 5000:
        print(f"  WARN Download failed or too small: {r.status_code}, {len(r.content)} bytes")
        return None

    try:
        img = Image.open(BytesIO(r.content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()
        print(f"  Compressed: {len(r.content)} -> {len(compressed)} bytes")
    except Exception as e:
        print(f"  WARN Compression failed: {e}")
        compressed = r.content

    filename = f"{slug}.jpg"
    upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    resp = requests.post(upload_url, headers={
        "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg", "x-upsert": "true"
    }, data=compressed, timeout=30)

    if resp.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  OK Uploaded: {public_url[:80]}...")
        return public_url
    else:
        print(f"  WARN Upload failed: {resp.status_code} {resp.text[:200]}")
        return None


def insert_article(article):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    resp = requests.post(url, headers=HEADERS_SB, json=article, timeout=15)
    if resp.status_code in (200, 201):
        result = resp.json()
        art_id = result[0]['id'] if isinstance(result, list) else result.get('id')
        print(f"  OK Inserted: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  FAIL Insert: {resp.status_code} {resp.text[:300]}")
        return None


# ============================================================
# ARTICLE 1: World Bank Report
# ============================================================
def write_article_1():
    print("\n=== ARTICLE 1: World Bank Global Growth ===")

    slug = "world-bank-india-fastest-growing-6-6-percent-global-growth-slashed-lost-decade-20260611"
    headline = "The World Bank Just Called India the Fastest-Growing Major Economy. It Called the Rest of the Decade a Write-Off."
    subheadline = "Global growth slashed to 2.5 per cent — and could crash to 1.3 per cent if the Iran war deepens. Oil at $94 a barrel is already rewriting the math for every NRI sending money home."

    body = """The World Bank's June 2026 Global Economic Prospects report, released on Thursday, delivered two headlines that matter to every Indian abroad: India is the fastest-growing large economy in the world, at 6.6 per cent GDP growth this year, and the rest of the developing world is falling behind in what the bank's chief economist called a "lost decade."

Indermit Gill, the World Bank's chief economist and himself of Indian origin, did not mince words. "Barring a miracle, the 2020s will prove to be what their ominous opening foreshadowed: a lost decade — not just for a couple of outliers, but for dozens of developing economies," he said at the report's launch.

## The Numbers

Global growth is now forecast at 2.5 per cent for 2026, down from 2.9 per cent in 2025 and a downgrade from the 2.6 per cent the bank had projected in January. Excluding the pandemic contraction and the 2008-09 financial crisis, that would mark the weakest year since 1991. Two-thirds of the world's economies face slower growth.

Commodity prices are expected to rise 22 per cent this year — the bank had expected them to fall 7 per cent in January. Oil is forecast to average $94 a barrel, $34 above the January projection. Fertiliser prices are up 38 per cent. Industrial metals are 18 per cent higher.

The worst-case scenario is grim: if the Strait of Hormuz remains blocked through the fourth quarter, growth drops to 2.1 per cent. Oil averages $115 a barrel. If equity markets or bond yields crack under the pressure, global output could grow by just 1.3 per cent — the weakest since 1991 outside of pandemics and financial crises.

## India's Bright Spot — With Caveats

India's 6.6 per cent makes it the clear standout among major economies, following 7 per cent growth in 2025. The bank expects Indian growth to remain "fairly high for the next two decades." By comparison, China is projected at 4.2 per cent, the US at 2.2 per cent, and the eurozone at a limp 0.7 per cent.

But the fine print matters. BMI, a Fitch group company, separately flagged that India is slowing from the 7.7 per cent GDP expansion in FY26. Higher inflation — expected to hit 5.3 per cent in FY27 — will eat into consumption growth, and the Strait of Hormuz disruption continues to impose a brutal terms-of-trade shock on an economy that imports 85 per cent of its crude oil.

The rupee tells the story. At 95.76 per dollar on Thursday, it is Asia's second-worst performing currency this year after a 6 per cent slide. The Reserve Bank of India is intervening daily — conducting dollar-rupee swaps, deploying state-run banks to sell dollars, and fully subsidising hedging costs on NRI deposits to lure foreign currency into the system.

## What the AI Gap Means

The report sounded a warning about artificial intelligence that should concern Indian policymakers. While AI could trigger the fastest global expansion since the 1970s if its benefits prove transformative, Gill warned that "AI's leading models suffer from a major blind spot: the languages of roughly half the world's people remain poorly represented in the data that trains the models."

For India, with 22 officially recognised languages and hundreds of dialects, this is not an abstract concern. Unless the gap is closed, "the AI revolution could widen rather than narrow the gap between rich and poor countries," the report said.

## What It Means for NRIs

The report reinforces a duality that has defined 2026. India's economy continues to outperform, making it the best destination for long-term capital, real estate, and family investments. At the same time, the rupee's slide means every dollar wired home buys significantly more — at 95.76, the exchange rate is nearly 10 per cent better than it was at the start of the year.

But the war overhang remains. The World Bank's warning that the 2020s may be a lost decade for development is a reminder that India's growth story, however resilient, is playing out against the most fragile global backdrop in a generation. If the Hormuz blockade persists and oil stays above $100, even India's fiscal math starts to buckle — the fertiliser subsidy bill has already doubled in three months, petrol prices are at record highs, and the government has burned through foreign exchange reserves at an unprecedented pace.

The numbers say India is winning. The world around it is not."""

    # Image sourcing
    print("  Sourcing images...")
    candidates = []

    wiki_img = fetch_wikipedia_person_image("Indermit Gill")
    if wiki_img:
        candidates.append(("wikipedia", wiki_img, "Indermit Gill, chief economist of the World Bank"))

    commons = fetch_wikimedia_commons_images("World Bank headquarters building Washington")
    for c in commons[:2]:
        candidates.append(("wikimedia_commons", c["url"], "The World Bank headquarters in Washington, D.C."))

    pexels = fetch_pexels_image("global economy stock market charts finance")
    if pexels:
        candidates.append(("pexels", pexels, "Global economic indicators on a trading screen"))

    img_url = None; img_caption = ""; img_attribution = ""
    for source, url, caption in candidates:
        img_url = url; img_caption = caption
        img_attribution = "Wikimedia Commons" if source in ("wikipedia", "wikimedia_commons") else "Pexels"
        break

    final_url = compress_and_upload(img_url, slug) if img_url else None

    return insert_article({
        "headline": headline, "subheadline": subheadline, "body": body, "slug": slug,
        "category": "news", "vertical": "economy", "status": "review", "is_editorial": False,
        "sources": json.dumps(["Reuters", "Wall Street Journal", "BMI/Fitch", "The Hindu BusinessLine"]),
        "diaspora_angle": "India's 6.6% growth and the rupee at 95.76 mean NRI remittances and investments buy more, but $94 oil and a potential lost decade for developing nations threaten the long-term outlook.",
        "image_url": final_url or "", "image_caption": img_caption, "image_attribution": img_attribution,
        "published_at": datetime.now(timezone.utc).isoformat()
    })


# ============================================================
# ARTICLE 2: Trump Kharg Island Threat
# ============================================================
def write_article_2():
    print("\n=== ARTICLE 2: Trump Threatens Kharg Island ===")

    slug = "trump-threatens-seize-kharg-island-iran-oil-hub-india-crude-imports-20260611"
    headline = "Trump Wants to Seize Iran's Oil Hub. India Buys 85 Per Cent of Its Crude From Abroad."
    subheadline = "The US president threatened to take Kharg Island, through which 90 per cent of Iranian oil exports flow. Brent is at $93. India's import bill is already at record levels."

    body = """President Donald Trump said on Thursday that the United States would "at some point in the not too distant future" seize Kharg Island, Iran's primary oil export terminal, and "assume total control" of the country's energy markets.

The threat, posted on Truth Social and then softened in a Fox News interview within the hour, represents the most dramatic escalation of the US-Iran war since it began on February 28. It came as the two sides traded airstrikes for a second consecutive day, with Iran firing at US bases in Kuwait, Jordan, and Bahrain, and American forces striking air defences and radar installations across Iran.

"At some point in the not too distant future, we will be taking Kharg Island, and other oil infrastructure points, and assume total control of their Oil and Gas Markets, much like we have with Venezuela," Trump wrote.

## What Kharg Island Is

Kharg Island sits about 25 kilometres off the coast of Iran in the Persian Gulf. It processes roughly 90 per cent of Iran's crude oil exports — about 2 million barrels per day before the blockade, or around 2 per cent of global supply. Pipelines from Iran's biggest oil fields — Gachsaran, Agha Jari, Marun — converge on the island, where crude is stored in massive onshore tanks before being loaded onto supertankers.

The US first bombed military targets near Kharg in March, deliberately avoiding the energy infrastructure. Trump said at the time he chose not to "wipe out" the terminals but would reconsider if Iran kept the Strait of Hormuz closed. Three months later, the strait remains blocked to most traffic, and Trump is now talking openly about a ground operation.

In the Fox News interview, Trump dialled back almost immediately. "I don't know that America has the stomach for it, to be honest with you," he said. "We could walk in there tomorrow. We could take soldiers — I don't want to have boots on the ground."

## The Math for India

The International Energy Agency estimates the world has lost about 13 million barrels a day of oil supply during the fighting — more than a billion barrels in total. Brent crude was at $93.20 on Thursday, up 30 per cent since the war began.

For India, the world's third-largest oil importer, the numbers are stark. The country imports roughly 85 per cent of its crude, and the war has been bleeding its external balances since March. The current account deficit is widening, the rupee has slid 6 per cent to 95.76 per dollar, and foreign portfolio investors have pulled out a record $30.4 billion from Indian equities this year.

The fertiliser subsidy bill has doubled in three months. Petrol and diesel prices are at all-time highs. Cooking gas cylinder costs are squeezing household budgets across India. The Reserve Bank of India now expects inflation to average 5.1 per cent this fiscal year.

A seizure of Kharg Island, or even a sustained threat of one, could push oil further towards $100 or beyond. If the Strait of Hormuz remains closed through the fourth quarter, the World Bank warned on Thursday, Brent could average $115 for 2026.

## India Caught in the Middle

The Kharg Island threat comes at a particularly awkward moment in India-US relations. Three Indian sailors were killed this week when US forces struck a tanker off Oman that they accused of not complying with directions. The US Navy has attacked three ships with Indian crews since Monday. India summoned the American envoy and demanded the attacks stop.

"The crew repeatedly failed to comply with directions from US forces," US Central Command said in a statement that did little to cool tempers in New Delhi.

Prime Minister Narendra Modi is set to hold bilateral talks with Trump on the sidelines of the G7 summit in Evian, France, next week. H-1B visas, trade, and energy cooperation are on the agenda. The killing of Indian seafarers will now shadow talks that were already contentious.

## Diplomacy by Bombardment

Behind the escalation, both sides say they are still talking. Three Iranian sources and Western officials told Reuters that indirect US-Iranian negotiations had "intensified," with progress on some issues but key questions still unresolved — including the release of frozen Iranian funds, Iran's demand for recognition of its control of the Strait, and Washington's insistence on a verifiable end to Iran's nuclear programme.

Iran's chief negotiator, parliament speaker Mohammad-Bagher Ghalibaf, warned Washington on X against "wrong strategies and impulsive decisions" that would "reset the entire board for the worse, explode energy infrastructure and markets and create an endless quagmire."

US Defence Secretary Pete Hegseth put it differently: "If we need to negotiate with bombs, we'll negotiate with bombs, and we're very good at it."

For India, the calculation is simpler. Every day the war continues, the import bill rises, the rupee weakens, and the fiscal space for development narrows. The government and the RBI have thrown everything they have at the problem — scrapping bond taxes, subsidising NRI deposits, incentivising overseas borrowings. But these are plugs for a leak that only a ceasefire can stop."""

    # Image sourcing
    print("  Sourcing images...")
    candidates = []

    commons = fetch_wikimedia_commons_images("Kharg Island Iran oil terminal")
    for c in commons[:2]:
        candidates.append(("wikimedia_commons", c["url"], "Kharg Island, Iran's primary oil export terminal in the Persian Gulf"))

    commons2 = fetch_wikimedia_commons_images("oil tanker Persian Gulf Strait Hormuz")
    for c in commons2[:2]:
        candidates.append(("wikimedia_commons", c["url"], "An oil tanker in the Persian Gulf near the Strait of Hormuz"))

    pexels = fetch_pexels_image("oil tanker ship ocean industrial")
    if pexels:
        candidates.append(("pexels", pexels, "An oil tanker at sea"))

    img_url = None; img_caption = ""; img_attribution = ""
    for source, url, caption in candidates:
        img_url = url; img_caption = caption
        img_attribution = "Wikimedia Commons" if source in ("wikipedia", "wikimedia_commons") else "Pexels"
        break

    final_url = compress_and_upload(img_url, slug) if img_url else None

    return insert_article({
        "headline": headline, "subheadline": subheadline, "body": body, "slug": slug,
        "category": "news", "vertical": "geopolitics", "status": "review", "is_editorial": False,
        "sources": json.dumps(["Reuters", "USA Today", "Wall Street Journal", "New York Post", "Barron's"]),
        "diaspora_angle": "India imports 85% of its crude oil and the Iran war has pushed Brent to $93, weakened the rupee 6% to 95.76, and triggered record FPI outflows — a Kharg Island seizure could push oil past $100.",
        "image_url": final_url or "", "image_caption": img_caption, "image_attribution": img_attribution,
        "published_at": datetime.now(timezone.utc).isoformat()
    })


# ============================================================
# ARTICLE 3: Kash Patel & World Cup Security
# ============================================================
def write_article_3():
    print("\n=== ARTICLE 3: Kash Patel World Cup Security ===")

    slug = "kash-patel-fbi-world-cup-2026-biggest-security-challenge-indian-american-20260611"
    headline = "An Indian-American Is Running the Biggest Security Operation in American History. The World Cup Just Kicked Off."
    subheadline = "FBI Director Kash Patel called the tournament 'the biggest lift in FBI history.' He has 300,000 background checks, 46 foreign police forces, and Iran's cyber-warfare team to worry about."

    body = """The FIFA World Cup kicked off in Mexico on Thursday with 48 teams, 11 host stadiums across three countries, and an estimated 3 million visitors descending on North America. Behind the spectacle, an Indian-American is running the largest security operation the United States has ever attempted.

Kash Patel, 46, the FBI Director and the first person of Indian descent to hold the position, told Reuters in an exclusive mid-flight interview aboard the bureau's Gulfstream jet that the tournament represents "probably the biggest lift in FBI history, in American history."

## The Scale of the Challenge

The numbers are staggering. The FBI is responsible for 300,000 background checks covering players, coaches, and tournament personnel. It has assembled a joint operations centre with police forces from 46 of the 48 participating nations — Iran and Haiti are the two exceptions. Eleven US cities are hosting matches, with 36 base camps housing teams across the country.

"Literally the first week in office when I got to the FBI I said we have to prepare for the Olympics, the World Cup, two Formula One races and the Super Bowl," Patel said in the interview, conducted in late May as he flew from Joint Base Andrews in Maryland to Dallas for a law enforcement conference.

Patel became FBI director in February 2025 and has already presided over several major investigations, including the murder of conservative commentator Charlie Kirk. But he said nothing compares to the complexity of securing a sporting event where terror, espionage, and cyberattacks converge simultaneously.

## Drones, Iran, and the Soft-Target Problem

Drones are the single biggest threat, according to Patel. The FBI launched a counterdrone training programme in October 2025 and has graduated 70 local police officers in host cities to date.

"Drones are one of the biggest ways that people who want to conduct adversarial attacks can effectuate them cheaply and from a distance, and with not much planning," he said.

The Iran dimension is unavoidable. A joint FBI-DHS threat assessment, reviewed by Reuters, details concerns about Iran's two World Cup group matches at SoFi Stadium near Los Angeles — including the potential for violent protests from fans or opponents of the Iranian government. Patel confirmed that Iran was responsible for a cyberattack on the Los Angeles Metro in March that shut down parts of the system, attributed to the pro-Iran group Ababil of Minab.

The 78-page threat document also flags heightened risks from the ongoing US-Iran war. "Recent conflicts in the Middle East, such as with Iran, have resonated with some US-based violent extremists and some hate crime perpetrators and could further exacerbate anti-US, anti-Israel, anti-Semitic, or anti-Muslim grievances," the assessment states.

But FBI officials say their greatest fear is not a coordinated state attack. It is a lone-wolf extremist acting alone — like the man who drove a truck into crowds on Bourbon Street in New Orleans on New Year's Day in an ISIS-inspired attack. "Those are among the hardest to detect and stop," officials told USA Today.

Stadiums can be hardened against threats. Fan zones, team hotels, restaurants, and transit stations cannot. Smaller host-adjacent cities, where teams have set up base camps, lack the big-event security budgets that main host cities receive.

## The ICE Question

The most politically charged element of World Cup security involves Immigration and Customs Enforcement. DHS Secretary Markwayne Mullin said ICE officers would be present throughout the tournament targeting human trafficking, counterfeit tickets, and drug smuggling — but did not rule out immigration arrests.

The FBI threat assessment notes that Trump's attendance at matches will "complicate security efforts" and warns that venue security personnel may be mistaken for immigration enforcement agents — a concern in host cities with large immigrant populations.

## Patel's Path

Patel's parents are Gujarati immigrants who came to the United States via East Africa. He was born in Garden City, New York, and built his career in national security — serving as a federal prosecutor, a senior adviser on the National Security Council, and chief of staff at the Department of Defence before Trump nominated him to lead the FBI.

His tenure has drawn scrutiny. Congressional Democrats have questioned his use of government aircraft, and critics accused him of turning the Winter Olympics in Milan into a taxpayer-funded junket after footage showed him celebrating with the US hockey team. Patel has pushed back, pointing out that he has taken fewer personal flights than his two predecessors and that he saves the agency millions by using military airfields.

Now, with the World Cup underway and the US-Iran war escalating simultaneously, his highest-profile test has begun. The tournament runs through July 19, with the final at MetLife Stadium in New Jersey.

The son of Gujarati immigrants, in charge of keeping 3 million people safe, on the biggest stage America has ever hosted. The clock is running."""

    # Image sourcing — Kash Patel
    print("  Sourcing images...")
    candidates = []

    wiki_img = fetch_wikipedia_person_image("Kash Patel")
    if wiki_img:
        candidates.append(("wikipedia", wiki_img, "FBI Director Kash Patel, the first Indian-American to lead the bureau"))

    commons = fetch_wikimedia_commons_images("Kash Patel FBI director")
    for c in commons[:2]:
        candidates.append(("wikimedia_commons", c["url"], "FBI Director Kash Patel"))

    pexels = fetch_pexels_image("football stadium security police event")
    if pexels:
        candidates.append(("pexels", pexels, "Security personnel at a major sporting venue"))

    img_url = None; img_caption = ""; img_attribution = ""
    for source, url, caption in candidates:
        img_url = url; img_caption = caption
        img_attribution = "Wikimedia Commons" if source in ("wikipedia", "wikimedia_commons") else "Pexels"
        break

    final_url = compress_and_upload(img_url, slug) if img_url else None

    return insert_article({
        "headline": headline, "subheadline": subheadline, "body": body, "slug": slug,
        "category": "news", "vertical": "diaspora-leadership", "status": "review", "is_editorial": False,
        "sources": json.dumps(["Reuters", "USA Today", "Fox News"]),
        "diaspora_angle": "Kash Patel, the son of Gujarati immigrants from East Africa, is the first Indian-American FBI director and now leads the largest security operation in US history.",
        "image_url": final_url or "", "image_caption": img_caption, "image_attribution": img_attribution,
        "published_at": datetime.now(timezone.utc).isoformat()
    })


# --- Main ---
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi News Writer — June 11, 2026 (afternoon)")
    print("=" * 60)

    results = []
    for fn in [write_article_1, write_article_2, write_article_3]:
        try:
            art_id = fn()
            results.append(art_id)
        except Exception as e:
            print(f"\n  FAIL: {e}")
            import traceback; traceback.print_exc()
            results.append(None)

    print("\n" + "=" * 60)
    print(f"Results: {sum(1 for r in results if r)}/{len(results)} articles inserted")
    for i, r in enumerate(results):
        print(f"  Article {i+1}: {'OK ' + str(r) if r else 'FAIL'}")
    print("=" * 60)
