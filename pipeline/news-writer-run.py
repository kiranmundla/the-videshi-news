#!/usr/bin/env python3
"""
The Videshi — News Writer
Generates 3 news articles, sources images, inserts to Supabase.
"""
import os, json, requests, urllib.parse, time, sys
from datetime import datetime, timezone
from PIL import Image
import io, subprocess

# === ENV ===
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ['SUPABASE_URL']
SB_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

SB_HEADERS = {
    'apikey': SB_KEY,
    'Authorization': f'Bearer {SB_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'

# === IMAGE SOURCING ===

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Use thumbnail as-is (330px, always works) for the image_url
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
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
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200",
        "format": "json"
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
                url = ii.get("thumburl") or ii.get("url", "")
                results.append({"url": url, "title": page.get("title", "")})
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
        result = subprocess.run(
            ['curl', '-sS', f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3',
             '-H', f'Authorization: {PEXELS_KEY}'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        for p in data.get('photos', []):
            url = p.get('src', {}).get('large2x') or p.get('src', {}).get('large')
            if url:
                print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def validate_image_url(url):
    """Check the URL returns an image > 5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', '0'))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl//1024}KB, {ct}")
            return True
        # Some servers don't support HEAD, try GET
        if r.status_code >= 400:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            if r2.status_code == 200:
                ct2 = r2.headers.get('Content-Type', '')
                if 'image' in ct2:
                    print(f"  ✓ Image validated via GET: {ct2}")
                    return True
    except Exception as e:
        print(f"  ⚠ Validation error: {e}")
    return False


def source_image(person_name=None, topic_queries=None, pexels_query=None):
    """Multi-source image sourcing. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Source 1: Wikipedia
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "priority": 3})

    # Source 2: Wikimedia Commons
    if topic_queries:
        for tq in topic_queries:
            commons = fetch_wikimedia_commons_images(tq)
            for r in commons[:2]:
                candidates.append({"url": r["url"], "source": "wikimedia_commons", "priority": 2})
            if commons:
                break

    # Source 3: Pexels
    if pexels_query:
        pex = fetch_pexels_image(pexels_query)
        if pex:
            candidates.append({"url": pex, "source": "pexels", "priority": 1})

    candidates.sort(key=lambda x: x["priority"], reverse=True)
    for c in candidates:
        if validate_image_url(c["url"]):
            attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
            return c["url"], attr

    return None, None


def insert_article(article):
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=SB_HEADERS, json=article, timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) and data else 'unknown'
        print(f"  ✓ Published: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# === ARTICLES ===

def article_modi_tour():
    print("\n=== Article 1: Modi's Five-Nation Tour ===")
    
    slug = "modi-five-nation-tour-uae-europe-energy-diplomacy-iran-crisis-20260604"
    headline = "Modi's Five-Nation Tour Is Not Ceremonial Diplomacy. It Is a Supply-Chain Emergency."
    subheadline = "With Hormuz choked, crude at $97 and the rupee near record lows, India's prime minister is racing through the UAE and four European capitals to lock down energy, tech and trade alternatives."
    
    body = """India imports more than 80 per cent of its crude oil. When the Strait of Hormuz — the corridor through which a fifth of the world's oil and gas once flowed freely — is contested and partially closed, that is not a foreign policy problem for New Delhi. It is an economic emergency.

Prime Minister Narendra Modi's five-country diplomatic tour this week — spanning the United Arab Emirates, the Netherlands, Sweden, Norway and Italy — is the clearest sign yet that India's leadership sees the Iran war not as a distant conflict but as a direct threat to the country's growth, inflation trajectory and fiscal stability. The tour comes as Brent crude sits near $97 a barrel, the rupee trades at 95.75 per dollar after touching a record low of 96.96 in mid-May, and the Reserve Bank of India prepares for one of its most consequential policy decisions on Friday.

## The Gulf First

Modi's stop in the UAE carried the most strategic weight. India and the UAE signed several defence and strategic cooperation agreements in the presence of UAE President Sheikh Mohamed bin Zayed Al Nahyan. Modi publicly condemned the Iranian attacks on the UAE and praised Abu Dhabi's "restraint, courage, and wisdom" during the regional crisis.

The relationship now stretches well beyond oil supply. India maintains strategic petroleum reserves in the UAE, has renewable energy co-investments, and operates logistics and port infrastructure through Indian companies. The UAE has steadily become one of India's most dependable energy partners — and in the current environment, dependability is the commodity in shortest supply.

For the roughly 3.5 million Indians living in Gulf states, the visit also carried an implicit message of diplomatic protection. The killing of an Indian national in the Iranian drone strike on Kuwait's airport on Tuesday night made that concern visceral. India's Ministry of External Affairs confirmed the death and said it was in contact with Kuwaiti authorities.

## The European Pivot

If the UAE leg was about securing existing energy lines, the European segment is about building new ones. In Sweden, Modi addressed a CEO roundtable and repeatedly highlighted global supply-chain disruptions, technological competition and energy insecurity. The visit to Norway — a significant oil and gas producer outside OPEC — signals India's intent to diversify sourcing beyond its traditional Gulf and Russian suppliers.

The Netherlands, one of Europe's largest trading partners with India, featured discussions on semiconductor supply chains, logistics, and agricultural technology. In Italy, the agenda centred on defence industrial cooperation and G7 coordination on the Middle East.

India's approach reflects a strategic calculation that the Iran war has permanently altered the energy landscape. Even if a ceasefire holds and the Strait of Hormuz eventually reopens, the era of assuming free passage through the world's most critical chokepoint is over. Iran has established a toll authority — the Persian Gulf Strait Authority — that has already processed applications from 300 ships, and roughly 65 per cent of outbound laden tankers are now transiting in "dark" mode with tracking systems switched off.

## What It Means for the Diaspora

For the Indian diaspora, the tour matters on two levels. Energy prices feed directly into the cost of living in India, affecting remittance calculations and family budgets back home. And the diplomatic infrastructure being built through tours like this one shapes the security environment for millions of Indians working and living across the Gulf and Europe.

External Affairs Minister S. Jaishankar spoke with his Iranian counterpart Abbas Araghchi this week specifically about shipping safety in the Strait of Hormuz — a conversation that underscores just how directly the war has intruded into India's daily diplomatic agenda.

Modi's five-country sprint is not a victory lap. It is a scramble — methodical, calculated, but undeniably urgent — to build the economic resilience India needs to weather a crisis that shows no sign of ending soon.

**Sources:** The Indian Eye, Reuters, CNN, Ministry of External Affairs"""

    print("  Sourcing image...")
    img_url, img_attr = source_image(
        person_name="Narendra Modi",
        topic_queries=["Modi UAE visit diplomatic", "Narendra Modi press conference"],
        pexels_query="Indian prime minister diplomatic summit"
    )

    sources = json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/iran-war-shock-pm-modi-takes-five-nation-outreach/"},
        {"name": "Reuters", "url": "https://reuters.com"},
        {"name": "CNN", "url": "https://cnn.com"},
        {"name": "MEA India", "url": "https://www.mea.gov.in/"}
    ])

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "news",
        "sources": sources,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False
    }
    if img_url:
        article["image_url"] = img_url
        article["image_caption"] = "Prime Minister Narendra Modi during his five-nation diplomatic tour"
        article["image_attribution"] = img_attr
    
    return insert_article(article)


