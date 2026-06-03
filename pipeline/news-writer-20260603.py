#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-06-03 evening batch)
Writes 4 news articles, sources images, inserts into Supabase.
"""

import requests
import json
import os
import urllib.parse
import subprocess
import uuid
from datetime import datetime, timezone

# ── Load env ──
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), val)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ── Image sourcing functions ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
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
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page in pages.values():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and mime.startswith("image/") and "svg" not in mime:
                    results.append({"url": url, "title": page.get("title", ""), "width": ii.get("width", 0)})
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} results for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for a relevant image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def validate_image(url):
    """Check that a URL returns a valid image > 5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD fails
        r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
        ct2 = r2.headers.get("Content-Type", "")
        chunk = r2.raw.read(6000)
        if r2.status_code == 200 and "image" in ct2 and len(chunk) > 5000:
            return True
    except:
        pass
    print(f"  ⚠ Image validation failed: {url[:80]}")
    return False


def source_image(person_names=None, wiki_queries=None, pexels_query=None):
    """Multi-source image compare. Returns best URL or None."""
    candidates = []

    # Wikipedia person images
    if person_names:
        for name in person_names:
            url = fetch_wikipedia_person_image(name)
            if url and validate_image(url):
                candidates.append(("wikipedia", url, name))

    # Wikimedia Commons
    if wiki_queries:
        for q in wiki_queries:
            results = fetch_wikimedia_commons_images(q)
            for r in results[:2]:
                if validate_image(r["url"]):
                    candidates.append(("commons", r["url"], r["title"]))

    # Pexels fallback
    if pexels_query:
        url = fetch_pexels_image(pexels_query)
        if url and validate_image(url):
            candidates.append(("pexels", url, pexels_query))

    if not candidates:
        print("  ✗ No valid image found from any source")
        return None

    # Prefer Wikipedia person > Commons > Pexels
    for source_type in ["wikipedia", "commons", "pexels"]:
        for c in candidates:
            if c[0] == source_type:
                print(f"  ★ Selected {c[0]} image: {c[1][:80]}...")
                return c[1]

    return candidates[0][1]


# ── Articles ──

articles = []

# ── ARTICLE 1: Modi's $4B Stimulus Package ──
print("\n═══ Article 1: Modi's $4B Stimulus Package ═══")
img1 = source_image(
    person_names=["Narendra Modi", "Ashwini Vaishnaw"],
    wiki_queries=["India Union Cabinet meeting", "Indian Parliament New Delhi"],
    pexels_query="India parliament building"
)

