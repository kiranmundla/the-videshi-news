#!/usr/bin/env python3
"""
News writer for The Videshi — June 12, 2026 batch (run B)
Writes 3 articles:
1. Federal judge blocks Trump's $100K H-1B fee
2. India summons US diplomat for second time in 3 days
3. India's May inflation hits new-series high at 3.93%
"""

import json, os, sys, uuid, requests, urllib.parse, subprocess
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
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

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

def fetch_wikipedia_person_image(person_name):
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
                print(f"  OK Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  WARN Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
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
                    "height": ii.get("height", 0),
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
        encoded = urllib.parse.quote(query)
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={encoded}&per_page=3&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  OK Pexels image for '{query}': {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  WARN Pexels error for '{query}': {e}")
    return None

def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            r2.close()
            if len(chunk) > 5000:
                return True
        print(f"  FAIL Image validation: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  FAIL Image validation error: {e}")
    return False

def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=15
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  OK Article inserted: {result[0].get('id', '?')[:16]}... slug={article['slug'][:50]}")
            return True
    print(f"  FAIL Insert: {r.status_code} — {r.text[:300]}")
    return False


# ═══════════════════════════════════════════════════════════════
# ARTICLE 1: H-1B $100K Fee Struck Down
# ═══════════════════════════════════════════════════════════════

def write_h1b_fee():
    print("\n=== Article 1: H-1B $100K Fee Struck Down ===")
    print("Sourcing image...")
    image_url = None
    image_caption = ""
    image_attribution = ""

    # Try Wikimedia Commons for US federal courthouse Boston
    commons = fetch_wikimedia_commons_images("Moakley United States Courthouse Boston")
    if commons:
        for c in commons:
            if validate_image(c["url"]):
                image_url = c["url"]
                image_caption = "The John Joseph Moakley United States Courthouse in Boston where the H-1B fee ruling was issued"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        commons2 = fetch_wikimedia_commons_images("United States Capitol building Washington")
        if commons2:
            for c in commons2:
                if validate_image(c["url"]):
                    image_url = c["url"]
                    image_caption = "The court ruled that only Congress has the constitutional authority to impose the fee"
                    image_attribution = "Wikimedia Commons"
                    break

    if not image_url:
        pexels = fetch_pexels_image("US visa passport immigration documents")
        if pexels and validate_image(pexels):
            image_url = pexels
            image_caption = "H-1B visa applications cost a few thousand dollars before Trump imposed the $100,000 surcharge in September 2025"
            image_attribution = "Pexels"

    if not image_url:
        print("  FAIL No image found")
        return False

    slug = "federal-judge-blocks-trump-100000-h1b-visa-fee-indians-biggest-winners-20260612"

    body = """A federal judge in Boston has struck down the Trump administration's $100,000 fee on H-1B visa applications, ruling that the president exceeded his constitutional authority by imposing what the court called an unauthorised tax.

US District Judge Leo Sorokin's decision on Monday vacated the policy in its entirety, delivering the most significant legal blow yet to an immigration measure that had sent shockwaves through Indian tech workers, hospitals, universities, and the companies that employ them.

## The Fee That Shook Silicon Valley and Beyond

In September 2025, President Trump signed a proclamation requiring every new H-1B visa petition to carry a $100,000 payment — a staggering increase from the few thousand dollars employers had previously paid. The administration argued the programme was being exploited to replace American workers with cheaper foreign labour.

"Abuses of the H-1B program present a national security threat by discouraging Americans from pursuing careers in science and technology," Trump contended in the proclamation.

The fee took immediate effect. Employers froze hiring pipelines. Universities cancelled faculty searches. Rural hospitals that relied on foreign-trained doctors to serve underserved communities found themselves priced out of the programme entirely.

## What the Court Said

Judge Sorokin's ruling dismantled the administration's legal foundation piece by piece. The core finding: the $100,000 payment is a tax, and only Congress has the constitutional power to levy taxes.

"The substance and application of the $100,000 payment reveal that it is a tax, regardless of what the payment is called," Sorokin wrote. He found that hiring H-1B workers is lawful activity, making the payment a revenue measure rather than a penalty for wrongdoing.

The ruling drew heavily on the Supreme Court's February decision in *Learning Resources, Inc. v. Trump* — the landmark tariff case that reined in executive overreach on trade levies. That precedent gave Sorokin a fresh framework that was unavailable to a Washington DC judge who had earlier upheld the fee in a separate challenge by the US Chamber of Commerce.

Sorokin also found the policy violated the Administrative Procedure Act, calling it "arbitrary and capricious" because the government failed to consider alternatives, exemptions for cap-exempt employers, or the reliance interests of affected institutions.

## Indians Have the Most at Stake

People born in India account for more than 70 percent of all approved H-1B petitions annually — by far the largest single nationality in the programme. The $100,000 fee had effectively priced out thousands of Indian professionals and the employers seeking to hire them.

The 65,000 annual H-1B cap, plus 20,000 additional visas for holders of US master's degrees, means the programme was already brutally competitive before the fee hike. Indian applicants, who face decade-long green card backlogs on top of H-1B uncertainty, bore a disproportionate burden.

Twenty state attorneys general, led by Massachusetts and California, brought the lawsuit that produced Monday's ruling. They argued the fee was crippling their ability to staff public schools, universities, and healthcare systems.

"Today's victory protects the integrity of the H-1B visa program as a tool to address severe labor shortages in vital industries like education, healthcare, and medical research," said Massachusetts Attorney General Andrea Joy Campbell.

The American Medical Association called it "a victory for patients," noting that international medical graduates — many of them Indian — play a vital role in caring for patients in underserved and rural areas.

## The Fight Is Not Over

The Trump administration has signalled it will appeal. "We are confident this order will be reversed," White House spokesperson Taylor Rogers said. The Department of Homeland Security called the ruling "blatant judicial activism."

Meanwhile, Republican Representative Mike Kennedy of Utah has introduced the PROTECT Act, which would codify the $100,000 fee through congressional legislation — the very route the court said was constitutionally required.

The legal landscape remains fractured. The DC court upheld the fee; the Boston court struck it down; a third challenge is pending in San Francisco. The issue appears headed for appellate courts, and possibly the Supreme Court, before any final resolution.

For now, the fee is vacated. But for the hundreds of thousands of Indian professionals whose careers in America hang on six digits and a lottery, the relief may be temporary."""

    article = {
        "headline": "A Federal Judge Just Killed Trump's $100,000 H-1B Fee. Indians, Who Get 75% of All Approvals, Have the Most to Gain.",
        "subheadline": "The Boston ruling calls it an unconstitutional tax. The White House says it will appeal. A Republican lawmaker wants Congress to impose the fee itself.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps([
            "https://www.edweek.org/policy-politics/federal-judge-strikes-down-trumps-100-000-fee-on-new-h-1b-visas/2026/06",
            "https://theindianeye.com/2026/06/09/100000-h-1b-visa-fee-us-judge-blocks-lawmakers-cheer-and-trump-lambasts/",
            "https://dailycaller.com/2026/06/10/rep-mike-kennedy-plan-bypass-obama-judge-ruling-protect-american-workers/"
        ]),
        "diaspora_angle": "Indians receive over 70% of all H-1B approvals — the $100K fee had priced thousands of Indian professionals and their employers out of the programme, and its removal is the biggest immigration relief for the diaspora in months.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


# ═══════════════════════════════════════════════════════════════
# ARTICLE 2: India Summons US Diplomat Second Time
# ═══════════════════════════════════════════════════════════════

def write_diplomat_summoned():
    print("\n=== Article 2: India Summons US Diplomat ===")
    print("Sourcing image...")
    image_url = None
    image_caption = ""
    image_attribution = ""

    # Try Jaishankar Wikipedia image
    wiki_img = fetch_wikipedia_person_image("Subrahmanyam Jaishankar")
    if wiki_img and validate_image(wiki_img):
        image_url = wiki_img
        image_caption = "External Affairs Minister S. Jaishankar's ministry summoned the US deputy chief of mission twice in three days"
        image_attribution = "Wikimedia Commons"

    if not image_url:
        commons = fetch_wikimedia_commons_images("South Block New Delhi India government")
        if commons:
            for c in commons:
                if validate_image(c["url"]):
                    image_url = c["url"]
                    image_caption = "South Block in New Delhi houses India's Ministry of External Affairs"
                    image_attribution = "Wikimedia Commons"
                    break

    if not image_url:
        pexels = fetch_pexels_image("India parliament New Delhi government building")
        if pexels and validate_image(pexels):
            image_url = pexels
            image_caption = "India has summoned the top US diplomat in New Delhi twice in three days over attacks on Indian-crewed ships"
            image_attribution = "Pexels"

    if not image_url:
        print("  FAIL No image found")
        return False

    slug = "india-summons-us-diplomat-second-time-three-days-sailor-deaths-20260612"

    body = """India summoned America's deputy chief of mission in New Delhi for the second time in three days on Friday, an extraordinary diplomatic rebuke that signals the deepest strain in the India-US relationship since Donald Trump returned to the White House.

The Ministry of External Affairs called in Jason Meeks, the senior-most US diplomat stationed in India, to lodge a formal protest against continued American military strikes on commercial vessels off the coast of Oman. The first summoning came on Wednesday, hours after three Indian sailors were killed when US forces struck the Palau-flagged oil tanker M/T Settebello. The second followed Thursday's attack on yet another vessel crewed by 20 Indians — this time without casualties.

## A Rare Diplomatic Weapon

India summoning a US diplomat to lodge a protest is, by the standards of the two decades-old strategic partnership, almost unheard of. New Delhi and Washington have built their relationship on quiet diplomacy, backchannels, and a shared vocabulary of strategic convergence that has survived disagreements over Russia sanctions, trade tariffs, and human rights criticism.

That vocabulary cracked this week.

"MEA summoned Meeks to lodge a protest against attacks on commercial vessels off the Coast of Oman," an Indian government source told Reuters. "Yesterday, yet another vessel with 20 Indian crew on board came under attack."

India's statement conspicuously avoided naming the US military or the naval blockade — diplomatic language that preserves the ability to de-escalate. But the act of summoning itself sends an unmistakable message: India considers the attacks on Indian-crewed ships a direct affront to its citizens and its interests.

## The Blockade That Is Killing Indian Sailors

The US Navy has struck nine merchant vessels attempting to transit waters near Iran as part of a naval blockade enforcing sanctions and choking off Iranian oil exports. The M/T Settebello was the eighth ship disabled. American forces said they issued warnings before firing precision munitions into the engine room.

India's shipping minister confirmed on X that three Indian sailors died in the Settebello strike. The International Maritime Organization, a UN agency, condemned the attack. India's initial response — a foreign ministry statement noting three Indian sailors were "missing" without mentioning the US — was widely criticised domestically as too weak.

By Friday, New Delhi had sharpened its tone. India has separately put all its maritime agencies on "heightened alert" and is coordinating with ship operators to reroute vessels away from the conflict zone.

## The Timing Could Not Be Worse

The diplomatic crisis arrives days before Prime Minister Narendra Modi is expected to meet Trump on the sidelines of the G7 summit in Évian-les-Bains, France, which begins on June 15. The meeting was already set to be tense — battered by Washington's tariffs, Trump's outreach to Pakistan and China, and India's frustration over immigration restrictions.

Now Modi walks into the room with dead sailors and a furious domestic audience demanding accountability.

The opposition Congress party has seized on the crisis. Rahul Gandhi has framed Pakistan's visible role in mediating the Iran ceasefire as a failure of Modi's foreign policy, adding to the political pressure for a muscular response.

India and the US have developed a deep strategic partnership over the past two decades, making it exceptionally rare for New Delhi to summon a US diplomat. The ties have come under mounting pressure during Trump's second term, battered by tariffs, immigration restrictions, and Washington's engagement with New Delhi's rivals.

## What This Means for the Diaspora

The India-US relationship is the scaffolding on which the lives of four million Indian Americans are built — from H-1B visa programmes and green card backlogs to defence deals and tech investment flows. When that relationship frays, the consequences ripple outward.

Indian-crewed commercial shipping is already rerouting, which will push up freight costs and delay goods. If the diplomatic temperature does not come down before the G7, the broader agenda — trade talks, defence cooperation, visa liberalisation — risks being sidelined by crisis management.

The immediate question is whether Trump's claim of an imminent Iran peace deal materialises. A deal signed this weekend would take the Strait of Hormuz off the table and remove the trigger for further strikes on commercial shipping. Without one, India faces the prospect of more attacks on vessels carrying its citizens through a warzone Washington created.

For now, the message from South Block is clear: India will not stay silent while its sailors die in someone else's war."""

    article = {
        "headline": "India Just Summoned America's Top Diplomat for the Second Time in Three Days. The Relationship Has Not Been This Strained in Years.",
        "subheadline": "Two diplomatic protests in 72 hours over attacks on Indian-crewed ships mark the sharpest public rebuke New Delhi has delivered to Washington in the modern partnership.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps([
            "https://www.reuters.com/world/india/india-summons-top-us-diplomat-second-time-protest-strikes-ships-off-oman-source-2026-06-12/",
            "https://www.audacy.com/national-news/trump-threatens-seize-kharg-island-iran-oil-exports-ceasefire-teeters",
            "https://en.wikipedia.org/wiki/52nd_G7_summit"
        ]),
        "diaspora_angle": "The India-US strategic partnership underpins visa programmes, defence deals, and tech investment flows that directly shape the lives of four million Indian Americans — a diplomatic crisis of this magnitude puts the broader bilateral agenda at risk.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