def article_online_gaming():
    print("\n=== Article 2: Supreme Court Online Gaming Ruling ===")
    
    slug = "supreme-court-online-gaming-virtual-gambling-house-dream11-gst-20260604"
    headline = "India's Supreme Court Just Called Every Mobile Phone a 'Virtual Gambling House.' The Online Gaming Industry Is Reeling."
    subheadline = "The court upheld state bans on online betting — even on games of skill — and backed 28% GST on the full value of bets. Dream11, MPL and 27 other companies face an existential reckoning."
    
    body = """The judgment landed like a controlled demolition. In a ruling formally cited as State of Tamil Nadu & Ors. v. Junglee Games India Pvt. Ltd. & Ors. (2026 INSC 594), a bench of Justice JB Pardiwala and Justice R Mahadevan did something India's online gaming industry had spent years and hundreds of crores of rupees trying to prevent. They held that states can ban betting on games of skill — and that the Constitution offers no protection for it.

The observation that will define the case, and probably the industry's next decade, was this: technological developments have transformed every mobile phone into a "virtual common gambling house."

## What the Court Actually Held

The legal architecture is important. Tamil Nadu and Karnataka had amended their police and gaming laws to criminalise online betting, including on skill-based games like rummy and poker. Both the Madras High Court and Karnataka courts had sided with the industry, striking down the amendments on the ground that "betting" under Entry 34 of List II could not cover games of skill.

The Supreme Court reversed those findings entirely. It held that staking money on the uncertain outcome of any game — regardless of the skill involved in playing it — amounts to "betting" within the meaning of Entry 34. Playing a game of skill is protected commercial activity under Article 19(1)(g), the bench held. But wagering on its outcome is *res extra commercium* — outside the domain of protected trade — and therefore subject to state prohibition.

The distinction is surgical and devastating. You can play rummy. You cannot bet on rummy. And any platform that facilitates the bet is now operating in a space where states have full legislative authority to shut it down.

## The GST Hammer

In a related but separate blow, the court also upheld the 28% GST levy on the full face value of deposits made on gaming platforms. This was not on the platform's commission or service fee alone — it was on the entire amount a user stakes.

The ruling covers retrospective demands as well. For companies like Dream11, Games24x7, and Mobile Premier League, this means past tax liabilities that could run into thousands of crores are now enforceable. The industry had argued that taxing the full bet value, rather than just the platform fee, was discriminatory and unconstitutional. The court disagreed.

## Public Health, Not Just Regulation

What makes this ruling particularly potent is its framing. The court did not treat online gaming as a narrow regulatory matter. It classified it as a public health and public order concern. The bench observed that online money gaming has "a definite impact on the public in terms of addiction, financial losses and resultant suicides."

By linking online betting to Entry 1 of List II — "public order" — rather than just Entry 34, the court opened additional legislative pathways for both states and the central government. Public order, the bench held, includes not just violence or disorder but also "activities that impair public health, create widespread fear or panic, disrupt ordinary life or cause social and economic instability."

This came months after Parliament passed the Promotion and Regulation of Online Gaming Act in 2025, which imposed a nationwide prohibition on real-money games and related advertising. Several platforms, including Dream11 and MPL, had already suspended their wagering features in response. The Supreme Court's ruling now makes a successful constitutional challenge to that central legislation considerably harder.

## What Happens Next

More than 27 online gaming companies are directly affected. The industry, valued at billions of dollars before the regulatory crackdown began, faces a fundamental question: can it survive as a business if users cannot stake real money?

For the diaspora, the implications extend to investment. Several NRI-backed venture funds had significant exposure to India's online gaming sector, which had been one of the fastest-growing segments of the country's startup ecosystem. Those bets — financial and strategic — now look very different.

The court's observation about virtual gambling houses will likely echo far beyond India. Regulators in Southeast Asia, Africa, and Latin America have been watching India's approach to online gaming closely. What India's highest court has now said is that the smartphone in your pocket is not just a device. In the wrong hands, at the wrong stakes, it is a casino.

**Sources:** LiveLaw, The Indian Eye, Asia Gaming Brief, Supreme Court Observer"""

    print("  Sourcing image...")
    img_url, img_attr = source_image(
        person_name=None,
        topic_queries=["Supreme Court India building New Delhi", "Supreme Court of India exterior"],
        pexels_query="supreme court building India"
    )

    sources = json.dumps([
        {"name": "LiveLaw", "url": "https://livelaw.in"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/supreme-court-upholds-28-gst-on-online-gaming/"},
        {"name": "Asia Gaming Brief", "url": "https://agbrief.com"},
        {"name": "Supreme Court Observer", "url": "https://scobserver.in"}
    ])

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "news",
        "sources": sources,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False
    }
    if img_url:
        article["image_url"] = img_url
        article["image_caption"] = "The Supreme Court of India in New Delhi"
        article["image_attribution"] = img_attr
    
    return insert_article(article)