articles.append({
    "headline": "Modi's Cabinet Just Approved a ₹39,290 Crore Stimulus. The Biggest Item Is a Bet on Cheaper Jet Fuel.",
    "subheadline": "A ₹10,000 crore Aviation Turbine Fuel stabilisation fund, a ₹5,041 crore Delhi transport overhaul and over ₹24,000 crore in new highways — the package is designed to absorb the economic shock of the Iran war.",
    "slug": "modi-cabinet-39290-crore-stimulus-atf-price-stabilization-delhi-transport-highways-20260603",
    "category": "news",
    "vertical": "news",
    "image_url": img1,
    "sources": json.dumps(["The Hindu BusinessLine", "NewsPoint", "TBS News", "The Indian EYE"]),
    "body": """The Union Cabinet has approved a ₹39,290 crore ($4 billion) package of projects spanning aviation fuel, urban transport and national highways — the most direct attempt yet by the Modi government to cushion the domestic economy from the fallout of the Iran war and the Strait of Hormuz disruption.

## The Jet Fuel Gamble

The centrepiece of the package is a ₹10,000 crore Aviation Turbine Fuel Price Stabilisation Fund, which will cap the price of jet fuel for domestic airline operations at ₹75.6 per litre. ATF prices have surged roughly 2.5 times since the Hormuz crisis began in late February, with jet fuel now accounting for nearly 40 per cent of an airline's operating costs.

Union Minister Ashwini Vaishnaw announced the decision, noting that the fund would be available to all willing Indian carriers for both domestic and international operations. Under the arrangement, airlines will procure ATF exclusively from oil marketing companies for up to three years, subject to annual review.

The market responded immediately. Shares of InterGlobe Aviation, which operates IndiGo — India's largest private airline — surged on the announcement. For NRI travellers, the implications are direct: capped fuel costs should slow the upward spiral of airfares on India routes that has made flying home significantly more expensive since the crisis began.

The mechanism comes with a built-in recovery clause. When international ATF prices moderate, the government will claw back the subsidy from oil marketing companies and return the funds to the Consolidated Fund of India. A monitoring committee comprising representatives from the Ministry of Civil Aviation, the Ministry of Petroleum and Natural Gas, and the Department of Expenditure will oversee implementation.

## Delhi's Transport Fleet Gets an Overhaul

The Cabinet simultaneously approved a ₹5,041 crore scheme to phase out old trucks and buses in Delhi. The initiative targets over 1.9 lakh trucks and 16,000 buses, replacing them with BS-VI-compliant models or electric vehicles.

Vehicle owners who scrap their old fleet will receive a 5 per cent interest subvention on loans for new vehicles, along with monthly fuel vouchers for five years through oil marketing companies. State governments will provide 100 per cent motor vehicle tax concessions and waive registration fees for replacements.

The catch: the incentives only apply if owners scrap their old vehicles or shift them to non-NCAP cities before buying replacements. The scheme is part of a broader push to reduce vehicular pollution in the capital, where air quality has been a chronic crisis.

## Highway Spending Across Four States

The remaining ₹24,000 crore-plus is allocated to highway infrastructure across Odisha, Bihar, Telangana and Madhya Pradesh. The projects include the ₹8,301 crore Rameshwar-Konark-Paradeep Coastal Highway in Odisha, the ₹3,936 crore four-laning of the Khagaria-Purnea section in Bihar, four-laning of NH-63 and NH-563 in Telangana at ₹7,597 crore, and upgrading NH-347B in Madhya Pradesh at ₹4,415 crore.

## Why It Matters for the Diaspora

The package signals that the government is no longer treating the Hormuz disruption as a temporary shock. The three-year horizon on the ATF fund and the scale of highway investment suggest New Delhi expects elevated energy prices and supply chain stress to persist well into 2027.

For the Indian diaspora, the ATF price cap is the most immediate relief. Fares on long-haul routes between India and the US, UK and Canada had risen by 30 to 50 per cent since March. If the stabilisation fund works as designed, it should prevent further escalation — though fares are unlikely to return to pre-crisis levels until the Strait of Hormuz reopens fully.

The package also underscores a broader fiscal challenge. With excise collections from petrol and diesel at a three-year high despite a recent ₹10-per-litre duty cut, the government is attempting to balance stimulus spending against a fiscal deficit that widened sharply in April. The ₹39,290 crore outlay is significant but calibrated — large enough to signal intent, small enough to stay within deficit guardrails."""
})


# ── ARTICLE 2: Yvette Cooper India Visit ──
print("\n═══ Article 2: UK Foreign Secretary Cooper's India Visit ═══")
img2 = source_image(
    person_names=["Yvette Cooper", "S. Jaishankar"],
    wiki_queries=["Yvette Cooper foreign secretary", "India UK diplomacy"],
    pexels_query="India UK flags diplomacy"
)