# ═══════════════════════════════════════════════════════════════
# ARTICLE 3: India May Inflation at New-Series High
# ═══════════════════════════════════════════════════════════════

def write_inflation():
    print("\n=== Article 3: India May Inflation ===")
    print("Sourcing image...")
    image_url = None
    image_caption = ""
    image_attribution = ""

    # Try Wikimedia Commons for Indian market / RBI
    commons = fetch_wikimedia_commons_images("Reserve Bank of India RBI building Mumbai")
    if commons:
        for c in commons:
            if validate_image(c["url"]):
                image_url = c["url"]
                image_caption = "The Reserve Bank of India has raised its inflation forecast for the current fiscal year to 5.1 percent from 4.6 percent"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        commons2 = fetch_wikimedia_commons_images("India vegetable market food prices")
        if commons2:
            for c in commons2:
                if validate_image(c["url"]):
                    image_url = c["url"]
                    image_caption = "Food inflation in India accelerated to 4.78 percent in May as fuel price hikes drove up transport and supply costs"
                    image_attribution = "Wikimedia Commons"
                    break

    if not image_url:
        pexels = fetch_pexels_image("India vegetable market food prices")
        if pexels and validate_image(pexels):
            image_url = pexels
            image_caption = "Food prices in India accelerated to 4.78 percent in May driven by four fuel price hikes and supply chain disruptions"
            image_attribution = "Pexels"

    if not image_url:
        print("  FAIL No image found")
        return False

    slug = "india-may-inflation-3-93-new-series-high-iran-war-food-fuel-20260612"

    body = """India's retail inflation rose to 3.93 percent in May, the highest reading since the government launched a revamped consumer price index in January, as four fuel price hikes and accelerating food costs pushed the war's economic toll deeper into everyday life.

The number, released by the statistics ministry on Friday, came in marginally below Reuters' forecast of 4.0 percent but confirmed what Indian households have felt for weeks: the grocery bill is climbing, the petrol pump hurts more than it did in April, and the worst may not be over.

## The Numbers Behind the Pain

Food inflation — the category that matters most to India's 1.4 billion people — accelerated to 4.78 percent in May from 4.20 percent in April. Vegetable prices, edible oils, and pulses were the main drivers, pushed higher by a combination of supply chain disruptions linked to the Strait of Hormuz closure and domestic transport costs that have risen in lockstep with diesel.

Transport inflation told its own story: it jumped to 1.75 percent from a 0.01 percent decline in April. The swing reflects the pass-through from state-owned fuel retailers, which raised petrol and diesel prices four times in May alone. Each hike was modest — a rupee or two per litre — but the cumulative effect has been corrosive, particularly for trucking, logistics, and the cost of moving food from farm to market.

The May print is the highest in the new CPI series, which uses a revised basket of goods and a new base year. While still below the RBI's 4 percent medium-term target, the trajectory is what worries economists.

## The Iran War's Long Shadow

The conflict between the United States and Iran, now in its fourth month, has reshaped India's macroeconomic landscape. Brent crude touched $93 a barrel earlier this month before sliding to $87 on Friday on hopes of a peace deal. But even at $87, oil prices remain elevated enough to keep India's import bill — roughly 85 percent of its crude is imported — under severe pressure.

The Reserve Bank of India has already responded. In its June policy review, the central bank raised its inflation forecast for the current fiscal year to 5.1 percent from 4.6 percent, citing higher oil prices and the risk of a weak monsoon. The RBI also flagged increasing risks to the rupee and the current account deficit.

"The pass-through of higher energy and raw material costs to consumers has started to push headline inflation higher, and the risks to the inflation trajectory have intensified," said Vikram Chhabra, senior economist at 360 ONE Asset in Mumbai. "We expect inflation to approach 6 percent, the upper end of the RBI's tolerance band, by the end of this calendar year."

## Rate Hikes Loom — But Not Yet

The inflation data complicates the RBI's already difficult balancing act. The central bank has been focused on supporting growth and defending the rupee, while hoping that a resolution in the Middle East would bring oil prices back down.

For now, most economists expect the RBI to stay on pause. "The sub-4 percent headline and core inflation points towards comfortable trends in the near term," said Upasna Bhardwaj, chief economist at Kotak Mahindra Bank. But she added that a 50-basis-point rate hike beginning in October remains her base case if the war drags on.

Sreejith Balasubramanian, senior economist at Bandhan AMC, flagged that the impact of the West Asia conflict will become "more visible in CPI in the coming months," pointing to wholesale price inflation that hit 8.3 percent in April and is expected to exceed 9 percent in May. The pass-through from wholesale to retail prices typically takes six to eight weeks.

If Trump's claimed Iran peace deal materialises this weekend, it could change the calculus dramatically. Brent crude falling below $80 would ease India's import costs, reduce the pressure on fuel retailers to hike prices further, and give the RBI breathing room to hold rates.

But if the deal collapses — as previous Trump announcements have — the worst-case scenario for Indian inflation involves $100-plus oil, a weak monsoon driving food prices higher, and the RBI forced into rate hikes that would slow an economy the World Bank just called the fastest-growing among major nations.

## What NRIs Should Watch

For the diaspora, India's inflation story is both personal and financial. Rising prices eat into the purchasing power of remittances — the rupee has weakened to 95 per dollar, but real-terms inflation means the money sent home buys less than the exchange rate suggests.

The RBI's measures to attract dollar inflows — including higher subsidised deposit rates and incentives for overseas borrowings — are partially aimed at stabilising the currency. These have already pushed corporate borrowing costs down by 40 to 45 basis points this week, triggering a $3 billion bond issuance rush by non-banking financial companies.

The critical variable remains oil. India imports 85 percent of its crude, and every dollar on the barrel price filters through to everything from cooking gas to tomatoes. A peace deal changes everything. Its absence changes nothing — except the speed at which prices climb."""

    article = {
        "headline": "India's Inflation Just Hit a New-Series High. The Iran War Is Now in Every Grocery Bill.",
        "subheadline": "Retail CPI rose to 3.93 percent in May after four fuel hikes. The RBI has raised its full-year forecast. Economists say 6 percent by December is no longer a tail risk.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps([
            "https://www.reuters.com/world/india/indias-may-retail-inflation-rises-393-year-2026-06-12/",
            "https://www.reuters.com/world/india/india-sees-3-bln-debt-fundraising-rush-yields-slump-after-rbi-moves-2026-06-12/",
            "https://www.reuters.com/world/india/rupee-rallies-oil-slump-sparks-unwinding-dollar-longs-2026-06-12/"
        ]),
        "diaspora_angle": "Rising Indian inflation erodes the purchasing power of remittances — the rupee at 95 per dollar means money sent home buys less in real terms, while RBI rate hikes would slow the economy the diaspora invests in.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    return insert_article(article)


# ── Main ────────────────────────────────────────────────────────

if __name__ == "__main__":
    results = []
    results.append(("H-1B Fee Ruling", write_h1b_fee()))
    results.append(("India-US Diplomat", write_diplomat_summoned()))
    results.append(("India May Inflation", write_inflation()))

    print("\n=== SUMMARY ===")
    for name, ok in results:
        print(f"  {'OK' if ok else 'FAIL'} {name}")

    failures = sum(1 for _, ok in results if not ok)
    if failures:
        print(f"\n{failures} article(s) failed")
        sys.exit(1)
    else:
        print(f"\nAll {len(results)} articles written successfully")