def article_drone_order():
    print("\n=== Article 3: India's $2 Billion Drone Order ===")
    
    slug = "india-2-billion-military-drone-order-domestic-manufacturers-defence-20260604"
    headline = "India Is About to Place Its Largest-Ever Military Drone Order. The $2 Billion Will Go Entirely to Domestic Firms."
    subheadline = "Lessons from the Pakistan confrontation and the Iran war have fast-tracked India's biggest unmanned systems purchase. Deliveries are expected within 18 to 24 months."
    
    body = """India is preparing to order more than $2 billion worth of military drones from domestic manufacturers this year, in what would be the country's largest-ever procurement of unmanned aerial systems. The plans are in advanced stages and deliveries are expected over 18 to 24 months, according to Smit Shah, president of the Drone Federation of India.

The order is expected to move through a fast-track procurement route, reflecting the urgency with which India's defence establishment has reassessed its drone capabilities following two recent conflicts that demonstrated their strategic value on an industrial scale.

## The Lessons That Forced the Pivot

The confrontation with Pakistan in May 2025 — Operation Sindoor — was the immediate catalyst. Both countries deployed unmanned aerial vehicles at a scale never before seen in a South Asian conflict. The episode exposed gaps in India's drone inventory, particularly in tactical-class systems that can be produced cheaply and deployed at volume.

The ongoing Iran war reinforced the lesson on a global stage. Iranian drones have struck targets across the Gulf, including Kuwait's airport this week. The war in Ukraine before it had already demonstrated that low-cost unmanned systems can neutralise platforms costing orders of magnitude more. Military planners in New Delhi have concluded that drone warfare is no longer a niche capability — it is the baseline.

"Drones are force multipliers on the modern battlefields," said Ramesh Chandra Padhi of IG Defence, a manufacturer of unmanned aerial vehicles and short-range missiles. "In the next phase, tactical drone procurements in India may exceed 200 billion rupees."

## The Domestic Industrial Base

The order's most significant feature is that it will go entirely to Indian companies. India now has more than 600 drone firms, many of them incubated through the government's iDEX (Innovations for Defence Excellence) programme, which funds startups developing military-grade technology.

The procurement aligns with a broader defence capital allocation. In March, the Ministry of Defence approved approximately 2.38 trillion rupees for acquisitions including transport aircraft, missile systems, and armed drones. The specific drone allocation was not disclosed, but the $2 billion figure cited by the Drone Federation represents the single largest category within that envelope.

The Indian Army has declared 2026 the "Year of Networking and Data Centricity," with unmanned aerial systems and counter-drone capabilities identified as key focus areas. The doctrine draws directly from Operation Sindoor, with emphasis on AI integration, real-time battlefield data, and swarm tactics that require large fleets of relatively inexpensive platforms.

## Why Domestic Matters

India's push to source drones domestically is not purely ideological. Global supply chains for military-grade components have been severely disrupted by the Iran war and earlier by the Ukraine conflict. Countries that depend on imported drone systems are finding deliveries delayed, prices inflated, and access to critical subsystems — particularly semiconductors and advanced sensors — constrained.

By building a domestic manufacturing base, India aims to insulate its military from these disruptions. The strategy also feeds into the government's broader Aatmanirbhar Bharat initiative, which has set ambitious targets for defence exports. The Indian Army's planning documents project that data-centric defence modernisation could contribute to 50,000 crore rupees in defence exports over the next few years.

The timing is also driven by the recognition that India's neighbourhood is not getting calmer. China continues to expand its military footprint along the Line of Actual Control, Pakistan's drone capabilities were demonstrated more recently than anyone in Delhi is comfortable admitting, and the Indian Ocean is increasingly a zone of great-power competition. A $2 billion drone order is an investment in the principle that the next conflict will be fought by machines as much as by soldiers — and India intends to build those machines itself.

## Diaspora Dimension

For the Indian diaspora, particularly those in the technology and defence sectors abroad, the order opens a new corridor. Several US and Israel-based Indian-origin entrepreneurs have stakes in drone component companies that could benefit from India's procurement surge. The iDEX programme has already attracted diaspora engineers back to India, and a $2 billion domestic order substantially raises the commercial incentive to build defence technology for the Indian market.

India's defence ministry has not officially confirmed the $2 billion figure. But the Drone Federation's confidence in the number, combined with the advanced procurement stage and the strategic urgency driving it, suggests the order is not a matter of if but when.

**Sources:** Reuters, Outlook Business, The Hindu BusinessLine, Drone Federation of India"""

    print("  Sourcing image...")
    img_url, img_attr = source_image(
        person_name=None,
        topic_queries=["Indian military drone UAV India", "India armed forces drone"],
        pexels_query="military drone unmanned aerial vehicle"
    )

    sources = json.dumps([
        {"name": "Reuters", "url": "https://reuters.com"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com"},
        {"name": "The Hindu BusinessLine", "url": "https://thehindubusinessline.com"},
        {"name": "Drone Federation of India", "url": "https://dronefederationofindia.org"}
    ])

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "news",
        "sources": sources,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False
    }
    if img_url:
        article["image_url"] = img_url
        article["image_caption"] = "An Indian military unmanned aerial vehicle during a defence exercise"
        article["image_attribution"] = img_attr
    
    return insert_article(article)


# === MAIN ===
if __name__ == "__main__":
    print(f"=== The Videshi News Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} ===")
    
    results = []
    
    for name, fn in [
        ("Modi Five-Nation Tour", article_modi_tour),
        ("SC Online Gaming Ruling", article_online_gaming),
        ("India $2B Drone Order", article_drone_order),
    ]:
        try:
            r = fn()
            results.append((name, r))
        except Exception as e:
            print(f"  ✗ {name} failed: {e}")
            import traceback; traceback.print_exc()
            results.append((name, None))

    print("\n=== SUMMARY ===")
    for title, art_id in results:
        status = f"✓ {art_id}" if art_id else "✗ FAILED"
        print(f"  {title}: {status}")
    
    successful = sum(1 for _, r in results if r)
    print(f"\n  {successful}/3 articles published.")