articles.append({
    "headline": "Britain's Foreign Secretary Arrives in India for the First Time. The Agenda Goes Far Beyond Trade.",
    "subheadline": "Yvette Cooper will meet Jaishankar and Modi on Thursday. The UK-India Vision 2035 review, the Iran war and the Free Trade Agreement are all on the table — but maritime security may be the most urgent item.",
    "slug": "yvette-cooper-india-visit-jaishankar-modi-uk-fta-vision-2035-maritime-security-20260603",
    "category": "news",
    "vertical": "news",
    "image_url": img2,
    "sources": json.dumps(["News Dive", "NewKerala", "hi INDiA", "Ministry of External Affairs"]),
    "body": """UK Foreign Secretary Yvette Cooper landed in New Delhi late on Wednesday for her first official visit to India, arriving from Beijing with an agenda shaped as much by the Iran war as by the long-standing ambition to deepen economic ties between the two countries.

Cooper will meet External Affairs Minister S. Jaishankar and call on Prime Minister Narendra Modi on Thursday. The discussions will span security, defence and economic cooperation, but it is the intersection of energy security and maritime freedom of navigation that gives this visit its urgency.

## The Hormuz Factor

The visit comes at a moment when the Strait of Hormuz remains largely closed, disrupting roughly a fifth of global oil and LNG shipments. Both Britain and India have significant exposure to the crisis — India through its dependence on Gulf energy imports, the UK through its interests in global shipping routes and its role as a guarantor of maritime security.

The British High Commission described the trip as a strategic effort to enhance cooperation in mitigating economic disruptions caused by the ongoing West Asia conflict. The phrase "freedom of navigation in maritime routes" — included in the official briefing — is a direct reference to the Hormuz chokepoint.

For Cooper, the India stop also follows her meetings in Beijing, where the UK has been navigating its own set of tensions with China. The sequencing is deliberate: the UK is signalling that India is a priority partner in a world where the old diplomatic architecture is under strain.

## Vision 2035 and the FTA

Beyond the immediate crisis, Cooper and Jaishankar will conduct a formal assessment of the UK-India Vision 2035 initiative, reviewing progress across economic development, technology, defence, climate and education. The annual evaluation is designed to keep the partnership dynamic, but it also serves as a report card on commitments made at higher diplomatic levels.

The Free Trade Agreement sits prominently on the agenda. UK Business and Trade Secretary Peter Kyle visited India recently to push for faster implementation of the deal, and Commerce Minister Piyush Goyal said on Tuesday that the two sides had "great conversations" on charting the next phase of economic engagement.

For the 1.6 million-strong Indian diaspora in the UK — the largest ethnic minority group in the country — the FTA has direct implications. It could lower barriers on remittances, ease professional mobility and expand market access for Indian businesses operating in Britain. The diaspora is also a political constituency that both governments are acutely aware of: British Indians played a visible role in the 2024 UK general election that brought the Labour government to power.

## Defence and Security Cooperation

Ministry of External Affairs spokesperson Randhir Jaiswal said on Tuesday that the talks would cover a "large gamut of issues," emphasising that the relationship extends well beyond trade. Defence cooperation, particularly in the Indo-Pacific, has accelerated in recent years. India and the UK already conduct joint military exercises and share intelligence on maritime threats.

The Iran war has added a new dimension. With Indian naval assets deployed in the Arabian Sea and British forces operating in the Persian Gulf, there is operational logic in deeper coordination. The UK's Carrier Strike Group has been active in the region, and India's navy has expanded its patrol area to cover shipping lanes disrupted by the Hormuz closure.

## What to Watch

Cooper's visit is her first to India as Foreign Secretary, and the optics matter. British High Commissioner Lindy Cameron described the UK-India partnership as a "strong defence against escalating global uncertainty" — diplomatic language that acknowledges both countries are navigating the same set of crises.

The substantive test will be whether the visit produces concrete movement on the FTA timeline or a joint statement on Hormuz. Without either, the trip risks being another round of diplomatic warmth without strategic weight. With both, it could mark a genuine upgrade in a relationship that has long punched below its potential."""
})


# ── ARTICLE 3: F-1 Student Visa Rule Changes ──
print("\n═══ Article 3: F-1 Student Visa Rule Changes ═══")
img3 = source_image(
    person_names=None,
    wiki_queries=["USCIS immigration office", "US student visa", "American university campus international students"],
    pexels_query="university graduation cap international students"
)

articles.append({
    "headline": "The US Just Proposed Killing 'Duration of Status' for Student Visas. Indian Graduates Have the Most to Lose.",
    "subheadline": "A new DHS rule would replace open-ended student stays with a fixed four-year limit and shut down the Day 1 CPT workaround that thousands of Indians rely on after losing the H-1B lottery.",
    "slug": "us-dhs-f1-student-visa-duration-of-status-elimination-indian-graduates-h1b-cpt-opt-20260603",
    "category": "news",
    "vertical": "news",
    "image_url": img3,
    "sources": json.dumps(["The Indian EYE", "US Department of Homeland Security", "Build (Danielle Goldman)", "Pew Research Center"]),
    "body": """The US Department of Homeland Security has proposed eliminating the "Duration of Status" framework for F-1 student visas — a change that, if implemented, would fundamentally reshape how Indian students manage their immigration pathway in the United States and close a critical workaround that thousands depend on.

Under the current system, international students on F-1 visas can remain in the US for as long as they maintain their student status and comply with visa requirements. The proposed rule, published on May 5, would replace that open-ended framework with a fixed admission period of up to four years. Any extension — including for continued studies or post-graduation work authorisation — would require formal approval from USCIS.

## What Changes, Practically

The shift from university-managed flexibility to federal gatekeeping is the core of the proposal. Currently, students seeking extensions or changes related to Optional Practical Training (OPT) and Curricular Practical Training (CPT) work through their universities with relatively light administrative friction. Under the new framework, every step beyond the initial four-year window would require navigating USCIS — an agency already notorious for processing delays and backlogs.

"The duration of status rule that has been proposed is going to fundamentally change the flexibility that students have had to apply for Optional Practical Training and Curricular Practical Training," said Danielle Goldman, co-founder and CEO of Build, an immigration advisory firm.

The proposal also targets the grace period available to F-1 students after their status ends, cutting it from 60 days to 30 days. That narrower window could limit the time available to secure alternative visa options or employment sponsorship — a particularly acute problem for students whose H-1B applications were not selected in the lottery.

## The Day 1 CPT Crackdown

For thousands of Indian professionals, the most consequential element of the rule is what it does to "Day 1 CPT" programmes. These allow graduates who fail to secure an H-1B visa to enrol in another academic programme while continuing to work legally. It has become a widely used pathway for Indian tech workers in AI, machine learning, software engineering and data science who face repeated lottery rejections.

Goldman said that route is likely to become significantly narrower. "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" she said.

The move would disproportionately affect Indian nationals, who form one of the largest international student populations in the US and account for a significant share of H-1B lottery applicants. Many of these professionals have been working in the US for years, building careers and families, while cycling through the lottery system.

## The Employer Side

Goldman warned that the impact extends beyond students. Companies in AI, semiconductors and other critical technology sectors depend on international talent, and many would struggle to recruit and retain skilled workers if existing immigration pathways become more restrictive.

"There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," she said. Foreign nationals make up a substantial portion of the US AI talent pool, and companies may be forced to seek alternative immigration solutions — including cap-exempt H-1B programmes and O-1 visas for highly accomplished professionals.

"The companies will either struggle because they won't have the talent or they will have to get creative and find alternate solutions," Goldman added.

## What It Means for the Diaspora

The proposed rule arrives in a landscape already hostile to legal immigration. The Trump administration has separately ordered green card applicants to leave the US during the application process, suspended the diversity visa lottery, and tightened scrutiny at ports of entry for H-1B and green card holders.

For Indian families navigating the US immigration system — many already facing decade-long green card backlogs due to per-country quotas — the cumulative effect is a narrowing of every pathway that once made the American route viable. The proposed rule is open for public comment before it can take effect, and legal challenges are expected. But the direction of travel is unmistakable.

Goldman's advice to current students: "Develop multiple backup plans rather than relying solely on H-1B lottery selection or Day 1 CPT programmes." For many Indian graduates, the question is no longer whether the US is getting harder. It is whether Canada, the UK or Australia offers a more certain future."""
})


# ── ARTICLE 4: India-Oman CEPA Kicks In ──
print("\n═══ Article 4: India-Oman CEPA ═══")
img4 = source_image(
    person_names=None,
    wiki_queries=["Port of Duqm Oman", "Oman India trade", "Arabian Sea shipping"],
    pexels_query="Oman port shipping container"
)

articles.append({
    "headline": "India Signed a Trade Deal With Oman Last Year. The Hormuz Crisis Just Made It the Smartest Bet in the Room.",
    "subheadline": "The India-Oman CEPA came into effect on June 1, giving Indian exporters duty-free access to 98% of Omani tariff lines — and, crucially, a trade route that bypasses the Strait of Hormuz entirely.",
    "slug": "india-oman-cepa-trade-deal-june-2026-hormuz-bypass-duqm-port-energy-security-20260603",
    "category": "news",
    "vertical": "news",
    "image_url": img4,
    "sources": json.dumps(["OilPrice.com", "Ministry of Commerce India", "American Enterprise Institute", "Reuters"]),
    "body": """When India and Oman signed the Comprehensive Economic Partnership Agreement late last year, the Strait of Hormuz was open, oil was trading below $70 a barrel, and the deal looked like a routine bilateral trade pact. Three months into a war that has choked the world's most important energy chokepoint, CEPA looks like one of the most fortuitous pieces of economic diplomacy India has conducted in years.

The agreement came into effect on June 1. Under its terms, Oman will eliminate customs duties on 98 per cent of its tariff lines, giving immediate preferential access to Indian exports including textiles, leather, pharmaceuticals, engineering goods and agricultural products.

## The Geography That Matters

The strategic value of the deal lies in a single geographical fact: Oman's primary ports — Duqm, Sohar and Salalah — are located outside the Strait of Hormuz, directly on the Arabian Sea. This gives India a secure energy and trade route that bypasses the chokepoint entirely.

The Strait of Hormuz currently funnels roughly 45 per cent of India's crude imports, 55 per cent of its LNG shipments and 90 per cent of its LPG imports. Its effective closure since February has forced Indian refiners to scramble for alternative supply routes, driving up costs and disrupting established supply chains.

Oman's ports offer an alternative. Duqm, in particular, has emerged as a strategic hub — India has already invested in a joint venture at the Duqm Special Economic Zone, and Indian companies operate in sectors ranging from logistics to petrochemicals within the port complex.

## Beyond the Bypass

The CEPA is not just about crisis management. The deal creates a framework for deeper economic integration between India and Oman at a moment when both countries are looking to diversify their economic relationships.

For Oman, the agreement opens the Indian market — the world's most populous country and fifth-largest economy — to Omani goods on preferential terms. For India, it secures a reliable partner in a Gulf that is increasingly fractured by the Iran war. Oman has maintained a traditional policy of neutrality in regional conflicts, making it one of the few Gulf states that maintains working relationships with both Iran and the Western coalition.

The timing of the pact's activation is also significant in the context of India's broader energy diversification strategy. Indian refiners have already increased crude purchases from Venezuela, Brazil, Angola and Nigeria in April and May to cover shortfalls from the Hormuz disruption. Oman adds another node to that diversification network — one with the advantage of geographic proximity and an existing strategic relationship.

## The IMEC Connection

The CEPA also feeds into the longer-term vision of the India-Middle East-Europe Economic Corridor (IMEC), first unveiled by Prime Minister Modi at the G20 summit in September 2023. IMEC was designed to create a rail and shipping corridor linking India to Europe through the Arabian Peninsula, bypassing traditional routes through the Suez Canal and the Strait of Hormuz.

The Hamas attack on Israel in October 2023 and the subsequent cascade of conflicts derailed IMEC's implementation. But analysts at the American Enterprise Institute argued this week that the Hormuz crisis has revived the strategic logic behind the corridor. With both the International North-South Transit Corridor through Iran and the Cape of Good Hope route around Africa facing their own disruptions — war damage at Chabahar and piracy off Somalia, respectively — IMEC becomes the most logical path forward.

Oman, with its ports outside the Hormuz chokepoint and its CEPA with India, would be a natural anchor in any revived IMEC framework.

## What It Means for the Diaspora

India's Omani diaspora numbers roughly 600,000, making it one of the largest Indian communities in the Gulf. The CEPA includes provisions that could ease business mobility and investment flows, particularly for Indian entrepreneurs operating in Oman's growing logistics and services sectors.

For the broader diaspora, the deal's significance is more structural. It represents a shift in how India thinks about trade resilience — moving from dependence on a single chokepoint to a diversified network of bilateral relationships designed to withstand geopolitical shocks. The Hormuz crisis was the stress test. The Oman deal passed it."""
})


# ── Insert into Supabase ──
print("\n\n═══ INSERTING ARTICLES ═══")
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
success_count = 0

for i, article in enumerate(articles):
    print(f"\n--- Article {i+1}: {article['headline'][:60]}... ---")
    
    if not article.get("image_url"):
        print("  ⚠ No image — skipping this article")
        continue
    
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": article["vertical"],
        "body": article["body"],
        "image_url": article["image_url"],
        "sources": article["sources"],
        "status": "published",
        "published_at": now,
        "is_editorial": False
    }
    
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=HEADERS,
            json=payload,
            timeout=15
        )
        if r.status_code in (200, 201):
            result = r.json()
            aid = result[0]["id"] if isinstance(result, list) and result else "unknown"
            print(f"  ✓ Published: {article['slug']} (id: {aid})")
            success_count += 1
        else:
            print(f"  ✗ Failed ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print(f"\n═══ DONE: {success_count}/{len(articles)} articles published ═══")
